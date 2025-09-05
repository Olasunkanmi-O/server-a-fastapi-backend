from llama_cpp import Llama

# Load Mistral 7B quantized model
llm = Llama(
    model_path="path/to/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
    n_ctx=4096,
    n_threads=8,
    n_gpu_layers=0  # Set >0 if using GPU
)

# Define the model name for traceability and future swapping
SOURCE_MODEL = "Mistral-7B-Q4"

def call_mistral(prompt: str) -> str:
    response = llm(prompt, max_tokens=256)
    return response["choices"][0]["text"]

def extract_category(response: str) -> str:
    # Basic parsing logic — customize as needed
    # Example: "Category: Food & Drink"
    if "Category:" in response:
        return response.split("Category:")[1].strip().split()[0]
    return "Uncategorized"

def extract_confidence(response: str) -> float:
    # Placeholder logic — customize based on your prompt format
    if "Confidence:" in response:
        try:
            return float(response.split("Confidence:")[1].strip().split()[0])
        except ValueError:
            return 0.5
    return 1.0  # Default high confidence if not specified

async def categorize_transaction(tx: dict) -> dict:
    description = tx["description"]
    amount = tx["amount"]
    tx_id = tx["id"]

    # Construct prompt
    prompt = f"Categorize this transaction: '{description}' for £{amount}'. Return category and confidence."

    # Call Mistral
    response = call_mistral(prompt)

    # Parse response
    category = extract_category(response)
    confidence = extract_confidence(response)
    needs_review = confidence < 0.7

    return {
        "id": tx_id,
        "category": category,
        "confidence": confidence,
        "needs_review": needs_review,
        "prompt": prompt,
        "response": response,
        "source_model": SOURCE_MODEL
    }