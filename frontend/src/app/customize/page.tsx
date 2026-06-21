"use client";

import { useCallback, useEffect, useState } from "react";
import NutritionCard from "@/components/NutritionCard";
import { api, type CustomizeParams, type Drink, type Nutrition } from "@/lib/api";

const MILK_TYPES = ["whole milk", "almond milk", "oat milk", "nonfat milk"] as const;
const SIZES = ["tall", "grande", "venti"] as const;
const CHANNELS = ["mobile", "drive-thru", "walk-in"] as const;

const defaultParams: CustomizeParams = {
  drink_id: 1,
  size: "grande",
  milk_type: "whole milk",
  vanilla_pumps: 0,
  caramel_pumps: 0,
  mocha_pumps: 0,
  whipped_cream: false,
  protein_boost: false,
  extra_espresso_shot: false,
};

export default function CustomizePage() {
  const [drinks, setDrinks] = useState<Drink[]>([]);
  const [params, setParams] = useState<CustomizeParams>(defaultParams);
  const [nutrition, setNutrition] = useState<Nutrition | null>(null);
  const [drinkName, setDrinkName] = useState("");
  const [customerName, setCustomerName] = useState("");
  const [channel, setChannel] = useState<string>("mobile");
  const [loading, setLoading] = useState(false);
  const [orderResult, setOrderResult] = useState<{ id: number; position?: number; wait: number } | null>(null);
  const [error, setError] = useState("");

  // Load drinks on mount
  useEffect(() => {
    api.getDrinks().then(setDrinks).catch(() => setError("Failed to load drinks. Is the backend running?"));
  }, []);

  // Live nutrition update on every customization change
  const updateNutrition = useCallback(async (p: CustomizeParams) => {
    try {
      const result = await api.customizeDrink(p);
      setNutrition(result.nutrition);
      setDrinkName(result.drink_name);
    } catch {
      /* ignore transient errors during typing */
    }
  }, []);

  useEffect(() => {
    if (params.drink_id) {
      updateNutrition(params);
    }
  }, [params, updateNutrition]);

  const handleChange = <K extends keyof CustomizeParams>(key: K, value: CustomizeParams[K]) => {
    setParams((prev) => ({ ...prev, [key]: value }));
    setOrderResult(null);
  };

  const handlePlaceOrder = async () => {
    if (!customerName.trim()) {
      setError("Please enter your name.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const order = await api.createOrder({ ...params, customer_name: customerName, channel });
      setOrderResult({
        id: order.id,
        position: order.queue_position,
        wait: order.estimated_wait_minutes,
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to place order.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="mb-2 text-3xl font-bold text-cafe-green-dark">Customize Your Drink</h1>
      <p className="mb-8 text-gray-600">Select a base drink and watch nutrition update in real time.</p>

      <div className="grid gap-8 lg:grid-cols-2">
        {/* Customization Form */}
        <div className="card space-y-5">
          <div>
            <label className="label">Base Drink</label>
            <select
              className="input-field"
              value={params.drink_id}
              onChange={(e) => handleChange("drink_id", Number(e.target.value))}
            >
              {drinks.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name} — {d.description.slice(0, 50)}…
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="label">Size</label>
            <div className="flex gap-2">
              {SIZES.map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => handleChange("size", s)}
                  className={`flex-1 rounded-lg border py-2 capitalize transition ${
                    params.size === s
                      ? "border-cafe-green bg-cafe-green text-white"
                      : "border-gray-300 hover:border-cafe-green"
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="label">Milk Type</label>
            <select
              className="input-field capitalize"
              value={params.milk_type}
              onChange={(e) => handleChange("milk_type", e.target.value)}
            >
              {MILK_TYPES.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-3 gap-4">
            {(["vanilla_pumps", "caramel_pumps", "mocha_pumps"] as const).map((key) => (
              <div key={key}>
                <label className="label capitalize">{key.replace("_pumps", "")} Pumps</label>
                <input
                  type="number"
                  min={0}
                  max={12}
                  className="input-field"
                  value={params[key]}
                  onChange={(e) => handleChange(key, Number(e.target.value))}
                />
              </div>
            ))}
          </div>

          <div className="space-y-2">
            <label className="label">Add-ons</label>
            {(
              [
                ["whipped_cream", "Whipped Cream"],
                ["protein_boost", "Protein Boost"],
                ["extra_espresso_shot", "Extra Espresso Shot"],
              ] as const
            ).map(([key, label]) => (
              <label key={key} className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={params[key]}
                  onChange={(e) => handleChange(key, e.target.checked)}
                  className="h-4 w-4 accent-cafe-green"
                />
                <span className="text-sm">{label}</span>
              </label>
            ))}
          </div>

          <hr />

          <div>
            <label className="label">Your Name</label>
            <input
              className="input-field"
              placeholder="Enter your name"
              value={customerName}
              onChange={(e) => setCustomerName(e.target.value)}
            />
          </div>

          <div>
            <label className="label">Order Channel</label>
            <div className="flex gap-2">
              {CHANNELS.map((c) => (
                <button
                  key={c}
                  type="button"
                  onClick={() => setChannel(c)}
                  className={`flex-1 rounded-lg border py-2 text-sm capitalize transition ${
                    channel === c
                      ? "border-cafe-green bg-cafe-green text-white"
                      : "border-gray-300 hover:border-cafe-green"
                  }`}
                >
                  {c}
                </button>
              ))}
            </div>
          </div>

          {error && <p className="text-sm text-red-600">{error}</p>}

          <button className="btn-primary w-full" onClick={handlePlaceOrder} disabled={loading}>
            {loading ? "Placing Order…" : "Place Order"}
          </button>
        </div>

        {/* Nutrition + Order Confirmation */}
        <div className="space-y-6">
          {nutrition && (
            <NutritionCard
              calories={nutrition.calories}
              sugar={nutrition.sugar}
              protein={nutrition.protein}
              caffeine={nutrition.caffeine}
              summary={nutrition.summary}
            />
          )}

          {drinkName && (
            <div className="card">
              <h3 className="mb-2 font-semibold text-cafe-green-dark">Your Drink</h3>
              <p className="text-lg">
                {drinkName} ({params.size})
              </p>
              <p className="mt-1 text-sm capitalize text-gray-500">
                {params.milk_type}
                {params.vanilla_pumps > 0 && ` · ${params.vanilla_pumps} vanilla`}
                {params.caramel_pumps > 0 && ` · ${params.caramel_pumps} caramel`}
                {params.mocha_pumps > 0 && ` · ${params.mocha_pumps} mocha`}
                {params.whipped_cream && " · whipped cream"}
                {params.protein_boost && " · protein boost"}
                {params.extra_espresso_shot && " · extra shot"}
              </p>
            </div>
          )}

          {orderResult && (
            <div className="card border-cafe-green bg-cafe-green-light/40">
              <h3 className="mb-2 font-semibold text-cafe-green-dark">Order Placed! 🎉</h3>
              <p className="text-sm">Order #{orderResult.id}</p>
              {orderResult.position && (
                <p className="mt-1 text-lg font-bold text-cafe-green">
                  You are #{orderResult.position} in queue
                </p>
              )}
              <p className="text-sm text-gray-600">
                Estimated wait: ~{orderResult.wait} minutes
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
