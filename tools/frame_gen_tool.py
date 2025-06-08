from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from PIL import Image
import os

def add_frame_to_image(image_path: str, material_choice: str) -> str:
    output_dir="D:\\Multi-Agent-Project\\outputs"
    frame_map = {
        "Classical": "frames/classic.png",
        "Wood": "frames/wooden.png",
        "White wood": "frames/wwooden.png",
        "Black wood": "frames/blackwww.png",
        "2k": "frames/kk.png"
    }
    frame_file = frame_map.get(material_choice)

    if not frame_file or not os.path.exists(frame_file):
        return "錯誤：找不到對應畫框風格的素材，請確認畫框風格是否正確"

    base_image = Image.open(image_path).convert("RGBA")
    frame_image = Image.open(frame_file).convert("RGBA")
    
    frame_width, frame_height = frame_image.size
    
    border_width = frame_width * 0.1 
    border_height = frame_height * 0.1  
    
    inner_width = int(frame_width - 2 * border_width)
    inner_height = int(frame_height - 2 * border_height)
    
    resized_image = base_image.resize((inner_width, inner_height), Image.LANCZOS)
    
    final_image = Image.new('RGBA', (frame_width, frame_height), (0, 0, 0, 0))
    
    position = (int((frame_width - inner_width) / 2), int((frame_height - inner_height) / 2))
    final_image.paste(resized_image, position)
    
    final_image = Image.alpha_composite(final_image, frame_image)

    os.makedirs(output_dir, exist_ok=True)
    
    file_name = os.path.basename(image_path)
    file_base, file_ext = os.path.splitext(file_name)
    #output_path = os.path.join(output_dir, f"{file_base}_{material_choice}_framed{file_ext}")
    output_path = os.path.join(output_dir, f"output.png")

    final_image.save(output_path, format="PNG")

    return output_path

# 輸入格式
class FrameGenInput(BaseModel):
    image_path: str = Field(..., description="File path of the image to be framed.")
    material_choice: str = Field(..., description="Frame style, e.g., Classical, Wood...")

# Tool 主體
class FrameGenerationTool(BaseTool):
    name: str = "Frame Generator"
    description: str = "Adds a picture frame to the image based on the selected frame style."
    args_schema: Type[BaseModel] = FrameGenInput

    def _run(self, image_path: str, material_choice: str) -> str:
        try:
            print(image_path)
            print(material_choice)
            result_path = add_frame_to_image(image_path, material_choice)
            return result_path
        except Exception as e:
            return f"加畫框時發生錯誤：{str(e)}"