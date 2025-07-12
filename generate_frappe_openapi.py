import json
from frappeclient import FrappeClient

# 类型映射
type_map = {
    "Data": ("string", None),
    "Small Text": ("string", None),
    "Text": ("string", None),
    "Text Editor": ("string", None),
    "Check": ("integer", "int32"),
    "Int": ("integer", "int32"),
    "Float": ("number", "float"),
    "Currency": ("number", "float"),
    "Date": ("string", "date"),
    "Datetime": ("string", "date-time"),
    "Time": ("string", "date-time"),
    "Select": ("string", None),
    "Link": ("string", None),
    "Table": ("array", None),
}

def get_all_doctypes(client):
    """获取所有 Doctype 名称"""
    doctype_docs = client.get_list("DocType", fields=["name"], limit_page_length=9999)
    return [doc["name"] for doc in doctype_docs]

def frappe_doctype_to_openapi_schema(client, doctype_name):
    """将 Frappe 的 DocType 转为 OpenAPI Schema"""
    doctype_meta = client.get_doc("DocType", doctype_name)
    fields = doctype_meta.get("fields", [])

    schema = {
        "title": doctype_name,
        "type": "object",
        "properties": {},
        "required": [],
    }

    for field in fields:
        fieldname = field.get("fieldname")
        fieldtype = field.get("fieldtype")
        label = field.get("label", "")
        options = field.get("options", "")

        if not fieldname:
            continue

        openapi_type, openapi_format = type_map.get(fieldtype, ("string", None))
        prop = {
            "type": openapi_type,
            "description": label or fieldname
        }
        if openapi_format:
            prop["format"] = openapi_format

        if fieldtype == "Select" and options:
            enum_values = [x.strip() for x in options.split("\n") if x.strip()]
            prop["enum"] = enum_values

        if fieldtype == "Table" and options:
            prop["items"] = {"$ref": f"#/components/schemas/{options}"}

        schema["properties"][fieldname] = prop

        if field.get("reqd"):
            schema["required"].append(fieldname)

    if not schema["required"]:
        schema.pop("required")

    return schema

def generate_paths_for_doctype(doctype):
    """生成对应 RESTful 路径（CRUD）"""
    base_path = f"/api/resource/{doctype}"
    item_path = f"/api/resource/{doctype}/{{name}}"

    return {
        base_path: {
            "get": {
                "summary": f"Get list of {doctype}",
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": f"#/components/schemas/{doctype}"}
                                }
                            }
                        }
                    }
                }
            },
            "post": {
                "summary": f"Create a new {doctype}",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": f"#/components/schemas/{doctype}"}
                        }
                    }
                },
                "responses": {
                    "201": {
                        "description": "Created"
                    }
                }
            }
        },
        item_path: {
            "get": {
                "summary": f"Get {doctype} by name",
                "parameters": [{
                    "name": "name",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"}
                }],
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": f"#/components/schemas/{doctype}"}
                            }
                        }
                    }
                }
            },
            "put": {
                "summary": f"Update {doctype} by name",
                "parameters": [{
                    "name": "name",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"}
                }],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": f"#/components/schemas/{doctype}"}
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Updated"}
                }
            },
            "delete": {
                "summary": f"Delete {doctype} by name",
                "parameters": [{
                    "name": "name",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"}
                }],
                "responses": {
                    "204": {"description": "Deleted"}
                }
            }
        }
    }

def generate_openapi(client, target_doctypes=None):
    """主函数：生成完整 OpenAPI 3 文档"""
    if not target_doctypes:
        target_doctypes = get_all_doctypes(client)

    openapi = {
        "openapi": "3.0.0",
        "info": {
            "title": "Frappe REST API",
            "version": "1.0.0"
        },
        "paths": {},
        "components": {
            "schemas": {}
        }
    }

    for doctype in target_doctypes:
        try:
            schema = frappe_doctype_to_openapi_schema(client, doctype)
            openapi["components"]["schemas"][doctype] = schema

            paths = generate_paths_for_doctype(doctype)
            openapi["paths"].update(paths)

            print(f"✅ 已生成：{doctype}")
        except Exception as e:
            print(f"⚠️ 跳过 {doctype}：{e}")

    return openapi

if __name__ == "__main__":
    client = FrappeClient("http://site1.localhost:8000")
    client.login("Administrator", "admin")
    target_doctypes = get_all_doctypes(client)  # 可选：获取所有 Doctype 列表
    openapi = generate_openapi(client, target_doctypes)  # 可指定部分 Doctype

    with open("frappe_openapi.json", "w", encoding="utf-8") as f:
        json.dump(openapi, f, indent=2, ensure_ascii=False)

    print("✅ OpenAPI 文档已导出：frappe_openapi.json")
