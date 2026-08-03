import sqlite3
import os

# 连接到 SQLite 数据库
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'travel_planner.db')
print(f"数据库路径: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 查询所有目的地的图片 URL
cursor.execute("SELECT name, cover_image FROM destinations")
results = cursor.fetchall()

print("\n数据库中的目的地图片 URL：")
for name, cover_image in results:
    print(f"{name}: {cover_image[:80]}...")

conn.close()