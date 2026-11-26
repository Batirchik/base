import { Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { BodyPartsPage } from "./pages/BodyPartsPage";
import { CardPage } from "./pages/CardPage";
import { ConditionsPage } from "./pages/ConditionsPage";
import { HomePage } from "./pages/HomePage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { SearchPage } from "./pages/SearchPage";
import { SectionPage } from "./pages/SectionPage";

export function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="body" element={<BodyPartsPage />} />
        <Route path="body/:partId" element={<SectionPage mode="body" />} />
        <Route path="conditions" element={<ConditionsPage />} />
        <Route
          path="condition/:conditionId"
          element={<SectionPage mode="condition" />}
        />
        <Route path="card/:cardId" element={<CardPage />} />
        <Route path="search" element={<SearchPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
