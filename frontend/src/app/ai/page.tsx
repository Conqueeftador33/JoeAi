"use client";

import { useState } from "react";
import { apiPost } from "../lib/api";
import { useJoeAIStore } from "../lib/store";

export default function AIPage() {
  const restaurantId = useJoeAIStore((s) => s.restaurantId);

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  async function ask() {
    setLoading(true);

    const res = await apiPost("/ai/ask", {
      restaurant_id: restaurantId,
      area: "marketing",
      question
    });

    setAnswer(res.answer);
    setLoading(false);
  }

  return (
    <div>
      <h1>JoeAI Marketing Brain</h1>

      <div className="search">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask about churn, campaigns, customers, menu, ROI..."
        />

        <button onClick={ask}>
          {loading ? "Thinking..." : "Ask"}
        </button>
      </div>

      <pre>{answer}</pre>
    </div>
  );
}
