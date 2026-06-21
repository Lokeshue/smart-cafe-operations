"use client";

import { useEffect, useState } from "react";

export default function Home() {
  const [drinks, setDrinks] = useState([]);

  useEffect(() => {
    fetch("https://smart-cafe-operations.onrender.com/api/drinks")
      .then((res) => res.json())
      .then((data) => setDrinks(data))
      .catch((err) => console.log(err));
  }, []);

  return (
    <main style={{ padding: 40 }}>
      <h1>Smart Cafe Operations</h1>

      <h2>Base Drink</h2>

      <select style={{ padding: 10, width: 300 }}>
        {drinks.map((drink: any) => (
          <option key={drink.id} value={drink.id}>
            {drink.name}
          </option>
        ))}
      </select>
    </main>
  );
}
