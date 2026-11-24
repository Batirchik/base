import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div>
      <h1>Сторінку не знайдено</h1>
      <p>
        <Link to="/">Повернутися на головну</Link>
      </p>
    </div>
  );
}
