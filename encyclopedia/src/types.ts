export type Kind = "recipe" | "protocol" | "recommendation";

export interface BodyPart {
  id: string;
  nameUk: string;
}

export interface Condition {
  id: string;
  nameUk: string;
}

export interface Card {
  id: string;
  titleUk: string;
  summaryUk: string;
  kind: Kind;
  foods: string[];
  supplements: string[];
  steps: string[];
  conditions: string[];
  bodyParts: string[];
  titleEn: string;
  publishedAt: string;
  url: string;
}

export const KIND_LABEL: Record<Kind, string> = {
  recipe: "Рецепт",
  protocol: "Протокол",
  recommendation: "Рекомендація",
};

export const DISCLAIMER =
  "Це освітня компіляція публічних описів відео, а не медична порада. Доктор Берг — хіропрактик, не лікар. Рішення щодо здоров’я ухвалюйте разом із лікарем.";
