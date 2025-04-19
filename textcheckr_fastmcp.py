from fastmcp import FastMCP
import json
import re

mcp = FastMCP("TextCheckr")

def analyze_text(input: str) -> dict:
    """分析文本的中文字數、英文字數，檢查括號對稱性，驗證 JSON 格式並計算深度，並分析 markdown 結構，返回詳細報告。"""
    # 初始化計數
    chinese_count = 0
    english_count = 0
    round_count = square_count = curly_count = 0
    stack = []
    pairs = {'(': ')', '[': ']', '{': '}'}
    is_symmetric = True

    # 一次遍歷完成所有統計和對稱檢查
    for c in input:
        # 中文字符（基本 CJK 區）
        if '\u4e00' <= c <= '\u9fff':
            chinese_count += 1
        # 英文字母（ASCII 範圍）
        elif c.isalpha() and c.isascii():
            english_count += 1

        # 括號數量統計
        if c in '()':
            round_count += 1
        elif c in '[]':
            square_count += 1
        elif c in '{}':
            curly_count += 1

        # 括號對稱性檢查
        if c in pairs:
            stack.append(c)
        elif c in pairs.values():
            if not stack or pairs[stack.pop()] != c:
                is_symmetric = False

    # 如果遍歷結束後仍有未匹配的左括號
    if stack:
        is_symmetric = False

    # JSON 格式驗證與深度計算
    is_valid = False
    depth = 0
    error_msg = ""
    try:
        obj = json.loads(input)
        is_valid = True

        def calc_depth(val) -> int:
            if not isinstance(val, (dict, list)):
                return 0
            if isinstance(val, list):
                if not val:
                    return 1
                return 1 + max(calc_depth(v) for v in val)
            else:
                if not val:
                    return 1
                return 1 + max(calc_depth(v) for v in val.values())

        depth = calc_depth(obj)
    except json.JSONDecodeError as e:
        error_msg = f"JSON 解析錯誤: {e}"
    except RecursionError:
        error_msg = "JSON 深度超過遞歸限制"
    except Exception as e:
        error_msg = str(e)

    # Markdown 分析
    headings = re.findall(r'^(#{1,6})\s+(.+)$', input, re.MULTILINE)
    heading_count = len(headings)
    heading_list = [f"{h[0]} {h[1]}" for h in headings]
    link_count = len(re.findall(r'\[.*?\]\(.*?\)', input))
    image_count = len(re.findall(r'!\[.*?\]\(.*?\)', input))
    code_block_count = len(re.findall(r'```[\s\S]*?```', input))
    list_count = len(re.findall(r'^\s*[-*+]\s+', input, re.MULTILINE))

    markdown_report = {
        "headingCount": heading_count,
        "headings": heading_list,
        "linkCount": link_count,
        "imageCount": image_count,
        "codeBlockCount": code_block_count,
        "listCount": list_count
    }

    return {
        "chineseCount": chinese_count,
        "englishCount": english_count,
        "bracketReport": {
            "round": round_count,
            "square": square_count,
            "curly": curly_count,
            "isSymmetric": is_symmetric
        },
        "json": {
            "isValid": is_valid,
            "depth": depth,
            "error": error_msg
        },
        "markdownReport": markdown_report
    }

@mcp.tool()
def analyze_text_tool(input: str) -> dict:
    """Tool: 分析文件的括號對稱、JSON 格式、字數、結構層數與 markdown 結構"""
    return analyze_text(input)

if __name__ == "__main__":
    mcp.run()
