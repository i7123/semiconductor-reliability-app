# Semiconductor Reliability Calculator

A comprehensive web application for semiconductor reliability calculations with usage tracking and authorization.

## Features

### Calculators Available
- **MTBF Calculator**: Mean Time Between Failures calculation
- **Arrhenius Model Calculator**: Temperature acceleration factors
- **Test Sample Size Calculator**: Required sample sizes for reliability demonstration testing

### Usage Control
- Free tier: 10 calculations per day
- User registration and authentication
- Premium upgrade for unlimited access
- Real-time usage tracking

## Setup Instructions

### Prerequisites
- Python 3.7+ installed
- Web browser for frontend

### Installation

1. **Navigate to the backend directory:**
   ```bash
   cd semiconductor-reliability-app/backend
   ```

2. **Set up virtual environment and install dependencies:**
   ```bash
   ./activate.sh
   ```
   
   Or manually:
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Run the backend server:**
   ```bash
   python -m app.main
   ```
   
   The API will be available at `http://localhost:8000`

4. **Open the frontend:**
   Open `frontend/index.html` in your web browser

## Usage

1. **Select a Calculator**: Choose from available reliability calculators
2. **Enter Parameters**: Fill in the required input fields
3. **Calculate**: Click the Calculate button to get results
4. **View Results**: Results are displayed in a formatted table

### Test Sample Size Calculator

This calculator helps determine the required sample size for reliability demonstration testing:

- **Success Run Testing**: Zero failures allowed
- **Time-Terminated Testing**: Fixed test duration
- **Failure-Terminated Testing**: Test until specific number of failures

Input parameters:
- Target reliability (0-1)
- Confidence level (80%, 90%, 95%, 99%)
- Test type and duration
- Maximum allowed failures

## API Endpoints

### Calculators
- `GET /api/calculators/` - List all available calculators
- `GET /api/calculators/{id}/info` - Get calculator details
- `POST /api/calculators/calculate/{id}` - Perform calculation
- `GET /api/calculators/calculate/{id}/example` - Get example inputs

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/usage` - Get usage status
- `POST /api/auth/upgrade` - Upgrade to premium

## Database

The app uses SQLite by default. The database file `semiconductor_calc.db` will be created automatically.

Tables:
- `users` - User accounts and premium status
- `usage_logs` - Calculation usage tracking
- `auth_tokens` - Authentication tokens

## Development

To add new calculators:

1. Create a new calculator class in `app/calculators/`
2. Inherit from `BaseCalculator`
3. Implement `info` property and `calculate` method
4. Register in `app/calculators/__init__.py`

## Security Features

- Input validation for all calculations
- Rate limiting (10 requests/day for free users)
- JWT token authentication
- SQL injection protection
- CORS enabled for frontend integration

## License

This project is for educational and research purposes.