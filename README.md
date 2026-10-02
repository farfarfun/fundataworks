# fundataworks

阿里云 DataWorks OpenAPI 的轻量 Python 客户端封装，覆盖节点、数据源、数据集成任务和工作流实例等常用接口。

## 安装

```bash
pip install fundataworks
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
