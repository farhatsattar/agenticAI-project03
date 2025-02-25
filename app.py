from dotenv import load_dotenv
import os
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
import streamlit as st
import requests
import ast

# Load environment variables from .env file
load_dotenv()

# Accessing environment variables
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')

# Check if API keys are available
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set in the environment variables.")
if not POLYGON_API_KEY:
    raise ValueError("POLYGON_API_KEY is not set in the environment variables.")

@tool
def calculator(expression: str) -> float:
    """Evaluate a mathematical expression and return the result."""
    try:
        result = ast.literal_eval(expression)
        return float(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"

@tool
def get_stock_price(symbol: str) -> str:
    """Fetches the real-time stock price using the Polygon API."""
    url = f"https://api.polygon.io/v1/last/stocks/{symbol}"
    
    try:
        response = requests.get(url, params={'apiKey': POLYGON_API_KEY})
        response.raise_for_status()

        data = response.json()
        price = data.get('last', {}).get('price')

        if price:
            return f"The real-time price of {symbol} is ${price}"  
        else:
            return f"Error: Could not retrieve stock data for {symbol}"

    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except requests.exceptions.RequestException as req_err:
        return f"Request error occurred: {req_err}"
    except Exception as err:
        return f"An unexpected error occurred: {err}"

# Register tools
tools = [calculator, get_stock_price]

# Set up LangChain agent
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", api_key=GOOGLE_API_KEY)
agent = initialize_agent(tools, llm, agent_type=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION)

# Streamlit UI
st.sidebar.title("App Options 🛠️")
selected_tool = st.sidebar.selectbox("Choose a tool", ("Calculator 🧮", "Get Stock Price 📈"))

st.sidebar.write("### Enter your query:")
expression = st.sidebar.text_input("Enter input:")
submit_button = st.sidebar.button("Submit 🚀")

# Main content
st.title("Gemini Calling Tool 🤖✨")
st.write("Welcome to the AI-powered tool for quick calculations and stock updates! 🚀")

# Process input on button click
if submit_button:
    if selected_tool == "Calculator 🧮" and expression:
        response = agent.invoke(f"Calculate {expression}")
    elif selected_tool == "Get Stock Price 📈" and expression:
        response = agent.invoke(f"What is the stock price of {expression}?")
    else:
        response = "Please enter a valid input."
    
    st.write(response)

