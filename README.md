# IT 资产管理系统

企业级 IT 资产管理系统，基于 FastAPI + Vue 3 构建，支持 Docker 一键部署。

## 功能特性

- 🔐 **用户认证** - JWT 令牌认证，支持登录/注册/登出
- 📦 **资产管理** - 资产 CRUD、筛选、分页，支持状态管理
- 🏷️ **分类管理** - 树形结构分类，支持多级分类
- 🏪 **供应商管理** - 供应商信息维护
- 📝 **采购管理** - 采购申请、审批流程（草稿→待审批→已通过/已拒绝→已采购）
- 📊 **仪表盘** - 资产统计、状态分布、待审批申请

## 技术栈

### 后端
- Python 3.11 + FastAPI
- SQLAlchemy 2.0 (异步) + PostgreSQL
- Redis (缓存)
- JWT 认证 (python-jose)
- Gunicorn + Uvicorn Workers

### 前端
- Vue 3 + TypeScript
- Vite 5
- Element Plus
- Pinia (状态管理)
- Axios (HTTP 客户端)

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

访问 http://localhost:3000

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

# 初始化数据库
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

- 用户名: `admin`
- 密码: `admin123`

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
│   │   ├── api/               # API 调用
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
| REDIS_HOST | Redis 主机 | redis |
| SECRET_KEY | JWT 密钥 | your-secret-key |

## 端口说明

| 服务 | 端口 | 描述 |
|------|------|------|
| frontend | 3000 | 前端页面 (映射到容器 80) |
| backend | 8000 | 后端 API |
| postgres | 5432 | PostgreSQL 数据库 |
| redis | 6379 | Redis 缓存 |

## License

MIT
