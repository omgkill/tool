---
name: go-backend-doc
description: 根据 Go 语言小游戏后端项目代码（gRPC + HTTP）生成清晰、简洁的项目文档，包含业务逻辑、API 接口和数据库结构。当用户上传 Go 后端代码并请求生成项目文档、技术文档、API 文档或数据库设计文档时触发。
---

# Go 后端项目文档生成器

自动分析 Go 后端项目代码，生成结构化的项目文档。专为小游戏后端设计，支持 gRPC 和 HTTP 协议。

## 使用场景

当用户需要以下任一情况时使用此 skill：
- 上传了 Go 项目代码并要求生成文档
- 需要理解现有项目的架构和业务逻辑
- 需要整理 API 接口文档
- 需要梳理数据库表结构
- 项目交接或知识传递
- 代码审查前的文档准备

## 文档结构

生成的文档采用以下层次结构：

```
项目文档
├── 1. 项目概览
│   ├── 项目名称和描述
│   ├── 技术栈
│   └── 目录结构
├── 2. 核心业务逻辑
│   ├── 业务模块清单
│   └── 每个模块的核心流程
├── 3. API 接口文档
│   ├── gRPC 服务
│   └── HTTP 接口
└── 4. 数据存储
    ├── 数据库表结构
    ├── 缓存使用
    └── 数据模型关系
```

## 执行流程

### 第 1 步：代码扫描与分析

首先全面扫描项目结构，识别关键组件：

```bash
# 查看项目整体结构
find /path/to/project -type f -name "*.go" | head -20

# 识别项目入口
cat main.go

# 找到配置文件
find . -name "*.yaml" -o -name "*.toml" -o -name "*.json" -o -name "config.go"
```

**识别要点：**
- 项目使用的框架（如 gin, echo, grpc-go）
- 配置管理方式
- 日志和中间件
- 依赖项 (go.mod)

### 第 2 步：提取业务逻辑

分析 `service`、`handler`、`controller` 等业务层代码：

**关注内容：**
1. **业务模块划分**：按功能域分组（如用户系统、游戏逻辑、支付系统）
2. **核心流程**：每个模块的主要业务流程
3. **业务规则**：特殊逻辑、校验规则、计算公式
4. **错误处理**：常见错误场景和处理方式

**输出格式示例：**

```markdown
## 核心业务逻辑

### 用户系统
- **登录流程**：验证 token → 查询用户信息 → 更新最后登录时间
- **注册流程**：参数校验 → 检查用户名重复 → 创建用户记录 → 发送欢迎邮件
- **业务规则**：
  - 用户名长度 3-20 字符
  - 密码需 bcrypt 加密存储
  - 24 小时内登录失败超过 5 次则锁定账户

### 游戏逻辑
- **开始游戏**：检查用户状态 → 扣除入场费 → 创建游戏房间 → 返回房间 ID
- **结算流程**：计算得分 → 更新排行榜 → 发放奖励 → 记录游戏历史
```

### 第 3 步：提取 API 接口

#### 3.1 gRPC 接口

查找 `.proto` 文件和 gRPC 服务实现：

```bash
# 找到 proto 定义
find . -name "*.proto"

# 找到 gRPC 服务实现
grep -r "pb.Unimplemented" --include="*.go"
```

**输出格式：**

```markdown
## API 接口文档

### gRPC 服务

#### UserService
**服务定义**：`proto/user.proto`

| 方法 | 请求类型 | 响应类型 | 说明 |
|------|---------|---------|------|
| Login | LoginRequest | LoginResponse | 用户登录 |
| Register | RegisterRequest | RegisterResponse | 用户注册 |
| GetProfile | GetProfileRequest | UserProfile | 获取用户资料 |

**请求示例 - Login**：
```protobuf
message LoginRequest {
  string username = 1;  // 用户名
  string password = 2;  // 密码
}
```

**响应示例**：
```protobuf
message LoginResponse {
  int32 code = 1;       // 状态码：0 成功，其他失败
  string message = 2;   // 提示信息
  string token = 3;     // JWT token
  UserProfile user = 4; // 用户信息
}
```

**错误码**：
- `1001`: 用户名或密码错误
- `1002`: 账户已被锁定
- `1003`: 参数格式错误
```

#### 3.2 HTTP 接口

查找路由定义和 handler：

```bash
# Gin 框架
grep -r "router\\.GET\\|router\\.POST" --include="*.go"

# Echo 框架
grep -r "e\\.GET\\|e\\.POST" --include="*.go"
```

**输出格式：**

```markdown
### HTTP 接口

#### 用户模块

**POST /api/v1/user/login**
登录接口

请求参数：
```json
{
  "username": "player001",
  "password": "encrypted_password"
}
```

响应示例：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "token": "eyJhbGc...",
    "user_id": 12345,
    "nickname": "玩家001"
  }
}
```

**GET /api/v1/user/profile**
获取用户资料（需要 token）

Headers：
- `Authorization: Bearer {token}`

响应示例：
```json
{
  "code": 0,
  "data": {
    "user_id": 12345,
    "username": "player001",
    "level": 10,
    "coins": 5000
  }
}
```
```

### 第 4 步：提取数据库结构

查找数据模型定义和迁移文件：

```bash
# 查找 model/entity 文件
find . -path "*/model/*.go" -o -path "*/entity/*.go"

# 查找数据库迁移
find . -name "*migration*" -o -name "*.sql"

# 搜索 GORM 模型定义
grep -r "gorm.Model" --include="*.go"
```

**分析内容：**
1. **表结构**：字段名称、类型、约束
2. **索引设计**：主键、唯一索引、普通索引
3. **表关系**：一对多、多对多关系
4. **缓存策略**：Redis 缓存的 key 设计

**输出格式：**

```markdown
## 数据存储

### 数据库表结构

#### users 表（用户表）
| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | bigint | 用户 ID | 主键，自增 |
| username | varchar(50) | 用户名 | 唯一，非空 |
| password | varchar(255) | 密码哈希 | 非空 |
| email | varchar(100) | 邮箱 | 唯一 |
| level | int | 等级 | 默认 1 |
| coins | bigint | 金币 | 默认 0 |
| created_at | timestamp | 创建时间 | |
| updated_at | timestamp | 更新时间 | |

**索引：**
- PRIMARY KEY: `id`
- UNIQUE KEY: `username`
- UNIQUE KEY: `email`
- INDEX: `level` (用于排行榜查询)

**代码对应：**
```go
type User struct {
    ID        uint   `gorm:"primaryKey"`
    Username  string `gorm:"uniqueIndex;size:50;not null"`
    Password  string `gorm:"size:255;not null"`
    Email     string `gorm:"uniqueIndex;size:100"`
    Level     int    `gorm:"default:1"`
    Coins     int64  `gorm:"default:0"`
    CreatedAt time.Time
    UpdatedAt time.Time
}
```

#### game_records 表（游戏记录）
| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | bigint | 记录 ID | 主键 |
| user_id | bigint | 用户 ID | 外键 → users.id |
| score | int | 得分 | |
| duration | int | 游戏时长（秒） | |
| status | tinyint | 状态（0-进行中，1-已完成） | |
| created_at | timestamp | 创建时间 | |

**索引：**
- PRIMARY KEY: `id`
- INDEX: `user_id` (查询用户历史)
- INDEX: `created_at` (时间范围查询)

### 缓存设计

使用 Redis 缓存热点数据：

**用户在线状态**
- Key 格式：`online:user:{user_id}`
- 类型：String
- 过期时间：300 秒
- 值：用户最后活跃时间戳

**游戏房间信息**
- Key 格式：`room:{room_id}`
- 类型：Hash
- 字段：`creator_id`, `player_count`, `status`, `created_at`
- 过期时间：游戏结束后 1 小时

**排行榜**
- Key 格式：`leaderboard:daily:{date}`
- 类型：Sorted Set
- Score：用户积分
- Member：user_id
- 过期时间：7 天

### 数据模型关系

```
User (1) ─────< (N) GameRecord
  │
  └──────< (N) UserItem (用户道具)
              │
              └──> (1) Item (道具模板)
```

**说明**：
- 一个用户可以有多条游戏记录
- 一个用户可以拥有多个道具实例
- 每个道具实例关联一个道具模板
```

### 第 5 步：生成完整文档

将以上内容整合为结构化的 Markdown 文档：

**文档头部模板：**

```markdown
# {项目名称} 技术文档

> 生成时间：{当前时间}
> 代码版本：{Git commit hash，如可获取}

## 目录
- [项目概览](#项目概览)
- [核心业务逻辑](#核心业务逻辑)
- [API 接口文档](#api-接口文档)
- [数据存储](#数据存储)
- [部署说明](#部署说明)

---

## 项目概览

### 技术栈
- **语言**：Go {version}
- **框架**：{主要框架和库}
- **协议**：gRPC + HTTP
- **数据库**：{数据库类型和版本}
- **缓存**：Redis
- **其他**：{其他重要依赖}

### 目录结构
```
{项目树状结构}
```

### 核心依赖
{从 go.mod 提取的关键依赖}
```

## 质量标准

生成的文档应满足：

1. **完整性**：覆盖所有主要模块、接口和数据表
2. **准确性**：代码示例直接从源码提取，避免臆测
3. **简洁性**：突出重点，避免冗余描述
4. **可读性**：使用表格、代码块等格式增强可读性
5. **可维护性**：包含代码位置引用，方便后续更新

## 特殊情况处理

### 代码量过大
如果项目文件超过 50 个 Go 文件：
1. 先询问用户关注的核心模块
2. 优先分析入口文件、路由定义、核心 service
3. 提供模块化文档，允许用户按需深入

### 缺少 proto 文件
如果项目使用 gRPC 但未找到 `.proto` 文件：
1. 从生成的 `pb.go` 文件推断接口结构
2. 在文档中标注"根据生成代码推断"

### 无明确的数据库迁移
如果没有 SQL 文件或迁移工具：
1. 从 model 定义推断表结构
2. 标注"根据 GORM/数据模型推断"

### 混合架构
如果项目同时有单体和微服务特征：
1. 按服务边界分组模块
2. 在项目概览中说明架构特点

## 输出文件

生成以下文件到 `/mnt/user-data/outputs/`：

1. **README.md** - 完整项目文档（主文档）
2. **API.md** - 详细的 API 接口文档（如接口较多）
3. **DATABASE.md** - 详细的数据库设计文档（如表较多）
4. **ARCHITECTURE.md** - 架构设计和业务流程图（如逻辑复杂）

## 最佳实践

1. **使用工具辅助**：
   - 用 `tree` 命令生成目录结构
   - 用 `grep` 快速定位关键代码
   - 用 Python 脚本解析复杂的 AST（如需要）

2. **保持文档更新性**：
   - 在文档头部注明生成时间
   - 如果代码有 Git 版本，记录 commit hash

3. **交互式改进**：
   - 生成初稿后询问用户是否需要补充
   - 根据反馈调整详细程度

4. **代码引用**：
   - 重要的业务逻辑附上源码位置
   - 格式：`// 参考：service/user/login.go:45-67`

## 示例对话

**用户**：请帮我生成这个 Go 项目的文档

**Claude**：
我会分析您的 Go 后端项目并生成完整的技术文档。让我先扫描项目结构...

[扫描代码，识别关键组件]

我发现这是一个基于 Gin + gRPC 的小游戏后端项目，包含以下模块：
- 用户系统
- 游戏逻辑
- 支付系统
- 排行榜

正在提取详细信息...
- [✓] 项目结构分析
- [✓] 业务逻辑提取
- [✓] API 接口文档
- [✓] 数据库结构

文档已生成完成！主要内容包括：
1. 项目概览和技术栈
2. 3 个核心业务模块的流程说明
3. 15 个 gRPC 接口和 8 个 HTTP 接口
4. 6 个数据库表结构和缓存设计

[呈现文档文件]

需要我深入某个模块的细节吗？

---

## 注意事项

- 保护敏感信息：自动过滤密码、密钥等配置
- 如果代码中有明显的 bug 或安全隐患，在文档中标注提醒
- 对于不确定的推断，明确标注"推测"或"待确认"
- 文档语言默认中文
