"""
梅花易数算法模块
基于《易经》的梅花易数预测
"""
from datetime import datetime
from typing import Dict, List, Tuple
import random


# 先天八卦
BAGUA = {
    1: {"name": "乾", "symbol": "☰", "五行": "金", "方位": "西北", "属性": "天"},
    2: {"name": "兑", "symbol": "☱", "五行": "金", "方位": "西", "属性": "泽"},
    3: {"name": "离", "symbol": "☲", "五行": "火", "方位": "南", "属性": "火"},
    4: {"name": "震", "symbol": "☳", "五行": "木", "方位": "东", "属性": "雷"},
    5: {"name": "巽", "symbol": "☴", "五行": "木", "方位": "东南", "属性": "风"},
    6: {"name": "坎", "symbol": "☵", "五行": "水", "方位": "北", "属性": "水"},
    7: {"name": "艮", "symbol": "☶", "五行": "土", "方位": "东北", "属性": "山"},
    8: {"name": "坤", "symbol": "☷", "五行": "土", "方位": "西南", "属性": "地"},
}

# 五行生克
WUXING_RELATIONS = {
    "木": {"生": "火", "克": "土"},
    "火": {"生": "土", "克": "金"},
    "土": {"生": "金", "克": "水"},
    "金": {"生": "水", "克": "木"},
    "水": {"生": "木", "克": "火"},
}

# 方位对应数
DIRECTION_TO_NUM = {
    "北": 1, "南": 3, "东": 4, "西": 2,
    "西北": 1, "东北": 7, "东南": 5, "西南": 8,
    "坎": 1, "离": 3, "震": 4, "兑": 2,
    "巽": 5, "艮": 7, "坤": 8, "乾": 1,
}


def get_gua_number(num: int) -> int:
    """获取卦数（1-8）"""
    return ((num - 1) % 8) + 1


def time_to_gua(year: int, month: int, day: int, hour: int) -> Tuple[int, int]:
    """
    时间起卦法
    上卦：(年+月+日) % 8
    下卦：(年+月+日+时) % 8
    """
    shang = get_gua_number(year + month + day)
    xia = get_gua_number(year + month + day + hour)
    return shang, xia


def direction_to_gua(direction: str) -> int:
    """方位起卦"""
    num = DIRECTION_TO_NUM.get(direction, 5)
    return get_gua_number(num)


def random_gua() -> Tuple[int, int]:
    """随机起卦（用于测试）"""
    return random.randint(1, 8), random.randint(1, 8)


def get_gua_details(num: int) -> Dict:
    """获取卦象详情"""
    return BAGUA.get(num, {"name": "未知", "symbol": "?", "五行": "未知", "方位": "未知", "属性": "未知"})


def analyze_wuxing(wuxing1: str, wuxing2: str) -> Dict:
    """五行生克分析"""
    if wuxing1 == wuxing2:
        return {"关系": "比和", "吉凶": "平", "说明": "五行相同，互相助益"}
    
    # 检查相生
    if WUXING_RELATIONS.get(wuxing1, {}).get("生") == wuxing2:
        return {"关系": "相生", "吉凶": "吉", "说明": f"{wuxing1}生{wuxing2}，主卦生助用神"}
    
    # 检查相克
    if WUXING_RELATIONS.get(wuxing1, {}).get("克") == wuxing2:
        return {"关系": "相克", "吉凶": "凶", "说明": f"{wuxing1}克{wuxing2}，主卦克制用神"}
    
    # 反向检查
    if WUXING_RELATIONS.get(wuxing2, {}).get("生") == wuxing1:
        return {"关系": "相生", "吉凶": "吉", "说明": f"{wuxing2}生{wuxing1}，用神生助主卦"}
    
    if WUXING_RELATIONS.get(wuxing2, {}).get("克") == wuxing1:
        return {"关系": "相克", "吉凶": "凶", "说明": f"{wuxing2}克{wuxing1}，用神克制主卦"}
    
    return {"关系": "无关", "吉凶": "平", "说明": "五行无关"}


def get_yongshen(wuxing: str) -> str:
    """用神（根据问测事项选择）"""
    yongshen_map = {
        "木": "用神为木，利东方、春季",
        "火": "用神为火，利南方、夏季",
        "土": "用神为土，利中央、季月",
        "金": "用神为金，利西方、秋季",
        "水": "用神为水，利北方、冬季",
    }
    return yongshen_map.get(wuxing, "用神待定")


def predict(question: str, method: str = "time", **kwargs) -> Dict:
    """
    梅花易数预测
    
    参数:
        question: 问题描述
        method: 起卦方法 "time"(时间) / "direction"(方位) / "random"(随机)
        **kwargs: method="time"时需要 year,month,day,hour
                  method="direction"时需要 direction
    
    返回:
        预测结果字典
    """
    # 起卦
    basis = {}
    if method == "time":
        year = kwargs.get("year", datetime.now().year)
        month = kwargs.get("month", datetime.now().month)
        day = kwargs.get("day", datetime.now().day)
        hour = kwargs.get("hour", datetime.now().hour)
        shang, xia = time_to_gua(year, month, day, hour)
        basis = {"year": year, "month": month, "day": day, "hour": hour}
    elif method == "direction":
        direction = kwargs.get("direction", "东")
        shang = direction_to_gua(direction)
        xia = random.randint(1, 8)
        basis = {"direction": direction, "direction_num": DIRECTION_TO_NUM.get(direction, 5)}
    else:
        shang, xia = random_gua()
        basis = {"random": True}
    
    # 变卦（动爻）
    bian = get_gua_number(shang + xia + random.randint(1, 6))
    
    # 卦象详情
    shang_detail = get_gua_details(shang)
    xia_detail = get_gua_details(xia)
    bian_detail = get_gua_details(bian)
    
    # 五行分析
    wuxing_analysis = analyze_wuxing(shang_detail["五行"], xia_detail["五行"])
    
    # 判断用神（简化：根据问题判断）
    # 这里可以根据question关键词判断用神
    if any(k in question for k in ["财", "钱", "收入", "盈利"]):
        yongshen = "财"
        yongshen_wuxing = "土"  # 财星
    elif any(k in question for k in ["官", "升职", "事业"]):
        yongshen = "官"
        yongshen_wuxing = "金"  # 官星
    elif any(k in question for k in ["学", "考", "试"]):
        yongshen = "印"
        yongshen_wuxing = "火"  # 印星
    else:
        yongshen = "用神"
        yongshen_wuxing = shang_detail["五行"]
    
    # 预测结果
    result = {
        "question": question,
        "method": method,
        "basis": basis,
        "gua": {
            "主卦": {
                "上卦": shang,
                "下卦": xia,
                "上卦详情": shang_detail,
                "下卦详情": xia_detail,
                "卦名": f"{shang_detail['name']}{xia_detail['name']}"
            },
            "变卦": {
                "动爻": bian,
                "变卦详情": bian_detail,
                "变卦名": f"{bian_detail['name']}{bian_detail['name']}"
            }
        },
        "analysis": {
            "五行分析": wuxing_analysis,
            "用神": yongshen,
            "用神五行": yongshen_wuxing,
            "用神建议": get_yongshen(yongshen_wuxing)
        },
        "prediction": _generate_prediction(wuxing_analysis, shang_detail, xia_detail, bian_detail, question)
    }
    
    return result


def _generate_prediction(wuxing_analysis: Dict, shang: Dict, xia: Dict, bian: Dict, question: str) -> Dict:
    """生成预测结论"""
    
    jixiong = wuxing_analysis.get("吉凶", "平")
    
    if jixiong == "吉":
        jieguo = "大吉"
        jieshi = "五行相生，主卦吉利，事态向好发展"
    elif jixiong == "凶":
        jieguo = "凶"
        jieshi = "五行相克，主卦不利，事态可能遇阻"
    else:
        jieguo = "平"
        jieshi = "五行平和，事态平稳发展"
    
    # 加上变卦影响
    jieshi += f"。变卦{bian['name']}，需关注变化。"
    
    # 建议
    if jixiong == "吉":
        jianyi = "宜把握时机，积极行动"
    elif jixiong == "凶":
        jianyi = "宜静待时机，谨慎行事"
    else:
        jianyi = "宜稳扎稳打，循序渐进"
    
    return {
        "卦象结果": jieguo,
        "解释": jieshi,
        "建议": jianyi,
        "注意": "易经预测仅供参考，人生仍需努力"
    }


def format_result(result: Dict) -> str:
    """格式化预测结果"""
    gua = result["gua"]
    analysis = result["analysis"]
    prediction = result["prediction"]
    
    shang = gua["主卦"]["上卦详情"]
    xia = gua["主卦"]["下卦详情"]
    bian = gua["变卦"]["变卦详情"]
    
    # 起卦依据
    method = result.get("method", "time")
    basis = result.get("basis", {})
    
    if method == "time":
        basis_text = f"""
📐 起卦依据（时间起卦法）：
  年份：{basis.get('year', '?')}
  月份：{basis.get('month', '?')}  
  日期：{basis.get('day', '?')}
  时辰：{basis.get('hour', '?')}
  上卦 = (年+月+日) mod 8 = ({basis.get('year',0)}+{basis.get('month',0)}+{basis.get('day',0)}) mod 8 = {gua['主卦']['上卦']}
  下卦 = (年+月+日+时) mod 8 = ({basis.get('year',0)}+{basis.get('month',0)}+{basis.get('day',0)}+{basis.get('hour',0)}) mod 8 = {gua['主卦']['下卦']}"""
    elif method == "direction":
        basis_text = f"""
📐 起卦依据（方位起卦法）：
  方位：{basis.get('direction', '?')}
  方位对应数：{basis.get('direction_num', '?')}
  上卦 = 方位数 mod 8 = {gua['主卦']['上卦']}
  下卦 = 随机数 = {gua['主卦']['下卦']}"""
    else:
        basis_text = f"""
📐 起卦依据（随机起卦法）：
  随机生成上下卦"""
    
    text = f"""
🔮 梅花易数预测
━━━━━━━━━━━━━━━━━━━━━━━
📋 问题：{result['question']}
📍 方法：{result['method']}
{basis_text}

🏯 卦象：
主卦：{shang['symbol']} {shang['name']} + {xia['symbol']} {xia['name']} = 「{gua['主卦']['卦名']}」
变卦：{bian['symbol']} {bian['name']} + {bian['symbol']} {bian['name']} = 「{gua['变卦']['变卦名']}」

⚖️ 五行分析：
主卦五行：{shang['五行']} + {xia['五行']}
关系：{analysis['五行分析']['关系']}（{analysis['五行分析']['吉凶']}）
{analysis['五行分析']['说明']}

🎯 用神：{analysis['用神']}（{analysis['用神五行']}）
{analysis['用神建议']}

━━━━━━━━━━━━━━━━━━━━━━━
📊 预测结果：{prediction['卦象结果']}
💡 {prediction['解释']}
✅ {prediction['建议']}
⚠️ {prediction['注意']}
━━━━━━━━━━━━━━━━━━━━━━━
"""
    return text


# 测试
if __name__ == "__main__":
    result = predict("最近工作顺利吗？", method="time", 
                    year=2026, month=2, day=27, hour=10)
    print(format_result(result))
