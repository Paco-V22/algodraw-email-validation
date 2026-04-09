"""
Générateur d'emails hebdomadaires Algo-Draw
Analyse Google Sheets + Supabase et génère les drafts d'emails
"""

import os
import pandas as pd
from datetime import datetime, timedelta
from supabase import create_client
import json

# --- CONFIGURATION ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
BASE_GS_URL = "https://docs.google.com/spreadsheets/d/1s1Z_Tp7VKdG6Ba-vrnmsYyHhIGi9KY7WvzF_iiskHDc"
GID_ACTIVES = "560625492"
GID_TERMINEES = "0"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def to_f(x):
    """Convertit une valeur en float"""
    if pd.isna(x) or str(x).strip() in ["", "-", "None"]: 
        return 0.0
    try: 
        return float(str(x).replace(',', '.').replace('%', '').replace('€', '').strip())
    except: 
        return 0.0

def load_data(gid):
    """Charge les données depuis Google Sheets"""
    csv_url = f"{BASE_GS_URL}/export?format=csv&gid={gid}"
    return pd.read_csv(csv_url)

def get_week_range():
    """Retourne le début et la fin de la semaine actuelle"""
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())  # Lundi
    end_of_week = start_of_week + timedelta(days=6)  # Dimanche
    return start_of_week, end_of_week

def detect_nouvelles_equipes(df_actives):
    """Détecte les nouvelles équipes ajoutées cette semaine"""
    start_week, end_week = get_week_range()
    
    nouvelles = []
    for idx, row in df_actives.iterrows():
        try:
            # Parse date démarrage
            demarrage = pd.to_datetime(row.get('Démarrage'), dayfirst=True, errors='coerce')
            if pd.isna(demarrage):
                continue
            
            # Vérifie si démarrage cette semaine
            if start_week <= demarrage <= end_week:
                # Vérifie si P1 (nouveau démarrage)
                if pd.notna(row.get('P1')) and pd.isna(row.get('P2')):
                    ssn = int(to_f(row.get('SSN', 0)))
                    proba = to_f(row.get('Proba Nul à 5 matchs', 0))
                    nouvelles.append({
                        'equipe': row.get('Équipe', 'N/A'),
                        'championnat': row.get('Championnat', 'N/A'),
                        'ssn': ssn,
                        'proba': proba,
                        'demarrage': demarrage.strftime('%d/%m/%Y')
                    })
        except Exception as e:
            print(f"Erreur parsing nouvelle équipe: {e}")
            continue
    
    return nouvelles

def detect_martingales_closes(df_terminees):
    """Détecte les martingales closes cette semaine"""
    start_week, end_week = get_week_range()
    
    closes = []
    for idx, row in df_terminees.iterrows():
        try:
            fin = pd.to_datetime(row.get('Fin'), dayfirst=True, errors='coerce')
            if pd.isna(fin):
                continue
            
            if start_week <= fin <= end_week:
                # Calcul du palier gagnant
                palier_gagnant = None
                for i, p_col in enumerate(['P1', 'P2', 'P3', 'P4', 'P5'], start=1):
                    if to_f(row.get(p_col, 0)) > 0:
                        palier_gagnant = i
                        break
                
                # Calcul net et ROI
                p_units = [1, 2, 4, 8, 16]
                played_indices = [i for i, p_col in enumerate(['P1','P2','P3','P4','P5']) if to_f(row.get(p_col, 0)) != 0]
                total_mises = sum([p_units[i] for i in played_indices])
                
                net_u = 0
                if palier_gagnant:
                    cote = to_f(row.get('Cote', 0))
                    mise_gagnante = p_units[palier_gagnant - 1]
                    net_u = (mise_gagnante * cote) - total_mises
                else:
                    net_u = -total_mises
                
                roi = (net_u / total_mises * 100) if total_mises > 0 else 0
                
                closes.append({
                    'equipe': row.get('Équipe', 'N/A'),
                    'score': row.get('Score', 'N/A'),
                    'palier': f"P{palier_gagnant}" if palier_gagnant else "Perdu",
                    'net_u': net_u,
                    'roi': roi
                })
        except Exception as e:
            print(f"Erreur parsing close: {e}")
            continue
    
    return closes

def detect_paliers_critiques(df_actives):
    """Détecte les martingales en palier critique (≥P3)"""
    critiques = []
    
    for idx, row in df_actives.iterrows():
        try:
            # Détermine palier actuel
            palier_actuel = None
            for i, p_col in enumerate(['P1', 'P2', 'P3', 'P4', 'P5'], start=1):
                if pd.notna(row.get(p_col)) and to_f(row.get(p_col)) == 0:
                    # Palier joué mais pas encore résolu
                    palier_actuel = i
            
            # Si ≥P3
            if palier_actuel and palier_actuel >= 3:
                proch_match = row.get('Proch. match', 'N/A')
                critiques.append({
                    'equipe': row.get('Équipe', 'N/A'),
                    'palier': f"P{palier_actuel}",
                    'proch_match': proch_match,
                    'championnat': row.get('Championnat', 'N/A')
                })
        except Exception as e:
            print(f"Erreur parsing critique: {e}")
            continue
    
    return critiques

def get_top_3_martingales(df_actives):
    """Retourne les 3 meilleures martingales par Proba Nul"""
    df_copy = df_actives.copy()
    df_copy['_proba'] = df_copy['Proba Nul à 5 matchs'].apply(to_f)
    df_sorted = df_copy.sort_values('_proba', ascending=False)
    
    top_3 = []
    for idx, row in df_sorted.head(3).iterrows():
        # Détermine palier actuel
        palier_actuel = "P1"
        for i, p_col in enumerate(['P1', 'P2', 'P3', 'P4', 'P5'], start=1):
            if pd.notna(row.get(p_col)):
                palier_actuel = f"P{i+1}" if i < 5 else "P5"
        
        top_3.append({
            'equipe': row.get('Équipe', 'N/A'),
            'championnat': row.get('Championnat', 'N/A'),
            'proba': to_f(row.get('Proba Nul à 5 matchs', 0)),
            'palier': palier_actuel,
            'status': 'En cours' if palier_actuel != 'P1' else 'Démarrage'
        })
    
    return top_3

def get_all_active_martingales(df_actives):
    """Retourne toutes les martingales actives triées par Proba"""
    df_copy = df_actives.copy()
    df_copy['_proba'] = df_copy['Proba Nul à 5 matchs'].apply(to_f)
    df_sorted = df_copy.sort_values('_proba', ascending=False)
    
    all_martingales = []
    for idx, row in df_sorted.iterrows():
        # Détermine palier actuel
        palier_actuel = "Démarrage"
        for i, p_col in enumerate(['P1', 'P2', 'P3', 'P4', 'P5'], start=1):
            if pd.notna(row.get(p_col)):
                if i < 5:
                    palier_actuel = f"P{i+1} en cours"
                else:
                    palier_actuel = "P5 en cours"
        
        all_martingales.append({
            'equipe': row.get('Équipe', 'N/A'),
            'championnat': row.get('Championnat', 'N/A'),
            'proba': to_f(row.get('Proba Nul à 5 matchs', 0)),
            'palier': palier_actuel
        })
    
    return all_martingales

def calculate_global_stats(df_actives, df_terminees):
    """Calcule les stats globales du portefeuille"""
    # Stats martingales closes
    total_closes = len(df_terminees)
    
    # ROI closes
    net_closes = 0
    invest_closes = 0
    
    for idx, row in df_terminees.iterrows():
        p_units = [1, 2, 4, 8, 16]
        played_indices = [i for i, p_col in enumerate(['P1','P2','P3','P4','P5']) if to_f(row.get(p_col, 0)) != 0]
        total_mises = sum([p_units[i] for i in played_indices])
        invest_closes += total_mises
        
        palier_gagnant = None
        for i, p_col in enumerate(['P1', 'P2', 'P3', 'P4', 'P5'], start=1):
            if to_f(row.get(p_col, 0)) > 0:
                palier_gagnant = i
                break
        
        if palier_gagnant:
            cote = to_f(row.get('Cote', 0))
            mise_gagnante = p_units[palier_gagnant - 1]
            net_closes += (mise_gagnante * cote) - total_mises
        else:
            net_closes += -total_mises
    
    roi_closes = (net_closes / invest_closes * 100) if invest_closes > 0 else 0
    
    # Capital engagé actuel
    capital_engage = 0
    for idx, row in df_actives.iterrows():
        p_units = [1, 2, 4, 8, 16]
        played_indices = [i for i, p_col in enumerate(['P1','P2','P3','P4','P5']) if to_f(row.get(p_col, 0)) != 0]
        capital_engage += sum([p_units[i] for i in played_indices])
    
    return {
        'total_closes': total_closes,
        'benefice_total_u': net_closes,
        'roi_closes': roi_closes,
        'capital_engage_u': capital_engage,
        'nb_actives': len(df_actives),
        'taux_reussite': 92  # Hardcodé comme validé
    }

def generate_email_data():
    """Génère toutes les données nécessaires pour les emails"""
    print("📊 Chargement des données Google Sheets...")
    df_actives = load_data(GID_ACTIVES)
    df_terminees = load_data(GID_TERMINEES)
    
    print("🔍 Analyse des données...")
    data = {
        'nouvelles_equipes': detect_nouvelles_equipes(df_actives),
        'closes': detect_martingales_closes(df_terminees),
        'paliers_critiques': detect_paliers_critiques(df_actives),
        'top_3': get_top_3_martingales(df_actives),
        'all_actives': get_all_active_martingales(df_actives),
        'stats_globales': calculate_global_stats(df_actives, df_terminees),
        'date_generation': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'semaine': get_week_range()[0].strftime('Semaine du %d %B %Y')
    }
    
    # Sauvegarder dans un fichier JSON pour l'interface de validation
    with open('/tmp/email_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Données générées : {len(data['nouvelles_equipes'])} nouvelles, {len(data['closes'])} closes")
    return data

if __name__ == "__main__":
    data = generate_email_data()
    print("📧 Données email générées avec succès !")
    print(json.dumps(data, indent=2, ensure_ascii=False))
