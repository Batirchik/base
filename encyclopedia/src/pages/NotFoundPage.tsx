import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div>
      <h1>Страница не найдена</h1>
      <p>
        <Link to="/">Вернуться на главную</Link>
      </p>
    </div>
  );
}
