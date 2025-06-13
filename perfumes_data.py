PERFUMES_CATALOG = {
    'chanel_no5': {
        'name': 'Chanel No. 5',
        'price': 12500,
        'description': 'Легендарный аромат с нотами альдегидов, иланг-иланга и сандала',
        'notes': {
            'top': ['альдегиды', 'лимон', 'нероли'],
            'heart': ['роза', 'жасмин', 'иланг-иланг'],
            'base': ['сандал', 'ветивер', 'амбра']
        },
        'gender': 'женский',
        'volume': '100ml',
        'brand': 'Chanel',
        'season': ['весна', 'лето'],
        'occasion': ['вечер', 'особый случай'],
        'longevity': 'долгий',
        'image_url': 'https://example.com/chanel5.jpg',
        'url': 'chanel-no5'
    },
    'dior_sauvage': {
        'name': 'Dior Sauvage',
        'price': 8900,
        'description': 'Свежий мужской аромат с нотами бергамота и амброксана',
        'notes': {
            'top': ['калабрийский бергамот', 'перец'],
            'heart': ['лаванда', 'розовый перец', 'ветивер'],
            'base': ['амброксан', 'кедр', 'лабданум']
        },
        'gender': 'мужской',
        'volume': '100ml',
        'brand': 'Dior',
        'season': ['весна', 'лето', 'осень'],
        'occasion': ['день', 'работа', 'спорт'],
        'longevity': 'средний',
        'image_url': 'https://example.com/dior_sauvage.jpg',
        'url': 'christian-dior-sauvage-eau-de-parfum'
    },
    'tom_ford_black_orchid': {
        'name': 'Tom Ford Black Orchid',
        'price': 15800,
        'description': 'Роскошный унисекс аромат с нотами черной орхидеи и шоколада',
        'notes': {
            'top': ['черная орхидея', 'черная смородина', 'бергамот'],
            'heart': ['орхидея', 'специи', 'фруктовые ноты'],
            'base': ['пачули', 'ваниль', 'сандал', 'шоколад']
        },
        'gender': 'унисекс',
        'volume': '50ml',
        'brand': 'Tom Ford',
        'season': ['осень', 'зима'],
        'occasion': ['вечер', 'свидание', 'особый случай'],
        'longevity': 'очень долгий',
        'image_url': 'https://example.com/tom_ford_black_orchid.jpg',
        'url': 'tom-ford-black-orchid'
    },
    'creed_aventus': {
        'name': 'Creed Aventus',
        'price': 22000,
        'description': 'Престижный мужской аромат с фруктовыми и древесными нотами',
        'notes': {
            'top': ['ананас', 'черная смородина', 'яблоко', 'бергамот'],
            'heart': ['роза', 'береза', 'жасмин', 'пачули'],
            'base': ['мускус', 'дубовый мох', 'амбра', 'ваниль']
        },
        'gender': 'мужской',
        'volume': '120ml',
        'brand': 'Creed',
        'season': ['весна', 'лето', 'осень'],
        'occasion': ['день', 'работа', 'особый случай'],
        'longevity': 'очень долгий',
        'image_url': 'https://example.com/creed_aventus.jpg',
        'url': 'creed-aventus'
    },
    'ysl_black_opium': {
        'name': 'YSL Black Opium',
        'price': 7200,
        'description': 'Соблазнительный женский аромат с нотами кофе и ванили',
        'notes': {
            'top': ['розовый перец', 'груша', 'мандарин'],
            'heart': ['кофе', 'жасмин', 'горький миндаль'],
            'base': ['ваниль', 'пачули', 'кедр', 'кашмеран']
        },
        'gender': 'женский',
        'volume': '90ml',
        'brand': 'Yves Saint Laurent',
        'season': ['осень', 'зима'],
        'occasion': ['вечер', 'свидание', 'клуб'],
        'longevity': 'долгий',
        'image_url': 'https://example.com/ysl_black_opium.jpg',
        'url': 'ysl-black-opium?etext=2202.E5v14_WdQjf1h-SoQ2H9WXWMpKLBextytHdYnu5ugD5qdmdyZGJ6ZWNpaWRxc2Jl.4c57b629400892d2ec26bb4ebad2d635d138a723'
    }
}

PROMOTIONS = {
    'first_buy': {
        'description': 'Скидка 15% на первую покупку',
        'discount': 0.15,
        'code': 'FIRST15'
    },
    'luxury_set': {
        'description': 'При покупке двух ароматов - скидка 20%',
        'discount': 0.20,
        'min_items': 2
    },
    'seasonal': {
        'description': 'Весенняя распродажа - скидка 10%',
        'discount': 0.10,
        'code': 'SPRING10'
    }
}

RECOMMENDATIONS = {
    'by_gender': {
        'мужской': ['dior_sauvage', 'creed_aventus'],
        'женский': ['chanel_no5', 'ysl_black_opium'],
        'унисекс': ['tom_ford_black_orchid']
    },
    'by_season': {
        'весна': ['chanel_no5', 'dior_sauvage', 'creed_aventus'],
        'лето': ['chanel_no5', 'dior_sauvage', 'creed_aventus'],
        'осень': ['dior_sauvage', 'tom_ford_black_orchid', 'creed_aventus', 'ysl_black_opium'],
        'зима': ['tom_ford_black_orchid', 'ysl_black_opium']
    },
    'by_occasion': {
        'работа': ['dior_sauvage', 'creed_aventus'],
        'свидание': ['tom_ford_black_orchid', 'ysl_black_opium'],
        'особый случай': ['chanel_no5', 'tom_ford_black_orchid', 'creed_aventus'],
        'день': ['dior_sauvage', 'creed_aventus'],
        'вечер': ['chanel_no5', 'tom_ford_black_orchid', 'ysl_black_opium']
    },
    'by_price': {
        'budget': ['ysl_black_opium'],
        'medium': ['dior_sauvage', 'chanel_no5'],
        'luxury': ['tom_ford_black_orchid', 'creed_aventus']
    }
}
