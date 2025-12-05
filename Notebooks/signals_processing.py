
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


def build_signal_features(df_signals):
    """
    Returns:
    - per-siren counts of positive/negative/neutral signals
    - per-siren counts of each signal_code
    """

    # Valence summary
    valence = (
        df_signals.groupby(['siren', 'signal_valence'])
        .size()
        .unstack(fill_value=0)
        .rename(columns={
            'positive': 'n_positive_signals',
            'negative': 'n_negative_signals',
            'neutral':  'n_neutral_signals'
        })
    )

    # Code summary
    code_counts = (
        df_signals.groupby(['siren', 'signal_code'])
        .size()
        .unstack(fill_value=0)
        .add_prefix('n_code_')
    )

    # Merge both
    return valence.join(code_counts, how='outer').fillna(0)
