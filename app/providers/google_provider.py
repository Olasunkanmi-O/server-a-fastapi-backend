import os
import google.generativeai as genai
from app.providers.base import LLMProviderInterface
import google.generativeai as genai






genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class GoogleProvider(LLMProviderInterface):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("models/gemini-1.5-pro")

    def categorize_transaction(self, description: str) -> str:
        prompt = f"Categorize this transaction: '{description}'. Return only the category label."
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini categorization error: {e}")
            return "Uncategorized"

    def summarize_business_health(self, query: str, transactions: list) -> str:
        tx_summary = "\n".join(
            [f"{tx['date']}: {tx['description']} (£{tx['amount']}) - {tx['category']}" for tx in transactions]
        )
        prompt = (
            f"You are a financial assistant. Based on the following transactions, answer the user's question.\n\n"
            f"User query: {query}\n\n"
            f"Transactions:\n{tx_summary}\n\n"
            f"Respond in plain English."
        )
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini summary error: {e}")
            return "Sorry, I couldn't generate a summary at this time."

    def generate_response(self, prompt: str) -> dict:
        # Gemini expects structured input, so we’ll treat the prompt as a user query
        return {
            "category": self.summarize_business_health(prompt, []),
            "confidence": 1.0
        }

