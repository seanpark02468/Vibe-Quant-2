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
                                (키: 'description', 'formula')

        Returns:
            str: Markdown 형식으로 생성된 투자 조언 리포트.
        """
        system_prompt = """
        당신은 개인 투자자를 위한 전문적이고 통찰력 있는 퀀트 투자 자문가입니다.
        복잡한 금융 데이터와 알파 팩터를 분석하여, 데이터에 기반한 실행 가능한 투자 전략을 제시하는 데 특화되어 있습니다.
        당신의 조언은 항상 명확한 근거와 논리를 바탕으로 하며, 잠재적 위험까지 투명하게 공개하여 투자자가 합리적인 의사결정을 내리도록 돕습니다.

        제시된 알파 팩터를 분석하여, 다음 목차와 세부 가이드에 따라 전문가 수준의 '투자 조언 리포트'를 Markdown 형식으로 작성해주세요.

        <투자 조언 리포트>
        1. 알파 팩터 분석
        2. 투자 전략 설계
        """

        user_prompt = f"""
        다음은 새롭게 발굴된 우수한 알파 팩터의 정보입니다. 이 정보를 바탕으로 '투자 조언 리포트'를 작성해주세요.

        - 팩터 설명: {best_factor.get('description', 'N/A')}
        - 팩터 수식: `{best_factor.get('formula', 'N/A')}`

        리포트 작성 가이드:
        - "알파 팩터 분석"에서는 수식을 구성하는 각 변수의 의미를 정의하고, 이 팩터가 어떤 투자 논리(Investment Thesis)에 기반하여 초과 수익을 창출할 수 있는지 비유나 구체적인 예시를 들어 설명해주세요. 이 팩터가 포착하는 시장 기회나 기업의 특징을 명확히 제시해야 합니다.
        - "투자 전략 설계"에서는 이 팩터를 실제 투자에 적용하기 위한 구체적인 방법론을 제시합니다. '투자 대상(Universe)', '종목 선정 기준(Screening)', '포트폴리오 구성 방식(Weighting)', '주기적인 리밸런싱 계획'을 구체적으로 명시해주세요. 또한, 이 전략을 실행할 때 발생할 수 있는 주요 리스크(예: 시장 하락, 특정 섹터 편중, 팩터 유효성 감소)를 객관적으로 분석하고 요약해야 합니다.   
        """

        report = self.llm_client.generate_text(user_prompt, system_prompt)
        return report
