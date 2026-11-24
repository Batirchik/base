import { useSearchParams } from "react-router-dom";
import { CardList } from "../components/CardList";
import { kindFromParam, KindFilter } from "../components/KindFilter";
import { ruPlural, searchCards, type KindFilter as KindValue } from "../lib/model";

export function SearchPage() {
  const [params, setParams] = useSearchParams();
  const q = params.get("q") ?? "";
  const kind = kindFromParam(params.get("kind"));
  const found = searchCards(q, kind);

  function setKind(next: KindValue) {
    const query = new URLSearchParams(params);
    if (next === "all") query.delete("kind");
    else query.set("kind", next);
    setParams(query, { replace: true });
  }

  return (
    <div>
      <h1>Поиск</h1>
      <p className="lede">
        {q
          ? `Запрос «${q}»: ${found.length} ${ruPlural(found.length, "карточка", "карточки", "карточек")}.`
          : "Введите название, продукт, добавку или состояние."}
      </p>
      <KindFilter value={kind} onChange={setKind} />
      <CardList cards={found} />
    </div>
  );
}
