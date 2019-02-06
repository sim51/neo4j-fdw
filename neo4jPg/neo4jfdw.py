import sys
import re
import json
from multicorn import ForeignDataWrapper, ANY, ALL
from multicorn.utils import log_to_postgres, ERROR, WARNING, DEBUG, INFO
from neo4j import GraphDatabase, basic_auth, CypherError

class Neo4jForeignDataWrapper(ForeignDataWrapper):
    """
    Neo4j FWD for Postgresql
    """

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
        cypher = self.cypher

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
                  cypher = cypher.replace('/*WHERE' + group + '*/', ' WHERE ' + ' AND '.join(group_where_condition))
                  log_to_postgres('Current cypher query is : ' + unicode(cypher), DEBUG)

            # Step 2 : if there is still some where clause, we replace the return by a with/where/return
            if(len(quals) > 0):
                log_to_postgres('Generic where clause', DEBUG)
                where_clauses = self.generate_where_conditions(quals)
                pattern = re.compile('(.*)RETURN(.*)', re.IGNORECASE|re.MULTILINE|re.DOTALL)
                match = pattern.match(cypher)
                cypher = match.group(1) + "WITH" + match.group(2) + " WHERE " + ' AND '.join(where_clauses) + " RETURN " + ', '.join(columns)
                log_to_postgres('Current cypher query after generic where is : ' + unicode(cypher), DEBUG)

        # Step 3 : We add the order clause at the end of the query
        if sortkeys is not None:
            orders = []
            for sortkey in sortkeys:
                if sortkey.is_reversed:
                    orders.append(sortkey.attname + ' DESC')
                else:
                    orders.append(sortkey.attname)
            cypher = cypher + ' ORDER BY ' + ', '.join(orders)
            log_to_postgres('Current cypher query after sort is : ' + unicode(cypher), DEBUG)

        return cypher


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

# def insert(self, new_values):
# def update(self, old_values, new_values):
# def delete(self, old_values):
