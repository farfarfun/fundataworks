"""fundataworks 测试。

覆盖包导入、`Client` 构造，以及各公开方法的「请求对象 -> call_api」拼装路径：
Action 名、HTTP 方法、API 版本号、query/body 字段映射，以及校验失败的错误路径。
不触碰真实网络（`call_api` 被 mock 掉）。

期望值不是照抄实现，而是对照官方 SDK
（`alibabacloud_dataworks_public20200518` / `...20240518` 的
`*_with_options` 方法）逐个核对后写死的，避免把实现里的缺陷当成契约固化下来。
"""

from __future__ import annotations

import importlib
import importlib.metadata
import typing
from unittest import mock

import pytest


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
    assert params.protocol == "HTTPS"
    assert params.pathname == "/"
    assert params.auth_type == "AK"
    assert params.req_body_type == "formData"
    assert params.body_type == "json"


def test_get_param_version_override_and_fallback():
    """`version=` 显式传入时优先于 `self.version`，不传则回退。"""
    from fundataworks import Client

    client = Client(_make_config())

    assert client.get_param(action="CreateNode", version="2024-05-18").version == (
        "2024-05-18"
    )
    assert client.get_param(action="ListNodes").version == "2020-05-18"
    # None 等价于不传。
    assert client.get_param(action="ListNodes", version=None).version == "2020-05-18"


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


def test_get_endpoint_falls_back_to_generated_rule_for_unknown_region():
    from fundataworks import Client

    endpoint = Client.get_endpoint(
        "dataworks-public",
        "unknown-region",
        "regional",
        "public",
        "aliyuncs.com",
        {},
        "",
    )

    assert endpoint == "dataworks-public.unknown-region.aliyuncs.com"


# ---------------------------------------------------------------------------
# 各请求方法：mock 掉 call_api（真正发起网络调用的地方），
# 断言 Action / HTTP 方法 / API 版本 / query / body 的完整映射。
# ---------------------------------------------------------------------------


def _client_with_mocked_call_api(version: str = "2020-05-18"):
    from fundataworks import Client

    client = Client(_make_config(), version=version)
    client.call_api = mock.MagicMock(return_value={"body": {}})
    return client


def _assert_api_call(client, action, method, api_version, *, query=None, body=None):
    client.call_api.assert_called_once()
    params, request, runtime = client.call_api.call_args.args
    assert params.action == action
    assert params.method == method
    assert params.version == api_version
    assert request.query == query
    assert request.body == body
    assert runtime is not None


def test_get_node_builds_2020_body_and_pins_version():
    """GetNode 按 2020-05-18 的 NodeId/ProjectEnv 拼 body，版本固定 2020-05-18。"""
    from alibabacloud_dataworks_public20200518 import models as models_20200518

    client = _client_with_mocked_call_api(version="2024-05-18")
    request = models_20200518.GetNodeRequest(node_id=1, project_env="PROD")

    result = client.get_node(request)

    _assert_api_call(
        client,
        "GetNode",
        "POST",
        "2020-05-18",
        body={"NodeId": 1, "ProjectEnv": "PROD"},
    )
    assert result == {"body": {}}


def test_get_node_omits_unset_fields():
    from alibabacloud_dataworks_public20200518 import models as models_20200518

    client = _client_with_mocked_call_api()
    request = models_20200518.GetNodeRequest(node_id=1)

    client.get_node(request)

    _assert_api_call(client, "GetNode", "POST", "2020-05-18", body={"NodeId": 1})


def test_list_data_sources_pins_2024_and_shrinks_types():
    """ListDataSources 用 2024-05-18 的收缩模型，`types` 以 simple 风格拼进 query。"""
    from alibabacloud_dataworks_public20240518 import models as models_20240518

    client = _client_with_mocked_call_api()
    request = models_20240518.ListDataSourcesRequest(
        project_id=1, types=["mysql", "odps"]
    )

    client.list_data_sources(request)

    _assert_api_call(
        client,
        "ListDataSources",
        "GET",
        "2024-05-18",
        query={"ProjectId": "1", "Types": "mysql,odps"},
    )


def test_create_node_pins_2024_and_maps_body():
    from alibabacloud_dataworks_public20240518 import models as models_20240518

    client = _client_with_mocked_call_api()
    request = models_20240518.CreateNodeRequest(
        project_id=1, container_id="c1", scene="DATASTUDIO", spec="{}"
    )

    client.create_node(request)

    _assert_api_call(
        client,
        "CreateNode",
        "POST",
        "2024-05-18",
        body={
            "ContainerId": "c1",
            "ProjectId": 1,
            "Scene": "DATASTUDIO",
            "Spec": "{}",
        },
    )


def test_list_nodes_follows_client_version():
    """ListNodes 与版本无关，直接序列化请求模型，版本跟随 Client(version=...)。"""
    from alibabacloud_dataworks_public20240518 import models as models_20240518

    client = _client_with_mocked_call_api(version="2024-05-18")
    request = models_20240518.ListNodesRequest(project_id=1, name="n")

    client.list_nodes(request)

    _assert_api_call(
        client,
        "ListNodes",
        "GET",
        "2024-05-18",
        query={"Name": "n", "ProjectId": "1"},
    )


def test_update_node_pins_2024_and_maps_body():
    from alibabacloud_dataworks_public20240518 import models as models_20240518

    client = _client_with_mocked_call_api()
    request = models_20240518.UpdateNodeRequest(id="1", project_id=1, spec="{}")

    client.update_node(request)

    _assert_api_call(
        client,
        "UpdateNode",
        "POST",
        "2024-05-18",
        body={"Id": "1", "ProjectId": 1, "Spec": "{}"},
    )


def test_list_folders_follows_client_version():
    from alibabacloud_dataworks_public20200518 import models as models_20200518

    client = _client_with_mocked_call_api()
    request = models_20200518.ListFoldersRequest(
        project_id=1, page_number=1, page_size=10
    )

    client.list_folders(request)

    _assert_api_call(
        client,
        "ListFolders",
        "POST",
        "2020-05-18",
        body={"PageNumber": 1, "PageSize": 10, "ProjectId": 1},
    )


def test_create_dijob_is_post_with_query_body_split():
    """CreateDIJob 必须是 POST，且大字段（收缩后的 JSON）走 body、不进 query。

    对照官方 `alibabacloud_dataworks_public20240518` 的
    `create_dijob_with_options`：query 只放 DestinationDataSourceType /
    JobName / JobType / MigrationType / Name / ProjectId /
    SourceDataSourceType，其余（含 *Settings、TableMappings、
    TransformationRules、Description）全部放 body。
    """
    from alibabacloud_dataworks_public20240518 import models as models_20240518

    client = _client_with_mocked_call_api()
    request = models_20240518.CreateDIJobRequest(
        project_id=1,
        job_name="smoke-job",
        job_type="DATABASE_REALTIME_MIGRATION",
        migration_type="FullAndRealtimeIncremental",
        name="smoke",
        source_data_source_type="MySQL",
        destination_data_source_type="Hologres",
        description="desc",
        job_settings=models_20240518.CreateDIJobRequestJobSettings(
            channel_settings='{"structInfo":"MANAGED"}'
        ),
    )

    client.create_dijob(request)

    client.call_api.assert_called_once()
    params, api_request, _runtime = client.call_api.call_args.args
    assert params.action == "CreateDIJob"
    assert params.method == "POST"
    assert params.version == "2024-05-18"
    assert api_request.query == {
        "DestinationDataSourceType": "Hologres",
        "JobName": "smoke-job",
        "JobType": "DATABASE_REALTIME_MIGRATION",
        "MigrationType": "FullAndRealtimeIncremental",
        "Name": "smoke",
        "ProjectId": "1",
        "SourceDataSourceType": "MySQL",
    }
    # 收缩后的 JSON 必须在 body 里，query 里一个都不能出现。
    assert api_request.body["Description"] == "desc"
    assert "structInfo" in api_request.body["JobSettings"]
    for shrink_key in (
        "JobSettings",
        "TableMappings",
        "TransformationRules",
        "SourceDataSourceSettings",
        "DestinationDataSourceSettings",
        "Description",
    ):
        assert shrink_key not in api_request.query


def test_create_disync_puts_task_content_in_body():
    """CreateDISyncTask 的 TaskContent 是完整任务 JSON，必须走 body。

    对照官方 `alibabacloud_dataworks_public20200518` 的
    `create_disync_task_with_options`：query 放 ClientToken / ProjectId /
    TaskName / TaskParam / TaskType，body 只放 TaskContent。
    """
    from alibabacloud_dataworks_public20200518 import models as models_20200518

    client = _client_with_mocked_call_api(version="2024-05-18")
    request = models_20200518.CreateDISyncTaskRequest(
        project_id=1,
        task_name="smoke-task",
        task_type="DI_OFFLINE",
        task_param='{"concurrent":1}',
        client_token="token-1",
        task_content='{"type":"job","steps":[]}',
    )

    client.create_disync(request)

    _assert_api_call(
        client,
        "CreateDISyncTask",
        "POST",
        "2020-05-18",
        query={
            "ClientToken": "token-1",
            "ProjectId": "1",
            "TaskName": "smoke-task",
            "TaskParam": '{"concurrent":1}',
            "TaskType": "DI_OFFLINE",
        },
        body={"TaskContent": '{"type":"job","steps":[]}'},
    )


def test_create_pipeline_run_pins_2024_and_shrinks_object_ids():
    from alibabacloud_dataworks_public20240518 import models as models_20240518

    client = _client_with_mocked_call_api()
    request = models_20240518.CreatePipelineRunRequest(
        project_id=1, type="MANUAL", object_ids=["a", "b"], description="d"
    )

    client.create_pipeline_run(request)

    _assert_api_call(
        client,
        "CreatePipelineRun",
        "POST",
        "2024-05-18",
        body={
            "Description": "d",
            "ObjectIds": '["a","b"]',
            "ProjectId": 1,
            "Type": "MANUAL",
        },
    )


def test_get_pipeline_run_pins_2024():
    from alibabacloud_dataworks_public20240518 import models as models_20240518

    client = _client_with_mocked_call_api()
    request = models_20240518.GetPipelineRunRequest(project_id=1, id="run-1")

    client.get_pipeline_run(request)

    _assert_api_call(
        client,
        "GetPipelineRun",
        "GET",
        "2024-05-18",
        query={"Id": "run-1", "ProjectId": "1"},
    )


def test_exec_pipeline_run_stage_splits_query_and_body():
    from alibabacloud_dataworks_public20240518 import models as models_20240518

    client = _client_with_mocked_call_api()
    request = models_20240518.ExecPipelineRunStageRequest(
        project_id=1, id="1", code="stage-code"
    )

    client.exec_pipeline_run_stage_with_options(request)

    _assert_api_call(
        client,
        "ExecPipelineRunStage",
        "POST",
        "2024-05-18",
        query={"ProjectId": "1"},
        body={"Code": "stage-code", "Id": "1"},
    )


# ---------------------------------------------------------------------------
# 类型注解必须与实现真正支持的请求模型一致
# ---------------------------------------------------------------------------

PUBLIC_REQUEST_METHODS = (
    "get_node",
    "list_data_sources",
    "create_node",
    "list_nodes",
    "update_node",
    "list_folders",
    "create_dijob",
    "create_disync",
    "create_pipeline_run",
    "get_pipeline_run",
    "exec_pipeline_run_stage_with_options",
)


def _annotated_request_types(method_name):
    """取出某个方法参数注解里声明的所有请求模型类。"""
    from fundataworks.client import core

    hints = typing.get_type_hints(getattr(core.Client, method_name))
    annotation = next(
        value for key, value in hints.items() if key not in ("return", "self")
    )
    args = typing.get_args(annotation)
    return list(args) if args else [annotation]


@pytest.mark.parametrize("method_name", PUBLIC_REQUEST_METHODS)
def test_annotations_resolve_to_existing_models(method_name):
    """注解不得引用某个版本里并不存在的模型类。

    两个 DataWorks 版本的模型并不对称（例如 `CreateNodeRequest` 只有
    2024-05-18 有），注解里写上不存在的类会让 `typing.get_type_hints()`
    直接抛 `AttributeError`，类型检查器也拿不到正确信息。
    """
    types = _annotated_request_types(method_name)
    assert types
    for request_type in types:
        assert isinstance(request_type, type)
        assert request_type.__name__.endswith("Request")


@pytest.mark.parametrize("method_name", PUBLIC_REQUEST_METHODS)
def test_every_annotated_request_model_actually_works(method_name):
    """注解里声明的每个请求模型都必须真的能传进去（空请求的边界路径）。

    这条用来拦住「注解声明支持某版本模型、但实现读的是另一版本独有字段」
    的情况，例如 `list_data_sources` 读 2024-05-18 独有的 `types`。
    """
    for request_type in _annotated_request_types(method_name):
        client = _client_with_mocked_call_api()
        getattr(client, method_name)(request_type())
        client.call_api.assert_called_once()


# ---------------------------------------------------------------------------
# 失败路径
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("method_name", PUBLIC_REQUEST_METHODS)
def test_validation_failure_short_circuits_before_call_api(method_name):
    """请求校验失败时必须在发请求之前抛出，不能把非法请求发到线上。"""
    from fundataworks.client import core

    request_type = _annotated_request_types(method_name)[0]
    client = _client_with_mocked_call_api()

    with mock.patch.object(
        core.UtilClient,
        "validate_model",
        side_effect=ValueError("invalid request"),
    ):
        with pytest.raises(ValueError, match="invalid request"):
            getattr(client, method_name)(request_type())

    client.call_api.assert_not_called()


def test_unknown_region_without_endpoint_map_entry_still_constructs():
    """未命中内置 endpoint_map 的 region 走规则生成，不应抛异常。"""
    from alibabacloud_tea_openapi import models as open_api_models

    from fundataworks import Client

    config = open_api_models.Config(
        access_key_id="fake-ak",
        access_key_secret="fake-sk",
        region_id="ap-northeast-2",
    )
    client = Client(config)
    assert client._endpoint == "dataworks-public.ap-northeast-2.aliyuncs.com"


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
