import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
import time

endpoint = "http://localhost:7200"
repo_name = "fifa24"
client = ApiClient(endpoint=endpoint)
accessor = GraphDBApi(client)
    
def update(query: str) -> dict:
    payload = {
        "update": query
    }
    result = accessor.sparql_update(body=payload, repo_name=repo_name)

    try:
        return json.loads(result)
    
    except Exception:
        return None
    
inference_teammates = """
PREFIX fifaplp: <http://fifa24/player/pred/>
PREFIX fifaplg: <http://fifa24/player/guid/>
PREFIX fifarel: <http://fifa24/relationship/>

INSERT {
    ?player1 fifarel:teammate ?player2
}
WHERE {
    {
        ?player1 a fifaplg:Player .
        ?player2 a fifaplg:Player .
    	FILTER(?player1!=?player2)
    }
    ?player1 fifaplp:team ?team1 .
    ?player2 fifaplp:team ?team1 .
}
"""

print("Inferencing teammates... (Aprox. 1 minute)")
start = time.time()
update(inference_teammates)
end = time.time()
print(f"Done! Inference took {end - start} seconds.\n")

inference_gender_and_leagues = """
PREFIX fifaplg: <http://fifa24/player/guid/>
PREFIX fifaplp: <http://fifa24/player/pred/>
PREFIX fifalp: <http://fifa24/league/pred/>
PREFIX fifatp: <http://fifa24/team/pred/>

INSERT {
    ?league fifalp:gender ?gender .
    ?player fifaplp:league ?league .
    ?team fifatp:gender ?gender .
}
WHERE {
	?player a fifaplg:Player .
	?player fifaplp:gender ?gender .
	?player fifaplp:team ?team .
    ?team fifatp:league ?league .
}"""

print("Inferencing team gender, league gender and player league... ")
start = time.time()
update(inference_gender_and_leagues)
end = time.time()
print(f"Done! Inference took {end - start} seconds.\n")

