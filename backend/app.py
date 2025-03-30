from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Set up Google Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure the Gemini API if key is available
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class QueryRequest(BaseModel):
    query: str
    schema: str = ""

@app.post("/api/translate")
async def translate_to_sql(request: QueryRequest):
    try:
        # Check if we have an API key
        if not GEMINI_API_KEY:
            # Fall back to mock response if no API key
            sql_query = generate_mock_sql(request.query, request.schema)
        else:
            # Configure the model
            generation_config = {
                "temperature": 0.1,  # Low temperature for more deterministic output
                "max_output_tokens": 256,
                "top_p": 0.8,
            }
            
            # Create the prompt for the model
            prompt = f"""
            You are a SQL expert. Translate the following natural language query into SQL code.
            Database Schema: {request.schema}
            
            Query: {request.query}
            
            Return only the SQL code and nothing else. Do not include any explanations or markdown formatting.
            """
            
            # Call Gemini API
            model = genai.GenerativeModel(
                model_name="gemini-1.5-pro",
                generation_config=generation_config
            )
            response = model.generate_content(prompt)
            
            # Extract SQL query from response
            sql_query = response.text.strip()
        
        # Generate mock data based on the query
        mock_data = generate_mock_data(request.query)
        
        return {
            "sql_query": sql_query,
            "data": mock_data,
            "visualizations": generate_visualizations(mock_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_mock_sql(query, schema):
    """Generate mock SQL based on the query"""
    query_lower = query.lower()
    
    if "sales" in query_lower and "month" in query_lower:
        return "SELECT Month, SUM(sales) as Total_Sales, SUM(profit) as Total_Profit FROM sales WHERE year = 2023 GROUP BY Month ORDER BY Month;"
    
    elif "top 5" in query_lower and "customer" in query_lower:
        return "SELECT Customer_Name, COUNT(order_id) as Total_Orders, SUM(order_amount) as Total_Spent FROM orders JOIN customers ON orders.customer_id = customers.id GROUP BY Customer_Name ORDER BY Total_Spent DESC LIMIT 5;"
    
    elif "average" in query_lower and "category" in query_lower:
        return "SELECT product_category, AVG(order_amount) as Average_Order_Value FROM orders JOIN products ON orders.product_id = products.id GROUP BY product_category ORDER BY Average_Order_Value DESC;"
    
    elif "employee" in query_lower and "hired" in query_lower:
        return "SELECT employee_name, hire_date, department FROM employees WHERE hire_date >= DATE_SUB(CURRENT_DATE, INTERVAL 6 MONTH) ORDER BY hire_date DESC;"
    
    else:
        return "SELECT * FROM table WHERE condition = value LIMIT 10;"

def generate_mock_data(query):
    """Generate mock data based on the query type for demonstration"""
    if "sales" in query.lower():
        return {
            "columns": ["Month", "Sales", "Profit"],
            "data": [
                ["Jan", 1000, 200],
                ["Feb", 1200, 240],
                ["Mar", 1100, 220],
                ["Apr", 1300, 260],
                ["May", 1400, 280],
                ["Jun", 1500, 300]
            ]
        }
    elif "customer" in query.lower():
        return {
            "columns": ["Customer", "Orders", "Total Spent"],
            "data": [
                ["John Doe", 5, 500],
                ["Jane Smith", 3, 300],
                ["Bob Johnson", 8, 800],
                ["Alice Brown", 12, 1200],
                ["Charlie Davis", 7, 700]
            ]
        }
    else:
        return {
            "columns": ["Category", "Count"],
            "data": [
                ["Category A", 10],
                ["Category B", 15],
                ["Category C", 8],
                ["Category D", 12]
            ]
        }

def generate_visualizations(data):
    """Generate visualization options based on the data"""
    columns = data["columns"]
    
    # Determine suitable visualization types based on data structure
    visualizations = []
    
    # If we have at least two columns
    if len(columns) >= 2:
        visualizations.append({
            "type": "bar",
            "title": f"{columns[0]} vs {columns[1]}",
            "x_axis": columns[0],
            "y_axis": columns[1]
        })
        
        visualizations.append({
            "type": "line",
            "title": f"{columns[0]} vs {columns[1]} Trend",
            "x_axis": columns[0],
            "y_axis": columns[1]
        })
    
    # If we have at least three columns
    if len(columns) >= 3:
        visualizations.append({
            "type": "scatter",
            "title": f"{columns[1]} vs {columns[2]}",
            "x_axis": columns[1],
            "y_axis": columns[2],
            "size": columns[0]
        })
    
    return visualizations

if __name__ == '__main__':
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)
