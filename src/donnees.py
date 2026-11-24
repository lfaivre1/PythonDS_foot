from io import StringIO
from pathlib import Path

import pandas as pd
import requests

#version des données SkillCorner fixée (état du dépôt au 14/09/2026)
COMMIT = '4340d274572876239c154c90bc507a9b3250a656'
BASE = f'https://raw.githubusercontent.com/SkillCorner/opendata/{COMMIT}/data'

URL_WIKIPEDIA = 'https://en.wikipedia.org/wiki/2024%E2%80%9325_A-League_Men'
#copie du tableau Wikipédia, utilisée si la page n'est pas accessible
FICHIER_SECOURS = Path(__file__).resolve().parent.parent / 'data' / 'classement_wikipedia_2024_25.csv'


def charger_match(id_match):
    evenements = pd.read_csv(f'{BASE}/matches/{id_match}/{id_match}_dynamic_events.csv', low_memory=False)
    infos = requests.get(f'{BASE}/matches/{id_match}/{id_match}_match.json', timeout=60).json()
    return infos, evenements


def liste_matchs():
    #identifiants des matchs disponibles, triés par date
    matchs = requests.get(f'{BASE}/matches.json', timeout=60).json()
    matchs = sorted(matchs, key=lambda m: (m['date_time'][:10], m['id']))
    return [m['id'] for m in matchs]


def nettoyer_classement(tableau):
    classement = tableau[['Pos', 'Team', 'Pld', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts']].copy()
    #mêmes noms que dans SkillCorner : on enlève (C) et FC, seul Newcastle s'écrit différemment
    classement['equipe'] = (classement['Team'].str.replace(r'\s*\([A-Z]\)', '', regex=True)
                            .str.replace(' FC', '').str.strip()
                            .replace({'Newcastle Jets': 'Newcastle United Jets'}))
    #Wikipédia écrit les différences de buts négatives avec le signe « − »
    classement['GD'] = classement['GD'].astype(str).str.replace('−', '-').str.replace('+', '')
    colonnes = ['Pos', 'Pld', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts']
    classement[colonnes] = classement[colonnes].apply(pd.to_numeric)
    classement = classement.drop(columns='Team').rename(columns={
        'Pos': 'rang_final', 'Pld': 'matchs_joues', 'W': 'victoires', 'D': 'nuls', 'L': 'defaites',
        'GF': 'buts_pour', 'GA': 'buts_contre', 'GD': 'difference_buts', 'Pts': 'points'})
    if len(classement) != 13:
        raise ValueError("ce tableau n'est pas le classement attendu")
    return classement


def charger_classement():
    try:
        page = requests.get(URL_WIKIPEDIA, headers={'User-Agent': 'projet ENSAE'}, timeout=30)
        page.raise_for_status()
        #le classement est le premier tableau de la page avec une colonne 'Pld'
        classement = nettoyer_classement(pd.read_html(StringIO(page.text), match='Pld')[0])
        print('Classement récupéré sur Wikipédia')
    except Exception as erreur:
        print('Wikipédia inaccessible (' + type(erreur).__name__ + '), on utilise la copie du tableau')
        classement = nettoyer_classement(pd.read_csv(FICHIER_SECOURS))
    return classement
