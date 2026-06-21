"use client";

import { useEffect, useState } from "react";
import RushAlert from "@/components/RushAlert";
import { api, type AnalyticsDashboard } from "@/lib/api";

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsDashboard | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const dashboard = await api.getAnalytics();
        setData(dashboard);
      } catch {
        /* backend offline */
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <p className="text-center text-gray-500">Loading analytics…</p>;
  }

  if (!data) {
    return (
      <div className="card text-center text-red-600">
        Unable to load analytics. Make sure the backend is running on port 8000.
      </div>
    );
  }

  const channelTotal = Object.values(data.orders_by_channel).reduce((a, b) => a + b, 0);

  return (
    <div>
      <h1 className="mb-2 text-3xl font-bold text-cafe-green-dark">Operations Analytics</h1>
      <p className="mb-8 text-gray-600">Real-time store monitoring dashboard</p>

      <RushAlert detected={data.rush_detected} message={data.rush_message} />

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "Total Orders", value: data.total_orders, icon: "📦" },
          { label: "Active Queue", value: data.active_queue_size, icon: "⏳" },
          { label: "Avg Wait Time", value: `${data.average_wait_minutes} min`, icon: "🕐" },
          {
            label: "Rush Status",
            value: data.rush_detected ? "ACTIVE" : "Normal",
            icon: data.rush_detected ? "🔴" : "🟢",
          },
        ].map((stat) => (
          <div key={stat.label} className="card text-center">
            <span className="text-2xl">{stat.icon}</span>
            <p className="mt-2 text-2xl font-bold text-cafe-green-dark">{stat.value}</p>
            <p className="text-sm text-gray-500">{stat.label}</p>
          </div>
        ))}
      </div>

      <div className="mt-8 card">
        <h2 className="mb-4 text-lg font-semibold text-cafe-green-dark">Orders by Channel</h2>
        <div className="space-y-3">
          {Object.entries(data.orders_by_channel).map(([channel, count]) => {
            const pct = channelTotal > 0 ? (count / channelTotal) * 100 : 0;
            return (
              <div key={channel}>
                <div className="mb-1 flex justify-between text-sm">
                  <span className="capitalize">{channel}</span>
                  <span className="font-medium">
                    {count} ({pct.toFixed(0)}%)
                  </span>
                </div>
                <div className="h-3 overflow-hidden rounded-full bg-gray-100">
                  <div
                    className="h-full rounded-full bg-cafe-green transition-all"
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
