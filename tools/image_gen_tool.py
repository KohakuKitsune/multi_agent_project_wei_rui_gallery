
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from diffusers import StableDiffusionPipeline
import torch
from PIL import Image
import uuid
import os

model_id = "sd-legacy/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16,safety_checker=None)
pipe = pipe.to("cuda")

def generate_image(prompt: str, output_dir="outputs") -> str:
    os.makedirs(output_dir, exist_ok=True)
    image = pipe(prompt).images[0]

    filename = f"generate.png"
    image_filepath = os.path.join(output_dir, filename)
    image.save(image_filepath)

    return image_filepath

class ImageGenInput(BaseModel):
    image_desc: str = Field(..., description="Optimized image prompt by design_coordinator agent.")

class ImageGenerationTool(BaseTool):
    name: str = "Image Generator"
    description: str = "Generate an image based on optimized image prompt and return filepath of the generated image."
    args_schema: Type[BaseModel] = ImageGenInput

    def _run(self, image_desc: str) -> str:
        if not image_desc.strip():
            return "错误：提示词为空，请重新描述"

        try:
            image_filepath = generate_image(image_desc)
            print("图像已生成，路径： ",image_filepath)
            return image_filepath 
        except Exception as e:
            return f"生成失败：{str(e)}"
        