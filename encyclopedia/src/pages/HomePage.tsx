import { Link } from "react-router-dom";
import {
  bodyParts,
  cards,
  conditions,
  countForCondition,
  countForPart,
  kindCounts,
} from "../lib/model";
import { KIND_LABEL } from "../types";

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
        <p className="eyebrow">Довідник за описами відео</p>
        <h1>Енциклопедія рецептів доктора Берга</h1>
        <p className="lede">
          {cards.length} карток українською: страви, режими прийому і конкретні
          рекомендації. Пояснювальні ролики без таких пунктів сюди не входять.
        </p>
        <ul className="stats">
          <li>
            <b>{counts.recipe}</b> {KIND_LABEL.recipe.toLowerCase()}ів
          </li>
          <li>
            <b>{counts.protocol}</b> протоколів
          </li>
          <li>
            <b>{counts.recommendation}</b> рекомендацій
          </li>
        </ul>
      </section>
      <section className="doors">
        <article>
          <h2>За частиною тіла</h2>
          <ul>
            {parts.slice(0, 8).map(({ part, count }) => (
              <li key={part.id}>
                <Link to={`/body/${part.id}`}>
                  {part.nameUk}
                  <span>{count}</span>
                </Link>
              </li>
            ))}
          </ul>
          <Link className="more" to="/body">
            Усі частини тіла
          </Link>
        </article>
        <article>
          <h2>За станом</h2>
          <ul>
            {states.map(({ item, count }) => (
              <li key={item.id}>
                <Link to={`/condition/${item.id}`}>
                  {item.nameUk}
                  <span>{count}</span>
                </Link>
              </li>
            ))}
          </ul>
          <Link className="more" to="/conditions">
            Усі стани
          </Link>
        </article>
      </section>
    </div>
  );
}
