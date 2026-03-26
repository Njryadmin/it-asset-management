# IT 资产管理系统

企业级 IT 资产管理系统，基于 FastAPI + Vue 3 构建，支持 Docker 一键部署。

## 功能特性

- 🔐 **用户认证** - JWT 令牌认证，支持登录/注册/登出
- 👥 **用户管理** - 用户列表、创建、编辑、启用/禁用（仅管理员）
- 📦 **资产管理** - 资产 CRUD、筛选、分页，支持状态管理
- 📥 **导入导出** - CSV 批量导入/导出，支持字段选择器
- 🏷️ **分类管理** - 树形结构分类，支持多级分类
- 🏪 **供应商管理** - 供应商信息维护
- 🏢 **部门管理** - 组织架构管理
- 📝 **采购管理** - 采购申请、审批流程（草稿→待审批→已通过/已拒绝→已采购）
- ⚙️ **系统设置** - 个人资料修改、密码修改
- 📊 **仪表盘** - 资产统计、状态分布、近期资产、待审批申请

## 技术栈

### 后端
- Python 3.11 + FastAPI
- SQLAlchemy 2.0 (异步) + PostgreSQL
- Redis (缓存)
- JWT 认证 (python-jose + passlib)
- Gunicorn + Uvicorn Workers
- Bcrypt 密码加密

### 前端
- Vue 3 + TypeScript
- Vite 5
- Element Plus
- Pinia (状态管理)
- Axios (HTTP 客户端)
- 字段自动转换 (snake_case ↔ camelCase)

## 快速开始

### 方式一：Docker 部署（推荐）

```bash
# 克隆项目
git clone https://github.com/Njryadmin/it-asset-management.git
cd it-asset-management

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

访问 http://localhost:3030

### 方式二：本地开发

#### 后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入数据库和 Redis 配置

# 初始化数据库和服务数据
python -m app.services.init_db

# 启动服务
uvicorn app.main:app --reload --port 8000
```

#### 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 超级管理员 |

## API 文档

启动后端服务后访问: http://localhost:8000/api/v1/docs

## 项目结构

```
it-asset-management/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/  # API 路由
│   │   ├── core/              # 核心配置 (config, database, redis, security)
│   │   ├── models/            # SQLAlchemy 模型
│   │   ├── schemas/           # Pydantic 模型
│   │   ├── services/          # 业务逻辑
│   │   └── main.py            # FastAPI 应用入口
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/               # API 调用封装
│   │   ├── components/        # 公共组件
│   │   ├── stores/            # Pinia 状态管理
│   │   ├── router/            # 路由配置
│   │   ├── views/             # 页面组件
│   │   ├── types/             # TypeScript 类型定义
│   │   └── styles/            # 全局样式
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 环境变量

### 后端 (.env)

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| POSTGRES_SERVER | PostgreSQL 主机 | postgres |
| POSTGRES_USER | 数据库用户 | postgres |
| POSTGRES_PASSWORD | 数据库密码 | postgres |
| POSTGRES_DB | 数据库名 | itasset |
| POSTGRES_PORT | 数据库端口 | 5432 |
| REDIS_HOST | Redis 主机 | redis |
| REDIS_PORT | Redis 端口 | 6379 |
| SECRET_KEY | JWT 密钥 | your-secret-key-change-in-production |
| ALGORITHM | JWT 算法 | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token 过期时间(分钟) | 1440 (24小时) |

## 端口说明

| 服务 | 端口 | 描述 |
|------|------|------|
| frontend | 3030 | 前端页面 |
| backend | 8000 | 后端 API |
| postgres | 5432 | PostgreSQL 数据库 |
| redis | 6379 | Redis 缓存 |

## 常见问题

### Q: 登录提示"登录已过期"
请确保使用最新版本的镜像。如有 Nginx 配置更新，需重新构建：
```bash
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### Q: 数据库初始化
首次部署时默认管理员账号会自动创建。如需重新初始化数据，运行：
```bash
docker exec it-asset-management-backend-1 python -m app.services.init_db
```

## License

MIT
