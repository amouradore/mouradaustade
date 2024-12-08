from flask import Flask, jsonify
from flask_cors import CORS
import requests
from datetime import datetime
import pytz

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "API is running"})

@app.route('/api/matches/<date>')
def get_matches(date):
    api_key = '3f9226033c324e538d8d34a36118390b'
    base_url = 'https://api.football-data.org/v4'
    
    try:
        # Convertir la date reçue
        selected_date = datetime.strptime(date, '%Y-%m-%d')
        
        headers = {
            'X-Auth-Token': api_key,
            'Accept': 'application/json'
        }
        
        params = {
            'date': selected_date.strftime('%Y-%m-%d'),
            'limit': 100
        }
        
        all_matches = []
        page = 1
        
        while True:
            params['page'] = page
            response = requests.get(f'{base_url}/matches', headers=headers, params=params)
            data = response.json()
            
            if 'matches' not in data or not data['matches']:
                break
                
            for match in data['matches']:
                match_date = datetime.strptime(match['utcDate'], '%Y-%m-%dT%H:%M:%SZ')
                user_timezone = pytz.timezone('Europe/Paris')
                match_date_local = match_date.replace(tzinfo=pytz.utc).astimezone(user_timezone)
                
                competition_name = match.get('competition', {}).get('name', 'Compétition inconnue')
                
                match_info = {
                    'team1': match['homeTeam']['name'],
                    'team2': match['awayTeam']['name'],
                    'team1_logo': match['homeTeam'].get('crest', ''),
                    'team2_logo': match['awayTeam'].get('crest', ''),
                    'time': match_date_local.strftime('%H:%M'),
                    'status': match['status'],
                    'score': f"{match.get('score', {}).get('fullTime', {}).get('home', '-')}-{match.get('score', {}).get('fullTime', {}).get('away', '-')}",
                    'competition': competition_name
                }
                all_matches.append(match_info)
            
            page += 1
            if not data.get('hasMore', False):
                break
        
        if not all_matches:
            return jsonify([{
                'team1': "Aucun match trouvé",
                'team2': "pour cette date",
                'time': "--:--",
                'status': "Info",
                'score': "-",
                'competition': ""
            }])
        
        return jsonify(all_matches)
        
    except Exception as e:
        print(f"Erreur lors de la récupération des matchs: {e}")
        return jsonify([{
            'team1': "Erreur de chargement",
            'team2': "Veuillez réessayer",
            'time': "--:--",
            'status': "Erreur",
            'score': "-",
            'competition': ""
        }]), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
