import itertools
import random
from datetime import datetime, timedelta

all_keywords = {
        'DE': ['Kostenloser Versand ', 'Jetzt einkaufen', '1+1 GRATIS', 'Holen Sie es jetzt ', 'Bestellen jetzt', '50% Rabatt', '60% Rabatt', '65% Rabatt', 'Bringen Sie es nach Hause', 'Hier kaufen', 'Jetzt kaufen', 'Beanspruchen Sie Ihr', 'Klicken Sie hier', 'Kostenloser Versand', 'Holen Sie es sich hier', 'Holen Sie sich Ihre', 'Holen Sie sich Ihr', 'Bestellen Sie hier', 'Link bestellen', 'Hier einkaufen', 'Jetzt einkaufen', 'Einen Freund markieren', 'Jemanden markieren', 'Nicht im Handel erhältlich', 'Die Leute sind verrückt nach'],
        'DK': ['Gratis levering!', '0% RABAT ', 'Bestil i dag med', 'tøj til kvinder', 'mode stil'],
        'FR': ['Livraison gratuite', 'Achetez maintenant', '1+1 GRATUIT', 'Obtenez-le maintenant', 'Commandez maintenant'],
        'NL': ['0% korting', 'Bestel Hier', 'Korting speciaal voor jou', 'Profiteer vandaag', 'Gratis Verzending', 'Profiteer van onze', 'Bestel NU'],
        'NO': ['Gratis frakt', '0% Rabatt', 'Få din nå', 'Bestill nå', 'gratis frakt i norge'],
        'SE': ['GRATIS Leverans!', 'Fri frakt', 'Mer info här  ', 'Handla nu ', '0% rabatt', 'Få hit den nu med 1+1 GRATIS'],
        'UK': ['Fast & Free UK Shipping ', 'Free Shipping ', 'Shop Now', 'Limited Offer', 'Get yours now', '30% off', '50% off', '60% off', '65% off', 'Bring it home', 'Buy here', 'Buy now', 'Claim yours', 'Click here', 'Free Shipping', 'Get it here', 'Get yours', 'Grab yours', 'Order here', 'Order link', 'Shop here', 'Shop now', 'Tag a friend', 'Tag someone', 'Not sold in stores', 'People are going crazy over'],
        'US': ['Fast & Free Shipping ', 'Free Shipping ', 'Shop Now', 'Limited Offer', 'Get yours now', '30% off', '50% off', '60% off', '65% off', 'Bring it home', 'Buy here', 'Buy now', 'Claim yours', 'Click here', 'Free Shipping', 'Get it here', 'Get yours', 'Grab yours', 'Order here', 'Order link', 'Shop here', 'Shop now', 'Tag a friend', 'Tag someone', 'Not sold in stores', 'People are going crazy over']
}
media_types = [
    'meme',
    'image',
    'image_and_meme',
    'video',
]


def get_date_ranges():
    start_date = '2022-01-01'
    format = '%Y-%m-%d'
    now = datetime.now()
    date_ranges = [
        ('', start_date),
    ]
    start_date = datetime.strptime(start_date, format)
    while start_date < now:
        end_date = start_date + timedelta(days=30)
        if end_date > now:
            date_ranges.append((start_date.strftime(format), ''))
            break
        date_ranges.append((start_date.strftime(format), end_date.strftime(format)))
        start_date = end_date

    return date_ranges


def get_country_keyword_combinations():
    combinations = []
    date_ranges = get_date_ranges()
    for country, keywords in all_keywords.items():
        for keyword in keywords:
            for m_type, date_range in itertools.product(media_types, date_ranges):
                combinations.append((country, keyword, m_type, date_range[0], date_range[1]))

    random.shuffle(combinations)

    return combinations
