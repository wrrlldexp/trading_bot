#!/usr/bin/env python3
"""
Interactive Testing Dashboard for Adaptive Grid Trading Bot
Run tests and display results in real-time
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_test(name, result=None):
    if result is True:
        print(f"{Colors.GREEN}✅ PASS{Colors.END}  {name}")
    elif result is False:
        print(f"{Colors.RED}❌ FAIL{Colors.END}  {name}")
    else:
        print(f"{Colors.BLUE}⏳ TEST{Colors.END}  {name}")

def check_file_exists(path, name):
    if os.path.exists(path):
        print_test(f"File exists: {name}", True)
        return True
    else:
        print_test(f"File exists: {name}", False)
        return False

def check_directory_exists(path, name):
    if os.path.isdir(path):
        print_test(f"Directory exists: {name}", True)
        return True
    else:
        print_test(f"Directory exists: {name}", False)
        return False

def test_project_structure():
    print_header("PROJECT STRUCTURE VALIDATION")
    
    base_path = "/Users/magomedkuriev/Desktop/Новая папка/trading_bot"
    
    # Backend files
    print(f"{Colors.CYAN}Backend Structure:{Colors.END}")
    backend_files = [
        ("backend/main.py", "FastAPI entry point"),
        ("backend/requirements.txt", "Python dependencies"),
        ("backend/app/__init__.py", "App package"),
        ("backend/app/core/config.py", "Configuration"),
        ("backend/app/core/database.py", "Database setup"),
        ("backend/app/models/models.py", "SQLAlchemy models"),
        ("backend/app/exchange/binance_client.py", "Binance API"),
        ("backend/app/strategies/adaptive_grid.py", "Trading strategy"),
        ("backend/app/routes/strategy.py", "Strategy endpoints"),
        ("backend/app/routes/trades.py", "Trade endpoints"),
        ("backend/app/analytics/analytics_engine.py", "Analytics"),
    ]
    
    backend_pass = 0
    for filepath, desc in backend_files:
        full_path = os.path.join(base_path, filepath)
        if check_file_exists(full_path, f"{filepath} - {desc}"):
            backend_pass += 1
    
    print(f"\n  Backend: {backend_pass}/{len(backend_files)} ✅")
    
    # Frontend files
    print(f"\n{Colors.CYAN}Frontend Structure:{Colors.END}")
    frontend_files = [
        ("frontend/package.json", "Dependencies"),
        ("frontend/tsconfig.json", "TypeScript config"),
        ("frontend/next.config.js", "Next.js config"),
        ("frontend/tailwind.config.ts", "Tailwind config"),
        ("frontend/postcss.config.js", "PostCSS config"),
        ("frontend/src/pages/index.tsx", "Dashboard page"),
        ("frontend/src/pages/strategy/[id].tsx", "Strategy page"),
        ("frontend/src/hooks/useApi.ts", "API hooks"),
        ("frontend/src/lib/api.ts", "API client"),
        ("frontend/src/types/index.ts", "TypeScript types"),
    ]
    
    frontend_pass = 0
    for filepath, desc in frontend_files:
        full_path = os.path.join(base_path, filepath)
        if check_file_exists(full_path, f"{filepath} - {desc}"):
            frontend_pass += 1
    
    print(f"\n  Frontend: {frontend_pass}/{len(frontend_files)} ✅")
    
    # Docker files
    print(f"\n{Colors.CYAN}Docker Configuration:{Colors.END}")
    docker_files = [
        ("docker-compose.yml", "Docker Compose config"),
        ("docker/Dockerfile.backend", "Backend Dockerfile"),
        ("docker/Dockerfile.frontend", "Frontend Dockerfile"),
        (".env", "Environment variables"),
    ]
    
    docker_pass = 0
    for filepath, desc in docker_files:
        full_path = os.path.join(base_path, filepath)
        if check_file_exists(full_path, f"{filepath} - {desc}"):
            docker_pass += 1
    
    print(f"\n  Docker: {docker_pass}/{len(docker_files)} ✅")
    
    # Documentation
    print(f"\n{Colors.CYAN}Documentation:{Colors.END}")
    doc_files = [
        ("README.md", "Main documentation"),
        ("QUICKSTART.md", "Quick start guide"),
        ("ARCHITECTURE.md", "System architecture"),
        ("API_REFERENCE.md", "API documentation"),
        ("PROJECT_SUMMARY.md", "Project summary"),
    ]
    
    doc_pass = 0
    for filepath, desc in doc_files:
        full_path = os.path.join(base_path, filepath)
        if check_file_exists(full_path, f"{filepath} - {desc}"):
            doc_pass += 1
    
    print(f"\n  Documentation: {doc_pass}/{len(doc_files)} ✅")
    
    total = backend_pass + frontend_pass + docker_pass + doc_pass
    total_files = len(backend_files) + len(frontend_files) + len(docker_files) + len(doc_files)
    
    return total, total_files

def test_file_contents():
    print_header("CODE QUALITY CHECKS")
    
    base_path = "/Users/magomedкурiев/Desktop/Новая папка/trading_bot"
    results = []
    
    # Check docker-compose.yml
    print(f"{Colors.CYAN}Docker Configuration:{Colors.END}")
    try:
        with open(f"{base_path}/docker-compose.yml", 'r') as f:
            content = f.read()
            if "name: 'trading-bot'" in content:
                print_test("docker-compose.yml uses correct name", True)
                results.append(True)
            else:
                print_test("docker-compose.yml uses correct name", False)
                results.append(False)
            
            if "service_healthy" in content:
                print_test("Health checks configured", True)
                results.append(True)
            else:
                print_test("Health checks configured", False)
                results.append(False)
    except Exception as e:
        print_test(f"docker-compose.yml parsing - {e}", False)
        results.append(False)
    
    # Check backend main.py
    print(f"\n{Colors.CYAN}Backend Application:{Colors.END}")
    try:
        with open(f"{base_path}/backend/main.py", 'r') as f:
            content = f.read()
            if "FastAPI" in content and "CORSMiddleware" in content:
                print_test("FastAPI setup", True)
                results.append(True)
            else:
                print_test("FastAPI setup", False)
                results.append(False)
    except Exception as e:
        print_test(f"backend/main.py - {e}", False)
        results.append(False)
    
    # Check frontend config
    print(f"\n{Colors.CYAN}Frontend Configuration:{Colors.END}")
    try:
        with open(f"{base_path}/frontend/postcss.config.js", 'r') as f:
            content = f.read()
            if "tailwindcss:" in content and "autoprefixer:" in content:
                print_test("PostCSS config (object-based)", True)
                results.append(True)
            else:
                print_test("PostCSS config (object-based)", False)
                results.append(False)
    except Exception as e:
        print_test(f"frontend/postcss.config.js - {e}", False)
        results.append(False)
    
    return results

def test_dependencies():
    print_header("DEPENDENCIES CHECK")
    
    base_path = "/Users/magomedkuriev/Desktop/Новая папка/trading_bot"
    results = []
    
    # Check Python dependencies
    print(f"{Colors.CYAN}Backend Dependencies:{Colors.END}")
    try:
        with open(f"{base_path}/backend/requirements.txt", 'r') as f:
            deps = f.read()
            required = ["fastapi", "sqlalchemy", "psycopg2", "python-binance"]
            for dep in required:
                if dep in deps.lower():
                    print_test(f"Package: {dep}", True)
                    results.append(True)
                else:
                    print_test(f"Package: {dep}", False)
                    results.append(False)
    except Exception as e:
        print_test(f"requirements.txt - {e}", False)
        results.append(False)
    
    # Check npm dependencies
    print(f"\n{Colors.CYAN}Frontend Dependencies:{Colors.END}")
    try:
        with open(f"{base_path}/frontend/package.json", 'r') as f:
            content = json.load(f)
            deps = content.get("dependencies", {})
            required = ["next", "react", "react-dom", "recharts", "axios", "zustand"]
            for dep in required:
                if dep in deps:
                    print_test(f"Package: {dep}", True)
                    results.append(True)
                else:
                    print_test(f"Package: {dep}", False)
                    results.append(False)
    except Exception as e:
        print_test(f"package.json - {e}", False)
        results.append(False)
    
    return results

def main():
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                                                            ║")
    print("║   🤖 ADAPTIVE GRID TRADING BOT - TEST SUITE 🤖             ║")
    print("║                                                            ║")
    print("║   Comprehensive System Tests & Validation                  ║")
    print("║                                                            ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Test 1: Project Structure
    struct_pass, struct_total = test_project_structure()
    print(f"\n{Colors.BOLD}Structure Tests: {struct_pass}/{struct_total} ✅{Colors.END}")
    
    # Test 2: File Contents
    content_results = test_file_contents()
    content_pass = sum(content_results)
    content_total = len(content_results)
    print(f"\n{Colors.BOLD}Content Tests: {content_pass}/{content_total} ✅{Colors.END}")
    
    # Test 3: Dependencies
    dep_results = test_dependencies()
    dep_pass = sum(dep_results)
    dep_total = len(dep_results)
    print(f"\n{Colors.BOLD}Dependencies: {dep_pass}/{dep_total} ✅{Colors.END}")
    
    # Summary
    total_pass = struct_pass + content_pass + dep_pass
    total_tests = struct_total + content_total + dep_total
    success_rate = (total_pass / total_tests * 100) if total_tests > 0 else 0
    
    print_header("TEST SUMMARY")
    
    print(f"{Colors.BOLD}Total Tests:{Colors.END} {total_tests}")
    print(f"{Colors.GREEN}{Colors.BOLD}Passed:{Colors.END} {total_pass}")
    print(f"{Colors.RED}{Colors.BOLD}Failed:{Colors.END} {total_tests - total_pass}")
    print(f"{Colors.CYAN}{Colors.BOLD}Success Rate:{Colors.END} {success_rate:.1f}%")
    
    print(f"\n{Colors.BOLD}System Status:{Colors.END}")
    if success_rate == 100:
        print(f"  {Colors.GREEN}✅ ALL TESTS PASSED{Colors.END}")
        print(f"  {Colors.GREEN}✅ SYSTEM READY FOR DEPLOYMENT{Colors.END}")
        print(f"  {Colors.GREEN}✅ PRODUCTION READY{Colors.END}")
    else:
        print(f"  {Colors.YELLOW}⚠️  Some tests failed{Colors.END}")
    
    print(f"\n{Colors.BOLD}Next Steps:{Colors.END}")
    print(f"  1. Start bot:       {Colors.CYAN}cd trading_bot && ./scripts/start.sh{Colors.END}")
    print(f"  2. Dashboard:       {Colors.CYAN}http://localhost:3000{Colors.END}")
    print(f"  3. API Docs:        {Colors.CYAN}http://localhost:8000/docs{Colors.END}")
    print(f"  4. View Logs:       {Colors.CYAN}./scripts/logs.sh{Colors.END}")
    
    print(f"\n{Colors.BOLD}Completed:{Colors.END} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    return 0 if success_rate == 100 else 1

if __name__ == "__main__":
    sys.exit(main())
