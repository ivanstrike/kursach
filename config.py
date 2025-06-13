TELEGRAM_TOKEN = "7716350342:AAEjdUngEZDCm-EMoSaFRj6keImv0-4tfss"

ML_CONFIG = {
    'vectorizer_params': {
        'analyzer': 'word',
        'ngram_range': (1, 2),  
        'max_features': 1000,
        'lowercase': True,
        'token_pattern': r'\b\w+\b',
        'min_df': 1,
        'max_df': 0.95
    }
}

THRESHOLDS = {
    'intent_similarity': 0.25,
    'dialogue_similarity': 0.25,
    'length_difference': 0.3
}

VOICE_CONFIG = {
    'language': 'ru',
    'timeout': 5,
    'phrase_time_limit': 10
}

HIST_THEME_LEN = 15

SENTIMENT_CONFIG = {
    'positive_threshold': 0.1,
    'negative_threshold': -0.1
}
