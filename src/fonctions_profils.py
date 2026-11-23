import pandas as pd                      
import matplotlib.pyplot as plt          


def compter_actions_joueurs(actions_zone14):
    """Compte les cinq catégories d'actions par player_id sur les quatre matchs."""
    tableau_usage = None

    for nom_action, resultats in actions_zone14.items():
        liste_tableaux = []
        for nom_match in resultats:
            liste_tableaux.append(resultats[nom_match])

        toutes_actions = pd.concat(liste_tableaux).copy()
        #on aligne le type des identifiants avec les bases de saison
        toutes_actions['player_id'] = toutes_actions['player_id'].astype(float)
        comptage = toutes_actions.groupby('player_id').agg({'event_type': 'count'})
        comptage = comptage.rename(columns={'event_type': nom_action}).reset_index()

        if tableau_usage is None:
            tableau_usage = comptage
        else:
            tableau_usage = tableau_usage.merge(comptage, on='player_id', how='outer')

    #on remplace les actions absentes par zéro, sans modifier les identifiants
    colonnes_actions = list(actions_zone14.keys())
    tableau_usage[colonnes_actions] = tableau_usage[colonnes_actions].fillna(0)
    tableau_usage[colonnes_actions] = tableau_usage[colonnes_actions].astype(int)
    tableau_usage['player_id'] = tableau_usage['player_id'].astype(int)
    tableau_usage['total'] = tableau_usage[colonnes_actions].sum(axis=1)
    return tableau_usage.sort_values('total', ascending=False)


def percentile(serie, valeur):
    if valeur != valeur:
        return float('nan')
    serie = serie.dropna()                       
    if len(serie) == 0:
        return float('nan')
    plus_faibles = (serie < valeur).sum()        
    egaux = (serie == valeur).sum()
    return (plus_faibles + 0.5 * egaux) / len(serie) * 100


def ligne_principale(df, identifiant, colonne_matchs):
    lignes_joueur = df.loc[df['player_id'] == identifiant]       
    if len(lignes_joueur) == 0:
        return None
    lignes_joueur = lignes_joueur.sort_values(colonne_matchs, ascending=False)   
    return lignes_joueur.iloc[0]                                  


def tableau_percentiles(df, identifiant, variables, categorie, colonne_matchs, variables_danger):
    lignes_joueur = df.loc[df['player_id'] == identifiant]
    resultat = []
    if len(lignes_joueur) == 0:
        print('Joueur', identifiant, 'absent des données de saison :', categorie)
        return resultat

    #si un joueur apparaît à plusieurs postes, on retient sa ligne avec le plus de matchs
    lignes_joueur = lignes_joueur.sort_values(colonne_matchs, ascending=False)
    ligne = lignes_joueur.iloc[0]
    poste = ligne['position_group']

    coequipiers = df.loc[df['equipe'] == 'Auckland']
    meme_poste = df.loc[df['position_group'] == poste]

    for variable in variables:
        if variable not in df.columns:
            print('Variable absente :', variable)
        else:
            valeur = ligne[variable]
            resultat.append({
                'player_id': identifiant,
                'joueur': ligne['player_name'],
                'poste': poste,
                'categorie': categorie,
                'variable': variable,
                'est_danger': variable in variables_danger,
                'valeur': valeur,
                'moyenne_coequipiers': coequipiers[variable].mean(),
                'percentile_coequipiers': percentile(coequipiers[variable], valeur),
                'moyenne_ligue_meme_poste': meme_poste[variable].mean(),
                'percentile_ligue_meme_poste': percentile(meme_poste[variable], valeur),
                'percentile_ligue_tous_postes': percentile(df[variable], valeur)
            })
    return resultat



def tableau_identite(top_joueurs, pas, courses, phys):
    lignes = []
    for i in range(len(top_joueurs)):
        joueur = top_joueurs.iloc[i]
        identifiant = joueur['player_id']
        lignes_joueur = phys.loc[phys['player_id'] == identifiant]
        colonne_matchs = 'count_match'
        colonne_minutes = 'minutes_full_all'
        if len(lignes_joueur) == 0:
            lignes_joueur = pas.loc[pas['player_id'] == identifiant]
            colonne_matchs = 'performance_count'
            colonne_minutes = 'minutes'

        ligne = {'Joueur': joueur['nom_joueur']}
        if len(lignes_joueur) == 0:
            ligne['Poste principal'] = 'absent des données de saison'
        else:
            lignes_joueur = lignes_joueur.sort_values(colonne_matchs, ascending=False)
            principale = lignes_joueur.iloc[0]
            ligne['Poste principal'] = principale['position_group']

            #tous les postes occupés, avec le nombre de matchs (une ligne de saison par poste)
            postes = []
            for j in range(len(lignes_joueur)):
                autre = lignes_joueur.iloc[j]
                postes.append(autre['position_group'] + ' (' + str(int(autre[colonne_matchs])) + ')')
            ligne['Postes joués (matchs)'] = ', '.join(postes)

            naissance = principale['player_birthdate']
            if isinstance(naissance, str):
                annee = float(naissance[:4])
                mois = float(naissance[5:7])
                ligne['Âge (ans)'] = round(2025 + 5 / 12 - (annee + (mois - 1) / 12), 1)
            else:
                ligne['Âge (ans)'] = float('nan')

            ligne['Matchs retenus (60 min ou plus)'] = int(principale[colonne_matchs])
            ligne['Minutes par match'] = round(principale[colonne_minutes], 1)

        ligne['Actions en zone 14 (4 matchs)'] = int(joueur['total'])
        lignes.append(ligne)
    return pd.DataFrame(lignes)


def valeur_joueur(df, identifiant, variable, colonne_matchs):
    ligne = ligne_principale(df, identifiant, colonne_matchs)
    if ligne is None or variable not in df.columns:
        return float('nan')
    return ligne[variable]


def tableau_profils(top_joueurs, bases, indicateurs):
    colonnes = {'Catégorie': [], 'Indicateur': []}
    for categorie, variable, libelle in indicateurs:
        colonnes['Catégorie'].append(categorie)
        colonnes['Indicateur'].append(libelle)

    #une colonne par joueur retenu
    for i in range(len(top_joueurs)):
        joueur = top_joueurs.iloc[i]
        valeurs = []
        for categorie, variable, libelle in indicateurs:
            df, colonne_matchs = bases[categorie]
            valeurs.append(valeur_joueur(df, joueur['player_id'], variable, colonne_matchs))
        colonnes[joueur['nom_joueur']] = valeurs

    #repères : moyenne des joueurs d'Auckland et moyenne des joueurs de la ligue
    moyenne_auckland = []
    moyenne_ligue = []
    for categorie, variable, libelle in indicateurs:
        df = bases[categorie][0]
        moyenne_auckland.append(df.loc[df['equipe'] == 'Auckland'][variable].mean())
        moyenne_ligue.append(df[variable].mean())
    colonnes['Moyenne Auckland'] = moyenne_auckland
    colonnes['Moyenne ligue'] = moyenne_ligue

    return pd.DataFrame(colonnes)


def graphique_percentiles(percentiles_joueurs, identifiant, titre, libelles):
    tableau = percentiles_joueurs.loc[percentiles_joueurs['player_id'] == identifiant]
    tableau = tableau.dropna(subset=['percentile_ligue_meme_poste'])     
    couleurs = {'Passes': 'steelblue', 'Courses sans ballon': 'seagreen', 'Physique': 'darkorange'}
    if len(tableau) == 0:
        print('Aucun percentile disponible pour ce joueur')
        return

    
    plt.figure(figsize=(10, 0.4 * len(tableau) + 1.5))
    #on parcourt le tableau à l'envers pour que le premier indicateur soit en haut du graphique
    for i in range(len(tableau) - 1, -1, -1):
        ligne = tableau.iloc[i]
        etiquette = libelles[ligne['variable']]
        plt.plot([0, ligne['percentile_ligue_meme_poste']], [etiquette, etiquette], color='lightgrey')
        plt.scatter(ligne['percentile_ligue_meme_poste'], etiquette,
                    color=couleurs[ligne['categorie']], s=70, zorder=3)
    #trait vertical au niveau médian, du premier au dernier indicateur (tracé après les autres traits, sous les points)
    premiere = libelles[tableau.iloc[0]['variable']]
    derniere = libelles[tableau.iloc[len(tableau) - 1]['variable']]
    plt.plot([50, 50], [derniere, premiere], color='lightgrey')
    plt.xlabel('Percentile parmi les joueurs de la ligue du même poste (50 = niveau médian)')
    plt.title(titre)
