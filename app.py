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
from core.optimizer import HyperparameterOptimizer

def calculate_penalty(formula: str, alpha1: float, alpha2: float) -> float:
    """
    app.py 내에서 패널티 계산을 위한 헬퍼 함수.
    optimizer.py의 로직과 동일하게 유지합니다.
    """
    complexity_penalty = len(formula)
    param_count_penalty = len(re.findall(r'\d+', formula))
    return alpha1 * complexity_penalty + alpha2 * param_count_penalty

def main():
    """
    AlphaAgent 투자 조언 웹서비스의 메인 실행 함수.
    """
    st.set_page_config(page_title="AlphaAgent: LLM-Driven Alpha Mining", layout="wide")

    # 주요 색상: 옐로우 (#FFCD00), 진한 파랑 (#002C5F), 연한 회색 배경 (#F8F9FA)
    st.markdown("""
        <style>
        /* 사이드바 전체 배경을 노란색으로 변경 */
        [data-testid="stSidebar"] {
            background-color: #FFCD00;
        }
        
        /* 사이드바 텍스트 색상을 진한 파란색으로 변경 */
        [data-testid="stSidebar"] * {
            color: #002C5F; 
        }

        /* '시작' 버튼 (사이드바의 primary 버튼) 스타일 변경 */
        .stButton button[data-testid="stSidebarSubmitButton"] {
            background-color: #FFFFFF; /* 흰색 배경 */
            color: #000000; /* 검은색 글씨 */
            border: 1px solid #FFCD00; /* 노란색 테두리 */
        }
        .stButton button[data-testid="stSidebarSubmitButton"]:hover {
            background-color: #F0F0F0; /* 호버 시 약간 회색 */
            color: #000000;
            border-color: #FFDE00;
        }

        </style>
    """, unsafe_allow_html=True)

    # --- UI 구성 ---
    st.title("Vibe Quant")
    st.markdown("""
    Vibe Quant는 개인 투자자가 손쉽게 퀀트 투자를 경험해볼 수 있게 도와줍니다.
    당신의 투자 아이디어를 바탕으로, 초과 수익 기회를 찾아주는 투자 포뮬라 (알파 팩터)를 탐색합니다.
    """)

    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    initial_insight = st.sidebar.text_area(
        "**당신의 투자 아이디어를 입력하세요.**",
        height=130,
        placeholder="예시: 거래량이 급증하는 소형주는 단기적으로 가격이 상승하는 경향이 있다."
    )
    start_button = st.sidebar.button("시작", type="primary")

    # --- 워크플로우 실행 ---
    if start_button:
        if not initial_insight.strip():
            st.sidebar.error("당신의 투자 아이디어를 입력해주세요.")
            return

        try:
            # 1. 에이전트 및 클라이언트 초기화
            with st.status("에이전트 및 클라이언트 초기화...", expanded=True) as status:
                llm_client = LLMClient()
                backtester_client = BacktesterClient()
                idea_agent = IdeaAgent(llm_client)
                factor_agent = FactorAgent(llm_client)
                eval_agent = EvalAgent(backtester_client)
                advice_agent = InvestmentAdviceAgent(llm_client)
                optimizer = HyperparameterOptimizer()
                status.update(label="초기화 완료", state="complete", expanded=False)

            # 2. 메인 로직 (1단계): 알파 팩터 탐색
            st.subheader("1단계: 알파 팩터 탐색")

            with st.expander("탐색 과정 보기", expanded=True):
                # --- 가설 생성 단계 ---
                with st.spinner("Vibe Quant가 당신의 투자 아이디어에 부합하는 투자 가설을 생성 중입니다..."):
                    current_hypothesis = idea_agent.generate_initial_hypothesis(initial_insight)
                if not current_hypothesis:
                    st.error("가설 생성에 실패했습니다. 워크플로우를 중단합니다."); return
                st.success("가설 생성이 완료되었습니다.")

                # --- 알파 팩터 생성 단계 ---
                with st.spinner("Vibe Quant가 투자 가설을 바탕으로 알파 팩터를 생성 중입니다..."):
                    generated_factors = factor_agent.create_factors(current_hypothesis, num_factors=3)
                if not generated_factors:
                    st.error("알파 팩터 생성에 실패했습니다. 워크플로우를 중단합니다."); return
                st.success("알파 팩터 생성이 완료되었습니다.")

                # --- 알파 팩터 평가 단계 ---
                with st.spinner(f"{len(generated_factors)}개 알파 팩터에 대한 평가를 실행합니다..."):
                    evaluated_factors = eval_agent.evaluate_factors(generated_factors)
                st.success("알파 팩터 평가가 완료되었습니다.")
            
            if not evaluated_factors or pd.DataFrame(evaluated_factors).empty:
                st.warning("유효한 알파 팩터가 발굴되지 않았습니다."); return

            # 3. 메인 로직 (2단계): 알파 팩터 최적화
            st.subheader("2단계: 알파 팩터 최적화")

            # 최적화를 위해 IC 값이 유효한(NaN이 아닌) 팩터만 필터링합니다.
            valid_factors_for_opt = [
                f for f in evaluated_factors 
                if f.get('ic') is not None and pd.notna(f.get('ic'))
            ]

            if not valid_factors_for_opt:
                st.warning("최적화를 수행할 유효한 알파 팩터가 없습니다. 기본값을 사용합니다.")
                # 최적화 실패 시 사용할 기본 파라미터
                optimal_params = {'lambda_val': 0.001, 'alpha1': 0.5, 'alpha2': 0.5}
            else:
                with st.spinner("알파 팩터 최적화 진행 중..."):
                    # 필터링된 유효한 팩터 리스트를 최적화 함수에 전달합니다.
                    optimal_params = optimizer.optimize(valid_factors_for_opt)
                st.success("알파팩터 최적화가 완료되었습니다.")

            # 4. 메인 로직 (3단계): 투자 조언 생성
            st.subheader("3단계: 투자 조언 생성")

            final_ranked_factors = []
            for factor in evaluated_factors:
                if factor.get('ic') is not None and pd.notna(factor.get('ic')):
                    penalty = calculate_penalty(factor['formula'], optimal_params['alpha1'], optimal_params['alpha2'])
                    final_score = factor['ic'] - optimal_params['lambda_val'] * penalty

                    factor_with_score = factor.copy()
                    factor_with_score['penalty'] = penalty
                    factor_with_score['optimized_score'] = final_score
                    final_ranked_factors.append(factor_with_score)

            if not final_ranked_factors:
                st.warning("점수를 계산할 유효한 팩터가 없습니다."); return

            final_ranked_factors.sort(key=lambda x: x['optimized_score'], reverse=True)

            best_factor = final_ranked_factors[0]

            # --- 투자 조언 리포트 생성 ---
            with st.spinner("Vibe Quant가 투자 조언 리포트를 작성 중입니다..."):
                final_report = advice_agent.generate_advice_report(best_factor)
            st.success("투자 조언 리포트 작성이 완료되었습니다.")

            st.markdown(final_report)

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()

