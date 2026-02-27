"""
Future Predictor - 基于GLM AI的预测系统
"""
import os
import json
import re
from datetime import datetime
from pathlib import Path
import requests

__version__ = "0.1.0"

CONFIG_DIR = Path.home() / ".predictor"
CONFIG_FILE = CONFIG_DIR / "config.json"
TEMPLATES_DIR = Path("templates")
PREDICTIONS_DIR = Path("predictions")


def get_config() -> dict:
    """获取配置"""
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_config(config: dict):
    """保存配置"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def fill_template(template: str, variables: dict) -> str:
    """填充模板变量"""
    result = template
    for key, value in variables.items():
        result = result.replace(f"{{{key}}}", str(value))
    # 检查未填充的变量
    unfilled = re.findall(r'\{([^}]+)\}', result)
    if unfilled:
        raise ValueError(f"未填充的变量: {', '.join(unfilled)}")
    return result


class Predictor:
    """预测器"""
    
    def __init__(self, glm_api_key: str = None, glm_base_url: str = None):
        config = get_config()
        self.api_key = glm_api_key or config.get("glm_api_key")
        self.base_url = glm_base_url or config.get("glm_base_url", "https://open.bigmodel.cn/api/paas/v4")
        if not self.api_key:
            raise ValueError("请设置GLM API Key: predictor config set api_key <your_key>")
    
    def call_glm(self, prompt: str, system_prompt: str = None) -> str:
        """调用GLM API"""
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
        """创建模板"""
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
        """列出所有模板"""
        TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
        templates = []
        for f in TEMPLATES_DIR.glob("*.md"):
            templates.append(f.stem)
        return templates
    
    def get_template(self, name: str) -> str:
        """获取模板内容"""
        template_path = TEMPLATES_DIR / f"{name}.md"
        if not template_path.exists():
            raise FileNotFoundError(f"模板不存在: {name}")
        with open(template_path, encoding="utf-8") as f:
            return f.read()
    
    def predict(self, template_name: str, variables: dict = None, system_prompt: str = None) -> dict:
        """执行预测"""
        # 获取模板
        template = self.get_template(template_name)
        
        # 填充变量
        if variables:
            prompt = fill_template(template, variables)
        else:
            # 尝试提取变量
            prompt = template
        
        # 调用API
        prediction = self.call_glm(prompt, system_prompt)
        
        # 保存历史
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
        """查看预测历史"""
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
