import os
import sys
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

DEEPRARE_ROOT = Path(__file__).resolve().parent.parent.parent.parent

# The project root is the DeepRare/ directory
# claim-layer lives one level up at ../claim-layer/
CLAIM_LAYER_SRC = DEEPRARE_ROOT.parent / "claim-layer" / "src"
CLAIM_LAYER_ROOT = DEEPRARE_ROOT.parent / "claim-layer"

for p in [str(DEEPRARE_ROOT), str(CLAIM_LAYER_SRC), str(CLAIM_LAYER_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)


class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8001
    debug: bool = True

    openai_api_key: str = ""
    nvidia_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""
    deepseek_api_key: str = ""

    google_cse_id: str = ""
    google_cse_api_key: str = ""
    bing_subscription_key: str = ""

    exomiser_jar_path: str = ""
    exomiser_data_path: str = ""

    orphanet_knowledge_path: str = ""
    disease_embeddings_path: str = ""
    similar_cases_path: str = ""
    hpo_concept2id_path: str = ""
    hpo_embeddings_path: str = ""
    orpha_concept2id_path: str = ""
    orpha2omim_path: str = ""
    exomiser_save_path: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

AVAILABLE_MODELS = [
    {"id": "meta/llama-3.1-70b-instruct", "name": "Llama 3.1 70B (NVIDIA NIM)", "provider": "nvidia"},
    {"id": "meta/llama-3.1-405b-instruct", "name": "Llama 3.1 405B (NVIDIA NIM)", "provider": "nvidia"},
    {"id": "gpt-4o", "name": "GPT-4o", "provider": "openai"},
    {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "provider": "openai"},
    {"id": "o1", "name": "O1", "provider": "openai"},
    {"id": "o3-mini", "name": "O3 Mini", "provider": "openai"},
    {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet", "provider": "anthropic"},
    {"id": "claude-3-5-haiku-20241022", "name": "Claude 3.5 Haiku", "provider": "anthropic"},
    {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash", "provider": "google"},
    {"id": "gemini-2.0-pro", "name": "Gemini 2.0 Pro", "provider": "google"},
    {"id": "deepseek-v3-241226", "name": "DeepSeek V3", "provider": "deepseek"},
    {"id": "deepseek-r1-250120", "name": "DeepSeek R1", "provider": "deepseek"},
]

PROVIDER_KEY_MAP = {
    "nvidia": "nvidia_api_key",
    "openai": "openai_api_key",
    "anthropic": "anthropic_api_key",
    "google": "google_api_key",
    "deepseek": "deepseek_api_key",
}
