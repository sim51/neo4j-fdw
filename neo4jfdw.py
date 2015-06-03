from multicorn import ForeignDataWrapper
from multicorn.utils import log_to_postgres, ERROR, WARNING, DEBUG
from py2neo import Graph

class Neo4jForeignDataWrapper(ForeignDataWrapper):
    """
    Neo4j FWD for Postgresql
    """
    
    def __init__(self, options, columns):
      super(Neo4jForeignDataWrapper, self).__init__(options, columns)
      
      if 'server' not in options:
            log_to_postgres('The server parameter is required and the default is http://localhost:7474', WARNING)
      self.server = options.get("server", "http://localhost:7474")
      
      if 'user' not in options:
          log_to_postgres('The user parameter is required for Neo4j > 2.2', WARNING)
      self.user = options.get("user", None)
      
      if 'password' not in options:
          log_to_postgres('The password parameter is required for Neo4j > 2.2', WARNING)
      self.password = options.get("password", None)
    
      if 'query' not in options:
          log_to_postgres('The query parameter is required', ERROR)
      self.query = options.get("query", None)
      
      self.columns = columns
    
    
    def execute(self, quals, columns):
        if self.query:
            statement = self.query
        else:
            statement = "MATCH (n) RETURN n LIMIT 100" 
            
        log_to_postgres('Neo4j query: ' + unicode(statement), DEBUG)
        
        # Manage py2neo authentification
        if self.user && self.password:
            authenticate(self.server, self.user, self.password)
	
	# Make the query
        graph = Graph(self.server + "/db/data/")
        for record in graph.cypher.stream(statement):
	    line = {}
	    for column_name in self.columns:
                line[column_name] = record[column_name]
            yield line
            