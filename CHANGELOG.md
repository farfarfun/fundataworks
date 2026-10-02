# CHANGELOG

## [0.1.3]

### 修复

- `create_dijob` 原先用 `method="GET"` 把全部字段（含收缩后的
  `JobSettings`/`TableMappings`/`TransformationRules`/`*DataSourceSettings`
  等 JSON 字符串）塞进 query string，与官方 SDK 的
  `create_dijob_with_options` 不符：现改为 `POST`，query 只保留
  `DestinationDataSourceType`/`JobName`/`JobType`/`MigrationType`/`Name`/
  `ProjectId`/`SourceDataSourceType`，其余字段走请求体。
- `create_disync` 原先把任务完整定义 `TaskContent` 放在 query string 里，
  现按官方 `create_disync_task_with_options` 的拼装方式移到请求体。
- 只存在于 `2024-05-18` 的 Action（`CreateNode`、`UpdateNode`、
  `CreatePipelineRun`、`GetPipelineRun`、`ExecPipelineRunStage`）以及按
  `2024-05-18` 收缩模型实现的 `ListDataSources`、`CreateDIJob`，原先一律使用
  `Client(version=...)`（默认 `2020-05-18`）作为 `Params.version`，默认配置下
  必然被网关拒绝。现由 `get_param(version=...)` 为每个 Action 固定正确版本；
  `CreateDISyncTask`（仅 `2020-05-18`）同理固定，`GetNode` 固定 `2020-05-18`。
- 修正参数类型注解：原先多个方法声明 `models_20200518.XxxRequest |
  models_20240518.XxxRequest`，但其中一侧的模型类并不存在
  （`CreateNodeRequest`/`UpdateNodeRequest`/`CreatePipelineRunRequest`/
  `ExecPipelineRunStageRequest` 只有 2024-05-18，`CreateDISyncTaskRequest`
  只有 2020-05-18），`typing.get_type_hints()` 会直接抛 `AttributeError`。
  现只声明真正支持的模型；`get_pipeline_run` 的注解由
  `CreatePipelineRunRequest` 改为正确的 `GetPipelineRunRequest`。
- `list_data_sources` 注解声明接受 2020-05-18 的请求模型，但实现读取
  2024-05-18 独有的 `types` 字段，传入前者会抛 `AttributeError`；`get_node`
  反之（读 2020-05-18 独有的 `node_id`）。注解已收窄到实际可用的版本。

### 变更

- `get_param()` 新增可选参数 `version`，为空时回退到 `self.version`。
- `Client(config, version=...)` 的作用范围缩小为与版本无关的
  `list_nodes`、`list_folders`，其余方法固定使用各自的 API 版本；README
  增加「API 版本」对照表说明。
- `README.md` 的安装说明不再写 `pip install fundataworks`——本包尚未发布到
  PyPI，改为从仓库地址安装。
- `pyproject.toml` 把 `[tool.ruff]` 移到文件末尾（原先插在
  `[dependency-groups]` 与 `[[project.authors]]` 之间），并补充
  `[tool.ruff.lint] select`。

### 新增

- `tests/test_smoke.py` 改为逐方法断言 Action / HTTP 方法 / `Params.version` /
  query / body 的完整字段映射，期望值对照官方 SDK 的 `*_with_options`
  实现核对，而非照抄本仓库实现。
- 新增注解一致性测试：参数注解里声明的每个请求模型都必须真实存在
  （`typing.get_type_hints()` 可解析），且必须真的能传进对应方法。
- 新增失败路径测试：`UtilClient.validate_model` 抛错时所有公开方法都必须在
  调用 `call_api` 之前中断。

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

### 废弃

- 无。
