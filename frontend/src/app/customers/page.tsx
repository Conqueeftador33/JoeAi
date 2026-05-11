"use client";

import { useEffect, useMemo, useState } from "react";
import { apiGet, apiPost } from "../lib/api";
import { useJoeAIStore } from "../lib/store";

export default function CustomersPage() {
  const restaurantId = useJoeAIStore((s) => s.restaurantId);

  const [rows, setRows] = useState<any[]>([]);
  const [q, setQ] = useState("");
  const [cat, setCat] = useState("all");
  const [sort, setSort] = useState("spent");

  const [form, setForm] = useState({
    name: "",
    phone: "",
    email: "",
    favorite_item: "",
    tags: "",
    notes: ""
  });

  async function load() {
    const d = await apiGet(`/customers?restaurant_id=${restaurantId}`);
    setRows(d);
  }

  useEffect(() => {
    load();
  }, [restaurantId]);

  async function add(e: any) {
    e.preventDefault();

    await apiPost("/customers", {
      restaurant_id: restaurantId,
      ...form
    });

    setForm({
      name: "",
      phone: "",
      email: "",
      favorite_item: "",
      tags: "",
      notes: ""
    });

    await load();
  }

  const filtered = useMemo(() => {
    let out = [...rows];

    if (q) {
      out = out.filter((c) => {
        const v =
          cat === "id" ? String(c.id)
          : cat === "name" ? c.name
          : cat === "phone" ? c.phone
          : cat === "email" ? c.email
          : cat === "favorite" ? c.favorite_item
          : cat === "tags" ? c.tags
          : `${c.id} ${c.name} ${c.phone} ${c.email} ${c.favorite_item} ${c.tags}`;

        return String(v || "").toLowerCase().includes(q.toLowerCase());
      });
    }

    if (sort === "orders") out.sort((a,b) => b.orders - a.orders);
    else if (sort === "name") out.sort((a,b) => a.name.localeCompare(b.name));
    else out.sort((a,b) => b.spent - a.spent);

    return out;
  }, [rows, q, cat, sort]);

  return (
    <div>
      <h1>Customers</h1>

      <div className="grid">
        <div className="panel">
          <h2>Add Customer</h2>

          <form className="form" onSubmit={add}>
            {["name","phone","email","favorite_item","tags","notes"].map((k) => (
              <input
                key={k}
                placeholder={k}
                value={(form as any)[k]}
                onChange={(e) => setForm({ ...form, [k]: e.target.value })}
                required={k === "name" || k === "phone"}
              />
            ))}

            <button>Save customer</button>
          </form>
        </div>

        <div className="panel">
          <h2>Search</h2>

          <div className="search">
            <select value={cat} onChange={(e) => setCat(e.target.value)}>
              <option value="all">all</option>
              <option value="name">name</option>
              <option value="id">id</option>
              <option value="phone">phone</option>
              <option value="email">email</option>
              <option value="favorite">favorite</option>
              <option value="tags">tags</option>
            </select>

            <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="search..." />
          </div>

          <select value={sort} onChange={(e) => setSort(e.target.value)}>
            <option value="spent">spent</option>
            <option value="orders">orders</option>
            <option value="name">name</option>
          </select>
        </div>
      </div>

      <div className="panel">
        <h2>Customer List</h2>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>id</th>
                <th>name</th>
                <th>phone</th>
                <th>spent</th>
                <th>orders</th>
                <th>favorite</th>
                <th>tags</th>
              </tr>
            </thead>

            <tbody>
              {filtered.map((c) => (
                <tr key={c.id}>
                  <td>{c.id}</td>
                  <td>{c.name}</td>
                  <td>{c.phone}</td>
                  <td>€{c.spent}</td>
                  <td>{c.orders}</td>
                  <td>{c.favorite_item}</td>
                  <td>{c.tags}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
