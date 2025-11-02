# 故障排除指南

## 401 Unauthorized - Invalid API key

### 问题描述
客户端请求时返回 `401 Unauthorized`，错误信息：`Invalid API key provided by client`

### 原因
后端启用了客户端 API key 验证，但客户端提供的 API key 与后端期望的值不匹配。

### 解决方案

#### 方案 1：禁用客户端 API key 验证（推荐用于开发/测试）

在 `.env` 文件中**不要设置**或**注释掉** `ANTHROPIC_API_KEY`：

```bash
# 禁用验证（不设置或设置为空）
# ANTHROPIC_API_KEY=

# 或者完全删除这一行
```

然后重启后端容器：
```bash
docker compose restart backend
```

#### 方案 2：启用并配置验证（用于生产环境）

1. 在 `.env` 文件中设置期望的 API key：
```bash
ANTHROPIC_API_KEY=your-expected-api-key-here
```

2. 客户端（Claude Code）必须使用相同的 API key：
```bash
export ANTHROPIC_API_KEY=your-expected-api-key-here
```

3. 重启后端容器：
```bash
docker compose restart backend
```

### 验证配置

检查后端日志，应该看到：
- `📊 Client API Key Validation: Disabled` - 验证已禁用
- 或 `📊 Client API Key Validation: Enabled` - 验证已启用

### 客户端使用说明

如果验证**已禁用**，客户端可以使用任何 API key（例如：`any-value`）

如果验证**已启用**，客户端必须使用与后端 `ANTHROPIC_API_KEY` 相同的值。

### 常见问题

**Q: 为什么后端显示验证已启用，但环境变量中没有设置？**
A: 这可能是配置缓存问题，尝试重启容器：
```bash
docker compose down
docker compose up -d
```

**Q: 如何确认验证是否真的被禁用？**
A: 查看后端启动日志，应该看到：
```
Warning: ANTHROPIC_API_KEY not set. Client API key validation will be disabled.
```

