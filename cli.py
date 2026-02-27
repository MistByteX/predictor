#!/usr/bin/env python3
"""
预测系统CLI工具
"""
import sys
import os
import json
import re
import argparse
from datetime import datetime
from pathlib import Path
import requests
from algorithms import ALGORITHMS, EnsemblePredictor
from meihua import predict, format_result

# 配置路径
CONFIG_DIR = Path.home() / ".predictor"
CONFIG_FILE = CONFIG_DIR / "config.json"
TEMPLATES_DIR = Path(__file__).parent / "templates"
PREDICTIONS_DIR = Path(__file__).parent / "predictions"

__version__ = "0.1.0"


def get_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_config(config: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def fill_template(template: str, variables: dict) -> str:
    result = template
    for key, value in variables.items():
        result = result.replace(f"{{{key}}}", str(value))
    unfilled = re.findall(r'\{([^}]+)\}', result)
    if unfilled:
        raise ValueError(f"未填充的变量: {', '.join(unfilled)}")
    return result


class Predictor:
    def __init__(self, glm_api_key: str = None, glm_base_url: str = None):
        config = get_config()
        self.api_key = glm_api_key or config.get("glm_api_key")
        self.base_url = glm_base_url or config.get("glm_base_url", "https://open.bigmodel.cn/api/paas/v4")
        if not self.api_key:
            raise ValueError("请设置GLM API Key: predictor config set api_key <your_key>")
    
    def call_glm(self, prompt: str, system_prompt: str = None) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": "glm-4-flash",
            "messages": messages,
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=120)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    def create_template(self, name: str, content: str = None, template_file: str = None):
        TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
        if template_file:
            with open(template_file, encoding="utf-8") as f:
                content = f.read()
        if not content:
            raise ValueError("需要提供模板内容")
        template_path = TEMPLATES_DIR / f"{name}.md"
        with open(template_path, "w", encoding="utf-8") as f:
            f.write(content)
        return str(template_path)
    
    def list_templates(self):
        TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
        return [f.stem for f in TEMPLATES_DIR.glob("*.md")]
    
    def get_template(self, name: str) -> str:
        template_path = TEMPLATES_DIR / f"{name}.md"
        if not template_path.exists():
            raise FileNotFoundError(f"模板不存在: {name}")
        with open(template_path, encoding="utf-8") as f:
            return f.read()
    
    def predict(self, template_name: str, variables: dict = None, system_prompt: str = None) -> dict:
        template = self.get_template(template_name)
        if variables:
            prompt = fill_template(template, variables)
        else:
            prompt = template
        
        prediction = self.call_glm(prompt, system_prompt)
        
        PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        record = {
            "template": template_name,
            "variables": variables or {},
            "prompt": prompt,
            "prediction": prediction,
            "timestamp": timestamp
        }
        
        history_file = PREDICTIONS_DIR / f"{timestamp}.json"
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        
        return {
            "prompt": prompt,
            "prediction": prediction,
            "history_file": str(history_file)
        }
    
    def history(self, limit: int = 10):
        PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)
        files = sorted(PREDICTIONS_DIR.glob("*.json"), reverse=True)[:limit]
        records = []
        for f in files:
            with open(f, encoding="utf-8") as fp:
                data = json.load(fp)
                records.append({
                    "timestamp": data["timestamp"],
                    "template": data["template"],
                    "prediction": data["prediction"][:100] + "..."
                })
        return records


def cmd_init(args):
    config = get_config()
    if not config:
        api_key = args.api_key or input("请设置GLM API Key: ").strip()
        if api_key:
            config["glm_api_key"] = api_key
            config["glm_base_url"] = "https://open.bigmodel.cn/api/paas/v4"
            save_config(config)
            print("✅ 配置已保存")
        else:
            print("❌ 需要API Key")
            sys.exit(1)
    else:
        print("已存在配置:", config)
    return 0


def cmd_config(args):
    config = get_config()
    if args.subcommand == "show":
        if config:
            print(json.dumps(config, ensure_ascii=False, indent=2))
        else:
            print("未配置，请先运行 predictor init")
        return 0
    if args.subcommand == "set":
        if args.key == "api_key":
            config["glm_api_key"] = args.value
            save_config(config)
            print(f"✅ 已设置 glm_api_key")
        elif args.key == "base_url":
            config["glm_base_url"] = args.value
            save_config(config)
            print(f"✅ 已设置 glm_base_url")
        else:
            print(f"❌ 未知配置项: {args.key}")
            sys.exit(1)
        return 0


def cmd_create_template(args):
    try:
        p = Predictor(glm_api_key=args.api_key)
        path = p.create_template(args.name, template_file=args.file)
        print(f"✅ 模板已创建: {path}")
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)
    return 0


def cmd_list_templates(args):
    try:
        p = Predictor(glm_api_key=args.api_key)
        templates = p.list_templates()
        if templates:
            print("📋 模板列表:")
            for t in templates:
                print(f"  - {t}")
        else:
            print("暂无模板，请先创建")
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)
    return 0


def cmd_predict(args):
    try:
        p = Predictor(glm_api_key=args.api_key)
        variables = None
        if args.variables:
            variables = json.loads(args.variables)
        
        # 多次预测
        if args.times > 1:
            print(f"\n🔄 开始{args.times}次预测取平均...")
            predictions = []
            for i in range(args.times):
                print(f"  [{i+1}/{args.times}] ", end="", flush=True)
                result = p.predict(args.template, variables=variables)
                predictions.append(result["prediction"])
                print("✓")
            
            # 合并结果
            print("\n" + "="*50)
            print(f"📊 预测结果（{args.times}次综合）:")
            print("="*50)
            for i, pred in enumerate(predictions, 1):
                print(f"\n--- 第{i}次预测 ---\n{pred[:300]}...")
            print("="*50)
            print(f"\n📁 已保存{len(predictions)}条记录")
        else:
            result = p.predict(args.template, variables=variables)
            print("\n" + "="*50)
            print("📊 预测结果:")
            print("="*50)
            print(result["prediction"])
            print("="*50)
            print(f"📁 已保存至: {result['history_file']}")
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)
    return 0


def cmd_history(args):
    try:
        p = Predictor(glm_api_key=args.api_key)
        records = p.history(limit=args.limit)
        if records:
            print("📜 预测历史:")
            for r in records:
                print(f"\n[{r['timestamp']}] {r['template']}")
                print(f"  {r['prediction']}")
        else:
            print("暂无历史记录")
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)
    return 0


def cmd_template(args):
    try:
        p = Predictor(glm_api_key=args.api_key)
        content = p.get_template(args.name)
        print(content)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        sys.exit(1)
    return 0


def cmd_algo_predict(args):
    """算法预测"""
    try:
        # 解析数据
        data = [float(x.strip()) for x in args.data.split(",")]
        
        # 获取算法
        if args.algorithm == "ensemble":
            predictor = EnsemblePredictor()
            result = predictor.predict(data, steps=args.steps)
            
            print("\n" + "="*50)
            print("📊 算法预测结果:")
            print("="*50)
            
            print(f"\n🔍 趋势分析:")
            trend = result["trend"]
            print(f"  趋势方向: {trend['trend']}")
            print(f"  趋势强度: {trend['strength']}")
            print(f"  平均变化率: {trend['avg_change_rate']}%")
            print(f"  波动性: {trend['volatility']}")
            print(f"  置信度: {trend['confidence']}")
            
            print(f"\n🔢 各算法预测:")
            for name, pred in result["predictions"].items():
                if isinstance(pred, (int, float)):
                    print(f"  {name}: {pred:.2f}")
            
            print(f"\n🎯 综合预测: {result['ensemble']}")
            print("="*50)
        else:
            if args.algorithm not in ALGORITHMS:
                print(f"❌ 未知算法: {args.algorithm}")
                sys.exit(1)
            
            algo = ALGORITHMS[args.algorithm]()
            pred = algo.predict(data, steps=args.steps)
            
            print("\n" + "="*50)
            print(f"📊 {args.algorithm} 预测结果:")
            print("="*50)
            print(f"预测值: {pred}")
            print("="*50)
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)
    return 0


def cmd_yi_predict(args):
    """梅花易数预测"""
    try:
        kwargs = {}
        if args.method == "time":
            now = datetime.now()
            kwargs["year"] = args.year or now.year
            kwargs["month"] = args.month or now.month
            kwargs["day"] = args.day or now.day
            kwargs["hour"] = args.hour or now.hour
        elif args.method == "direction":
            if not args.direction:
                print("❌ 方位起卦需要指定 --direction")
                sys.exit(1)
            kwargs["direction"] = args.direction
        
        result = predict(args.question, method=args.method, **kwargs)
        print(format_result(result))
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)
    return 0


def main():
    parser = argparse.ArgumentParser(prog="predictor", description="未来预测系统")
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    parser.add_argument("--api-key", dest="api_key", help="GLM API Key")
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    parser_init = subparsers.add_parser("init", help="初始化配置")
    parser_init.set_defaults(func=cmd_init)
    
    parser_config = subparsers.add_parser("config", help="配置管理")
    config_sub = parser_config.add_subparsers(dest="subcommand", help="配置子命令")
    config_show = config_sub.add_parser("show", help="显示配置")
    config_show.set_defaults(func=cmd_config)
    config_set = config_sub.add_parser("set", help="设置配置")
    config_set.add_argument("key", help="配置项")
    config_set.add_argument("value", help="配置值")
    config_set.set_defaults(func=cmd_config)
    
    parser_ct = subparsers.add_parser("create-template", help="创建模板")
    parser_ct.add_argument("name", help="模板名称")
    parser_ct.add_argument("-f", "--file", help="模板文件路径")
    parser_ct.set_defaults(func=cmd_create_template)
    
    parser_lt = subparsers.add_parser("list-templates", help="列出模板")
    parser_lt.set_defaults(func=cmd_list_templates)
    
    parser_tpl = subparsers.add_parser("template", help="查看模板")
    parser_tpl.add_argument("name", help="模板名称")
    parser_tpl.set_defaults(func=cmd_template)
    
    parser_pred = subparsers.add_parser("predict", help="执行预测")
    parser_pred.add_argument("template", help="模板名称")
    parser_pred.add_argument("-v", "--variables", help="JSON格式变量")
    parser_pred.add_argument("-n", "--times", type=int, default=1, help="预测次数（取平均）")
    parser_pred.set_defaults(func=cmd_predict)
    
    parser_hist = subparsers.add_parser("history", help="查看历史")
    parser_hist.add_argument("-n", "--limit", type=int, default=10, help="显示条数")
    parser_hist.set_defaults(func=cmd_history)
    
    # 算法预测
    parser_algo = subparsers.add_parser("algo", help="算法预测")
    parser_algo.add_argument("-d", "--data", required=True, help="历史数据，逗号分隔")
    parser_algo.add_argument("-s", "--steps", type=int, default=1, help="预测步数")
    parser_algo.add_argument("-a", "--algorithm", default="ensemble", help="算法: ma/ema/linear/poly/ensemble")
    parser_algo.set_defaults(func=cmd_algo_predict)
    
    # 梅花易数
    parser_yi = subparsers.add_parser("yi", help="梅花易数预测")
    parser_yi.add_argument("question", help="预测问题")
    parser_yi.add_argument("-m", "--method", default="time", choices=["time", "direction", "random"], help="起卦方式")
    parser_yi.add_argument("-y", "--year", type=int, help="年份")
    parser_yi.add_argument("--month", type=int, help="月份")
    parser_yi.add_argument("--day", type=int, help="日期")
    parser_yi.add_argument("--hour", type=int, help="小时")
    parser_yi.add_argument("--direction", help="方位（如：东、西北）")
    parser_yi.set_defaults(func=cmd_yi_predict)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
