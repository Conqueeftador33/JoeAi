"use client";

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "../lib/api";
import { useJoeAIStore } from "../lib/store";

export default function OrdersPage() {
  const restaurantId = useJoeAIStore((s) => s.restaurantId);

  const [orders, setOrders] = useState<any[]>([]);
  const [menu, setMenu] = useState<any[]>([]);

  const [form, setForm] = useState({
    customer_id: "",
    item1: "",
    qty1: "1",
    item2: "",
    qty2: "1",
    item3: "",
    qty3: "1",
    channel: "dine_in"
  });

  async function load() {
    const o = await apiGet(`/orders?restaurant_id=${restaurantId}`);
    const m = await apiGet(`/menu?restaurant_id=${restaurantId}`);

    setOrders(o);
    setMenu(m);
  }

  useEffect(() => {
    load();
  }, [restaurantId]);

  async function save(e: any) {
    e.preventDefault();

    const map: any = {};
    menu.forEach((m) => map[m.name] = m);

    const items = [
      { name: form.item1, quantity: Number(form.qty1 || 1) },
      { name: form.item2, quantity: Number(form.qty2 || 1) },
      { name: form.item3, quantity: Number(form.qty3 || 1) }
    ]
    .filter((x) => x.name)
    .map((x) => ({
      name: x.name,
      quantity: x.quantity,
      unit_price: map[x.name]?.price || 0,
      unit_cost: map[x.name]?.cost || 0,
      category: map[x.name]?.category || "Other"
    }));

    await apiPost("/orders", {
      restaurant_id: restaurantId,
      customer_id: form.customer_id,
      channel: form.channel,
      items
    });

    await load();
  }

  return (
    <div>
      <h1>Orders & Receipts</h1>

      <div className="panel">
        <h2>New Receipt</h2>

        <form className="form" onSubmit={save}>
          <input
            placeholder="customer_id"
            value={form.customer_id}
            onChange={(e) => setForm({ ...form, customer_id: e.target.value })}
          />

          {[1,2,3].map((n) => (
            <div key={n} className="search">
              <select
                value={(form as any)[`item${n}`]}
                onChange={(e) => setForm({ ...form, [`item${n}`]: e.target.value })}
              >
                <option value="">item {n}</option>

                {menu.map((m) => (
                  <option key={m.id} value={m.name}>
                    {m.name}
                  </option>
                ))}
              </select>

              <input
                value={(form as any)[`qty${n}`]}
                onChange={(e) => setForm({ ...form, [`qty${n}`]: e.target.value })}
                placeholder="qty"
              />
            </div>
          ))}

          <select value={form.channel} onChange={(e) => setForm({ ...form, channel: e.target.value })}>
            {["dine_in","takeaway","delivery","glovo","just_eat","pos"].map((x) => (
              <option key={x}>{x}</option>
            ))}
          </select>

          <button>Save receipt</button>
        </form>
      </div>

      <div className="panel">
        <h2>Receipts</h2>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>id</th>
                <th>customer</th>
                <th>items</th>
                <th>channel</th>
                <th>amount</th>
                <th>date</th>
              </tr>
            </thead>

            <tbody>
              {orders.map((o) => (
                <tr key={o.id}>
                  <td>{o.id}</td>
                  <td>{o.customer_id}</td>
                  <td>{o.items_summary}</td>
                  <td>{o.channel}</td>
                  <td>€{o.amount}</td>
                  <td>{o.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
