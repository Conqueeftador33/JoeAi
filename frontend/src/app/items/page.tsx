"use client";

import { useEffect, useState } from "react";
import { apiGet } from "../lib/api";
import { useJoeAIStore } from "../lib/store";

export default function ItemsPage() {
  const restaurantId = useJoeAIStore((s) => s.restaurantId);

  const [rows, setRows] = useState<any[]>([]);

  useEffect(() => {
    apiGet(`/analytics/items?restaurant_id=${restaurantId}`).then(setRows);
  }, [restaurantId]);

  return (
    <div>
      <h1>Item Analytics</h1>

      <div className="panel">
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>item</th>
                <th>quantity</th>
                <th>revenue</th>
                <th>margin</th>
              </tr>
            </thead>

            <tbody>
              {rows.map((r) => (
                <tr key={r.name}>
                  <td>{r.name}</td>
                  <td>{r.quantity}</td>
                  <td>€{r.revenue}</td>
                  <td>€{r.margin}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
