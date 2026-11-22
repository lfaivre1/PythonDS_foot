#les données de position sont déjà normalisées dans le même sens, pas besoin de vérifier dans quel l'équipe attaque

import pandas as pd
import matplotlib.pyplot as plt


def bornes_zone14(match_json):
    longueur = float(match_json['pitch_length'])
    return 17.5, longueur / 2 - 16.5, -11.33, 11.33


def dans_zone14(x, y, match_json):
    #on repère les positions situées dans le rectangle de la zone 14
    x_min, x_max, y_min, y_max = bornes_zone14(match_json)
    return (x >= x_min) & (x <= x_max) & (y >= y_min) & (y <= y_max)


def preparer_evenements(match_json, evenements):
    #on garde une copie et on convertit uniquement les colonnes nécessaires
    df = evenements.copy()
    colonnes_numeriques = [
        'team_id', 'frame_start', 'frame_end',
        'x_start', 'y_start', 'x_end', 'y_end',
        'pass_epv_delta_for', 'pass_epv_total', 'pass_reception_epv_for',
        'possession_epv_for_end', 'possession_epv_delta_for'
    ]
    for colonne in colonnes_numeriques:
        if colonne in df.columns:
            df[colonne] = df[colonne].astype(float)            
        else:
            df[colonne] = float('nan')

    for colonne in ['lead_to_shot', 'lead_to_goal']:
        if colonne in df.columns:
            if df[colonne].isna().sum() == 0:                 
                df[colonne] = df[colonne].astype(int)
            else:
                df[colonne] = df[colonne].astype(float)
        else:
            df[colonne] = float('nan')

    return df

def passes_depuis_zone14(match_json, evenements, id_equipe):
    #x_end et y_end : emplacement de fin de possession du passeur
    df = preparer_evenements(match_json, evenements)
    passes = df.loc[
        (df['team_id'] == id_equipe)
        & (df['event_type'] == 'player_possession')
        & (df['end_type'] == 'pass')
    ].copy()
    return passes.loc[dans_zone14(passes['x_end'], passes['y_end'], match_json)].copy()


def frappes_depuis_zone14(match_json, evenements, id_equipe):
    #la valeur EPV associée n'est pas un xG
    df = preparer_evenements(match_json, evenements)
    frappes = df.loc[
        (df['team_id'] == id_equipe)
        & (df['event_type'] == 'player_possession')
        & (df['end_type'] == 'shot')
    ].copy()
    return frappes.loc[dans_zone14(frappes['x_end'], frappes['y_end'], match_json)].copy()


def passes_vers_zone14(match_json, evenements, id_equipe):
    #on estime les réceptions à l'aide de la possession suivante
    df = preparer_evenements(match_json, evenements)
    possessions = df.loc[df['event_type'] == 'player_possession'].copy()
    possessions = possessions.sort_values(['frame_start', 'frame_end']).reset_index(drop=True)
    actuelle = possessions.iloc[:-1].reset_index(drop=True).copy()
    suivante = possessions.iloc[1:].reset_index(drop=True)

    actuelle['equipe_suivante'] = suivante['team_id']
    actuelle['joueur_suivant'] = suivante['player_id']
    actuelle['frame_suivante'] = suivante['frame_start']
    actuelle['x_arrivee'] = suivante['x_start']
    actuelle['y_arrivee'] = suivante['y_start']
    actuelle['ecart_frames'] = actuelle['frame_suivante'] - actuelle['frame_end']
    fin_mt1 = match_json['match_periods'][0]['end_frame']

    receptions = actuelle.loc[
        (actuelle['team_id'] == id_equipe)
        & (actuelle['end_type'] == 'pass')
        & (actuelle['equipe_suivante'] == id_equipe)
        & (actuelle['joueur_suivant'] != actuelle['player_id'])
        & (actuelle['ecart_frames'] >= 0)
        & (actuelle['ecart_frames'] <= 30)
        & ~(
            (actuelle['frame_end'] <= fin_mt1)
            & (actuelle['frame_suivante'] > fin_mt1)
        )
    ].copy()

    return receptions.loc[
        dans_zone14(receptions['x_arrivee'], receptions['y_arrivee'], match_json)
        & ~dans_zone14(receptions['x_end'], receptions['y_end'], match_json) #le point d'arrivée est dans la zone 14 mais pas le point de départ de la passe (pris en compte au dessus)
    ].copy()


def courses_vers_zone14(match_json, evenements, id_equipe):
    df = preparer_evenements(match_json, evenements)
    courses = df.loc[
        (df['team_id'] == id_equipe) & (df['event_type'] == 'off_ball_run')
    ].copy()
    return courses.loc[
        dans_zone14(courses['x_end'], courses['y_end'], match_json)
        & ~dans_zone14(courses['x_start'], courses['y_start'], match_json) #les courses commencent en dehors et finissent dedans
    ].copy()


def courses_depuis_zone14(match_json, evenements, id_equipe):
    df = preparer_evenements(match_json, evenements)
    courses = df.loc[
        (df['team_id'] == id_equipe) & (df['event_type'] == 'off_ball_run')
    ].copy()
    return courses.loc[
        dans_zone14(courses['x_start'], courses['y_start'], match_json)
        & ~dans_zone14(courses['x_end'], courses['y_end'], match_json) #les courses commencent dedans et finissent en dehors
    ].copy()



def tracer_terrain(match_json):
    longueur = float(match_json['pitch_length'])
    largeur = float(match_json['pitch_width'])
    x_min, x_max, y_min, y_max = bornes_zone14(match_json)
    plt.plot(
        [-longueur/2, longueur/2, longueur/2, -longueur/2, -longueur/2],
        [-largeur/2, -largeur/2, largeur/2, largeur/2, -largeur/2],
        color='black'
    )
    plt.plot([0, 0], [-largeur/2, largeur/2], color='black')
    plt.plot([x_min, x_max, x_max, x_min, x_min],
             [y_min, y_min, y_max, y_max, y_min], color='red')
    plt.xlabel('Longueur (m)')
    plt.ylabel('Largeur (m)')
    plt.axis('equal') #pour avoir la même échelle sur les deux axesS
   


def carte_actions(match_json, actions, titre, type_action):
    #on trace un terrain pour une action et un match
    plt.figure(figsize=(10, 5))
    tracer_terrain(match_json)
    if type_action == 'passes_depuis':
        plt.scatter(actions['x_end'], actions['y_end'], color='blue', s=24)
    elif type_action == 'frappes':
        plt.scatter(actions['x_end'], actions['y_end'], color='red', s=38)
    elif type_action == 'passes_vers':
        for _, ligne in actions.iterrows():
            plt.arrow(ligne['x_end'], ligne['y_end'],
                      ligne['x_arrivee'] - ligne['x_end'],
                      ligne['y_arrivee'] - ligne['y_end'],
                      color='blue', alpha=0.5, head_width=0.8,
                      head_length=1.0, length_includes_head=True)
    elif type_action == 'courses':
        for _, ligne in actions.iterrows():
            plt.arrow(ligne['x_start'], ligne['y_start'],
                      ligne['x_end'] - ligne['x_start'],
                      ligne['y_end'] - ligne['y_start'],
                      color='green', alpha=0.5, head_width=0.8,
                      head_length=1.0, length_includes_head=True)
    plt.title(titre)



def bilan_match(match_json, evenements, id_equipe):
    #on rassemble quelques indicateurs dans un dictionnaire simple
    df = preparer_evenements(match_json, evenements)
    passes = df.loc[(df['team_id'] == id_equipe)
                    & (df['event_type'] == 'player_possession')
                    & (df['end_type'] == 'pass')].copy()
    frappes = df.loc[(df['team_id'] == id_equipe)
                     & (df['event_type'] == 'player_possession')
                     & (df['end_type'] == 'shot')].copy()
    p_depuis = passes_depuis_zone14(match_json, evenements, id_equipe)
    p_vers = passes_vers_zone14(match_json, evenements, id_equipe)
    f_depuis = frappes_depuis_zone14(match_json, evenements, id_equipe)
    c_vers = courses_vers_zone14(match_json, evenements, id_equipe)
    c_depuis = courses_depuis_zone14(match_json, evenements, id_equipe)
    return {
        'Passes totales': len(passes),
        'Passes depuis Z14': len(p_depuis),
        'Part passes depuis Z14 (%)': 100 * len(p_depuis) / len(passes) if len(passes) else float('nan'),
        'EPV moyen passes Z14': p_depuis['pass_epv_delta_for'].mean(),
        'Passes Z14 liées à un tir': p_depuis['lead_to_shot'].sum(min_count=1),
        'Passes vers Z14 (estimées)': len(p_vers),
        'Frappes totales': len(frappes),
        'Frappes depuis Z14': len(f_depuis),
        'Courses vers Z14': len(c_vers),
        'Courses depuis Z14': len(c_depuis)
    }
