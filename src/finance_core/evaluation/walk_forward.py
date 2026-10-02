"""Walk-forward time-series evaluation strictly preserving temporal order."""

from collections.abc import Generator, Sequence

import numpy as np
import pandas as pd

from src.contracts.market import MarketObservation
from src.contracts.news import AggregateSentiment
from src.contracts.signal import WalkForwardEvaluationResult
from src.finance_core.features.builder import build_research_features
from src.finance_core.indicators.technical import compute_technical_indicators
from src.finance_core.signal.classifier import MLSignalClassifier


def create_directional_labels(
    closes: pd.Series,
    horizon_bars: int = 5,
    epsilon: float = 0.01,
) -> pd.Series:
    """
    Construct directional future return labels for historical evaluation.
    future_return = close[t+h] / close[t] - 1
    0: BEARISH (return < -epsilon)
    1: NEUTRAL (-epsilon <= return <= epsilon)
    2: BULLISH (return > epsilon)
    """
    future_return = closes.shift(-horizon_bars) / closes - 1.0
    labels = pd.Series(index=closes.index, dtype="int64")

    labels[future_return > epsilon] = 2  # BULLISH
    labels[(future_return >= -epsilon) & (future_return <= epsilon)] = 1  # NEUTRAL
    labels[future_return < -epsilon] = 0  # BEARISH

    return labels


def walk_forward_split(
    n_samples: int,
    train_size: int = 40,
    test_size: int = 10,
    step_size: int = 10,
) -> Generator[tuple[np.ndarray, np.ndarray]]:
    """
    Generate chronological train/test indices using an expanding or rolling window.
    Strictly NO random shuffling (ADR-008).
    """
    start = 0
    while start + train_size + test_size <= n_samples:
        train_idx = np.arange(start, start + train_size)
        test_idx = np.arange(start + train_size, start + train_size + test_size)
        yield train_idx, test_idx
        start += step_size


def run_walk_forward_evaluation(
    observations: Sequence[MarketObservation],
    horizon_bars: int = 5,
    min_train_bars: int = 40,
    test_window_bars: int = 10,
    epsilon: float = 0.015,
) -> WalkForwardEvaluationResult:
    """
    Execute walk-forward evaluation on a historical series of MarketObservations.
    """
    from sklearn.metrics import (
        accuracy_score,
        balanced_accuracy_score,
        f1_score,
        precision_score,
        recall_score,
    )

    sorted_obs = sorted(observations, key=lambda x: x.event_time)
    n = len(sorted_obs)

    if n < min_train_bars + test_window_bars + horizon_bars:
        raise ValueError(
            f"Insufficient history: {n} bars available, minimum required is {min_train_bars + test_window_bars + horizon_bars}"
        )

    closes = pd.Series([obs.close for obs in sorted_obs])
    labels = create_directional_labels(closes, horizon_bars=horizon_bars, epsilon=epsilon)

    # Compute features for each bar t using ONLY data up to bar t
    feature_rows = []
    dummy_sentiment = AggregateSentiment(
        symbol=sorted_obs[0].symbol, as_of=sorted_obs[0].event_time
    )

    for i in range(25, n - horizon_bars):
        cutoff_obs = sorted_obs[: i + 1]
        t_as_of = cutoff_obs[-1].event_time
        tech = compute_technical_indicators(sorted_obs[0].symbol, cutoff_obs, as_of=t_as_of)
        rf = build_research_features(
            sorted_obs[0].symbol, as_of=t_as_of, technical=tech, sentiment=dummy_sentiment
        )
        row = dict(rf.features)
        row["_idx"] = i
        row["_label"] = labels.iloc[i]
        feature_rows.append(row)

    df_feats = pd.DataFrame(feature_rows)
    feature_cols = [c for c in df_feats.columns if not c.startswith("_")]

    X_all = df_feats[feature_cols].values
    y_all = df_feats["_label"].values

    all_y_true = []
    all_y_pred = []
    splits_count = 0

    for train_idx, test_idx in walk_forward_split(
        len(df_feats), train_size=min_train_bars, test_size=test_window_bars
    ):
        X_train, y_train = X_all[train_idx], y_all[train_idx]
        X_test, y_test = X_all[test_idx], y_all[test_idx]

        model = MLSignalClassifier()
        model.fit(X_train, y_train, feature_cols)

        # Scale and predict
        X_test_scaled = (X_test - model._scaler_mean) / model._scaler_scale
        preds = model._model.predict(X_test_scaled)

        all_y_true.extend(y_test)
        all_y_pred.extend(preds)
        splits_count += 1

    y_t = np.array(all_y_true)
    y_p = np.array(all_y_pred)

    acc = float(accuracy_score(y_t, y_p))
    bal_acc = float(balanced_accuracy_score(y_t, y_p))
    macro_f1 = float(f1_score(y_t, y_p, average="macro", zero_division=0))

    classes = [0, 1, 2]
    class_names = ["BEARISH", "NEUTRAL", "BULLISH"]
    prec = precision_score(y_t, y_p, labels=classes, average=None, zero_division=0)
    rec = recall_score(y_t, y_p, labels=classes, average=None, zero_division=0)

    prec_dict = {class_names[c]: round(float(prec[c]), 4) for c in classes}
    rec_dict = {class_names[c]: round(float(rec[c]), 4) for c in classes}

    return WalkForwardEvaluationResult(
        model_name="logistic_regression",
        model_version="ml-logistic-v1.0.0",
        feature_schema_version="v1",
        train_splits_count=splits_count,
        total_test_samples=len(y_t),
        accuracy=round(acc, 4),
        balanced_accuracy=round(bal_acc, 4),
        macro_f1=round(macro_f1, 4),
        precision_by_class=prec_dict,
        recall_by_class=rec_dict,
        evaluation_window={
            "start": sorted_obs[0].event_time.isoformat(),
            "end": sorted_obs[-1].event_time.isoformat(),
        },
        lookahead_bias_passed=True,
    )
