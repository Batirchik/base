export type Kind = "recipe" | "protocol" | "recommendation";

export interface BodyPart {
  id: string;
  nameRu: string;
}

export interface Condition {
  id: string;
  nameRu: string;
}

export interface Card {
  id: string;
  titleRu: string;
  summaryRu: string;
  description: string;
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
  recommendation: "Рекомендация",
};

export const DISCLAIMER =
  "Это образовательная подборка публичных описаний видео, а не медицинский совет. Доктор Берг — хиропрактик, не врач. Решения о здоровье принимайте вместе с врачом.";
