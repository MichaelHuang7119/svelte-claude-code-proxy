# Svelte Claude Code Proxy

Claude API 代理管理前端界面，支持多 Provider 配置、实时监控和动态管理。

## 功能特性

- 📋 **Provider 管理**：添加、编辑、删除 Provider 配置
- 🔄 **实时监控**：自动轮询 Provider 健康状态
- ✅ **连接测试**：动态测试 Provider 连接
- ⚙️ **配置管理**：全局配置、熔断器设置
- 🎯 **多模型支持**：配置 big/middle/small 模型列表

## 配置说明

本项目支持两种方式连接后端 API，适用于不同的使用场景。

### 方式 1：直接访问后端（推荐用于生产环境）

直接连接到后端服务，绕过前端代理，性能最佳。

```bash
export ANTHROPIC_BASE_URL=http://localhost:8082
export ANTHROPIC_API_KEY="any-value"
```

**优点：**
- ✅ 性能最佳，无额外代理开销
- ✅ 直接连接，延迟最低
- ✅ 适合生产环境部署

**适用场景：**
- 生产环境部署
- 需要最高性能的场景
- 后端服务可直接访问的情况

### 方式 2：通过前端代理访问（推荐用于开发环境）

通过前端开发服务器代理访问后端，统一入口。

```bash
export ANTHROPIC_BASE_URL=http://localhost:5173
export ANTHROPIC_API_KEY="any-value"
```

**优点：**
- ✅ 统一入口点，便于管理
- ✅ CORS 问题自动处理
- ✅ 开发时更方便，无需关注后端端口
- ✅ 可在前端统一处理认证和错误

**适用场景：**
- 开发环境
- 需要统一前端管理的情况
- 需要前端代理处理 CORS 的场景

## 代理路径说明

前端代理（`http://localhost:5173`）会自动将以下路径转发到后端（`http://localhost:8082`）：

| 路径 | 说明 | 后端端点 |
|------|------|----------|
| `/v1/*` | Claude API 端点 | `/v1/messages`, `/v1/messages/count_tokens` |
| `/api/*` | 配置管理 API | `/api/config/providers`, `/api/providers/*` |
| `/health` | 健康检查 | `/health` |
| `/test-connection` | 连接测试 | `/test-connection` |

## 使用示例

### 使用方式 1（直接后端）

```bash
# 设置环境变量
export ANTHROPIC_BASE_URL=http://localhost:8082
export ANTHROPIC_API_KEY="any-value"

# 启动后端服务（端口 8082）
cd /home/huangyf/code/claude-code-proxy
python src/main.py

# Claude 客户端会直接连接到 http://localhost:8082
```

### 使用方式 2（前端代理）

```bash
# 设置环境变量
export ANTHROPIC_BASE_URL=http://localhost:5173
export ANTHROPIC_API_KEY="any-value"

# 启动后端服务（端口 8082）
cd /home/huangyf/code/claude-code-proxy
python src/main.py

# 启动前端服务（端口 5173）
cd /home/huangyf/code/svelte-claude-code-proxy
npm run dev

# Claude 客户端会连接到 http://localhost:5173，请求自动代理到后端
```

## 快速切换配置

如果需要快速切换配置方式，可以创建两个配置文件：

**`.env.direct`**（直接后端）：
```bash
ANTHROPIC_BASE_URL=http://localhost:8082
ANTHROPIC_API_KEY=any-value
```

**`.env.proxy`**（前端代理）：
```bash
ANTHROPIC_BASE_URL=http://localhost:5173
ANTHROPIC_API_KEY=any-value
```

然后使用：
```bash
# 使用直接后端
source .env.direct

# 使用前端代理
source .env.proxy
```

## 注意事项

1. **服务端口**：
   - 后端默认端口：`8082`
   - 前端默认端口：`5173`
   - 确保两个服务都在运行（使用方式2时）

2. **代理配置**：
   - 前端代理配置在 `vite.config.ts` 中
   - 仅开发环境有效（Vite dev server）
   - 生产环境需要配置反向代理（如 Nginx）

3. **API Key**：
   - `ANTHROPIC_API_KEY` 的值可以是任意值（如 "any-value"）
   - 用于客户端身份验证
   - 后端会根据配置的 provider 进行实际的 API 调用

4. **性能考虑**：
   - 方式 1（直接后端）：性能最优，延迟最低
   - 方式 2（前端代理）：有轻微性能开销，但开发体验更好

## 快速开始

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
# 确保后端服务运行在 http://localhost:8082
cd /home/huangyf/code/claude-code-proxy
python src/main.py

# 启动前端开发服务器
cd /home/huangyf/code/svelte-claude-code-proxy
npm run dev

# 或者自动打开浏览器
npm run dev -- --open
```

### 构建生产版本

```bash
npm run build
```

### 预览生产构建

```bash
npm run preview
```

## 技术栈

- **SvelteKit** - 前端框架
- **Svelte 5** - 使用最新 runes 语法
- **TypeScript** - 类型安全
- **Tailwind CSS** - 样式框架

## 项目结构

```
svelte-claude-code-proxy/
├── src/
│   ├── lib/
│   │   ├── components/      # 组件
│   │   ├── stores/          # 状态管理
│   │   ├── api/             # API 客户端
│   │   └── types/           # TypeScript 类型定义
│   └── routes/              # 页面路由
├── vite.config.ts           # Vite 配置（包含代理设置）
├── package.json
└── README.md                # 本文档
```

> To deploy your app, you may need to install an [adapter](https://svelte.dev/docs/kit/adapters) for your target environment.
