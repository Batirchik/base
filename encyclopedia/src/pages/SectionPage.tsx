import { useParams, useSearchParams } from "react-router-dom";
import { CardList } from "../components/CardList";
import { CardView } from "../components/CardView";
import { Disclaimer } from "../components/Disclaimer";
import { kindFromParam, KindFilter } from "../components/KindFilter";
import {
  cardsForCondition,
  cardsForPart,
  getCondition,
  getPart,
  type KindFilter as KindValue,
} from "../lib/model";
import { NotFoundPage } from "./NotFoundPage";

export function SectionPage({ mode }: { mode: "body" | "condition" }) {
  const params = useParams();
  const [query, setQuery] = useSearchParams();
  const kind = kindFromParam(query.get("kind"));
  const key = mode === "body" ? params.partId : params.conditionId;
  const title =
    mode === "body" ? getPart(key ?? "")?.nameUk : getCondition(key ?? "")?.nameUk;
  if (!key || !title) return <NotFoundPage />;

  const found =
    mode === "body" ? cardsForPart(key, kind) : cardsForCondition(key, kind);

  function setKind(next: KindValue) {
    const nextQuery = new URLSearchParams(query);
    if (next === "all") nextQuery.delete("kind");
    else nextQuery.set("kind", next);
    setQuery(nextQuery, { replace: true });
  }

  return (
    <div>
      <p className="eyebrow print-only">Енциклопедія Берга</p>
      <h1>{title}</h1>
      <p className="lede no-print">
        {found.length} карток. Друк розділу зберігає посилання на відео.
      </p>
      <div className="toolbar no-print">
        <KindFilter value={kind} onChange={setKind} />
        <button type="button" onClick={() => window.print()}>
          Зберегти розділ як PDF
        </button>
      </div>
      <div className="print-only">
        <Disclaimer />
      </div>
      <CardList cards={found} />
      <div className="print-only">
        {found.map((card) => (
          <CardView key={card.id} card={card} />
        ))}
      </div>
    </div>
  );
}
