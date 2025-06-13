import pickle
import os
from typing import Dict, List, Optional, Tuple, Any
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import numpy as np
from text_processor import TextProcessor
from config import ML_CONFIG
from intents_config import PerfumeBotConfig

class IntentClassifier:

    def __init__(self):
        self.text_processor = TextProcessor()
        self.vectorizer = TfidfVectorizer(**ML_CONFIG['vectorizer_params'])
        self.classifier = MultinomialNB()
        self.is_trained = False
        self.model_path = 'intent_model.pkl'
        self.load_model()

    def prepare_training_data(self, bot_config: PerfumeBotConfig) -> Tuple[List[str], List[str]]:
        X_text = []
        y = []
        for intent, intent_data in bot_config.intents.items():
            for example in intent_data['examples']:
                processed_text = self.text_processor.preprocess_for_ml(example)
                X_text.append(processed_text)
                y.append(intent)

                if len(intent_data['examples']) < 15:
                    augmented = self._augment_text(processed_text)
                    if augmented != processed_text:
                        X_text.append(augmented)
                        y.append(intent)

        return X_text, y

    def _augment_text(self, text: str) -> str:
        synonyms = {
            'духи': ['парфюм', 'аромат', 'запах'],
            'покажи': ['продемонстрируй', 'представь', 'покажите'],
            'хочу': ['желаю', 'мне нужно', 'планирую'],
            'купить': ['приобрести', 'заказать', 'взять'],
            'цена': ['стоимость', 'ценник', 'прайс'],
            'привет': ['здравствуй', 'добрый день', 'салют'],
            'пока': ['до свидания', 'прощай', 'всего хорошего']
        }

        words = text.split()
        for i, word in enumerate(words):
            if word in synonyms and len(synonyms[word]) > 0:
                import random
                if random.random() < 0.3:
                    words[i] = random.choice(synonyms[word])

        return ' '.join(words)

    def train(self, bot_config: PerfumeBotConfig) -> Dict[str, Any]:
        print("Подготовка данных для обучения...")
        X_text, y = self.prepare_training_data(bot_config)
        if len(X_text) < 10:
            print("Недостаточно данных для обучения!")
            return {'success': False, 'error': 'Not enough training data'}

        print(f"Обучение на {len(X_text)} примерах...")
        X = self.vectorizer.fit_transform(X_text)

        if len(X_text) > 20:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
        else:
            X_train, X_test, y_train, y_test = X, X, y, y

        self.classifier.fit(X_train, y_train)
        y_pred = self.classifier.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        print(f"Точность модели: {accuracy:.2f}")

        if len(set(y_test)) > 1:
            print("\nДетальный отчет по классификации:")
            print(classification_report(y_test, y_pred, zero_division=0))

        self.is_trained = True
        self.save_model()

        return {
            'success': True,
            'accuracy': accuracy,
            'training_samples': len(X_text),
            'classes': list(set(y))
        }

    def predict_intent_from_processed(self, processed_text: str) -> Tuple[Optional[str], float]:
        if not self.is_trained:
            return None, 0.0

        if not processed_text:
            return None, 0.0

        try:
            X = self.vectorizer.transform([processed_text])
            intent = self.classifier.predict(X)[0]

            probabilities = self.classifier.predict_proba(X)[0]
            confidence = np.max(probabilities)

            return intent, float(confidence)
        except Exception as e:
            print(f"Ошибка предсказания намерения: {e}")
            return None, 0.0

    def save_model(self):
        try:
            model_data = {
                'vectorizer': self.vectorizer,
                'classifier': self.classifier,
                'is_trained': self.is_trained
            }
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
            print("Модель сохранена!")
        except Exception as e:
            print(f"Ошибка сохранения модели: {e}")

    def load_model(self):
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                self.vectorizer = model_data['vectorizer']
                self.classifier = model_data['classifier']
                self.is_trained = model_data['is_trained']
                print("Модель загружена!")
        except Exception as e:
            print(f"Ошибка загрузки модели: {e}")
            self.is_trained = False
