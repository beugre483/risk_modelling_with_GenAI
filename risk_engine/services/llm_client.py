import os
import unicodedata
from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv


load_dotenv()

class LLMClient:
    def __init__(self, model_name="mistral-small-latest"):
        # On récupère la clé
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("MISTRAL_API_KEY manquante dans l'environnement.")
        
        self.llm = ChatMistralAI(
            model=model_name,
            api_key=api_key,
            temperature=0
        )

    def invoke(self, prompt):
        return self.llm.invoke(prompt)
    
    def invoke_structured(self, prompt, schema):
        """
        Appel avec structured output. 
        Renvoie TOUJOURS un objet du type 'schema' ou lève une exception.
        """
        try:
            structured_llm = self.llm.with_structured_output(schema)
            result = structured_llm.invoke(prompt)
            
            if result is None:
                raise ValueError("Le LLM a renvoyé un résultat vide.")
            return result

        except Exception as e:

            print(f"[LLMClient Error] Erreur lors de l'extraction structurée : {e}")
            raise RuntimeError(f"Échec de la génération structurée : {str(e)}")
        
        

llm_client_services=None

def get_llm():
    "recupère linstance unique du service"
    global llm_client_services
    
    if llm_client_services is None:
         llm_client_services= LLMClient()
         
    return llm_client_services