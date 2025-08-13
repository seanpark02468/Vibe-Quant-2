# /core/optimizer.py

import re
import numpy as np
from bayes_opt import BayesianOptimization

class HyperparameterOptimizer:
    """
    베이지안 최적화를 사용하여 최적의 정규화 계수를 탐색하는 클래스.
    """
    def __init__(self):
        self.evaluated_factors = None

    def _calculate_penalty(self, formula: str, alpha1: float, alpha2: float) -> float:
        """
        팩터의 복잡도에 기반한 패널티 점수를 계산합니다. (간소화된 버전)

        Args:
            formula (str): 팩터 수식.
            alpha1 (float): 팩터 길이(복잡도)에 대한 가중치.
            alpha2 (float): 팩터 내 파라미터 수에 대한 가중치.

        Returns:
            float: 계산된 패널티 점수.
        """
        # 팩터 복잡도: 수식의 길이
        complexity_penalty = len(formula)

        # 파라미터 수: 수식에 사용된 숫자 개수
        param_count_penalty = len(re.findall(r'\d+', formula))

        return alpha1 * complexity_penalty + alpha2 * param_count_penalty

    def _objective_function(self, lambda_val: float, alpha1: float, alpha2: float) -> float:
        """
        베이지안 최적화의 목적 함수.
        IC와 패널티를 조합하여 팩터의 최종 점수를 계산하고, 그 중 최대값을 반환합니다.
        Score = IC - lambda * Penalty
        """
        if not self.evaluated_factors:
            return 0.0

        scores = []
        for factor in self.evaluated_factors:
            ic = factor.get('ic', 0.0)
            formula = factor.get('formula', '')

            penalty = self._calculate_penalty(formula, alpha1, alpha2)

            # 최종 점수 계산
            score = ic - lambda_val * penalty
            scores.append(score)

        return max(scores) if scores else 0.0

    def optimize(self, evaluated_factors: list) -> dict:
        """
        주어진 평가된 팩터 목록을 기반으로 베이지안 최적화를 실행합니다.

        Args:
            evaluated_factors (list): IC 점수가 포함된 팩터 리스트.

        Returns:
            dict: 찾은 최적의 하이퍼파라미터.
        """
        self.evaluated_factors = evaluated_factors

        # 하이퍼파라미터 탐색 범위 (0.0 ~ 1.0 사이에서 탐색)
        # lambda는 패널티의 강도를 조절하므로 작은 범위로 설정 (e.g., 0 ~ 0.01)
        pbounds = {
            'lambda_val': (0, 0.01),
            'alpha1': (0, 1.0),
            'alpha2': (0, 1.0)
        }

        optimizer = BayesianOptimization(
            f=self._objective_function,
            pbounds=pbounds,
            random_state=42,
        )

        # 최적화 실행
        # init_points: 랜덤 탐색 횟수, n_iter: 베이지안 최적화 반복 횟수
        optimizer.maximize(init_points=5, n_iter=10)

        return optimizer.max['params']
