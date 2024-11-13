# AgritechTZ - Crop Prices Scraper and API

---

AgritechTZ is a FastAPI-based application designed to scrape, store, and serve daily crop price data. This project retrieves crop prices from Viwanda’s data sources, stores them in a PostgreSQL database, and provides a REST API for querying the stored data.

## Table of Contents

  1. [Requirements](#requirements)
  2. [Setup](#setup)
  3. [Environment Variables](#environment-variables)
  4. [Database Migrations](#database-migrations)
  5. [Running the Application](#running-the-application)
  6. [API Endpoints](#api-endpoints)
  7. [Scheduler for Daily Updates](#run-scheduler)
  8. [Testing](#testing)
  9. [Contributing](#contributing)
  10. [License](#license)

## Requirements

    Python 3.11 (or higher)
    PostgreSQL for the database
    Docker (optional, for containerized deployment)

## Setup

Follow the following steps to setup and get the application running on your local (development) environment.

### Clone the repository:

```sh
git clone https://github.com/yourusername/agritechtz.git
cd agritechtz
```

### Create a virtual environment:

```sh
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

### Install dependencies:

```sh
poetry install
```

## Environment Variables

Create a .env file in the root directory with the following variables:

```sh
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/agritechtz
BASE_URL=https://viwanda.example.com  # Base URL for crop price data
API_KEY=your_api_key  # Optional: if the source requires an API key
SCHEDULER_INTERVAL=24h  # Interval for running the scheduler
```

> Note: Replace user, password, and localhost:5432/agritechtz with your actual PostgreSQL credentials.

### Database Migrations

Use Alembic to handle database migrations. To apply migrations, run:

```sh
alembic upgrade head
```

To generate a new migration based on changes to the models:

```sh
alembic revision --autogenerate -m "Migration message"
```

### Running the Application

#### Start FastAPI:

```sh
uvicorn agritechtz.main:app --reload
```

This will run the FastAPI app on [http://127.0.0.1:8000](http://127.0.0.1:8000).

#### Run Scheduler:

The scheduler.py script is used to run periodic jobs to scrape and update the crop price data in the database.

The scheduler frequency will honor the interval you've used in your `.env` file above

```sh
python agritechtz/scheduler.py
```

### API Endpoints

The API allows querying the crop price data by various filters. Here are some example endpoints:

```sh
GET /api/v1/crop-prices/: Retrieve crop prices with optional filters for date, region, and district
```

The full API documentation is available at http://127.0.0.1:8000/docs.
Scheduler for Daily Updates

The scheduler is configured to run daily_updates_job() every 24 hours (midnight). This job scrapes the crop prices from Viwanda's PDF files and stores them in the PostgreSQL database.

To configure the frequency, adjust the SCHEDULER_INTERVAL variable in your .env file.

## Testing

### Run tests:

```sh
pytest
```

#### Code Coverage:

```sh
pytest --cov=agritechtz
```

## Contributing

Contributions are welcome! Please submit a pull request with any enhancements, bug fixes, or new features.

Fork the repository
Create a feature branch: git checkout -b feature-branch-name
Commit your changes: git commit -m 'Add feature'
Push to the branch: git push origin feature-branch-name
Open a pull request

## License

This project is licensed under the MIT License. See the LICENSE file for more information.
