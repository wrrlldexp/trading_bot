# Contributing to Trading Bot

Thank you for your interest in contributing! Here are guidelines to help you get started.

## Code of Conduct

- Be respectful and constructive
- Focus on the code, not the person
- Help others learn and grow
- Report issues responsibly

## How to Contribute

### 1. Report Bugs

**Before creating a bug report, please check the issue list** as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- Use a clear and descriptive title
- Describe the exact steps to reproduce the problem
- Provide specific examples to demonstrate the steps
- Describe the behavior you observed after following the steps
- Explain which behavior you expected to see instead and why
- Include screenshots or logs if possible

### 2. Suggest Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- Use a clear and descriptive title
- Provide a step-by-step description of the suggested enhancement
- Provide specific examples to demonstrate the steps
- Describe the current behavior and expected behavior
- Explain why this enhancement would be useful

### 3. Code Contributions

#### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/trading_bot.git
cd trading_bot

# Create a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt
cd ../frontend
npm install
```

#### Development Workflow

1. **Create a branch**
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-description
```

2. **Make changes**
   - Follow the existing code style
   - Write clear commit messages
   - Keep commits atomic and logical

3. **Test your changes**
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

4. **Run Docker locally**
```bash
docker-compose up -d
# Test your changes
docker-compose down
```

5. **Commit and push**
```bash
git add .
git commit -m "feat: clear description of what you changed"
git push origin feature/your-feature-name
```

6. **Create a Pull Request**
   - Provide a clear description
   - Reference related issues
   - Ensure CI passes

## Code Style Guide

### Python

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints where possible
- Maximum line length: 100 characters
- Use docstrings for functions and classes

Example:
```python
def calculate_grid_levels(
    current_price: float,
    grid_step: float,
    num_levels: int
) -> list[float]:
    """
    Calculate grid price levels.
    
    Args:
        current_price: Current market price
        grid_step: Step size in percentage
        num_levels: Number of levels to generate
        
    Returns:
        List of price levels
    """
    levels = []
    for i in range(-num_levels, num_levels + 1):
        level = current_price * (1 + grid_step * i / 100)
        levels.append(level)
    return sorted(levels)
```

### TypeScript/JavaScript

- Use TypeScript for new code
- Follow [Airbnb style guide](https://github.com/airbnb/javascript)
- Use meaningful variable names
- Add JSDoc comments for exported functions

Example:
```typescript
/**
 * Fetch strategies from the API
 * @param limit - Maximum number of strategies to fetch
 * @returns Array of strategies
 */
export const fetchStrategies = async (
  limit: number = 10
): Promise<Strategy[]> => {
  const response = await api.get('/strategies', { params: { limit } });
  return response.data;
};
```

## Commit Message Convention

Use conventional commits format:

```
type(scope): subject

body

footer
```

Types:
- `feat:` - A new feature
- `fix:` - A bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, missing semicolons, etc.)
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `test:` - Adding or updating tests
- `chore:` - Build process, dependencies, etc.

Examples:
```
feat(grid): implement adaptive grid rebuild logic

fix(api): correct order flipping endpoint response

docs(readme): add docker deployment instructions

chore(deps): upgrade fastapi to 0.105
```

## Testing

### Backend Tests

```bash
cd backend
# Run all tests
pytest

# Run specific test file
pytest tests/test_grid_adaptation.py

# Run with coverage
pytest --cov=app tests/
```

### Frontend Tests

```bash
cd frontend
# Run tests
npm test

# Build for testing
npm run build
```

### Integration Tests

```bash
docker-compose up -d
./scripts/docker-manage.sh test-endpoints
docker-compose down
```

## Documentation

- Update README.md if you change functionality
- Add docstrings to all functions
- Update API documentation for new endpoints
- Include code examples where helpful

## Pull Request Process

1. Update documentation and README.md if needed
2. Add tests for new functionality
3. Ensure all tests pass locally
4. Ensure Docker builds successfully
5. Request review from maintainers
6. Address feedback promptly

## Questions?

- Check existing issues and discussions
- Create a new issue with the `question` label
- Review documentation in DOCKER_GUIDE.md and API_REFERENCE.md

## Additional Notes

- This project uses Docker Compose for development
- The trading strategy is based on grid trading with ATR
- Always test on testnet before using real funds
- Keep security as a top priority

---

Thank you for contributing! 🚀
