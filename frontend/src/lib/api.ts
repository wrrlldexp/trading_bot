import axios, { AxiosInstance } from "axios";
import {
  Strategy,
  Order,
  Trade,
  PortfolioSnapshot,
  StrategyStats,
  PortfolioOverview,
} from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        "Content-Type": "application/json",
      },
    });
  }

  // Strategies
  async getStrategies(): Promise<Strategy[]> {
    const res = await this.client.get("/api/strategies");
    return res.data;
  }

  async getStrategy(id: number): Promise<Strategy> {
    const res = await this.client.get(`/api/strategies/${id}`);
    return res.data;
  }

  async createStrategy(data: Omit<Strategy, "id" | "created_at" | "updated_at">): Promise<Strategy> {
    const res = await this.client.post("/api/strategies", data);
    return res.data;
  }

  async controlStrategy(
    id: number,
    action: "start" | "stop" | "pause" | "resume"
  ): Promise<any> {
    const res = await this.client.post(`/api/strategies/${id}/control`, {
      action,
    });
    return res.data;
  }

  // Orders
  async getOrders(skip = 0, limit = 100, status?: string): Promise<Order[]> {
    const res = await this.client.get("/api/orders", {
      params: { skip, limit, status },
    });
    return res.data;
  }

  async getOrder(id: number): Promise<Order> {
    const res = await this.client.get(`/api/orders/${id}`);
    return res.data;
  }

  async getStrategyOrders(strategyId: number): Promise<Order[]> {
    const res = await this.client.get(`/api/strategies/${strategyId}/orders`);
    return res.data;
  }

  // Trades
  async getTrades(skip = 0, limit = 100, status?: string): Promise<Trade[]> {
    const res = await this.client.get("/api/trades", {
      params: { skip, limit, status },
    });
    return res.data;
  }

  async getTrade(id: number): Promise<Trade> {
    const res = await this.client.get(`/api/trades/${id}`);
    return res.data;
  }

  async getStrategyTrades(strategyId: number): Promise<Trade[]> {
    const res = await this.client.get(`/api/strategies/${strategyId}/trades`);
    return res.data;
  }

  // Portfolio
  async getPortfolio(strategyId: number): Promise<PortfolioOverview> {
    const res = await this.client.get(`/api/strategies/${strategyId}/portfolio`);
    return res.data;
  }

  async getPortfolioHistory(strategyId: number, skip = 0, limit = 100): Promise<PortfolioSnapshot[]> {
    const res = await this.client.get("/api/portfolio-history", {
      params: { strategy_id: strategyId, skip, limit },
    });
    return res.data;
  }

  // Stats
  async getStrategyStats(strategyId: number): Promise<StrategyStats> {
    const res = await this.client.get(`/api/strategies/${strategyId}/stats`);
    return res.data;
  }

  // Health
  async health(): Promise<any> {
    const res = await this.client.get("/api/health");
    return res.data;
  }
}

export const apiClient = new ApiClient();
