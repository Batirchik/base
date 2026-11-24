import { Link } from "react-router-dom";
import { KIND_LABEL, type Card } from "../types";

export function CardList({ cards }: { cards: Card[] }) {
  if (cards.length === 0) {
    return <p className="empty">У цьому доборі немає карток.</p>;
  }
  return (
    <ul className="list screen-only">
      {cards.map((card) => (
        <li key={card.id}>
          <Link to={`/card/${card.id}`} data-kind={card.kind}>
            <span className="kind">{KIND_LABEL[card.kind]}</span>
            <strong>{card.titleUk}</strong>
            <em>{card.summaryUk}</em>
          </Link>
        </li>
      ))}
    </ul>
  );
}
