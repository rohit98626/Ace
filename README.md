# SQL GPT Backend

This is the backend service for the SQL GPT application, which translates natural language questions into SQL queries using Google's Gemini AI.

## Prerequisites

- Python 3.9+
- Gemini API key (from Google AI Studio)

## Installation

1. Clone the repository and navigate to the backend directory:

```bash
cd backend
```

2. Create a virtual environment:

```bash
python -m venv venv
```

3. Activate the virtual environment:

- On Windows:
```bash
venv\Scripts\activate
```

- On macOS/Linux:
```bash
source venv/bin/activate
```

4. Install the dependencies:

```bash
pip install -r requirements.txt
```

5. Create a `.env` file in the backend directory with your Gemini API key:

```
GEMINI_API_KEY=your_gemini_api_key_here
FLASK_ENV=development
PORT=5000
```

## Running the Server

Start the development server:

```bash
python app.py
```

The API will be available at `http://localhost:5000`.

## API Endpoints

### Health Check

```
GET /api/health
```

Returns a simple health status check to verify the API is running.

### Translate Natural Language to SQL

```
POST /api/translate
```

Translates a natural language question into a SQL query using Gemini AI.

#### Request Body

```json
{
  "query": "Show me total sales by product category for the last quarter"
}
```

#### Response

```json
{
  "query": "Show me total sales by product category for the last quarter",
  "sql": "SELECT p.category_name, SUM(s.sale_amount) as total_sales FROM sales s JOIN products p ON s.product_id = p.id WHERE s.sale_date >= DATEADD(QUARTER, -1, GETDATE()) GROUP BY p.category_name ORDER BY total_sales DESC;",
  "explanation": "This query joins the sales and products tables, filters for sales in the last quarter, groups by product category, sums the sale amounts, and orders by total sales in descending order."
}
```

## Error Handling

The API returns appropriate HTTP status codes:

- 200: Successful operation
- 400: Invalid request (missing query)
- 500: Server error

## Deployment

For production deployment, consider using Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## License

This project is licensed under the MIT License. 