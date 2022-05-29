from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(kw_only=True)
class UIConfig:
    scope: str = None
    primary_metric: UIConfigMetric
    secondary_metric: UIConfigMetric
    menu_visibility: UIConfigVisibility
    judgment_visibility: UIConfigVisibility
    combo_visibility: UIConfigVisibility
    primary_metric_visibility: UIConfigVisibility
    secondary_metric_visibility: UIConfigVisibility
    judgment_animation: UIConfigAnimation
    combo_animation: UIConfigAnimation
    judgment_error_style: UIConfigJudgementErrorStyle
    judgment_error_placement: UIConfigJudgementErrorPlacement
    judgment_error_min: float

    def to_dict(self):
        result = {
            "primaryMetric": self.primary_metric,
            "secondaryMetric": self.secondary_metric,
            "menuVisibility": self.menu_visibility.to_dict(),
            "judgmentVisibility": self.judgment_visibility.to_dict(),
            "comboVisibility": self.combo_visibility.to_dict(),
            "primaryMetricVisibility": self.primary_metric_visibility.to_dict(),
            "secondaryMetricVisibility": self.secondary_metric_visibility.to_dict(),
            "judgmentAnimation": self.judgment_animation.to_dict(),
            "comboAnimation": self.combo_animation.to_dict(),
            "judgmentErrorStyle": self.judgment_error_style,
            "judgmentErrorPlacement": self.judgment_error_placement,
            "judgmentErrorMin": self.judgment_error_min,
        }
        if self.scope is not None:
            result["scope"] = self.scope
        return result


@dataclass(kw_only=True)
class UIConfigVisibility:
    scale: float
    alpha: float

    def to_dict(self):
        return {
            "scale": self.scale,
            "alpha": self.alpha,
        }


@dataclass(kw_only=True)
class UIConfigAnimation:
    scale: UIConfigAnimationTween
    alpha: UIConfigAnimationTween

    def to_dict(self):
        return {
            "scale": self.scale.to_dict(),
            "alpha": self.alpha.to_dict(),
        }


@dataclass(kw_only=True)
class UIConfigAnimationTween:
    start: float
    end: float
    duration: float
    ease: str

    def to_dict(self):
        return {
            "from": self.start,
            "to": self.end,
            "duration": self.duration,
            "ease": self.ease,
        }


UIConfigMetric = Literal["arcade", "accuracy", "life", "perfectRate", "errorHeatmap"]
UIConfigJudgementErrorStyle = Literal[
    "none",
    "plus",
    "minus",
    "arrowUp",
    "arrowDown",
    "arrowLeft",
    "arrowRight",
    "triangleUp",
    "triangleDown",
    "triangleLeft",
    "triangleRight",
]
UIConfigJudgementErrorPlacement = Literal["both", "left", "right"]
