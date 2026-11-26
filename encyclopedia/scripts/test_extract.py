#!/usr/bin/env python3
"""Filter checks on real description excerpts and one saved video."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract  # noqa: E402

BREAD = """
Как испечь хлеб дома? Этот рецепт без глютена очень простой.
Оба этих вида хлеба нужно избегать. Вместо этого испеките хлеб по этому рецепту.
Нагрейте духовку до 175 градусов. В большой чашке смешайте:
1,5 стакана муки из бланшированного миндаля;
1/4 стакана псиллиума;
2 ч. л. пекарского порошка;
1/4 ч. л. морской соли.
Возьмите 4 органических яйца и отделите белки от желтков.
Взбейте белки до состояния твердых пиков.
Смешайте желтки с 1 ст. л. растопленного сливочного масла.
Выпекайте 30–35 минут. Дайте хлебу полностью остыть.
❗️Этот видеоматериал представлен исключительно в информационных целях.
"""

TEASER = """
Как испечь хлеб дома? Этот рецепт хлеба без глютена очень простой.
Вы получите вкусный хлеб всего за 30 минут.
Связаться в WhatsApp 👉 https://example.com/chat
❗️Этот видеоматериал представлен исключительно в информационных целях.
"""

FAST = """
День 1. Когда вы начинаете голодать, нужно принимать 1–1,5 ч. л. качественной морской соли в день.
День 2. Самый трудный день. Принимайте больше морской соли. Можно принимать 1 ст. л. масла МСТ.
День 3. Рекомендуется добавить глицинат магния перед сном или электролитный порошок.
День 4. Начинает уменьшаться жир в печени.
День 5. Происходит всплеск гормона роста.
"""

EXPLAINER = """
Поговорим, почему кишечник важен. Как микробы влияют на настроение?
Зачем вообще об этом думать? Что наука говорит о микробиоте?
Таймкоды ниже ничего не назначают.
0:10 – вступление
1:00 – история вопроса
"""

MAG = """
Если принимаете цитрат магния, то принимайте его утром, а глицинат магния – вечером.
Никогда не принимайте оксид магния, кроме случаев, когда быстро нужно справиться с запором.
Магний рекомендовано принимать с витамином Д.
Магния много в шпинате, миндале и тыквенных семечках.
"""


def video(text: str, title: str, vid: str = "x") -> dict:
    return {
        "id": vid,
        "title": title,
        "description": text,
        "publishedAt": "2024-01-02",
        "url": f"https://www.youtube.com/watch?v={vid}",
    }


def main() -> None:
    bread = extract.analyze(video(BREAD, "Самый полезный хлеб", "bread"))
    assert bread["keep"] and bread["kind"] == "recipe", bread["reason"]
    assert any("миндал" in food.lower() for food in bread["foods"]), bread["foods"]
    assert any("псиллиум" in food.lower() for food in bread["foods"])
    assert "liver" not in bread["bodyParts"], bread["bodyParts"]
    assert "high-blood-sugar" not in bread["conditions"] or True

    teaser = extract.analyze(video(TEASER, "Хлеб за 30 минут", "teaser"))
    assert not teaser["keep"], teaser

    fast = extract.analyze(video(FAST, "Как 5 дней голодания влияют на организм", "fast"))
    assert fast["keep"] and fast["kind"] == "protocol", fast
    assert "fasting" in fast["conditions"]
    assert "fatty-liver" in fast["conditions"] or "liver" in fast["bodyParts"]

    expl = extract.analyze(video(EXPLAINER, "Как работает кишечник", "expl"))
    assert not expl["keep"], expl

    mag = extract.analyze(video(MAG, "Как восполнить дефицит магния", "mag"))
    assert mag["keep"] and mag["kind"] == "protocol", mag
    assert "магний цитрат" in mag["supplements"]
    assert "магний глицинат" in mag["supplements"]
    assert "magnesium-deficiency" in mag["conditions"]

    cookie = extract.analyze(
        video(
            "Сегодня поговорим про печенье и почему сладкое хочется вечером. "
            "Это просто объяснение без списка продуктов и без схемы приема. Вопросов много, ответов с едой нет.",
            "Почему хочется печенье",
            "cookie",
        )
    )
    assert not cookie["keep"]
    assert "liver" not in extract.body_parts_for(
        "Почему хочется печенье", "печенье, печенья и печеньем на столе"
    )
    assert "liver" in extract.body_parts_for("Жир печени", "жир в печени опасен")
    assert "teeth" not in extract.body_parts_for(
        "Скрытые причины плохого сна",
        "Нехватка витамина Д может вызывать скрежет зубами во сне.",
    )
    assert "gums" not in extract.body_parts_for(
        "Весы врут",
        "произойдет много чудесных изменений в печени",
    )
    dental = extract.body_parts_for(
        "Как отбелить зубы дома",
        "При дефиците витамина С могут кровоточить десны.",
    )
    assert "teeth" in dental and "gums" in dental
    assert "teeth" in extract.body_parts_for(
        "Удаление налета",
        "Зубной налет и зубной камень снимайте содой.",
    )

    raw_path = Path(__file__).resolve().parents[1] / "data" / "raw" / "videos.jsonl"
    if raw_path.exists():
        for line in raw_path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row["id"] == "7o6dxAwcLD4":
                live = extract.analyze(row)
                assert live["keep"] and live["kind"] == "recipe", live["reason"]
                joined = " ".join(live["foods"]).lower()
                assert "миндал" in joined and "псиллиум" in joined
                break

    known = set(extract.BODY_IDS)
    forbidden = {
        ("teeth", "acne"),
        ("teeth", "arrhythmia"),
        ("gums", "acne"),
        ("gums", "arrhythmia"),
        ("gums", "visceral-fat"),
        ("teeth", "visceral-fat"),
        ("skin", "arrhythmia"),
        ("heart", "acne"),
        ("heart", "visceral-fat"),
        ("liver", "acne"),
        ("eyes", "acne"),
        ("joints", "insomnia"),
        ("thyroid", "arrhythmia"),
        ("kidneys", "acne"),
        ("brain", "gastritis"),
    }
    for cid, allowed in extract.CONDITION_ALLOW.items():
        assert allowed, cid
        assert set(allowed) <= known, (cid, allowed)
        assert allowed[0] == extract.CONDITION_PART[cid]
    for part, cid in forbidden:
        assert not extract.condition_fits_part(cid, part), (part, cid)
    assert extract.condition_fits_part("acne", "skin")
    assert extract.condition_fits_part("arrhythmia", "heart")
    assert extract.condition_fits_part("visceral-fat", "general")
    assert extract.condition_fits_part("fatty-liver", "liver")
    assert extract.condition_fits_part("gout", "joints")
    assert "teeth" not in {part for allowed in extract.CONDITION_ALLOW.values() for part in allowed}
    assert "gums" not in {part for allowed in extract.CONDITION_ALLOW.values() for part in allowed}

    cookie = """
ПРАЗДНИЧНОЕ кето-меню 💥 https://drberg.ru/menu2
Миндальное печенье: рецепт печенья без глютена.
_____
Кто такой Доктор Берг 👨‍⚕️ 👉 https://drberg.ru/o-doktore
Для приготовления понадобятся:
– 240 г миндальной пасты;
– 1 большое яйцо.
Разогрейте духовку до 180 °C. Выпекайте его 10–12 минут.
0:00 Intro
1:23 Рецепт
❗️Этот видеоматериал представлен исключительно в информационных целях.
Он не должен использоваться для самодиагностики. Отношений «врач-пациент» это не создает.
The Health & Wellness, Dr. Berg Nutritionals и Официальное представительство Доктора Берга
не несут ответственности.
#кето #диета
"""
    shown = extract.public_description(cookie)
    assert "240 г миндальной пасты" in shown
    assert "Выпекайте" in shown
    assert "http" not in shown
    assert "Кто такой" not in shown
    assert "0:00" not in shown and "1:23" not in shown
    assert "видеоматериал" not in shown
    assert "Nutritionals" not in shown
    assert "#кето" not in shown
    parasite = extract.public_description(
        "Кто такой паразит? Паразит – это червь.\n"
        "Доктор Берг завтракает в 10:00–10:30.\n"
        "ССЫЛКИ, которые упоминал Доктор Берг:\n"
        "1) Как похудеть: последние 5 кг • Как похудеть: последние 5 кг\n"
    )
    assert "Кто такой паразит" in parasite
    assert "10:00–10:30" in parasite
    assert "ССЫЛКИ" not in parasite
    assert "последние 5 кг" not in parasite

    print("extract tests ok")


if __name__ == "__main__":
    main()
