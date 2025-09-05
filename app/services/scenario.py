from llama_cpp import Llama

llm = Llama(
    model_path="path/to/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
    n_ctx=4096,
    n_threads=8,
    n_gpu_layers=0
)

SOURCE_MODEL = "Mistral-7B-Q4"

def call_mistral(prompt: str) -> str:
    response = llm(prompt, max_tokens=512)
    return response["choices"][0]["text"]

async def generate_scenario(full_prompt: str) -> dict:
    response = call_mistral(full_prompt)
    return {
        "prompt": full_prompt,
        "response": response,
        "source_model": SOURCE_MODEL,
        "confidence": None  # Placeholder for future scoring
    }