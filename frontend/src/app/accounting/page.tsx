"use client";

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "../lib/api";
import { useJoeAIStore } from "../lib/store";

function Row({ a, b }: any) {
  return <div className="row"><span>{a}</span><b>{b}</b></div>;
}

export default function AccountingPage() {
  const restaurantId = useJoeAIStore((s) => s.restaurantId);

  const [data, setData] = useState<any>(null);
  const [ai, setAi] = useState("");

  useEffect(() => {
    apiGet(`/dashboard?restaurant_id=${restaurantId}`).then(setData);
  }, [restaurantId]);

  async function analyze() {
    const r = await apiPost("/ai/accounting", {
      restaurant_id: restaurantId
    });

    setAi(r.answer);
  }

  if (!data) return <div>Loading...</div>;

  return (
    <div>
      <h1>Accounting</h1>

      <div className="grid">
        <div className="panel">
          <h2>Metrics</h2>

          <Row a="Revenue" b={`€${data.kpis.total_revenue}`} />
          <Row a="Cost" b={`€${data.kpis.total_cost_estimate}`} />
          <Row a="Margin" b={`€${data.kpis.gross_margin_estimate}`} />
          <Row a="AOV" b={`€${data.kpis.avg_order}`} />
          <Row a="Churn Risk" b={`${data.kpis.churn_risk_rate}%`} />

          <button onClick={analyze}>
            AI accounting analysis
          </button>
        </div>

        <div className="panel">
          <h2>AI Analysis</h2>

          <pre>{ai}</pre>
        </div>
      </div>
    </div>
  );
}
