import numpy as np

from fonctions_zone14 import preparer_evenements, bilan_match


def bilan_equipe(infos, evenements, id_equipe):
    #les comptages de bilan_match(), rapportés au volume de jeu de l'équipe sur le match
    bilan = bilan_match(infos, evenements, id_equipe)
    df = preparer_evenements(infos, evenements)
    df = df.loc[df['team_id'] == id_equipe]
    courses = (df['event_type'] == 'off_ball_run').sum()
    #couloir où se terminent les possessions qui arrivent dans le dernier tiers adverse
    fins = df.loc[(df['event_type'] == 'player_possession') & (df['third_end'] == 'attacking_third'), 'channel_end']
    return {
        'part_passes_depuis_z14': bilan['Passes depuis Z14'] / bilan['Passes totales'],
        'passes_vers_z14_pour_100_passes': 100 * bilan['Passes vers Z14 (estimées)'] / bilan['Passes totales'],
        'part_tirs_depuis_z14': bilan['Frappes depuis Z14'] / bilan['Frappes totales'] if bilan['Frappes totales'] > 0 else np.nan,
        'courses_vers_z14_pour_100_courses': 100 * bilan['Courses vers Z14'] / courses,
        'courses_depuis_z14_pour_100_courses': 100 * bilan['Courses depuis Z14'] / courses,
        'part_fins_cote_gauche': fins.isin(['wide_left', 'half_space_left']).mean(),
        'part_fins_cote_droit': fins.isin(['wide_right', 'half_space_right']).mean(),
    }


def test_permutation(a, b, n_tirages=10000):
    #on mélange les étiquettes des deux groupes et on compte les écarts au moins aussi grands que l'écart observé
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    a, b = a[~np.isnan(a)], b[~np.isnan(b)]
    observe = a.mean() - b.mean()
    valeurs = np.concatenate([a, b])
    generateur = np.random.default_rng(0)
    extremes = 0
    for _ in range(n_tirages):
        generateur.shuffle(valeurs)
        if abs(valeurs[:len(a)].mean() - valeurs[len(a):].mean()) >= abs(observe) - 1e-12:
            extremes += 1
    return (extremes + 1) / (n_tirages + 1)
