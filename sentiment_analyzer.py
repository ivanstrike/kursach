import random
from typing import Dict, List, Optional, Tuple
from text_processor import TextProcessor

class SentimentAnalyzer:
    def __init__(self):
        self.text_processor = TextProcessor()

        self.sentiment_dict = {
            'хороший': 0.7, 'отличный': 0.9, 'прекрасный': 0.8, 'замечательный': 0.8,
            'нравиться': 0.6, 'любить': 0.8, 'восхитительный': 0.9, 'классный': 0.6,
            'красивый': 0.7, 'приятный': 0.6, 'качественный': 0.7, 'роскошный': 0.8,
            'элегантный': 0.7, 'стильный': 0.6, 'модный': 0.5, 'популярный': 0.4,
            'известный': 0.3, 'брендовый': 0.4, 'дорогой': 0.2, 'престижный': 0.6,
            'соблазнительный': 0.7, 'притягательный': 0.6, 'чувственный': 0.7,
            'свежий': 0.5, 'легкий': 0.4, 'долгий': 0.5, 'стойкий': 0.6,

            'плохой': -0.7, 'ужасный': -0.9, 'отвратительный': -0.9, 'некачественный': -0.8,
            'дешевый': -0.5, 'дорогой': -0.3, 'странный': -0.4, 'неприятный': -0.6,
            'невкусный': -0.7, 'резкий': -0.5, 'химический': -0.6, 'искусственный': -0.4,
            'слабый': -0.4, 'короткий': -0.3, 'не': -0.5, 'нет': -0.3,
            'ненавидеть': -0.8, 'разочаровать': -0.6, 'расстроить': -0.5,

            'обычный': 0.0, 'нормальный': 0.0, 'средний': 0.0, 'простой': 0.0,
            'покупать': 0.1, 'выбирать': 0.0, 'искать': 0.0, 'нужный': 0.1,
            'подходить': 0.2, 'рекомендовать': 0.3, 'советовать': 0.2
        }

    def analyze_sentiment_from_lemmas(self, lemmas: List[str]) -> Dict[str, float]:
        if not lemmas:
            return {'score': 0.0, 'label': 'neutral', 'confidence': 0.0}

        total_score = 0.0
        word_count = 0
        sentiment_words = []

        for lemma in lemmas:
            if lemma in self.sentiment_dict:
                score = self.sentiment_dict[lemma]
                total_score += score
                word_count += 1
                sentiment_words.append((lemma, score))

        if word_count > 0:
            avg_score = total_score / word_count
            confidence = min(word_count / len(lemmas), 1.0)
        else:
            avg_score = 0.0
            confidence = 0.0

        if avg_score > 0.1:
            label = 'positive'
        elif avg_score < -0.1:
            label = 'negative'
        else:
            label = 'neutral'

        return {
            'score': avg_score,
            'label': label,
            'confidence': confidence,
            'sentiment_words': sentiment_words
        }

    def get_emotion_response(self, sentiment: Dict[str, float], context: str = '') -> str:
        label = sentiment['label']
        score = sentiment['score']

        if label == 'positive':
            if score > 0.6:
                responses = [
                    "Отлично! Вижу, вы цените качественные ароматы! ",
                    "Замечательно! У нас есть именно то, что вам понравится! ",
                    "Прекрасно! Давайте найдем для вас идеальный аромат! "
                ]
            else:
                responses = [
                    "Хорошо! Расскажу вам о наших лучших предложениях!",
                    "Понимаю! У нас много интересных вариантов!",
                    "Отлично! Помогу подобрать что-то подходящее!"
                ]
        elif label == 'negative':
            if score < -0.6:
                responses = [
                    "Понимаю ваши сомнения. Позвольте показать вам что-то особенное!",
                    "Не переживайте! У нас есть ароматы на любой вкус!",
                    "Давайте найдем то, что вам точно понравится! "
                ]
            else:
                responses = [
                    "Понимаю. Возможно, стоит рассмотреть другие варианты?",
                    "Хорошо, давайте поищем что-то более подходящее!",
                    "Не проблема! У нас широкий выбор!"
                ]
        else:
            responses = [
                "Понятно. Расскажите больше о ваших предпочтениях!",
                "Хорошо. Что вас интересует в ароматах?",
                "Отлично! Давайте подберем что-то специально для вас!"
            ]

        return random.choice(responses)


