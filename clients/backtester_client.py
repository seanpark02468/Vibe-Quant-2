# /clients/backtester_client.py

import pandas as pd
import lightgbm as lgb
from scipy.stats import pearsonr
import streamlit as st
import os
import gdown
import pyarrow
import inspect
from core import operators

class BacktesterClient:
    """
    데이터 로딩 및 간소화된 백테스팅을 수행하는 클라이언트.
    LightGBM 모델을 사용하여 팩터의 예측력을 평가하고 정보 계수(IC)를 계산합니다.
    """
    def __init__(self):
        """
        클라이언트를 초기화하고 데이터를 로드합니다.
        """
        self.stock_data = self.load_data()
        if not self.stock_data.empty:
            # operators.py의 함수들이 올바르게 작동하려면 멀티 인덱스가 필수입니다.
            if not isinstance(self.stock_data.index, pd.MultiIndex):
                self.stock_data.set_index(['date', 'ticker'], inplace=True)
                self.stock_data.sort_index(inplace=True)

    def load_data(self) -> pd.DataFrame:
        """
        구글 드라이브에서 Parquet 형식의 주식 데이터를 다운로드하여 로드합니다.
        다운로드 실패 및 파일 손상을 처리하는 로직이 강화되었습니다.
        """
        output_path = 'kor_stocks.parquet'
        
        # 파일이 로컬에 존재하지 않는 경우에만 다운로드
        if not os.path.exists(output_path):
            try:
                with st.spinner("구글 드라이브에서 데이터를 다운로드 중입니다... (파일 크기에 따라 시간이 걸릴 수 있습니다)"):
                    # gdown.download의 결과를 변수로 받아 성공 여부 확인
                    downloaded_path = gdown.download(id=st.secrets["GOOGLE_DRIVE_FILE_ID"], output=output_path, quiet=False)
                    if downloaded_path is None:
                        st.error("파일 다운로드에 실패했습니다. 구글 드라이브 파일 ID와 공유 설정을 확인하세요.")
                        return pd.DataFrame()
            except Exception as e:
                st.error(f"구글 드라이브 파일 다운로드 중 심각한 오류 발생: {e}")
                # 실패 시 불완전한 파일이 남아있을 수 있으므로 삭제
                if os.path.exists(output_path):
                    os.remove(output_path)
                return pd.DataFrame()

        # 다운로드된 로컬 파일을 읽고 유효성을 검사합니다.
        try:
            df = pd.read_parquet(output_path)
            df['date'] = pd.to_datetime(df['date'])
            df.sort_values(by=['ticker', 'date'], inplace=True)
            df.reset_index(drop=True, inplace=True)
            st.success("데이터 로딩 완료")
            return df
        except pyarrow.lib.ArrowInvalid as e: # Parquet 파일이 아닐 때 발생하는 특정 오류
            st.error(f"다운로드된 파일이 유효한 Parquet 형식이 아닙니다. 파일을 삭제하고 재시도합니다. 오류: {e}")
            # 손상된 파일 삭제
            os.remove(output_path)
            return pd.DataFrame()
        except FileNotFoundError:
            st.error(f"데이터 파일({output_path})을 찾을 수 없습니다.")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"데이터 로드 중 알 수 없는 오류 발생: {e}")
            return pd.DataFrame()

    def run_backtest(self, factor_expression: str) -> float:
        """
        주어진 팩터 표현식을 평가하고 LightGBM을 사용하여 백테스트를 실행합니다.
        pd.eval()과 명시적 실행 범위를 사용하여 안정성을 높였습니다.
        """
        if self.stock_data.empty:
            st.warning("주식 데이터가 없어 백테스팅을 건너뜁니다.")
            return 0.0

        try:
            # 1. operators.py에서 연산자 함수들을 동적으로 로드
            operator_funcs = {
                name: func for name, func in inspect.getmembers(operators, inspect.isfunction)
                if not name.startswith('_')
            }

            # 2. 데이터프레임의 컬럼들을 딕셔너리로 준비
            data_vars = {col: self.stock_data[col] for col in self.stock_data.columns}

            # 3. 연산자 함수와 데이터 컬럼을 하나의 실행 범위(scope)로 통합
            eval_scope = {**operator_funcs, **data_vars}

            # 4. 최상위 pd.eval() 함수를 사용하여 팩터 계산
            # - local_dict에 통합된 실행 범위를 전달하여 모든 변수와 함수를 인식시킴
            # - global_dict를 비워두어 보안 강화
            factor_values = pd.eval(
                factor_expression,
                engine='python',
                local_dict=eval_scope,
                global_dict={}
            )

            # 5. 예측 대상(target) 생성: 다음 날의 수익률
            # 그룹별(ticker)로 수익률을 계산하여 데이터 왜곡 방지
            target = self.stock_data.groupby(level='ticker')['close'].pct_change(1).shift(-1)

            # 6. 데이터셋 준비
            # factor_values에 원본 데이터프레임의 인덱스를 명시적으로 부여하여 안정성 확보
            df_backtest = pd.DataFrame({
                'factor': factor_values,
                'target': target
            }, index=self.stock_data.index).dropna()

            # 7. 학습에 필요한 최소 데이터 수 확인
            if len(df_backtest) < 100:
                st.warning(f"'{factor_expression}' 팩터 계산 후 데이터가 너무 적어 백테스팅을 건너뜁니다. (데이터 수: {len(df_backtest)})")
                return 0.0

            X = df_backtest[['factor']]
            y = df_backtest['target']

            # 8. LightGBM 모델 학습 및 예측
            model = lgb.LGBMRegressor(random_state=42, n_estimators=100, verbosity=-1)
            model.fit(X, y)
            predictions = model.predict(X)

            # 9. 정보 계수(IC) 계산
            # 피어슨 상관계수를 사용하여 예측값과 실제값의 상관관계 측정
            ic, _ = pearsonr(predictions, y)

            return float(ic)

        except Exception as e:
            # st.warning(f"'{factor_expression}' 팩터 백테스팅 중 오류 발생: {e}")
            return 0.0
