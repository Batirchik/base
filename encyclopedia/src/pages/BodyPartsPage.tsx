import { Link } from "react-router-dom";
import { bodyParts, countForPart } from "../lib/model";

export function BodyPartsPage() {
  return (
    <div>
      <h1>Части тела</h1>
      <p className="lede">
        Список частей тела фиксированный. Карточка попадает в раздел, если описание
        видео касается этой части.
      </p>
      <ul className="index-grid">
        {bodyParts.map((part) => {
          const count = countForPart(part.id);
          return (
            <li key={part.id}>
              <Link to={`/body/${part.id}`} aria-disabled={count === 0}>
                <strong>{part.nameRu}</strong>
                <span>{count === 0 ? "нет карточек" : `${count}`}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
