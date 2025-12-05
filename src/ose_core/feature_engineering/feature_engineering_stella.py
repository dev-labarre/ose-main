# INITIAL SETUP

# Import necessary libraries
import pandas as pd
import numpy as np
import re
import ast
from pathlib import Path



# PATHS, CONSTANTS & VARIABLES

# Set path to datasets
DATA_DIR = Path("~/code/StellaRodriguesLallement/OSE_Project/Dataset_visualization/src/ose_core/data_ingestion/extracted_datasets").expanduser()

legal_forms = {
    'SAS': r'\bSAS\b|\bSASU\b',
    'SA': r'\bSA\b',
    'SARL': r'\bSARL\b',
    'EURL': r'\bEURL\b',
    'SNC': r'\bSNC\b',
    'SCI': r'\bSCI\b',
}

signal_weights = {
    'B': 25,   # Construction (usine)
    'X': 15,   # Foncier / bâti
    'E': 20,   # Création (nouvelle usine)
    'F': 15,   # Croissance
    'N': 10,   # Recrutement
    'S': 7,    # Lancement
    'K1': 8,   # Investissements

    # Red flags
    'O': -15,  # Fermeture d’établissement
    'M': -20,  # Licenciements / chômage technique
    'I': -50   # Liquidation / RJ / LJ
}


# DATA LOADING

df_basic     = pd.read_csv(DATA_DIR / '01_company_basic_info.csv', dtype={'siren': str})
df_financial = pd.read_csv(DATA_DIR / '02_financial_data.csv', dtype={'siren': str})
df_workforce = pd.read_csv(DATA_DIR / '03_workforce_data.csv', dtype={'siren': str})
df_structure = pd.read_csv(DATA_DIR / '04_company_structure.csv', dtype={'siren': str})
df_flags     = pd.read_csv(DATA_DIR / '05_classification_flags.csv', dtype={'siren': str})
df_kpi       = pd.read_csv(DATA_DIR / '07_kpi_data.csv', dtype={'siren': str})
df_signals   = pd.read_csv(DATA_DIR / '08_signals.csv', dtype={'siren': str})

print("All datasets loaded successfully!")



# DATA FORMATTING & ENGINNERING

# Extracting legal forms and combining all text into one text


df_basic['full_text'] = (
    df_basic['company_name'].fillna('') + ' ' +
    df_basic['raison_sociale'].fillna('') + ' ' +
    df_basic['raison_sociale_keyword'].fillna('')
)

df_basic['full_text']

def extract_legal_form(text):
    for form, pattern in legal_forms.items():
        if re.search(pattern, text, flags=re.IGNORECASE):
            return form
    return 'other'



# SELECTING FEATURES

# Selecting basic features
df_basic_feat = df_basic[['company_name','siren', 'siret', 'departement']].copy()
df_basic_feat['forme_juridique'] = df_basic['full_text'].apply(extract_legal_form)
df_basic_feat.head(50)

# Selecting workforce features
df_workforce_feat = df_workforce[['siren', 'effectif', 'effectifConsolide']].copy()

# Selecting structure features
structure_selected = [
    'siren',
    'nbFilialesDirectes',
    'nbEtabSecondaire',
    'nbMarques',
    'hasGroupOwner',   # or 'appartient_groupe'
    'nombre_etablissements_secondaires_inactifs'
]
df_structure_feat = df_structure[structure_selected].copy()

# Selecting flag features
df_flags_feat = df_flags[['siren','filtre_levee_fond', 'hasMarques']].copy()





def prepare_signals(df_signals):
    """
    Clean the raw signals table:
    - convert string dicts to Python dict
    - extract signal_code & signal_label
    - normalise timestamps
    """
    df = df_signals.copy()

    # Convert the 'type' JSON-like string into a dictionary
    df['type'] = df['type'].apply(ast.literal_eval)

    # Extract fields
    df['signal_code'] = df['type'].apply(lambda x: x.get('code'))
    df['signal_label'] = df['type'].apply(lambda x: x.get('label'))

    # Parse date
    df['publishedAt'] = pd.to_datetime(df['publishedAt'], utc=True)

    return df[['siren', 'signal_code', 'signal_label', 'publishedAt']]


def filter_recent_signals(df_signals, months=12):
    cutoff = pd.Timestamp.now(tz='UTC') - pd.DateOffset(months=months)
    return df_signals[df_signals['publishedAt'] >= cutoff].copy()

positive_codes = ['B', 'K1', 'F', 'E', 'S']   # Construction, Investissements, Croissance, Création, Lancement produits
negative_codes = ['M', 'O', 'I']              # Licenciement, RJ/LJ, Fermeture

def classify_signal(code):
    if code in positive_codes:
        return 'positive'
    elif code in negative_codes:
        return 'negative'
    else:
        return 'neutral'

def add_valence(df_signals):
    df = df_signals.copy()
    df['signal_valence'] = df['signal_code'].apply(classify_signal)
    return df











# DATASET BUILDING
def build_dataset():
    """
    Main function that returns the cleaned, merged feature table.
    """
    # Merge all tables on siren
    df = df_basic_feat.merge(df_workforce_feat, on='siren', how='left')
    df = df.merge(df_structure_feat, on='siren', how='left')
    df = df.merge(df_flags_feat, on='siren', how='left')
    #df = df.merge(df_kpi_feat, on='siren', how='left')
    #df = df.merge(df_signals_recent, on='siren', how='left')

    return df

build_dataset()
