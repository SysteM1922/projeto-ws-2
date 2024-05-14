from .utils import select

def get_leagues() -> list[dict]:
    query = """
    PREFIX fifalg: <http://fifa24/league/guid/> 
    PREFIX fifalp: <http://fifa24/league/pred/>

    SELECT ?league ?label ?image
    WHERE {
	    ?league fifalp:label ?label .
	    ?league fifalp:imageUrl ?image .
    }
    ORDER BY ?label
    """
    
    result = select(query)

    for league in result:
        league['id'] = league['league'].split('/')[-1]

    return result


def get_leagues_by_name(name: str) -> dict:
    query = f"""
    PREFIX fifalg: <http://fifa24/league/guid/>
    PREFIX fifalp: <http://fifa24/league/pred/>

    SELECT ?league ?label ?image
    WHERE {{
        ?league fifalp:label ?label .
        FILTER regex(?label, "{name}", "i")
        ?league fifalp:imageUrl ?image .
    }}
    ORDER BY ?label
    """

    result = select(query)

    for league in result:
        league['id'] = league['league'].split('/')[-1]

    return result