# IT 资产管理系统

> 🎉 **版本 1.0 测试版 (v1.0.0-beta)**

企业级 IT 资产管理系统，基于 FastAPI + Vue 3 构建，支持 Docker 一键部署。

**微信主题风格** - 现代简洁的 UI 设计，支持浅色/深色主题切换

![IT资产管理](https://img.shields.io/badge/IT%E8%B5%84%E4%BA%A7%E7%AE%A1%E7%90%86-v1.0.0--blue)
![Vue3](https://img.shields.io/badge/Vue-3.4-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![Element Plus](https://img.shields.io/badge/Element%20Plus-2.5-blue)

## 功能特性

### 核心功能
| 模块 | 功能 |
|------|------|
| 📊 **仪表盘** | 统计数据、资产状态分布圆环图、今日入库/出库、待审批采购、快捷入口 |
| 💻 **资产管理** | CRUD、导入导出(CSV)、状态管理、使用人、地区分类 |
| 🏷️ **分类管理** | 树形结构、多级分类、导入导出 |
| 🏢 **部门管理** | 组织架构管理、独立菜单项 |
| 🏪 **供应商管理** | 供应商 CRUD、导入导出、启用/禁用 |
| 📝 **采购管理** | 申请、审批流程(草稿→待审批→已通过/已拒绝→已采购) |
| 👥 **用户管理** | 用户 CRUD、角色管理 (仅管理员) |
| ⚙️ **系统设置** | 站点信息、基础配置、主题切换 |

### UI/UX 特性
- 🎨 **微信主题风格** - 主色调 #1AAD19
- 🌙 **深色/浅色主题** - 一键切换
- 📱 **移动端适配** - 响应式布局、操作列下拉菜单
- 🌓 **磨砂玻璃效果** - 侧边栏毛玻璃质感

## 技术栈

### 后端
| 技术 | 说明 |
|------|------|
| Python 3.11 + FastAPI | 高性能异步 API 框架 |
| SQLAlchemy 2.0 (异步) | 异步 ORM |
| PostgreSQL 15 | 关系型数据库 |
| Redis 7 | 缓存、会话存储 |
| JWT (python-jose + passlib) | 认证授权 |
| Gunicorn + Uvicorn | WSGI/ASGI 服务器 |
| Bcrypt | 密码加密 |

### 前端
| 技术 | 说明 |
|------|------|
| Vue 3.4 + TypeScript | 渐进式 JavaScript 框架 |
| Vite 5 | 下一代前端构建工具 |
| Element Plus | UI 组件库 |
| Pinia | 状态管理 |
| Axios | HTTP 客户端 (自动转换 snake_case ↔ camelCase) |
| Day.js | 日期处理 |

## 快速部署

### 方式一：Docker 一键部署（推荐）

```bash
# 克隆项目
git clone https://github.com/Njryadmin/it-asset-management.git
cd it-asset-management

# 启动所有服务 (首次启动自动初始化数据库)
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
```

访问 http://localhost:3030

### 方式二：构建 Docker 镜像发布

```bash
# 构建所有镜像
docker-compose build

# 打包为单个 tar 文件
docker save it-asset-management-frontend:latest -o it-asset-frontend.tar
docker save it-asset-management-backend:latest -o it-asset-backend.tar
docker save postgres:15-alpine -o postgres.tar
docker save redis:7-alpine -o redis.tar

# 传输到目标机器后加载
docker load -i it-asset-frontend.tar
docker load -i it-asset-backend.tar
docker load -i postgres.tar
docker load -i redis.tar

# 启动
docker-compose up -d
```

### 方式三：本地开发

```bash
# 后端
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 前端 (新终端)
cd frontend
npm install
npm run dev
```

## 测试账户

| 用户名 | 密码 | 角色 | 说明 |
|--------|------|------|------|
| admin | admin123 | 超级管理员 | 全部功能 |
| zhangsan | test123456 | 普通用户 | 受限功能 |

## API 文档

启动后端后访问: http://localhost:8000/api/v1/docs

## 项目结构

```
it-asset-management/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/   # API 路由 (资产/用户/采购/设置等)
│   │   ├── core/               # 核心配置 (config, database, redis, security)
│   │   ├── models/             # SQLAlchemy 模型
│   │   ├── schemas/            # Pydantic 验证模型
│   │   ├── services/           # 业务逻辑
│   │   └── main.py            # FastAPI 应用入口
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/               # Axios 封装 + 拦截器
│   │   ├── components/        # 公共组件 (MainLayout 等)
│   │   ├── composables/       # Vue Composables (useColumnSettings)
│   │   ├── stores/            # Pinia 状态管理
│   │   ├── router/            # Vue Router 配置
│   │   ├── views/            # 页面组件
│   │   ├── types/            # TypeScript 类型定义
│   │   └── styles/           # 全局样式 (微信主题 CSS 变量)
│   ├── public/                # 静态资源 (logo, favicon)
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml         # 编排配置
└── README.md
```

## 环境变量

### 后端配置

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| POSTGRES_SERVER | PostgreSQL 主机 | postgres |
| POSTGRES_USER | 数据库用户 | postgres |
| POSTGRES_PASSWORD | 数据库密码 | postgres |
| POSTGRES_DB | 数据库名 | itasset |
| POSTGRES_PORT | 数据库端口 | 5432 |
| REDIS_HOST | Redis 主机 | redis |
| REDIS_PORT | Redis 端口 | 6379 |
| SECRET_KEY | JWT 密钥 | (需生产环境设置) |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token 过期时间 | 1440 (24小时) |

## 端口说明

| 服务 | 端口 | 描述 |
|------|------|------|
| frontend | 3030 | 前端页面 |
| backend | 8000 | 后端 API |
| postgres | 5432 | PostgreSQL 数据库 |
| redis | 6379 | Redis 缓存 |

## 数据导入导出

### 支持模块
- 💻 资产管理 (字段: 编号、名称、分类、供应商、部门、使用人、状态、地区等)
- 🏷️ 分类管理 (支持按上级分类名称匹配)
- 🏪 供应商管理
- 🏢 部门管理 (支持按上级部门名称匹配)

### 导出示例
```csv
资产编号,名称,序列号,分类名称,供应商名称,部门名称,使用人,状态,购入日期,购入价格,地区
ASSET001,ThinkPad T490,SN123456,计算机设备,联想官方旗舰店,技术部,张三,in_use,2024-01-15,6999.00,上海
```

## 常见问题

### Q: 登录提示"登录已过期"
A: 检查后端服务是否正常运行 `docker-compose ps`

### Q: 如何重启服务
```bash
docker-compose restart backend
```

### Q: 如何查看数据库
```bash
docker exec -it it-asset-management-postgres-1 psql -U postgres -d itasset
```

### Q: 如何完全重建
```bash
docker-compose down -v  # 删除数据
docker-compose up -d     # 重新创建
```

## 版本历史

### v1.0.0-beta (2026-03-26)
- ✅ 微信主题风格 UI
- ✅ 仪表盘全新设计
- ✅ 登录页品牌展示
- ✅ 移动端适配优化
- ✅ 权限控制系统
- ✅ 导入导出优化 (显示实际名称)
- ✅ 资产管理添加"使用人"字段

## License

MIT License
