export interface Strategy {
  id: number;
  name: string;
  pair: string;
  is_active: boolean;
  status: string;
  grid_levels: number;
  grid_profit_per_trade: number;
  atr_period: number;
  atr_multiplier: number;
  reverse_mode: boolean;
  total_trades: number;
  total_profit: number;
  win_rate: number;
  roi: number;
  created_at: string;
  updated_at: string;
}

export interface Order {
  id: number;
  exchange_order_id?: string;
  pair: string;
  side: "buy" | "sell";
  price: number;
  quantity: number;
  filled_quantity: number;
  status: string;
  average_fill_price: number;
  commission: number;
  is_grid_order: boolean;
  created_at: string;
  filled_at?: string;
}

export interface Trade {
  id: number;
  pair: string;
  entry_price: number;
  exit_price?: number;
  quantity: number;
  side: "buy" | "sell";
  status: string;
  profit_loss: number;
  roi: number;
  opened_at: string;
  closed_at?: string;
}

export interface PortfolioSnapshot {
  total_value: number;
  btc_balance: number;
  usdt_balance: number;
  total_profit: number;
  roi: number;
  max_drawdown: number;
  timestamp: string;
}

export interface GridLevel {
  level: number;
  price: number;
  side: "buy" | "sell";
  is_filled: boolean;
  filled_at?: string;
}

export interface StrategyStats {
  total_trades: number;
  total_profit: number;
  win_rate: number;
  roi: number;
  active_orders: number;
  active_trades: number;
  max_drawdown: number;
  uptime_seconds: number;
}

export interface PortfolioOverview {
  current_total_value: number;
  btc_balance: number;
  usdt_balance: number;
  total_profit: number;
  roi: number;
  max_drawdown: number;
  active_trades: number;
  active_orders: number;
  total_trades: number;
  win_rate: number;
}
