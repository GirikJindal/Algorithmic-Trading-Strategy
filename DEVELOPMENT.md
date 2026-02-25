# Development Setup Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip
- git
- Virtual environment tool (venv, virtualenv, conda, etc.)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd trading-system
```

### 2. Create Virtual Environment
```bash
# Using venv (recommended)
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env  # or your preferred editor
```

### 5. Run the Demo
```bash
python demo.py
```

## 📋 Environment Variables

Create a `.env` file with the following variables:

```bash
# API Keys (get from respective providers)
ALPHA_VANTAGE_API_KEY=your_key_here
POLYGON_API_KEY=your_key_here
ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_secret_here

# Database (optional)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=trading_db
DB_USER=trader
DB_PASSWORD=your_password

# Application
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

## 🐳 Docker Development

### Using Docker Compose (Recommended)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f trading-system

# Stop services
docker-compose down
```

### Manual Docker Build
```bash
# Build image
docker build -t trading-system .

# Run container
docker run -p 8000:8000 --env-file .env trading-system
```

## 🧪 Testing

### Run All Tests
```bash
pytest tests/
```

### Run with Coverage
```bash
pytest --cov=src/trading_system tests/
```

### Code Quality
```bash
# Format code
black src/

# Sort imports
isort src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

## 📊 Usage Examples

### Command Line Interface
```bash
# Activate virtual environment first
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run backtest
trading-system backtest rsi AAPL --start-date 2023-01-01 --end-date 2023-12-31

# Compare strategies
trading-system compare sma_crossover rsi macd AAPL

# Generate signals
trading-system signals macd TSLA
```

### Web API
```bash
# Start the API server
python -m trading_system.trading.api

# API will be available at http://localhost:8000
# Documentation at http://localhost:8000/docs
```

### Python API
```python
from trading_system.data.providers import DataProviderFactory
from trading_system.strategies.strategies import StrategyFactory, StrategyConfig
from trading_system.backtesting.engine import BacktestRunner

# Your trading code here
```

## 🔧 Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code
   - Add tests
   - Update documentation

3. **Run Quality Checks**
   ```bash
   black src/
   isort src/
   flake8 src/
   mypy src/
   pytest tests/
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "Add your feature"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## 🐛 Troubleshooting

### Common Issues

**Import Errors**
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**API Key Errors**
```bash
# Check your .env file
cat .env

# Make sure API keys are set
echo $ALPHA_VANTAGE_API_KEY
```

**Port Already in Use**
```bash
# Kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn trading_system.trading.api:app --host 0.0.0.0 --port 8001
```

### Getting Help

- **Documentation**: See `docs/` directory
- **API Docs**: Run the server and visit `/docs`
- **Issues**: Check existing GitHub issues
- **Discussions**: Use GitHub Discussions for questions

## 📚 Project Structure

```
trading-system/
├── src/trading_system/     # Main package
│   ├── core/              # Core functionality
│   ├── data/              # Data providers
│   ├── strategies/        # Trading strategies
│   ├── backtesting/       # Backtesting engine
│   ├── risk/             # Risk management
│   ├── trading/          # Trading integration
│   └── utils/            # Utilities
├── tests/                 # Unit tests
├── docs/                  # Documentation
├── config/                # Configuration files
├── docker-compose.yml     # Docker orchestration
├── Dockerfile            # Docker image
├── requirements.txt      # Python dependencies
├── setup.py             # Package setup
└── README.md            # Project documentation
```

## 🚀 Deployment

### Production Deployment
```bash
# Using Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Or using Kubernetes
kubectl apply -f k8s/
```

### Environment Variables for Production
```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
```

## 🤝 Contributing

1. Follow the development setup guide
2. Write tests for new features
3. Update documentation
4. Follow code style guidelines
5. Create meaningful commit messages

---

Happy trading! 📈🚀