# /agents/eval_agent.py

from clients.backtester_client import BacktesterClient

class EvalAgent:
    """
    생성된 알파 팩터의 성과를 평가하는 에이전트.
    BacktesterClient를 사용하여 각 팩터의 정보 계수(IC)를 계산합니다.
    """
    def __init__(self, backtester_client: BacktesterClient):
        """
        에이전트를 초기화합니다.

        Args:
            backtester_client (BacktesterClient): 백테스팅을 수행할 클라이언트.
        """
        self.backtester_client = backtester_client

    def evaluate_factors(self, factors: list) -> list:
        """
        팩터 리스트를 받아 각각의 성과(IC)를 평가합니다.

        Args:
            factors (list): FactorAgent가 생성한 팩터 딕셔너리 리스트.

        Returns:
            list: 각 팩터에 'ic' 점수가 추가되고, IC를 기준으로 내림차순 정렬된 리스트.
        """
        evaluated_results = []
        for factor in factors:
            formula = factor.get('formula')
            if not formula:
                continue

            # 백테스터를 통해 IC 점수 계산
            ic_score = self.backtester_client.run_backtest(formula)

            result = factor.copy()
            result['ic'] = ic_score
            evaluated_results.append(result)

        # IC 점수가 높은 순으로 정렬
        evaluated_results.sort(key=lambda x: x['ic'], reverse=True)
        return evaluated_results

    def summarize_for_feedback(self, evaluated_factors: list) -> dict:
        """
        평가된 팩터 목록을 분석하여 IdeaAgent에 전달할 피드백을 요약합니다.

        Returns:
            dict: 최고 성과 팩터, 평균 IC 등 요약 정보가 담긴 딕셔너리.
        """
        if not evaluated_factors:
            return {"message": "평가할 유효한 팩터가 없습니다."}

        best_factor = evaluated_factors[0]
        ic_scores = [f['ic'] for f in evaluated_factors if f.get('ic') is not None]

        summary = {
            "best_factor_formula": best_factor.get('formula'),
            "best_factor_ic": best_factor.get('ic'),
            "average_ic": sum(ic_scores) / len(ic_scores) if ic_scores else 0,
            "num_factors_evaluated": len(evaluated_factors),
            "num_successful_factors (IC > 0)": len([s for s in ic_scores if s > 0])
        }
        return summary
