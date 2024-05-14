import requests
import json
import os

def filter_data(data):
    del data['playStyle']
    del data['playStylePlus']
    del data['team']['isPopular']
    del data['position']['positionType']

    new_stats = []
    for key in data['stats']:
        new_stats.append({"label": key, "value": data['stats'][key]["value"]})
    data['stats'] = new_stats

    return data

def get_data():

    if os.path.exists(filename):
        print('File already exists\nUsing existing file')
        return
    
    url = 'https://drop-api.ea.com/rating/fc-24?locale=en&limit=100'
    for i in range(0, 17327, 100):
        print(f'Getting data from {i} to {i + 100}')
        response = requests.get(url, params={'offset': i})
        data = response.json()
        with open(filename, 'a') as file:
            for item in data['items']:
                item = filter_data(item)
                json.dump(item, file)
                file.write('\n')

def filter_entities():

    global players
    global positions
    global genders
    global nationalities
    global teams
    global leagues

    positions_ids = set()
    genders_ids = set()
    nationalities_ids = set()
    teams_ids = set()
    leagues_names = set()

    with open(filename, 'r') as file:
        for line in file:

            data = json.loads(line)

            del data['rank']

            alt_positions = data.pop("alternatePositions")
            if alt_positions:
                data["alternatePositions"] = [position["id"] for position in alt_positions]
                for position in alt_positions:
                    if position["id"] not in positions_ids:
                        positions_ids.add(position["id"])
                        positions.append(position)
            else:
                data["alternatePositions"] = []

            position = data.pop("position")
            if position["id"] not in positions_ids:
                positions_ids.add(position["id"])
                positions.append(position)
            data["position"] = position["id"]

            gender = data.pop("gender")
            if gender["id"] not in genders_ids:
                genders_ids.add(gender["id"])
                genders.append(gender)
            data["gender"] = gender["id"]

            nationality = data.pop("nationality")
            if nationality["id"] not in nationalities_ids:
                nationalities_ids.add(nationality["id"])
                nationalities.append(nationality)
            data["nationality"] = nationality["id"]
            
            league = data.pop("leagueName")
            if league not in leagues_names:
                leagues[league] = {"id": len(leagues_names), "label": league}
                leagues_names.add(league)
            league_id = leagues[league]["id"]
            
            team = data.pop("team")
            data["team"] = team["id"]
            if team["id"] not in teams_ids:
                teams_ids.add(team["id"])
                teams.append({"id": team["id"], "label": team["label"], "imageUrl": team["imageUrl"], "league": league_id})

            players.append(data)

def to_n3_rdf():

    global players
    global positions
    global genders
    global nationalities
    global teams
    global leagues

    with open('fifa.n3', 'w', encoding='utf-8') as file:
        string_to_write = '@prefix fifaplg: <http://fifa24/player/guid/> .\n'
        string_to_write += '@prefix fifaplp: <http://fifa24/player/pred/> .\n'
        string_to_write += '@prefix fifapog: <http://fifa24/position/guid/> .\n'
        string_to_write += '@prefix fifapop: <http://fifa24/position/pred/> .\n'
        string_to_write += '@prefix fifagg: <http://fifa24/gender/guid/> .\n'
        string_to_write += '@prefix fifagp: <http://fifa24/gender/pred/> .\n'
        string_to_write += '@prefix fifang: <http://fifa24/nationality/guid/> .\n'
        string_to_write += '@prefix fifanp: <http://fifa24/nationality/pred/> .\n'
        string_to_write += '@prefix fifatg: <http://fifa24/team/guid/> .\n'
        string_to_write += '@prefix fifatp: <http://fifa24/team/pred/> .\n'
        string_to_write += '@prefix fifalg: <http://fifa24/league/guid/> .\n'
        string_to_write += '@prefix fifalp: <http://fifa24/league/pred/> .\n'
        string_to_write += '@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n'
        file.write(string_to_write)

        leagues_file = open('leagues.json', 'r', encoding='utf-8')
        leagues_json = json.load(leagues_file)
        leagues_file.close()

        string_to_write = "\n"
        for league in leagues:
            string_to_write += f'fifalg:{leagues[league]["id"]} fifalp:label "{league}"^^xsd:string;\nfifalp:imageUrl "{leagues_json[league]}"^^xsd:string.\n'
        file.write(string_to_write)

        string_to_write = "\n"
        for nationality in nationalities:
            string_to_write += f'fifang:{nationality["id"]} fifanp:label "{nationality["label"]}"^^xsd:string;\nfifanp:imageUrl "{nationality["imageUrl"]}"^^xsd:string.\n'
        file.write(string_to_write)

        string_to_write = "\n"
        for gender in genders:
            string_to_write += f'fifagg:{gender["id"]} fifagp:label "{gender["label"]}"^^xsd:string.\n'
        file.write(string_to_write)

        string_to_write = "\n"
        for position in positions:
            string_to_write += f'fifapog:{position["id"]} fifapop:label "{position["label"]}"^^xsd:string;\nfifapop:shortLabel "{position["shortLabel"]}"^^xsd:string.\n'
        file.write(string_to_write)

        string_to_write = "\n"
        for team in teams:
            string_to_write += f'fifatg:{team["id"]} fifatp:label "{team["label"]}"^^xsd:string;\nfifatp:imageUrl "{team["imageUrl"]}"^^xsd:string;\nfifatp:league fifalg:{team["league"]}.\n'
        file.write(string_to_write)

        for player in players:
            string_to_write = "\n"
            string_to_write += f'fifaplg:{player["id"]} fifaplp:overallRating "{player["overallRating"]}"^^xsd:int;\n'
            string_to_write += f'fifaplp:firstName "{player["firstName"]}"^^xsd:string;\n'
            string_to_write += f'fifaplp:lastName "{player["lastName"]}"^^xsd:string;\n'
            if player["commonName"]:
                string_to_write += f'fifaplp:commonName "{player["commonName"]}"^^xsd:string;\n'
            string_to_write += f'fifaplp:birthdate "{player["birthdate"]}"^^xsd:date;\n'
            string_to_write += f'fifaplp:height "{player["height"]}"^^xsd:int;\n'
            string_to_write += f'fifaplp:skillMoves "{player["skillMoves"]}"^^xsd:int;\n'
            string_to_write += f'fifaplp:weakFootAbility "{player["weakFootAbility"]}"^^xsd:int;\n'
            string_to_write += f'fifaplp:attackingWorkRate "{player["attackingWorkRate"]}"^^xsd:int;\n'
            string_to_write += f'fifaplp:defensiveWorkRate "{player["defensiveWorkRate"]}"^^xsd:int;\n'
            string_to_write += f'fifaplp:preferredFoot "{player["preferredFoot"]}"^^xsd:int;\n'
            string_to_write += f'fifaplp:weight "{player["weight"]}"^^xsd:int;\n'
            string_to_write += f'fifaplp:avatarUrl "{player["avatarUrl"]}"^^xsd:string;\n'
            string_to_write += f'fifaplp:shieldUrl "{player["shieldUrl"]}"^^xsd:string;\n'
            string_to_write += f'fifaplp:position fifapog:{player["position"]};\n'
            string_to_write += f'fifaplp:gender fifagg:{player["gender"]};\n'
            string_to_write += f'fifaplp:nationality fifang:{player["nationality"]};\n'
            string_to_write += f'fifaplp:team fifatg:{player["team"]};\n'

            if player["alternatePositions"]:
                string_to_write += f'fifaplp:altPos '
                for position in player["alternatePositions"]:
                    string_to_write += f'fifapog:{position},'
                string_to_write = string_to_write[:-1] + ';\n'

            string_to_write += f'fifaplp:stat '
            for stat in player["stats"]:
                string_to_write += f'"\\"{stat["label"]}\\":{stat["value"]}",'
            string_to_write = string_to_write[:-1] + '.\n'

            file.write(string_to_write)


filename = 'fifa.json'

players = []
positions = []
genders = []
nationalities = []
teams = []
leagues = dict()

def main():
    get_data()

    filter_entities()

    to_n3_rdf()

if __name__ == '__main__':
    main()