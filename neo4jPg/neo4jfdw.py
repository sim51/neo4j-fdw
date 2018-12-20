from multicorn import ForeignDataWrapper, ANY, ALL
from multicorn.utils import log_to_postgres, ERROR, WARNING, DEBUG, INFO
from neo4j import GraphDatabase, basic_auth, CypherError
import re

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
        for index, qual in enumerate(quals):
            params[unicode(index)] = qual.value
        log_to_postgres('Neo4j query is : ' + unicode(statement), DEBUG)
        log_to_postgres('With params : ' + unicode(params), DEBUG)

        # Execute & retrieve neo4j data
        session = self.driver.session()
        try:
            for record in session.run(statement, params):
                line = {}
                for column_name in columns:
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
        where_clause = ' AND '.join(self.extract_conditions(quals))
        log_to_postgres('Where clause is : ' + unicode(where_clause), DEBUG)

        pattern = re.compile('(.*)RETURN(.*)', re.IGNORECASE|re.MULTILINE|re.DOTALL)
        match = pattern.match(self.cypher)

        if len(where_clause) > 0 and match:
            cypher = match.group(1) + "WITH" + match.group(2) + " WHERE " + where_clause + " RETURN " + ', '.join(columns)

        if sortkeys is not None:
            orders = []
            for sortkey in sortkeys:
                if sortkey.is_reversed:
                    orders.append(sortkey.attname + ' DESC')
                else:
                    orders.append(sortkey.attname)
            cypher = cypher + ' ORDER BY ' + ', '.join(orders)

        return cypher


    def extract_conditions(self, quals):
        """
        Build a neo4j search criteria string from a list of quals
        """
        conditions = []
        for index, qual in enumerate(quals):
            # quals is a list with ANY
            if qual.list_any_or_all == ANY:
                values = [
                    '( %s )' % self.make_condition(qual.field_name, qual.operator[0], value, unicode(index) + '[' + unicode(array_index) + ']')
                    for array_index, value in enumerate(qual.value)
                ]
                conditions.append( ' ( ' +  ' OR '.join(values) + ' ) ')
            # quals is a list with ALL
            elif qual.list_any_or_all == ALL:
                conditions.extend([
                    self.make_condition(qual.field_name, qual.operator[0], value, unicode(index) + '[' + unicode(array_index) + ']')
                    for array_index, value in enumerate(qual.value)
                ])
            # quals is just a string
            else:
                conditions.append(self.make_condition( qual.field_name, qual.operator, qual.value, index))

        conditions = [x for x in conditions if x not in (None, '()', '')]
        return conditions


    def make_condition(self, field_name, operator, value, index):
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
            condition = field_name + ' ' + operator + "$" + unicode(index) + ""

        log_to_postgres('Condition is : ' + unicode(condition), DEBUG)
        return condition

# def insert(self, new_values):
# def update(self, old_values, new_values):
# def delete(self, old_values):
