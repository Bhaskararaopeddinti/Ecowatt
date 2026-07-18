# EcoWatt AI - AI-Powered Energy Leak & Efficiency Advisor

An intelligent web application that helps households and small businesses understand their electricity usage, detect energy leaks, identify appliance-wise consumption, predict electricity bills, and receive personalized AI recommendations to reduce electricity costs.

## Features

### Core Features
- **Smart Meter Simulation**: Generate realistic smart meter data or upload CSV files
- **AI Appliance Detection**: Identify which appliances are consuming electricity using ML
- **Energy Leak Detection**: Detect phantom loads, standby power, spikes, and faulty appliances
- **Bill Prediction**: Predict daily, weekly, and monthly electricity bills with confidence scores
- **Recommendation Engine**: Get personalized energy-saving recommendations ranked by savings
- **AI Chatbot**: Ask questions about your energy usage and get intelligent answers
- **Carbon Footprint Tracking**: Monitor your environmental impact
- **PDF Reports**: Generate detailed energy consumption reports

### Dashboard
- Today's electricity usage
- Monthly usage statistics
- Current and predicted bills
- Energy score (0-100)
- Carbon footprint
- Money saved
- Active alerts
- Interactive charts with Chart.js

## Technology Stack

### Backend
- **Python 3.8+**
- **FastAPI** - Modern, fast web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **SQLite** - Database (MVP) / PostgreSQL ready for production
- **Scikit-learn** - Machine learning library
- **Pandas & NumPy** - Data manipulation
- **JWT** - Authentication
- **Passlib** - Password hashing

### Frontend
- **HTML5**
- **CSS3** (Custom, no frameworks)
- **Vanilla JavaScript**
- **Chart.js** - Data visualization

### Machine Learning
- **Random Forest** - Appliance detection
- **Isolation Forest** - Anomaly detection
- **Linear Regression** - Bill prediction
- **Scikit-learn Pipelines** - ML workflows

## Project Structure

```
EcoWattAI/
├── frontend/
│   ├── index.html          # Landing page
│   ├── login.html          # Authentication
│   ├── dashboard.html     # Main dashboard
│   ├── analysis.html      # Detailed analysis
│   ├── reports.html       # PDF reports
│   ├── chatbot.html       # AI chatbot
│   ├── settings.html      # User settings
│   ├── css/
│   │   ├── style.css      # Main styles
│   │   ├── dashboard.css  # Dashboard styles
│   │   └── responsive.css # Responsive & dark mode
│   ├── js/
│   │   ├── app.js         # Landing page scripts
│   │   ├── auth.js        # Authentication
│   │   ├── api.js         # API utilities
│   │   ├── dashboard.js   # Dashboard logic
│   │   ├── analysis.js    # Analysis logic
│   │   ├── reports.js     # Reports logic
│   │   ├── chatbot.js     # Chatbot logic
│   │   └── settings.js    # Settings logic
│   └── assets/
│       ├── images/
│       └── icons/
└── backend/
    ├── main.py            # FastAPI application
    ├── database.py        # Database configuration
    ├── models.py          # SQLAlchemy models
    ├── schemas.py         # Pydantic schemas
    ├── requirements.txt    # Python dependencies
    ├── routers/
    │   ├── auth.py        # Authentication endpoints
    │   ├── energy.py      # Energy data endpoints
    │   ├── appliances.py  # Appliance endpoints
    │   ├── alerts.py      # Alert endpoints
    │   ├── predictions.py # Prediction endpoints
    │   ├── recommendations.py # Recommendation endpoints
    │   ├── dashboard.py   # Dashboard endpoints
    │   ├── chatbot.py     # Chatbot endpoints
    │   ├── reports.py     # Report endpoints
    │   └── settings.py    # Settings endpoints
    ├── services/
    │   ├── smart_meter_simulator.py # Data simulation
    │   └── __init__.py
    ├── ai/
    │   ├── appliance_detection.py  # AI Module 1
    │   ├── energy_leak_detection.py # AI Module 2
    │   ├── bill_prediction.py       # AI Module 3
    │   ├── recommendation_engine.py # AI Module 4
    │   ├── chatbot.py              # AI Module 5
    │   └── __init__.py
    └── utils/
        ├── auth.py         # Authentication utilities
        └── __init__.py
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set environment variables (optional):
```bash
export SECRET_KEY="your-secret-key-here"
export DATABASE_URL="sqlite:///./ecowatt.db"  # or PostgreSQL URL
```

5. Run the application:
```bash
python main.py
```

The backend will start on `http://localhost:8000`

### Frontend Setup

The frontend is static HTML/CSS/JavaScript. Simply open the `frontend/index.html` file in a web browser, or serve it using a web server.

For development, you can use Python's built-in server:
```bash
cd frontend
python -m http.server 3000
```

Then access the application at `http://localhost:3000`

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

### Main API Endpoints

#### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user
- `PUT /api/auth/me` - Update user profile

#### Energy Data
- `POST /api/energy/data` - Create energy data entry
- `GET /api/energy/data` - Get energy data
- `GET /api/energy/data/recent` - Get recent energy data
- `POST /api/energy/simulate` - Simulate smart meter data

#### Appliances
- `POST /api/appliances/` - Create appliance
- `GET /api/appliances/` - Get all appliances
- `POST /api/appliances/detect` - Detect appliances using AI

#### Alerts
- `POST /api/alerts/` - Create alert
- `GET /api/alerts/` - Get alerts
- `POST /api/alerts/detect` - Detect energy leaks using AI

#### Predictions
- `POST /api/predictions/generate/daily` - Generate daily prediction
- `POST /api/predictions/generate/weekly` - Generate weekly prediction
- `POST /api/predictions/generate/monthly` - Generate monthly prediction

#### Recommendations
- `POST /api/recommendations/generate` - Generate AI recommendations
- `GET /api/recommendations/` - Get recommendations

#### Chatbot
- `POST /api/chatbot/ask` - Ask the AI chatbot a question
- `GET /api/chatbot/history` - Get chat history

#### Reports
- `POST /api/reports/generate/{type}` - Generate report
- `GET /api/reports/download/{id}` - Download report

#### Settings
- `GET /api/settings/` - Get user settings
- `PUT /api/settings/` - Update user settings

## Usage

### Getting Started

1. **Sign Up**: Create an account on the landing page
2. **Simulate Data**: Use the "Simulate Data" button to generate sample smart meter data
3. **View Dashboard**: Explore your energy usage statistics and charts
4. **Run Analysis**: Use the Analysis page to get detailed insights
5. **Detect Appliances**: Let AI identify which appliances are consuming electricity
6. **Check for Leaks**: Run energy leak detection to find wastage
7. **Get Recommendations**: Receive personalized energy-saving tips
8. **Chat with AI**: Ask questions about your energy usage
9. **Generate Reports**: Download PDF reports for your records

### Smart Meter Data

The application includes a smart meter simulator that generates realistic data. You can also upload your own CSV files with the following columns:
- timestamp
- voltage (V)
- current (A)
- power (W)
- energy (kWh)
- frequency (Hz)
- power_factor

## AI Modules

### Module 1: Appliance Detection
Uses Random Forest classification to identify appliances based on power consumption patterns. Supports detection of:
- Air Conditioner
- Water Heater
- Microwave
- Washing Machine
- Refrigerator
- Motor
- TV
- Laptop
- Fan
- Lights

### Module 2: Energy Leak Detection
Uses Isolation Forest for anomaly detection to identify:
- Phantom load
- High standby power
- Energy spikes
- Faulty appliances
- Long-running devices
- Abnormal usage patterns

### Module 3: Bill Prediction
Uses Linear Regression and ensemble methods to predict:
- Tomorrow's bill
- Weekly bill
- Monthly bill
- With confidence scores and reasoning

### Module 4: Recommendation Engine
Generates personalized recommendations based on:
- Current consumption patterns
- Appliance efficiency
- Historical data
- User behavior
- Ranked by potential savings

### Module 5: AI Chatbot
Intelligent assistant that can answer questions about:
- Why bills are high
- Which appliances use most electricity
- How to reduce bills
- What to replace first
- Potential savings
- Carbon footprint
- Energy leaks

## Carbon Footprint

The application calculates your carbon footprint based on:
- Default factor: 0.85 kg CO2 per kWh (configurable in settings)
- Daily, monthly, and yearly emissions
- Trees required to offset your footprint
- Visual charts and trends

## Database Schema

### Tables
- **users** - User accounts and profiles
- **energy_data** - Smart meter readings
- **appliances** - Appliance information
- **alerts** - Energy leak and anomaly alerts
- **predictions** - Bill predictions
- **recommendations** - AI-generated recommendations
- **reports** - Generated PDF reports
- **chat_history** - Chatbot conversation history
- **settings** - User preferences and settings

## Security

- JWT authentication for all API endpoints
- Password hashing with bcrypt
- Input validation with Pydantic
- CORS configuration
- SQL injection prevention with SQLAlchemy ORM
- Rate limiting (can be added)

## Future Enhancements

- Solar ROI Calculator
- IoT Smart Meter Integration
- Voice Assistant
- Mobile App (React Native)
- Email Alerts
- WhatsApp Alerts
- SMS Notifications
- Predictive Maintenance
- Government Electricity Subsidy Suggestions
- Real-time WebSocket updates
- Multi-language support

## Contributing

This is a demonstration project. For production use, consider:
- Adding comprehensive error handling
- Implementing proper logging
- Adding unit and integration tests
- Setting up CI/CD pipeline
- Configuring production database (PostgreSQL)
- Adding Redis for caching
- Implementing rate limiting
- Adding monitoring and analytics

## License

This project is for educational and demonstration purposes.

## Support

For issues or questions, please refer to the API documentation at `/docs` endpoint when the backend is running.

## Acknowledgments

- FastAPI framework
- Scikit-learn ML library
- Chart.js visualization library
- All open-source contributors
