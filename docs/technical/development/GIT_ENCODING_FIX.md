# Git提交信息中文乱码解决方案

## 问题说明

在Windows PowerShell中，Git提交信息中的中文可能显示为乱码。这是因为：
1. PowerShell默认使用GBK编码
2. Git提交信息已以UTF-8存储，但显示时编码不匹配

## 解决方案

### 方案1：使用英文提交信息（推荐）

**最简单可靠的方法**：使用英文写提交信息，避免编码问题。

```bash
git commit -m "refactor: restructure project, organize docs and code"
```

### 方案2：配置Git编码（已配置）

已设置以下Git配置：
```bash
git config --global core.quotepath false
git config --global i18n.commitencoding utf-8
git config --global i18n.logoutputencoding utf-8
```

### 方案3：使用UTF-8编码查看

在PowerShell中设置UTF-8编码：
```powershell
chcp 65001
git log --oneline -1
```

### 方案4：使用Git Bash

使用Git Bash而不是PowerShell，Git Bash对UTF-8支持更好。

## 最佳实践

### 提交信息格式（英文）

```
<type>: <subject>

<body>

<footer>
```

**类型（type）**：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具

**示例**：
```bash
git commit -m "refactor: restructure project directories

- Create new directory structure (docs, backend, frontend, apps, tests)
- Migrate all documents to docs directory
- Migrate code to backend directory
- Update all import paths and relative path references
- Verify system functionality"
```

## 当前提交信息

虽然PowerShell显示乱码，但：
- ✅ 提交信息在Git中是以UTF-8正确存储的
- ✅ 在GitHub/GitLab等平台上显示正常
- ✅ 使用Git Bash或UTF-8终端查看正常

## 验证

在GitHub上查看提交信息，应该显示正常的中文。

## 建议

**推荐使用英文提交信息**，原因：
1. 避免编码问题
2. 国际化友好
3. 更专业
4. 团队协作更方便

如果需要使用中文，确保：
1. 使用UTF-8编码
2. 在Git Bash中操作
3. 或在GitHub上查看（显示正常）
