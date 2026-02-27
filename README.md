# Predictor

## 万物预测系统

- GLM AI 预测 - 调用GLM大模型进行万物预测
- 梅花易数 - 基于《易经》的传统预测算法
- 算法预测 - 移动平均、指数平滑、线性回归

## 安装

pip install --break-system-packages requests

## 使用

### 1. 初始化配置
python cli.py init --api-key <your_glm_api_key>

### 2. 万物预测
python cli.py predict universal -v '{"地点":"北京","日期":"明天","当前天气":"晴"}'

### 3. 梅花易数
python cli.py yi "最近工作顺利吗" -m time

## License
MIT
