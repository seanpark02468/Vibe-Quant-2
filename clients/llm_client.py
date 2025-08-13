# /clients/llm_client.py

import streamlit as st
from openai import OpenAI
import os

class LLMClient:
    """
    OpenAI의 Large Language Model (LLM)과 상호작용하는 클라이언트.
    Streamlit의 secrets 관리 기능을 사용하여 API 키를 안전하게 관리합니다.
    """
    def __init__(self):
        """
        클라이언트를 초기화하고 OpenAI API에 연결합니다.
        """
        try:
            # Streamlit의 secrets.toml에서 API 키를 가져옵니다.
            api_key = st.secrets["OPENAI_API_KEY"]
            self.client = OpenAI(api_key=api_key)
        except KeyError:
            raise ValueError("OpenAI API 키가 .streamlit/secrets.toml 파일에 설정되지 않았습니다.")
        except Exception as e:
            raise RuntimeError(f"OpenAI 클라이언트 초기화 중 오류 발생: {e}")

    def generate_text(self, user_prompt: str, system_prompt: str) -> str:
        """
        주어진 프롬프트를 기반으로 LLM을 사용하여 텍스트를 생성합니다.

        Args:
            user_prompt (str): 모델에 전달할 사용자 프롬프트.
            system_prompt (str): 모델의 역할과 행동을 정의하는 시스템 프롬프트.

        Returns:
            str: LLM이 생성한 텍스트 응답.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7, # 창의성과 일관성 사이의 균형을 맞추기 위한 설정
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            st.error(f"LLM 응답 생성 중 오류 발생: {e}")
            return "" # 오류 발생 시 빈 문자열 반환
