import requests
from urllib.parse import quote
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class PromptOptimizerInput(BaseModel):
    image_desc: str = Field(..., description="Image description provided by the customer.")

class ImagePromptOptimizerTool(BaseTool):
    name: str = "Image Prompt Optimizer"
    description: str = "Optimize and generate image prompts based on image description provided by customer using the GPT-4.1-mini model via Pollinations"
    args_schema: Type[BaseModel] = PromptOptimizerInput

    def _run(self, image_desc: str) -> str:
        system_instruction = (
            "You are a prompt engineering expert, responsible for optimizing image description provided by customer  "
            "into image generation prompts. The prompt must begin with: 'Generate an image of ......' "
        )
        model = "gpt-4.1-mini"

        # Construct and encode URL
        base_url = "https://text.pollinations.ai"
        query = quote(image_desc)
        print(query)
        sys_param = quote(system_instruction)
        url = f"{base_url}/{query}?model={model}&system={sys_param}"

        print(f"[🔧 DEBUG] Pollinations API URL: {url}")

        try:
            response = requests.get(url)
            response.raise_for_status()
            image_prompt = response.text.strip()

            print("[✅ DEBUG] Optimized Prompt:")
            print(image_prompt)

            return image_prompt

        except Exception as e:
            print(f"[ERROR] Pollinations API request failed: {e}")
            print("[INFO] Setting image prompt to error image")
            image_prompt = "An Error Sign"
            return image_prompt
