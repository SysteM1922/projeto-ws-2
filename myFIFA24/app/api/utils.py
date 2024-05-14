import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient

endpoint = "http://localhost:7200"
repo_name = "fifa24"
client = ApiClient(endpoint=endpoint)
accessor = GraphDBApi(client)

def select(query: str) -> dict:
    payload = {
        "query": query
    }
    result = accessor.sparql_select(body=payload, repo_name=repo_name)

    try:
        result = json.loads(result)["results"]["bindings"]
        for res in result:
            for key in res:
                res[key] = res[key]["value"]

        return result
    
    except Exception:
        return []
    
def ask(query: str) -> dict:
    payload = {
        "query": query
    }
    result = accessor.sparql_select(body=payload, repo_name=repo_name)

    try:
        return json.loads(result)["boolean"]
    
    except Exception:
        return None
    
def update(query: str) -> dict:
    payload = {
        "update": query
    }
    result = accessor.sparql_update(body=payload, repo_name=repo_name)

    try:
        return json.loads(result)
    
    except Exception:
        return None