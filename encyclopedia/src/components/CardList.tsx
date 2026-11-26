import { Link } from "react-router-dom";
import { KIND_LABEL, type Card } from "../types";

function excerpt(text: string): string {
  const flat = text.replace(/\s+/g, " ").trim();
  if (flat.length <= 240) return flat;
  return `${flat.slice(0, 240).trimEnd()}…`;
}

export function CardList({ cards }: { cards: Card[] }) {
  if (cards.length === 0) {
    return <p className="empty">В этой подборке нет карточек.</p>;
  }
  return (
    <ul className="list screen-only">
      {cards.map((card) => (
        <li key={card.id}>
          <Link to={`/card/${card.id}`} data-kind={card.kind}>
            <span className="kind">{KIND_LABEL[card.kind]}</span>
            <strong>{card.titleRu}</strong>
            <em>{excerpt(card.description)}</em>
          </Link>
        </li>
      ))}
    </ul>
  );
}
