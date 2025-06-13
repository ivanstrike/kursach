import random
import pickle
import os
from typing import Dict, List, Optional, Tuple, Any
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np
from difflib import SequenceMatcher

from text_processor import TextProcessor
from sentiment_analyzer import SentimentAnalyzer
from topic_classifier import TopicClassifier
from perfumes_data import PERFUMES_CATALOG, RECOMMENDATIONS, PROMOTIONS
from config import ML_CONFIG
from intents_config import PerfumeBotConfig
from perfume_service import PerfumeService
from intent_classifier import IntentClassifier

class PerfumeBot:
    """Основной класс чат-бота для продажи духов"""

    BUSINESS_INTENTS = {
        'perfume_catalog', 'price_inquiry', 'purchase_intent',
        'promotion_inquiry', 'brand_chanel', 'brand_dior',
        'season_spring', 'season_summer', 'season_autumn', 'season_winter'
    }
    CASUAL_INTENTS = {
        'greeting', 'goodbye', 'bot_name', 'bot_identity', 'help', 'joke',
        'smalltalk_mood', 'smalltalk_compliment', 'smalltalk_gratitude', 'smalltalk_activity',
        'location_question', 'abilities', 'age_question', 'inspiration', 'weather', 'recommendation_unsure'
    }
    RECOMMEND_KEYWORDS = ['порекомендуй', 'посоветуй', 'подскажи', 'что выбрать', 'помоги выбрать']
    PURCHASE_KEYWORDS = ['купить', 'заказать', 'приобрести', 'взять']
    CATALOG_KEYWORDS = ['каталог', 'что есть', 'покажи', 'ассортимент']
    PRICE_KEYWORDS = ['цена', 'стоит', 'стоимость', 'цены', 'прайс']
    MALE_KEYWORDS = ['мужск', 'для мужчины', 'парню', 'для него']
    FEMALE_KEYWORDS = ['женск', 'для женщины', 'девушке', 'для неё']
    FRIENDLY_KEYWORDS = ['как дела', 'что посоветуешь']


    def __init__(self):
        self.config = PerfumeBotConfig()
        self.text_processor = TextProcessor()
        self.intent_classifier = IntentClassifier()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.topic_classifier = TopicClassifier()
        self.perfume_service = PerfumeService()
        self.user_preferences = {}
        self.theme_history = []
        self.conversation_stage = 'casual'
        self.message_count = 0
        self.casual_message_count = 0
        self.casual_topics_discussed = set()
        self.last_casual_response = None
        self.casual_messages_threshold = 4
        self.offer_made = False
        self.stats = {'intent': 0, 'generate': 0, 'failure': 0, 'casual': 0}
        if not self.intent_classifier.is_trained:
            print("Внимание: ML-модель не обучена! Запустите train_intent_model.py для обучения.")

    def process_message(self, text: str, user_id: str = None) -> str:
        if not text or not text.strip():
            return random.choice(self.config.failure_phrases)

        self.message_count += 1

        cleaned_text = self.text_processor.clear_phrase(text)
        lemmas = self.text_processor.lemmatize_text(cleaned_text)
        processed_for_ml = ' '.join(lemmas)

        sentiment = self.sentiment_analyzer.analyze_sentiment_from_lemmas(lemmas)
        topic, topic_score = self.topic_classifier.get_main_topic_from_lemmas(lemmas)
        intent, confidence = self.intent_classifier.predict_intent_from_processed(processed_for_ml)

        print(f"[DEBUG] text: '{text}' | intent: {intent} | confidence: {confidence:.3f} | topic: {topic} | topic_score: {topic_score}")



        if intent is not None and confidence >= 0.1:
            if self._is_casual_intent(intent):
                self.casual_message_count += 1
            elif self._is_business_intent(intent):
                self.casual_message_count = 0
            response = self._generate_contextual_response(text, intent, confidence, sentiment, topic)
            return response

        keyword_response = self._handle_keywords(text)
        if keyword_response:
            return keyword_response

        fallback_intent = self._detect_brand_fallback(text)
        if fallback_intent:
            intent = fallback_intent
            confidence = 0.8
            response = self._generate_contextual_response(text, intent, confidence, sentiment, topic)
            return response

        if (intent is None or confidence < 0.1):
            dialogue_response = self._search_in_dialogues(text)
            if dialogue_response:
                self.stats['generate'] += 1
                return dialogue_response

        return random.choice(self.config.failure_phrases)

    def _generate_contextual_response(self, text: str, intent: str, confidence: float,
                                    sentiment: Dict, topic: str) -> str:

        if self._is_business_intent(intent):
            self.conversation_stage = 'business'
            return self._generate_business_response(text, intent, confidence, sentiment, topic)

        if self._is_casual_intent(intent):
            if intent == 'goodbye':
                self.reset_conversation()
            response = self._generate_casual_response(text, intent, confidence, sentiment, topic)

            if (self.casual_message_count >= self.casual_messages_threshold and
                not self.offer_made and
                self.conversation_stage == 'casual'):

                response += self._add_natural_transition()
                self.conversation_stage = 'warming_up'
                self.offer_made = True

            return response

        dialogue_response = self._search_in_dialogues(text)
        if dialogue_response:
            self.stats['generate'] += 1
            return dialogue_response

        if intent and confidence > 0.3:
            return self._handle_intent(intent, text, sentiment)

        if topic and sentiment['label'] != 'negative':
            return self._handle_topic(topic, text, sentiment)

        if sentiment['label'] == 'negative' and sentiment['confidence'] > 0.5:
            return self._handle_negative_sentiment(text, sentiment)

        self.stats['failure'] += 1
        return random.choice(self.config.failure_phrases)

    def _handle_intent(self, intent: str, text: str, sentiment: Dict) -> str:
        self.stats['intent'] += 1

        intent_data = self.config.intents.get(intent, {})

        if 'action' in intent_data:
            return self._execute_action(intent_data['action'], text, sentiment)

        responses = intent_data.get('responses', [])
        if responses:
            base_response = random.choice(responses)
            if sentiment['label'] == 'positive':
                return base_response + " " + self._get_positive_addition()
            return base_response

        return random.choice(self.config.failure_phrases)

    def _execute_action(self, action: str, text: str, sentiment: Dict) -> str:
        business_actions = {
            'show_catalog': lambda: self.perfume_service.show_catalog(),
            'show_prices': lambda: self.perfume_service.show_prices(),
            'recommend_male': lambda: self.perfume_service.recommend_by_gender('мужской'),
            'recommend_female': lambda: self.perfume_service.recommend_by_gender('женский'),
            'show_promotions': lambda: self.perfume_service.show_promotions(),
            'show_chanel': lambda: self.perfume_service.show_brand('Chanel'),
            'show_dior': lambda: self.perfume_service.show_brand('Dior'),
            'process_purchase': lambda: self.perfume_service.process_purchase_intent(text)
        }
        if action in business_actions:
            return business_actions[action]()
        elif action.startswith('recommend_'):
            season_or_occasion = action.replace('recommend_', '')
            return self.perfume_service.recommend_by_criteria(season_or_occasion)

        for intent_name, intent_data in self.config.intents.items():
            if intent_data.get('action') == action:
                responses = intent_data.get('responses', [])
                if responses:
                    return random.choice(responses)
        return "С удовольствием!"

    def _generate_casual_response(self, text: str, intent: str, confidence: float,
                                sentiment: Dict, topic: str) -> str:
        self.stats['casual'] += 1
        self.casual_topics_discussed.add(intent)

        intent_data = self.config.intents.get(intent, {})
        responses = intent_data.get('responses', [])

        if responses and confidence > 0.1:
            response = random.choice(responses)

            if intent == 'greeting' and self.message_count > 1:
                follow_up = [
                    " Как прошел день?", " Что интересного?",
                    " Как настроение?", " Что нового?"
                ]
                response += random.choice(follow_up)

            return response

        return self.sentiment_analyzer.get_emotion_response(sentiment)

    def _generate_business_response(self, text: str, intent: str, confidence: float,
                                  sentiment: Dict, topic: str) -> str:
        self.stats['intent'] += 1

        return self._handle_intent(intent, text, sentiment)

    def _add_natural_transition(self) -> str:
        transitions = [
            "\n\nКстати, а вы любите ароматы? У меня есть несколько интересных предложений! ",
            "\n\nА знаете, раз мы так хорошо общаемся... Может, расскажу вам о чудесных ароматах? ",
            "\n\nЗдорово пообщались! А не хотели бы узнать о прекрасных парфюмах? ",
            "\n\nКстати, а как относитесь к парфюмерии? Могу показать что-то особенное! "
        ]
        return random.choice(transitions)

    def _detect_brand_fallback(self, text: str) -> Optional[str]:
        text_lower = text.lower()

        chanel_keywords = ['chanel', 'шанель', 'коко', 'coco', 'номер 5', 'no 5', 'chance', 'bleu', 'gabrielle', 'allure']
        dior_keywords = ['dior', 'диор', 'miss', 'sauvage', 'jadore', 'j\'adore', 'poison', 'fahrenheit', 'joy', 'addict']

        chanel_matches = sum(1 for keyword in chanel_keywords if keyword in text_lower)
        dior_matches = sum(1 for keyword in dior_keywords if keyword in text_lower)

        if chanel_matches > dior_matches and chanel_matches > 0:
            return 'brand_chanel'
        elif dior_matches > chanel_matches and dior_matches > 0:
            return 'brand_dior'

        return None

    def get_stats(self) -> Dict[str, int]:
        return self.stats.copy()

    def reset_conversation(self):
        self.conversation_history = []
        self.user_preferences = {}
        self.current_theme = None
        self.theme_history = []

        self.conversation_stage = 'casual'
        self.message_count = 0
        self.casual_message_count = 0
        self.casual_topics_discussed = set()
        self.offer_made = False

    @staticmethod
    def _is_business_intent(intent: str) -> bool:
        return intent in PerfumeBot.BUSINESS_INTENTS

    @staticmethod
    def _is_casual_intent(intent: str) -> bool:
        return intent in PerfumeBot.CASUAL_INTENTS

    def _handle_keywords(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        if any(word in text_lower for word in self.RECOMMEND_KEYWORDS):
            return "С удовольствием помогу с выбором! \n\nРасскажите:\n• Для кого аромат?\n• На какой случай?\n• Какие ароматы нравятся?"
        if any(word in text_lower for word in self.PURCHASE_KEYWORDS):
            return "🛒 Замечательно! Какой именно аромат вас заинтересовал?\nИли хотите, чтобы я что-то порекомендовал? "
        if any(word in text_lower for word in self.CATALOG_KEYWORDS):
            return self.perfume_service.show_catalog()
        if any(word in text_lower for word in self.PRICE_KEYWORDS):
            return self.perfume_service.show_prices()
        if any(word in text_lower for word in self.MALE_KEYWORDS):
            return self.perfume_service.recommend_by_gender('мужской')
        if any(word in text_lower for word in self.FEMALE_KEYWORDS):
            return self.perfume_service.recommend_by_gender('женский')
        if any(word in text_lower for word in self.FRIENDLY_KEYWORDS):
            friendly_responses = [
                "Отлично! Готов помочь вам с выбором прекрасных ароматов! ",
                "Прекрасно! Давайте подберем вам идеальный аромат! ",
                "Замечательно! Расскажите, что вас интересует в мире парфюмерии? "
            ]
            return random.choice(friendly_responses)
        return None

    def _normalize_for_dialogue(self, text: str) -> str:
        import re
        text = text.lower()
        text = re.sub(r'[\W_]+', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _search_in_dialogues(self, text: str) -> Optional[str]:
        try:
            dialogue_file = 'dialogues.txt'
            if not os.path.exists(dialogue_file):
                return None
            with open(dialogue_file, 'r', encoding='utf-8') as f:
                content = f.read()
            dialogues = self._parse_dialogues(content)
            if not isinstance(dialogues, list):
                return None
            dialogues = [tuple(item) for item in dialogues if isinstance(item, (list, tuple)) and len(item) == 2]
            if not dialogues:
                return None
            best_match = None
            best_score = 0.0
            norm_user = self._normalize_for_dialogue(text)
            threshold = 0.45 if len(norm_user) > 20 else 0.35
            for question, answer in dialogues:
                norm_q = self._normalize_for_dialogue(question)
                if norm_user == norm_q or norm_user in norm_q or norm_q in norm_user:
                    return answer
                similarity = SequenceMatcher(None, norm_user, norm_q).ratio()
                if similarity > best_score and similarity > threshold:
                    best_score = similarity
                    best_match = answer
            return best_match
        except Exception as e:
            print(f"Ошибка при поиске в диалогах: {e}")
            return None

    def _parse_dialogues(self, content: str) -> List[Tuple[str, str]]:
        """Парсинг файла диалогов"""
        dialogues = []
        lines = content.strip().split('\n')

        current_question = None
        current_answer = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith('Q:'):
                current_question = line[2:].strip()
            elif (line.startswith('A:') or line.startswith('А:')) and current_question:
                current_answer = line[2:].strip()
                dialogues.append((current_question, current_answer))
                current_question = None
                current_answer = None

        return dialogues

    def _handle_topic(self, topic: str, text: str, sentiment: Dict) -> str:
        topic_responses = {
            'perfume_interest': [
                "Отлично! Расскажите, какой стиль ароматов предпочитаете? ",
                "Прекрасно! Для кого подбираем аромат? "
            ],
            'price_inquiry': [
                "Конечно! Покажу наши цены... ",
                "С радостью расскажу о ценах! "
            ],
            'recommendation': [
                "Обязательно помогу с выбором! Расскажите о предпочтениях ",
                "Подберу идеальный аромат! Какой стиль нравится? "
            ]
        }

        responses = topic_responses.get(topic, [])
        if responses:
            return random.choice(responses)

        return "Интересная тема! Расскажите подробнее "

    def _handle_negative_sentiment(self, text: str, sentiment: Dict) -> str:
        responses = [
            "Понимаю ваши сомнения. Давайте найдем то, что вам точно понравится! ",
            "Не переживайте! У нас есть ароматы на любой вкус! ",
            "Позвольте предложить вам что-то особенное! "        ]
        return random.choice(responses)

    def _get_positive_addition(self) -> str:
        additions = [
            "Вы точно не пожалеете!",
            "Это будет отличный выбор!", "Уверен, вам понравится!"
        ]
        return random.choice(additions)
