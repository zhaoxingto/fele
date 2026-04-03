# fele

一个面向中小企业的 SaaS 进销存系统起步项目。

当前结构：

- `backend/`: FastAPI + SQLAlchemy + PostgreSQL
- `frontend/`: Vue 3 + SoybeanAdmin + AG Grid
- `docker-compose.yml`: 可选，不再作为默认启动方式

## 多租户设计

- 平台共享表放在 `public` schema
- 每个公司就是一个租户
- 每个租户单独使用自己的 schema，例如 `tenant_acme_trading`
- 超级管理员属于平台级账号
- 公司管理员和子账号通过平台用户表 + 租户成员关系管理

## 一键启动

在项目根目录执行：

```bash
start-dev.bat
```

脚本会自动：

- 检查并补齐 `backend/.env`
- 创建 `backend/.venv`
- 安装后端依赖
- 检查并安装前端依赖
- 分别打开前后端开发窗口

启动后访问：

- 前端：`http://127.0.0.1:9527/login`
- 后端：`http://127.0.0.1:8000/docs`

## 数据库连接

- Host: `127.0.0.1`
- Port: `5432`
- Database: `fele_erp`
- User: `postgres`
- Password: `aa123456`

## 默认账号

- 超级管理员邮箱：`admin@fele.local`
- 超级管理员密码：`Admin@123456`

## 已验证示例租户

- 公司：`Acme Trading`
- 租户 schema：`tenant_acme_trading`
- 公司管理员：`owner@acme.local`
- 公司管理员密码：`Owner@123456`

## 手动创建公司租户

```bash
d:\fele\backend\.venv\Scripts\python.exe d:\fele\backend\scripts\provision_tenant.py --company "Your Company" --owner-email owner@yourcompany.local --owner-password "Owner@123456" --owner-name "Company Owner"
```

执行后会自动：

- 创建平台租户记录
- 创建公司管理员账号
- 建立租户成员关系
- 创建该公司的独立 schema
- 初始化该 schema 下的业务表
