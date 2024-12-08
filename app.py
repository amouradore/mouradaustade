# app.py
from flask import Flask, jsonify
from flask_cors import CORS
import requests
from datetime import datetime
import pytz

app = Flask(__name__)
CORS(app)  # Permet les requêtes cross-origin

@app.route('/api/matches/<date>')
def get_matches(date):
    api_key = '3f9226033c324e538d8d34a36118390b'
    base_url = 'https://api.football-data.org/v4'
    
    try:
        headers = {
            'X-Auth-Token': api_key,
            'Accept': 'application/json'
        }
        
        params = {
            'date': date,
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
                
                match_info = {
                    'team1': match['homeTeam']['name'],
                    'team2': match['awayTeam']['name'],
                    'team1_logo': match['homeTeam'].get('crest', ''),
                    'team2_logo': match['awayTeam'].get('crest', ''),
                    'time': match_date_local.strftime('%H:%M'),
                    'status': match['status'],
                    'score': f"{match.get('score', {}).get('fullTime', {}).get('home', '-')}-{match.get('score', {}).get('fullTime', {}).get('away', '-')}",
                    'competition': match.get('competition', {}).get('name', 'Compétition inconnue')
                }
                all_matches.append(match_info)
            
            page += 1
            if not data.get('hasMore', False):
                break
        
        return jsonify(all_matches)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()