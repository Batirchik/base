import { Link } from "react-router-dom";
import { bodyParts, countForPart } from "../lib/model";

export function BodyPartsPage() {
  return (
    <div>
      <h1>Частини тіла</h1>
      <p className="lede">
        Словник частин тіла фіксований. Картка потрапляє в розділ, якщо опис
        відео стосується цієї частини.
      </p>
      <ul className="index-grid">
        {bodyParts.map((part) => {
          const count = countForPart(part.id);
          return (
            <li key={part.id}>
              <Link to={`/body/${part.id}`} aria-disabled={count === 0}>
                <strong>{part.nameUk}</strong>
                <span>{count === 0 ? "немає карток" : `${count}`}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
