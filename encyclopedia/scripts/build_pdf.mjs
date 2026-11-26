import { readFileSync, writeFileSync, mkdtempSync, existsSync, statSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const cards = JSON.parse(readFileSync(join(root, "src/data/cards.json"), "utf8"));
const parts = JSON.parse(readFileSync(join(root, "src/data/bodyParts.json"), "utf8"));
const conditions = JSON.parse(readFileSync(join(root, "src/data/conditions.json"), "utf8"));
const conditionName = new Map(conditions.map((item) => [item.id, item.nameRu]));
const conditionParts = new Map(
  conditions.map((item) => [item.id, new Set(item.bodyParts || [])]),
);
const kindLabel = {
  recipe: "Рецепт",
  protocol: "Протокол",
  recommendation: "Рекомендация",
};
const disclaimer =
  "Это образовательная подборка публичных описаний видео, а не медицинский совет. Доктор Берг — хиропрактик, не врач. Решения о здоровье принимайте вместе с врачом.";

function esc(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function descriptionHtml(text) {
  return String(text || "")
    .replaceAll("\r\n", "\n")
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => `<p>${esc(line)}</p>`)
    .join("");
}

function cardHtml(card) {
  const foods = card.foods.map((item) => `<li>${esc(item)}</li>`).join("");
  const supplements = card.supplements.map((item) => `<li>${esc(item)}</li>`).join("");
  const steps = card.steps.map((item) => `<li>${esc(item)}</li>`).join("");
  const states = card.conditions.map((id) => conditionName.get(id) ?? id).join(", ");
  return `<article class="card">
    <p class="kind">${kindLabel[card.kind]}</p>
    <p class="card-title">${esc(card.titleRu)}</p>
    <div class="description">${descriptionHtml(card.description)}</div>
    ${foods ? `<p class="label">Продукты</p><ul>${foods}</ul>` : ""}
    ${supplements ? `<p class="label">Добавки</p><ul>${supplements}</ul>` : ""}
    ${steps ? `<p class="label">${card.kind === "recipe" ? "Шаги" : "Режим"}</p><ol>${steps}</ol>` : ""}
    ${states ? `<p>Состояния: ${esc(states)}</p>` : ""}
    ${card.titleEn ? `<p>English: ${esc(card.titleEn)}</p>` : ""}
    ${card.publishedAt ? `<p>${esc(card.publishedAt)}</p>` : ""}
    <p><a href="${esc(card.url)}">Смотреть видео на YouTube</a></p>
  </article>`;
}

const chapters = [];
const toc = [];
for (const part of parts) {
  const inPart = cards.filter((card) => card.bodyParts.includes(part.id));
  if (inPart.length === 0) continue;
  const groups = new Map();
  const loose = [];
  for (const card of inPart) {
    const related = card.conditions.filter((id) => conditionParts.get(id)?.has(part.id));
    if (related.length === 0) loose.push(card);
    for (const conditionId of related) {
      if (!groups.has(conditionId)) groups.set(conditionId, []);
      groups.get(conditionId).push(card);
    }
  }
  const ordered = [...groups.entries()].sort((a, b) =>
    (conditionName.get(a[0]) ?? a[0]).localeCompare(conditionName.get(b[0]) ?? b[0], "ru"),
  );
  const partId = `part-${part.id}`;
  const conditionItems = ordered
    .map(([id]) => {
      const anchor = `${partId}--${id}`;
      return `<li><a href="#${anchor}">${esc(conditionName.get(id) ?? id)}</a></li>`;
    })
    .join("");
  toc.push(
    `<li class="toc-part"><a href="#${partId}">${esc(part.nameRu)}</a><ul>${conditionItems}</ul></li>`,
  );
  const blocks = ordered
    .map(
      ([id, group]) =>
        `<h2 id="${partId}--${id}">${esc(conditionName.get(id) ?? id)}</h2>${group.map(cardHtml).join("")}`,
    )
    .join("");
  const rest = loose.map(cardHtml).join("");
  chapters.push(
    `<section><h1 class="part" id="${partId}">${esc(part.nameRu)}</h1>${blocks}${rest}</section>`,
  );
}

const html = `<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <title>Энциклопедия рецептов доктора Берга</title>
  <style>
    body { font-family: "Liberation Serif", "Noto Serif", "DejaVu Serif", Georgia, serif; color: #1c1915; margin: 0; }
    main { padding: 24px 36px 48px; }
    h1.part { break-before: page; font-size: 22pt; }
    h2 { font-size: 15pt; margin-top: 1.2em; }
    .card { margin: 0.8em 0 1.2em; padding-bottom: 0.6em; border-bottom: 1px solid #ddd; }
    .card-title { font-size: 13pt; font-weight: 700; margin: 0.15em 0 0.4em; }
    .label { font-weight: 700; margin: 0.7em 0 0.2em; }
    .description p { margin: 0.3em 0; }
    .kind { letter-spacing: 0.06em; text-transform: uppercase; font-size: 9pt; color: #5e564c; }
    a { color: #1d4a38; }
    .note { background: #f6f0e4; padding: 12px 14px; }
    .toc { margin: 1em 0 2em; padding: 0; }
    .toc-part { break-inside: avoid; margin: 0.45em 0 0.7em; }
    .toc ul { margin: 0.15em 0 0.2em 1.2em; padding: 0; }
    .toc li { margin: 0.08em 0; }
  </style>
</head>
<body>
  <main>
    <h1>Энциклопедия рецептов доктора Берга</h1>
    <p class="note">${esc(disclaimer)}</p>
    <p>Карточки сгруппированы по части тела, затем по состоянию. Пункты оглавления открывают раздел внутри файла. Ссылка на видео открывает ролик на YouTube.</p>
    <h2>Оглавление</h2>
    <ul class="toc">
      ${toc.join("\n")}
    </ul>
    ${chapters.join("\n")}
  </main>
</body>
</html>`;

const dir = mkdtempSync(join(tmpdir(), "berg-pdf-"));
const htmlPath = join(dir, "guide.html");
const pdfPath = join(root, "public/berg-dovidnyk.pdf");
const profile = join(tmpdir(), "chrome-berg-pdf");
writeFileSync(htmlPath, html);
try {
  execFileSync(
    "timeout",
    [
      "240",
      "google-chrome",
      "--headless=new",
      "--disable-gpu",
      "--no-sandbox",
      `--user-data-dir=${profile}`,
      "--no-pdf-header-footer",
      `--print-to-pdf=${pdfPath}`,
      htmlPath,
    ],
    { stdio: "inherit" },
  );
} catch (error) {
  if (!existsSync(pdfPath) || statSync(pdfPath).size < 1000) throw error;
}
execFileSync("python3", [join(root, "scripts/add_pdf_outline.py"), pdfPath], {
  stdio: "inherit",
});
console.log(pdfPath);
