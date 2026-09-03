"""fundataworks 冒烟测试（smoke tests）。

覆盖包导入、`Client` 构造以及各公开方法的“请求对象 -> call_api”拼装路径。
不测试真实网络行为（`call_api` 被 mock 掉）。

历史说明：`core.py` 中若干方法曾用
`Union[models_20200518.XxxRequest, models_20240518.XxxRequest]` 做参数
注解，但两个 DataWorks OpenAPI 版本的请求模型并不对称
（`CreateNodeRequest`/`UpdateNodeRequest`/`CreatePipelineRunRequest`/
`ExecPipelineRunStageRequest` 仅存在于 2024-05-18 版本，
`CreateDISyncTaskRequest` 仅存在于 2020-05-18 版本），且该文件当时没有
`from __future__ import annotations`，导致注解在类定义阶段被立即求值、
从而在 import 期直接抛出 `AttributeError`。现已在 `core.py` 顶部加入
`from __future__ import annotations` 使注解延迟求值，问题修复，
本文件不再需要跳过逻辑。
"""

from __future__ import annotations

import importlib
import importlib.metadata
from unittest import mock


def test_package_metadata_is_installed():
    """fundataworks 应该已经通过可编辑安装注册到当前环境。"""
    dist_version = importlib.metadata.version("fundataworks")
    assert dist_version


def test_declared_runtime_dependencies_are_importable():
    """pyproject.toml 中声明的运行时依赖模块应该都能独立 import 成功。"""
    for mod_name in (
        "alibabacloud_tea_openapi",
        "alibabacloud_tea_util",
        "alibabacloud_dataworks_public20200518",
        "alibabacloud_dataworks_public20240518",
        "alibabacloud_openapi_util",
        "alibabacloud_endpoint_util",
    ):
        importlib.import_module(mod_name)


def test_import_top_level():
    import fundataworks

    assert hasattr(fundataworks, "Client")
    assert fundataworks.__all__ == ["Client"]


def test_import_submodules():
    import fundataworks.client
    import fundataworks.client.core

    assert fundataworks.client.Client is fundataworks.client.core.Client
    assert fundataworks.Client is fundataworks.client.core.Client


# ---------------------------------------------------------------------------
# Client 构造 —— 使用假凭据 + 已在本地 endpoint_map 命中的 region，
# 因此不会发起任何真实网络请求。
# ---------------------------------------------------------------------------


def _make_config():
    from alibabacloud_tea_openapi import models as open_api_models

    return open_api_models.Config(
        access_key_id="fake-ak-for-smoke-test",
        access_key_secret="fake-sk-for-smoke-test",
        region_id="cn-hangzhou",
    )


def test_client_construction_without_network():
    from fundataworks import Client

    client = Client(_make_config())
    assert client.version == "2020-05-18"
    # cn-hangzhou 命中 core.py 内置的 _endpoint_map，走本地解析，不发网络请求。
    assert client._endpoint == "dataworks.cn-hangzhou.aliyuncs.com"


def test_client_construction_with_explicit_version():
    from fundataworks import Client

    client = Client(_make_config(), version="2024-05-18")
    assert client.version == "2024-05-18"


def test_client_get_param_builds_expected_params():
    from fundataworks import Client

    client = Client(_make_config())
    params = client.get_param(action="GetNode")

    assert params.action == "GetNode"
    assert params.version == "2020-05-18"
    assert params.method == "POST"
    assert params.style == "RPC"


def test_get_endpoint_prefers_explicit_endpoint():
    from fundataworks import Client

    endpoint = Client.get_endpoint(
        "dataworks-public",
        "cn-hangzhou",
        "regional",
        "public",
        "aliyuncs.com",
        {"cn-hangzhou": "dataworks.cn-hangzhou.aliyuncs.com"},
        "explicit.example.com",
    )
    assert endpoint == "explicit.example.com"


def test_get_endpoint_falls_back_to_map():
    from fundataworks import Client

    endpoint = Client.get_endpoint(
        "dataworks-public",
        "cn-hangzhou",
        "regional",
        "public",
        "aliyuncs.com",
        {"cn-hangzhou": "dataworks.cn-hangzhou.aliyuncs.com"},
        "",
    )
    assert endpoint == "dataworks.cn-hangzhou.aliyuncs.com"


# ---------------------------------------------------------------------------
# 各请求方法：mock 掉 call_api（真正发起网络调用的地方），
# 只验证「请求对象 -> call_api 调用」这段拼装逻辑不会抛异常、
# 且确实按预期发起了一次调用。不触碰真实阿里云网络/凭据。
# ---------------------------------------------------------------------------


def _client_with_mocked_call_api():
    from fundataworks import Client

    client = Client(_make_config())
    client.call_api = mock.MagicMock(return_value={"body": {}})
    return client


def test_get_node_calls_api_once():
    from alibabacloud_dataworks_public20200518 import models as models_20200518

    client = _client_with_mocked_call_api()
    request = models_20200518.GetNodeRequest(node_id=1, project_env="PROD")

    result = client.get_node(request)

    client.call_api.assert_called_once()
    assert result == {"body": {}}


def test_get_node_omits_unset_fields():
    from alibabacloud_dataworks_public20200518 import models as models_20200518

    client = _client_with_mocked_call_api()
    request = models_20200518.GetNodeRequest(node_id=1)

    client.get_node(request)

    _, args, _kwargs = client.call_api.mock_calls[0]
    body = args[1].body
    assert body == {"NodeId": 1}


def test_list_data_sources_calls_api_once():
    from alibabacloud_dataworks_public20240518 import models as models_20240518

    client = _client_with_mocked_call_api()
    request = models_20240518.ListDataSourcesRequest(project_id=1)

    client.list_data_sources(request)

    client.call_api.assert_called_once()


def test_create_node_calls_api_once():
    from alibabacloud_dataworks_public20240518 import models as models_20240518

    client = _client_with_mocked_call_api()
    request = models_20240518.CreateNodeRequest(
        project_id=1, container_id="c1", scene="DATASTUDIO", spec="{}"
    )

    client.create_node(request)

    client.call_api.assert_called_once()


def test_list_nodes_calls_api_once():
    from alibabacloud_dataworks_public20240518 import models as models_20240518

    client = _client_with_mocked_call_api()
    request = models_20240518.ListNodesRequest(project_id=1)

    client.list_nodes(request)

    client.call_api.assert_called_once()


def test_update_node_calls_api_once():
    from alibabacloud_dataworks_public20240518 import models as models_20240518

    client = _client_with_mocked_call_api()
    request = models_20240518.UpdateNodeRequest(id="1", project_id=1, spec="{}")

    client.update_node(request)

    client.call_api.assert_called_once()


def test_list_folders_calls_api_once():
    from alibabacloud_dataworks_public20240518 import models as models_20240518

    client = _client_with_mocked_call_api()
    request = models_20240518.ListFoldersRequest(
        project_id=1, page_number=1, page_size=10
    )

    client.list_folders(request)

    client.call_api.assert_called_once()


def test_create_dijob_calls_api_once():
    from alibabacloud_dataworks_public20200518 import models as models_20200518

    client = _client_with_mocked_call_api()
    request = models_20200518.CreateDIJobRequest(project_id=1, job_name="smoke-job")

    client.create_dijob(request)

    client.call_api.assert_called_once()


def test_create_disync_calls_api_once():
    from alibabacloud_dataworks_public20200518 import models as models_20200518

    client = _client_with_mocked_call_api()
    request = models_20200518.CreateDISyncTaskRequest(
        project_id=1, task_name="smoke-task"
    )

    client.create_disync(request)

    client.call_api.assert_called_once()


def test_create_pipeline_run_calls_api_once():
    from alibabacloud_dataworks_public20240518 import models as models_20240518

    client = _client_with_mocked_call_api()
    request = models_20240518.CreatePipelineRunRequest(project_id=1, type="MANUAL")

    client.create_pipeline_run(request)

    client.call_api.assert_called_once()


def test_get_pipeline_run_calls_api_once():
    # 注意：core.py 里 get_pipeline_run 的类型注解写的是
    # CreatePipelineRunRequest（沿用查询字段，不影响运行时行为），
    # 这里按注解声明的类型构造请求做冒烟验证。
    from alibabacloud_dataworks_public20240518 import models as models_20240518

    client = _client_with_mocked_call_api()
    request = models_20240518.CreatePipelineRunRequest(project_id=1)

    client.get_pipeline_run(request)

    client.call_api.assert_called_once()


def test_exec_pipeline_run_stage_with_options_calls_api_once():
    from alibabacloud_dataworks_public20240518 import models as models_20240518

    client = _client_with_mocked_call_api()
    request = models_20240518.ExecPipelineRunStageRequest(
        project_id=1, id="1", code="stage-code"
    )

    client.exec_pipeline_run_stage_with_options(request)

    client.call_api.assert_called_once()


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------


def test_no_cli_entry_point_declared():
    """pyproject.toml 当前没有声明 [project.scripts]，所以没有 CLI 可测试。

    这里显式断言一下当前状态，避免以后悄悄加了 CLI 却忘了补冒烟测试。
    """
    metadata = importlib.metadata.metadata("fundataworks")
    entry_points = importlib.metadata.entry_points(group="console_scripts")
    fundataworks_scripts = [
        ep for ep in entry_points if ep.dist and ep.dist.name == "fundataworks"
    ]
    assert fundataworks_scripts == []
    assert metadata is not None
