# fundataworks

阿里云 DataWorks OpenAPI 的轻量 Python 客户端封装，覆盖节点、数据源、数据集成任务和工作流实例等常用接口。

## 安装

```bash
pip install fundataworks
```

## 最小可运行示例

```python
from alibabacloud_tea_openapi import models as open_api_models
from fundataworks import Client

config = open_api_models.Config(
    access_key_id="<your-access-key-id>",
    access_key_secret="<your-access-key-secret>",
    region_id="cn-hangzhou",
)
client = Client(config)

# 查询数据源列表需要传入对应版本的请求模型，示例：
# from alibabacloud_dataworks_public20240518 import models as models_20240518
# request = models_20240518.ListDataSourcesRequest(project_id=123456)
# result = client.list_data_sources(request)
```

---

## 关于 farfarfun

[farfarfun](https://github.com/farfarfun) 是一个专注于实用工具库的开源组织，
涵盖云存储、数据处理、AI、多媒体与开发工具链等方向。

- 🏠 组织主页：<https://github.com/farfarfun>
- 📦 PyPI：<https://pypi.org/user/niuliangtao/>
- 📧 联系：farfarfun@qq.com

本项目基于 [MIT](LICENSE) 协议开源。
