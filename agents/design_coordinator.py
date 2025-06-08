import os
from crewai import Agent, LLM
from tools.prompt_optimizer import ImagePromptOptimizerTool
from dotenv import load_dotenv

load_dotenv()

llm = LLM(
    model="gpt-4o",  # 或 "gpt-4" / "gpt-3.5-turbo"
    api_key=os.getenv("OPENAI_API_KEY")
)

design_coordinator = Agent(
    name="Design Coordinator",
    role="Coordinate client requirements and manage prompt optimization",
    goal="Accurately convey the client's design intent and coordinate multi-agent collaboration",
    backstory="You are an experienced design coordination agent, responsible for translating client needs into clear prompts and coordinating image generation and order processing.",
    tools=[ImagePromptOptimizerTool()],
    verbose=True,
    llm=llm  # ✅ The key lies here
)