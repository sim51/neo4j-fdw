import sys
import pytz
import re
import json
import datetime
from dateutil import parser
from multicorn import ForeignDataWrapper, Qual, ANY, ALL
from multicorn.utils import log_to_postgres, ERROR, WARNING, DEBUG, INFO
from neo4j import GraphDatabase, basic_auth, CypherError
import neotime

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
        self.table_stat = int(options.get("estimated_rows", -1))
        if(self.table_stat < 0):
            self.table_stat = self.compute_table_stat()
        log_to_postgres('Table estimated rows : ' + unicode(self.table_stat), DEBUG)


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
            params[unicode(qual.field_name)] = self.convert_to_neo4j(self.columns[qual.field_name], qual.value)

        log_to_postgres('Neo4j query is : ' + unicode(statement), DEBUG)
        log_to_postgres('With params : ' + unicode(params), DEBUG)

        # Execute & retrieve neo4j data
        session = self.driver.session()
        try:
            for record in session.run(statement, params):
                line = {}
                for column_name in columns:
                    # TODO: from neo4j type to pg types
                    line[column_name] = self.convert_to_pg(self.columns[column_name], record[column_name])
                log_to_postgres("sending result item to PG : " + unicode(line),  DEBUG)
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

        needUpdateProjection = True

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
                              customQual = Qual(where_config[qual.field_name], qual.operator, qual.value)
                              group_where_condition.append(self.generate_condition(customQual, qual.field_name ))
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
                needUpdateProjection=False

        # Step 3 : We construct the projection for the return
        # we only modify the projection if it's needed (ie. we don't return all the tables columns)
        if(needUpdateProjection and len(columns) < len(self.columns)):
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
            conditions.append( self.generate_condition( qual ) )

        conditions = [x for x in conditions if x not in (None, '()', '')]
        return conditions


    def generate_condition(self, qual, cypher_variable=None):
        """
        Build a neo4j condition from a qual
        """

        condition = ''

        if cypher_variable is not None:
            query_param_name = cypher_variable
        else:
            query_param_name = qual.field_name

        # quals is a list with ANY
        if qual.list_any_or_all == ANY:
            values = [
                '( %s )' % self.generate_condition(Qual(qual.field_name, qual.operator[0], value), '`' + unicode(query_param_name) + '`' + '[' + unicode(array_index) + ']')
                for array_index, value in enumerate(qual.value)
            ]
            condition = ' ( ' +  ' OR '.join(values) + ' ) '

        # quals is a list with ALL
        elif qual.list_any_or_all == ALL:
            values = [
                '( %s )' % self.generate_condition(Qual(qual.field_name, qual.operator[0], value), '`' + unicode(query_param_name) + '`' + '[' + unicode(array_index) + ']')
                for array_index, value in enumerate(qual.value)
            ]
            condition = ' ( ' +  ' AND '.join(values) + ' ) '

        # quals is just a string
        else:
            if qual.operator in ('~~', '!~~', '~~*', '!~~*'):
                # Convert to cypher regex
                regex = qual.value.replace('%', '.*')

                # For the negation, we prefix with NOT
                if qual.operator in ('!~~', '!~~*'):
                    condition += ' NOT '

                # Adding the variable name
                condition += qual.field_name + " =~ '"

                # If it's a ILIKE, we prefix regex with (?i)
                if qual.operator in ('~~*', '!~~*'):
                    condition += '(?i)'

                # We add the regex
                condition += regex + "' "

            else:
                if query_param_name.startswith('`'):
                    condition = qual.field_name +  qual.operator + "$" + unicode(query_param_name)
                else:
                    condition = qual.field_name +  qual.operator + "$`" + unicode(query_param_name) + '`'

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

    def convert_to_pg(self, column, value):
        """
        Convert a value to a PG type.
        Most work implicitly, but neoTime.Time needs a helping hand when TimeZones are involved
        """
        #log_to_postgres('Convert column:' + str(column), DEBUG)
        result = value

        # we want a time with timezone
        if column.type_name == 'time with time zone':
            if isinstance(value, neotime.Time):
                try:
                    tz = value.tzinfo         # Take TimeZone directly, since str(neotime.Time) does not expose this
                    if value.tzinfo is None :
                        tz = pytz.utc
                    parsed = parser.parse(str(value))
                    result = datetime.time(parsed.hour, parsed.minute, parsed.second, parsed.microsecond, tz)

                except ValueError as e:
                    log_to_postgres('Value ' + str(value) + ' of type ' + str(type(value)) + ' can not be compared with a time field => ' +  str(e), ERROR)
        return result

    def convert_to_neo4j(self, column, value):
        """
        Convert the value to the adequate Neo4j type.
        This is used for the quals.

        PG datetime types :
        @see https://www.postgresql.org/docs/current/datatype-datetime.html
        ------------------------------
         * timestamp with/without TZ
         * date
         * time with/without TZ

        Python datetime types :
        @see https://docs.python.org/2/library/datetime.html
        ------------------------------
         * datetime with/without TZ
         * date
         * time with/without TZ

        Neo4j datetime types :
        @see https://neo4j.com/docs/cypher-manual/3.5/syntax/temporal/
        ------------------------------
         * datetime & LocalDateTime
         * date
         * time & LocalTime

         /!\ It seems that Multicorn doesn't support time convertion as well as `now()`
        """
        result = value
        log_to_postgres('Convert '+ unicode(value)+ ' for neo4j column type:' + unicode(column.type_name), DEBUG)

        # we want a date
        if column.type_name == 'date':
            # if we have a datetime, we only take the date
            if isinstance(value, datetime.datetime):
                result = value.date()
            # if we have a date, it's perfect !
            elif isinstance(value, datetime.date):
                result = value
            else:
                # else we try to parse the string ...
                try:
                    parsed = parser.parse(unicode(value))
                    if parsed.tzinfo is not None:
                        parsed = parsed.replace(tzinfo=None)
                    result = parsed.date()
                except Exception as e:
                    log_to_postgres('Value ' + unicode(value) + ' of type ' + unicode(type(value)) + ' can not be compared with a date type field => ' +  unicode(e), ERROR)

        # we want a time without timezone
        elif column.type_name == 'time without time zone':
            # if we have a datetime, we only take the time
            if isinstance(value, datetime.datetime):
                result = value.replace(tzinfo=None).time()
            # if we have a time, it's perfect !
            elif isinstance(value, datetime.time):
                result = value
            # else we try to parse the string ...
            else:
                try:
                    parsed = parser.parse(unicode(value))
                    if parsed.tzinfo is not None:
                        parsed = parsed.replace(tzinfo=None)
                    result = datetime.time(parsed.hour, parsed.minute, parsed.second, parsed.microsecond)
                except Exception as e:
                    log_to_postgres('Value ' + unicode(value) + ' of type ' + unicode(type(value)) + ' can not be compared with a localtime field => ' +  unicode(e), ERROR)

        # we want a time with timezone
        elif column.type_name == 'time with time zone':
            # if we have a datetime, we only take the time
            if isinstance(value, datetime.datetime):
                result = value.replace(tzinfo=None).time()
            # Add the timezone if needed
            elif isinstance(value, datetime.time):
                result = value.time()
            # else we try to parse the string ...
            else:
                try:
                    parsed = parser.parse(unicode(value))
                    tz = parsed.tzinfo
                    if parsed.tzinfo is None :
                        tz = pytz.utc
                    result = datetime.time(parsed.hour, parsed.minute, parsed.second, parsed.microsecond, tz)
                except ValueError as e:
                    log_to_postgres('Value ' + unicode(value) + ' of type ' + unicode(type(value)) + ' can not be compared with a time field => ' +  unicode(e), ERROR)

        elif column.type_name == 'timestamp without time zone':
            # if we have a datetime, we remove the tz
            if isinstance(value, datetime.datetime):
                result = value.replace(tzinfo=None)
            # if we have date, we convert it to a datetime
            elif isinstance(value, datetime.date):
                result = datetime.datetime(value.year, value.month, value.day)
            # Otherwise we try to parse the value as a string
            else:
                try:
                    parsed = parser.parse(unicode(value))
                    if parsed.tzinfo is not None:
                        parsed = parsed.replace(tzinfo=None)
                    result = parsed
                except ValueError as e:
                    log_to_postgres('Value ' + unicode(value) + ' of type ' + unicode(type(value)) + ' can not be compared with a localdatetime field => ' +  unicode(e), ERROR)

        elif column.type_name == 'timestamp with time zone':
            # if we have a datetime
            if isinstance(value, datetime.datetime):
                result = value
                # check if a TZ is present
                if value.tzinfo is None:
                    result = value.replace(tzinfo=pytz.utc)
            # if we have date, we convert it to a datetime
            elif isinstance(value, datetime.date):
                result = datetime.datetime(value.year, value.month, value.day, 0, 0, 0, 0, pytz.utc)
            # Otherwise we try to parse the value as a string
            else:
                try:
                    parsed = parser.parse(unicode(value))
                    if parsed.tzinfo is None:
                        parsed = parsed.replace(tzinfo=pytz.utc)
                    result = parsed
                except ValueError as e:
                    log_to_postgres('Value ' + unicode(value) + ' of type ' + unicode(type(value)) + ' can not be compared with a datetime field => ' +  unicode(e), ERROR)

        log_to_postgres('Value is ' + unicode(result), DEBUG)
        return result

