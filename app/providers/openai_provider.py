import openai
from app.providers.base import LLMProviderInterface

class OpenAIProvider(LLMProviderInterface):
    def __init__(self, api_key: str):
        openai.api_key = api_key
        self.model = "gpt-4o-mini"  # Or "gpt-4", "gpt-3.5-turbo", etc.

    def summarize_business_health(self, query: str, transactions: list) -> str:
        tx_summary = "\n".join(
            [f"{tx['date']}: {tx['description']} (£{tx['amount']}) - {tx['category']}" for tx in transactions]
        )

        messages = [
            {"role": "system", "content": "You are a financial assistant."},
            {"role": "user", "content": f"User query: {query}\n\nTransactions:\n{tx_summary}"}
        ]

        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=1000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI error: {e}")
            return "Sorry, I couldn't generate a summary at this time."
