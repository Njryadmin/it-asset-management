# IT 资产管理系统

> 🎉 **版本 2.0 (v2.0.0)** — 2026-03-28

企业级 IT 资产管理系统，基于 FastAPI + Vue 3 构建，支持 Docker 一键部署。

**微信主题风格** — 现代简洁的 UI 设计，支持浅色/深色主题切换

**在线演示：** http://192.168.10.1:3030
默认账号：`admin` / `admin123`

---

## 功能特性

### 核心功能
| 模块 | 功能 |
|------|------|
| 📊 **仪表盘** | 统计数据、资产状态分布、科技感圆环图、今日入库/出库统计、待审批采购、快捷入口、滚动公告 |
| 💻 **资产管理** | CRUD、导入导出(CSV)、状态管理、**资产详情页**（使用人姓名/品牌型号/维保记录） |
| 🏷️ **分类管理** | 树形结构、多级分类、导入导出 |
| 🏢 **部门管理** | 组织架构管理，支持按字段导出，上级部门名称关联 |
| 🏪 **供应商管理** | 供应商 CRUD、导入导出、启用/禁用 |
| 📝 **采购管理** | 申请、提交审批、**审批通过后自动创建资产**（一键闭环） |
| ✅ **审批管理** | 我的申请 / **待我审批** / 审批历史，审批意见填写，**进度可视化** |
| 🔧 **审批流程配置** | 可视化配置审批步骤、多级审批（管理员） |
| 👥 **用户管理** | 用户 CRUD、角色管理（仅管理员） |
| 📋 **审计日志** | 操作记录全追踪（CREATE/UPDATE/DELETE/APPROVE/REJECT），变更前后状态对比，支持多维度筛选 |
| 📈 **报表中心** | 资产汇总/分类分布/部门分布/重要度分布/近6月趋势（ECharts 可视化） |
| 🔧 **维保记录** | 资产维保历史记录（维修/保养/巡检），费用/供应商追踪 |
| ⚙️ **系统设置** | 站点信息、基础配置、主题切换、Logo/图标上传、公告设置、版本号管理 |

### v2.0 新增功能
| 模块 | 功能 |
|------|------|
| 🔐 **审计日志** | 全操作记录追踪，before/after 状态对比，多维度筛选（操作类型/资源类型/时间范围） |
| ✅ **多级审批工作流** | 审批流程引擎，提交→审批→通过/拒绝，审批链完整记录，可视化进度条 |
| 🔧 **审批流程配置** | 管理员可视化配置审批步骤，无需数据库操作 |
| 📈 **资产报表中心** | 资产总览/分类分布/部门分布/重要度分布/趋势分析（ECharts 图表） |
| 💻 **资产详情页** | 单个资产全生命周期，使用人姓名、品牌型号、维保记录、操作日志 |
| 🔒 **RBAC 细粒度控制** | 审批管理/报表中心/审计日志/流程配置仅管理员可见 |
| 🔧 **采购→自动入库** | 采购审批通过后标记"已采购"时，自动在资产表创建记录，一键闭环 |
| 🔧 **维保记录管理** | 维修/保养/巡检历史记录，费用和供应商追踪 |
| 📌 **版本号动态化** | 版本号从系统设置读取，不再硬编码 |

### UI/UX 特性
- 🎨 **微信主题风格** — 主色调 #1AAD19，扁平简洁
- 🌙 **深色/浅色主题** — 一键切换，完整适配所有页面
- 💻 **仪表盘重新设计** — 科技感仪表盘风格，玻璃拟态卡片，SVG 弧形仪表盘
- 🔐 **登录页重新设计** — 深色品牌区 + 白色表单卡，精细网格背景，脉冲光晕
- 📱 **移动端适配** — 响应式布局，移动端 hamburger 菜单，统计卡片自适应
- 🏷️ **站点 Logo** — 上传后侧边栏顶部展示，支持 Favicon
- 📢 **滚动公告** — 仪表盘顶部橙色公告条，来回滚动播放
- ✏️ **文字链接型按钮** — 编辑/删除采用微信风格文字链接，hover 显示图标

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + TypeScript + Vite + Element Plus + Pinia + Axios + ECharts |
| 后端 | FastAPI 0.110 + SQLAlchemy 2.0（异步）+ Pydantic v2 |
| 数据库 | PostgreSQL 15 |
| 缓存 | Redis 7 |
| 部署 | Docker + Docker Compose |
| CI/CD | GitHub Actions (GHCR) |

---

## 数据库

### 已实现的表（12张）
| 表名 | 说明 |
|------|------|
| `users` | 用户表 |
| `assets` | 资产主表（v2 新增 brand/model/location/importance_level/deleted_at） |
| `categories` | 资产分类表（树形） |
| `departments` | 部门表（树形） |
| `suppliers` | 供应商表 |
| `purchase_requests` | 采购申请表 |
| `system_settings` | 系统设置表（v2 新增 version 字段） |
| `audit_logs` | 审计日志表（v2 新增，before/after JSONB） |
| `approval_flows` | 审批流程模板表（v2 新增） |
| `approval_instances` | 审批实例表（v2 新增，含审批链 JSONB） |
| `asset_maintenance_logs` | 资产维保记录表（v2 新增） |
| `asset_attachments` | 资产附件表（v2 新增） |

---

## API 接口

| 模块 | 路径 | 方法 | 说明 |
|------|------|------|------|
| 认证 | `/api/v1/auth/login` | POST | 登录 |
| 认证 | `/api/v1/auth/me` | GET | 当前用户 |
| 资产 | `/api/v1/assets` | GET/POST | 资产列表/新增 |
| 资产 | `/api/v1/assets/{id}` | GET/PUT/DELETE | 资产详情/更新/删除 |
| 资产 | `/api/v1/assets/stats` | GET | 资产统计 |
| 采购 | `/api/v1/purchase-requests` | GET/POST | 采购申请 |
| 采购 | `/api/v1/purchase-requests/{id}/submit` | POST | 提交审批 |
| 采购 | `/api/v1/purchase-requests/{id}/purchase` | POST | 标记已采购（自动创建资产） |
| 审批 | `/api/v1/approval-instances` | GET | 审批实例列表 |
| 审批 | `/api/v1/approval-instances/my-pending` | GET | 我的待审批（分页） |
| 审批 | `/api/v1/approval-instances/my-applications` | GET | 我的申请列表 |
| 审批 | `/api/v1/approval-instances/{id}/approve` | POST | 审批通过 |
| 审批 | `/api/v1/approval-instances/{id}/reject` | POST | 审批拒绝 |
| 审批 | `/api/v1/approval-flows` | GET/POST | 审批流程模板 CRUD |
| 审计 | `/api/v1/audit-logs` | GET | 审计日志列表（支持多维筛选） |
| 报表 | `/api/v1/reports/assets/summary` | GET | 资产汇总 |
| 报表 | `/api/v1/reports/assets/distribution` | GET | 资产分布 |
| 报表 | `/api/v1/reports/assets/trend` | GET | 资产趋势（近6月） |
| 维保 | `/api/v1/asset-maintenance-logs` | GET/POST/PUT/DELETE | 维保记录 CRUD |
| 用户 | `/api/v1/users/me/permissions` | GET | 当前用户权限列表 |
| 设置 | `/api/v1/settings` | GET/PUT | 系统设置（含 version 字段） |

完整 API 文档：http://localhost:8000/api/v1/docs

---

## 快速部署

### 方式一：GitHub Container Registry（推荐）

```bash
# 登录 GHCR
docker login ghcr.io -u Njryadmin -p <YOUR_TOKEN>

# 拉取并运行
docker run -d \
  --name it-asset-backend \
  -p 8000:8000 \
  ghcr.io/njryadmin/it-asset-management/backend:latest

docker run -d \
  --name it-asset-frontend \
  -p 3030:80 \
  ghcr.io/njryadmin/it-asset-management/frontend:latest
```

### 方式二：本地构建

```bash
git clone https://github.com/Njryadmin/it-asset-management.git
cd it-asset-management
docker-compose up -d
```

访问 http://localhost:3030，默认账号：`admin` / `admin123`

---

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

---

## GitHub Actions

每次 push 到 main 分支自动构建并推送镜像到 GHCR：

- **Backend 镜像**: `ghcr.io/njryadmin/it-asset-management/backend`
- **Frontend 镜像**: `ghcr.io/njryadmin/it-asset-management/frontend`

查看构建状态: https://github.com/Njryadmin/it-asset-management/actions

---

## 常见问题

### Q: 登录提示"登录已过期"
```bash
docker-compose ps
docker-compose restart backend
```

### Q: 如何完全重建
```bash
docker-compose down -v
docker-compose up -d
```

### Q: Logo 上传后不显示
确保已挂载 `static_data` 数据卷，镜像重建后静态文件会持久化。

### Q: 如何查看日志
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Q: 如何升级到最新版本
```bash
git pull origin main
docker-compose build backend frontend
docker-compose up -d
```

---

## 版本历史

### v2.0.0 (2026-03-27)
- ✅ **审计日志** — 全操作记录追踪，before/after 状态对比，多维度筛选
- ✅ **多级审批工作流** — 审批流程引擎，审批链完整记录，进度可视化
- ✅ **审批流程配置页** — 管理员可视化配置审批步骤
- ✅ **资产报表中心** — ECharts 可视化（分类分布/部门分布/趋势分析）
- ✅ **资产详情页** — 使用人姓名、品牌型号、维保记录、操作日志
- ✅ **采购→自动入库** — 审批通过后自动创建资产记录，一键闭环
- ✅ **维保记录管理** — 维修/保养/巡检历史记录
- ✅ **RBAC 细粒度** — 审批管理/报表中心/审计日志/流程配置仅管理员
- ✅ **仪表盘重新设计** — 科技感仪表盘风格，玻璃拟态卡片
- ✅ **登录页重新设计** — 深色品牌区 + 白色表单卡
- ✅ **版本号动态化** — 从 system_settings 读取
- ✅ assets 表新增字段（brand/model/location/importance_level/deleted_at）
- ✅ GitHub Actions 自动构建

### v1.0.0 (2026-03-27)
- ✅ 仪表盘全新设计（SVG 圆环图、仪表盘进度条）
- ✅ 滚动公告功能（仪表盘顶部橙色公告条）
- ✅ 站点 Logo 上传 + 侧边栏顶部展示
- ✅ 文字链接型操作按钮（微信风格）
- ✅ 移动端响应式优化（hamburger 菜单、统计卡片自适应）
- ✅ 部门导出修复（按字段导出、路由顺序修复）
- ✅ 分类管理 UI 重构（与其他页面风格统一）
- ✅ GitHub Actions 自动构建

### v1.0.0-beta (2026-03-26)
- ✅ 微信主题风格 UI
- ✅ 登录页品牌展示
- ✅ 权限控制系统
- ✅ 导入导出功能
- ✅ GitHub Actions 自动构建发布

---

## License

MIT License
