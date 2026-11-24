import { Link, useParams } from "react-router-dom";
import { CardView } from "../components/CardView";
import { getCard, partName } from "../lib/model";
import { NotFoundPage } from "./NotFoundPage";

export function CardPage() {
  const { cardId } = useParams();
  const card = cardId ? getCard(cardId) : undefined;
  if (!card) return <NotFoundPage />;
  return (
    <div>
      <p className="crumbs no-print">
        <Link to="/">Головна</Link>
        {card.bodyParts[0] && (
          <>
            {" / "}
            <Link to={`/body/${card.bodyParts[0]}`}>{partName(card.bodyParts[0])}</Link>
          </>
        )}
      </p>
      <CardView card={card} />
    </div>
  );
}
