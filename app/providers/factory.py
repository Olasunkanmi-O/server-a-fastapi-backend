from app.config import settings
from app.providers.openai_provider import OpenAIProvider
#from app.providers.anthropic_provider import AnthropicProvider
#from app.providers.deepseek_provider import DeepseekProvider
from app.providers.google_provider import GoogleProvider

def get_provider(provider_name: str):
    print(f"Factory received provider_name: {provider_name}")
    if provider_name == "openai":
        return OpenAIProvider()
    elif provider_name == "anthropic":
        return AnthropicProvider()
    elif provider_name == "deepseek":
        return DeepseekProvider()
    elif provider_name == "google":
        return GoogleProvider()
    else:
        raise ValueError(f"Unsupported provider: {provider_name}")
