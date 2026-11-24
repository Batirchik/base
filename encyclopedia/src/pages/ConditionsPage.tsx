import { Link } from "react-router-dom";
import { conditions, countForCondition } from "../lib/model";

export function ConditionsPage() {
  const rows = [...conditions].sort((a, b) => a.nameUk.localeCompare(b.nameUk, "uk"));
  return (
    <div>
      <h1>Стани</h1>
      <p className="lede">
        Один стан — один розділ. Синоніми з описів зведені разом, тож «жирова
        печінка» не розпадається на кілька сторінок.
      </p>
      <ul className="index-list">
        {rows.map((item) => (
          <li key={item.id}>
            <Link to={`/condition/${item.id}`}>
              {item.nameUk}
              <span>{countForCondition(item.id)}</span>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
