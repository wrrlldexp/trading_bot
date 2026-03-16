"use client";

import { useStrategy, useStrategyOrders, useStrategyTrades } from "@/hooks/useApi";
import { useRouter } from "next/router";
import Link from "next/link";

/**
 * Strategy Detail Page Component
 * 
 * Displays detailed information about a specific trading strategy including:
 * - Strategy overview (name, status, profit/loss, ROI)
 * - Active orders
 * - Trade history
 * 
 * Uses dynamic routing with strategy ID from URL parameters.
 */
export default function StrategyDetail() {
  const router = useRouter();
  const { id } = router.query;
  const strategyId = id ? Number(id) : null;

  if (!strategyId) {
    return <div className="p-8">Loading...</div>;
  }

  const { data: strategy, isLoading: strategyLoading } = useStrategy(strategyId);
  const { data: orders = [] } = useStrategyOrders(strategyId);
  const { data: trades = [] } = useStrategyTrades(strategyId);

  if (strategyLoading) {
    return <div className="p-8">Loading strategy...</div>;
  }

  if (!strategy) {
    return <div className="p-8 text-red-600">Strategy not found</div>;
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto p-8">
        <Link href="/" className="text-blue-400 hover:text-blue-300 mb-6 block">
          ← Back to Dashboard
        </Link>

        <h1 className="text-4xl font-bold mb-8">{strategy.name}</h1>

        {/* Overview Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-gray-800 p-4 rounded">
            <p className="text-gray-400 text-sm">Total Profit</p>
            <p className="text-2xl font-bold text-green-400">
              ${strategy.total_profit.toFixed(2)}
            </p>
          </div>
          <div className="bg-gray-800 p-4 rounded">
            <p className="text-gray-400 text-sm">ROI</p>
            <p className="text-2xl font-bold text-blue-400">
              {strategy.roi.toFixed(2)}%
            </p>
          </div>
          <div className="bg-gray-800 p-4 rounded">
            <p className="text-gray-400 text-sm">Win Rate</p>
            <p className="text-2xl font-bold text-purple-400">
              {strategy.win_rate.toFixed(2)}%
            </p>
          </div>
          <div className="bg-gray-800 p-4 rounded">
            <p className="text-gray-400 text-sm">Total Trades</p>
            <p className="text-2xl font-bold text-yellow-400">
              {strategy.total_trades}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Active Orders */}
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-bold mb-4">Active Orders</h2>
            <div className="overflow-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-700">
                    <th className="text-left py-2">Side</th>
                    <th className="text-right py-2">Price</th>
                    <th className="text-right py-2">Qty</th>
                    <th className="text-right py-2">Filled</th>
                  </tr>
                </thead>
                <tbody>
                  {orders
                    .filter((o) => o.status === "open")
                    .map((order) => (
                      <tr key={order.id} className="border-b border-gray-700">
                        <td className="py-2 capitalize text-yellow-400">
                          {order.side}
                        </td>
                        <td className="text-right">${order.price.toFixed(2)}</td>
                        <td className="text-right">{order.quantity.toFixed(4)}</td>
                        <td className="text-right">
                          {order.filled_quantity.toFixed(4)}
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
              {orders.filter((o) => o.status === "open").length === 0 && (
                <p className="text-gray-400 text-center py-4">No active orders</p>
              )}
            </div>
          </div>

          {/* Recent Trades */}
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-bold mb-4">Recent Trades</h2>
            <div className="overflow-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-700">
                    <th className="text-left py-2">Side</th>
                    <th className="text-right py-2">Entry</th>
                    <th className="text-right py-2">Exit</th>
                    <th className="text-right py-2">P&L</th>
                  </tr>
                </thead>
                <tbody>
                  {trades.slice(0, 10).map((trade) => (
                    <tr key={trade.id} className="border-b border-gray-700">
                      <td className="py-2 capitalize text-yellow-400">
                        {trade.side}
                      </td>
                      <td className="text-right">${trade.entry_price.toFixed(2)}</td>
                      <td className="text-right">
                        ${trade.exit_price?.toFixed(2) || "-"}
                      </td>
                      <td
                        className={`text-right ${
                          trade.profit_loss >= 0
                            ? "text-green-400"
                            : "text-red-400"
                        }`}
                      >
                        ${trade.profit_loss.toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {trades.length === 0 && (
                <p className="text-gray-400 text-center py-4">No trades yet</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
