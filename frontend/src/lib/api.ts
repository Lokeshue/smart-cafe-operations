/**
 * API client for Smart Café backend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001/api";

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API error: ${res.status}`);
  }

  return res.json();
}

export interface Drink {
  id: number;
  name: string;
  description: string;
  base_calories: number;
  base_sugar: number;
  base_protein: number;
  base_caffeine: number;
}

export interface Nutrition {
  calories: number;
  sugar: number;
  protein: number;
  caffeine: number;
  summary: string;
}

export interface CustomizeResponse {
  drink_name: string;
  size: string;
  customizations: Record<string, unknown>;
  nutrition: Nutrition;
}

export interface Order {
  id: number;
  customer_name: string;
  drink_name: string;
  customizations: Record<string, unknown>;
  channel: string;
  order_time: string;
  priority_score: number;
  status: string;
  estimated_wait_minutes: number;
  queue_position?: number;
}

export interface QueueStatus {
  total_in_queue: number;
  orders: Order[];
  rush_detected: boolean;
  rush_message?: string;
  average_wait_minutes: number;
}

export interface AnalyticsDashboard {
  total_orders: number;
  average_wait_minutes: number;
  orders_by_channel: Record<string, number>;
  rush_detected: boolean;
  rush_message?: string;
  active_queue_size: number;
}

export interface CustomizeParams {
  drink_id: number;
  size: string;
  milk_type: string;
  vanilla_pumps: number;
  caramel_pumps: number;
  mocha_pumps: number;
  whipped_cream: boolean;
  protein_boost: boolean;
  extra_espresso_shot: boolean;
}

export const api = {
  getDrinks: () => fetchApi<Drink[]>("/drinks"),

  customizeDrink: (params: CustomizeParams) =>
    fetchApi<CustomizeResponse>("/customize-drink", {
      method: "POST",
      body: JSON.stringify(params),
    }),

  createOrder: (params: CustomizeParams & { customer_name: string; channel: string }) =>
    fetchApi<Order>("/orders", {
      method: "POST",
      body: JSON.stringify(params),
    }),

  getOrders: (status?: string) =>
    fetchApi<Order[]>(`/orders${status ? `?status=${status}` : ""}`),

  getOrder: (id: number) => fetchApi<Order>(`/orders/${id}`),

  updateOrderStatus: (id: number, status: string) =>
    fetchApi<Order>(`/orders/${id}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    }),

  getQueueStatus: () => fetchApi<QueueStatus>("/queue/status"),

  getAnalytics: () => fetchApi<AnalyticsDashboard>("/analytics/dashboard"),

  getRushAnalytics: () => fetchApi<{ rush_detected: boolean; message: string }>("/analytics/rush"),
};
