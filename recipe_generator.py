import sys
import os
import json
from openai import AzureOpenAI
import azureopenai
from app_config import AZURE_OPENAI_API_KEY, AZURE_ENDPOINT, AZURE_API_VERSION, DEPLOYED_MODEL_NAME
from azure.identity import DefaultAzureCredential, get_bearer_token_provider


class RecipeGenerator:
    def __init__(self, api_key):
        self.api_key = AZURE_OPENAI_API_KEY
        self.api_version=AZURE_API_VERSION,
        self.api_base=AZURE_ENDPOINT
        self.api_type = "azure"
        self.deployment_name = DEPLOYED_MODEL_NAME

    def generate(self, recipe):
        prompts = [{"role": "user", "content": json.dumps(recipe)}]
        instruction = {
            "role": "system",
            "content": "Take the recipes information and generate a recipe with a mouthwatering intro and a step by step guide."
        }
        prompts.append(instruction)
        token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")
        client = AzureOpenAI(
            api_version=self.api_version,
            azure_endpoint=self.api_base,
            azure_ad_token_provider=token_provider,
        )
        generated_content = client.chat.completions.create(
            model=self.deployment_name,  # gpt-35-instant
            messages=prompts,
            max_tokens=1000
        )        
        return generated_content.choices[0].message.content