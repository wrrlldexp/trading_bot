#!/usr/bin/env python3
"""
Comprehensive system tests for Adaptive Grid Trading Bot
Tests API endpoints, database, data integrity, and business logic
"""

import requests
import json
import time
from typing import Dict, List, Any
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 5

class Colors:
    """Terminal colors for output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class TestResult:
    """Track test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors: List[str] = []
    
    def add_pass(self, name: str):
        self.passed += 1
        print(f"{Colors.GREEN}✅ PASS{Colors.RESET} {name}")
    
    def add_fail(self, name: str, reason: str):
        self.failed += 1
        self.errors.append(f"{name}: {reason}")
        print(f"{Colors.RED}❌ FAIL{Colors.RESET} {name}: {reason}")
    
    def add_error(self, name: str, error: Exception):
        self.failed += 1
        self.errors.append(f"{name}: {str(error)}")
        print(f"{Colors.RED}⚠️  ERROR{Colors.RESET} {name}: {str(error)}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}TEST SUMMARY{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"Total: {total}")
        print(f"{Colors.GREEN}Passed: {self.passed}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.RESET}")
        
        if self.errors:
            print(f"\n{Colors.BOLD}Errors:{Colors.RESET}")
            for error in self.errors:
                print(f"  • {error}")


class APITester:
    """Test API endpoints"""
    
    def __init__(self):
        self.results = TestResult()
        self.strategy_id = None
        self.order_id = None
        self.trade_id = None
    
    def test_health(self):
        """Test health check endpoint"""
        print(f"\n{Colors.BLUE}Testing Health Endpoints{Colors.RESET}")
        
        try:
            response = requests.get(f"{BASE_URL}/api/health", timeout=TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                if "status" in data and data["status"] == "healthy":
                    self.results.add_pass("GET /api/health")
                    return True
                else:
                    self.results.add_fail("GET /api/health", "Invalid response format")
                    return False
            else:
                self.results.add_fail("GET /api/health", f"Status {response.status_code}")
                return False
        except Exception as e:
            self.results.add_error("GET /api/health", e)
            return False
    
    def test_get_strategies(self):
        """Test get strategies endpoint"""
        print(f"\n{Colors.BLUE}Testing Strategy Endpoints{Colors.RESET}")
        
        try:
            response = requests.get(f"{BASE_URL}/api/strategies", timeout=TIMEOUT)
            if response.status_code == 200:
                strategies = response.json()
                if isinstance(strategies, list):
                    self.results.add_pass(f"GET /api/strategies (found {len(strategies)})")
                    if len(strategies) > 0:
                        self.strategy_id = strategies[0]["id"]
                        return True
                    return True
                else:
                    self.results.add_fail("GET /api/strategies", "Expected list")
                    return False
            else:
                self.results.add_fail("GET /api/strategies", f"Status {response.status_code}")
                return False
        except Exception as e:
            self.results.add_error("GET /api/strategies", e)
            return False
    
    def test_create_strategy(self):
        """Test create strategy endpoint"""
        try:
            payload = {
                "name": f"Test Strategy {int(time.time())}",
                "pair": "BTCUSDT",
                "grid_levels": 10,
                "grid_profit_per_trade": 0.1,
                "atr_period": 14,
                "atr_multiplier": 2.0,
                "reverse_mode": False
            }
            
            response = requests.post(f"{BASE_URL}/api/strategies", json=payload, timeout=TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                if "id" in data:
                    self.strategy_id = data["id"]
                    self.results.add_pass("POST /api/strategies")
                    return True
                else:
                    self.results.add_fail("POST /api/strategies", "No ID in response")
                    return False
            else:
                self.results.add_fail("POST /api/strategies", f"Status {response.status_code}")
                return False
        except Exception as e:
            self.results.add_error("POST /api/strategies", e)
            return False
    
    def test_get_strategy_detail(self):
        """Test get strategy detail endpoint"""
        if not self.strategy_id:
            self.results.add_fail("GET /api/strategies/{id}", "No strategy ID")
            return False
        
        try:
            response = requests.get(f"{BASE_URL}/api/strategies/{self.strategy_id}", timeout=TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data["id"] == self.strategy_id:
                    self.results.add_pass(f"GET /api/strategies/{self.strategy_id}")
                    return True
                else:
                    self.results.add_fail("GET /api/strategies/{id}", "ID mismatch")
                    return False
            else:
                self.results.add_fail("GET /api/strategies/{id}", f"Status {response.status_code}")
                return False
        except Exception as e:
            self.results.add_error("GET /api/strategies/{id}", e)
            return False
    
    def test_get_orders(self):
        """Test get orders endpoint"""
        print(f"\n{Colors.BLUE}Testing Order Endpoints{Colors.RESET}")
        
        try:
            response = requests.get(f"{BASE_URL}/api/orders", timeout=TIMEOUT)
            if response.status_code == 200:
                orders = response.json()
                if isinstance(orders, list):
                    self.results.add_pass(f"GET /api/orders (found {len(orders)})")
                    if len(orders) > 0:
                        self.order_id = orders[0]["id"]
                    return True
                else:
                    self.results.add_fail("GET /api/orders", "Expected list")
                    return False
            else:
                self.results.add_fail("GET /api/orders", f"Status {response.status_code}")
                return False
        except Exception as e:
            self.results.add_error("GET /api/orders", e)
            return False
    
    def test_get_trades(self):
        """Test get trades endpoint"""
        print(f"\n{Colors.BLUE}Testing Trade Endpoints{Colors.RESET}")
        
        try:
            response = requests.get(f"{BASE_URL}/api/trades", timeout=TIMEOUT)
            if response.status_code == 200:
                trades = response.json()
                if isinstance(trades, list):
                    self.results.add_pass(f"GET /api/trades (found {len(trades)})")
                    if len(trades) > 0:
                        self.trade_id = trades[0]["id"]
                    return True
                else:
                    self.results.add_fail("GET /api/trades", "Expected list")
                    return False
            else:
                self.results.add_fail("GET /api/trades", f"Status {response.status_code}")
                return False
        except Exception as e:
            self.results.add_error("GET /api/trades", e)
            return False
    
    def test_strategy_stats(self):
        """Test strategy stats endpoint"""
        if not self.strategy_id:
            self.results.add_fail("GET /api/strategies/{id}/stats", "No strategy ID")
            return False
        
        try:
            response = requests.get(f"{BASE_URL}/api/strategies/{self.strategy_id}/stats", timeout=TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_trades", "total_profit", "win_rate", "roi"]
                if all(field in data for field in required_fields):
                    self.results.add_pass(f"GET /api/strategies/{self.strategy_id}/stats")
                    return True
                else:
                    self.results.add_fail("GET /api/strategies/{id}/stats", "Missing fields")
                    return False
            else:
                self.results.add_fail("GET /api/strategies/{id}/stats", f"Status {response.status_code}")
                return False
        except Exception as e:
            self.results.add_error("GET /api/strategies/{id}/stats", e)
            return False
    
    def test_portfolio_history(self):
        """Test portfolio history endpoint"""
        if not self.strategy_id:
            return False
        
        try:
            response = requests.get(
                f"{BASE_URL}/api/portfolio-history?strategy_id={self.strategy_id}",
                timeout=TIMEOUT
            )
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.results.add_pass(f"GET /api/portfolio-history (found {len(data)})")
                    return True
                else:
                    self.results.add_fail("GET /api/portfolio-history", "Expected list")
                    return False
            else:
                self.results.add_fail("GET /api/portfolio-history", f"Status {response.status_code}")
                return False
        except Exception as e:
            self.results.add_error("GET /api/portfolio-history", e)
            return False
    
    def test_data_integrity(self):
        """Test data integrity and relationships"""
        print(f"\n{Colors.BLUE}Testing Data Integrity{Colors.RESET}")
        
        if not self.strategy_id:
            self.results.add_fail("Data integrity check", "No strategy ID")
            return False
        
        try:
            # Get strategy
            strategy_resp = requests.get(f"{BASE_URL}/api/strategies/{self.strategy_id}", timeout=TIMEOUT)
            if strategy_resp.status_code != 200:
                self.results.add_fail("Strategy data load", f"Status {strategy_resp.status_code}")
                return False
            
            strategy = strategy_resp.json()
            
            # Verify required fields
            required_fields = ["id", "name", "pair", "status", "total_profit", "roi"]
            if all(field in strategy for field in required_fields):
                self.results.add_pass("Strategy data integrity")
            else:
                self.results.add_fail("Strategy data integrity", "Missing fields")
                return False
            
            # Get strategy orders
            orders_resp = requests.get(
                f"{BASE_URL}/api/strategies/{self.strategy_id}/orders",
                timeout=TIMEOUT
            )
            if orders_resp.status_code == 200:
                orders = orders_resp.json()
                if isinstance(orders, list):
                    self.results.add_pass(f"Strategy orders ({len(orders)} found)")
                    
                    # Verify order structure
                    if len(orders) > 0:
                        order = orders[0]
                        order_fields = ["id", "side", "price", "quantity", "status"]
                        if all(field in order for field in order_fields):
                            self.results.add_pass("Order data structure")
                        else:
                            self.results.add_fail("Order data structure", "Missing fields")
                else:
                    self.results.add_fail("Strategy orders", "Expected list")
            else:
                self.results.add_fail("Strategy orders", f"Status {orders_resp.status_code}")
            
            return True
        except Exception as e:
            self.results.add_error("Data integrity", e)
            return False
    
    def run_all(self):
        """Run all tests"""
        print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}ADAPTIVE GRID TRADING BOT - SYSTEM TESTS{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"Testing: {BASE_URL}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Health checks
        self.test_health()
        
        # Strategy endpoints
        self.test_get_strategies()
        self.test_get_strategy_detail()
        self.test_strategy_stats()
        
        # Order endpoints
        self.test_get_orders()
        
        # Trade endpoints
        self.test_get_trades()
        
        # Portfolio
        self.test_portfolio_history()
        
        # Data integrity
        self.test_data_integrity()
        
        # Summary
        self.results.summary()
        
        return self.results.failed == 0


def main():
    """Main test runner"""
    # Check if backend is accessible
    try:
        requests.get(f"{BASE_URL}/api/health", timeout=TIMEOUT)
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}❌ Cannot connect to {BASE_URL}{Colors.RESET}")
        print(f"{Colors.YELLOW}Make sure the backend is running: ./scripts/start.sh{Colors.RESET}")
        return False
    except Exception as e:
        print(f"{Colors.RED}❌ Error connecting to backend: {e}{Colors.RESET}")
        return False
    
    # Run tests
    tester = APITester()
    success = tester.run_all()
    
    return success


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
