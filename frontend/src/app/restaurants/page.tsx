"use client";

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "../lib/api";
import { useJoeAIStore } from "../lib/store";

export default function RestaurantsPage() {
  const restaurantId = useJoeAIStore((s) => s.restaurantId);
  const setRestaurantId = useJoeAIStore((s) => s.setRestaurantId);

  const [rows, setRows] = useState<any[]>([]);

  const [form, setForm] = useState({
    name: "",
    city: "",
    cuisine: "",
    address: "",
    phone: "",
    email: "",
    website: ""
  });

  async function load() {
    const d = await apiGet("/restaurants");
    setRows(d);
  }

  useEffect(() => {
    load();
  }, []);

  async function save(e: any) {
    e.preventDefault();

    await apiPost("/restaurants", form);

    setForm({
      name: "",
      city: "",
      cuisine: "",
      address: "",
      phone: "",
      email: "",
      website: ""
    });

    await load();
  }

  return (
    <div>
      <h1>Restaurants</h1>

      <div className="panel">
        <h2>Add Restaurant</h2>

        <form className="form" onSubmit={save}>
          {["name","city","cuisine","address","phone","email","website"].map((k) => (
            <input
              key={k}
              placeholder={k}
              value={(form as any)[k]}
              onChange={(e) => setForm({ ...form, [k]: e.target.value })}
            />
          ))}

          <button>Save restaurant</button>
        </form>
      </div>

      <div className="panel">
        <h2>Restaurant List</h2>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>id</th>
                <th>name</th>
                <th>cuisine</th>
                <th>address</th>
                <th>select</th>
              </tr>
            </thead>

            <tbody>
              {rows.map((r) => (
                <tr key={r.id}>
                  <td>{r.id}</td>
                  <td>{r.name}</td>
                  <td>{r.cuisine}</td>
                  <td>{r.address}</td>

                  <td>
                    <button onClick={() => setRestaurantId(r.id)}>
                      {restaurantId === r.id ? "Selected" : "Select"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
