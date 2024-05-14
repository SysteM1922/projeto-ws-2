import json
import time
from .utils import select

cache = {}

def get_nationalities() -> list[dict]:
    query = """
        PREFIX fifanp: <http://fifa24/nationality/pred/>

        SELECT ?nationality ?label
        WHERE {
            ?nationality fifanp:label ?label .
        }
        ORDER BY ?label
        """
    
    if query in cache:
        result = cache[query]["result"]

        for query in list(cache):
            if time.time() - cache[query]["time"] > 300:
                del cache[query]

        return result
    
    result = select(query)

    for nationality in result:
        nationality["id"] = nationality["nationality"].split("/")[-1]

    cache[query] = {"time": time.time(), "result": result}

    return result

def get_genders() -> list[dict]:
    query = """
        PREFIX fifagp: <http://fifa24/gender/pred/>

        SELECT ?gender ?label
        WHERE {
            ?gender fifagp:label ?label .
        }
        ORDER BY ?label
        """
    
    if query in cache:
        result = cache[query]["result"]

        for query in list(cache):
            if time.time() - cache[query]["time"] > 300:
                del cache[query]

        return result
    
    result = select(query)

    for gender in result:
        gender["id"] = gender["gender"].split("/")[-1]

    cache[query] = {"time": time.time(), "result": result}

    return result

def get_positions() -> list[dict]:
    
    query = """
        PREFIX fifapop: <http://fifa24/position/pred/>

        SELECT ?positionid ?label
        WHERE {
            ?positionid fifapop:shortLabel ?label .
        }
        """
    
    if query in list(cache):
        result = cache[query]["result"]

        for query in cache:
            if time.time() - cache[query]["time"] > 300:
                del cache[query]

        return result
    
    ret = [{"label": "GK", "id": None},
              {"label": "CB", "id": None},
              {"label": "RB", "id": None},
              {"label": "RWB", "id": None},
              {"label": "LB", "id": None},
              {"label": "LWB", "id": None},
              {"label": "CDM", "id": None},
              {"label": "CM", "id": None},
              {"label": "CAM", "id": None},
              {"label": "RM", "id": None},
              {"label": "LM", "id": None},
              {"label": "LW", "id": None},
              {"label": "RW", "id": None},
              {"label": "CF", "id": None},
              {"label": "ST", "id": None},
              ]
    
    result = select(query)

    for position in ret:
        for pos in result:
            if pos["label"] == position["label"]:
                position["id"] = pos["positionid"].split("/")[-1]

    cache[query] = {"time": time.time(), "result": ret}

    return ret

def get_total_players(props: dict = None) -> int:

    name = ""
    gender = ""
    nationality = ""
    team = ""
    position = ""
    extra_position = ""
    
    if props: 
        for prop in props:
            match prop["prop"]:
                case "name":
                    name += f'FILTER REGEX(?name, "{prop["value"]}", "i")'
                case "nationality":
                    nationality += f'FILTER(?nationalityid = fifang:{prop["value"]})'
                case "league":
                    team = f'?teamid fifatp:league fifalg:{prop["value"]} .'
                case "team":
                    team = f'FILTER(?teamid = fifatg:{prop["value"]})'
                case "gender":
                    gender = f'FILTER(?genderid = fifagg:{prop["value"]})'
                case "position":
                    position = f'FILTER(?positionid = fifapog:{prop["value"]})'
                    extra_position = f"""UNION {{
                    ?playerid fifaplp:altPos fifapog:{prop["value"]} .
                    ?playerid fifaplp:firstName ?fName .
                    ?playerid fifaplp:lastName ?lName .
                    OPTIONAL {{ ?playerid fifaplp:commonName ?cName . }}
                    }}"""  

    query = f"""
        PREFIX fifaplp: <http://fifa24/player/pred/>
        PREFIX fifang: <http://fifa24/nationality/guid/>
        PREFIX fifalg: <http://fifa24/league/guid/>
        PREFIX fifatg: <http://fifa24/team/guid/>
        PREFIX fifapog: <http://fifa24/position/guid/>
        PREFIX fifagg: <http://fifa24/gender/guid/>

        SELECT (COUNT(?playerid) AS ?total)
        WHERE {{
            {{
            ?playerid fifaplp:gender ?genderid .
            {gender}
            ?playerid fifaplp:position ?positionid .
            {position}
            ?playerid fifaplp:nationality ?nationalityid .
            {nationality}
            ?playerid fifaplp:team ?teamid .
            {team}
            ?playerid fifaplp:firstName ?fName .
            ?playerid fifaplp:lastName ?lName .
            OPTIONAL {{ ?playerid fifaplp:commonName ?cName . }}
            {name}
            }}
            {extra_position}
        }}
        """
    
    result = select(query)

    return int(result[0]["total"])

def get_players_by_prop(start: int = 0, limit: int = 30, props: dict = None) -> list[dict]:

    order = "DESC(?ovr) ?name"
    name = ""
    gender = ""
    nationality = ""
    team = ""
    position = ""
    extra_position = ""

    if props:
        for prop in props:
            match prop["prop"]:
                case "name":
                    name += f'FILTER REGEX(?name, "{prop["value"]}", "i")'
                case "nationality":
                    nationality += f'FILTER(?nationalityid = fifang:{prop["value"]})'
                case "league":
                    team = f'?teamid fifatp:league fifalg:{prop["value"]} .'
                case "team":
                    team = f'FILTER(?teamid = fifatg:{prop["value"]})'
                case "gender":
                    gender = f'FILTER(?genderid = fifagg:{prop["value"]})'
                case "position":
                    position = f'FILTER(?positionid = fifapog:{prop["value"]})'
                    extra_position = f"""UNION {{
                    ?playerid fifaplp:gender ?genderid .
                    ?genderid fifagp:label ?gender .
                    ?playerid fifaplp:altPos fifapog:{prop["value"]} .
                    ?playerid fifaplp:position ?positionid .
                    ?positionid fifapop:shortLabel ?position .
                    ?playerid fifaplp:nationality ?nationalityid .
                    ?nationalityid fifanp:imageUrl ?flag .
                    ?nationalityid fifanp:label ?nationality .
                    ?teamid fifatp:label ?team .
                    ?playerid fifaplp:team ?teamid .
                    ?teamid fifatp:imageUrl ?logo .
                    ?playerid fifaplp:overallRating ?ovr .
                    ?playerid fifaplp:firstName ?fName .
                    ?playerid fifaplp:lastName ?lName .
                    OPTIONAL {{ ?playerid fifaplp:commonName ?cName . }}
                    BIND(COALESCE(?cName, CONCAT(?fName, " ", ?lName)) AS ?name)
                    ?playerid fifaplp:skillMoves ?skills .
                    ?playerid fifaplp:weakFootAbility ?weakfoot .
                    ?playerid fifaplp:attackingWorkRate ?attwr .
                    ?playerid fifaplp:defensiveWorkRate ?defwr .
                    ?playerid fifaplp:avatarUrl ?image .
                    ?playerid fifaplp:stat ?stat .
                    }}"""
                case "order":
                    signal = "ASC" if prop["value"][0] == "-" else "DESC"
                    ord = prop["value"][1:]
                    if ord == "ovr":
                        order = f"{signal}(?ovr) ?name"
                    elif ord == "name":
                        order = f"{signal}(?name) DESC(?ovr)"
                    else:
                        order = f"{signal}(?{ord}) DESC(?ovr) ?name"

    query = f"""
        PREFIX fifaplp: <http://fifa24/player/pred/>
        PREFIX fifang: <http://fifa24/nationality/guid/>
        PREFIX fifanp: <http://fifa24/nationality/pred/>
        PREFIX fifalg: <http://fifa24/league/guid/>
        PREFIX fifatg: <http://fifa24/team/guid/>
        PREFIX fifatp: <http://fifa24/team/pred/>
        PREFIX fifapog: <http://fifa24/position/guid/>
        PREFIX fifapop: <http://fifa24/position/pred/>
        PREFIX fifagg: <http://fifa24/gender/guid/>
        PREFIX fifagp: <http://fifa24/gender/pred/>

        SELECT ?playerid ?name ?flag ?nationality ?teamid ?team ?logo ?position ?ovr ?gender ?image ?skills ?weakfoot ?attwr ?defwr (CONCAT("{{",GROUP_CONCAT(?stat; separator=", "), "}}") AS ?stats)
        WHERE {{
            {{
            ?playerid fifaplp:gender ?genderid .
            {gender}
            ?genderid fifagp:label ?gender .
            ?playerid fifaplp:position ?positionid .
            {position}
            ?positionid fifapop:shortLabel ?position .
            ?playerid fifaplp:nationality ?nationalityid .
            {nationality}
            ?nationalityid fifanp:imageUrl ?flag .
            ?nationalityid fifanp:label ?nationality .
            ?playerid fifaplp:team ?teamid .
            {team}
            ?teamid fifatp:label ?team .
            ?teamid fifatp:imageUrl ?logo .
            ?playerid fifaplp:overallRating ?ovr .
            ?playerid fifaplp:firstName ?fName .
            ?playerid fifaplp:lastName ?lName .
            OPTIONAL {{ ?playerid fifaplp:commonName ?cName . }}
            {name}
            BIND(COALESCE(?cName, CONCAT(?fName, " ", ?lName)) AS ?name)
            ?playerid fifaplp:skillMoves ?skills .
            ?playerid fifaplp:weakFootAbility ?weakfoot .
            ?playerid fifaplp:attackingWorkRate ?attwr .
            ?playerid fifaplp:defensiveWorkRate ?defwr .
            ?playerid fifaplp:avatarUrl ?image .
            ?playerid fifaplp:stat ?stat .
            }}
            {extra_position}
        }}
        GROUP BY ?playerid ?name ?flag ?nationality ?teamid ?team ?logo ?position ?ovr ?gender ?image ?skills ?weakfoot ?attwr ?defwr
        ORDER BY {order}
        OFFSET {start}
        LIMIT {limit}
        """
    
    if query in list(cache):

        result = cache[query]["result"]
        for query in cache:
            if time.time() - cache[query]["time"] > 300:
                del cache[query]
        
        return result

    result = select(query)

    for player in result:
        player["id"] = player["playerid"].split("/")[-1]
        player["teamid"] = player["teamid"].split("/")[-1]
        player["stats"] = json.loads(player["stats"])

    cache[query] = {"time": time.time(), "result": result}

    return result

def get_player_by_guid(guid: str) -> dict:
    query = f"""
        PREFIX fifaplp: <http://fifa24/player/pred/>
        PREFIX fifaplg: <http://fifa24/player/guid/>
        PREFIX fifanp: <http://fifa24/nationality/pred/>
        PREFIX fifatp: <http://fifa24/team/pred/>
        PREFIX fifapop: <http://fifa24/position/pred/>
        PREFIX fifagp: <http://fifa24/gender/pred/>

        SELECT ?playerid ?name ?position ?nationality ?flag ?teamid ?team ?teamName ?gender ?card ?birth ?height ?weight ?skills ?weakfoot ?foot ?attwr ?defwr (CONCAT("{{",GROUP_CONCAT(?stat; separator=", "), "}}") AS ?stats)
        WHERE {{
            ?playerid fifaplp:gender ?genderid .
            FILTER(?playerid = fifaplg:{guid})
            ?playerid fifaplp:position ?positionid .
            ?positionid fifapop:shortLabel ?position .
            ?genderid fifagp:label ?gender .
            ?playerid fifaplp:nationality ?nationalityid .
            ?nationalityid fifanp:label ?nationality .
            ?nationalityid fifanp:imageUrl ?flag .
            ?playerid fifaplp:team ?teamid .
            ?teamid fifatp:imageUrl ?team .
            ?teamid fifatp:label ?teamName .
            ?playerid fifaplp:firstName ?fName .
            ?playerid fifaplp:lastName ?lName .
            OPTIONAL {{ ?playerid fifaplp:commonName ?cName . }}
            BIND(COALESCE(?cName, CONCAT(?fName, " ", ?lName)) AS ?name)
            ?playerid fifaplp:shieldUrl ?card .
            ?playerid fifaplp:birthdate ?birth .
            ?playerid fifaplp:height ?height .
            ?playerid fifaplp:weight ?weight .
            ?playerid fifaplp:skillMoves ?skills .
            ?playerid fifaplp:weakFootAbility ?weakfoot .
            ?playerid fifaplp:preferredFoot ?foot .
            ?playerid fifaplp:attackingWorkRate ?attwr .
            ?playerid fifaplp:defensiveWorkRate ?defwr .
            ?playerid fifaplp:stat ?stat .
        }}
        GROUP BY ?playerid ?name ?position ?nationality ?flag ?teamid ?team ?teamName ?gender ?card ?birth ?height ?weight ?skills ?weakfoot ?foot ?attwr ?defwr
        LIMIT 1
        """

    result = select(query)

    if not result:
        return None
    
    player = result[0]
    player["stats"] = json.loads(player["stats"])
    player["teamid"] = player["teamid"].split("/")[-1]

    return player

def get_players_by_team_guid(guid: str) -> list[dict]:
    query = f"""
        PREFIX fifaplp: <http://fifa24/player/pred/>
        PREFIX fifanp: <http://fifa24/nationality/pred/>
        PREFIX fifatg: <http://fifa24/team/guid/>
        PREFIX fifatp: <http://fifa24/team/pred/>
        PREFIX fifapop: <http://fifa24/position/pred/>
        PREFIX fifagp: <http://fifa24/gender/pred/>

        SELECT ?playerid ?name ?flag ?nationality ?position ?ovr ?image ?skills ?weakfoot ?attwr ?defwr (CONCAT("{{",GROUP_CONCAT(?stat; separator=", "), "}}") AS ?stats)
        WHERE {{
            ?playerid fifaplp:position ?positionid .
            ?positionid fifapop:shortLabel ?position .
            ?playerid fifaplp:nationality ?nationalityid .
            ?nationalityid fifanp:imageUrl ?flag .
            ?nationalityid fifanp:label ?nationality .
            ?playerid fifaplp:team ?teamid .
            FILTER(?teamid = fifatg:{guid})
            ?playerid fifaplp:overallRating ?ovr .
            ?playerid fifaplp:firstName ?fName .
            ?playerid fifaplp:lastName ?lName .
            OPTIONAL {{ ?playerid fifaplp:commonName ?cName . }}
            BIND(COALESCE(?cName, CONCAT(?fName, " ", ?lName)) AS ?name)
            ?playerid fifaplp:skillMoves ?skills .
            ?playerid fifaplp:weakFootAbility ?weakfoot .
            ?playerid fifaplp:attackingWorkRate ?attwr .
            ?playerid fifaplp:defensiveWorkRate ?defwr .
            ?playerid fifaplp:avatarUrl ?image .
            ?playerid fifaplp:stat ?stat .
        }}
        GROUP BY ?playerid ?name ?flag ?nationality ?position ?ovr ?image ?skills ?weakfoot ?attwr ?defwr
        ORDER BY DESC(?ovr) ?name
        """

    if query in cache:
        result = cache[query]["result"]

        for query in list(cache):
            if time.time() - cache[query]["time"] > 300:
                del cache[query]

        return result
    
    result = select(query)

    for player in result:
        player["id"] = player["playerid"].split("/")[-1]
        player["stats"] = json.loads(player["stats"])

    cache[query] = {"time": time.time(), "result": result}

    return result

def get_players_base_info_by_name(name: str) -> dict:
    query = f"""
        PREFIX fifaplp: <http://fifa24/player/pred/>

        SELECT ?playerid ?name ?ovr ?image ?shield
        WHERE {{
            ?playerid fifaplp:overallRating ?ovr .
            ?playerid fifaplp:firstName ?fName .
            ?playerid fifaplp:lastName ?lName .
            OPTIONAL {{ ?playerid fifaplp:commonName ?cName . }}
            BIND(COALESCE(?cName, CONCAT(?fName, " ", ?lName)) AS ?name)
            FILTER REGEX(?name, "{name}", "i")
            ?playerid fifaplp:avatarUrl ?image .
            ?playerid fifaplp:shieldUrl ?shield .
        }}
        """
    
    return select(query)
