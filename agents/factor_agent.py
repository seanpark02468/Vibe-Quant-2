# /agents/factor_agent.py

import json
import re
import inspect
from pathlib import Path
from clients.llm_client import LLMClient
from core import operators

class FactorAgent:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

        # operator.json 불러오기
        operator_json_path = Path(__file__).parent.parent / "agents" / "operators.json"
        with open(operator_json_path, "r", encoding="utf-8") as f:
            self.operator_info = json.load(f)

        # 허용 연산자 리스트
        self.available_operators = list(self.operator_info.keys())

    def create_factors(self, hypothesis: dict, num_factors: int = 3) -> list:
        # system_prompt 생성
        system_prompt = f"""
You are an experienced Python and pandas quant developer.
Your task is to convert the given investment hypothesis into mathematical alpha factor expressions.

You MUST strictly follow these rules:

1. **Output Format**
   - The final output MUST be a valid JSON array.
   - Each element MUST be an object with exactly two keys:
     - "description": a concise human-readable explanation of the factor.
     - "formula": a Python expression that can be evaluated by `pandas.DataFrame.eval()`.

2. **Allowed Variables**
   - You may ONLY use the following base data columns:
     - 'open', 'high', 'low', 'close', 'volume'

3. **Allowed Functions (Operators)**
   - You may ONLY use functions listed in the "Allowed Operators Dictionary" below.
   - You MUST use the function names exactly as written (case-sensitive).
   - No other functions, libraries, or methods are allowed.
   - Attribute access (e.g., `obj.attr`) is strictly forbidden.

4. **Prohibited**
   - Any function or variable not listed below.
   - Any import statements, external libraries (e.g., numpy, talib).
   - Any access to object attributes or private members.
   - Any string output outside the JSON array.

5. **Factor Requirements**
   - Create {num_factors} different factors.
   - Each formula should return a vector/Series compatible with the DataFrame’s index.
   - Be creative but stay within the constraints.

[Allowed Operators Dictionary: function_name → description]
{json.dumps(self.operator_info, ensure_ascii=False, indent=2)}

Example output:
[
  {{
    "description": "Invest in assets with low 5-day return volatility",
    "formula": "1 / (stddev(close, 5) + 1e-6)"
  }},
  {{
    "description": "Price momentum over the last 10 days",
    "formula": "delta(close, 10)"
  }}
]
""".strip()

        user_prompt = f"다음 가설을 바탕으로, 규칙에 맞는 알파 팩터 {num_factors}개를 JSON 리스트 형식으로 생성해주세요:\n\n---\n{json.dumps(hypothesis, indent=2, ensure_ascii=False)}\n---"

        # LLM 호출
        response_text = self.llm_client.generate_text(user_prompt, system_prompt)

        # JSON 추출
        match = re.search(r'```json\s*(\[.*?\])\s*```|(\[.*?\])', response_text, re.DOTALL)
        if not match:
            return []
        json_string = match.group(1) if match.group(1) else match.group(2)

        try:
            factors = json.loads(json_string)
            if isinstance(factors, list) and all(isinstance(f, dict) and 'formula' in f for f in factors):
                return factors
        except json.JSONDecodeError:
            return []

        return []
