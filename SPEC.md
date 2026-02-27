# 预测系统规范

## 项目概述
- **项目名称**: Future Predictor
- **类型**: 命令行工具 + Python库
- **核心功能**: 基于模板和GLM AI API进行未来走向预测
- **目标用户**: 需要对未来事件进行分析预测的用户

## 功能规范

### 核心功能

1. **模板管理**
   - 支持创建、编辑、删除预测模板
   - 模板格式为Markdown
   - 支持变量占位符 `{variable_name}`
   - 模板存储在 `templates/` 目录

2. **变量填充**
   - 运行时指定变量值
   - 支持JSON格式批量输入变量

3. **预测执行**
   - 调用GLM API生成预测
   - 支持自定义系统提示词
   - 返回Markdown格式预测结果

4. **历史记录**
   - 保存预测历史到 `predictions/` 目录
   - 可查看历史预测

### CLI命令

```bash
# 初始化项目
predictor init

# 创建模板
predictor create-template <name> -t <template_file.md>

# 列出模板
predictor list-templates

# 执行预测
predictor predict <template_name> -v '{"var1": "value1", "var2": "value2"}'

# 查看历史
predictor history

# 查看版本
predictor version
```

### API设计

```python
from predictor import Predictor

# 初始化
p = Predictor(glm_api_key="your-key", glm_base_url="https://open.bigmodel.cn/api/paas/v4")

# 创建模板
p.create_template("stock_trend", "股票走势预测模板.md")

# 执行预测
result = p.predict("stock_trend", variables={"股票代码": "600519", "时间范围": "一个月"})
```

## 技术实现

- Python 3.8+
- 依赖: requests, rich
- API: GLM-4-Flash (免费)
- 配置文件: `~/.predictor/config.json`

## 验收标准

1. ✅ 可创建Markdown模板
2. ✅ 支持变量替换
3. ✅ 调用GLM API返回预测结果
4. ✅ 保存预测历史
5. ✅ CLI工具完整可用
