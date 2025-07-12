import os
import random
import string
from pprint import pprint
from frappeclient import FrappeClient
from dotenv import load_dotenv

# ✅ 自动加载同目录下的 .env 文件
load_dotenv()

# ✅ 使用环境变量避免暴露凭证（可改为硬编码测试）
FRAPPE_URL = os.getenv("FRAPPE_URL", "http://localhost:8000")
FRAPPE_USER = os.getenv("FRAPPE_USER", "administrator@example.com")
FRAPPE_PASSWORD = os.getenv("FRAPPE_PASSWORD", "admin")

# 🔐 初始化连接
client = FrappeClient(FRAPPE_URL)
client.login(FRAPPE_USER, FRAPPE_PASSWORD)

# 1️⃣ 获取 Doctype 一览
print("\n=== 所有可用 Doctype 一览 ===")
meta_list = client.get_list("DocType", fields=["name"], limit_page_length=9999)
doctypes = [doc["name"] for doc in meta_list]
pprint(doctypes)

# 🧪 选用测试用的 Doctype（例如 Note）
target_doctype = "Note"

# 2️⃣ 获取 Doctype 结构定义（字段列表）
print(f"\n=== 取得 Doctype '{target_doctype}' 的字段结构 ===")
meta = client.get_doc("DocType", target_doctype)
fields = [
    f["fieldname"] for f in meta.get("fields", [])
    if f["fieldtype"] not in ("Section Break", "Column Break", "Tab Break")
       and f["fieldname"]  # 过滤无效字段
]
pprint(fields)

# 3️⃣ 构造新增文档的数据（只填部分字段）
print(f"\n=== 插入 Doctype '{target_doctype}' 的测试文档 ===")
new_title = "AutoNote_" + ''.join(random.choices(string.ascii_letters, k=6))
new_doc = {
    "doctype": target_doctype,
    "title": new_title,
    "public": True
}
inserted = client.insert(new_doc)
pprint(inserted)
doc_name = inserted["name"]

# 4️⃣ 获取该文档内容
print(f"\n=== 读取文档 '{doc_name}' ===")
fetched_doc = client.get_doc(target_doctype, doc_name)
pprint(fetched_doc)

# 5️⃣ 更新文档内容
print(f"\n=== 更新文档 '{doc_name}' 的 title 字段 ===")
fetched_doc["title"] = fetched_doc["title"] + "_Updated"
updated_doc = client.update(fetched_doc)
pprint(updated_doc)

# 6️⃣ 查询文档列表（只获取 title 字段）
print(f"\n=== 获取 Doctype '{target_doctype}' 的文档列表（部分字段） ===")
doc_list = client.get_list(target_doctype, fields=["name", "title", "public"], limit_page_length=5)
pprint(doc_list)

# 7️⃣ 删除该测试文档
print(f"\n=== 删除文档 '{doc_name}' ===")
client.delete(target_doctype, doc_name)
print(f"✅ 文档 '{doc_name}' 已删除")

