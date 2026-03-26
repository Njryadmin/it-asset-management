# IT 资产管理系统

> 🎉 **版本 1.0 测试版 (v1.0.0-beta)**

企业级 IT 资产管理系统，基于 FastAPI + Vue 3 构建，支持 Docker 一键部署。

**微信主题风格** - 现代简洁的 UI 设计，支持浅色/深色主题切换

## 功能特性

### 核心功能
| 模块 | 功能 |
|------|------|
| 📊 **仪表盘** | 统计数据、资产状态分布圆环图、今日入库/出库、待审批采购、快捷入口 |
| 💻 **资产管理** | CRUD、导入导出(CSV)、状态管理、使用人、地区分类 |
| 🏷️ **分类管理** | 树形结构、多级分类、导入导出 |
| 🏢 **部门管理** | 组织架构管理，独立菜单项 |
| 🏪 **供应商管理** | 供应商 CRUD、导入导出、启用/禁用 |
| 📝 **采购管理** | 申请、审批流程(草稿→待审批→已通过/已拒绝→已采购) |
| 👥 **用户管理** | 用户 CRUD、角色管理 (仅管理员) |
| ⚙️ **系统设置** | 站点信息、基础配置、主题切换 |

### UI/UX 特性
- 🎨 **微信主题风格** - 主色调 #1AAD19
- 🌙 **深色/浅色主题** - 一键切换
- 📱 **移动端适配** - 响应式布局，操作列下拉菜单
- 🌓 **磨砂玻璃效果** - 侧边栏毛玻璃质感

## 快速部署

### 方式一：GitHub Container Registry（推荐）

每次代码 push 后自动构建，可直接拉取：

```bash
# 登录 GHCR
docker login ghcr.io -u Njryadmin -p <YOUR_TOKEN>

# 拉取镜像
docker pull ghcr.io/Njryadmin/it-asset-management/backend:latest
docker pull ghcr.io/Njryadmin/it-asset-management/frontend:latest
docker pull postgres:15-alpine
docker pull redis:7-alpine
```

**使用 docker-compose.yml：**
```yaml
services:
  backend:
    image: ghcr.io/Njryadmin/it-asset-management/backend:latest
    # ...
  frontend:
    image: ghcr.io/Njryadmin/it-asset-management/frontend:latest
    # ...
```

### 方式二：本地打包文件部署

下载打包好的镜像文件：
- 下载地址: Releases 页面 (待发布)

```bash
# 加载镜像
gunzip < it-asset-management-v1.0.0-beta-allinone.tar.gz | docker load

# 启动服务
docker-compose up -d
```

### 方式三：本地构建

```bash
# 克隆项目
git clone https://github.com/Njryadmin/it-asset-management.git
cd it-asset-management

# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d
```

## 测试账户

| 用户名 | 密码 | 角色 | 说明 |
|--------|------|------|------|
| admin | admin123 | 超级管理员 | 全部功能 |
| zhangsan | test123456 | 普通用户 | 受限功能 |

## 访问地址

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:3030 |
| 后端 API | http://localhost:8000 |
| API 文档 | http://localhost:8000/api/v1/docs |

## 技术栈

### 后端
- Python 3.11 + FastAPI
- SQLAlchemy 2.0 (异步) + PostgreSQL
- Redis 7
- JWT 认证

### 前端
- Vue 3.4 + TypeScript
- Vite 5 + Element Plus
- Pinia + Axios

## 项目结构

```
it-asset-management/
├── backend/                  # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/endpoints/   # API 路由
│   │   ├── core/               # 核心配置
│   │   ├── models/             # 数据库模型
│   │   └── schemas/            # Pydantic 模型
│   └── Dockerfile
├── frontend/                 # Vue3 前端
│   ├── src/
│   │   ├── api/               # Axios 封装
│   │   ├── components/         # 公共组件
│   │   ├── views/             # 页面组件
│   │   └── styles/            # 全局样式
│   ├── public/                # 静态资源
│   └── Dockerfile
├── docker-compose.yml        # Docker 编排
├── .github/workflows/         # GitHub Actions
└── README.md
```

## 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| POSTGRES_SERVER | PostgreSQL 主机 | postgres |
| POSTGRES_USER | 数据库用户 | postgres |
| POSTGRES_PASSWORD | 数据库密码 | postgres |
| POSTGRES_DB | 数据库名 | itasset |
| REDIS_HOST | Redis 主机 | redis |
| REDIS_PORT | Redis 端口 | 6379 |
| SECRET_KEY | JWT 密钥 | (需设置) |

## GitHub Actions

每次 push 到 main 分支自动构建并推送镜像到 GHCR：

- **Backend 镜像**: `ghcr.io/Njryadmin/it-asset-management/backend`
- **Frontend 镜像**: `ghcr.io/Njryadmin/it-asset-management/frontend`

查看构建状态: https://github.com/Njryadmin/it-asset-management/actions

## 常见问题

### Q: 登录提示"登录已过期"
```bash
# 检查服务状态
docker-compose ps

# 重启后端
docker-compose restart backend
```

### Q: 如何完全重建
```bash
docker-compose down -v
docker-compose up -d
```

### Q: 如何查看日志
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
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
- ✅ GitHub Actions 自动构建发布

## License

MIT License
