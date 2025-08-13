# /agents/advice_agent.py

import json
from clients.llm_client import LLMClient

class InvestmentAdviceAgent:
    """
    최종 선택된 알파 팩터를 기반으로 사용자 친화적인 투자 조언 리포트를 생성하는 에이전트.
    """
    def __init__(self, llm_client: LLMClient):
        """
        에이전트를 초기화합니다.

        Args:
            llm_client (LLMClient): LLM과 상호작용하기 위한 클라이언트.
        """
        self.llm_client = llm_client

    def generate_advice_report(self, best_factor: dict) -> str:
        """
        최고 성과 팩터 정보를 바탕으로 투자 조언 리포트를 생성합니다.

        Args:
            best_factor (dict): 최고 성과 팩터 정보.
                                (키: 'description', 'formula', 'ic')

        Returns:
            str: Markdown 형식으로 생성된 투자 조언 리포트.
        """
        system_prompt = """
        당신은 개인 투자자를 위한 친절하고 통찰력 있는 투자 자문가입니다.
        복잡한 금융 데이터를 쉽게 풀어 설명하고, 실행 가능한 투자 조언을 제공하는 데 능숙합니다.
        제시된 알파 팩터(투자 전략의 핵심 아이디어)를 분석하여,
        다음 목차에 따라 명확하고 간결한 '투자 조언 리포트'를 Markdown 형식으로 작성해주세요.

        <한 눈에 보는 투자 전략>
        1. 신규 팩터 "X"의 정의
        2. 투자 전략 개요
        3. 핵심 투자 제안
        """
        user_prompt = f"""
        다음은 새롭게 발굴된 우수한 알파 팩터의 정보입니다. 이 정보를 바탕으로 투자 조언 리포트를 작성해주세요.

        - 팩터 설명: {best_factor.get('description', 'N/A')}
        - 팩터 수식: `{best_factor.get('formula', 'N/A')}`
        - 팩터 성과 (정보 계수 IC): {best_factor.get('ic', 0.0):.4f}

        리포트 작성 가이드:
        - "신규 팩터 'X'의 정의"에서는 팩터 수식을 일반 투자자가 이해할 수 있는 언어로 쉽게 해석해주세요. 이 팩터가 어떤 시장 상황이나 주식의 특징을 포착하려 하는지 설명해주세요.
        - "투자 전략 개요"에서는 이 팩터를 어떻게 활용할 수 있는지, 예상되는 투자 스타일(예: 단기 모멘텀, 장기 가치투자 등)과 목표, 그리고 잠재적 위험에 대해 요약해주세요.
        - "핵심 투자 제안"에서는 투자자가 실제로 취할 수 있는 구체적인 행동(Actionable Advice)을 한두 문장으로 명확하게 제시해주세요.
        """

        report = self.llm_client.generate_text(user_prompt, system_prompt)
        return report
