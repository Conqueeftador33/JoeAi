"use client";

import { useState } from "react";
import { apiPost } from "../lib/api";
import { useJoeAIStore } from "../lib/store";

export default function CampaignsPage() {
  const restaurantId = useJoeAIStore((s) => s.restaurantId);

  const [campaign, setCampaign] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function generate(segment: string) {
    setLoading(true);

    const res = await apiPost("/campaigns/ai-generate", {
      restaurant_id: restaurantId,
      segment
    });

    setCampaign(res);
    setLoading(false);
  }

  return (
    <div>
      <h1>Campaigns</h1>

      <div className="buttons">
        <button onClick={() => generate("inactive")}>Inactive</button>
        <button onClick={() => generate("cold")}>Cold</button>
        <button onClick={() => generate("vip")}>VIP</button>
        <button onClick={() => generate("returning")}>Returning</button>
      </div>

      {loading && <div className="panel">Generating campaign...</div>}

      {campaign?.strategy?.ai_plan && (
        <div className="panel">
          <h2>AI Campaign Strategy</h2>
          <pre>{campaign.strategy.ai_plan}</pre>
        </div>
      )}

      {campaign?.messages?.length > 0 && (
        <div className="panel">
          <h2>Generated Messages</h2>

          {campaign.messages.map((m: any) => (
            <div key={m.customer_id} className="panel">
              <b>{m.name}</b>
              <p>{m.message}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
