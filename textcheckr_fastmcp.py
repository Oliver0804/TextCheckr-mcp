from fastmcp import FastMCP
import json
import re
import traceback

mcp = FastMCP("TextCheckr")

def analyze_text(input: str) -> dict:
    """分析文本的中文字數、英文字數，檢查括號對稱性，驗證 JSON 格式並計算深度，並分析 markdown 結構，返回詳細報告。"""
    result = {
        "chineseCount": 0,
        "englishCount": 0,
        "wordCount": 0,
        "bracketReport": {
            "round": 0,
            "square": 0,
            "curly": 0,
            "isSymmetric": True,
            "error": ""
        },
        "json": {
            "isValid": False,
            "depth": 0,
            "error": ""
        },
        "markdownReport": {
            "headingCount": 0,
            "headings": [],
            "linkCount": 0,
            "imageCount": 0,
            "codeBlockCount": 0,
            "listCount": 0,
            "error": ""
        }
    }
    
    # 嘗試進行字數統計與括號檢查
    try:
        # 初始化計數
        chinese_count = 0
        english_count = 0
        round_count = square_count = curly_count = 0
        stack = []
        pairs = {'(': ')', '[': ']', '{': '}'}
        is_symmetric = True

        # 英文單詞數量
        word_count = len(re.findall(r'\b[a-zA-Z]+\b', input))

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
            
        # 更新結果
        result["chineseCount"] = chinese_count
        result["englishCount"] = english_count
        result["wordCount"] = word_count
        result["bracketReport"]["round"] = round_count
        result["bracketReport"]["square"] = square_count
        result["bracketReport"]["curly"] = curly_count
        result["bracketReport"]["isSymmetric"] = is_symmetric
    except Exception as e:
        result["bracketReport"]["error"] = f"字數與括號分析時發生錯誤: {str(e)}"

    # 嘗試進行JSON格式驗證
    try:
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
            
        # 更新結果
        result["json"]["isValid"] = is_valid
        result["json"]["depth"] = depth
        result["json"]["error"] = error_msg
    except Exception as e:
        result["json"]["error"] = f"JSON分析時發生未預期錯誤: {str(e)}"

    # 嘗試進行Markdown分析
    try:
        # Markdown 分析
        headings = re.findall(r'^(#{1,6})\s+(.+)$', input, re.MULTILINE)
        heading_count = len(headings)
        heading_list = [f"{h[0]} {h[1]}" for h in headings]
        link_count = len(re.findall(r'\[.*?\]\(.*?\)', input))
        image_count = len(re.findall(r'!\[.*?\]\(.*?\)', input))
        code_block_count = len(re.findall(r'```[\s\S]*?```', input))
        list_count = len(re.findall(r'^\s*[-*+]\s+', input, re.MULTILINE))
        
        # 更新結果
        result["markdownReport"]["headingCount"] = heading_count
        result["markdownReport"]["headings"] = heading_list
        result["markdownReport"]["linkCount"] = link_count
        result["markdownReport"]["imageCount"] = image_count
        result["markdownReport"]["codeBlockCount"] = code_block_count
        result["markdownReport"]["listCount"] = list_count
    except Exception as e:
        result["markdownReport"]["error"] = f"Markdown分析時發生錯誤: {str(e)}"

    return result

@mcp.tool()
def analyze_text_tool(input: str) -> dict:
    """Tool: 分析文件的括號對稱、JSON 格式、字數、結構層數與 markdown 結構"""
    try:
        # 檢查輸入是否為空
        if not input or len(input.strip()) == 0:
            return {
                "error": True,
                "message": "輸入文本為空，請提供有效的文本內容進行分析。"
            }
            
        # 檢查輸入長度，防止太長的文本導致處理問題
        max_length = 50000  # 設定合理的最大長度限制
        if len(input) > max_length:
            return {
                "error": True, 
                "message": f"輸入文本過長，請將文本控制在 {max_length} 字元以內。目前長度：{len(input)} 字元。"
            }
            
        # 處理文本分析
        result = analyze_text(input)
        
        # 檢查結果是否包含錯誤信息
        has_error = (
            result.get("bracketReport", {}).get("error") or 
            result.get("json", {}).get("error") or 
            result.get("markdownReport", {}).get("error")
        )
        
        if has_error:
            result["warning"] = "部分分析可能不完整，請查看各部分的錯誤信息。"
        
        return result
    except json.JSONDecodeError as e:
        return {
            "error": True,
            "message": f"JSON 解析錯誤: {str(e)}"
        }
    except RecursionError as e:
        return {
            "error": True,
            "message": "文本結構過於複雜，導致處理超出系統限制。請嘗試減少嵌套層級或縮短文本。"
        }
    except Exception as e:
        # 捕獲所有其他異常，確保始終能返回響應
        error_details = traceback.format_exc()
        return {
            "error": True,
            "message": f"處理文本時發生未預期錯誤: {str(e)}",
            "details": error_details[:500] if len(error_details) > 500 else error_details  # 限制詳細信息的長度
        }

if __name__ == "__main__":
    mcp.run()
