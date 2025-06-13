from perfumes_data import PERFUMES_CATALOG, RECOMMENDATIONS, PROMOTIONS
from typing import List, Optional, Dict, Any
import random

class PerfumeService:
    """Сервис для работы с каталогом парфюмерии и бизнес-логикой"""

    EMOJI_ICONS = {
        'catalog': '🎯',
        'price': '💰',
        'recommendation': '✨',
        'promotion': '🎁',
        'purchase': '🛒',
        'brand': '👑'
    }

    RESPONSE_TEMPLATES = {
        'catalog_header': "🎯 **Наш каталог элитных ароматов:**\n\n",
        'price_header': "💰 **Цены на наши ароматы:**\n\n",
        'recommendation_header': "✨ **Рекомендации для {category} ароматов:**\n\n",
        'brand_header': "👑 **Ароматы {brand}:**\n\n",
        'promotion_header': "🎁 **Наши специальные предложения:**\n\n",
        'no_perfumes': "К сожалению, сейчас нет ароматов категории '{category}'",
        'no_brand': "К сожалению, ароматов бренда {brand} сейчас нет в наличии 😔",
        'catalog_footer': "Хотите узнать подробнее о каком-то аромате? Просто назовите его!",
        'price_footer': "\n🎁 Действуют специальные предложения! Напишите 'акции' для подробностей.",
        'recommendation_footer': "Какой аромат заинтересовал больше всего?",
        'brand_footer': "Интересует что-то из коллекции {brand}? ",
        'promotion_footer': "Готовы воспользоваться предложением? Скажите 'купить'! 🛒",
        'purchase_no_perfume': "🛒 Замечательно! Какой именно аромат вас заинтересовал?\nИли хотите, чтобы я что-то порекомендовал?"
    }

    CONTACT_INFO = {
        'phone': '+7 (999) 123-45-67',
        'email': 'order@perfume-shop.ru'
    }

    def show_catalog(self) -> str:
        """Показать полный каталог ароматов"""
        response = self.RESPONSE_TEMPLATES['catalog_header']
        for perfume_id, perfume in PERFUMES_CATALOG.items():
            response += self._format_perfume_brief(perfume)
        response += self.RESPONSE_TEMPLATES['catalog_footer']
        return response

    def show_prices(self) -> str:
        """Показать цены на ароматы, отсортированные по возрастанию"""
        response = self.RESPONSE_TEMPLATES['price_header']
        sorted_perfumes = self._get_sorted_perfumes_by_price()
        for perfume_id, perfume in sorted_perfumes:
            response += f"• {perfume['name']}: **{perfume['price']:,} руб.**\n"
        response += self.RESPONSE_TEMPLATES['price_footer']
        return response

    def recommend_by_gender(self, gender: str) -> str:
        """Рекомендации ароматов по полу"""
        recommendations = self._get_perfumes_by_gender(gender)
        if not recommendations:
            return self.RESPONSE_TEMPLATES['no_perfumes'].format(category=gender)
        response = self.RESPONSE_TEMPLATES['recommendation_header'].format(category=gender)
        for perfume_id in recommendations:
            if perfume_id in PERFUMES_CATALOG:
                perfume = PERFUMES_CATALOG[perfume_id]
                response += self._format_perfume_recommendation(perfume)
        response += self.RESPONSE_TEMPLATES['recommendation_footer']
        return response

    def show_promotions(self) -> str:
        """Показать акции и специальные предложения"""
        response = self.RESPONSE_TEMPLATES['promotion_header']
        for promo_id, promo in PROMOTIONS.items():
            response += self._format_promotion(promo)
        response += self.RESPONSE_TEMPLATES['promotion_footer']
        return response

    def show_brand(self, brand: str) -> str:
        """Показать ароматы определенного бренда"""
        brand_perfumes = self._get_perfumes_by_brand(brand)
        if not brand_perfumes:
            return self.RESPONSE_TEMPLATES['no_brand'].format(brand=brand)
        response = self.RESPONSE_TEMPLATES['brand_header'].format(brand=brand)
        for perfume_id, perfume in brand_perfumes:
            response += self._format_perfume_full(perfume)
        response += self.RESPONSE_TEMPLATES['brand_footer'].format(brand=brand)
        return response

    def recommend_by_criteria(self, criteria: str) -> str:
        """Рекомендации по критериям (сезон, повод)"""
        criteria_mapping = self._get_criteria_mapping()
        mapped_criteria = criteria_mapping.get(criteria, criteria)
        season_recs = RECOMMENDATIONS['by_season'].get(mapped_criteria, [])
        if season_recs:
            return self.format_recommendations(season_recs, f"для {mapped_criteria}")
        occasion_recs = RECOMMENDATIONS['by_occasion'].get(mapped_criteria, [])
        if occasion_recs:
            return self.format_recommendations(occasion_recs, f"для {mapped_criteria}")
        return f"🔍 Подбираю ароматы для '{mapped_criteria}'..."

    def format_recommendations(self, perfume_ids: List[str], context: str) -> str:
        """Форматирование рекомендаций"""
        response = f"✨ **Идеальные ароматы {context}:**\n\n"
        for perfume_id in perfume_ids:
            if perfume_id in PERFUMES_CATALOG:
                perfume = PERFUMES_CATALOG[perfume_id]
                response += self._format_perfume_recommendation(perfume)
        response += "Что-то приглянулось? Расскажу подробнее! 😊"
        return response

    def process_purchase_intent(self, text: str) -> str:
        """Обработка намерения покупки"""
        mentioned_perfume = self.extract_perfume_from_text(text)
        if mentioned_perfume:
            return self._format_purchase_response(mentioned_perfume)
        return self.RESPONSE_TEMPLATES['purchase_no_perfume']

    def extract_perfume_from_text(self, text: str) -> Optional[str]:
        """Извлечение упоминания парфюма из текста"""
        text_lower = text.lower()
        for perfume_id, perfume in PERFUMES_CATALOG.items():
            if perfume['name'].lower() in text_lower:
                return perfume_id
        for perfume_id, perfume in PERFUMES_CATALOG.items():
            if self._check_perfume_keywords(text_lower, perfume):
                return perfume_id
        return None

    def _format_perfume_brief(self, perfume: Dict[str, Any]) -> str:
        return (f"**{perfume['name']}** ({perfume['brand']})\n"
                f"{perfume['price']:,} руб. | {perfume['volume']}\n"
                f"{perfume['gender'].title()}\n"
                f"{perfume['description'][:80]}...\n\n")

    def _format_perfume_full(self, perfume: Dict[str, Any]) -> str:
        return (f"✨ **{perfume['name']}**\n"
                f"💰 {perfume['price']:,} руб. | 📦 {perfume['volume']}\n"
                f"👤 {perfume['gender'].title()}\n"
                f"📝 {perfume['description']}\n\n")

    def _format_perfume_recommendation(self, perfume: Dict[str, Any]) -> str:
        return (f"✨ **{perfume['name']}**\n"
                f"💰 {perfume['price']:,} руб.\n"
                f"📝 {perfume['description']}\n\n")

    def _format_promotion(self, promo: Dict[str, Any]) -> str:
        discount_percent = int(promo['discount'] * 100)
        response = f"🎁 **{promo['description']}**\n"
        response += f"💸 Скидка: {discount_percent}%\n"
        if 'code' in promo:
            response += f"🏷️ Промокод: `{promo['code']}`\n"
        if 'min_items' in promo:
            response += f"📦 Минимум товаров: {promo['min_items']}\n"
        response += "\n"
        return response

    def _format_purchase_response(self, perfume_id: str) -> str:
        perfume = PERFUMES_CATALOG[perfume_id]
        response = f"🛒 **Отличный выбор!**\n\n"
        response += f"✨ {perfume['name']}\n"
        response += f"💰 {perfume['price']:,} руб.\n\n"
        response += "📞 Для оформления заказа свяжитесь с нами:\n"
        response += f"📱 {self.CONTACT_INFO['phone']}\n"
        response += f"📧 {self.CONTACT_INFO['email']}\n\n"
        response += "🎁 Не забудьте про наши акции!"
        return response

    def _get_sorted_perfumes_by_price(self) -> List[tuple]:
        return sorted(PERFUMES_CATALOG.items(), key=lambda x: x[1]['price'])

    def _get_perfumes_by_gender(self, gender: str) -> List[str]:
        return RECOMMENDATIONS['by_gender'].get(gender, [])

    def _get_perfumes_by_brand(self, brand: str) -> List[tuple]:
        return [(pid, p) for pid, p in PERFUMES_CATALOG.items() if p['brand'].lower() == brand.lower()]

    def _get_criteria_mapping(self) -> Dict[str, str]:
        return {
            'evening': 'вечер',
            'work': 'работа',
            'spring': 'весна',
            'summer': 'лето',
            'autumn': 'осень',
            'winter': 'зима'
        }

    def _check_perfume_keywords(self, text_lower: str, perfume: Dict[str, Any]) -> bool:
        brand_words = perfume['brand'].lower().split()
        name_words = perfume['name'].lower().split()
        for brand_word in brand_words:
            if brand_word in text_lower:
                for name_word in name_words:
                    if name_word in text_lower and len(name_word) > 3:
                        return True
        return False

    def get_perfume_details(self, perfume_id: str) -> Optional[str]:
        if perfume_id not in PERFUMES_CATALOG:
            return None
        perfume = PERFUMES_CATALOG[perfume_id]
        return self._format_perfume_full(perfume)

    def search_perfumes(self, query: str) -> List[str]:
        query_lower = query.lower()
        results = []
        for perfume_id, perfume in PERFUMES_CATALOG.items():
            if (query_lower in perfume['name'].lower() or
                query_lower in perfume['brand'].lower() or
                query_lower in perfume['description'].lower()):
                results.append(perfume_id)
        return results
