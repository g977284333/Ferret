# Git提交规范

## 提交信息格式

### 标准格式

```
<type>: <subject>

<body>

<footer>
```

### 类型（Type）

- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构代码
- `test`: 测试相关
- `chore`: 构建/工具/配置
- `perf`: 性能优化

### 主题（Subject）

- 简短描述（50字符以内）
- 使用祈使句（如：add, fix, update）
- 首字母小写
- 不以句号结尾

### 正文（Body，可选）

- 详细说明修改内容
- 解释为什么修改
- 如何修改

### 示例

```bash
# 简单提交
git commit -m "feat: add Product Hunt scraper"

# 详细提交
git commit -m "refactor: restructure project directories

- Create new directory structure (docs, backend, frontend, apps, tests)
- Migrate all documents to docs directory, organized by type
- Migrate code to backend directory, modular organization
- Migrate test files to tests directory, unified management
- Update all import paths and relative path references
- Update README and document indexes
- Verify system functionality

Main improvements:
- Clear document classification (requirements, design, technical, guides, reference)
- Modular code (backend independent directory)
- Unified test management (cases, results, data separation)
- Reserved expansion space (frontend, app directories)"
```

## 编码问题

### 推荐：使用英文

**最佳实践**：使用英文写提交信息，避免编码问题。

### 如果必须使用中文

1. 确保Git配置正确（已配置）
2. 使用Git Bash而不是PowerShell
3. 或在GitHub上查看（显示正常）

## 提交频率

- 功能完成后立即提交
- 每个逻辑变更一个提交
- 不要累积大量变更

## 提交前检查

```bash
# 查看变更
git status

# 查看差异
git diff

# 运行测试
python backend/tests/validation/validate_system.py
```
