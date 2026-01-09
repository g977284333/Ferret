# 调试启动问题

## 窗口立即关闭的原因

窗口立即关闭通常是因为：
1. Python代码有语法错误
2. 导入模块失败
3. 运行时错误

## 查看错误信息的方法

### 方法1：使用查看启动错误.bat（推荐）

1. 双击运行：`查看启动错误.bat`
2. 这个脚本会：
   - 先测试导入是否成功
   - 如果导入失败，会显示错误并暂停
   - 如果导入成功，会启动服务器

### 方法2：在PowerShell中手动运行

1. 打开PowerShell
2. 运行以下命令：
   ```powershell
   cd D:\workspace\GC\Ferret\frontend\web
   python app.py
   ```
3. **不要关闭窗口**，查看完整的错误信息
4. 把错误信息复制给我

### 方法3：测试导入

先测试是否能正常导入：
```powershell
cd D:\workspace\GC\Ferret\frontend\web
python -c "from app import app; print('OK')"
```

如果这个命令失败，说明是导入问题。

## 常见错误及解决方法

### 错误1：ModuleNotFoundError

**错误信息**：
```
ModuleNotFoundError: No module named 'xxx'
```

**解决方法**：
```powershell
pip install flask flask-cors pytrends pandas
```

### 错误2：ImportError

**错误信息**：
```
ImportError: cannot import name 'xxx' from 'yyy'
```

**解决方法**：
- 检查文件路径是否正确
- 检查模块是否存在

### 错误3：SyntaxError

**错误信息**：
```
SyntaxError: invalid syntax
```

**解决方法**：
- 检查代码语法
- 查看错误提示的行号

## 请提供的信息

如果还是无法启动，请提供：

1. **运行 `python app.py` 后的完整输出**
   - 包括所有错误信息
   - 包括最后几行输出

2. **或者运行 `查看启动错误.bat` 后显示的内容**

3. **或者运行测试导入命令的输出**：
   ```powershell
   python -c "from app import app; print('OK')"
   ```

把这些信息发给我，我会帮你解决问题。
