# -*- coding: utf-8 -*-

# # app.py

# import streamlit as st
# import pandas as pd

# # 프로젝트 구성 요소 임포트
# from clients.llm_client import LLMClient
# from clients.backtester_client import BacktesterClient
# from agents.idea_agent import IdeaAgent
# from agents.factor_agent import FactorAgent
# from agents.eval_agent import EvalAgent
# from agents.advice_agent import InvestmentAdviceAgent
# from core.optimizer import HyperparameterOptimizer

# def main():
#     """
#     AlphaAgent 투자 조언 웹서비스의 메인 실행 함수.
#     """
#     st.set_page_config(page_title="AlphaAgent: LLM-Driven Alpha Mining", layout="wide")

#     # --- UI 구성 ---
#     st.title("🤖 AlphaAgent: LLM 기반 알파 탐색 및 투자 조언")
#     st.markdown("""
#     'AlphaAgent' 논문을 기반으로 구현된 이 서비스는 LLM 에이전트를 활용하여 새로운 투자 아이디어(알파 팩터)를 발굴하고,
#     백테스팅을 통해 검증한 뒤, 최종적으로 개인 투자자를 위한 조언 리포트를 생성합니다.
#     """)

#     st.sidebar.header("조정 패널")
#     initial_insight = st.sidebar.text_area(
#         "초기 투자 아이디어를 입력하세요",
#         height=150,
#         placeholder="예시: 거래량이 급증하는 소형주는 단기적으로 가격이 상승하는 경향이 있다."
#     )
#     num_rounds = st.sidebar.slider("탐색 반복 횟수 (Rounds)", 1, 5, 2)
#     start_button = st.sidebar.button("알파 탐색 시작", type="primary")

#     # --- 워크플로우 실행 ---
#     if start_button:
#         if not initial_insight.strip():
#             st.sidebar.error("초기 투자 아이디어를 입력해주세요.")
#             return

#         try:
#             # 1. 에이전트 및 클라이언트 초기화
#             with st.status("에이전트 및 클라이언트 초기화 중...", expanded=True) as status:
#                 llm_client = LLMClient()
#                 backtester_client = BacktesterClient()
#                 idea_agent = IdeaAgent(llm_client)
#                 factor_agent = FactorAgent(llm_client)
#                 eval_agent = EvalAgent(backtester_client)
#                 advice_agent = InvestmentAdviceAgent(llm_client)
#                 # optimizer = HyperparameterOptimizer() # 최적화는 현재 워크플로우에 미포함
#                 status.update(label="초기화 완료!", state="complete", expanded=False)

#         # except ValueError as e:
#         #     st.error(f"설정 오류: {e}")
#         #     st.stop()
#         # except Exception as e:
#         #     st.error(f"오류가 발생했습니다: {e}")
#         #     st.exception(e) # 모든 예외에 대해 스택 트레이스 표시
#         #     st.stop()
#             # 2. 메인 순환 로직 (Hypothesis -> Factor -> Evaluation)
#             current_hypothesis = {}
#             feedback_summary = {}
#             all_evaluated_factors = []

#             for i in range(num_rounds):
#                 round_num = i + 1
#                 st.subheader(f"🔄 Round {round_num}")

#                 with st.expander(f"Round {round_num}: 전체 과정 보기", expanded=True):
#                     # --- 가설 생성 단계 ---
#                     st.info(f"**단계 1: 가설 생성**")
#                     with st.spinner("LLM이 새로운 투자 가설을 생성 중입니다..."):
#                         if i == 0:
#                             current_hypothesis = idea_agent.generate_initial_hypothesis(initial_insight)
#                         else:
#                             current_hypothesis = idea_agent.refine_hypothesis(feedback_summary)

#                     if not current_hypothesis:
#                         st.error("가설 생성에 실패했습니다. 워크플로우를 중단합니다.")
#                         return
#                     st.write("✨ **생성된 가설:**")
#                     st.json(current_hypothesis)

#                     # --- 팩터 생성 단계 ---
#                     st.info(f"**단계 2: 팩터 변환**")
#                     with st.spinner("LLM이 가설을 바탕으로 알파 팩터 수식을 생성 중입니다..."):
#                         generated_factors = factor_agent.create_factors(current_hypothesis, num_factors=3)

#                     if not generated_factors:
#                         st.error("팩터 생성에 실패했습니다. 워크플로우를 중단합니다.")
#                         return
#                     st.write("📝 **생성된 팩터 후보:**")
#                     st.json(generated_factors)

#                     # --- 팩터 평가 단계 ---
#                     st.info(f"**단계 3: 팩터 평가**")
#                     with st.spinner(f"{len(generated_factors)}개 팩터에 대한 백테스팅을 실행합니다... (시간이 소요될 수 있습니다)"):
#                         evaluated_factors = eval_agent.evaluate_factors(generated_factors)

#                     st.write("📊 **팩터 평가 결과 (IC 기준 내림차순):**")
#                     st.dataframe(pd.DataFrame(evaluated_factors))
#                     all_evaluated_factors.extend(evaluated_factors)

#                     # --- 피드백 요약 ---
#                     feedback_summary = eval_agent.summarize_for_feedback(evaluated_factors)
#                     st.write("📈 **이번 라운드 요약:**")
#                     st.json(feedback_summary)

#             # 3. 최종 분석 및 투자 조언 생성
#             st.success("모든 알파 탐색 라운드가 완료되었습니다.")
#             st.header("🏆 최종 결과 분석")

#             if not all_evaluated_factors:
#                 st.warning("유효한 팩터가 발굴되지 않았습니다.")
#                 return

#             # 전체 라운드에서 IC가 가장 높은 팩터 선정
#             overall_best_factor = max([f for f in all_evaluated_factors if f.get('ic') is not None], key=lambda x: x['ic'])

#             st.write("전체 라운드에서 발굴된 최고의 알파 팩터는 다음과 같습니다:")
#             st.json(overall_best_factor)

#             # --- 투자 조언 리포트 생성 ---
#             st.header("📜 최종 투자 조언 리포트")
#             with st.spinner("LLM이 최종 리포트를 작성 중입니다..."):
#                 final_report = advice_agent.generate_advice_report(overall_best_factor)

#             st.markdown(final_report)

#         except Exception as e:
#             st.error(f"오류가 발생했습니다: {e}")

# if __name__ == "__main__":
#     main()

# # app.py

# import streamlit as st
# import pandas as pd

# # 프로젝트 구성 요소 임포트
# from clients.llm_client import LLMClient
# from clients.backtester_client import BacktesterClient
# from agents.idea_agent import IdeaAgent
# from agents.factor_agent import FactorAgent
# from agents.eval_agent import EvalAgent
# from agents.advice_agent import InvestmentAdviceAgent
# # from core.optimizer import HyperparameterOptimizer # 현재 워크플로우에 미포함

# def main():
#     """
#     AlphaAgent 투자 조언 웹서비스의 메인 실행 함수.
#     """
#     st.set_page_config(page_title="AlphaAgent: LLM-Driven Alpha Mining", layout="wide")

#     # --- UI 구성 ---
#     st.title("🤖 AlphaAgent: LLM 기반 알파 탐색 및 투자 조언")
#     st.markdown("""
#     'AlphaAgent' 논문을 기반으로 구현된 이 서비스는 LLM 에이전트를 활용하여 새로운 투자 아이디어(알파 팩터)를 발굴하고,
#     백테스팅을 통해 검증한 뒤, 최종적으로 개인 투자자를 위한 조언 리포트를 생성합니다.
#     """)

#     st.sidebar.header("조정 패널")
#     initial_insight = st.sidebar.text_area(
#         "초기 투자 아이디어를 입력하세요",
#         height=150,
#         placeholder="예시: 거래량이 급증하는 소형주는 단기적으로 가격이 상승하는 경향이 있다."
#     )
#     # num_rounds 슬라이더 제거
#     start_button = st.sidebar.button("알파 탐색 시작", type="primary")

#     # --- 워크플로우 실행 ---
#     if start_button:
#         if not initial_insight.strip():
#             st.sidebar.error("초기 투자 아이디어를 입력해주세요.")
#             return

#         try:
#             # 1. 에이전트 및 클라이언트 초기화
#             with st.status("에이전트 및 클라이언트 초기화 중...", expanded=True) as status:
#                 llm_client = LLMClient()
#                 backtester_client = BacktesterClient()
#                 idea_agent = IdeaAgent(llm_client)
#                 factor_agent = FactorAgent(llm_client)
#                 eval_agent = EvalAgent(backtester_client)
#                 advice_agent = InvestmentAdviceAgent(llm_client)
#                 status.update(label="초기화 완료!", state="complete", expanded=False)

#             # 2. 메인 로직 (Hypothesis -> Factor -> Evaluation) - 단일 실행
#             st.subheader("🔄 알파 탐색 과정")
            
#             with st.expander("전체 과정 보기", expanded=True):
#                 # --- 가설 생성 단계 ---
#                 st.info("**단계 1: 가설 생성**")
#                 with st.spinner("LLM이 새로운 투자 가설을 생성 중입니다..."):
#                     current_hypothesis = idea_agent.generate_initial_hypothesis(initial_insight)

#                 if not current_hypothesis:
#                     st.error("가설 생성에 실패했습니다. 워크플로우를 중단합니다.")
#                     return
#                 st.write("✨ **생성된 가설:**")
#                 st.json(current_hypothesis)

#                 # --- 팩터 생성 단계 ---
#                 st.info("**단계 2: 팩터 변환**")
#                 with st.spinner("LLM이 가설을 바탕으로 알파 팩터 수식을 생성 중입니다..."):
#                     generated_factors = factor_agent.create_factors(current_hypothesis, num_factors=3)

#                 if not generated_factors:
#                     st.error("팩터 생성에 실패했습니다. 워크플로우를 중단합니다.")
#                     return
#                 st.write("📝 **생성된 팩터 후보:**")
#                 st.json(generated_factors)

#                 # --- 팩터 평가 단계 ---
#                 st.info("**단계 3: 팩터 평가**")
#                 with st.spinner(f"{len(generated_factors)}개 팩터에 대한 백테스팅을 실행합니다... (시간이 소요될 수 있습니다)"):
#                     evaluated_factors = eval_agent.evaluate_factors(generated_factors)

#                 st.write("📊 **팩터 평가 결과 (IC 기준 내림차순):**")
#                 st.dataframe(pd.DataFrame(evaluated_factors))

#             # 3. 최종 분석 및 투자 조언 생성
#             st.success("알파 탐색이 완료되었습니다.")
#             st.header("🏆 최종 결과 분석")

#             if not evaluated_factors or pd.DataFrame(evaluated_factors).empty:
#                 st.warning("유효한 팩터가 발굴되지 않았습니다.")
#                 return

#             # IC가 가장 높은 팩터 선정
#             best_factor = max([f for f in evaluated_factors if f.get('ic') is not None], key=lambda x: x['ic'])

#             st.write("발굴된 최고의 알파 팩터는 다음과 같습니다:")
#             st.json(best_factor)

#             # --- 투자 조언 리포트 생성 ---
#             st.header("📜 최종 투자 조언 리포트")
#             with st.spinner("LLM이 최종 리포트를 작성 중입니다..."):
#                 final_report = advice_agent.generate_advice_report(best_factor)

#             st.markdown(final_report)

#         except Exception as e:
#             st.error(f"오류가 발생했습니다: {e}")

# if __name__ == "__main__":
#     main()

# # app.py

# import streamlit as st
# import pandas as pd
# import re

# # 프로젝트 구성 요소 임포트
# from clients.llm_client import LLMClient
# from clients.backtester_client import BacktesterClient
# from agents.idea_agent import IdeaAgent
# from agents.factor_agent import FactorAgent
# from agents.eval_agent import EvalAgent
# from agents.advice_agent import InvestmentAdviceAgent
# from core.optimizer import HyperparameterOptimizer # 최적화 모듈 임포트

# def calculate_penalty(formula: str, alpha1: float, alpha2: float) -> float:
#     """
#     app.py 내에서 패널티 계산을 위한 헬퍼 함수.
#     optimizer의 로직과 동일하게 유지합니다.
#     """
#     complexity_penalty = len(formula)
#     param_count_penalty = len(re.findall(r'\d+', formula))
#     return alpha1 * complexity_penalty + alpha2 * param_count_penalty

# def main():
#     """
#     AlphaAgent 투자 조언 웹서비스의 메인 실행 함수.
#     """
#     st.set_page_config(page_title="AlphaAgent: LLM-Driven Alpha Mining", layout="wide")

#     # --- UI 구성 ---
#     st.title("Vibe Quant")
#     st.markdown("""
#     이 서비스는 LLM 에이전트를 활용하여 새로운 투자 아이디어(알파 팩터)를 발굴하고,
#     백테스팅을 통해 검증한 뒤, 최종적으로 개인 투자자를 위한 조언 리포트를 생성합니다.
#     """)

#     st.sidebar.header("입력 패널")
#     initial_insight = st.sidebar.text_area(
#         "초기 투자 아이디어를 입력하세요",
#         height=150,
#         placeholder="예시: 거래량이 급증하는 소형주는 단기적으로 가격이 상승하는 경향이 있다."
#     )
#     start_button = st.sidebar.button("알파 탐색 시작", type="primary")

#     # --- 워크플로우 실행 ---
#     if start_button:
#         if not initial_insight.strip():
#             st.sidebar.error("초기 투자 아이디어를 입력해주세요.")
#             return

#         try:
#             # 1. 에이전트 및 클라이언트 초기화
#             with st.status("에이전트 및 클라이언트 초기화 중...", expanded=True) as status:
#                 llm_client = LLMClient()
#                 backtester_client = BacktesterClient()
#                 idea_agent = IdeaAgent(llm_client)
#                 factor_agent = FactorAgent(llm_client)
#                 eval_agent = EvalAgent(backtester_client)
#                 advice_agent = InvestmentAdviceAgent(llm_client)
#                 optimizer = HyperparameterOptimizer() # Optimizer 인스턴스 생성
#                 status.update(label="초기화 완료!", state="complete", expanded=False)

#             # 2. 메인 로직 (1단계): 초기 알파 탐색
#             st.subheader("🔄 1단계: 초기 알파 탐색 및 평가")
            
#             with st.expander("초기 탐색 과정 보기", expanded=True):
#                 # --- 가설 생성 단계 ---
#                 with st.spinner("LLM이 새로운 투자 가설을 생성 중입니다..."):
#                     current_hypothesis = idea_agent.generate_initial_hypothesis(initial_insight)
#                 if not current_hypothesis:
#                     st.error("가설 생성에 실패했습니다. 워크플로우를 중단합니다."); return
#                 st.write("✨ **생성된 가설:**"); st.json(current_hypothesis)

#                 # --- 팩터 생성 단계 ---
#                 with st.spinner("LLM이 가설을 바탕으로 알파 팩터 수식을 생성 중입니다..."):
#                     # 최적화를 위해 더 많은 팩터 후보군 생성
#                     generated_factors = factor_agent.create_factors(current_hypothesis, num_factors=3)
#                 if not generated_factors:
#                     st.error("팩터 생성에 실패했습니다. 워크플로우를 중단합니다."); return
#                 st.write("📝 **생성된 팩터 후보:**"); st.json(generated_factors)

#                 # --- 팩터 평가 단계 ---
#                 with st.spinner(f"{len(generated_factors)}개 팩터에 대한 백테스팅을 실행합니다..."):
#                     evaluated_factors = eval_agent.evaluate_factors(generated_factors)
#                 st.write("📊 **초기 팩터 평가 결과 (IC 기준 내림차순):**")
#                 st.dataframe(pd.DataFrame(evaluated_factors))
            
#             if not evaluated_factors or pd.DataFrame(evaluated_factors).empty:
#                 st.warning("유효한 팩터가 발굴되지 않았습니다."); return

#             # 3. 메인 로직 (2단계): 하이퍼파라미터 최적화
#             st.subheader("⚙️ 2단계: 하이퍼파라미터 최적화")
#             with st.spinner("베이지안 최적화를 통해 최적의 패널티 계수를 찾고 있습니다..."):
#                 optimal_params = optimizer.optimize(evaluated_factors)
#             st.success("하이퍼파라미터 최적화가 완료되었습니다.")
#             st.write("최적의 패널티 계수는 다음과 같습니다:")
#             st.json(optimal_params)

#             # 4. 메인 로직 (3단계): 최종 분석 및 투자 조언 생성
#             st.subheader("🏆 3단계: 최종 분석 및 투자 조언")

#             # 최적화된 계수를 사용하여 모든 팩터의 최종 점수 계산
#             final_ranked_factors = []
#             for factor in evaluated_factors:
#                 if factor.get('ic') is not None:
#                     penalty = calculate_penalty(factor['formula'], optimal_params['alpha1'], optimal_params['alpha2'])
#                     final_score = factor['ic'] - optimal_params['lambda_val'] * penalty
                    
#                     factor_with_score = factor.copy()
#                     factor_with_score['penalty'] = penalty
#                     factor_with_score['optimized_score'] = final_score
#                     final_ranked_factors.append(factor_with_score)
            
#             if not final_ranked_factors:
#                 st.warning("점수를 계산할 유효한 팩터가 없습니다."); return
                
#             # 최종 점수(optimized_score) 기준으로 정렬
#             final_ranked_factors.sort(key=lambda x: x['optimized_score'], reverse=True)
#             st.write("최적화된 점수를 포함한 최종 팩터 랭킹:")
#             st.dataframe(pd.DataFrame(final_ranked_factors))

#             # 최종 점수가 가장 높은 팩터를 선정
#             best_factor = final_ranked_factors[0]

#             st.write("✨ **최종 선정된 최고의 알파 팩터:**")
#             st.json(best_factor)

#             # --- 투자 조언 리포트 생성 ---
#             st.header("📜 최종 투자 조언 리포트")
#             with st.spinner("LLM이 최종 리포트를 작성 중입니다..."):
#                 final_report = advice_agent.generate_advice_report(best_factor)

#             st.markdown(final_report)

#         except Exception as e:
#             st.error(f"오류가 발생했습니다: {e}")

# if __name__ == "__main__":
#     main()

# app.py

import streamlit as st
import pandas as pd
import re

# 프로젝트 구성 요소 임포트
from clients.llm_client import LLMClient
from clients.backtester_client import BacktesterClient
from agents.idea_agent import IdeaAgent
from agents.factor_agent import FactorAgent
from agents.eval_agent import EvalAgent
from agents.advice_agent import InvestmentAdviceAgent
from core.optimizer import HyperparameterOptimizer # 최적화 모듈 임포트

def calculate_penalty(formula: str, alpha1: float, alpha2: float) -> float:
    """
    app.py 내에서 패널티 계산을 위한 헬퍼 함수.
    optimizer의 로직과 동일하게 유지합니다.
    """
    complexity_penalty = len(formula)
    param_count_penalty = len(re.findall(r'\d+', formula))
    return alpha1 * complexity_penalty + alpha2 * param_count_penalty

def main():
    """
    AlphaAgent 투자 조언 웹서비스의 메인 실행 함수.
    """
    st.set_page_config(page_title="AlphaAgent: LLM-Driven Alpha Mining", layout="wide")

    # --- UI 구성 ---
    st.title("Vibe Quant")
    st.markdown("""
    이 서비스는 LLM 에이전트를 활용하여 새로운 투자 아이디어(알파 팩터)를 발굴하고,
    백테스팅을 통해 검증한 뒤, 최종적으로 개인 투자자를 위한 조언 리포트를 생성합니다.
    """)

    st.sidebar.header("입력 패널")
    initial_insight = st.sidebar.text_area(
        "초기 투자 아이디어를 입력하세요",
        height=150,
        placeholder="예시: 거래량이 급증하는 소형주는 단기적으로 가격이 상승하는 경향이 있다."
    )
    start_button = st.sidebar.button("알파 탐색 시작", type="primary")

    # --- 워크플로우 실행 ---
    if start_button:
        if not initial_insight.strip():
            st.sidebar.error("초기 투자 아이디어를 입력해주세요.")
            return

        try:
            # 1. 에이전트 및 클라이언트 초기화
            with st.status("에이전트 및 클라이언트 초기화 중...", expanded=True) as status:
                llm_client = LLMClient()
                backtester_client = BacktesterClient()
                idea_agent = IdeaAgent(llm_client)
                factor_agent = FactorAgent(llm_client)
                eval_agent = EvalAgent(backtester_client)
                advice_agent = InvestmentAdviceAgent(llm_client)
                optimizer = HyperparameterOptimizer() # Optimizer 인스턴스 생성
                status.update(label="초기화 완료!", state="complete", expanded=False)

            # 2. 메인 로직 (1단계): 초기 알파 탐색
            st.subheader("🔄 1단계: 초기 알파 탐색 및 평가")
            
            with st.expander("초기 탐색 과정 보기", expanded=True):
                # --- 가설 생성 단계 ---
                with st.spinner("LLM이 새로운 투자 가설을 생성 중입니다..."):
                    current_hypothesis = idea_agent.generate_initial_hypothesis(initial_insight)
                if not current_hypothesis:
                    st.error("가설 생성에 실패했습니다. 워크플로우를 중단합니다."); return
                st.write("✨ **생성된 가설:**"); st.json(current_hypothesis)

                # --- 팩터 생성 단계 ---
                with st.spinner("LLM이 가설을 바탕으로 알파 팩터 수식을 생성 중입니다..."):
                    generated_factors = factor_agent.create_factors(current_hypothesis, num_factors=3)
                if not generated_factors:
                    st.error("팩터 생성에 실패했습니다. 워크플로우를 중단합니다."); return
                st.write("📝 **생성된 팩터 후보:**"); st.json(generated_factors)

                # --- 팩터 평가 단계 ---
                with st.spinner(f"{len(generated_factors)}개 팩터에 대한 백테스팅을 실행합니다..."):
                    evaluated_factors = eval_agent.evaluate_factors(generated_factors)
                st.write("📊 **초기 팩터 평가 결과 (IC 기준 내림차순):**")
                st.dataframe(pd.DataFrame(evaluated_factors))
            
            if not evaluated_factors or pd.DataFrame(evaluated_factors).empty:
                st.warning("유효한 팩터가 발굴되지 않았습니다."); return

            # 3. 메인 로직 (2단계): 하이퍼파라미터 최적화
            st.subheader("⚙️ 2단계: 하이퍼파라미터 최적화")

            # --- 🔑 주요 수정 사항 ---
            # 최적화를 위해 IC 값이 유효한(NaN이 아닌) 팩터만 필터링합니다.
            valid_factors_for_opt = [
                f for f in evaluated_factors 
                if f.get('ic') is not None and pd.notna(f.get('ic'))
            ]

            if not valid_factors_for_opt:
                st.warning("하이퍼파라미터 최적화를 수행할 유효한 팩터가 없습니다. 기본값을 사용합니다.")
                # 최적화 실패 시 사용할 기본 파라미터
                optimal_params = {'lambda_val': 0.001, 'alpha1': 0.5, 'alpha2': 0.5}
            else:
                with st.spinner("베이지안 최적화를 통해 최적의 패널티 계수를 찾고 있습니다..."):
                    # 필터링된 유효한 팩터 리스트를 최적화 함수에 전달합니다.
                    optimal_params = optimizer.optimize(valid_factors_for_opt)
            
            st.success("하이퍼파라미터 최적화가 완료되었습니다.")
            st.write("최적의 패널티 계수는 다음과 같습니다:")
            st.json(optimal_params)

            # 4. 메인 로직 (3단계): 최종 분석 및 투자 조언 생성
            st.subheader("🏆 3단계: 최종 분석 및 투자 조언")

            final_ranked_factors = []
            for factor in evaluated_factors:
                if factor.get('ic') is not None and pd.notna(factor.get('ic')): # 최종 랭킹에서도 유효한 팩터만 사용
                    penalty = calculate_penalty(factor['formula'], optimal_params['alpha1'], optimal_params['alpha2'])
                    final_score = factor['ic'] - optimal_params['lambda_val'] * penalty
                    
                    factor_with_score = factor.copy()
                    factor_with_score['penalty'] = penalty
                    factor_with_score['optimized_score'] = final_score
                    final_ranked_factors.append(factor_with_score)
            
            if not final_ranked_factors:
                st.warning("점수를 계산할 유효한 팩터가 없습니다."); return
            
            final_ranked_factors.sort(key=lambda x: x['optimized_score'], reverse=True)
            st.write("최적화된 점수를 포함한 최종 팩터 랭킹:")
            st.dataframe(pd.DataFrame(final_ranked_factors))

            best_factor = final_ranked_factors[0]

            st.write("✨ **최종 선정된 최고의 알파 팩터:**")
            st.json(best_factor)

            # --- 투자 조언 리포트 생성 ---
            st.header("📜 최종 투자 조언 리포트")
            with st.spinner("LLM이 최종 리포트를 작성 중입니다..."):
                final_report = advice_agent.generate_advice_report(best_factor)

            st.markdown(final_report)

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()
