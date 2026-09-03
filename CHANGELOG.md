# CHANGELOG

## [0.1.2]

### 新增

- 补充 README 简介、安装命令、最小可运行示例。
- 补充 tests/ 冒烟测试，覆盖 Client 构造与各公开方法的正常路径。

### 修复

- 修复 `core.py` 中因 `Union[models_20200518.XxxRequest, models_20240518.XxxRequest]`
  类型注解在类定义阶段被立即求值、而两个 DataWorks OpenAPI 版本请求模型不对称导致的
  `AttributeError`：为模块加入 `from __future__ import annotations`，注解不再在导入期求值。

### 变更

- `requires-python` 由 `>=3.13` 调整为 `>=3.10`，与组织规范统一。
- `pyproject.toml` 中 `[project]` 显式声明 `license = "MIT"`，移除与实际构建后端
  （hatchling）不匹配的 `[tool.setuptools] license-files` 配置。
- `Client` 及其公开方法补充中文 docstring，并将 `typing.Union`/`typing.Dict` 替换为
  `X | Y`、`dict[str, Any]` 等 3.10 新式写法。
- `.gitignore` 补充 `*.db`、`*.rar`、`.run/`、`logs/` 规则。
