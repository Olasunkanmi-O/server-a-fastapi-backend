from app.config import settings
from app.providers.openai_provider import OpenAIProvider
#from app.providers.anthropic_provider import AnthropicProvider
#from app.providers.deepseek_provider import DeepseekProvider
from app.providers.google_provider import GoogleProvider

def get_provider(provider_name: str = settings.LLM_PROVIDER):
    if provider_name == "openai":
        return OpenAIProvider(api_key=settings.API_KEY)
    elif provider_name == "anthropic":
        return AnthropicProvider(api_key=settings.ANTHROPIC_API_KEY)
    elif provider_name == "deepseek":
        return DeepseekProvider(api_key=settings.DEEPSEEK_API_KEY)
    elif provider_name == "google":
        return GoogleProvider(api_key=settings.GEMINI_API_KEY)
    else:
        raise ValueError(f"Unsupported provider: {provider_name}")