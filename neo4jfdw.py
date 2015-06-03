from multicorn import ForeignDataWrapper
from multicorn.utils import log_to_postgres, ERROR, WARNING, DEBUG
from py2neo import neo4j
import re


class Neo4jForeignDataWrapper(ForeignDataWrapper):
    """
    Neo4j FWD for Postgresql
    """

    def __init__(self, options, columns):
        # Calling super constructor
        super(Neo4jForeignDataWrapper, self).__init__(options, columns)

        # Managed server option
        if 'server' not in options:
            log_to_postgres('The server parameter is required and the default is "localhost"', WARNING)
        self.server = options.get("server", "localhost:7474")

        if 'port' not in options:
            log_to_postgres('The port parameter is required and the default is "7474"', WARNING)
        self.port = options.get("port", "7474")

        if 'user' not in options:
            log_to_postgres('The user parameter is required for Neo4j > 2.2', WARNING)
        self.user = options.get("user", None)

        if 'password' not in options:
            log_to_postgres('The password parameter is required for Neo4j > 2.2', WARNING)
        self.password = options.get("password", None)

        if 'cypher' not in options:
            log_to_postgres('The cypher parameter is required', ERROR)
        self.cypher = options.get("cypher", "MATCH (n) RETURN n LIMIT 100")

        # Setting table columns
        self.columns = columns

        # Create a py2neo graph instance
        if self.user and self.password:
            neo4j.authenticate(self.server + ":" + self.port, self.user, self.password)
        self.graph = neo4j.Graph("http://" + self.server + ":" + self.port + "/db/data/")


    def execute(self, quals, columns):

        log_to_postgres('Query Columns:  %s' % columns, DEBUG)
        log_to_postgres('Query Filters:  %s' % quals, DEBUG)

        statement = self.make_cypher(quals, columns)
        log_to_postgres('Neo4j query: ' + unicode(statement), DEBUG)

        # Execute & retrieve neo4j data
        for record in self.graph.cypher.stream(statement):
            line = {}
            for column_name in self.columns:
                if hasattr(record, column_name):
                    line[column_name] = record[column_name]
            yield line

    def make_cypher(self, quals, columns):
        """
        Override cypher query to add search criteria
        """
        cypher = self.cypher
        where_clause = 'AND '.join(self.extract_conditions(quals))

        pattern = re.compile('(.*)RETURN(.*)', re.IGNORECASE)
        match = pattern.match(self.cypher)
        if len(where_clause) > 0 and match:
            cypher = match.group(1) + "WITH" + match.group(2) + " WHERE " + where_clause + " RETURN " + ', '.join(columns)

        return cypher


    def extract_conditions(self, quals):
        """
        Build a neo4j search criteria string from a list of quals
        """
        conditions = []
        for qual in quals:
            conditions.append(self.make_condition(qual.field_name, qual.operator, qual.value))

        conditions = [x for x in conditions if x not in (None, '()')]
        return conditions


    def make_condition(self, key, operator, value):
        """
        Build a neo4j condition from a qual
        """
        if operator not in ('~~', '!~~', '~~*', '!~~*', '=', '<>', '>=', '<='):
            return ''

        condition = ''

        # Managed LIKE & ILIKE
        if operator in ('~~', '!~~', '~~*', '!~~*'):
            # Convert to cypher regex
            regex = value.replace('%', '.*')

            # For the negation, we prefix with NOT
            if operator in ('!~~', '!~~*'):
                condition += 'NOT '

            # Adding the variable name
            condition += key + "=~'"

            # If it's a ILIKE, we prefix regex with (?i)
            if operator in ('~~*', '!~~*'):
                condition += '(?i)'

            # We add the regex
            condition += regex + "'"

        else:
            condition = key + operator + value

        return condition

# def insert(self, new_values):
# def update(self, old_values, new_values):
#def delete(self, old_values):
      
            