# fele

`fele` 是一个面向中小企业的 SaaS 进销存系统起步项目。

当前技术栈：

- `backend/`: FastAPI + SQLAlchemy
- `frontend/`: Vue 3 + SoybeanAdmin + AG Grid
- `docker-compose.yml`: 可选，本地默认使用脚本启动

## 功能概览

当前已经完成的核心能力：

- 公司管理配置
  - 公司基本信息
  - 客户档案
  - 产品类别
  - 产品资料
  - 供应商档案
- 产品支持 `SKU` 和 `条码`
- 编码规则
  - `SKU` 支持：顺序号、随机、日期+随机
  - `条码` 支持：顺序号、随机数字
- 超级管理员后台
  - 公司管理
  - 账号管理
  - 订阅管理
- 账号管理增强
  - 启停账号
  - 重置密码
  - 最近 7 次登录时间和 IP
- 订阅管理增强
  - 套餐
  - 到期时间
  - 状态
  - 授权范围
  - 状态筛选
  - 临期提醒

## 多租户设计

- 平台共用表放在平台库
- 每个公司对应一个租户
- 每个租户使用独立 schema，例如 `tenant_acme_trading`
- 超级管理员属于平台级账号
- 公司管理员和成员通过平台用户表 + 租户成员关系管理

## 一键启动

在项目根目录执行：

```powershell
.\start-dev.bat
```

脚本会自动：

- 检查并补齐 `backend/.env`
- 创建 `backend/.venv`
- 安装后端依赖
- 安装前端依赖
- 分别启动前后端开发窗口

启动后访问：

- 前端: `http://127.0.0.1:9527/login`
- 后端文档: `http://127.0.0.1:8000/docs`

## 默认账号

平台超级管理员：

- 邮箱: `admin@fele.local`
- 密码: `Admin@123456`

示例公司管理员：

- 公司: `Acme Trading`
- schema: `tenant_acme_trading`
- 邮箱: `owner@acme.local`
- 密码: `Owner@123456`

## 管理后台说明

只有超级管理员可以看到“管理后台”菜单。

包含：

- 公司管理
  - 查看全部公司
  - 启停公司
  - 查看租户信息
- 账号管理
  - 查看平台账号和公司管理员账号
  - 启停账号
  - 重置密码
  - 查看最近 7 次登录时间和 IP
- 订阅管理
  - 套餐
  - 到期时间
  - 状态
  - 授权范围
  - 状态筛选
  - 临期提醒

## 编码规则

公司管理页支持配置 `SKU` 和 `条码` 的生成规则。

当前支持：

- `SKU`
  - 顺序号
  - 随机
  - 日期 + 随机
- `条码`
  - 顺序号
  - 随机数字

产品资料新建/编辑时，`SKU` 和 `条码` 输入框后面都有一个小图标按钮，可以按当前规则直接生成编码。

## 手动创建公司租户

```powershell
d:\fele\backend\.venv\Scripts\python.exe d:\fele\backend\scripts\provision_tenant.py --company "Your Company" --owner-email owner@yourcompany.local --owner-password "Owner@123456" --owner-name "Company Owner"
```

执行后会自动：

- 创建平台租户记录
- 创建公司管理员账号
- 建立租户成员关系
- 创建公司独立 schema
- 初始化该 schema 下的业务表

## GitHub

仓库地址：

- `https://github.com/zhaoxingto/fele`
