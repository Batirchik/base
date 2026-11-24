#!/usr/bin/env python3
"""Keep a video only when its public description has a recipe, a protocol, or a concrete recommendation."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BODY_PARTS = json.loads((ROOT / "src" / "data" / "bodyParts.json").read_text(encoding="utf-8"))
BODY_IDS = [row["id"] for row in BODY_PARTS]

GEN_MONTHS = {
    "января": 1,
    "февраля": 2,
    "марта": 3,
    "апреля": 4,
    "мая": 5,
    "июня": 6,
    "июля": 7,
    "августа": 8,
    "сентября": 9,
    "октября": 10,
    "ноября": 11,
    "декабря": 12,
}

DISCLAIMER_RE = re.compile(
    r"(❗️|Этот видеоматериал представлен|This video is provided for informational)",
    re.I,
)
URL_RE = re.compile(r"https?://|www\.", re.I)
CTA_RE = re.compile(
    r"(whatsapp|telegram|t\.me|vk\.com|instagram|rutube|дзен|drberg|"
    r"скачать бесплатно|бесплатн\w+ (?:тест|чек-лист|материал)|"
    r"заказ(?:ать)? доставку|книги и меню|кто такой доктор|пройти тест|"
    r"курсы доктора|связаться|реклама на канале|подписывай|"
    r"этот ролик в оригинале|опубликован\s+\d)",
    re.I,
)
TIMESTAMP_RE = re.compile(r"^\s*\d{1,2}:\d{2}\b")
QTY_RE = re.compile(
    r"(?:\d+\s*/\s*\d+|\d+(?:[.,]\d+)?)(?:\s*[–—-]\s*(?:\d+\s*/\s*\d+|\d+(?:[.,]\d+)?))?\s*"
    r"(?:г|гр|грамм\w*|мл|кг|л\b|шт\.?|ч\.\s*л\.?|ст\.\s*л\.?|"
    r"чайн\w+\s+лож\w+|столов\w+\s+лож\w+|стакан\w*|щепотк\w*|"
    r"зубчик\w*|пучк\w*|головк\w*|капл\w*|"
    r"cups?|tbsp|tsp|grams?|ounces?)\b",
    re.I,
)
FOOD_NUM_RE = re.compile(
    r"\b\d+\s+(?:органическ\w+\s+|больш\w+\s+)?(?:яйц\w*|белк\w*|желтк\w*|зубчик\w*)\b",
    re.I,
)
COOK_RE = re.compile(
    r"\b(разогрейте|нагрейте|смешайте|добавьте|перемешайте|выпекайте|запекайте|"
    r"нарежьте|выложите|взбейте|обжарьте|жарьте|варите|тушите|измельчите|"
    r"посолите|застелите|охладите|остудите|сформируйте|смажьте|полейте|посыпьте|"
    r"поставьте|вымесите|разомните|процедите|взбейте|отделите|поместите|"
    r"preheat|bake|whisk|simmer)\b",
    re.I,
)
ACTION_RE = re.compile(
    r"\b(нужно|надо|следует|рекоменд\w+|принимайте|принять|пейте|ешьте|"
    r"избегайте|исключите|сократите|увеличьте|добавьте|уберите|"
    r"не ешьте|не пейте|не принимайте|замените|выберите|голодайте|"
    r"выходите|сократите|пейте|take|avoid|eat)\b",
    re.I,
)
DAY_RE = re.compile(r"^\s*день\s+\d+\b", re.I)
TIME_RE = re.compile(
    r"\b(утром|вечером|перед сном|натощак|в день|в течение дня|раз в день|"
    r"каждый день|на ночь)\b",
    re.I,
)
META_RE = re.compile(
    r"(вы узнаете|в этом видео|поговорим|разбираемся|доктор берг объясн|"
    r"давайте разбер|сегодня обсуд|из этого видео|в сегодняшнем ролике)",
    re.I,
)

# Longer patterns first where a form should win over a generic name.
SUPPLEMENT_RES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"глицинат\w*\s+магн|магн\w*\s+глицинат", re.I), "магний глицинат"),
    (re.compile(r"цитрат\w*\s+магн|магн\w*\s+цитрат", re.I), "магний цитрат"),
    (re.compile(r"оксид\w*\s+магн|магн\w*\s+оксид", re.I), "магний оксид"),
    (re.compile(r"треонат\w*\s+магн|магн\w*\s+треонат", re.I), "магний треонат"),
    (re.compile(r"\bмагни", re.I), "магний"),
    (re.compile(r"витамин\w*\s*д3|витамин\w*\s*d3|d3\s*\+\s*k2|д3\s*\+\s*к2", re.I), "витамин D3"),
    (re.compile(r"витамин\w*\s*к2|витамин\w*\s*k2", re.I), "витамин K2"),
    (re.compile(r"витамин\w*\s*д\b|витамин\w*\s*d\b", re.I), "витамин D"),
    (re.compile(r"витамин\w*\s*b1|витамин\w*\s*в1|тиамин", re.I), "витамин B1"),
    (re.compile(r"витамин\w*\s*b12|витамин\w*\s*в12", re.I), "витамин B12"),
    (re.compile(r"витамин\w*\s*с\b|витамин\w*\s*c\b", re.I), "витамин C"),
    (re.compile(r"фолат|фолиев", re.I), "фолаты"),
    (re.compile(r"омега-?\s*3|рыбий жир|рыбьего жира|масл\w+\s+из\s+печени\s+трески", re.I), "омега-3"),
    (re.compile(r"\bцинк", re.I), "цинк"),
    (re.compile(r"\bкалий\b|\bкалия\b", re.I), "калий"),
    (re.compile(r"электролит", re.I), "электролиты"),
    (re.compile(r"\bйод\b|\bйода\b", re.I), "йод"),
    (re.compile(r"селен", re.I), "селен"),
    (re.compile(r"берберин", re.I), "берберин"),
    (re.compile(r"пробиотик", re.I), "пробиотик"),
    (re.compile(r"коллаген", re.I), "коллаген"),
    (re.compile(r"креатин", re.I), "креатин"),
    (re.compile(r"мелатонин", re.I), "мелатонин"),
    (re.compile(r"ашваганд", re.I), "ашваганда"),
    (re.compile(r"куркумин", re.I), "куркумин"),
    (re.compile(r"псиллиум|подорожник\w*\s+блош", re.I), "псиллиум"),
    (re.compile(r"\bжелеза\b|препараты железа", re.I), "железо"),
    (re.compile(r"\bкальци", re.I), "кальций"),
    (re.compile(r"глицин\b", re.I), "глицин"),
    (re.compile(r"инозитол", re.I), "инозитол"),
    (re.compile(r"коэнзим|q10", re.I), "коэнзим Q10"),
]

FOOD_RES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"морск\w+\s+сол", re.I), "морская соль"),
    (re.compile(r"\bмст\b|\bmct\b", re.I), "масло MCT"),
    (re.compile(r"сливочн\w+\s+масл", re.I), "сливочное масло"),
    (re.compile(r"оливков\w+\s+масл", re.I), "оливковое масло"),
    (re.compile(r"кокосов\w+\s+масл", re.I), "кокосовое масло"),
    (re.compile(r"яблочн\w+\s+уксус", re.I), "яблочный уксус"),
    (re.compile(r"бланшированн\w+\s+миндал|мук\w+\s+из\s+миндал|миндальн\w+\s+мук", re.I), "миндальная мука"),
    (re.compile(r"миндальн\w+\s+паст", re.I), "миндальная паста"),
    (re.compile(r"\bминдал", re.I), "миндаль"),
    (re.compile(r"кокосов\w+\s+мук", re.I), "кокосовая мука"),
    (re.compile(r"семен\w+\s+тыкв|тыквенн\w+\s+семеч|семечек тыквы", re.I), "тыквенные семечки"),
    (re.compile(r"шпинат", re.I), "шпинат"),
    (re.compile(r"проростк\w+\s+брокколи|брокколи", re.I), "брокколи"),
    (re.compile(r"капустн\w+\s+сок", re.I), "капустный сок"),
    (re.compile(r"квашен\w+\s+капуст", re.I), "квашеная капуста"),
    (re.compile(r"цветн\w+\s+капуст", re.I), "цветная капуста"),
    (re.compile(r"\bкапуст", re.I), "капуста"),
    (re.compile(r"авокадо", re.I), "авокадо"),
    (re.compile(r"оливк", re.I), "оливки"),
    (re.compile(r"яйц", re.I), "яйца"),
    (re.compile(r"лосос", re.I), "лосось"),
    (re.compile(r"сардин", re.I), "сардины"),
    (re.compile(r"скумбр", re.I), "скумбрия"),
    (re.compile(r"говядин|говяж", re.I), "говядина"),
    (re.compile(r"\bкур(иц|ин)", re.I), "курица"),
    (re.compile(r"свинин", re.I), "свинина"),
    (re.compile(r"индейк", re.I), "индейка"),
    (re.compile(r"бекон", re.I), "бекон"),
    (re.compile(r"костн\w+\s+бульон", re.I), "костный бульон"),
    (re.compile(r"\bсыр\b|\bсыра\b|моцарелл|пармезан", re.I), "сыр"),
    (re.compile(r"сливк", re.I), "сливки"),
    (re.compile(r"кефир", re.I), "кефир"),
    (re.compile(r"йогурт", re.I), "йогурт"),
    (re.compile(r"эритрит|эритритол", re.I), "эритритол"),
    (re.compile(r"архат|монк", re.I), "подсластитель из архата"),
    (re.compile(r"стеви", re.I), "стевия"),
    (re.compile(r"\bкакао\b", re.I), "какао"),
    (re.compile(r"шоколад", re.I), "шоколад"),
    (re.compile(r"кориц", re.I), "корица"),
    (re.compile(r"имбир", re.I), "имбирь"),
    (re.compile(r"куркум", re.I), "куркума"),
    (re.compile(r"чеснок", re.I), "чеснок"),
    (re.compile(r"\bлук\b|\bлука\b", re.I), "лук"),
    (re.compile(r"лимон", re.I), "лимон"),
    (re.compile(r"ягод", re.I), "ягоды"),
    (re.compile(r"черник", re.I), "черника"),
    (re.compile(r"клубник", re.I), "клубника"),
    (re.compile(r"малины|малина", re.I), "малина"),
    (re.compile(r"орех|пекан", re.I), "орехи"),
    (re.compile(r"семен\w+\s+чиа|\bчиа\b", re.I), "семена чиа"),
    (re.compile(r"льнян", re.I), "льняное семя"),
    (re.compile(r"\bгриб(ы|ов|ам|ами|ах|а|е|ной|ных|ное)?\b|шампиньон", re.I), "грибы"),
    (re.compile(r"авокадо", re.I), "авокадо"),
    (re.compile(r"огурец|огурц", re.I), "огурцы"),
    (re.compile(r"помидор|томат", re.I), "помидоры"),
    (re.compile(r"салат", re.I), "салат"),
    (re.compile(r"руколл|руккол", re.I), "руккола"),
    (re.compile(r"сельдере", re.I), "сельдерей"),
    (re.compile(r"кабачок|цукини", re.I), "кабачок"),
    (re.compile(r"баклажан", re.I), "баклажан"),
    (re.compile(r"перец", re.I), "перец"),
    (re.compile(r"морков", re.I), "морковь"),
    (re.compile(r"свекл", re.I), "свекла"),
    (re.compile(r"тыкв", re.I), "тыква"),
    (re.compile(r"зелень|петрушк|укроп|кинз", re.I), "зелень"),
    (re.compile(r"костн\w+\s+бульон|бульон", re.I), "бульон"),
    (re.compile(r"желатин", re.I), "желатин"),
    (re.compile(r"кофе", re.I), "кофе"),
    (re.compile(r"\bчай\b", re.I), "чай"),
    (re.compile(r"углевод", re.I), "углеводы"),
    (re.compile(r"\bсоль\b|\bсоли\b", re.I), "соль"),
    (re.compile(r"пекарск\w+\s+порош|разрыхлител", re.I), "пекарский порошок"),
    (re.compile(r"ваниль|ванил", re.I), "ваниль"),
    (re.compile(r"глютен|без глютена", re.I), "без глютена"),
]

BODY_RES: list[tuple[str, re.Pattern[str]]] = [
    ("teeth", re.compile(r"\bзуб(ы|ов|ам|ами|ах|а)?\b|кариес|\bteeth\b|\btooth\b", re.I)),
    ("gums", re.compile(r"десн|десен|пародонт|\bgums?\b", re.I)),
    ("joints", re.compile(r"сустав|колен|артрит|артроз|\bknee\b|\bjoints?\b", re.I)),
    ("bones", re.compile(r"\bкост(ь|и|ей|ям)\b|остеопор|\bbones?\b", re.I)),
    ("muscles", re.compile(r"мышц|\bmuscles?\b", re.I)),
    ("spine", re.compile(r"позвоноч|шейных позвонк|\bspine\b", re.I)),
    ("liver", re.compile(r"\bпечени\b|\bпечень\b|печеночн|гепатоз|fatty liver|\bliver\b", re.I)),
    ("gallbladder", re.compile(r"желчн|желчного|gallbladder", re.I)),
    ("gut", re.compile(r"кишеч|микробиом|микробн|вздут|запор|\bsibo\b|сибр|пищевар|пищеварен|\bgut\b", re.I)),
    ("stomach", re.compile(r"желудк|гастрит|изжог|рефлюкс|\bstomach\b", re.I)),
    ("pancreas", re.compile(r"поджелудоч|\bpancreas\b", re.I)),
    ("skin", re.compile(r"\bкожа\b|\bкожи\b|\bкоже\b|кожн|акне|прыщ|псориаз|экзем|\bskin\b", re.I)),
    ("hair", re.compile(r"волос|\bhair\b", re.I)),
    ("nails", re.compile(r"ногт|\bnails?\b|грибок ногт", re.I)),
    ("thyroid", re.compile(r"щитовид|\bthyroid\b", re.I)),
    ("adrenals", re.compile(r"надпочеч|\badrenal", re.I)),
    ("hormones", re.compile(r"гормон|эстроген|тестостерон|инсулин|\bhormones?\b", re.I)),
    ("heart", re.compile(r"сердц|аритм|\bheart\b", re.I)),
    ("vessels", re.compile(r"сосуд|давлен|гипертон|варикоз|\bblood pressure\b", re.I)),
    ("blood", re.compile(r"\bкровь\b|\bкрови\b|холестерин|анеми|сахар\w*\s+в\s+крови|\bblood\b", re.I)),
    ("kidneys", re.compile(r"почк|почк|\bkidneys?\b", re.I)),
    ("bladder", re.compile(r"моче(вой|испуск)|мочевой пузыр|цистит|\bbladder\b", re.I)),
    ("prostate", re.compile(r"простат", re.I)),
    ("reproductive", re.compile(r"беременност|яичник|менопауз|спкя|\bpcos\b|фертиль", re.I)),
    ("eyes", re.compile(r"\bглаз|\bглаза\b|зрени|\beyes?\b", re.I)),
    ("ears", re.compile(r"\bухо\b|\bуши\b|\bуха\b|ушн|тиннит|\bears?\b|\bear\b", re.I)),
    ("brain", re.compile(r"\bмозг|когнитив|деменц|памят|\bbrain\b", re.I)),
    ("nerves", re.compile(r"нервн|невропат|\bnerves?\b", re.I)),
    ("lungs", re.compile(r"\bлегки[ехм]\b|бронх|кашел|пневмон|\blungs?\b", re.I)),
    ("immune", re.compile(r"иммун|\bimmune\b", re.I)),
]

# id, Ukrainian name, regex, implied body part
CONDITIONS: list[tuple[str, str, re.Pattern[str], str | None]] = [
    ("fatty-liver", "Жирова хвороба печінки", re.compile(r"жиров\w+\s+(гепатоз|печен)|жир\w*\s+в\s+печен|стеатоз|fatty liver|\bnafld\b", re.I), "liver"),
    ("visceral-fat", "Вісцеральний жир", re.compile(r"висцеральн\w+\s+жир|жир\w*\s+вокруг\s+сердца|жир\w*\s+на\s+живот", re.I), "heart"),
    ("overweight", "Зайва вага", re.compile(r"лишн\w+\s+вес|ожирен|похуде|\bobesity\b|\boverweight\b", re.I), "general"),
    ("insulin-resistance", "Інсулінорезистентність", re.compile(r"инсулинорезист", re.I), "hormones"),
    ("high-insulin", "Високий інсулін", re.compile(r"избыт\w+\s+инсулин|высок\w+\s+инсулин|инсулин\w*\s+натощак", re.I), "hormones"),
    ("diabetes", "Цукровий діабет", re.compile(r"диабет|сахарн\w+\s+диабет|\bdiabetes\b", re.I), "pancreas"),
    ("high-blood-sugar", "Високий цукор у крові", re.compile(r"сахар\w*\s+в\s+крови|уровен\w+\s+сахара|гликеми", re.I), "blood"),
    ("high-blood-pressure", "Високий тиск", re.compile(r"гипертон|высок\w+\s+давлен|кровян\w+\s+давлен|\bhypertension\b", re.I), "vessels"),
    ("high-cholesterol", "Високий холестерин", re.compile(r"холестерин", re.I), "blood"),
    ("arrhythmia", "Аритмія", re.compile(r"аритм|мерцательн", re.I), "heart"),
    ("gerd", "Печія і рефлюкс", re.compile(r"изжог|рефлюкс|\bgerd\b|heartburn|acid reflux", re.I), "stomach"),
    ("gastritis", "Гастрит", re.compile(r"гастрит", re.I), "stomach"),
    ("constipation", "Запор", re.compile(r"\bзапор", re.I), "gut"),
    ("bloating", "Здуття", re.compile(r"вздут|метеоризм|\bbloating\b", re.I), "gut"),
    ("ibs", "Синдром подразненого кишечника", re.compile(r"синдром\w*\s+раздраженн\w+\s+кишеч|\bibs\b", re.I), "gut"),
    ("sibo", "СІБР", re.compile(r"\bсибр\b|\bsibo\b", re.I), "gut"),
    ("candida", "Кандида", re.compile(r"кандид", re.I), "gut"),
    ("leaky-gut", "Підвищена проникність кишечника", re.compile(r"дыряв\w+\s+кишеч|leaky gut", re.I), "gut"),
    ("gallstones", "Жовчнокам'яна хвороба", re.compile(r"камн\w+\s+в\s+желч|желчнокамен", re.I), "gallbladder"),
    ("kidney-stones", "Камені в нирках", re.compile(r"камн\w+\s+в\s+почк|почечнокамен|kidney stones", re.I), "kidneys"),
    ("gout", "Подагра", re.compile(r"подагр|\bgout\b", re.I), "joints"),
    ("arthritis", "Артрит", re.compile(r"артрит|\barthritis\b", re.I), "joints"),
    ("osteoarthritis", "Артроз", re.compile(r"артроз|остеоартр", re.I), "joints"),
    ("osteoporosis", "Остеопороз", re.compile(r"остеопор", re.I), "bones"),
    ("hypothyroid", "Гіпотиреоз", re.compile(r"гипотиреоз", re.I), "thyroid"),
    ("hyperthyroid", "Гіпертиреоз", re.compile(r"гипертиреоз", re.I), "thyroid"),
    ("hashimoto", "Тиреоїдит Хашимото", re.compile(r"хашимото", re.I), "thyroid"),
    ("acne", "Акне", re.compile(r"\bакне\b|прыщ", re.I), "skin"),
    ("psoriasis", "Псоріаз", re.compile(r"псориаз", re.I), "skin"),
    ("eczema", "Екзема", re.compile(r"экзем", re.I), "skin"),
    ("hair-loss", "Випадіння волосся", re.compile(r"выпаден\w+\s+волос|облысен", re.I), "hair"),
    ("nail-fungus", "Грибок нігтів", re.compile(r"грибок\w*\s+ногт|онихомикоз", re.I), "nails"),
    ("insomnia", "Безсоння", re.compile(r"бессонниц|плох\w+\s+сон|\binsomnia\b", re.I), "brain"),
    ("anxiety", "Тривога", re.compile(r"тревог|\banxiety\b", re.I), "brain"),
    ("depression", "Депресія", re.compile(r"депресс", re.I), "brain"),
    ("migraine", "Мігрень", re.compile(r"мигрен", re.I), "brain"),
    ("headache", "Головний біль", re.compile(r"головн\w+\s+бол", re.I), "brain"),
    ("dementia", "Деменція", re.compile(r"деменц|альцгеймер", re.I), "brain"),
    ("anemia", "Анемія", re.compile(r"анеми", re.I), "blood"),
    ("magnesium-deficiency", "Дефіцит магнію", re.compile(r"дефицит\w*\s+магн|нехватк\w+\s+магн", re.I), "general"),
    ("vitamin-d-deficiency", "Дефіцит вітаміну D", re.compile(r"дефицит\w*\s+витамина\s*д|нехватк\w+\s+витамина\s*д", re.I), "general"),
    ("menopause", "Менопауза", re.compile(r"менопауз", re.I), "reproductive"),
    ("pcos", "СПКЯ", re.compile(r"спкя|\bpcos\b|поликистоз", re.I), "reproductive"),
    ("pregnancy", "Вагітність", re.compile(r"беременност", re.I), "reproductive"),
    ("prostatitis", "Простатит", re.compile(r"простатит", re.I), "prostate"),
    ("uti", "Цистит", re.compile(r"цистит", re.I), "bladder"),
    ("asthma", "Астма", re.compile(r"астм", re.I), "lungs"),
    ("cold", "Застуда", re.compile(r"простуд|\bорви\b", re.I), "immune"),
    ("inflammation", "Запалення", re.compile(r"воспален", re.I), "immune"),
    ("cramps", "Судоми", re.compile(r"судорог", re.I), "muscles"),
    ("edema", "Набряки", re.compile(r"\bотеки\b|\bотеков\b", re.I), "vessels"),
    ("varicose", "Варикоз", re.compile(r"варикоз", re.I), "vessels"),
    ("hemorrhoids", "Геморой", re.compile(r"геморр", re.I), "gut"),
    ("pancreatitis", "Панкреатит", re.compile(r"панкреатит", re.I), "pancreas"),
    ("adrenal-fatigue", "Виснаження наднирників", re.compile(r"усталост\w+\s+надпочеч|надпочечник\w+\s+истощ", re.I), "adrenals"),
    ("keto-flu", "Кетогрип", re.compile(r"кето-?грип|keto flu", re.I), "general"),
    ("fasting", "Голодування", re.compile(r"голодан", re.I), "general"),
]

CONDITION_PART = {cid: part for cid, _name, _rx, part in CONDITIONS}
CONDITION_NAME = {cid: name for cid, name, _rx, _part in CONDITIONS}

GENERIC_SUPPS = {"магний", "витамин D"}
SPECIFIC_OF = {
    "магний": {"магний глицинат", "магний цитрат", "магний оксид", "магний треонат"},
    "витамин D": {"витамин D3"},
}


def clean_description(text: str) -> str:
    text = text.replace("\u202f", " ").replace("\xa0", " ")
    text = DISCLAIMER_RE.split(text)[0]
    kept: list[str] = []
    for line in text.splitlines():
        raw = line.strip()
        if not raw or set(raw) <= set("_-—–• \t"):
            continue
        if URL_RE.search(raw) or CTA_RE.search(raw) or TIMESTAMP_RE.match(raw):
            continue
        if "💊" in raw or "👉" in raw or "➡" in raw:
            continue
        kept.append(raw)
    return "\n".join(kept)


def published_from_text(text: str, fallback: str | None) -> str | None:
    if fallback:
        return fallback
    m = re.search(
        r"Опубликован[ао]?\s+(\d{1,2})\s+([а-яё]+)\s+(\d{4})",
        text,
        re.I,
    )
    if not m:
        return None
    month = GEN_MONTHS.get(m.group(2).lower())
    if not month:
        return None
    return f"{int(m.group(3)):04d}-{month:02d}-{int(m.group(1)):02d}"


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    out: list[str] = []
    for part in parts:
        cleaned = part.strip(" \t-–—•")
        if len(cleaned) >= 25:
            out.append(cleaned)
    return out


def is_question(text: str) -> bool:
    return text.rstrip().endswith("?")


def ingredient_bits(text: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for bit in re.split(r"[\n;]+", text):
        item = bit.strip(" \t-–—•.")
        if not item or len(item) > 160 or is_question(item):
            continue
        if not (QTY_RE.search(item) or FOOD_NUM_RE.search(item)):
            continue
        if COOK_RE.search(item) and len(item) > 90:
            continue
        if re.search(r"градус", item, re.I) and not re.search(r"стакан|лож|мук|соль|яйц|г\b|мл", item, re.I):
            continue
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        found.append(item)
    return found


def find_names(text: str, table: list[tuple[re.Pattern[str], str]]) -> list[str]:
    found: list[str] = []
    for pattern, name in table:
        if pattern.search(text) and name not in found:
            found.append(name)
    return found


def supplements_in(text: str) -> list[str]:
    found = find_names(text, SUPPLEMENT_RES)
    drop: set[str] = set()
    for generic, specifics in SPECIFIC_OF.items():
        if generic in found and specifics & set(found):
            drop.add(generic)
    return [name for name in found if name not in drop]


def foods_in(text: str) -> list[str]:
    return find_names(text, FOOD_RES)


def dedupe(items: list[str]) -> list[str]:
    out: list[str] = []
    for item in items:
        if item not in out:
            out.append(item)
    return out


def body_parts_for(title: str, text: str) -> list[str]:
    title_hits = [bid for bid, rx in BODY_RES if rx.search(title)]
    counts: list[tuple[int, str]] = []
    for bid, rx in BODY_RES:
        n = len(rx.findall(text))
        if n:
            counts.append((n, bid))
    counts.sort(key=lambda pair: (-pair[0], BODY_IDS.index(pair[1])))
    text_hits = [bid for _n, bid in counts[:3]]
    ordered = []
    for bid in title_hits + text_hits:
        if bid not in ordered and bid != "general":
            ordered.append(bid)
    return ordered


# Mentioned in passing in almost every video; only the title earns a section.
TITLE_ONLY_CONDITIONS = {"inflammation", "overweight", "fasting"}


def conditions_for(title: str, text: str) -> list[str]:
    hits: list[str] = []
    title_hits: list[str] = []
    for cid, _name, rx, _part in CONDITIONS:
        in_title = rx.search(title) is not None
        in_text = rx.search(text) is not None
        if cid in TITLE_ONLY_CONDITIONS:
            if in_title:
                title_hits.append(cid)
            continue
        if in_title:
            title_hits.append(cid)
        elif in_text:
            hits.append(cid)
    return dedupe(title_hits + hits)[:4]


def actionable(text: str) -> list[str]:
    return [
        s
        for s in sentences(text)
        if not is_question(s) and not META_RE.search(s) and ACTION_RE.search(s)
    ]


def analyze(video: dict) -> dict:
    """Return a decision for one raw video record."""
    description = video.get("description") or ""
    cleaned = clean_description(description)
    title = video.get("title") or ""
    base = {
        "id": video["id"],
        "title": title,
        "publishedAt": published_from_text(description, video.get("publishedAt")),
        "url": video.get("url") or f"https://www.youtube.com/watch?v={video['id']}",
        "cleaned": cleaned,
    }
    if len(cleaned) < 80:
        return {**base, "keep": False, "reason": "too-little-text"}

    prose = re.sub(r"\b([Дд]ень)\s+(\d+)\s*\.", r"\1 \2:", cleaned)
    bits = ingredient_bits(cleaned)
    cook_steps = [
        s
        for s in sentences(prose)
        if not is_question(s) and not META_RE.search(s) and COOK_RE.search(s)
    ]
    day_steps = [s for s in sentences(prose) if DAY_RE.match(s) and not META_RE.search(s)]
    timed = [
        s
        for s in sentences(prose)
        if not is_question(s)
        and not META_RE.search(s)
        and (TIME_RE.search(s) or QTY_RE.search(s))
        and ACTION_RE.search(s)
    ]
    actions = actionable(prose)
    supps = supplements_in(cleaned)
    named_foods = foods_in(cleaned)
    # "без глютена" is not a food to list on its own
    named_foods = [f for f in named_foods if f != "без глютена"]

    recipe = len(bits) >= 2 and len(cook_steps) >= 1
    form_guidance = [
        s
        for s in actions
        if supplements_in(s)
        and (TIME_RE.search(s) or re.search(r"не принимайте|никогда не", s, re.I))
    ]
    protocol = (
        len(day_steps) >= 2
        or (len(timed) >= 2 and (supps or named_foods or bits))
        or len(form_guidance) >= 2
    )
    concrete_actions = []
    for sentence in actions:
        if foods_in(sentence) or supplements_in(sentence) or QTY_RE.search(sentence):
            concrete_actions.append(sentence)
    recommendation = len(concrete_actions) >= 1 and (named_foods or supps or bits)

    if recipe:
        kind = "recipe"
        foods = bits[:16]
        steps = cook_steps[:12]
        supps = []
        reason = "recipe-with-amounts-and-method"
    elif protocol:
        kind = "protocol"
        foods = dedupe(bits[:8] + named_foods)[:12]
        steps = dedupe(day_steps + timed)[:12]
        reason = "protocol-with-schedule-or-doses"
    elif recommendation:
        kind = "recommendation"
        foods = named_foods[:12]
        steps = concrete_actions[:8]
        reason = "concrete-food-or-supplement-advice"
    else:
        return {**base, "keep": False, "reason": "no-recipe-protocol-or-recommendation"}

    if "морская соль" in foods and "соль" in foods:
        foods = [food for food in foods if food != "соль"]
    if not foods and not supps and len(steps) < 2:
        return {**base, "keep": False, "reason": "nothing-concrete-extracted"}

    parts = body_parts_for(title, cleaned)
    conds = conditions_for(title, cleaned)
    for cid in conds:
        implied = CONDITION_PART.get(cid)
        if implied and implied != "general" and implied not in parts:
            parts.append(implied)
    if not parts:
        parts = ["general"]

    return {
        **base,
        "keep": True,
        "reason": reason,
        "kind": kind,
        "foods": foods,
        "supplements": supps[:8],
        "steps": steps,
        "conditions": conds,
        "bodyParts": parts[:5],
    }


def norm_title(title: str) -> str:
    text = title.lower().replace("ё", "е")
    text = re.sub(r"\(русская озвучка\)", " ", text)
    text = re.sub(r"[^a-zа-я0-9]+", " ", text)
    return " ".join(text.split())
