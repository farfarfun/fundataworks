from typing import Union, Dict, Any

from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util.client import Client as UtilClient
from alibabacloud_dataworks_public20200518 import models as models_20200518
from alibabacloud_dataworks_public20240518 import models as models_20240518
from alibabacloud_openapi_util.client import Client as OpenApiUtilClient
from alibabacloud_tea_openapi.client import Client as OpenApiClient
from alibabacloud_endpoint_util.client import Client as EndpointUtilClient
from alibabacloud_tea_openapi.models import OpenApiRequest, Params
from alibabacloud_tea_util.models import RuntimeOptions


class Client(OpenApiClient):
    def __init__(self, config: open_api_models.Config, version="2020-05-18"):
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
        endpoint_map: Dict[str, str],
        endpoint: str,
    ) -> str:
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
    ) -> Params:
        return Params(
            action=action,
            version=self.version,
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
        request: Union[
            models_20200518.GetNodeRequest,
            models_20240518.GetNodeRequest,
        ],
    ) -> Dict[str, Any]:
        request.validate()
        body = {}
        if request.node_id is not None:
            body["NodeId"] = request.node_id
        if request.project_env is not None:
            body["ProjectEnv"] = request.project_env

        return self.call_api(
            self.get_param(action="GetNode"),
            OpenApiRequest(body=OpenApiUtilClient.parse_to_map(body)),
            RuntimeOptions(),
        )

    def list_data_sources(
        self,
        request1: Union[
            models_20200518.ListDataSourcesRequest,
            models_20240518.ListDataSourcesRequest,
        ],
    ):
        request1.validate()
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
            self.get_param(action="ListDataSources", method="GET"),
            OpenApiRequest(query=OpenApiUtilClient.query(query)),
            RuntimeOptions(),
        )

    def create_node(
        self,
        request: Union[
            models_20200518.CreateNodeRequest, models_20240518.CreateNodeRequest
        ],
    ) -> Dict[str, Any]:
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
            self.get_param(action="CreateNode", method="POST"),
            OpenApiRequest(body=OpenApiUtilClient.parse_to_map(body)),
            RuntimeOptions(),
        )

    def list_nodes(
        self,
        request: Union[
            models_20200518.ListNodesRequest, models_20240518.ListNodesRequest
        ],
    ) -> Dict[str, Any]:
        UtilClient.validate_model(request)
        query = OpenApiUtilClient.query(UtilClient.to_map(request))
        return self.call_api(
            self.get_param(action="ListNodes", method="GET"),
            OpenApiRequest(query=OpenApiUtilClient.query(query)),
            RuntimeOptions(),
        )

    def update_node(
        self,
        request: Union[
            models_20200518.UpdateNodeRequest, models_20240518.UpdateNodeRequest
        ],
    ) -> Dict[str, Any]:
        UtilClient.validate_model(request)
        body = {}
        if not UtilClient.is_unset(request.id):
            body["Id"] = request.id
        if not UtilClient.is_unset(request.project_id):
            body["ProjectId"] = request.project_id
        if not UtilClient.is_unset(request.spec):
            body["Spec"] = request.spec

        return self.call_api(
            self.get_param(action="UpdateNode", method="POST"),
            OpenApiRequest(body=OpenApiUtilClient.parse_to_map(body)),
            RuntimeOptions(),
        )

    def create_dijob(
        self,
        tmp_req: Union[
            models_20200518.CreateDIJobRequest, models_20240518.CreateDIJobRequest
        ],
    ) -> Dict[str, Any]:
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
        query = OpenApiUtilClient.query(UtilClient.to_map(request))
        return self.call_api(
            self.get_param(action="CreateDIJob", method="GET"),
            OpenApiRequest(query=OpenApiUtilClient.query(query)),
            RuntimeOptions(),
        )

    def create_disync(
        self,
        request: Union[
            models_20200518.CreateDISyncTaskRequest,
            models_20240518.CreateDISyncTaskRequest,
        ],
    ) -> Dict[str, Any]:
        UtilClient.validate_model(request)
        query = {}
        if not UtilClient.is_unset(request.client_token):
            query["ClientToken"] = request.client_token
        if not UtilClient.is_unset(request.project_id):
            query["ProjectId"] = request.project_id
        if not UtilClient.is_unset(request.task_content):
            query["TaskContent"] = request.task_content
        if not UtilClient.is_unset(request.task_name):
            query["TaskName"] = request.task_name
        if not UtilClient.is_unset(request.task_param):
            query["TaskParam"] = request.task_param
        if not UtilClient.is_unset(request.task_type):
            query["TaskType"] = request.task_type

        return self.call_api(
            self.get_param(action="CreateDISyncTask", method="POST"),
            OpenApiRequest(query=OpenApiUtilClient.query(query)),
            RuntimeOptions(),
        )

    def list_folders(
        self,
        request: Union[
            models_20200518.ListFoldersRequest,
            models_20240518.ListFoldersRequest,
        ],
    ) -> Dict[str, Any]:
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
        tmp_req: Union[
            models_20200518.CreatePipelineRunRequest,
            models_20240518.CreatePipelineRunRequest,
        ],
    ) -> Dict[str, Any]:
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
            self.get_param(action="CreatePipelineRun", method="POST"),
            OpenApiRequest(body=OpenApiUtilClient.parse_to_map(body)),
            RuntimeOptions(),
        )

    def get_pipeline_run(
        self,
        request: Union[
            models_20200518.CreatePipelineRunRequest,
            models_20240518.CreatePipelineRunRequest,
        ],
    ) -> Dict[str, Any]:
        UtilClient.validate_model(request)
        query = OpenApiUtilClient.query(UtilClient.to_map(request))
        return self.call_api(
            self.get_param(action="GetPipelineRun", method="GET"),
            OpenApiRequest(query=OpenApiUtilClient.query(query)),
            RuntimeOptions(),
        )

    def exec_pipeline_run_stage_with_options(
        self,
        request: Union[
            models_20200518.ExecPipelineRunStageRequest,
            models_20240518.ExecPipelineRunStageRequest,
        ],
    ) -> Dict[str, Any]:
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
            self.get_param(action="ExecPipelineRunStage", method="POST"),
            OpenApiRequest(
                query=OpenApiUtilClient.query(query),
                body=OpenApiUtilClient.parse_to_map(body),
            ),
            RuntimeOptions(),
        )
