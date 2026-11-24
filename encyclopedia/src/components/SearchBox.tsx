import { FormEvent, useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

export function SearchBox() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const [value, setValue] = useState(params.get("q") ?? "");

  useEffect(() => {
    setValue(params.get("q") ?? "");
  }, [params]);

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    const q = value.trim();
    navigate(q ? `/search?q=${encodeURIComponent(q)}` : "/search");
  }

  return (
    <form className="search no-print" onSubmit={onSubmit} role="search">
      <label htmlFor="site-search">Пошук</label>
      <input
        id="site-search"
        value={value}
        onChange={(event) => setValue(event.target.value)}
        placeholder="Назва, продукт, добавка або стан"
      />
      <button type="submit">Знайти</button>
    </form>
  );
}
