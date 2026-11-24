import { Link } from "react-router-dom";
import { conditions, countForCondition } from "../lib/model";

export function ConditionsPage() {
  const rows = [...conditions].sort((a, b) => a.nameRu.localeCompare(b.nameRu, "ru"));
  return (
    <div>
      <h1>Состояния</h1>
      <p className="lede">
        Одно состояние — один раздел. Синонимы из описаний сведены вместе, поэтому
        «жировая печень» не разбивается на несколько страниц.
      </p>
      <ul className="index-list">
        {rows.map((item) => (
          <li key={item.id}>
            <Link to={`/condition/${item.id}`}>
              {item.nameRu}
              <span>{countForCondition(item.id)}</span>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
