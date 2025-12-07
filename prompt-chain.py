
import os
import asyncio
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "openai/gpt-4o-mini"
# Helper function
async def call_openrouter(prompt):
    """Call OpenRouter API with the given prompt."""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "model": MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.5,
                "max_tokens": 200,
            }
            
            async with session.post(
                f"{BASE_URL}/chat/completions",
                json=payload,
                headers=headers
            ) as response:
                if response.status != 200:
                    error_data = await response.text()
                    print(f"Error calling OpenRouter: {error_data}")
                    return "Error: Unable to process this step."
                
                data = await response.json()
                return data["choices"][0]["message"]["content"].strip()
                
    except Exception as error:
        print(f"Error calling OpenRouter: {str(error)}")
        return "Error: Unable to process this step."
# Run the chain
async def run_prompt_chain(customer_query):
    """Run the complete prompt chain for customer query processing."""
    outputs = []

    # 1. Interpret the customer's intent
    interpret_intent = f"""
    You are a helpful banking assistant.
    Analyze the following customer query and describe what the customer wants or is reporting.
    Query: "{customer_query}"
    """
    intent = await call_openrouter(interpret_intent)
    outputs.append(intent)

    # 2. Mapping the query for possible categories
    map_categories = f"""
    Based on this intent: "{intent}",
    Suggest one or more possible categories from the following list that might apply:
    [Account Opening, Billing Issue, Account Access, Transaction Inquiry, Card Services, Account Statement, Loan Inquiry, General Information].
    """
    possible_categories = await call_openrouter(map_categories)
    outputs.append(possible_categories)

    # 3. Choose the most appropriate category
    choose_categories = f"""
    From these possible categories: "{possible_categories}",
    Choose the single most appropriate one that best matches the intent: "{intent}".
    """
    best_category = await call_openrouter(choose_categories)
    outputs.append(best_category)

    # 4. Extracting additional details
    extract_details = f"""
    From the original query "{customer_query}", extract any extra useful information like transaction date, amount, card type, or account number (if mentioned).
    """
    extra_details = await call_openrouter(extract_details)
    outputs.append(extra_details)

    # 5. Generate response
    generate_response = f"""
    Write a short, polite, and professional response to the customer based on:
    - Intent: {intent}
    - Category: {best_category}
    - Details: {extra_details}
    """
    response = await call_openrouter(generate_response)
    outputs.append(response)

    return outputs
