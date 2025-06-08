import os
from crewai import Agent, LLM
from tools.feasibility_checker import FeasibilityCheckerTool
from tools.pricing_module import PricingTool
from dotenv import load_dotenv

load_dotenv()

llm = LLM(
    model="gpt-4o",  # 或 "gpt-4" / "gpt-3.5-turbo"
    api_key=os.getenv("OPENAI_API_KEY")
)

feasibility_planner = Agent(
    name="Feasibility Planner",
    role="Evaluate the production feasibility of a design and generate pricing",
    goal="Ensure the design is manufacturable and provide accurate pricing",
    backstory=(
        "You are an expert in production feasibility analysis. "
        "Your responsibilities include verifying the practicality and manufacturability of the design, "
        "and accurately calculating the cost for production based on the design specifications."
    ),
    tools=[FeasibilityCheckerTool(), PricingTool()],
    verbose=True,
    llm=llm  # ✅ The key lies here
)