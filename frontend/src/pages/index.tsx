"use client";

import { useStrategies, useStrategyOrders, useStrategyTrades } from "@/hooks/useApi";
import { useState } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ComposedChart, Line } from "recharts";

export default function Dashboard() {
  const { data: strategies = [], isLoading, error } = useStrategies();
  const [selectedStrategy] = useState<number | null>(strategies[0]?.id ?? null);

  const { data: orders = [] } = useStrategyOrders(selectedStrategy);
  const { data: trades = [] } = useStrategyTrades(selectedStrategy);

  if (isLoading) {
    return <div className="min-h-screen bg-gray-950 text-white p-8">Loading...</div>;
  }

  if (error) {
    return <div className="min-h-screen bg-gray-950 text-white p-8 text-red-600">Error loading strategies</div>;
  }

  const strategy = strategies[0];
  if (!strategy) {
    return <div className="min-h-screen bg-gray-950 text-white p-8">No strategies found</div>;
  }

  const activeOrders = orders.filter(o => o.status === "open").length;
  const netProfit = strategy.total_profit;
  const profitPercent = strategy.roi;
  
  const chartData = Array.from({ length: 24 }, (_, i) => {
    const baseEquity = 100000;
    const volatility = Math.sin(i * 0.5) * 5000 + Math.random() * 2000;
    return {
      day: i + 1,
      equity: baseEquity + netProfit + volatility,
      profit: Math.max(0, netProfit * (i / 24)),
    };
  });

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-950 to-gray-900 text-white">
      <div className="fixed left-0 top-0 w-16 h-screen bg-gray-950 border-r border-gray-800 flex flex-col items-center py-6 gap-6">
        <div className="w-8 h-8 bg-blue-600 rounded"></div>
        <div className="w-8 h-8 bg-gray-700 rounded"></div>
        <div className="w-8 h-8 bg-gray-700 rounded"></div>
        <div className="w-8 h-8 bg-gray-700 rounded"></div>
        <div className="w-8 h-8 bg-gray-700 rounded"></div>
      </div>

      <div className="ml-16 p-8">
        <div className="flex justify-between items-center mb-8">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-gray-600 rounded"></div>
            <span className="text-gray-400 text-sm">Web</span>
            <h1 className="text-2xl font-bold">Dashboard</h1>
          </div>
          <div className="flex items-center gap-4">
            <div className="relative">
              <input
                type="text"
                placeholder="Search"
                className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm text-white placeholder-gray-500 w-48"
              />
              <span className="absolute right-3 top-2.5 text-gray-500">🔍</span>
            </div>
            <div className="w-10 h-10 bg-gray-700 rounded-full flex items-center justify-center">👤</div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <p className="text-gray-400 text-sm font-medium mb-3">Total Balance</p>
            <h3 className="text-3xl font-bold mb-2">${(100000 + netProfit).toLocaleString('en-US', { maximumFractionDigits: 2 })}</h3>
            <p className="text-xs text-gray-500">BTC: 0.1254</p>
          </div>

          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <p className="text-gray-400 text-sm font-medium mb-3">Active Orders</p>
            <h3 className="text-3xl font-bold mb-2">{activeOrders}</h3>
            <p className="text-xs text-gray-500">Open positions</p>
          </div>

          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <p className="text-gray-400 text-sm font-medium mb-3">Net Profit</p>
            <div className="flex items-center gap-3">
              <div>
                <h3 className={`text-3xl font-bold ${netProfit >= 0 ? "text-green-400" : "text-red-400"}`}>
                  {netProfit >= 0 ? "+" : ""}{netProfit.toFixed(2)} USDT
                </h3>
              </div>
              <span className={`text-lg font-bold ${profitPercent >= 0 ? "text-green-400" : "text-red-400"}`}>
                {profitPercent >= 0 ? "+" : ""}{profitPercent.toFixed(1)}%
              </span>
            </div>
          </div>

          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <p className="text-gray-400 text-sm font-medium mb-3">Drawdown</p>
            <h3 className="text-3xl font-bold text-red-400 mb-2">-3.2%</h3>
            <p className="text-xs text-gray-500">Max equity loss</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            <div className="bg-gray-800 border border-gray-700 rounded-lg">
              <div className="px-6 py-4 border-b border-gray-700">
                <h2 className="text-lg font-semibold">Open Orders</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-700">
                      <th className="px-6 py-3 text-left text-gray-400 font-medium">Type</th>
                      <th className="px-6 py-3 text-left text-gray-400 font-medium">Pair</th>
                      <th className="px-6 py-3 text-left text-gray-400 font-medium">Price</th>
                      <th className="px-6 py-3 text-left text-gray-400 font-medium">Amount</th>
                      <th className="px-6 py-3 text-left text-gray-400 font-medium">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {orders.slice(0, 5).map((order, idx) => (
                      <tr key={idx} className="border-b border-gray-700 hover:bg-gray-700/50">
                        <td className="px-6 py-3">
                          <span className={`px-2 py-1 rounded text-xs font-bold ${
                            order.side === "buy" ? "bg-green-900 text-green-400" : "bg-red-900 text-red-400"
                          }`}>
                            {order.side === "buy" ? "Buy" : "Sell"}
                          </span>
                        </td>
                        <td className="px-6 py-3 text-white">{order.pair}</td>
                        <td className="px-6 py-3 text-white">{order.price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                        <td className="px-6 py-3 text-white">{order.quantity.toFixed(4)}</td>
                        <td className={`px-6 py-3 font-medium ${order.status === "open" ? "text-green-400" : "text-gray-400"}`}>
                          {order.status === "open" ? "Open" : order.status}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="bg-gray-800 border border-gray-700 rounded-lg">
              <div className="px-6 py-4 border-b border-gray-700 flex justify-between items-center">
                <h2 className="text-lg font-semibold">Trade History</h2>
                <div className="flex gap-2">
                  <button className="text-xs px-3 py-1 rounded bg-gray-700 text-gray-300 hover:bg-gray-600">7d</button>
                  <button className="text-xs px-3 py-1 rounded bg-gray-700 text-gray-300 hover:bg-gray-600">1m</button>
                  <button className="text-xs px-3 py-1 rounded bg-gray-700 text-gray-300 hover:bg-gray-600">3m</button>
                  <button className="text-xs px-3 py-1 rounded bg-gray-600 text-white">All</button>
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-700">
                      <th className="px-6 py-3 text-left text-gray-400 font-medium">Time</th>
                      <th className="px-6 py-3 text-left text-gray-400 font-medium">Pair</th>
                      <th className="px-6 py-3 text-left text-gray-400 font-medium">Side</th>
                      <th className="px-6 py-3 text-left text-gray-400 font-medium">Price</th>
                      <th className="px-6 py-3 text-left text-gray-400 font-medium">Amount</th>
                      <th className="px-6 py-3 text-left text-gray-400 font-medium">Profit</th>
                    </tr>
                  </thead>
                  <tbody>
                    {trades.slice(0, 5).map((trade, idx) => (
                      <tr key={idx} className="border-b border-gray-700 hover:bg-gray-700/50">
                        <td className="px-6 py-3 text-gray-400">12:45:32</td>
                        <td className="px-6 py-3 text-white">{trade.pair}</td>
                        <td className="px-6 py-3">
                          <span className={`px-2 py-1 rounded text-xs font-bold ${
                            trade.side === "buy" ? "bg-green-900 text-green-400" : "bg-red-900 text-red-400"
                          }`}>
                            {trade.side === "buy" ? "Buy" : "Sell"}
                          </span>
                        </td>
                        <td className="px-6 py-3 text-white">{trade.entry_price.toFixed(2)}</td>
                        <td className="px-6 py-3 text-white">{trade.quantity.toFixed(4)}</td>
                        <td className={`px-6 py-3 font-bold ${trade.profit_loss >= 0 ? "text-green-400" : "text-red-400"}`}>
                          {trade.profit_loss >= 0 ? "+" : ""}{trade.profit_loss.toFixed(2)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <div className="space-y-8">
            <div className="bg-gray-800 border border-gray-700 rounded-lg">
              <div className="px-6 py-4 border-b border-gray-700">
                <h2 className="text-lg font-semibold">Bot Controls</h2>
              </div>
              <div className="p-6 space-y-3">
                <button className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded-lg transition">
                  Start Bot
                </button>
                <button className="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3 rounded-lg transition">
                  Stop Bot
                </button>
                <button className="w-full bg-gray-700 hover:bg-gray-600 text-white font-bold py-3 rounded-lg flex justify-between items-center px-4 transition">
                  <span>Reverse Mode</span>
                  <span>›</span>
                </button>
                <button className="w-full bg-gray-700 hover:bg-gray-600 text-white font-bold py-3 rounded-lg flex justify-between items-center px-4 transition">
                  <span>Grid Settings</span>
                  <span>›</span>
                </button>
                <button className="w-full bg-gray-700 hover:bg-gray-600 text-white font-bold py-3 rounded-lg flex justify-between items-center px-4 transition">
                  <span>Risk Management</span>
                  <span>›</span>
                </button>
              </div>
            </div>

            <div className="bg-gray-800 border border-gray-700 rounded-lg">
              <div className="px-6 py-4 border-b border-gray-700">
                <h2 className="text-lg font-semibold">Equity</h2>
              </div>
              <div className="p-4">
                <ResponsiveContainer width="100%" height={300}>
                  <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10B981" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#10B981" stopOpacity={0.1}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
                    <XAxis dataKey="day" stroke="#9CA3AF" style={{ fontSize: '12px' }} />
                    <YAxis stroke="#9CA3AF" style={{ fontSize: '12px' }} width={50} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1F2937', 
                        border: '1px solid #4B5563', 
                        borderRadius: '6px',
                        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.3)'
                      }}
                      labelStyle={{ color: '#fff', fontSize: '12px' }}
                      formatter={(value) => [`$${value.toLocaleString('en-US', { maximumFractionDigits: 0 })}`, 'Equity']}
                    />
                    <Bar dataKey="profit" fill="#FBBF24" opacity={0.4} radius={[2, 2, 0, 0]} />
                    <Line 
                      type="natural" 
                      dataKey="equity" 
                      stroke="#10B981" 
                      strokeWidth={3}
                      dot={false}
                      isAnimationActive={false}
                      fill="url(#colorEquity)"
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
