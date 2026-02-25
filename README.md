# 🐟 闲鱼自动回复系统

## 原始项目

> https://github.com/GuDong2003/xianyu-auto-reply-fix

本项目基于以上项目进行安全修复。

## 🔒 安全修复说明

**本仓库已移除原项目中的以下不安全代码：**

| 风险类型 | 涉及文件 | 修复措施 |
|---------|---------|---------|
| **Cookie 外泄** | `XianyuAutoAsync.py` | 禁用了将 Cookie 明文发送到外部 IP `119.29.64.68:8081` 的好评接口 |
| **数据外发** | `XianyuAutoAsync.py` | 禁用了向 `36.111.68.231:3000` 发送消息的 QQ 通知接口 |
| **订单信息外泄** | `XianyuAutoAsync.py` | 禁用了向 `78shuk.top` 和 `116.196.116.76` 发送订单数据的亦凡 API |
| **远程代码执行 (RCE)** | `auto_updater.py` | 禁用了从不可信 HTTP 服务器 (`116.196.116.76`) 自动下载并执行代码的更新模块 |
| **动态代码执行** | `secure_confirm_ultra.py`<br>`secure_freeshipping_ultra.py` | 移除了多层混淆的 `exec()` 代码，替换为明文版本 |
| **统计上报** | `usage_statistics.py` | 禁用了向作者服务器上报机器指纹的功能 |
| **邮件内容外发** | `db_manager.py` | 禁用了向第三方服务器发送邮件内容的 API |
| **前端外联** | `static/js/app.js`<br>`static/index.html` | 清理了硬编码的外部 IP 地址 |
| **配置泄露** | `global_config.yml`<br>`config.py` | 清空了指向第三方服务器的 API 地址默认值 |

> ⚠️ **警告**：原项目存在多处将用户敏感数据（Cookie、订单、消息）发送到不明外部服务器的代码，且包含可能导致远程代码执行的自动更新机制。**强烈建议使用本安全修复版本**。

## 📋 项目概述

一个功能完整的闲鱼自动回复和管理系统，采用现代化的技术架构，支持多用户、多账号管理，具备智能回复、自动发货、自动确认发货、商品管理等企业级功能。系统基于Python异步编程，使用FastAPI提供RESTful API，SQLite数据库存储，支持Docker一键部署。

> **⚠️ 重要提示：本项目仅供学习研究使用，严禁商业用途！使用前请仔细阅读[版权声明](#️-版权声明与使用条款)。**

## 🏗️ 技术架构

### 核心技术栈
- **后端框架**: FastAPI + Python 3.11+ 异步编程
- **数据库**: SQLite 3 + 多用户数据隔离 + 自动迁移
- **前端**: Bootstrap 5 + Vanilla JavaScript + 响应式设计
- **通信协议**: WebSocket + RESTful API + 实时通信
- **部署方式**: Docker + Docker Compose + 一键部署
- **日志系统**: Loguru + 文件轮转 + 实时收集
- **安全认证**: JWT + 图形验证码 + 邮箱验证 + 权限控制

### 系统架构特点
- **微服务设计**: 模块化架构，易于维护和扩展
- **异步处理**: 基于asyncio的高性能异步处理
- **多用户隔离**: 完全的数据隔离和权限控制
- **容器化部署**: Docker容器化，支持一键部署
- **实时监控**: WebSocket实时通信和状态监控
- **自动化运维**: 自动重连、异常恢复、日志轮转

## ✨ 核心特性

### 🔐 多用户系统
- **用户注册登录** - 支持邮箱验证码注册，图形验证码保护
- **数据完全隔离** - 每个用户的数据独立存储，互不干扰
- **权限管理** - 严格的用户权限控制和JWT认证
- **安全保护** - 防暴力破解、会话管理、安全日志
- **授权期限管理** - 核心滑块验证模块包含授权期限验证，确保合规使用

### 📱 多账号管理
- **无限账号支持** - 每个用户可管理多个闲鱼账号
- **独立运行** - 每个账号独立监控，互不影响
- **实时状态** - 账号连接状态实时监控
- **批量操作** - 支持批量启动、停止账号任务

### 🤖 智能回复系统
- **关键词匹配** - 支持精确关键词匹配回复
- **指定商品回复** - 支持为特定商品设置专门的回复内容，优先级最高
- **商品专用关键词** - 支持为特定商品设置专用关键词回复
- **通用关键词** - 支持全局通用关键词，适用于所有商品
- **批量导入导出** - 支持Excel格式的关键词批量导入导出
- **AI智能回复** - 集成OpenAI API，支持上下文理解
- **变量替换** - 回复内容支持动态变量（用户名、商品信息、商品ID等）
- **优先级策略** - 指定商品回复 > 商品专用关键词 > 通用关键词 > 默认回复 > AI回复

### 🚚 自动发货功能
- **智能匹配** - 基于商品信息自动匹配发货规则
- **多规格支持** - 支持同一商品的不同规格自动匹配对应卡券
- **精确匹配+兜底机制** - 优先精确匹配规格，失败时自动降级到普通卡券
- **延时发货** - 支持设置发货延时时间（0-3600秒）
- **多种触发** - 支持付款消息、小刀消息等多种触发条件
- **防重复发货** - 智能防重复机制，避免重复发货
- **多种发货方式** - 支持固定文字、批量数据、API调用、图片发货等方式
- **图片发货** - 支持上传图片并自动发送给买家，图片自动上传到CDN
- **自动确认发货** - 检测到付款后自动调用闲鱼API确认发货，支持锁机制防并发
- **防重复确认** - 智能防重复确认机制，避免重复API调用
- **订单详情缓存** - 订单详情获取支持数据库缓存，大幅提升性能
- **发货统计** - 完整的发货记录和统计功能

### 🛍️ 商品管理
- **自动收集** - 消息触发时自动收集商品信息
- **API获取** - 通过闲鱼API获取完整商品详情
- **多规格支持** - 支持多规格商品的规格信息管理
- **批量管理** - 支持批量查看、编辑、切换多规格状态
- **智能去重** - 自动去重，避免重复存储

### 🔍 商品搜索功能
- **真实数据获取** - 基于Playwright技术获取真实闲鱼商品数据
- **智能排序** - 按"人想要"数量自动倒序排列
- **多页搜索** - 支持一次性获取多页商品数据
- **前端分页** - 灵活的前端分页显示
- **商品详情** - 支持查看完整商品详情信息

### 📊 系统监控
- **实时日志** - 完整的操作日志记录和查看
- **性能监控** - 系统资源使用情况监控
- **健康检查** - 服务状态健康检查

### 📁 数据管理
- **Excel导入导出** - 支持关键词数据的Excel格式导入导出
- **模板生成** - 自动生成包含示例数据的导入模板
- **批量操作** - 支持批量添加、更新关键词数据
- **数据验证** - 导入时自动验证数据格式和重复性
- **多规格卡券管理** - 支持创建和管理多规格卡券
- **发货规则管理** - 支持多规格发货规则的创建和管理
- **数据备份** - 自动数据备份和恢复
- **一键部署** - 提供预构建Docker镜像，无需编译即可快速部署

## 📁 项目结构

<details>
<summary>点击展开查看详细项目结构</summary>

```
xianyu-auto-reply/
├── 📄 核心文件
│   ├── Start.py                    # 项目启动入口，初始化所有服务
│   ├── XianyuAutoAsync.py         # 闲鱼WebSocket连接和消息处理核心
│   ├── reply_server.py            # FastAPI Web服务器和完整API接口
│   ├── db_manager.py              # SQLite数据库管理，支持多用户数据隔离
│   ├── cookie_manager.py          # 多账号Cookie管理和任务调度
│   ├── ai_reply_engine.py         # AI智能回复引擎，支持多种AI模型
│   ├── order_status_handler.py    # 订单状态处理和更新模块
│   ├── file_log_collector.py      # 实时日志收集和管理系统
│   ├── config.py                  # 全局配置文件管理器
│   ├── usage_statistics.py        # 用户统计和数据分析模块
│   ├── simple_stats_server.py     # 简单统计服务器（可选）
│   ├── build_binary_module.py     # 二进制模块编译脚本（Nuitka编译工具）
│   ├── secure_confirm_ultra.py    # 自动确认发货模块（多层加密保护）
│   ├── secure_confirm_decrypted.py # 自动确认发货模块（解密版本）
│   ├── secure_freeshipping_ultra.py # 自动免拼发货模块（多层加密保护）
│   └── secure_freeshipping_decrypted.py # 自动免拼发货模块（解密版本）
├── 🛠️ 工具模块
│   └── utils/
│       ├── xianyu_utils.py        # 闲鱼API工具函数（加密、签名、解析）
│       ├── message_utils.py       # 消息格式化和处理工具
│       ├── ws_utils.py            # WebSocket客户端封装
│       ├── image_utils.py         # 图片处理和管理工具
│       ├── image_uploader.py      # 图片上传到闲鱼CDN
│       ├── image_utils.py         # 图片处理工具（压缩、格式转换）
│       ├── item_search.py         # 商品搜索功能（基于Playwright，无头模式）
│       ├── order_detail_fetcher.py # 订单详情获取工具
│       └── qr_login.py            # 二维码登录功能
├── 🌐 前端界面
│   └── static/
│       ├── index.html             # 主管理界面（集成所有功能模块）
│       ├── login.html             # 用户登录页面
│       ├── register.html          # 用户注册页面（邮箱验证）
│       ├── js/
│       │   └── app.js             # 主要JavaScript逻辑和所有功能模块
│       ├── css/
│       │   ├── variables.css      # CSS变量定义
│       │   ├── layout.css         # 布局样式
│       │   ├── components.css     # 组件样式
│       │   ├── accounts.css       # 账号管理样式
│       │   ├── keywords.css       # 关键词管理样式
│       │   ├── items.css          # 商品管理样式
│       │   ├── logs.css           # 日志管理样式
│       │   ├── notifications.css  # 通知样式
│       │   ├── dashboard.css      # 仪表板样式
│       │   ├── admin.css          # 管理员样式
│       │   └── app.css            # 主应用样式
│       ├── lib/
│       │   ├── bootstrap/         # Bootstrap框架
│       │   └── bootstrap-icons/   # Bootstrap图标
│       ├── uploads/
│       │   └── images/            # 上传的图片文件
│       ├── userscripts/           # 油猴用户脚本
│       │   └── goofish-dark-mode.user.js # 闲鱼聊天暗色模式脚本
│       └── xianyu_js_version_2.js # 闲鱼JavaScript工具库
├── 🐳 Docker部署
│   ├── Dockerfile                 # Docker镜像构建文件（优化版）
│   ├── Dockerfile-cn             # 国内优化版Docker镜像构建文件
│   ├── docker-compose.yml        # Docker Compose一键部署配置
│   ├── docker-compose-cn.yml     # 国内优化版Docker Compose配置
│   ├── docker-deploy.sh          # Docker部署管理脚本（Linux/macOS）
│   ├── docker-deploy.bat         # Docker部署管理脚本（Windows）
│   ├── entrypoint.sh              # Docker容器启动脚本
│   └── .dockerignore             # Docker构建忽略文件
├── 🌐 Nginx配置
│   └── nginx/
│       ├── nginx.conf            # Nginx反向代理配置
│       └── ssl/                  # SSL证书目录
├── 📋 配置文件
│   ├── global_config.yml         # 全局配置文件（WebSocket、API等）
│   ├── requirements.txt          # Python依赖包列表（精简版，无内置模块）
│   ├── .gitignore                # Git忽略文件配置（完整版）
│   └── README.md                 # 项目说明文档（本文件）
└── 📊 数据目录（运行时创建）
    ├── data/                     # 数据目录（Docker挂载，自动创建）
    │   ├── xianyu_data.db        # SQLite主数据库文件
    │   ├── user_stats.db         # 用户统计数据库
    │   └── xianyu_data_backup_*.db # 数据库备份文件
    ├── logs/                     # 按日期分割的日志文件
    └── backups/                  # 其他备份文件
```

</details>

## 🚀 快速开始

**⚡ 最快部署方式（推荐）**：使用预构建镜像，无需下载源码，一条命令即可启动！

### 方式一：Docker 一键部署（最简单）⭐

<details>
<summary>暂未测试</summary>
**国内用户（阿里云镜像，推荐）**：
```bash
# 1. 创建数据目录
mkdir -p xianyu-auto-reply

# 2. 一键启动容器（支持AMD64/ARM64，自动选择架构）
docker run -d \
  -p 8080:8080 \
  --restart always \
  -v $PWD/xianyu-auto-reply/:/app/data/ \
  --name xianyu-auto-reply \
  registry.cn-shanghai.aliyuncs.com/zhinian-software/xianyu-auto-reply:latest

# 3. 访问系统
# http://localhost:8080
```

**国际用户（Docker Hub镜像）**：
```bash
# 使用Docker Hub国际镜像
docker run -d \
  -p 8080:8080 \
  --restart always \
  -v $PWD/xianyu-auto-reply/:/app/data/ \
  --name xianyu-auto-reply \
  zhinianblog/xianyu-auto-reply:latest
```

**Windows用户**：
```powershell
# 创建数据目录
mkdir xianyu-auto-reply

# 国内用户（阿里云）
docker run -d -p 8080:8080 --restart always -v %cd%/xianyu-auto-reply/:/app/data/ --name xianyu-auto-reply registry.cn-shanghai.aliyuncs.com/zhinian-software/xianyu-auto-reply:latest

# 国际用户（Docker Hub）
docker run -d -p 8080:8080 --restart always -v %cd%/xianyu-auto-reply/:/app/data/ --name xianyu-auto-reply zhinianblog/xianyu-auto-reply:latest
```

**ARM64服务器** (Oracle Cloud, AWS Graviton等)：
```bash
# Docker会自动选择ARM64镜像，无需特殊配置
docker run -d \
  -p 8080:8080 \
  --restart always \
  -v $PWD/xianyu-auto-reply/:/app/data/ \
  --name xianyu-auto-reply \
  registry.cn-shanghai.aliyuncs.com/zhinian-software/xianyu-auto-reply:latest
```

### 方式二：从源码构建部署

#### 🌍 国际版（推荐海外用户）
```bash
# 1. 克隆项目
git clone https://github.com/Mr-Q526/xianyu-auto-reply-fix.git
cd xianyu-auto-reply-fix

# 2. 使用完整版配置（包含Redis缓存等增强功能）
docker-compose up -d --build

# 3. 访问系统
# http://localhost:8080
```

#### 🇨🇳 中国版（推荐国内用户）
```bash
# 1. 克隆项目
git clone https://github.com/Mr-Q526/xianyu-auto-reply-fix.git
cd xianyu-auto-reply-fix

# 2. 使用中国镜像源配置（下载速度更快）
docker-compose -f docker-compose-cn.yml up -d --build

# 3. 访问系统
# http://localhost:8080
```

**Windows用户**：
```cmd
# 国际版
docker-compose up -d --build

# 中国版（推荐）
docker-compose -f docker-compose-cn.yml up -d --build
```
</details>

### 方式三：本地开发部署

```bash
# 1. 克隆项目
git clone https://github.com/Mr-Q526/xianyu-auto-reply-fix.git
cd xianyu-auto-reply-fix

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 3. 安装Python依赖
pip install --upgrade pip
pip install -r requirements.txt

# 4. 安装Playwright浏览器
playwright install chromium
playwright install-deps chromium  # Linux需要

# 5. 启动系统
python Start.py

# 6. 访问系统
# http://localhost:8080
```

### 📋 环境要求

- **Python**: 3.11+
- **Node.js**: 16+ (用于JavaScript执行)
- **系统**: Windows/Linux/macOS
- **架构**: x86_64 (amd64) / ARM64 (aarch64)
- **内存**: 建议2GB+
- **存储**: 建议10GB+
- **Docker**: 20.10+ (Docker部署)
- **Docker Compose**: 2.0+ (Docker部署)

### 🖥️ 多架构支持

**支持的架构**:
- ✅ **linux/amd64** - Intel/AMD处理器（传统服务器、PC、虚拟机）
- ✅ **linux/arm64** - ARM64处理器（ARM服务器、树莓派4+、Apple M系列）

**镜像仓库**:
- 🇨🇳 **阿里云**: `registry.cn-shanghai.aliyuncs.com/zhinian-software/xianyu-auto-reply:latest`
- 🌍 **Docker Hub**: `zhinianblog/xianyu-auto-reply:latest`

**自动构建**: GitHub Actions自动构建并推送多架构镜像到两个镜像仓库，Docker会自动选择匹配的架构

**适用的ARM云服务器**:
- Oracle Cloud - Ampere A1 (永久免费4核24GB)
- AWS - Graviton2/3实例
- 阿里云 - 倚天710实例
- 腾讯云 - 星星海ARM实例
- 华为云 - 鲲鹏ARM实例

### ⚙️ 环境变量配置（可选）

系统支持通过环境变量进行配置，主要配置项包括：

```bash
# 基础配置
WEB_PORT=8080                          # Web服务端口
API_HOST=0.0.0.0                       # API服务主机
TZ=Asia/Shanghai                       # 时区设置

# 数据库配置
DB_PATH=data/xianyu_data.db            # 数据库文件路径（默认在data目录）

# 管理员配置
ADMIN_USERNAME=admin                   # 管理员用户名
ADMIN_PASSWORD=admin123                # 管理员密码（请修改）
JWT_SECRET_KEY=your-secret-key         # JWT密钥（请修改）

# 功能开关
AUTO_REPLY_ENABLED=true                # 启用自动回复
AUTO_DELIVERY_ENABLED=true             # 启用自动发货
AI_REPLY_ENABLED=false                 # 启用AI回复

# 日志配置
LOG_LEVEL=INFO                         # 日志级别
SQL_LOG_ENABLED=true                   # SQL日志

# 资源限制
MEMORY_LIMIT=2048                      # 内存限制(MB)
CPU_LIMIT=2.0                          # CPU限制(核心数)

# 更多配置请参考 docker-compose.yml 文件
```

> 💡 **提示**：所有配置项都有默认值，可根据需要选择性配置



### 🌐 访问系统

部署完成后，您可以通过以下方式访问系统：

- **Web管理界面**：http://localhost:8090
- **默认管理员账号**：
  - 用户名：`admin`
  - 密码：`admin123`
- **API文档**：http://localhost:8090/docs
- **健康检查**：http://localhost:8090/health

> ⚠️ **安全提示**：首次登录后请立即修改默认密码！


## 📋 系统使用

### 1. 用户注册
- 访问 `http://localhost:8090/register.html`
- 填写用户信息，完成邮箱验证
- 输入图形验证码完成注册

### 2. 添加闲鱼账号
- 登录系统后进入主界面
- 点击"添加新账号"
- 输入账号ID和完整的Cookie值
- 系统自动启动账号监控任务

### 3. 配置自动回复
- **关键词回复**：设置关键词和对应回复内容
- **AI回复**：配置OpenAI API密钥启用智能回复
- **默认回复**：设置未匹配时的默认回复

### 4. 设置自动发货
- 添加发货规则，设置商品关键词和发货内容
- 支持文本内容和卡密文件两种发货方式
- 系统检测到付款消息时自动确认发货并自动发货

### 5. 使用商品搜索功能
- 访问商品搜索页面（需要登录）
- 输入搜索关键词和查询页数
- 系统自动获取真实闲鱼商品数据
- 商品按"人想要"数量自动排序
- 支持查看商品详情和跳转到闲鱼页面

### 6. 安装闲鱼聊天暗色模式脚本（可选）
本项目提供了一个油猴用户脚本，可为闲鱼官网聊天页面添加暗色模式支持。

**安装步骤**：
1. 安装油猴扩展（Tampermonkey）到您的浏览器
2. 访问 `static/userscripts/goofish-dark-mode.user.js` 获取脚本
3. 在油猴扩展中创建新脚本，粘贴脚本内容并保存
4. 访问闲鱼聊天页面（goofish.com/im*）即可生效

**功能特性**：
- 支持三种模式：开启 / 关闭 / 跟随系统
- 通过油猴菜单快速切换暗色模式状态
- 参考 macOS/Discord 风格的简洁配色方案

## 🏗️ 系统架构

```
┌─────────────────────────────────────┐
│           Web界面 (FastAPI)         │
│         用户管理 + 功能界面          │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│        CookieManager               │
│         多账号任务管理              │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│      XianyuLive (多实例)           │
│     WebSocket连接 + 消息处理        │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│        SQLite数据库                │
│   用户数据 + 商品信息 + 配置数据     │
└─────────────────────────────────────┘
```

## ⚙️ 配置说明

### 管理员密码配置

**重要**：为了系统安全，强烈建议修改默认管理员密码！

#### 默认密码
- **用户名**：`admin`
- **默认密码**：`admin123`
- **初始化机制**：首次创建数据库时自动创建admin用户


### 全局配置文件
`global_config.yml` 包含详细的系统配置，支持：
- WebSocket连接参数
- API接口配置
- 自动回复设置
- 商品管理配置
- 日志配置等

## 🔧 高级功能

### AI回复配置
1. 在用户设置中配置OpenAI API密钥
2. 选择AI模型（支持GPT-3.5、GPT-4、通义千问等）
3. 设置回复策略和提示词
4. 启用AI回复功能

### 自动发货规则
1. 进入发货管理页面
2. 添加发货规则，设置商品关键词
3. 上传卡密文件或输入发货内容
4. 系统自动匹配商品并发货

### 商品信息管理
1. 系统自动收集消息中的商品信息
2. 通过API获取完整商品详情
3. 支持手动编辑商品信息
4. 为自动发货提供准确的商品数据

## 📊 监控和维护

### 日志管理
- **实时日志**：Web界面查看实时系统日志
- **日志文件**：`logs/` 目录下的按日期分割的日志文件
- **日志级别**：支持DEBUG、INFO、WARNING、ERROR级别

## 🤝 贡献指南

欢迎为项目做出贡献！您可以通过以下方式参与：

### 📝 提交问题
- 在 [GitHub Issues](https://github.com/Mr-Q526/xianyu-auto-reply-fix/issues) 中报告Bug
- 提出新功能建议和改进意见
- 分享使用经验和最佳实践

### 🔧 代码贡献
- Fork 项目到您的GitHub账号
- 创建功能分支：`git checkout -b feature/your-feature`
- 提交更改：`git commit -am 'Add some feature'`
- 推送分支：`git push origin feature/your-feature`
- 提交 Pull Request


## ❓ 常见问题

### 1. 端口被占用
如果8090端口被占用，可以修改 `global_config.yml` 文件中的 `AUTO_REPLY.api.port` 配置，或者在 Docker 启动时通过环境变量 `WEB_PORT` 指定端口。

### 2. 数据库连接失败
检查数据库文件权限，确保应用有读写权限。

### 3. WebSocket连接失败
检查防火墙设置，确保WebSocket端口可以访问。

### 4. Shell脚本执行错误（Linux/macOS）
如果遇到 `bad interpreter` 错误，说明脚本的行结束符格式不正确：

```bash
# 方法1：手动修复行结束符
sed -i 's/\r$//' docker-deploy.sh
chmod +x docker-deploy.sh
./docker-deploy.sh

# 方法2：直接使用bash运行
bash docker-deploy.sh
```

### 5. Docker容器启动失败
如果遇到 `exec /app/entrypoint.sh: no such file or directory` 错误：

```bash
# 确保entrypoint.sh文件存在并重新构建
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 6. 预构建镜像拉取失败
如果无法拉取预构建镜像，可以使用源码构建：

```bash
# 克隆项目并从源码构建
git clone https://github.com/Mr-Q526/xianyu-auto-reply-fix.git
cd xianyu-auto-reply-fix
./docker-deploy.sh
```

### 7. Windows系统部署
Windows用户推荐使用批处理脚本：

```cmd
# 使用Windows批处理脚本
docker-deploy.bat

# 或者使用PowerShell
powershell -ExecutionPolicy Bypass -File docker-deploy.bat
```

## ⚖️ 版权声明

**本项目仅供学习和研究使用，严禁商业用途！**

- **原项目作者**：zhinianboke / GuDong2003
- **原项目地址**：https://github.com/GuDong2003/xianyu-auto-reply-fix
- **安全修复版**：https://github.com/Mr-Q526/xianyu-auto-reply-fix

使用本项目产生的任何风险由使用者自行承担，作者不对使用本项目造成的任何损失承担责任。

---

## 🗺️ 未来规划

因安全原因禁用的功能将逐步以**本地化方案**重新实现，核心原则是所有数据处理在本地完成，不依赖不可信的第三方服务器。

### 安全功能修复

| 功能 | 原问题 | 计划方案 | 阶段 |
|-----|--------|---------|------|
| **自动好评** | Cookie 外发到第三方服务器 | 本地直接调用闲鱼官方 API | 第一阶段 |
| **邮件发送** | 邮件内容经由第三方代发 | 完善 SMTP 直发，添加配置引导 | 第一阶段 |
| **QQ 通知** | 消息发送到不明 QQ 机器人 | 支持自部署的开源 QQ 机器人框架 | 第二阶段 |
| **商品详情获取** | 数据经由第三方 API 中转 | 本地直接调用闲鱼 API + Playwright | 第二阶段 |
| **安全自动更新** | 从 HTTP 裸 IP 下载代码执行 | 基于 GitHub Releases + SHA256 校验 | 第三阶段 |
| **卡券 API** | 订单数据外发到第三方 | 设计通用接口规范，支持自有服务 | 第三阶段 |

### 新功能开发

| 功能 | 描述 | 阶段 |
|-----|------|------|
| **📊 销售可视化分析** | 销售趋势图、热销商品排行、买家分析、时段分析、数据导出 | 第二阶段 |
| **🤖 Agent 自动采购** | 对接发卡平台 API，库存不足自动采购 | 第四阶段 |
| **☁️ 百度网盘自动上传** | 采购资源自动上传网盘，生成分享链接 | 第四阶段 |
| **🎫 智能卡券管理** | 自动创建卡券、关联商品、同步库存 | 第四阶段 |
| **⚡ 自动发货规则生成** | 新商品自动创建发货规则，自动填充网盘链接 | 第四阶段 |
| **🔄 全流程编排引擎** | 可视化工作流配置，实现采购→上传→卡券→发货全自动 | 第四阶段 |

完整的开发路线图请参阅 [ROADMAP.md](ROADMAP.md)。

---

🎉 **开始使用闲鱼自动回复系统，让您的闲鱼店铺管理更加智能高效！**

**⚠️ 重要提醒：本项目仅供学习研究使用，严禁商业用途！**

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Mr-Q526/xianyu-auto-reply-fix&type=Date)](https://www.star-history.com/#Mr-Q526/xianyu-auto-reply-fix&Date)
