"use client";

import { useCallback, useEffect, useState } from "react";
import RushAlert from "@/components/RushAlert";
import { api, type Order, type QueueStatus } from "@/lib/api";

const STATUS_FLOW = ["Received", "In Progress", "Ready", "Picked Up"] as const;

const channelColors: Record<string, string> = {
  mobile: "bg-blue-100 text-blue-800",
  "drive-thru": "bg-orange-100 text-orange-800",
  "walk-in": "bg-purple-100 text-purple-800",
};

const statusColors: Record<string, string> = {
  Received: "bg-gray-100 text-gray-700",
  "In Progress": "bg-yellow-100 text-yellow-800",
  Ready: "bg-green-100 text-green-800",
  "Picked Up": "bg-gray-200 text-gray-500",
};

function formatCustomizations(c: Record<string, unknown>): string {
  const parts: string[] = [];
  if (c.size) parts.push(String(c.size));
  if (c.milk_type) parts.push(String(c.milk_type));
  if (c.vanilla_pumps) parts.push(`${c.vanilla_pumps} vanilla`);
  if (c.caramel_pumps) parts.push(`${c.caramel_pumps} caramel`);
  if (c.mocha_pumps) parts.push(`${c.mocha_pumps} mocha`);
  if (c.whipped_cream) parts.push("whipped cream");
  if (c.protein_boost) parts.push("protein boost");
  if (c.extra_espresso_shot) parts.push("extra shot");
  return parts.join(" · ") || "standard";
}

function nextStatus(current: string): string | null {
  const idx = STATUS_FLOW.indexOf(current as (typeof STATUS_FLOW)[number]);
  if (idx >= 0 && idx < STATUS_FLOW.length - 1) return STATUS_FLOW[idx + 1];
  return null;
}

export default function BaristaPage() {
  const [queue, setQueue] = useState<QueueStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState<number | null>(null);

  const fetchQueue = useCallback(async () => {
    try {
      const data = await api.getQueueStatus();
      setQueue(data);
    } catch {
      /* backend may be offline */
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchQueue();
    const interval = setInterval(fetchQueue, 5000);
    return () => clearInterval(interval);
  }, [fetchQueue]);

  const handleStatusUpdate = async (order: Order) => {
    const next = nextStatus(order.status);
    if (!next) return;

    setUpdating(order.id);
    try {
      await api.updateOrderStatus(order.id, next);
      await fetchQueue();
    } finally {
      setUpdating(null);
    }
  };

  if (loading) {
    return <p className="text-center text-gray-500">Loading queue…</p>;
  }

  return (
    <div>
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-cafe-green-dark">Barista Queue Dashboard</h1>
          <p className="text-gray-600">Smart-sequenced orders from all channels</p>
        </div>
        {queue && (
          <div className="flex gap-4 text-sm">
            <span className="rounded-lg bg-white px-4 py-2 shadow-sm">
              <strong>{queue.total_in_queue}</strong> in queue
            </span>
            <span className="rounded-lg bg-white px-4 py-2 shadow-sm">
              Avg wait: <strong>{queue.average_wait_minutes} min</strong>
            </span>
          </div>
        )}
      </div>

      {queue && <RushAlert detected={queue.rush_detected} message={queue.rush_message} />}

      {!queue || queue.orders.length === 0 ? (
        <div className="card mt-6 text-center text-gray-500">
          <p className="text-lg">No active orders in queue.</p>
          <p className="mt-1 text-sm">Orders will appear here when customers place them.</p>
        </div>
      ) : (
        <div className="mt-6 space-y-4">
          {queue.orders.map((order) => (
            <div
              key={order.id}
              className="card flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
            >
              <div className="flex items-start gap-4">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-cafe-green text-lg font-bold text-white">
                  #{order.queue_position}
                </div>
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="font-semibold text-cafe-green-dark">{order.customer_name}</h3>
                    <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${channelColors[order.channel] || ""}`}>
                      {order.channel}
                    </span>
                    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${statusColors[order.status] || ""}`}>
                      {order.status}
                    </span>
                  </div>
                  <p className="mt-1 font-medium">{order.drink_name}</p>
                  <p className="text-sm capitalize text-gray-500">
                    {formatCustomizations(order.customizations)}
                  </p>
                  <p className="mt-1 text-xs text-gray-400">
                    Ordered {new Date(order.order_time).toLocaleTimeString()} · Priority: {order.priority_score} · Est. {order.estimated_wait_minutes} min
                  </p>
                </div>
              </div>

              {nextStatus(order.status) && (
                <button
                  className="btn-primary shrink-0 text-sm"
                  onClick={() => handleStatusUpdate(order)}
                  disabled={updating === order.id}
                >
                  {updating === order.id ? "Updating…" : `Mark ${nextStatus(order.status)}`}
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="mt-8 card bg-cafe-green-light/20">
        <h3 className="mb-2 font-semibold text-cafe-green-dark">Smart Sequencing Rules</h3>
        <ul className="list-inside list-disc space-y-1 text-sm text-gray-600">
          <li>Older orders receive higher priority (10 pts/min waited)</li>
          <li>Drive-thru orders boosted +50 when average wait exceeds 5 min</li>
          <li>Similar drinks batched together (+20 if same drink in progress)</li>
          <li>Mobile orders boosted +15 after 7 min wait</li>
        </ul>
      </div>
    </div>
  );
}
