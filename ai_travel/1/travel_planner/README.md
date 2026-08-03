# AI 旅游行程规划助手

> 基于 Flask + AI 的智能旅游行程规划系统，让旅行更简单

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-2.3%2B-green)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)

---

## 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [详细使用指南](#详细使用指南)
- [项目结构](#项目结构)
- [API 接口](#api-接口)
- [常见问题](#常见问题)

---

## 项目简介

AI 旅游行程规划助手是一款面向自助游用户的智能行程规划系统。用户可以通过自然语言与 AI 对话，快速生成个性化的旅行行程，支持多轮对话调整行程细节，并可以将行程导出为 PDF 或分享到社区与其他旅行者交流。

### 适用场景

- **个人旅行规划**：快速制定个性化旅行计划
- **旅行灵感获取**：浏览热门目的地和他人分享的行程
- **行程分享交流**：将优质行程分享给其他旅行者
- **团队协作规划**：复制他人行程并进行二次创作

---

## 功能特性

### 一、用户系统

| 功能 | 说明 |
|------|------|
| 用户注册 | 支持用户名/邮箱注册，密码加密存储 |
| 用户登录 | 支持用户名或邮箱登录 |
| 个人资料 | 修改头像、昵称、个人简介 |
| 密码修改 | 安全修改登录密码 |
| 收藏管理 | 查看和管理收藏的行程 |

### 二、目的地浏览

| 功能 | 说明 |
|------|------|
| 目的地列表 | 按分类（自然/历史/美食/都市/海滨）筛选 |
| 关键词搜索 | 快速查找目标目的地 |
| 目的地详情 | 图片轮播、详细介绍、最佳旅行季节 |
| 热门行程推荐 | 查看该目的地的热门公开行程 |
| 地图展示 | 高德地图显示目的地位置 |

### 三、AI 智能行程生成

| 功能 | 说明 |
|------|------|
| 向导式创建 | 3步完成行程创建：选择目的地 → 设置参数 → AI生成 |
| 多参数设置 | 天数、预算档次（经济/舒适/豪华）、兴趣标签 |
| 多兴趣标签 | 美食、历史、自然、购物、摄影、休闲等 |
| 补充说明 | 自定义需求让AI更懂你 |
| 流式输出 | SSE实时显示AI生成过程 |
| 多轮对话调整 | 与AI对话修改行程细节 |

### 四、行程编辑与管理

| 功能 | 说明 |
|------|------|
| 可视化编辑 | 按天折叠面板，直观展示行程 |
| 拖拽排序 | Sortable.js支持活动拖拽排序 |
| 动态调整 | 添加/删除天数和活动 |
| 费用统计 | Chart.js饼图实时展示费用分布 |
| 保存行程 | 一键保存编辑后的行程 |
| 复制行程 | 基于他人公开行程二次创作 |
| 删除行程 | 删除不需要的行程 |

### 五、社区分享

| 功能 | 说明 |
|------|------|
| 公开分享 | 将行程设为公开，分享到社区 |
| 瀑布流展示 | 美观的社区行程展示 |
| 排序筛选 | 按热度/最新排序，标签筛选 |
| 点赞收藏 | AJAX无刷新点赞/收藏 |
| 评论交流 | 支持一级回复的评论系统 |

### 六、其他功能

| 功能 | 说明 |
|------|------|
| 地图集成 | 高德地图JS API显示景点位置和路线 |
| PDF导出 | 一键导出精美PDF文档 |
| 响应式设计 | Bootstrap 5适配各种屏幕尺寸 |

---

## 技术栈

### 后端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.8+ | 编程语言 |
| **Flask** | 2.3+ | Web框架，蓝图架构 |
| **SQLAlchemy** | 3.0+ | ORM数据库操作 |
| **Flask-Login** | 0.6+ | 用户认证管理 |
| **Flask-WTF** | 1.1+ | 表单处理与CSRF保护 |
| **SQLite** | - | 开发环境数据库 |
| **MySQL** | 8.0+ | 生产环境数据库（可选） |
| **Redis** | 5.0+ | 缓存服务（可选） |
| **bcrypt** | 4.0+ | 密码加密 |
| **OpenAI API** | 1.0+ | AI行程生成 |
| **WeasyPrint** | 61.0+ | PDF生成 |
| **python-dotenv** | 1.0+ | 环境变量管理 |

### 前端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| **Bootstrap** | 5.3 | UI框架，响应式布局 |
| **Font Awesome** | 6.4 | 图标库 |
| **Chart.js** | 4.0 | 费用饼图可视化 |
| **Sortable.js** | 1.15 | 拖拽排序功能 |
| **高德地图 JS API** | 2.0 | 地图展示 |
| **Jinja2** | - | 模板引擎 |

### 开发工具

| 工具 | 用途 |
|------|------|
| **pytest** | 单元测试 |
| **Faker** | 测试数据生成 |
| **Flask-Migrate** | 数据库迁移 |

---

## 快速开始

### 环境要求

| 软件 | 版本 | 必需 |
|------|------|------|
| Python | 3.8+ | ✅ 必需 |
| SQLite | - | ✅ 开发环境自带 |
| MySQL | 8.0+ | ❌ 生产环境可选 |
| Redis | 5.0+ | ❌ 可选（缓存加速） |

### 安装步骤

#### 1. 解压项目

```bash
# 解压到任意目录
unzip travel_planner.zip
cd travel_planner
```

#### 2. 创建虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

#### 4. 配置环境变量

创建 `.env` 文件（参考 `.env.example`）：

```env
# Flask配置
SECRET_KEY=your-secret-key-here

# AI服务配置（可选，不配置则AI功能不可用）
AI_API_KEY=your-openai-api-key
AI_API_SECRET=your-api-secret
AI_API_FID=your-api-fid
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-3.5-turbo

# 高德地图配置（可选，不配置则地图不可用）
AMAP_KEY=your-amap-key

# 天气API配置（可选）
WEATHER_API_KEY=your-weather-api-key
```

#### 5. 初始化数据库

```bash
# 数据库已预置测试数据，无需额外初始化
# 如需重新初始化：
python init_db.py
```

#### 6. 启动服务器

```bash
# 方式一：直接运行
python wsgi.py

# 方式二：使用Flask命令
flask run

# 方式三：使用waitress（生产环境推荐）
waitress-serve --host=127.0.0.1 --port=5000 wsgi:app
```

#### 7. 访问系统

打开浏览器访问：**http://127.0.0.1:5000**

### 测试账号

| 角色 | 用户名 | 邮箱 | 密码 |
|------|--------|------|------|
| 管理员 | admin | admin@example.com | Admin123456 |
| 测试用户 | test | test@example.com | Test123456 |

---

## 详细使用指南

### 一、注册与登录

1. **注册账号**
   - 点击右上角"注册"按钮
   - 填写用户名、邮箱、密码
   - 密码需至少8位，包含字母和数字

2. **登录系统**
   - 点击右上角"登录"按钮
   - 输入用户名或邮箱
   - 输入密码后点击登录

### 二、浏览目的地

1. **查看目的地列表**
   - 点击导航栏"目的地"
   - 可按分类筛选（自然风光、历史文化、美食之都等）
   - 可搜索关键词快速查找

2. **查看目的地详情**
   - 点击目的地卡片进入详情页
   - 查看图片轮播、详细介绍
   - 查看该目的地的热门行程推荐

### 三、AI生成行程

1. **开始创建**
   - 点击导航栏"开始规划"或首页"创建行程"
   - 进入3步向导流程

2. **Step 1：选择目的地**
   - 从下拉列表选择目的地
   - 或输入自定义目的地名称

3. **Step 2：设置参数**
   - 选择旅行天数（1-14天）
   - 选择预算档次（经济/舒适/豪华）
   - 选择兴趣标签（可多选）
   - 填写补充说明（可选）

4. **Step 3：AI生成**
   - 点击"生成行程"
   - AI实时流式输出行程内容
   - 生成完成后自动跳转编辑页

### 四、编辑行程

1. **可视化编辑**
   - 每天行程以折叠面板展示
   - 点击展开查看当天活动详情

2. **拖拽排序**
   - 拖动活动卡片调整顺序
   - 支持跨天移动活动

3. **添加/删除**
   - 点击"添加活动"新增活动
   - 点击活动卡片"×"删除活动
   - 点击"添加一天"新增行程天数

4. **费用统计**
   - 右侧实时显示费用饼图
   - 按分类统计：景点、美食、住宿、交通、购物

5. **保存行程**
   - 点击"保存行程"按钮
   - 保存成功后跳转到行程详情页

### 五、分享行程

1. **公开分享**
   - 在行程详情页点击"分享"
   - 行程将出现在社区广场
   - 其他用户可查看、点赞、收藏

2. **复制行程**
   - 在他人公开行程详情页点击"复制并修改"
   - 行程复制到你的账号下
   - 可自由编辑修改

### 六、社区互动

1. **浏览社区**
   - 点击导航栏"社区"
   - 瀑布流展示公开行程
   - 可按热度/最新排序

2. **点赞收藏**
   - 点击行程卡片"点赞"按钮
   - 点击"收藏"保存到个人收藏
   - AJAX无刷新操作

3. **评论交流**
   - 点击行程进入详情页
   - 在评论区发表看法
   - 可回复他人评论

### 七、导出PDF

1. **导出行程**
   - 在行程详情页点击"导出PDF"
   - 系统生成精美PDF文档
   - 自动下载到本地

---

## 项目结构

```
travel_planner/
├── app/                          # 应用主目录
│   ├── __init__.py               # 应用工厂
│   ├── extensions.py             # Flask扩展初始化
│   ├── models/                   # 数据模型
│   │   ├── user.py               # 用户模型
│   │   ├── destination.py        # 目的地模型
│   │   ├── itinerary.py          # 行程模型
│   │   ├── comment.py            # 评论模型
│   │   └── social.py             # 社交模型
│   ├── blueprints/               # 蓝图路由
│   │   ├── auth/                 # 用户认证
│   │   │   ├── routes.py         # 登录/注册/个人资料
│   │   │   └── forms.py          # 表单定义
│   │   ├── destinations/         # 目的地模块
│   │   │   └── routes.py         # 目的地列表/详情
│   │   ├── itineraries/          # 行程管理
│   │   │   ├── routes.py         # 创建/编辑/保存/分享
│   │   │   └── forms.py          # 行程表单
│   │   ├── community/            # 社区模块
│   │   │   └── routes.py         # 点赞/收藏/评论
│   │   └── ai/                   # AI服务
│   │       └── routes.py         # AI生成/对话
│   ├── services/                 # 业务逻辑层
│   │   ├── ai_service.py         # AI行程生成服务
│   │   ├── weather_service.py    # 天气查询服务
│   │   └── pdf_service.py        # PDF生成服务
│   ├── templates/                # Jinja2模板
│   │   ├── base.html             # 基础模板
│   │   ├── index.html            # 首页
│   │   ├── auth/                 # 认证相关页面
│   │   ├── destinations/         # 目的地页面
│   │   ├── itineraries/          # 行程页面
│   │   └── community/            # 社区页面
│   └── static/                   # 静态资源
│       ├── css/                  # 样式文件
│       │   └── custom.css        # 自定义样式
│       ├── js/                   # JavaScript
│       │   ├── itinerary_editor.js # 行程编辑器
│       │   └── map.js            # 地图功能
│       └── uploads/              # 用户上传文件
├── instance/                     # 实例目录
│   └── travel_planner.db         # SQLite数据库
├── tests/                        # 单元测试
│   ├── conftest.py               # 测试配置
│   ├── test_auth.py              # 认证测试
│   ├── test_itineraries.py       # 行程测试
│   └── test_ai.py                # AI测试
│   └── test_community.py         # 社区测试
├── config.py                     # 配置文件
│   ├── Config                    # 基础配置
│   ├── DevelopmentConfig         # 开发配置
│   └── ProductionConfig          # 生产配置
├── requirements.txt              # 依赖列表
├── wsgi.py                       # WSGI入口
├── init_db.py                    # 数据库初始化
├── .env                          # 环境变量（需创建）
├── .env.example                  # 环境变量示例
└── README.md                     # 项目说明
```

---

## API 接口

### 认证模块 `/auth`

| 方法 | 路由 | 说明 | 参数 |
|------|------|------|------|
| GET/POST | `/auth/register` | 用户注册 | username, email, password |
| GET/POST | `/auth/login` | 用户登录 | username/email, password |
| GET | `/auth/logout` | 用户登出 | - |
| GET/POST | `/auth/profile` | 个人资料 | avatar, nickname, bio |

### 目的地模块 `/destinations`

| 方法 | 路由 | 说明 | 参数 |
|------|------|------|------|
| GET | `/destinations/` | 目的地列表 | category, search |
| GET | `/destinations/<id>` | 目的地详情 | - |

### 行程模块 `/itineraries`

| 方法 | 路由 | 说明 | 参数 |
|------|------|------|------|
| GET/POST | `/itineraries/create` | 创建Step1 | destination_id |
| GET/POST | `/itineraries/create/step2` | 创建Step2 | days, budget, interests |
| POST | `/itineraries/create/generate` | AI生成 | destination, days, budget, interests, notes |
| GET | `/itineraries/<id>` | 行程详情 | - |
| GET | `/itineraries/<id>/edit` | 编辑行程 | - |
| POST | `/itineraries/save` | 保存行程 | JSON数据 |
| POST | `/itineraries/share` | 公开分享 | id |
| POST | `/itineraries/clone` | 复制行程 | id |
| POST | `/itineraries/delete` | 删除行程 | id |
| GET | `/itineraries/my` | 我的行程 | - |
| GET | `/itineraries/<id>/pdf` | 导出PDF | - |

### 社区模块 `/community`

| 方法 | 路由 | 说明 | 参数 |
|------|------|------|------|
| GET | `/community/` | 社区广场 | sort, tag |
| POST | `/community/like/<id>` | 点赞 | - |
| POST | `/community/favorite/<id>` | 收藏 | - |
| POST | `/community/comment/<id>` | 发表评论 | content |
| DELETE | `/community/comment/<id>` | 删除评论 | - |

### AI模块 `/ai`

| 方法 | 路由 | 说明 | 参数 |
|------|------|------|------|
| POST | `/ai/generate_itinerary` | AI生成行程 | destination, days, budget, interests, notes |
| GET | `/ai/chat` | AI对话(SSE) | message, itinerary_id |
| POST | `/ai/apply_changes/<id>` | 应用AI建议 | changes |

---

## 常见问题

### Q1: 启动服务器报错 "No module named 'app'"

**原因**：工作目录不正确

**解决**：
```bash
cd travel_planner  # 确保在项目根目录
python wsgi.py
```

### Q2: AI功能不可用

**原因**：未配置AI API Key

**解决**：
1. 在 `.env` 文件中配置 `AI_API_KEY`
2. 如使用国内AI服务，还需配置 `AI_API_SECRET` 和 `AI_API_FID`

### Q3: 地图不显示

**原因**：未配置高德地图Key

**解决**：
1. 访问 https://lbs.amap.com/ 注册账号
2. 创建应用获取Web端JS API Key
3. 在 `.env` 中配置 `AMAP_KEY=你的Key`

### Q4: PDF导出失败

**原因**：WeasyPrint依赖缺失

**解决**：
```bash
pip install WeasyPrint
# Windows可能需要安装GTK库
```

### Q5: 数据库连接失败

**原因**：数据库路径问题

**解决**：
- 开发环境使用SQLite，数据库在 `instance/travel_planner.db`
- 确保 `instance` 目录存在

### Q6: 登录后跳转异常

**原因**：CSRF Token问题

**解决**：
- 确保浏览器启用Cookie
- 清除浏览器缓存重新登录

---

## 开发指南

### 添加新功能

1. **添加新路由**
   - 在对应蓝图的 `routes.py` 中添加路由函数
   - 使用 `@blueprint_bp.route()` 装饰器

2. **添加新模型**
   - 在 `app/models/` 创建模型文件
   - 继承 `db.Model`
   - 在 `init_db.py` 添加测试数据

3. **添加新模板**
   - 在 `app/templates/` 对应目录创建HTML
   - 继承 `base.html` 基础模板

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行指定测试
pytest tests/test_auth.py -v

# 生成覆盖率报告
pytest tests/ --cov=app --cov-report=html
```

---

## 注意事项

1. **生产环境部署**
   - 修改 `SECRET_KEY` 为安全随机值
   - 使用 MySQL 替代 SQLite
   - 配置 Redis 缓存
   - 使用 waitress 或 Nginx 部署

2. **API Key 安全**
   - 不要将 `.env` 文件上传到公开仓库
   - 定期更换 API Key

3. **AI 费用控制**
   - OpenAI API 按token计费
   - 建议设置调用频率限制

4. **数据备份**
   - 定期备份 `instance/travel_planner.db`
   - 生产环境配置数据库自动备份

---

## 许可证

本项目基于 MIT 许可证开源。

---

## 致谢

感谢以下开源项目：

- [Flask](https://flask.palletsprojects.com/) - 轻量级Web框架
- [Bootstrap](https://getbootstrap.com/) - 响应式UI框架
- [Font Awesome](https://fontawesome.com/) - 丰富的图标库
- [Chart.js](https://www.chartjs.org/) - 美观的图表库
- [Sortable.js](https://sortablejs.github.io/Sortable/) - 拖拽排序
- [高德地图](https://lbs.amap.com/) - 地图服务
- [OpenAI](https://openai.com/) - AI服务

---

**项目作者**：智能系统课程期末作业

**最后更新**：2024年