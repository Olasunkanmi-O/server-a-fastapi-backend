# app/providers/base.py
from abc import ABC, abstractmethod

class LLMProviderInterface(ABC):
    @abstractmethod
    def summarize_business_health(self, query: str, transactions: list) -> str:
        pass