"""阿里云 DataWorks OpenAPI 客户端封装。

关于 API 版本：DataWorks 的两个 OpenAPI 版本（2020-05-18 与 2024-05-18）
请求模型并不对称，同名 Action 的请求拼装方式也可能不同。因此本模块的每个方法
只声明它**实际支持**的请求模型，并在 `Params` 里固定对应的 API 版本：

- 只存在于 2024-05-18 的 Action：`CreateNode`、`UpdateNode`、
  `CreatePipelineRun`、`GetPipelineRun`、`ExecPipelineRunStage`；
- 只存在于 2020-05-18 的 Action：`CreateDISyncTask`；
- 两个版本都有、但本模块按某一版本的字段拼装的：`GetNode`（2020-05-18 的
  `NodeId`/`ProjectEnv`）、`ListDataSources` 与 `CreateDIJob`（2024-05-18 的
  收缩请求模型）；
- 真正与版本无关（直接把请求模型序列化成 query）的：`ListNodes`、
  `ListFolders`，这两个方法沿用 `Client(version=...)` 指定的版本。

`from __future__ import annotations` 保留，使注解延迟求值、降低导入开销。
"""

from __future__ import annotations

from typing import Any

from alibabacloud_dataworks_public20200518 import models as models_20200518
from alibabacloud_dataworks_public20240518 import models as models_20240518
from alibabacloud_endpoint_util.client import Client as EndpointUtilClient
from alibabacloud_openapi_util.client import Client as OpenApiUtilClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_openapi.client import Client as OpenApiClient
from alibabacloud_tea_openapi.models import OpenApiRequest, Params
from alibabacloud_tea_util.client import Client as UtilClient
from alibabacloud_tea_util.models import RuntimeOptions

#: DataWorks OpenAPI 的两个版本号。
API_VERSION_2020 = "2020-05-18"
API_VERSION_2024 = "2024-05-18"


class Client(OpenApiClient):
    """阿里云 DataWorks OpenAPI 客户端。

    封装节点、数据源、数据集成任务（DI Job / DISync Task）、目录以及
    工作流实例（Pipeline Run）等常用接口的请求拼装与调用。
    """

    def __init__(
        self, config: open_api_models.Config, version: str = API_VERSION_2020
    ) -> None:
        """初始化客户端。

        参数:
            config: 阿里云 OpenAPI 通用配置（AK/SK、region 等）。
            version: 与版本无关的方法（`list_nodes`、`list_folders`）默认使用的
                DataWorks OpenAPI 版本号，默认 `2020-05-18`，另支持
                `2024-05-18`。其余方法的实现只对应某一个版本，会固定使用该
                版本，不受此参数影响（见模块 docstring）。
        """
        super().__init__(config)
        self.version = version
        self._endpoint_rule = "regional"
        self._endpoint_map = {
            "ap-northeast-1": "dataworks.ap-northeast-1.aliyuncs.com",
            "ap-south-1": "dataworks.ap-south-1.aliyuncs.com",
            "ap-southeast-1": "dataworks.ap-southeast-1.aliyuncs.com",
            "ap-southeast-2": "dataworks.ap-southeast-2.aliyuncs.com",
            "ap-southeast-3": "dataworks.ap-southeast-3.aliyuncs.com",
            "ap-southeast-5": "dataworks.ap-southeast-5.aliyuncs.com",
            "cn-beijing": "dataworks.cn-beijing.aliyuncs.com",
            "cn-chengdu": "dataworks.cn-chengdu.aliyuncs.com",
            "cn-hangzhou": "dataworks.cn-hangzhou.aliyuncs.com",
            "cn-hongkong": "dataworks.cn-hongkong.aliyuncs.com",
            "cn-huhehaote": "dataworks.aliyuncs.com",
            "cn-qingdao": "dataworks.aliyuncs.com",
            "cn-shanghai": "dataworks.cn-shanghai.aliyuncs.com",
            "cn-shenzhen": "dataworks.cn-shenzhen.aliyuncs.com",
            "cn-zhangjiakou": "dataworks.aliyuncs.com",
            "eu-central-1": "dataworks.eu-central-1.aliyuncs.com",
            "eu-west-1": "dataworks.eu-west-1.aliyuncs.com",
            "me-east-1": "dataworks.me-east-1.aliyuncs.com",
            "us-east-1": "dataworks.us-east-1.aliyuncs.com",
            "us-west-1": "dataworks.us-west-1.aliyuncs.com",
            "cn-hangzhou-finance": "dataworks.aliyuncs.com",
            "cn-shenzhen-finance-1": "dataworks.aliyuncs.com",
            "cn-shanghai-finance-1": "dataworks.aliyuncs.com",
            "cn-north-2-gov-1": "dataworks.aliyuncs.com",
        }
        self.check_config(config)
        self._endpoint = self.get_endpoint(
            "dataworks-public",
            self._region_id,
            self._endpoint_rule,
            self._network,
            self._suffix,
            self._endpoint_map,
            self._endpoint,
        )

    @staticmethod
    def get_endpoint(
        product_id: str,
        region_id: str,
        endpoint_rule: str,
        network: str,
        suffix: str,
        endpoint_map: dict[str, str],
        endpoint: str,
    ) -> str:
        """解析实际请求的 endpoint。

        参数:
            product_id: 产品代码。
            region_id: 地域 ID。
            endpoint_rule: endpoint 生成规则。
            network: 网络类型。
            suffix: endpoint 后缀。
            endpoint_map: 地域到 endpoint 的映射表。
            endpoint: 显式指定的 endpoint，非空时优先使用。

        返回:
            最终使用的 endpoint 字符串。
        """
        if not UtilClient.empty(endpoint):
            return endpoint
        if not UtilClient.is_unset(endpoint_map) and not UtilClient.empty(
            endpoint_map.get(region_id)
        ):
            return endpoint_map.get(region_id)
        return EndpointUtilClient.get_endpoint_rules(
            product_id, region_id, endpoint_rule, network, suffix
        )

    def get_param(
        self,
        action: str,
        method: str = "POST",
        protocol: str = "HTTPS",
        pathname: str = "/",
        auth_type: str = "AK",
        body_type: str = "json",
        req_body_type: str = "formData",
        style: str = "RPC",
        version: str | None = None,
    ) -> Params:
        """构造一次 OpenAPI 调用所需的 `Params`。

        参数:
            action: OpenAPI 的 Action 名称，例如 `GetNode`。
            method: HTTP 方法，默认 `POST`。
            protocol: 请求协议，默认 `HTTPS`。
            pathname: 请求路径，默认 `/`。
            auth_type: 鉴权方式，默认 `AK`。
            body_type: 响应体类型，默认 `json`。
            req_body_type: 请求体类型，默认 `formData`。
            style: API 风格，默认 `RPC`。
            version: 本次调用使用的 API 版本号。为 `None` 时回退到
                `self.version`。某个 Action 只存在于单一版本时必须显式传入，
                否则会把请求发到不存在该 Action 的版本上。

        返回:
            组装好的 `Params` 对象，供 `call_api` 使用。
        """
        return Params(
            action=action,
            version=version or self.version,
            protocol=protocol,
            pathname=pathname,
            method=method,
            auth_type=auth_type,
            style=style,
            req_body_type=req_body_type,
            body_type=body_type,
        )

    def get_node(
        self,
        request: models_20200518.GetNodeRequest,
    ) -> dict[str, Any]:
        """查询单个节点详情（2020-05-18）。

        本方法按 2020-05-18 的字段（`NodeId`/`ProjectEnv`）拼装请求体，
        因此只接受 `alibabacloud_dataworks_public20200518` 的 `GetNodeRequest`
        （2024-05-18 的同名模型字段是 `id`/`project_id`，不兼容）。

        参数:
            request: `GetNodeRequest`，需指定 `node_id`，可选 `project_env`。

        返回:
            OpenAPI 调用返回的响应字典。
        """
        UtilClient.validate_model(request)
        body = {}
        if not UtilClient.is_unset(request.node_id):
            body["NodeId"] = request.node_id
        if not UtilClient.is_unset(request.project_env):
            body["ProjectEnv"] = request.project_env

        return self.call_api(
            self.get_param(action="GetNode", version=API_VERSION_2020),
            OpenApiRequest(body=OpenApiUtilClient.parse_to_map(body)),
            RuntimeOptions(),
        )

    def list_data_sources(
        self,
        request1: models_20240518.ListDataSourcesRequest,
    ) -> dict[str, Any]:
        """查询数据源列表（2024-05-18）。

        本方法会把请求收缩成 2024-05-18 的 `ListDataSourcesShrinkRequest`
        并读取只有该版本才有的 `types` 字段，因此只接受
        `alibabacloud_dataworks_public20240518` 的 `ListDataSourcesRequest`。

        参数:
            request1: `ListDataSourcesRequest`，用于按项目、类型等条件过滤。

        返回:
            OpenAPI 调用返回的响应字典。
        """
        UtilClient.validate_model(request1)
        request = models_20240518.ListDataSourcesShrinkRequest()
        OpenApiUtilClient.convert(request1, request)
        if not UtilClient.is_unset(request1.types):
            request.types_shrink = (
                OpenApiUtilClient.array_to_string_with_specified_style(
                    request1.types, "Types", "simple"
                )
            )
        query = OpenApiUtilClient.query(UtilClient.to_map(request))
        return self.call_api(
            self.get_param(
                action="ListDataSources", method="GET", version=API_VERSION_2024
            ),
            OpenApiRequest(query=OpenApiUtilClient.query(query)),
            RuntimeOptions(),
        )

    def create_node(
        self,
        request: models_20240518.CreateNodeRequest,
    ) -> dict[str, Any]:
        """创建节点（2024-05-18 独有）。

        参数:
            request: `CreateNodeRequest`，需指定 `project_id`、`spec` 等字段。

        返回:
            OpenAPI 调用返回的响应字典。
        """
        UtilClient.validate_model(request)
        body = {}
        if not UtilClient.is_unset(request.container_id):
            body["ContainerId"] = request.container_id
        if not UtilClient.is_unset(request.project_id):
            body["ProjectId"] = request.project_id
        if not UtilClient.is_unset(request.scene):
            body["Scene"] = request.scene
        if not UtilClient.is_unset(request.spec):
            body["Spec"] = request.spec
        return self.call_api(
            self.get_param(
                action="CreateNode", method="POST", version=API_VERSION_2024
            ),
            OpenApiRequest(body=OpenApiUtilClient.parse_to_map(body)),
            RuntimeOptions(),
        )

    def list_nodes(
        self,
        request: models_20200518.ListNodesRequest | models_20240518.ListNodesRequest,
    ) -> dict[str, Any]:
        """查询节点列表。

        请求模型直接序列化成 query，与版本无关，两个版本的 `ListNodesRequest`
        都可用；发出的 API 版本取 `Client(version=...)`，请与传入的模型版本保持一致。

        参数:
            request: `ListNodesRequest`，用于按项目等条件过滤。

        返回:
            OpenAPI 调用返回的响应字典。
        """
        UtilClient.validate_model(request)
        query = OpenApiUtilClient.query(UtilClient.to_map(request))
        return self.call_api(
            self.get_param(action="ListNodes", method="GET"),
            OpenApiRequest(query=OpenApiUtilClient.query(query)),
            RuntimeOptions(),
        )

    def update_node(
        self,
        request: models_20240518.UpdateNodeRequest,
    ) -> dict[str, Any]:
        """更新节点（2024-05-18 独有）。

        参数:
            request: `UpdateNodeRequest`，需指定 `id`、`project_id`、`spec`。

        返回:
            OpenAPI 调用返回的响应字典。
        """
        UtilClient.validate_model(request)
        body = {}
        if not UtilClient.is_unset(request.id):
            body["Id"] = request.id
        if not UtilClient.is_unset(request.project_id):
            body["ProjectId"] = request.project_id
        if not UtilClient.is_unset(request.spec):
            body["Spec"] = request.spec

        return self.call_api(
            self.get_param(
                action="UpdateNode", method="POST", version=API_VERSION_2024
            ),
            OpenApiRequest(body=OpenApiUtilClient.parse_to_map(body)),
            RuntimeOptions(),
        )

    def create_dijob(
        self,
        tmp_req: models_20240518.CreateDIJobRequest,
    ) -> dict[str, Any]:
        """创建数据集成任务（DI Job，2024-05-18）。

        本方法会把请求收缩成 2024-05-18 的 `CreateDIJobShrinkRequest`，因此只
        接受 `alibabacloud_dataworks_public20240518` 的 `CreateDIJobRequest`
        （2020-05-18 的同名模型有 `system_debug` 等该收缩模型没有的字段）。

        参数:
            tmp_req: `CreateDIJobRequest`，包含来源/目标数据源、任务与
                资源配置等字段（列表/对象字段会被收缩为字符串再发起请求）。

        返回:
            OpenAPI 调用返回的响应字典。
        """
        UtilClient.validate_model(tmp_req)
        request = models_20240518.CreateDIJobShrinkRequest()
        OpenApiUtilClient.convert(tmp_req, request)
        if not UtilClient.is_unset(tmp_req.destination_data_source_settings):
            request.destination_data_source_settings_shrink = (
                OpenApiUtilClient.array_to_string_with_specified_style(
                    tmp_req.destination_data_source_settings,
                    "DestinationDataSourceSettings",
                    "json",
                )
            )
        if not UtilClient.is_unset(tmp_req.job_settings):
            request.job_settings_shrink = (
                OpenApiUtilClient.array_to_string_with_specified_style(
                    tmp_req.job_settings, "JobSettings", "json"
                )
            )
        if not UtilClient.is_unset(tmp_req.resource_settings):
            request.resource_settings_shrink = (
                OpenApiUtilClient.array_to_string_with_specified_style(
                    tmp_req.resource_settings, "ResourceSettings", "json"
                )
            )
        if not UtilClient.is_unset(tmp_req.source_data_source_settings):
            request.source_data_source_settings_shrink = (
                OpenApiUtilClient.array_to_string_with_specified_style(
                    tmp_req.source_data_source_settings,
                    "SourceDataSourceSettings",
                    "json",
                )
            )
        if not UtilClient.is_unset(tmp_req.table_mappings):
            request.table_mappings_shrink = (
                OpenApiUtilClient.array_to_string_with_specified_style(
                    tmp_req.table_mappings, "TableMappings", "json"
                )
            )
        if not UtilClient.is_unset(tmp_req.transformation_rules):
            request.transformation_rules_shrink = (
                OpenApiUtilClient.array_to_string_with_specified_style(
                    tmp_req.transformation_rules, "TransformationRules", "json"
                )
            )
        query = {}
        if not UtilClient.is_unset(request.destination_data_source_type):
            query["DestinationDataSourceType"] = request.destination_data_source_type
        if not UtilClient.is_unset(request.job_name):
            query["JobName"] = request.job_name
        if not UtilClient.is_unset(request.job_type):
            query["JobType"] = request.job_type
        if not UtilClient.is_unset(request.migration_type):
            query["MigrationType"] = request.migration_type
        if not UtilClient.is_unset(request.name):
            query["Name"] = request.name
        if not UtilClient.is_unset(request.project_id):
            query["ProjectId"] = request.project_id
        if not UtilClient.is_unset(request.source_data_source_type):
            query["SourceDataSourceType"] = request.source_data_source_type
        body = {}
        if not UtilClient.is_unset(request.description):
            body["Description"] = request.description
        if not UtilClient.is_unset(request.destination_data_source_settings_shrink):
            body["DestinationDataSourceSettings"] = (
                request.destination_data_source_settings_shrink
            )
        if not UtilClient.is_unset(request.job_settings_shrink):
            body["JobSettings"] = request.job_settings_shrink
        if not UtilClient.is_unset(request.resource_settings_shrink):
            body["ResourceSettings"] = request.resource_settings_shrink
        if not UtilClient.is_unset(request.source_data_source_settings_shrink):
            body["SourceDataSourceSettings"] = (
                request.source_data_source_settings_shrink
            )
        if not UtilClient.is_unset(request.table_mappings_shrink):
            body["TableMappings"] = request.table_mappings_shrink
        if not UtilClient.is_unset(request.transformation_rules_shrink):
            body["TransformationRules"] = request.transformation_rules_shrink
        return self.call_api(
            self.get_param(
                action="CreateDIJob", method="POST", version=API_VERSION_2024
            ),
            OpenApiRequest(
                query=OpenApiUtilClient.query(query),
                body=OpenApiUtilClient.parse_to_map(body),
            ),
            RuntimeOptions(),
        )

    def create_disync(
        self,
        request: models_20200518.CreateDISyncTaskRequest,
    ) -> dict[str, Any]:
        """创建数据同步任务（DISync Task，2020-05-18 独有）。

        `TaskContent` 是任务的完整 JSON 定义，必须放在请求体里；其余字段放
        query。

        参数:
            request: `CreateDISyncTaskRequest`，需指定 `project_id`、
                `task_name`、`task_content` 等字段。

        返回:
            OpenAPI 调用返回的响应字典。
        """
        UtilClient.validate_model(request)
        query = {}
        if not UtilClient.is_unset(request.client_token):
            query["ClientToken"] = request.client_token
        if not UtilClient.is_unset(request.project_id):
            query["ProjectId"] = request.project_id
        if not UtilClient.is_unset(request.task_name):
            query["TaskName"] = request.task_name
        if not UtilClient.is_unset(request.task_param):
            query["TaskParam"] = request.task_param
        if not UtilClient.is_unset(request.task_type):
            query["TaskType"] = request.task_type
        body = {}
        if not UtilClient.is_unset(request.task_content):
            body["TaskContent"] = request.task_content

        return self.call_api(
            self.get_param(
                action="CreateDISyncTask", method="POST", version=API_VERSION_2020
            ),
            OpenApiRequest(
                query=OpenApiUtilClient.query(query),
                body=OpenApiUtilClient.parse_to_map(body),
            ),
            RuntimeOptions(),
        )

    def list_folders(
        self,
        request: models_20200518.ListFoldersRequest
        | models_20240518.ListFoldersRequest,
    ) -> dict[str, Any]:
        """查询目录（文件夹）列表。

        两个版本的 `ListFolders` 请求字段与拼装方式完全一致，所以两个版本的
        `ListFoldersRequest` 都可用；发出的 API 版本取 `Client(version=...)`。

        参数:
            request: `ListFoldersRequest`，可指定分页、父目录路径、
                项目 ID/标识等过滤条件。

        返回:
            OpenAPI 调用返回的响应字典。
        """
        UtilClient.validate_model(request)
        body = {}
        if not UtilClient.is_unset(request.page_number):
            body["PageNumber"] = request.page_number
        if not UtilClient.is_unset(request.page_size):
            body["PageSize"] = request.page_size
        if not UtilClient.is_unset(request.parent_folder_path):
            body["ParentFolderPath"] = request.parent_folder_path
        if not UtilClient.is_unset(request.project_id):
            body["ProjectId"] = request.project_id
        if not UtilClient.is_unset(request.project_identifier):
            body["ProjectIdentifier"] = request.project_identifier
        return self.call_api(
            self.get_param(action="ListFolders", method="POST"),
            OpenApiRequest(body=OpenApiUtilClient.parse_to_map(body)),
            RuntimeOptions(),
        )

    def create_pipeline_run(
        self,
        tmp_req: models_20240518.CreatePipelineRunRequest,
    ) -> dict[str, Any]:
        """创建工作流实例（Pipeline Run，2024-05-18 独有）。

        参数:
            tmp_req: `CreatePipelineRunRequest`，需指定 `project_id`、
                `type`，可选 `object_ids`、`description`。

        返回:
            OpenAPI 调用返回的响应字典。
        """
        UtilClient.validate_model(tmp_req)
        request = models_20240518.CreatePipelineRunShrinkRequest()
        OpenApiUtilClient.convert(tmp_req, request)
        if not UtilClient.is_unset(tmp_req.object_ids):
            request.object_ids_shrink = (
                OpenApiUtilClient.array_to_string_with_specified_style(
                    tmp_req.object_ids, "ObjectIds", "json"
                )
            )
        body = {}
        if not UtilClient.is_unset(request.description):
            body["Description"] = request.description
        if not UtilClient.is_unset(request.object_ids_shrink):
            body["ObjectIds"] = request.object_ids_shrink
        if not UtilClient.is_unset(request.project_id):
            body["ProjectId"] = request.project_id
        if not UtilClient.is_unset(request.type):
            body["Type"] = request.type

        return self.call_api(
            self.get_param(
                action="CreatePipelineRun", method="POST", version=API_VERSION_2024
            ),
            OpenApiRequest(body=OpenApiUtilClient.parse_to_map(body)),
            RuntimeOptions(),
        )

    def get_pipeline_run(
        self,
        request: models_20240518.GetPipelineRunRequest,
    ) -> dict[str, Any]:
        """查询工作流实例（Pipeline Run）详情（2024-05-18 独有）。

        参数:
            request: `GetPipelineRunRequest`，需指定 `project_id` 与 `id`。

        返回:
            OpenAPI 调用返回的响应字典。
        """
        UtilClient.validate_model(request)
        query = OpenApiUtilClient.query(UtilClient.to_map(request))
        return self.call_api(
            self.get_param(
                action="GetPipelineRun", method="GET", version=API_VERSION_2024
            ),
            OpenApiRequest(query=OpenApiUtilClient.query(query)),
            RuntimeOptions(),
        )

    def exec_pipeline_run_stage_with_options(
        self,
        request: models_20240518.ExecPipelineRunStageRequest,
    ) -> dict[str, Any]:
        """推进工作流实例的某个阶段（stage）执行（2024-05-18 独有）。

        参数:
            request: `ExecPipelineRunStageRequest`，需指定 `project_id`、
                `id`，可选 `code`。

        返回:
            OpenAPI 调用返回的响应字典。
        """
        UtilClient.validate_model(request)
        query = {}
        if not UtilClient.is_unset(request.project_id):
            query["ProjectId"] = request.project_id
        body = {}
        if not UtilClient.is_unset(request.code):
            body["Code"] = request.code
        if not UtilClient.is_unset(request.id):
            body["Id"] = request.id

        return self.call_api(
            self.get_param(
                action="ExecPipelineRunStage", method="POST", version=API_VERSION_2024
            ),
            OpenApiRequest(
                query=OpenApiUtilClient.query(query),
                body=OpenApiUtilClient.parse_to_map(body),
            ),
            RuntimeOptions(),
        )
