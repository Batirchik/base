import type { KindFilter } from "../lib/model";
import { KIND_LABEL, type Kind } from "../types";

const OPTIONS: Array<{ id: KindFilter; label: string }> = [
  { id: "all", label: "Все" },
  { id: "recipe", label: KIND_LABEL.recipe },
  { id: "protocol", label: KIND_LABEL.protocol },
  { id: "recommendation", label: KIND_LABEL.recommendation },
];

export function KindFilter({
  value,
  onChange,
}: {
  value: KindFilter;
  onChange: (kind: KindFilter) => void;
}) {
  return (
    <div className="kinds no-print" role="group" aria-label="Тип карточки">
      {OPTIONS.map((option) => (
        <button
          key={option.id}
          type="button"
          className={value === option.id ? "on" : ""}
          aria-pressed={value === option.id}
          onClick={() => onChange(option.id)}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}

export function kindFromParam(value: string | null): KindFilter {
  if (value === "recipe" || value === "protocol" || value === "recommendation") {
    return value satisfies Kind;
  }
  return "all";
}
