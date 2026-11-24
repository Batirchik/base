import { NavLink, Outlet } from "react-router-dom";
import { Disclaimer } from "./Disclaimer";
import { SearchBox } from "./SearchBox";

export function Layout() {
  return (
    <div className="shell">
      <header className="top no-print">
        <div className="brand">
          <NavLink to="/" className="mark">
            Енциклопедія Берга
          </NavLink>
          <p>Рецепти, протоколи й рекомендації з описів відео</p>
        </div>
        <nav>
          <NavLink to="/body">Частини тіла</NavLink>
          <NavLink to="/conditions">Стани</NavLink>
          <a href="/berg-dovidnyk.pdf">Повний PDF</a>
        </nav>
        <SearchBox />
      </header>
      <main>
        <Outlet />
      </main>
      <footer className="foot">
        <Disclaimer />
        <p className="source">
          Джерело: публічні описи каналу{" "}
          <a href="https://www.youtube.com/@DrEricBerg">Dr. Eric Berg</a>.
          Сирі описи не публікуються як сторінки.
        </p>
      </footer>
    </div>
  );
}
