import { Link } from "react-router-dom";
import { formatDate, partName, conditionName } from "../lib/model";
import { KIND_LABEL, type Card } from "../types";

export function CardView({ card, linked }: { card: Card; linked?: boolean }) {
  const title = linked ? (
    <Link to={`/card/${card.id}`}>{card.titleUk}</Link>
  ) : (
    card.titleUk
  );
  return (
    <article className="card" id={`card-${card.id}`} data-kind={card.kind}>
      <p className="kind">{KIND_LABEL[card.kind]}</p>
      <h2>{title}</h2>
      <p className="summary">{card.summaryUk}</p>
      {card.foods.length > 0 && (
        <section>
          <h3>Продукти</h3>
          <ul className="chips">
            {card.foods.map((food) => (
              <li key={food}>{food}</li>
            ))}
          </ul>
        </section>
      )}
      {card.supplements.length > 0 && (
        <section>
          <h3>Добавки</h3>
          <ul className="chips">
            {card.supplements.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </section>
      )}
      {card.steps.length > 0 && (
        <section>
          <h3>{card.kind === "recipe" ? "Кроки" : "Режим"}</h3>
          <ol>
            {card.steps.map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ol>
        </section>
      )}
      <div className="meta">
        {card.bodyParts.length > 0 && (
          <p>
            Частини тіла:{" "}
            {card.bodyParts.map((id, index) => (
              <span key={id}>
                {index > 0 && ", "}
                <Link to={`/body/${id}`}>{partName(id)}</Link>
              </span>
            ))}
          </p>
        )}
        {card.conditions.length > 0 && (
          <p>
            Стани:{" "}
            {card.conditions.map((id, index) => (
              <span key={id}>
                {index > 0 && ", "}
                <Link to={`/condition/${id}`}>{conditionName(id)}</Link>
              </span>
            ))}
          </p>
        )}
        <p>Англійська назва: {card.titleEn}</p>
        {card.publishedAt && <p>Дата: {formatDate(card.publishedAt)}</p>}
        <p>
          <a href={card.url}>Дивитися відео на YouTube</a>
        </p>
      </div>
    </article>
  );
}
