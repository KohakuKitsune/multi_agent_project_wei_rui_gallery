from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class PricingInput(BaseModel):
    design_description: str = Field(..., description="设计描述，用于报价计算")

class PricingTool(BaseTool):
    name: str = "Pricing Tool"
    description: str = "根据设计复杂度计算报价"
    args_schema: Type[BaseModel] = PricingInput

    def _run(self, design_description: str) -> str:
        base_price = 100
        complexity_factor = len(design_description) // 10
        price = base_price + complexity_factor * 50
        return f"报价为：¥{price}"
