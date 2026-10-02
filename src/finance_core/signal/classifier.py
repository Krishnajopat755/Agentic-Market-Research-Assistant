"""ML signal classification model with point-in-time training and inference."""

import pickle

import numpy as np

from src.contracts.features import ResearchFeatures
from src.contracts.signal import SignalContributor, SignalResult
from src.finance_core.market_data.normalization import normalize_datetime

STATE_MAP = {0: "BEARISH", 1: "NEUTRAL", 2: "BULLISH"}
LABEL_TO_INT = {"BEARISH": 0, "NEUTRAL": 1, "BULLISH": 2}


class MLSignalClassifier:
    """Logistic Regression / Classical ML model for directional market state."""

    def __init__(self, model_version: str = "ml-logistic-v1.0.0"):
        self.model_version = model_version
        self.feature_names: list[str] = []
        self._model = None
        self._scaler_mean: np.ndarray | None = None
        self._scaler_scale: np.ndarray | None = None

    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: list[str]) -> None:
        """Fit model strictly on chronological training sets with StandardScaler."""
        from sklearn.linear_model import LogisticRegression

        self.feature_names = list(feature_names)
        self._scaler_mean = np.mean(X, axis=0)
        self._scaler_scale = np.std(X, axis=0)
        self._scaler_scale[self._scaler_scale == 0] = 1.0

        X_scaled = (X - self._scaler_mean) / self._scaler_scale

        self._model = LogisticRegression(
            solver="lbfgs",
            max_iter=500,
            random_state=42,
        )
        self._model.fit(X_scaled, y)

    def predict(self, features: ResearchFeatures, horizon_bars: int = 5) -> SignalResult:
        """Produce point-in-time prediction from features."""
        if self._model is None:
            # Fallback if model not yet fitted: return default neutral
            return SignalResult(
                symbol=features.symbol,
                as_of=normalize_datetime(features.as_of),
                horizon_bars=horizon_bars,
                method="ml",
                model_version=self.model_version,
                state="NEUTRAL",
                score=0.0,
                confidence=0.50,
                feature_artifact_ref=features.artifact_ref,
                limitations=["Model not yet fitted on training history."],
            )

        # Prepare feature vector strictly aligned with trained feature_names
        feat_dict = features.features
        x = np.array([feat_dict.get(name, 0.0) for name in self.feature_names]).reshape(1, -1)
        x_scaled = (x - self._scaler_mean) / self._scaler_scale

        probs = self._model.predict_proba(x_scaled)[0]
        # Classes: 0 (BEARISH), 1 (NEUTRAL), 2 (BULLISH)
        classes = list(self._model.classes_)
        prob_dict = {c: probs[i] for i, c in enumerate(classes)}

        p_bear = prob_dict.get(0, 0.0)
        p_bull = prob_dict.get(2, 0.0)

        # Scalar score: p_bull - p_bear in [-1.0, 1.0]
        score = p_bull - p_bear
        pred_class = classes[int(np.argmax(probs))]
        state = STATE_MAP.get(pred_class, "NEUTRAL")
        confidence = float(np.max(probs))

        # Top contributors from logistic regression coefficients
        contributors: list[SignalContributor] = []
        if hasattr(self._model, "coef_"):
            coef = (
                self._model.coef_[pred_class]
                if len(self._model.coef_) > 1
                else self._model.coef_[0]
            )
            for idx, name in enumerate(self.feature_names):
                val = float(x[0, idx])
                weight = float(coef[idx])
                contribution = float(x_scaled[0, idx] * weight)
                direction = (
                    "BULLISH"
                    if contribution > 0.02
                    else ("BEARISH" if contribution < -0.02 else "NEUTRAL")
                )
                contributors.append(
                    SignalContributor(
                        name=name,
                        weight=round(weight, 4),
                        value=round(val, 4),
                        contribution=round(contribution, 4),
                        direction=direction,
                    )
                )
            contributors.sort(key=lambda c: abs(c.contribution), reverse=True)

        return SignalResult(
            symbol=features.symbol,
            as_of=normalize_datetime(features.as_of),
            horizon_bars=horizon_bars,
            method="ml",
            model_version=self.model_version,
            state=state,
            score=round(score, 4),
            confidence=round(confidence, 4),
            feature_artifact_ref=features.artifact_ref,
            top_contributors=contributors[:5],
            evidence_refs=[f"features:{features.symbol}", f"model:{self.model_version}"],
            limitations=[
                f"Statistical model trained on historical walk-forward windows. Calibrated max class probability: {confidence:.1%}.",
                "ML signals are quantitative research inputs and do not guarantee future performance.",
            ],
        )

    def serialize(self) -> bytes:
        return pickle.dumps(self)

    @classmethod
    def deserialize(cls, data: bytes) -> "MLSignalClassifier":
        return pickle.loads(data)
