# fundataworks

阿里云 DataWorks OpenAPI 的轻量 Python 客户端封装，覆盖节点、数据源、数据集成任务和工作流实例等常用接口。

## 安装

本包尚未发布到 PyPI，直接从仓库安装：

```bash
uv pip install git+https://github.com/farfarfun/fundataworks.git
```

## 最小可运行示例

```python
import os

from alibabacloud_tea_openapi import models as open_api_models
from fundataworks import Client

config = open_api_models.Config(
    access_key_id=os.environ["ALIBABA_CLOUD_ACCESS_KEY_ID"],
    access_key_secret=os.environ["ALIBABA_CLOUD_ACCESS_KEY_SECRET"],
    region_id="cn-hangzhou",
)
client = Client(config)

# 查询数据源列表需要传入对应版本的请求模型，示例：
# from alibabacloud_dataworks_public20240518 import models as models_20240518
# request = models_20240518.ListDataSourcesRequest(project_id=123456)
# result = client.list_data_sources(request)
```

## API 版本

DataWorks 有 `2020-05-18` 与 `2024-05-18` 两个 OpenAPI 版本，模型并不对称。
每个方法只接受它**实际支持**的请求模型，并固定把请求发往对应版本：

| 方法 | 请求模型来自 | 发出的 API 版本 |
| --- | --- | --- |
| `get_node` | `...20200518` | 固定 `2020-05-18` |
| `create_disync` | `...20200518` | 固定 `2020-05-18` |
| `list_data_sources` | `...20240518` | 固定 `2024-05-18` |
| `create_dijob` | `...20240518` | 固定 `2024-05-18` |
| `create_node` / `update_node` | `...20240518` | 固定 `2024-05-18` |
| `create_pipeline_run` / `get_pipeline_run` / `exec_pipeline_run_stage_with_options` | `...20240518` | 固定 `2024-05-18` |
| `list_nodes` / `list_folders` | 两个版本都可 | 跟随 `Client(config, version=...)` |

`Client(config, version="2024-05-18")` 只影响上表最后一行的两个方法。

运行前通过环境变量配置凭据：

```bash
export ALIBABA_CLOUD_ACCESS_KEY_ID="..."
export ALIBABA_CLOUD_ACCESS_KEY_SECRET="..."
```

不要将真实凭据写入代码、配置文件或日志，也不要提交到版本库。生产环境建议使用密钥管理服务注入环境变量，并按最小权限原则配置访问权限。

## 开发

```bash
uv sync --group dev
uv run ruff check --fix .
uv run ruff format .
uv run pytest
```

---

## 关于 farfarfun

[farfarfun](https://github.com/farfarfun) 是一个专注于实用工具库的开源组织，
涵盖云存储、数据处理、AI、多媒体与开发工具链等方向。

- 🏠 组织主页：<https://github.com/farfarfun>
- 📦 PyPI：<https://pypi.org/user/niuliangtao/>
- 📧 联系：farfarfun@qq.com

本项目基于 [MIT](LICENSE) 协议开源。
