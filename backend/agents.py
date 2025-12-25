import os
import google.generativeai as genai
import httpx
from groq import Groq
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()

class Agent:
    def __init__(self, name, model_id):
        self.name = name
        self.model_id = model_id

    async def generate(self, prompt: str) -> str:
        raise NotImplementedError

class GeminiAgent(Agent):
    def __init__(self):
        super().__init__("Chairman (Gemini)", "gemini-1.5-flash-001")
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel(self.model_id)

    async def generate(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error from {self.name}: {str(e)}"

class MistralAgent(Agent):
    def __init__(self):
        super().__init__("Council Member 1 (Mistral)", "mistral-small-latest")
        self.client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

    async def generate(self, prompt: str) -> str:
        try:
            response = self.client.chat.complete(
                model=self.model_id,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error from {self.name}: {str(e)}"

class GroqAgent(Agent):
    def __init__(self, name, model_id):
        super().__init__(name, model_id)
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    async def generate(self, prompt: str) -> str:
        try:
            completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model_id,
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Error from {self.name}: {str(e)}"

class HuggingFaceAgent(Agent):
    """Free and open-source model via Hugging Face Inference API"""
    def __init__(self):
        super().__init__("Council Member 4 (Llama 3.2)", "meta-llama/Llama-3.2-3B-Instruct")
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model_id}"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    async def generate(self, prompt: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    json={"inputs": prompt, "parameters": {"max_new_tokens": 500}}
                )
                response.raise_for_status()
                result = response.json()
                
                # Handle different response formats from Hugging Face
                if isinstance(result, list) and len(result) > 0:
                    if "generated_text" in result[0]:
                        return result[0]["generated_text"]
                    elif "text" in result[0]:
                        return result[0]["text"]
                elif isinstance(result, dict):
                    if "generated_text" in result:
                        return result["generated_text"]
                    elif "text" in result:
                        return result["text"]
                
                return str(result)
        except Exception as e:
            return f"Error from {self.name}: {str(e)}"

