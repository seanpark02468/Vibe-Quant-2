# /core/operators.py

import pandas as pd
import numpy as np

# 모든 함수는 멀티 인덱스(ticker, date)를 가진 Series를 입력으로 받습니다.

def _get_rolling_obj(series: pd.Series, window: int) -> pd.core.window.rolling.Rolling:
    """Helper to get a rolling object for time-series operations on a multi-index Series."""
    return series.groupby(level='ticker').rolling(window=window, min_periods=max(1, int(window * 0.8)))

# --- Basic Math Operators ---

def sign(series: pd.Series) -> pd.Series:
    """ 데이터의 부호를 반환합니다 (양수: 1, 음수: -1, 0: 0). """
    return np.sign(series)

# --- Time-series Operators ---

def delay(series: pd.Series, d: int) -> pd.Series:
    """ d일 전의 데이터 값을 가져옵니다. """
    return series.groupby(level='ticker').shift(d)

def delta(series: pd.Series, d: int) -> pd.Series:
    """ 오늘의 데이터 값과 d일 전의 데이터 값 사이의 차이를 계산합니다. """
    return series - series.groupby(level='ticker').shift(d)

def correlation(series1: pd.Series, series2: pd.Series, d: int) -> pd.Series:
    """ 지난 d일 동안의 두 데이터 시리즈 간의 시계열 상관관계를 계산합니다. """
    rolling_corr = _get_rolling_obj(series1, d).corr(series2)
    return rolling_corr.reset_index(level=0, drop=True)

def covariance(series1: pd.Series, series2: pd.Series, d: int) -> pd.Series:
    """ 지난 d일 동안의 두 데이터 시리즈 간의 시계열 공분산을 계산합니다. """
    rolling_cov = _get_rolling_obj(series1, d).cov(series2)
    return rolling_cov.reset_index(level=0, drop=True)

def ts_min(series: pd.Series, d: int) -> pd.Series:
    """ 지난 d일 동안의 시계열 최소값을 찾습니다. """
    rolling_min = _get_rolling_obj(series, d).min()
    return rolling_min.reset_index(level=0, drop=True)

def ts_max(series: pd.Series, d: int) -> pd.Series:
    """ 지난 d일 동안의 시계열 최대값을 찾습니다. """
    rolling_max = _get_rolling_obj(series, d).max()
    return rolling_max.reset_index(level=0, drop=True)

def ts_argmin(series: pd.Series, d: int) -> pd.Series:
    """ 지난 d일 동안 시계열 최소값이 발생한 날의 상대적 위치를 반환합니다. """
    rolling_argmin = _get_rolling_obj(series, d).apply(np.argmin, raw=True)
    return rolling_argmin.reset_index(level=0, drop=True)

def ts_argmax(series: pd.Series, d: int) -> pd.Series:
    """ 지난 d일 동안 시계열 최대값이 발생한 날의 상대적 위치를 반환합니다. """
    rolling_argmax = _get_rolling_obj(series, d).apply(np.argmax, raw=True)
    return rolling_argmax.reset_index(level=0, drop=True)

def ts_rank(series: pd.Series, d: int) -> pd.Series:
    """ 지난 d일 동안의 시계열 순위를 계산합니다 (현재 값의 순위). """
    rolling_rank = _get_rolling_obj(series, d).apply(lambda w: w.rank(pct=True).iloc[-1], raw=False)
    return rolling_rank.reset_index(level=0, drop=True)

def stddev(series: pd.Series, d: int) -> pd.Series:
    """ 지난 d일 동안의 이동 시계열 표준편차를 계산합니다. """
    rolling_std = _get_rolling_obj(series, d).std()
    return rolling_std.reset_index(level=0, drop=True)

def ts_sum(series: pd.Series, d: int) -> pd.Series:
    """ 지난 d일 동안의 시계열 합계를 계산합니다. """
    rolling_sum = _get_rolling_obj(series, d).sum()
    return rolling_sum.reset_index(level=0, drop=True)

def ts_product(series: pd.Series, d: int) -> pd.Series:
    """ 지난 d일 동안의 시계열 곱을 계산합니다. """
    rolling_prod = _get_rolling_obj(series, d).apply(np.prod, raw=True)
    return rolling_prod.reset_index(level=0, drop=True)

def decay_linear(series: pd.Series, d: int) -> pd.Series:
    """ 지난 d일 동안 선형적으로 감소하는 가중치를 적용한 가중 이동 평균을 계산합니다. """
    weights = np.arange(1, d + 1)
    rolling_decay = _get_rolling_obj(series, d).apply(lambda s: np.dot(s, weights) / weights.sum(), raw=True)
    return rolling_decay.reset_index(level=0, drop=True)

# --- Cross-sectional Operators ---

def rank(series: pd.Series) -> pd.Series:
    """ 횡단면 순위를 계산합니다. 즉, 각 날짜 내에서 모든 티커의 순위를 매깁니다. """
    return series.groupby(level='date').rank(pct=True)

def scale(series: pd.Series, a: float = 1.0) -> pd.Series:
    """ 횡단면 데이터를 스케일링하여 절대값의 합이 'a'가 되도록 합니다. """
    scaler = series.groupby(level='date').transform(lambda x: x.abs().sum())
    return series * a / scaler

def indneutralize(series: pd.Series, industry_series: pd.Series) -> pd.Series:
    """ 산업(또는 다른 그룹)에 대해 데이터를 중립화합니다. """
    group_mean = series.groupby([series.index.get_level_values('date'), industry_series]).transform('mean')
    return series - group_mean
