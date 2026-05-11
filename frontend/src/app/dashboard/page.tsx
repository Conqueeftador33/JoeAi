"use client";

import { useEffect, useState } from "react";
import { apiGet } from "../lib/api";
import { useJoeAIStore } from "../lib/store";

function Card({ t, v }: any) {
  return <div className="card"><span>{t}</span><b>{v}</b></div>;
}

function Row({ a, b }: any) {
  return <div className="row"><span>{a}</span><b>{b}</b></div>;
}

export default function DashboardPage() {
  const [data, setData] = useState<any>(null);
  const restaurantId = useJoeAIStore((s) => s.restaurantId);

  useEffect(() => {
    apiGet(`/dashboard?restaurant_id=${restaurantId}`).then(setData);
  }, [restaurantId]);

  if (!data) return <div>Loading...</div>;

  return (
    <div>
      <h1>Dashboard</h1>

      <div className="kpis">
        <Card t="Customers" v={data.kpis.customers} />
        <Card t="Revenue" v={`€${data.kpis.total_revenue}`} />
        <Card t="Churn Risk" v={`${data.kpis.churn_risk_rate}%`} />
        <Card t="AOV" v={`€${data.kpis.avg_order}`} />
        <Card t="Margin" v={`€${data.kpis.gross_margin_estimate}`} />
        <Card t="LTV" v={`€${data.kpis.ltv_estimate}`} />
      </div>

      <div className="panel">
        <h2>{data.restaurant.name}</h2>
        <Row a="Cuisine" b={data.restaurant.cuisine} />
        <Row a="Address" b={data.restaurant.address} />
        <Row a="Phone" b={data.restaurant.phone} />
      </div>
    </div>
  );
}
