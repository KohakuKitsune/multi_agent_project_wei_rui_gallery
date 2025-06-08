from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class FeasibilityInput(BaseModel):
    design_description: str = Field(..., description="最终确认的设计描述")

class FeasibilityCheckerTool(BaseTool):
    name: str = "Feasibility Checker"
    description: str = "判断设计是否具备生产可行性"
    args_schema: Type[BaseModel] = FeasibilityInput

    def _run(self, design_description: str) -> str:
        if "不合理" in design_description or len(design_description) < 5:
            return "设计不可行：存在结构或材料问题"
        return "设计可行"
