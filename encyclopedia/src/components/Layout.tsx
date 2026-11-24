import { NavLink, Outlet } from "react-router-dom";
import { Disclaimer } from "./Disclaimer";
import { SearchBox } from "./SearchBox";

export function Layout() {
  return (
    <div className="shell">
      <header className="top no-print">
        <div className="brand">
          <NavLink to="/" className="mark">
            Энциклопедия Берга
          </NavLink>
          <p>Рецепты, протоколы и рекомендации из описаний видео</p>
        </div>
        <nav>
          <NavLink to="/body">Части тела</NavLink>
          <NavLink to="/conditions">Состояния</NavLink>
          <a href="/berg-dovidnyk.pdf">Полный PDF</a>
        </nav>
        <SearchBox />
      </header>
      <main>
        <Outlet />
      </main>
      <footer className="foot">
        <Disclaimer />
        <p className="source">
          Источник: публичные описания канала{" "}
          <a href="https://www.youtube.com/@DrEricBerg">Dr. Eric Berg</a>. Исходные
          описания не публикуются как страницы.
        </p>
      </footer>
    </div>
  );
}
