# TextCheckr-mcp

文件括號、JSON 結構、字數分析的 MCP 工具，支援 cline 平台自動化文件結構檢查。

## 主要功能

- 檢查括號 () [] {} 是否對稱
- 驗證 JSON 格式與計算最大巢狀層數
- 統計中文字數、英文字數、各種括號數量
- MCP 工具介面，支援 cline 自動化調用

## 安裝步驟

1. **Clone 專案**
   ```bash
   git clone https://github.com/Oliver0804/TextCheckr-mcp.git
   cd TextCheckr-mcp
   ```

2. **建立 Python 環境並安裝依賴**
   建議使用 conda 或 venv，Python 3.8+。
   ```bash
   conda create -n mcp python=3.12
   conda activate mcp
   pip install fastmcp
   ```

3. **測試本地啟動**
   ```bash
   python textcheckr_fastmcp.py
   ```
   若看到 `Starting server "TextCheckr"...` 表示啟動成功。

## cline MCP 設定範例

請在 `cline_mcp_settings.json` 的 `"mcpServers"` 欄位加入：

```json
"textcheckr-mcp": {
  "autoApprove": [
    "analyze_text"
  ],
  "disabled": false,
  "timeout": 60,
  "command": "/Users/oliver/anaconda3/envs/mcp/bin/python",
  "args": [
    "/Users/oliver/code/mcp/TextCheckr-mcp/textcheckr_fastmcp.py"
  ],
  "transportType": "stdio"
}
```
> 請依實際 Python 路徑與專案路徑調整。

## 工具說明

- analyze_text(input: str): 回傳分析報告，格式如下
  ```json
  {
    "chineseCount": 5,
    "englishCount": 8,
    "bracketReport": {
      "round": 2,
      "square": 2,
      "curly": 2,
      "isSymmetric": true
    },
    "json": {
      "isValid": true,
      "depth": 3
    }
  }
  ```

## 參考

- [TextCheckr-mcp GitHub Repo](https://github.com/Oliver0804/TextCheckr-mcp)
- [fastmcp 官方文件](https://github.com/jlowin/fastmcp)
