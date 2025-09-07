import google.generativeai as genai
from app.providers.base import LLMProviderInterface
from app.config import settings
from app.config import settings

class GoogleProvider(LLMProviderInterface):
    """Wrapper for Google Gemini API."""

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model_name = settings.GOOGLE_MODEL or "gemini-1.5-pro-latest"
        self.client = genai.GenerativeModel(self.model_name)
    """Wrapper for Google Gemini API."""

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model_name = settings.GOOGLE_MODEL or "gemini-1.5-pro-latest"
        self.client = genai.GenerativeModel(self.model_name)

    def categorize_transaction(self, description: str) -> str:
        prompt = f"Categorize this transaction: '{description}'. Return only the category label."
        try:
            response = self.client.generate_content(prompt)
            response = self.client.generate_content(prompt)
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
            response = self.client.generate_content(prompt)
            response = self.client.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini summary error: {e}")
            return "Sorry, I couldn't generate a summary at this time."

    def generate_response(self, prompt: str) -> dict:
        print(f"Gemini generating response for: {prompt}")
        try:
            summary = self.summarize_business_health(prompt, [])
            print(f"Gemini summary: {summary}")
            return {
                "category": summary,
                "confidence": 1.0
            }
        except Exception as e:
            print(f"Gemini generate_response error: {e}")
            return {
                "category": "Error",
                "confidence": 0.0,
                "error": str(e)
            }