import { useQuery, UseQueryResult } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { Strategy, Order, Trade, PortfolioOverview } from "@/types";

/**
 * Generic hook factory for creating optimized queries
 * Reduces boilerplate and ensures consistent configuration
 */
function createUseQuery<T>(
  queryKey: (string | number | null)[],
  queryFn: () => Promise<T>,
  refetchInterval: number = 5000,
  enabled: boolean = true
): UseQueryResult<T> {
  return useQuery<T>({
    queryKey,
    queryFn,
    refetchInterval,
    enabled,
  });
}

export function useStrategies() {
  return createUseQuery<Strategy[]>(
    ["strategies"],
    () => apiClient.getStrategies(),
    5000
  );
}

export function useStrategy(id: number) {
  return createUseQuery<Strategy>(
    ["strategy", id],
    () => apiClient.getStrategy(id),
    5000
  );
}

export function useOrders() {
  return createUseQuery<Order[]>(
    ["orders"],
    () => apiClient.getOrders(),
    3000
  );
}

export function useStrategyOrders(strategyId: number | null) {
  const isEnabled = strategyId !== null && strategyId !== undefined;
  return createUseQuery<Order[]>(
    ["strategy", strategyId, "orders"],
    () => apiClient.getStrategyOrders(strategyId!),
    3000,
    isEnabled
  );
}

export function useTrades() {
  return createUseQuery<Trade[]>(
    ["trades"],
    () => apiClient.getTrades(),
    5000
  );
}

export function useStrategyTrades(strategyId: number | null) {
  const isEnabled = strategyId !== null && strategyId !== undefined;
  return createUseQuery<Trade[]>(
    ["strategy", strategyId, "trades"],
    () => apiClient.getStrategyTrades(strategyId!),
    5000,
    isEnabled
  );
}

export function usePortfolio(strategyId: number | null) {
  const isEnabled = strategyId !== null && strategyId !== undefined;
  return createUseQuery<PortfolioOverview>(
    ["portfolio", strategyId],
    () => apiClient.getPortfolio(strategyId!),
    5000,
    isEnabled
  );
}

export function useHealth() {
  return createUseQuery(
    ["health"],
    () => apiClient.health(),
    10000
  );
}
