import json
from typing import Dict, List, Tuple, Optional

class IntentsConfig:
    def __init__(self, path: str = 'intents.json'):
        with open(path, 'r', encoding='utf-8') as f:
            self.intents: Dict[str, Dict] = json.load(f)
        self.failure_phrases: List[str] = [
            'Извините, не совсем понял. Можете перефразировать? ',
            'Не уловил смысл. Расскажите подробнее о том, что вас интересует? ',
            'Хм, интересно... А можете объяснить по-другому? ',
            'Давайте начнем сначала. Что именно вы ищете? '
        ]

    def get_intents(self) -> Dict[str, Dict]:
        return self.intents

    def get_failure_phrases(self) -> List[str]:
        return self.failure_phrases

    def add_intent(self, intent_name: str, intent_data: dict) -> None:
        self.intents[intent_name] = intent_data

    def remove_intent(self, intent_name: str) -> None:
        if intent_name in self.intents:
            del self.intents[intent_name]

    def get_intent_info(self, intent_name: str) -> Optional[Dict]:
        return self.intents.get(intent_name, None)

    def get_all_examples(self) -> Tuple[List[str], List[str]]:
        examples: List[str] = []
        labels: List[str] = []
        for intent_name, intent_data in self.intents.items():
            for example in intent_data.get('examples', []):
                examples.append(example)
                labels.append(intent_name)
        return examples, labels

    def get_intent_count(self) -> int:
        return len(self.intents)

    def get_examples_count(self) -> int:
        return sum(len(intent_data.get('examples', [])) for intent_data in self.intents.values())

    def validate_intents(self) -> List[str]:
        errors: List[str] = []
        seen_examples = set()
        for intent_name, intent_data in self.intents.items():
            examples = intent_data.get('examples', [])
            if not examples:
                errors.append(f"Намерение '{intent_name}' не содержит примеров")
            for ex in examples:
                if ex in seen_examples:
                    errors.append(f"Дублирующий пример '{ex}' в интенте '{intent_name}'")
                seen_examples.add(ex)
            if not intent_data.get('responses') and not intent_data.get('action'):
                errors.append(f"Намерение '{intent_name}' не содержит ни responses, ни action")
        return errors

def create_intents_config() -> IntentsConfig:
    return IntentsConfig()

class PerfumeBotConfig(IntentsConfig):
    pass
