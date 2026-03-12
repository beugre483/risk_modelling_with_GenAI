import os
import time
import random
import unicodedata
from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv

load_dotenv()


def _is_rate_limit(e: Exception) -> bool:
    msg = str(e).lower()
    return "429" in msg or "rate_limit" in msg or "rate limit" in msg


class LLMClient:
    def __init__(self, model_name="mistral-small-latest", max_retries: int = 5, base_delay: float = 2.0):
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("MISTRAL_API_KEY manquante dans l'environnement.")

        self.llm = ChatMistralAI(
            model=model_name,
            api_key=api_key,
            temperature=0
        )
        self.max_retries = max_retries
        self.base_delay = base_delay

    def _retry(self, func, *args, **kwargs):
        """Exécute func avec retry + backoff exponentiel sur rate limit."""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if _is_rate_limit(e) and attempt < self.max_retries - 1:
                    delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"⏳ Rate limit Mistral — attente {delay:.1f}s (tentative {attempt + 1}/{self.max_retries})")
                    time.sleep(delay)
                else:
                    raise

    def invoke(self, prompt):
        return self._retry(self.llm.invoke, prompt)

    def invoke_structured(self, prompt, schema):
        """
        Appel avec structured output.
        Renvoie TOUJOURS un objet du type 'schema' ou lève une exception.
        """
        try:
            structured_llm = self.llm.with_structured_output(schema)
            result = self._retry(structured_llm.invoke, prompt)

            if result is None:
                raise ValueError("Le LLM a renvoyé un résultat vide.")
            return result

        except Exception as e:
            print(f"[LLMClient Error] Erreur lors de l'extraction structurée : {e}")
            raise RuntimeError(f"Échec de la génération structurée : {str(e)}")


llm_client_services = None


def get_llm() -> LLMClient:
    """Récupère l'instance unique du service."""
    global llm_client_services

    if llm_client_services is None:
        llm_client_services = LLMClient()

    return llm_client_services