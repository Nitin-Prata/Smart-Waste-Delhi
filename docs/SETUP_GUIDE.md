# 🚀 Complete Setup Guide for Smart Delhi Project

This guide will walk you through setting up the entire Smart Waste & Air Quality Management system from scratch, using only free resources.

## 📋 Prerequisites

### Required Software

- **Python 3.9+**: [Download here](https://www.python.org/downloads/)
- **Node.js 16+**: [Download here](https://nodejs.org/)
- **PostgreSQL 13+**: [Download here](https://www.postgresql.org/download/)
- **Redis 6+**: [Download here](https://redis.io/download)
- **Git**: [Download here](https://git-scm.com/downloads)

### Free Accounts (Optional)

- **GitHub**: For code hosting
- **Render/Railway**: For free deployment
- **Mapbox**: Free tier for maps (optional)

## 🛠️ Step-by-Step Setup

### Step 1: Project Setup

```bash
# Clone or create project directory
mkdir smart-waste-delhi
cd smart-waste-delhi

# Create project structure
mkdir backend frontend data models docs training
```

### Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn sqlalchemy psycopg2-binary redis
pip install tensorflow scikit-learn pandas numpy matplotlib seaborn
pip install requests aiohttp python-dotenv pydantic
pip install pytest pytest-asyncio httpx

# Create requirements.txt
pip freeze > requirements.txt
```

### Step 3: Database Setup

```bash
# Start PostgreSQL (if not running)
# On Windows: Start from Services
# On macOS: brew services start postgresql
# On Linux: sudo systemctl start postgresql

# Create database
createdb smart_waste_delhi

# Start Redis (if not running)
# On Windows: Download and run redis-server.exe
# On macOS: brew services start redis
# On Linux: sudo systemctl start redis
```

### Step 4: Environment Configuration

```bash
# Copy environment template
cp env.example .env

# Edit .env file with your settings
# Use any text editor to modify the file
```

Example `.env` file:

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost/smart_waste_delhi
REDIS_URL=redis://localhost:6379

# AI Model Settings
LSTM_MODEL_PATH=models/lstm_air_quality.h5
RANDOM_FOREST_MODEL_PATH=models/rf_waste_prediction.pkl

# Delhi Coordinates
DELHI_CENTER_LAT=28.7041
DELHI_CENTER_LON=77.1025

# Air Quality Thresholds
AQI_GOOD=50
AQI_MODERATE=100
AQI_UNHEALTHY_SENSITIVE=150
AQI_UNHEALTHY=200
AQI_VERY_UNHEALTHY=300
AQI_HAZARDOUS=500

# Waste Management Settings
WASTE_COLLECTION_INTERVAL_HOURS=24
BIN_FILL_THRESHOLD=0.8

# Development
DEBUG=true
LOG_LEVEL=INFO
```

### Step 5: Data Generation

```bash
# Navigate to data directory
cd ../data

# Run data collection script
python data_collection.py
```

This will create:

- `synthetic_air_quality_delhi_YYYYMMDD.csv`
- `waste_bins_delhi_YYYYMMDD.csv`
- `waste_readings_delhi_YYYYMMDD.csv`
- `weather_delhi_YYYYMMDD.csv`
- `dataset_summary.json`

### Step 6: AI Model Training

```bash
# Navigate to training directory
cd ../training

# Train air quality model
python train_air_quality_model.py

# Train waste management model
python train_waste_model.py
```

This will create:

- `models/lstm_air_quality.h5`
- `models/rf_waste_prediction.pkl`
- `models/rf_waste_classification.pkl`
- `models/waste_scalers.pkl`
- Model information files and plots

### Step 7: Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Initialize React app
npx create-react-app . --template typescript

# Install additional dependencies
npm install axios react-router-dom mapbox-gl chart.js react-chartjs-2
npm install tailwindcss @tailwindcss/forms lucide-react recharts
npm install react-hot-toast date-fns clsx framer-motion

# Install dev dependencies
npm install --save-dev @types/mapbox-gl autoprefixer postcss
```

### Step 8: Configure Tailwind CSS

```bash
# Initialize Tailwind CSS
npx tailwindcss init -p

# This creates tailwind.config.js and postcss.config.js
```

### Step 9: Start the Backend

```bash
# Navigate to backend directory
cd ../backend

# Activate virtual environment (if not already active)
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Start the FastAPI server
python main.py
```

The backend will be available at:

- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Step 10: Start the Frontend

```bash
# Open new terminal and navigate to frontend
cd frontend

# Start React development server
npm start
```

The frontend will be available at:

- **Dashboard**: http://localhost:3000

## 🧪 Testing the Setup

### Backend API Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test dashboard overview
curl http://localhost:8000/api/dashboard/overview

# Test air quality data
curl http://localhost:8000/api/air-quality/current

# Test waste management data
curl http://localhost:8000/api/waste/summary
```

### Frontend Testing

1. Open http://localhost:3000 in your browser
2. Navigate through different pages:
   - Dashboard
   - Air Quality
   - Waste Management
   - AI Insights
   - Map
   - Citizen View
   - Alerts

### Model Testing

```bash
# Test LSTM model
python -c "
import tensorflow as tf
model = tf.keras.models.load_model('models/lstm_air_quality.h5')
print('LSTM model loaded successfully')
"

# Test Random Forest model
python -c "
import joblib
model = joblib.load('models/rf_waste_prediction.pkl')
print('Random Forest model loaded successfully')
"
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Database Connection Error

```bash
# Check if PostgreSQL is running
# Windows: Check Services
# macOS: brew services list | grep postgresql
# Linux: sudo systemctl status postgresql

# Test connection
psql -h localhost -U username -d smart_waste_delhi
```

#### 2. Redis Connection Error

```bash
# Check if Redis is running
# Windows: Check if redis-server.exe is running
# macOS: brew services list | grep redis
# Linux: sudo systemctl status redis

# Test connection
redis-cli ping
```

#### 3. Python Dependencies Error

```bash
# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

#### 4. Node.js Dependencies Error

```bash
# Clear npm cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

#### 5. Model Training Errors

```bash
# Check if data files exist
ls -la data/*.csv

# Regenerate data if needed
python data/data_collection.py
```

### Performance Optimization

#### For Better Performance

```bash
# Install additional packages for better performance
pip install ujson orjson  # Faster JSON processing
pip install uvloop  # Faster event loop (Linux/macOS only)

# Use production server
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

#### For Development

```bash
# Enable auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Enable debug mode
export DEBUG=true
python main.py
```

## 📊 Data Verification

### Check Generated Data

```bash
# Check data files
ls -la data/

# Verify data quality
python -c "
import pandas as pd
import json

# Check air quality data
aq_df = pd.read_csv('data/synthetic_air_quality_delhi_*.csv')
print(f'Air quality records: {len(aq_df)}')
print(f'Stations: {aq_df.station_name.nunique()}')

# Check waste data
waste_df = pd.read_csv('data/waste_readings_delhi_*.csv')
print(f'Waste records: {len(waste_df)}')
print(f'Bins: {waste_df.bin_id.nunique()}')

# Check summary
with open('data/dataset_summary.json', 'r') as f:
    summary = json.load(f)
print('Dataset summary:', summary)
"
```

### Verify Model Performance

```bash
# Check model files
ls -la models/

# Test model predictions
python -c "
import tensorflow as tf
import joblib
import numpy as np

# Test LSTM
lstm_model = tf.keras.models.load_model('models/lstm_air_quality.h5')
test_input = np.random.random((1, 24, 9))
prediction = lstm_model.predict(test_input)
print(f'LSTM prediction shape: {prediction.shape}')

# Test Random Forest
rf_model = joblib.load('models/rf_waste_prediction.pkl')
test_input = np.random.random((1, 12))
prediction = rf_model.predict(test_input)
print(f'RF prediction: {prediction[0]}')
"
```

## 🚀 Deployment Options

### Free Cloud Deployment

#### Option 1: Render (Recommended)

1. Push code to GitHub
2. Connect GitHub repo to Render
3. Deploy backend and frontend separately
4. Use Render's free PostgreSQL and Redis

#### Option 2: Railway

1. Push code to GitHub
2. Connect to Railway
3. Deploy full-stack application
4. Use Railway's free database

#### Option 3: Vercel + Supabase

1. Deploy frontend to Vercel
2. Deploy backend to Railway/Render
3. Use Supabase for database
4. All services have free tiers

### Local Production Setup

```bash
# Install production dependencies
pip install gunicorn uvicorn[standard]

# Create production config
cp .env .env.production

# Start production server
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📈 Monitoring and Maintenance

### Health Checks

```bash
# Create health check script
cat > health_check.py << 'EOF'
import requests
import time

def check_backend():
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        return response.status_code == 200
    except:
        return False

def check_frontend():
    try:
        response = requests.get('http://localhost:3000', timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print(f"Backend: {'✅' if check_backend() else '❌'}")
    print(f"Frontend: {'✅' if check_frontend() else '❌'}")
EOF

# Run health check
python health_check.py
```

### Log Monitoring

```bash
# Check backend logs
tail -f backend/logs/app.log

# Check frontend logs (in browser console)
# Open Developer Tools > Console
```

## 🎯 Next Steps

### For Students

1. **Customize the Dashboard**: Add your own visualizations
2. **Extend AI Models**: Try different algorithms
3. **Add Real Data**: Integrate actual Delhi data sources
4. **Mobile App**: Create React Native version
5. **Voice Integration**: Add text-to-speech features

### For Hackathon

1. **Demo Preparation**: Create presentation slides
2. **Video Recording**: Record 3-minute demo
3. **Documentation**: Update README with your changes
4. **Deployment**: Deploy to free cloud platform
5. **Submission**: Submit with all required materials

## 📞 Support

### Getting Help

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check `/docs` folder for detailed guides
- **Community**: Ask questions in project discussions

### Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://reactjs.org/docs/
- **TensorFlow Docs**: https://www.tensorflow.org/
- **Scikit-learn Docs**: https://scikit-learn.org/

---

**🎉 Congratulations! You now have a fully functional Smart Delhi system running locally.**

_This setup uses only free resources and can be deployed to free cloud platforms for hackathon submission._
