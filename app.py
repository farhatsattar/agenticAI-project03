

from dotenv import load_dotenv
import os
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
import streamlit as st




# load  environment from varibles .env file

load_dotenv()
# accessing environment variables

GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

import requests
@tool
def calculator(expression: str) -> float:
    """
    Evaluate a mathematical expression and return the result.

    Parameters:
    expression (str): A string containing the mathematical expression to evaluate.

    Returns:
    float: The result of the evaluated expression.

    Examples:
    >>> evaluate_expression("2 + 3 * 4")
    14.0
    >>> evaluate_expression("(10 / 2) + 8")
    13.0

    Note:
    - This function uses Python's `eval()` to calculate the result.
    - Ensure the input is sanitized to avoid malicious code execution.
    """
    try:
        # Evaluate the expression safely
        result = eval(expression, {"__builtins__": {}})
        return float(result)
    except Exception as e:
        print(f"Error evaluating expression: {e}")
        return None


@tool
def get_stock_price(symbol: str) -> str:
    """Fetches the current stock price of a company based on its stock symbol using the Polygon API.

    Args:
        symbol (str): The stock symbol of the company (e.g., 'AAPL' for Apple, 'GOOGL' for Google).

    Returns:
        str: A message containing the current stock price of the company.

    Raises:
        HTTPError: If the HTTP request to the stock API fails (e.g., 404 or 500 status).
        RequestException: If there is an issue with the request itself (e.g., connection error).
        Exception: For any other unexpected errors during the execution of the function.

    """
    api_key = "lvLE3xhAVp41AGEi_Dz3J59FBMIrUKiN"  # Replace this with your actual secret API key from Polygon
    url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev"  # Polygon endpoint for previous close price

    try:
        # Send a GET request with the API key
        response = requests.get(url, params={'apiKey': api_key})
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx, 5xx)

        # Assuming the data contains 'close' in the response for the last closing price
        data = response.json()
        price = data.get('results', [{}])[0].get('c')  # 'c' is the closing price

        if price:
            return f"Tool used: get_stock_price\n get_stock_price tool is used to find The current price of {symbol} is ${price}"
        else:
            return f"Error: Could not retrieve stock data for {symbol}.\nTool used: get_stock_price"

    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}\nTool used: get_stock_price"
    except requests.exceptions.RequestException as req_err:
        return f"Request error occurred: {req_err}\nTool used: get_stock_price"
    except Exception as err:
        return f"An unexpected error occurred: {err}\nTool used: get_stock_price"

tools = [calculator,get_stock_price]



llm = ChatGoogleGenerativeAI(model = "gemini-2.0-flash-exp" , api_key=GOOGLE_API_KEY)


agent = initialize_agent(tools, llm , agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION )




st.title("Gemini calling tool")
st.write("welcome to app")
user_input = st.text_input("Enter your query")

if st.button("submit"):
    st.sidebar("calculator")
    response = agent.invoke(user_input)
    st.write(response["output"])

