from intents_config import PerfumeBotConfig
from perfume_bot import IntentClassifier

if __name__ == "__main__":
    print("=== Обучение ML-модели для классификации интентов ===")
    config = PerfumeBotConfig()
    classifier = IntentClassifier()
    result = classifier.train(config)
    print(f"Результат обучения: {result}")
    if result['success']:
        print("Модель успешно обучена и сохранена в intent_model.pkl")
    else:
        print("Ошибка обучения: ", result.get('error'))
