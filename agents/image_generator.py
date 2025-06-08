import os
from crewai import Agent, LLM
from tools.image_gen_tool import ImageGenerationTool
from tools.frame_gen_tool import FrameGenerationTool
from dotenv import load_dotenv

load_dotenv()
llm = LLM(
    model="gpt-4o",  # 或 "gpt-4" / "gpt-3.5-turbo"
    api_key=os.getenv("OPENAI_API_KEY")
)

image_generator = Agent(
    name="Image Generator",
    role="Generate images based on image descriptions provided by the customer and then frame the images, or else just frame the image if there is image provided by the customer.",
    goal="Deliver a detailed and high-quality framed design preview",
    backstory=(
        "You are an AI agent highly skilled in image synthesis. "
        "When receiving a prompt from the Design Coordinator, you respond as follows:\n"
        "- If you receive an image, use the Frame Generation Tool directly to produce a framed preview.\n"
        "- If you receive a text prompt, first use the Image Generation Tool to generate the image, "
        "then use the Frame Generation Tool to frame it.\n"
        "Your objective is always to provide a detailed and visually accurate preview of the final framed design."
    ),
    tools=[ImageGenerationTool(), FrameGenerationTool()],
    verbose=True,
    llm=llm  # ✅ The key lies here
)