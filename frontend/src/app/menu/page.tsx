"use client";

import { useEffect, useMemo, useState } from "react";
import { apiGet, apiPost } from "../lib/api";
import { useJoeAIStore } from "../lib/store";

export default function MenuPage() {
  const restaurantId = useJoeAIStore((s) => s.restaurantId);

  const [rows, setRows] = useState<any[]>([]);
  const [q, setQ] = useState("");
  const [cat, setCat] = useState("name");

  const [form, setForm] = useState({
    name: "",
    category: "",
    price: "",
    cost: ""
  });

  async function load() {
    const d = await apiGet(`/menu?restaurant_id=${restaurantId}`);
    setRows(d);
  }

  useEffect(() => {
    load();
  }, [restaurantId]);

  async function save(e: any) {
    e.preventDefault();

    await apiPost("/menu", {
      restaurant_id: restaurantId,
      ...form
    });

    setForm({
      name: "",
      category: "",
      price: "",
      cost: ""
    });

    await load();
  }

  const filtered = useMemo(() => {
    return rows.filter((m) => {
      const v =
        cat === "id" ? String(m.id)
        : cat === "category" ? m.category
        : cat === "price" ? String(m.price)
        : m.name;

      return String(v || "").toLowerCase().includes(q.toLowerCase());
    });
  }, [rows, q, cat]);

  return (
    <div>
      <h1>Menu</h1>

      <div className="grid">
        <div className="panel">
          <h2>Add Item</h2>

          <form className="form" onSubmit={save}>
            {["name","category","price","cost"].map((k) => (
              <input
                key={k}
                placeholder={k}
                value={(form as any)[k]}
                onChange={(e) => setForm({ ...form, [k]: e.target.value })}
              />
            ))}

            <button>Save item</button>
          </form>
        </div>

        <div className="panel">
          <h2>Search</h2>

          <div className="search">
            <select value={cat} onChange={(e) => setCat(e.target.value)}>
              <option value="name">name</option>
              <option value="id">id</option>
              <option value="category">category</option>
              <option value="price">price</option>
            </select>

            <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="search..." />
          </div>
        </div>
      </div>

      <div className="panel">
        <h2>Menu Items</h2>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>id</th>
                <th>name</th>
                <th>category</th>
                <th>price</th>
                <th>cost</th>
              </tr>
            </thead>

            <tbody>
              {filtered.map((m) => (
                <tr key={m.id}>
                  <td>{m.id}</td>
                  <td>{m.name}</td>
                  <td>{m.category}</td>
                  <td>€{m.price}</td>
                  <td>€{m.cost}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
