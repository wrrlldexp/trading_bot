"""
API routes package.

Includes routers for:
- health: Health checks and status
- strategy: Strategy CRUD and operations
- trades: Trade and order endpoints
- grid_management: Grid management and adaptation
"""

from app.routes import health, strategy, trades, grid_management

__all__ = ["health", "strategy", "trades", "grid_management"]
