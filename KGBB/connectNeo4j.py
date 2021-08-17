# .\.venvs\lpthw\Scripts\activate
# $env:PYTHONPATH = "$env:PYTHONPATH;."


# Connection info to Neo4j UseCaseKGBB_Database pw:test
# username: python    password: useCaseKGBB   uri: bolt://localhost:7687



from neo4j import GraphDatabase


class Neo4jConnection:

    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd

    def query(self, query, db=None):
        try:
            driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
            session = driver.session(database=db) if db is not None else driver.session()
            response = session.run(query).data()
            driver.close()
        except Exception as e:
            print(e)
            return None
        if len(response) == 0:
            return None
        print(response)
        result = response
        return result
