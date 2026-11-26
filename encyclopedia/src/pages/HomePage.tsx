import { Link } from "react-router-dom";
import {
  bodyParts,
  cards,
  conditions,
  countForCondition,
  countForPart,
  kindCounts,
  ruPlural,
} from "../lib/model";

export function HomePage() {
  const counts = kindCounts();
  const parts = bodyParts
    .map((part) => ({ part, count: countForPart(part.id) }))
    .filter((row) => row.count > 0)
    .sort((a, b) => b.count - a.count);
  const states = conditions
    .map((item) => ({ item, count: countForCondition(item.id) }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 12);

  return (
    <div className="home">
      <section className="hero">
        <p className="eyebrow">Справочник по описаниям видео</p>
        <h1>Энциклопедия рецептов доктора Берга</h1>
        <p className="lede">
          {cards.length}{" "}
          {ruPlural(cards.length, "карточка", "карточки", "карточек")} на русском:
          блюда, режимы приёма и конкретные рекомендации. Поясняющие ролики без
          таких пунктов сюда не входят.
        </p>
        <ul className="stats">
          <li>
            <b>{counts.recipe}</b>{" "}
            {ruPlural(counts.recipe, "рецепт", "рецепта", "рецептов")}
          </li>
          <li>
            <b>{counts.protocol}</b>{" "}
            {ruPlural(counts.protocol, "протокол", "протокола", "протоколов")}
          </li>
          <li>
            <b>{counts.recommendation}</b>{" "}
            {ruPlural(counts.recommendation, "рекомендация", "рекомендации", "рекомендаций")}
          </li>
        </ul>
      </section>
      <section className="doors">
        <article>
          <h2>По части тела</h2>
          <ul>
            {parts.slice(0, 8).map(({ part, count }) => (
              <li key={part.id}>
                <Link to={`/body/${part.id}`}>
                  {part.nameRu}
                  <span>{count}</span>
                </Link>
              </li>
            ))}
          </ul>
          <Link className="more" to="/body">
            Все части тела
          </Link>
        </article>
        <article>
          <h2>По состоянию</h2>
          <ul>
            {states.map(({ item, count }) => (
              <li key={item.id}>
                <Link to={`/condition/${item.id}`}>
                  {item.nameRu}
                  <span>{count}</span>
                </Link>
              </li>
            ))}
          </ul>
          <Link className="more" to="/conditions">
            Все состояния
          </Link>
        </article>
      </section>
    </div>
  );
}
