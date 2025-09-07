from app.providers.google_provider import GoogleProvider

provider = GoogleProvider()
print("Model:", provider.model_name)
response = provider.generate_response("Summarize this transaction")
print(response)
