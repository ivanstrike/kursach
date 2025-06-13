import random
from typing import Dict, List, Optional, Tuple
from text_processor import TextProcessor

class TopicClassifier:
    def __init__(self):
        self.text_processor = TextProcessor()

        self.topic_keywords = {
            'greeting': ['привет', 'здравствовать', 'добрый', 'день', 'утро', 'вечер', 'салют'],
            'goodbye': ['пока', 'свидание', 'встреча', 'прощать'],
            'perfume_interest': ['духи', 'аромат', 'парфюм', 'запах', 'нота', 'композиция', 'флакон'],
            'price_inquiry': ['цена', 'стоимость', 'стоить', 'деньги', 'рубль', 'дорогой', 'дешевый', 'скидка'],
            'recommendation': ['посоветовать', 'рекомендовать', 'подобрать', 'выбрать', 'подходить'],
            'brand_inquiry': ['бренд', 'марка', 'фирма', 'производитель', 'chanel', 'dior', 'ysl'],
            'gender_preference': ['мужской', 'женский', 'унисекс', 'мужчина', 'женщина', 'девушка', 'парень'],
            'occasion': ['работа', 'свидание', 'вечер', 'день', 'праздник', 'офис', 'клуб', 'встреча'],
            'season': ['весна', 'лето', 'осень', 'зима', 'холодный', 'теплый', 'жаркий'],
            'purchase': ['купить', 'заказать', 'приобрести', 'взять', 'покупка', 'оформить'],
            'complaint': ['жалоба', 'проблема', 'не работать', 'плохой', 'ужасный', 'некачественный'],
            'compliment': ['спасибо', 'благодарить', 'отличный', 'хороший', 'замечательный', 'помочь']
        }

    def classify_topic(self, text: str) -> Dict[str, float]:
        if not text:
            return {}

        lemmas = self.text_processor.lemmatize_text(text)

        if not lemmas:
            return {}

        topic_scores = {}

        for topic, keywords in self.topic_keywords.items():
            score = 0
            matched_keywords = []

            for lemma in lemmas:
                for keyword in keywords:
                    if lemma == keyword:
                        score += 1.0
                        matched_keywords.append(lemma)
                    elif keyword in lemma or lemma in keyword:
                        score += 0.5
                        matched_keywords.append(lemma)

            if score > 0:
                normalized_score = score / len(lemmas)
                topic_scores[topic] = {
                    'score': normalized_score,
                    'matched_keywords': matched_keywords
                }

        return topic_scores

    def get_main_topic(self, text: str) -> Tuple[Optional[str], float]:
        topic_scores = self.classify_topic(text)

        if not topic_scores:
            return None, 0.0

        main_topic = max(topic_scores.items(), key=lambda x: x[1]['score'])
        return main_topic[0], main_topic[1]['score']

    def get_main_topic_from_lemmas(self, lemmas: List[str]) -> Tuple[Optional[str], float]:
        if not lemmas:
            return None, 0.0

        topic_scores = {}

        for topic, keywords in self.topic_keywords.items():
            score = 0
            matched_keywords = []

            for lemma in lemmas:
                for keyword in keywords:
                    if lemma == keyword:
                        score += 1.0
                        matched_keywords.append(lemma)
                    elif keyword in lemma or lemma in keyword:
                        score += 0.5
                        matched_keywords.append(lemma)

            if score > 0:
                normalized_score = score / len(lemmas)
                topic_scores[topic] = {
                    'score': normalized_score,
                    'matched_keywords': matched_keywords
                }

        if not topic_scores:
            return None, 0.0

        main_topic = max(topic_scores.items(), key=lambda x: x[1]['score'])
        return main_topic[0], main_topic[1]['score']