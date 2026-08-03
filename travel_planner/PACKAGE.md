# 项目打包说明

## 打包前准备

### 1. 清理临时文件

以下文件/目录在打包前应删除：
- `venv/` - 虚拟环境（接收方需自行创建）
- `__pycache__/` - Python缓存
- `*.pyc` - 编译文件
- `.env` - 环境变量文件（包含您的API Key，不应分享）
- `*.log` - 日志文件
- 测试脚本（如 `test_*.py`、`check_*.py`）

### 2. 保留必要文件

必须保留的文件：
- `app/` - 应用代码目录
- `instance/travel_planner.db` - 数据库（含测试数据）
- `config.py` - 配置文件
- `requirements.txt` - 依赖列表
- `wsgi.py` - 启动入口
- `init_db.py` - 数据库初始化脚本
- `README.md` - 项目说明
- `.env.example` - 环境变量示例

## 打包方法

### Windows 系统

```powershell
# 进入项目目录
cd c:\Users\Administrator\Downloads\智能系统作业\期末作业

# 删除虚拟环境（减小体积）
Remove-Item -Recurse -Force travel_planner\venv

# 删除缓存文件
Get-ChildItem -Path travel_planner -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Path travel_planner -Recurse -Filter "*.pyc" | Remove-Item -Force

# 删除.env文件（保护您的API Key）
Remove-Item -Force travel_planner\.env

# 打包为ZIP
Compress-Archive -Path travel_planner -DestinationPath travel_planner.zip
```

### Linux/macOS 系统

```bash
# 进入项目目录
cd /path/to/期末作业

# 删除虚拟环境
rm -rf travel_planner/venv

# 删除缓存
find travel_planner -name "__pycache__" -type d -exec rm -rf {} +
find travel_planner -name "*.pyc" -delete

# 删除.env文件
rm -f travel_planner/.env

# 打包为ZIP
zip -r travel_planner.zip travel_planner
```

## 打包后检查

确保ZIP文件包含以下内容：

```
travel_planner.zip
├── travel_planner/
│   ├── app/                  ✅ 必需
│   ├── instance/             ✅ 必需（含数据库）
│   ├── config.py             ✅ 必需
│   ├── requirements.txt      ✅ 必需
│   ├── wsgi.py               ✅ 必需
│   ├── init_db.py            ✅ 必需
│   ├── README.md             ✅ 必需
│   ├── .env.example          ✅ 必需
│   └── tests/                ✅ 推荐（可选）
```

## 接收方使用说明

接收方收到项目后：

1. 解压 `travel_planner.zip`
2. 创建虚拟环境：`python -m venv venv`
3. 激活虚拟环境：`venv\Scripts\activate` (Windows)
4. 安装依赖：`pip install -r requirements.txt`
5. 创建 `.env` 文件（参考 `.env.example`）
6. 启动服务器：`python wsgi.py`
7. 访问：http://127.0.0.1:5000

详见 `README.md` 文件。