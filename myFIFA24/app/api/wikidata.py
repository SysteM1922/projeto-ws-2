from SPARQLWrapper import SPARQLWrapper2
from .cache import Cache

sparql = SPARQLWrapper2("https://query.wikidata.org/sparql")

def get_team_info(team_name):

    query=f"""
    SELECT DISTINCT ?item
    WHERE {{
        ?item wdt:P31 wd:Q476028 .
        ?item rdfs:label ?name .
        FILTER(CONTAINS(?name, "{team_name}"))
    }}
    ORDER BY ?name
    LIMIT 1
    """

    result = Cache.get(query)
    if result:
        return result

    sparql.setQuery(query)

    try:
        team_q = sparql.query().bindings[0]["item"].value

        query_2 = f"""
        SELECT DISTINCT ?stad ?image ?coachName ?coachImage ?capacity
        WHERE {{
            OPTIONAL{{
                <{team_q}> wdt:P115 ?stadium .
                ?stadium rdfs:label ?stad .
                FILTER(LANG(?stad) = "en")
            }}
            OPTIONAL{{
                ?stadium wdt:P18 ?image .
            }}
            OPTIONAL{{
                ?stadium wdt:P1083 ?capacity .
            }}
            OPTIONAL{{
                <{team_q}> p:P286 ?card .
                ?card ps:P286 ?coach .
                ?card pq:P580 ?start_date .
                OPTIONAL{{
                    ?card pq:P582 ?end_date .
                }}
                ?coach rdfs:label ?coachName .
                FILTER(LANG(?coachName) = "en")
            }}
            OPTIONAL{{
                ?coach wdt:P18 ?coachImage .
            }}
        }}
        ORDER BY DESC(?start_date) DESC(?end_date)
        LIMIT 1
        """

        sparql.setQuery(query_2)

        results = sparql.query().bindings[0]

    except IndexError:
        results = {}

    ret = {
        "stadium": results["stad"].value if "stad" in results else None,
        "stadium_image": results["image"].value if "image" in results else None,
        "capacity": results["capacity"].value if "capacity" in results else None,
        "coach": results["coachName"].value if "coachName" in results else None,
        "coach_image": results["coachImage"].value if "coachImage" in results else None
    }

    Cache.set(query, ret)

    return ret

def get_player_info(player_name):

    query = f"""
    SELECT DISTINCT ?item
    WHERE {{
        ?item wdt:P106 wd:Q937857 .
        ?item wdt:P1559 ?o .
        ?item rdfs:label ?name .
        FILTER(LANG(?name) = "en")
        FILTER(CONTAINS(?name, "{player_name}"))
    }}
    LIMIT 1
    """

    result = Cache.get(query)
    if result:
        return result

    sparql.setQuery(query)

    try:

        player_q = sparql.query().bindings[0]["item"].value

        query_2 = f"""
        SELECT DISTINCT ?teamName ?teamImg
        WHERE{{
            <{player_q}> p:P54 ?card .
            ?card ps:P54 ?team .
            ?card pq:P580 ?start_date .
            OPTIONAL{{
                ?card pq:P582 ?end_date .
            }}
            ?team rdfs:label ?teamName .
            FILTER(LANG(?teamName) = "en")
            OPTIONAL{{
                ?team wdt:P154 ?teamImg .
            }}
        }}
        ORDER BY ?start_date ?end_date
        """

        sparql.setQuery(query_2)

        results = sparql.query().bindings

        ret = []

        team_names = []
        team_imgs = []

        for result in results:
            if "national" not in result["teamName"].value:
                team_names.append(result["teamName"].value)
                team_imgs.append(result["teamImg"].value if "teamImg" in result else None)

        last_team = "00000000"
        for team in reversed(list(team_names)):
            if last_team in team:
                team_imgs.pop(team_names.index(team))
                team_names.remove(team)
            else:
                last_team = team

        for i in range(len(team_names)):
            ret.append({
                "team": team_names[i],
                "team_image": team_imgs[i]
            })

    except IndexError:
        ret = []

    Cache.set(query, ret)

    return ret
        