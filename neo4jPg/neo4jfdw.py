import sys
import re
import json
from multicorn import ForeignDataWrapper, Qual, ANY, ALL
from multicorn.utils import log_to_postgres, ERROR, WARNING, DEBUG, INFO
from neo4j import GraphDatabase, basic_auth, CypherError

class Neo4jForeignDataWrapper(ForeignDataWrapper):
    """
    Neo4j FWD for Postgresql
    """

    _startup_cost = 20

    def __init__(self, options, columns):

        # Calling super constructor
        super(Neo4jForeignDataWrapper, self).__init__(options, columns)

        # Managed server option
        if 'url' not in options:
            log_to_postgres('The Bolt url parameter is required and the default is "bolt://localhost:7687"', WARNING)
        self.url = options.get("url", "bolt://localhost:7687")

        if 'user' not in options:
            log_to_postgres('The user parameter is required  and the default is "neo4j"', ERROR)
        self.user = options.get("user", "neo4j")

        if 'password' not in options:
            log_to_postgres('The password parameter is required for Neo4j', ERROR)
        self.password = options.get("password", "")

        if 'cypher' not in options:
            log_to_postgres('The cypher parameter is required', ERROR)
        self.cypher = options.get("cypher", "MATCH (n) RETURN n LIMIT 100")

        # Setting table columns
        self.columns = columns

        # Create a neo4j driver instance
        self.driver = GraphDatabase.driver( self.url, auth=basic_auth(self.user, self.password))

        self.columns_stat = self.compute_columns_stat()
        self.table_stat = self.compute_table_stat();


    def get_rel_size(self, quals, columns):
        """
        This method must return a tuple of the form (expected_number_of_row, expected_mean_width_of_a_row (in bytes)).
        The quals and columns arguments can be used to compute those estimates.
        For example, the imapfdw computes a huge width whenever the payload column is requested.
        """
        log_to_postgres('get_rel_size is called', DEBUG)
        # TODO: take the min of the columns stat based on the quals ?
        return (self.table_stat, len(columns)*100)

    def get_path_keys(self):
        """
        This method must return a list of tuple of the form (column_name, expected_number_of_row).
        The expected_number_of_row must be computed as if a where column_name = some_value filter were applied.
        This helps the planner to estimate parameterized paths cost, and change the plan accordingly.
        For example, informing the planner that a filter on a column may return exactly one row, instead of the full billion, may help it on deciding to use a nested-loop instead of a full sequential scan.
        """
        log_to_postgres('get_path_keys is called', DEBUG)
        return self.columns_stat

    def execute(self, quals, columns, sortkeys=None):

        log_to_postgres('Query Columns:  %s' % columns, DEBUG)
        log_to_postgres('Query Filters:  %s' % quals, DEBUG)

        statement = self.make_cypher(quals, columns, sortkeys)

        params = {}
        for qual in quals:
            params[unicode(qual.field_name)] = qual.value

        log_to_postgres('Neo4j query is : ' + unicode(statement), DEBUG)
        log_to_postgres('With params : ' + unicode(params), DEBUG)

        # Execute & retrieve neo4j data
        session = self.driver.session()
        try:
            for record in session.run(statement, params):
                line = {}
                for column_name in columns:
                    # TODO: from neo4j type to pg types
                    line[column_name] = record[column_name]
                yield line
        except CypherError:
            raise RuntimeError("Bad cypher query : " + statement)
        finally:
            session.close()

    def make_cypher(self, quals, columns, sortkeys):
        """
        Override cypher query to add search criteria
        """
        query = self.cypher
        log_to_postgres('Init cypher query is : ' + unicode(query), DEBUG)
        log_to_postgres('Quals are : ' + unicode(quals), DEBUG)

        if(quals is not None and len(quals) > 0):

            # Step 1 : we check if there is some `where` annotation in the query
            where_match = re.findall('/\*WHERE([^}]*})\*/', self.cypher)
            if(where_match is not None):
              for group in where_match:
                  log_to_postgres('Find a custom WHERE clause : ' + unicode(group), DEBUG)
                  group_where_condition = []

                  # parse the JSON and check if field are in the where clause
                  # if so we replace it and remove the clause from the where
                  where_config = json.loads(group)
                  for field in where_config:
                      fieldQuals = filter(lambda qual: qual.field_name == field, quals)
                      if (len(fieldQuals) > 0):
                          for qual in fieldQuals:
                              log_to_postgres('Find a field for this custom WHERE clause : ' + unicode(qual), DEBUG)
                              # Generate the condition
                              group_where_condition.append(self.generate_condition(where_config[qual.field_name], qual.operator, qual.value, '`' + qual.field_name + '`'))
                              # Remove the qual from the initial qual list
                              quals = filter(lambda qual: not qual.field_name == field, quals)

                  # replace the captured group by the condition
                  if (len(group_where_condition) > 0):
                      query = query.replace('/*WHERE' + group + '*/', ' WHERE ' + ' AND '.join(group_where_condition))
                  else:
                      query = query.replace('/*WHERE' + group + '*/', '')
                  log_to_postgres('Current cypher query is : ' + unicode(query), DEBUG)

            # Step 2 : if there is still some where clause, we replace the return by a with/where/return
            if(len(quals) > 0):
                log_to_postgres('Generic where clause', DEBUG)
                where_clauses = self.generate_where_conditions(quals)
                pattern = re.compile('(.*)RETURN(.*)', re.IGNORECASE|re.MULTILINE|re.DOTALL)
                match = pattern.match(query)
                query = match.group(1) + "WITH" + match.group(2) + " WHERE " + ' AND '.join(where_clauses) + " RETURN " + ', '.join(columns)
                log_to_postgres('Current cypher query after generic where is : ' + unicode(query), DEBUG)

        # Step 3 : We construct the projection for the return
        return_pattern = re.compile('(.*)RETURN(.*)', re.IGNORECASE|re.MULTILINE|re.DOTALL)
        return_match = return_pattern.match(query)
        query = return_match.group(1) + "WITH" + return_match.group(2) + " RETURN " + ', '.join(columns)

        # Step 4 : We add the order clause at the end of the query
        if sortkeys is not None:
            orders = []
            for sortkey in sortkeys:
                if sortkey.is_reversed:
                    orders.append(sortkey.attname + ' DESC')
                else:
                    orders.append(sortkey.attname)
            query = query + ' ORDER BY ' + ', '.join(orders)
            log_to_postgres('Current cypher query after sort is : ' + unicode(query), DEBUG)

        return query


    def generate_where_conditions(self, quals):
        """
        Build a neo4j search criteria string from a list of quals
        """
        conditions = []
        for index, qual in enumerate(quals):

            # quals is a list with ANY
            if qual.list_any_or_all == ANY:
                values = [
                    '( %s )' % self.generate_condition(qual.field_name, qual.operator[0], value, '`' + unicode(qual.field_name) + '`' + '[' + unicode(array_index) + ']')
                    for array_index, value in enumerate(qual.value)
                ]
                conditions.append( ' ( ' +  ' OR '.join(values) + ' ) ')

            # quals is a list with ALL
            elif qual.list_any_or_all == ALL:
                conditions.extend([
                    self.generate_condition(qual.field_name, qual.operator[0], value, '`' + unicode(qual.field_name) + '`' + '[' + unicode(array_index) + ']')
                    for array_index, value in enumerate(qual.value)
                ])

            # quals is just a string
            else:
                conditions.append(self.generate_condition( qual.field_name, qual.operator, qual.value, '`' + unicode(qual.field_name) + '`'))

        conditions = [x for x in conditions if x not in (None, '()', '')]
        return conditions


    def generate_condition(self, field_name, operator, value, cypher_variable):
        """
        Build a neo4j condition from a qual
        """
        condition = ''
        if operator in ('~~', '!~~', '~~*', '!~~*'):
            # Convert to cypher regex
            regex = value.replace('%', '.*')

            # For the negation, we prefix with NOT
            if operator in ('!~~', '!~~*'):
                condition += ' NOT '

            # Adding the variable name
            condition += field_name + " =~ '"

            # If it's a ILIKE, we prefix regex with (?i)
            if operator in ('~~*', '!~~*'):
                condition += '(?i)'

            # We add the regex
            condition += regex + "' "

        else:
            condition = field_name +  operator + "$" + unicode(cypher_variable)

        log_to_postgres('Condition is : ' + unicode(condition), DEBUG)
        return condition

    def compute_columns_stat(self):
        result = list();

        session = self.driver.session()
        try:
            for column_name in self.columns:
                quals = [Qual(column_name, '=', 'WHATEVER')];
                query = 'EXPLAIN ' + self.make_cypher(quals, self.columns, None)
                rs = session.run(query, {})
                explain_summary = rs.summary().plan[2]
                stats = explain_summary['EstimatedRows']

                log_to_postgres('Explain query for column ' + unicode(column_name) + ' is : ' + unicode(query), DEBUG)
                log_to_postgres('Stat for column ' + unicode(column_name) + ' is : ' + unicode(explain_summary['EstimatedRows']), DEBUG)

                result.append(((column_name,), int(stats)))

        except CypherError:
            raise RuntimeError("Bad cypher query : " + query)
        finally:
            session.close()

        log_to_postgres('Columns stats are :' + unicode(result), DEBUG)
        return result

    def compute_table_stat(self):
        stats = 100000000
        session = self.driver.session()
        try:
            rs = session.run('EXPLAIN ' + self.cypher, {})
            explain_summary = rs.summary().plan[2]
            stats = explain_summary['EstimatedRows']
            log_to_postgres('Stat for table is ' + unicode(explain_summary['EstimatedRows']), DEBUG)
        except CypherError:
            raise RuntimeError("Bad cypher query : " + cypher)
        finally:
            session.close()

        log_to_postgres('Table stat is :' + unicode(stats), DEBUG)
        return stats

