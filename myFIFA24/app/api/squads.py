from .utils import select, update, ask

def get_squads_by_user_id(user_id: str) -> list[dict]:
    query = f"""
    PREFIX fifasqp: <http://fifa24/squad/pred/>

    SELECT ?squadId ?name ?formation
    WHERE {{
        ?squadId fifasqp:userId "{user_id}"^^xsd:string .
        ?squadId fifasqp:name ?name .
        ?squadId fifasqp:formation ?formation .
    }}
    ORDER BY ?name
    """

    result = select(query)

    for squad in result:
        squad["squadId"] = squad["squadId"].split("/")[-1]

    return result

def get_squad_by_guid(guid: str) -> dict:
    query = f"""
    PREFIX fifasqg: <http://fifa24/squad/guid/>
    PREFIX fifasqp: <http://fifa24/squad/pred/>
    PREFIX fifaspp: <http://fifa24/squad_player/pred/>
    PREFIX fifaplp: <http://fifa24/player/pred/>

    SELECT ?name ?formation ?playerId ?playerShield ?playerPos ?squadPlayerId ?userId
    WHERE {{
        fifasqg:{guid} fifasqp:name ?name .
        fifasqg:{guid} fifasqp:formation ?formation .
        OPTIONAL{{
            fifasqg:{guid} fifasqp:player ?squadPlayerId .
            ?squadPlayerId fifaspp:player ?playerId .
            ?squadPlayerId fifaspp:position ?playerPos .
            ?playerId fifaplp:shieldUrl ?playerShield .
        }}
        fifasqg:{guid} fifasqp:userId ?userId .
    }}
    """

    result = select(query)

    if not result:
        return None
    
    squad = {
        "id": guid,
        "name": result[0]["name"],
        "formation": result[0]["formation"],
        "players": [],
        "userId": result[0]["userId"],
    }

    for player in result:
        squad["players"].append({
            "id": player.get("playerId", "").split("/")[-1],
            "shield": player.get("playerShield"),
            "pos": player.get("playerPos"),
            "squadPlayerId": player.get("squadPlayerId"),
        })

    return squad

def create_squad(user_id: str, squad: dict) -> dict:

    status = ask(f"ASK {{ <http://fifa24/squad/guid/{user_id}_{squad["id"]}> ?p ?o }}")

    if status:
        return False

    squad_players = ""
    for player in squad["players"]:
        squad_players += f"fifasqg:{user_id}_{squad["id"]} fifasqp:player fifaspg:{squad["id"]}_{player["pos"]} .\n"
        squad_players += f"fifaspg:{squad["id"]}_{player["pos"]} fifaspp:player fifaplg:{player["id"]} .\n"
        squad_players += f"fifaspg:{squad["id"]}_{player["pos"]} fifaspp:position \"{player["pos"]}\"^^xsd:int .\n"

    query = f"""
    PREFIX fifasqg: <http://fifa24/squad/guid/>
    PREFIX fifasqp: <http://fifa24/squad/pred/>
    PREFIX fifaspg: <http://fifa24/squad_player/guid/>
    PREFIX fifaspp: <http://fifa24/squad_player/pred/>
    PREFIX fifaplg: <http://fifa24/player/guid/>

    INSERT DATA {{
    	fifasqg:{user_id}_{squad["id"]} fifasqp:name "{squad["name"]}"^^xsd:string .
        fifasqg:{user_id}_{squad["id"]} fifasqp:formation "{squad["formation"]}"^^xsd:string .
        fifasqg:{user_id}_{squad["id"]} fifasqp:userId "{user_id}"^^xsd:string .
        {squad_players}
    }}
    """

    update(query)

    return ask(f"ASK {{ <http://fifa24/squad/guid/{user_id}_{squad["id"]}> ?p ?o }}")

def update_squad(guid: str, squad: dict) -> dict:

    delete = ""
    insert = ""

    new_players = []
    old_players = []

    old_squad = get_squad_by_guid(guid)

    if not old_squad:
        return False
    
    if old_squad["name"] != squad["name"]:
        delete += f"""
        fifasqg:{guid} fifasqp:name "{old_squad["name"]}"^^xsd:string .
        """
        insert += f"""
        fifasqg:{guid} fifasqp:name "{squad["name"]}"^^xsd:string .
        """

    if old_squad["formation"] != squad["formation"]:
        delete += f"""
        fifasqg:{guid} fifasqp:formation "{old_squad["formation"]}"^^xsd:string .
        """
        insert += f"""
        fifasqg:{guid} fifasqp:formation "{squad["formation"]}"^^xsd:string .
        """
    
    old_players_by_pos = {player["pos"]: player for player in old_squad["players"]}
    new_players_by_pos = {player["pos"]: player for player in squad["players"]}
    
    for pos in old_players_by_pos:
        if pos in new_players_by_pos:
            if old_players_by_pos[pos]["id"] != new_players_by_pos[pos]["id"]:
                old_player = old_players_by_pos[pos]
                new_player = new_players_by_pos[pos]
                new_player["squadPlayerId"] = old_player["squadPlayerId"]
                old_players.append(old_player)
                new_players.append(new_player)

                delete += f"""
                fifasqg:{guid} fifasqp:player <{old_player["squadPlayerId"]}> .
                <{old_player["squadPlayerId"]}> ?p{old_player["pos"]} ?o{old_player["pos"]} .
                """
                if new_player["id"]:
                    insert += f"""
                    fifasqg:{guid} fifasqp:player fifaspg:{guid}_{new_player["pos"]} .
                    <{old_player["squadPlayerId"]}> fifaspp:player fifaplg:{new_player["id"]} .
                    <{old_player["squadPlayerId"]}> fifaspp:position "{new_player["pos"]}"^^xsd:int .
                    """
        else:
            old_player = old_players_by_pos[pos]
            old_players.append(old_player)
            delete += f"""
            fifasqg:{guid} fifasqp:player <{old_player["squadPlayerId"]}> .
            <{old_player["squadPlayerId"]}> ?p{old_player["pos"]} ?o{old_player["pos"]} .
            """

    for pos in new_players_by_pos:
        if pos not in old_players_by_pos:
            new_player = new_players_by_pos[pos]
            new_player["squadPlayerId"] = f'http://fifa24/squad_player/guid/{guid}_{new_player["pos"]}'
            new_players.append(new_player)
            insert += f"""
            fifasqg:{guid} fifasqp:player <{new_player["squadPlayerId"]}> .
            <{new_player["squadPlayerId"]}> fifaspp:player fifaplg:{new_player["id"]} .
            <{new_player["squadPlayerId"]}> fifaspp:position "{new_player["pos"]}"^^xsd:int .
            """

    query_delete = f"""
    PREFIX fifasqg: <http://fifa24/squad/guid/>
    PREFIX fifasqp: <http://fifa24/squad/pred/>

    DELETE {{
        {delete}
    }}
    WHERE {{
        {delete}
    }}
    """

    query_insert = f"""
    PREFIX fifasqg: <http://fifa24/squad/guid/>
    PREFIX fifasqp: <http://fifa24/squad/pred/>
    PREFIX fifaspg: <http://fifa24/squad_player/guid/>
    PREFIX fifaspp: <http://fifa24/squad_player/pred/>
    PREFIX fifaplg: <http://fifa24/player/guid/>

    INSERT DATA {{
        {insert}
    }}
    """

    update(query_delete)
        
    for player in old_players:
        if ask(f"ASK {{ <{player["squadPlayerId"]}> <http://fifa24/squad_player/pred/player> <http://fifa24/player/guid/{player["id"]}> }}"):
            return False

    update(query_insert)
        
    for player in new_players:
        if not ask(f"ASK {{ <{player["squadPlayerId"]}> <http://fifa24/squad_player/pred/player> <http://fifa24/player/guid/{player["id"]}> }}"):
            delete_squad(guid)
            create_squad(old_squad["userId"], old_squad)
            return False
        
    return True

def delete_squad(guid: str) -> dict:
    query_squad_players = f"""
    PREFIX fifasqg: <http://fifa24/squad/guid/>
    PREFIX fifasqp: <http://fifa24/squad/pred/>

    DELETE {{
        ?squadPlayerId ?p2 ?o2 .
    }}
    WHERE {{
        fifasqg:{guid} fifasqp:player ?squadPlayerId .
        ?squadPlayerId ?p2 ?o2 .
    }}
    """

    update(query_squad_players)

    query_squad = f"""
    PREFIX fifasqg: <http://fifa24/squad/guid/>
    PREFIX fifasqp: <http://fifa24/squad/pred/>

    DELETE {{
        fifasqg:{guid} ?p1 ?o1 .
    }}
    WHERE {{
        fifasqg:{guid} ?p1 ?o1 .
    }}
    """

    update(query_squad)

    return not ask(f"ASK {{ <http://fifa24/squad/guid/{guid}> ?p ?o }}")

