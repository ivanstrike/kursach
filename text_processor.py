import re
from typing import List
from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsMorphTagger,
    Doc
)
import pymorphy2

class TextProcessor:
    def __init__(self):
        self.segmenter = Segmenter()
        self.morph_vocab = MorphVocab()
        self.emb = NewsEmbedding()
        self.morph_tagger = NewsMorphTagger(self.emb)

        self.morph = pymorphy2.MorphAnalyzer()

        self.alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя- '

        self.stop_words = {
            'а', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как', 'к', 'по',
            'из', 'за', 'от', 'до', 'при', 'о', 'об', 'для', 'или', 'и', 'но', 'да',
            'нет', 'это', 'то', 'же', 'ли', 'бы', 'был', 'была', 'было', 'были'
        }

    def clear_phrase(self, phrase: str) -> str:
        if not phrase:
            return ""

        phrase = phrase.lower().strip()
        phrase = re.sub(r'\s+', ' ', phrase)
        phrase = re.sub(r'[^\w\s-]', ' ', phrase)
        result = ''.join(symbol for symbol in phrase if symbol in self.alphabet)
        result = re.sub(r'[-\s]+', ' ', result).strip()

        return result

    def lemmatize_text(self, text: str) -> List[str]:
        text = self.clear_phrase(text)
        if not text:
            return []

        try:
            doc = Doc(text)
            doc.segment(self.segmenter)
            doc.tag_morph(self.morph_tagger)

            lemmas = []
            for token in doc.tokens:
                if token.text and len(token.text) > 1:
                    if hasattr(token, 'lemma') and token.lemma:
                        lemma = token.lemma.lower()
                    else:
                        parsed = self.morph.parse(token.text)[0]
                        lemma = parsed.normal_form.lower()

                    if lemma not in self.stop_words and len(lemma) > 2:
                        lemmas.append(lemma)

            return lemmas

        except Exception as e:
            print(f"Ошибка лемматизации с Natasha: {e}")
            return self._lemmatize_with_pymorphy(text)

    def _lemmatize_with_pymorphy(self, text: str) -> List[str]:
        words = text.split()
        lemmas = []

        for word in words:
            if len(word) > 2:
                parsed = self.morph.parse(word)[0]
                lemma = parsed.normal_form.lower()
                if lemma not in self.stop_words:
                    lemmas.append(lemma)

        return lemmas

    def preprocess_for_ml(self, text: str) -> str:
        text = self.clear_phrase(text)
        lemmas = self.lemmatize_text(text)
        return ' '.join(lemmas)
