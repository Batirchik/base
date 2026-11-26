import rawCards from "../data/cards.json";
import rawConditions from "../data/conditions.json";
import rawParts from "../data/bodyParts.json";
import type { BodyPart, Card, Condition, Kind } from "../types";

export const cards = rawCards as Card[];
export const conditions = rawConditions as Condition[];
export const bodyParts = rawParts as BodyPart[];

const conditionById = new Map(conditions.map((item) => [item.id, item]));
const partById = new Map(bodyParts.map((item) => [item.id, item]));
const cardById = new Map(cards.map((card) => [card.id, card]));

const MONTHS = [
  "января",
  "февраля",
  "марта",
  "апреля",
  "мая",
  "июня",
  "июля",
  "августа",
  "сентября",
  "октября",
  "ноября",
  "декабря",
];

export function fold(value: string): string {
  return value
    .toLowerCase()
    .replaceAll("’", "'")
    .replaceAll("ё", "е")
    .replaceAll("ы", "и")
    .replaceAll("э", "е")
    .replaceAll("ъ", "")
    .replaceAll("і", "и")
    .replaceAll("ї", "и")
    .replaceAll("є", "е")
    .replaceAll("ґ", "г");
}

function blob(card: Card): string {
  const conditionNames = card.conditions
    .map((id) => conditionById.get(id)?.nameRu ?? "")
    .join(" ");
  const partNames = card.bodyParts.map((id) => partById.get(id)?.nameRu ?? "").join(" ");
  return fold(
    [
      card.titleRu,
      card.titleEn,
      card.description,
      card.summaryRu,
      card.foods.join(" "),
      card.supplements.join(" "),
      conditionNames,
      partNames,
    ].join(" "),
  );
}

const searchBlobs = cards.map((card) => ({ card, text: blob(card) }));

export function getCard(id: string): Card | undefined {
  return cardById.get(id);
}

export function getPart(id: string): BodyPart | undefined {
  return partById.get(id);
}

export function getCondition(id: string): Condition | undefined {
  return conditionById.get(id);
}

export function conditionName(id: string): string {
  return conditionById.get(id)?.nameRu ?? id;
}

export function partName(id: string): string {
  return partById.get(id)?.nameRu ?? id;
}

export type KindFilter = Kind | "all";

function byKind(card: Card, kind: KindFilter): boolean {
  return kind === "all" || card.kind === kind;
}

export function cardsForPart(partId: string, kind: KindFilter): Card[] {
  return cards.filter((card) => card.bodyParts.includes(partId) && byKind(card, kind));
}

export function cardsForCondition(conditionId: string, kind: KindFilter): Card[] {
  return cards.filter(
    (card) => card.conditions.includes(conditionId) && byKind(card, kind),
  );
}

export function searchCards(query: string, kind: KindFilter): Card[] {
  const needle = fold(query.trim());
  if (!needle) {
    return cards.filter((card) => byKind(card, kind));
  }
  return searchBlobs
    .filter((row) => row.text.includes(needle) && byKind(row.card, kind))
    .map((row) => row.card);
}

export function countForPart(partId: string): number {
  return cards.filter((card) => card.bodyParts.includes(partId)).length;
}

export function countForCondition(conditionId: string): number {
  return cards.filter((card) => card.conditions.includes(conditionId)).length;
}

export function formatDate(iso: string): string {
  if (!iso) return "";
  const [year, month, day] = iso.split("-").map(Number);
  if (!year || !month || !day) return iso;
  return `${day} ${MONTHS[month - 1]} ${year}`;
}

export function kindCounts(): Record<Kind, number> {
  return {
    recipe: cards.filter((card) => card.kind === "recipe").length,
    protocol: cards.filter((card) => card.kind === "protocol").length,
    recommendation: cards.filter((card) => card.kind === "recommendation").length,
  };
}

export function ruPlural(count: number, one: string, few: string, many: string): string {
  const n10 = count % 10;
  const n100 = count % 100;
  if (n10 === 1 && n100 !== 11) return one;
  if (n10 >= 2 && n10 <= 4 && (n100 < 12 || n100 > 14)) return few;
  return many;
}
