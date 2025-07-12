from frappeclient import FrappeClient
import json

def generate_mcp_tools(client, output_path="erpnext_all_doctypes_mcp.json"):
    """生成所有 Doctype 的 MCP 工具描述并保存为 JSON 文件"""

    def get_all_doctypes(client):
        """从 ERPNext 获取所有有效 Doctype 名称"""
        docs = client.get_list("DocType", fields=["name"], limit_page_length=9999)
        return [d["name"] for d in docs if d["name"] not in ("DocType", "DocField", "DocPerm")]

    def convert_frappe_doctype_to_mcp_tool(doctype_meta):
        """将 Doctype 转换为 MCP 工具条目（包含增删改查）"""
        doctype_name = doctype_meta["name"]
        fields = doctype_meta.get("fields", [])

        properties = {}
        required_fields = []
        for f in fields:
            fieldname = f.get("fieldname")
            if not fieldname:
                continue
            properties[fieldname] = {"type": "string"}
            if f.get("reqd"):
                required_fields.append(fieldname)

        input_schema = {
            "type": "object",
            "properties": properties
        }
        if required_fields:
            input_schema["required"] = required_fields

        tools = [
            {
                "name": f"create_{doctype_name.lower()}",
                "description": f"在 ERPNext 中创建 {doctype_name}",
                "inputSchema": input_schema
            },
            {
                "name": f"read_{doctype_name.lower()}",
                "description": f"根据名称读取 {doctype_name} 文档",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"}
                    },
                    "required": ["name"]
                }
            },
            {
                "name": f"update_{doctype_name.lower()}",
                "description": f"根据名称更新 {doctype_name} 文档",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "data": input_schema
                    },
                    "required": ["name", "data"]
                }
            },
            {
                "name": f"delete_{doctype_name.lower()}",
                "description": f"根据名称删除 {doctype_name} 文档",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"}
                    },
                    "required": ["name"]
                }
            }
        ]
        return tools

    # 初始化 MCP JSON 基础结构
    mcp_dict = {
        "erpnext-mcp": {
            "name": "erpnext-mcp",
            "display_name": "ERPNext Server",
            "description": "MCP-compatible ERPNext API server",
            "repository": {
                "type": "git",
                "url": "https://github.com/frappe/frappe"
            },
            "homepage": "https://erpnext.com",
            "author": {
                "name": "Frappe Technologies",
                "url": "https://frappe.io"
            },
            "license": "MIT",
            "categories": ["Finance", "Web Services"],
            "tags": ["erpnext", "frappe", "accounting"],
            "installations": {
                "manual": {
                    "type": "manual",
                    "description": "调用已有的 ERPNext API 服务，无需安装",
                    "recommended": True
                }
            },
            "tools": [],
            "arguments": {
                "ERP_URL": {
                    "description": "ERPNext 服务器的基地址",
                    "required": True,
                    "example": "http://site1.localhost:8000"
                },
                "API_KEY": {
                    "description": "用于访问 ERPNext API 的 API Key",
                    "required": True,
                    "example": "your-api-key"
                },
                "API_SECRET": {
                    "description": "用于访问 ERPNext API 的 API Secret",
                    "required": True,
                    "example": "your-api-secret"
                }
            },
            "examples": [],
            "is_official": False
        }
    }

    all_doctypes = get_all_doctypes(client)

    for doctype in all_doctypes:
        try:
            meta = client.get_doc("DocType", doctype)
            tools = convert_frappe_doctype_to_mcp_tool(meta)
            mcp_dict["erpnext-mcp"]["tools"].extend(tools)
        except Exception as e:
            print(f"⚠️ 跳过 {doctype}：{e}")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(mcp_dict, f, indent=2, ensure_ascii=False)

    print(f"✅ MCP 工具文件已生成：{output_path}")

if __name__ == "__main__":
    client = FrappeClient("http://site1.localhost:8000")
    client.login("Administrator", "admin")
    # 生成 MCP 工具格式
    mcp_json = generate_mcp_tools(client, output_path="erpnext_mcp.json")
