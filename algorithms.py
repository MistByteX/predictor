"""
预测算法模块 - 纯Python实现
"""
import math
from typing import List, Dict


class MovingAverage:
    """移动平均预测"""
    
    def __init__(self, window: int = 5):
        self.window = window
    
    def predict(self, data: List[float], steps: int = 1) -> List[float]:
        if len(data) < self.window:
            return [sum(data) / len(data)] * steps
        
        ma = sum(data[-self.window:]) / self.window
        return [ma] * steps


class ExponentialSmoothing:
    """指数平滑预测"""
    
    def __init__(self, alpha: float = 0.3):
        self.alpha = alpha
    
    def predict(self, data: List[float], steps: int = 1) -> List[float]:
        if not data:
            return [0] * steps
        
        result = [data[0]]
        for val in data[1:]:
            result.append(self.alpha * val + (1 - self.alpha) * result[-1])
        
        return [result[-1]] * steps


class LinearRegression:
    """线性回归预测"""
    
    def __init__(self):
        self.slope = 0
        self.intercept = 0
    
    def fit(self, data: List[float]):
        n = len(data)
        if n < 2:
            self.slope = 0
            self.intercept = sum(data) / n
            return
        
        x_mean = (n - 1) / 2
        y_mean = sum(data) / n
        
        numerator = sum((i - x_mean) * (data[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            self.slope = 0
        else:
            self.slope = numerator / denominator
        
        self.intercept = y_mean - self.slope * x_mean
    
    def predict(self, data: List[float], steps: int = 1) -> List[float]:
        self.fit(data)
        n = len(data)
        return [self.slope * (n + i) + self.intercept for i in range(1, steps + 1)]


class TrendAnalysis:
    """趋势分析"""
    
    def analyze(self, data: List[float]) -> Dict:
        if len(data) < 2:
            return {"trend": "unknown", "strength": 0}
        
        changes = []
        for i in range(1, len(data)):
            if data[i-1] != 0:
                changes.append((data[i] - data[i-1]) / data[i-1])
        
        if not changes:
            return {"trend": "unknown", "strength": 0}
        
        avg_change = sum(changes) / len(changes)
        
        if avg_change > 0.05:
            trend = "上涨"
            strength = min(abs(avg_change) * 10, 1.0)
        elif avg_change < -0.05:
            trend = "下跌"
            strength = min(abs(avg_change) * 10, 1.0)
        else:
            trend = "震荡"
            strength = 0.5
        
        # 波动性
        mean = sum(changes) / len(changes)
        variance = sum((c - mean) ** 2 for c in changes) / len(changes)
        volatility = math.sqrt(variance)
        
        # 置信度
        positive = sum(1 for c in changes if c > 0)
        negative = sum(1 for c in changes if c < 0)
        confidence = max(positive, negative) / len(changes)
        
        return {
            "trend": trend,
            "strength": round(strength, 2),
            "avg_change_rate": round(avg_change * 100, 2),
            "volatility": round(volatility, 4),
            "confidence": round(confidence, 2)
        }


class EnsemblePredictor:
    """集成预测器"""
    
    def __init__(self):
        self.algorithms = {
            "ma": MovingAverage(window=5),
            "ema": ExponentialSmoothing(alpha=0.3),
            "linear": LinearRegression()
        }
        self.trend = TrendAnalysis()
    
    def predict(self, data: List[float], steps: int = 1) -> Dict:
        if len(data) < 3:
            return {"error": "数据量不足，需要至少3个数据点", "results": {}}
        
        trend_result = self.trend.analyze(data)
        
        predictions = {}
        for name, algo in self.algorithms.items():
            try:
                pred = algo.predict(data, steps)
                # 取第一个预测值
                predictions[name] = pred[0] if isinstance(pred, list) else pred
            except Exception as e:
                predictions[name] = str(e)
        
        # 加权平均
        weights = {"ma": 0.3, "ema": 0.35, "linear": 0.35}
        total = 0
        weight_sum = 0
        for k in weights:
            if isinstance(predictions.get(k), (int, float)):
                total += predictions[k] * weights[k]
                weight_sum += weights[k]
        ensemble = total / weight_sum if weight_sum > 0 else 0
        
        return {
            "trend": trend_result,
            "predictions": predictions,
            "ensemble": round(ensemble, 2),
            "steps": steps
        }


ALGORITHMS = {
    "ma": MovingAverage,
    "ema": ExponentialSmoothing,
    "linear": LinearRegression,
    "trend": TrendAnalysis,
    "ensemble": EnsemblePredictor
}
