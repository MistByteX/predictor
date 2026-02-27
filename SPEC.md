# 预测系统规范 (v0.2.0)

## 项目概述
- **项目名称**: Future Predictor
- **类型**: 命令行工具 + Python库
- **核心功能**: 基于GLM AI的通用预测系统，支持梅花易数和多Agent模拟
- **目标用户**: 需要对未来事件进行分析预测的用户

## 核心目标
**无论给什么事件都能准确预测 - 统一模板系统**

## 功能规范

### 1. 统一模板系统
- 只有一套通用模板 `universal.md`
- 适用于任何类型事件的预测
- 变量可自由定义

### 2. 梅花易数集成（可选）
- 通过 `--meihua` 或 `-m` 开启
- 自动调用梅花易数算法
- 结果自动附加到预测输出中

### 3. 多Agent模拟（可选）
- 通过 `--agents` 或 `-a` 指定Agent数量
- 每个Agent独立分析事件发展
- 模拟不同视角下的事件演进

### 4. 直接提问模式
```bash
# 简单预测
predictor ask "明天天气怎么样"

# 启用梅花易数
predictor ask "我的事业发展如何" -m

# 启用多Agent模拟
predictor ask "这个项目能成功吗" -a 3

# 同时启用
predictor ask "这笔投资能赚钱吗" -m -a 3
```

### 5. 模板预测模式
```bash
# 使用模板预测
predictor predict universal -v '{"事件描述": "...", "时间": "..."}' -m -a 2
```

### CLI命令

```bash
# 初始化
predictor init

# 直接提问（推荐）
predictor ask <事件描述> [选项]

# 梅花易数单独预测
predictor yi <问题>

# 其他命令
predictor list-templates
predictor history
predictor algo -d "1,2,3,4,5"
```

## 技术实现

- Python 3.8+
- 依赖: requests, rich
- API: GLM-4-Flash (免费)
- 配置文件: `~/.predictor/config.json`

## 验收标准

1. ✅ 统一模板适用任何事件
2. ✅ 梅花易数自动集成
3. ✅ 多Agent模拟支持
4. ✅ CLI工具完整可用
