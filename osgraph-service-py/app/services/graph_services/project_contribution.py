import os
from datetime import datetime, timedelta
from typing import Any, Dict

from dotenv import load_dotenv

from app.dal.graph.tugraph import GraphClient
from app.dal.search.es import ElasticsearchClient
from app.services.graph_services.base import BaseService, FilterKey, ServiceConfig

load_dotenv()


def get_default_start_time() -> int:
    return int((datetime.now() - timedelta(days=30)).timestamp() * 1000)


def get_default_end_time() -> int:
    return int(datetime.now().timestamp() * 1000)


class ProjectContributionServiceConfig(ServiceConfig):
    def __init__(self):
        super().__init__(
            name="项目贡献",
            comment="这是一个获取项目贡献的图谱",
            inputTypes=["GitHubRepo"],
            filterKeys=[
                FilterKey(
                    key="start-time",
                    type="int",
                    default=get_default_start_time(),
                    required=False,
                ),
                FilterKey(
                    key="end-time",
                    type="int",
                    default=get_default_end_time(),
                    required=False,
                ),
                FilterKey(
                    key="contribution-limit", type="int", default=50, required=False
                ),
            ],
        )


class ProjectContributionService(BaseService):
    def __init__(self):
        super().__init__(ProjectContributionServiceConfig())

    def execute(self, data: Dict[str, Any]) -> Any:
        validated_data = self.validate_params(data)
        github_repo: str = validated_data["GitHubRepo"]
        start_time: int = validated_data["start-time"] or get_default_start_time()
        end_time: int = validated_data["end-time"] or get_default_end_time()
        config_name = os.getenv("FLASK_CONFIG")
        # if config_name == 'development':
        #     start_time = 0
        start_time = 0
        contribution_limit: int = validated_data["contribution-limit"]
        es = ElasticsearchClient()
        query = {"term": {"name.keyword": github_repo}}
        res = es.search(index="github_repo", query=query)
        if len(res):
            repo_id = res[0]["id"]
            graph_name = os.getenv("TUGRAPHDB_OSGRAPH_GITHUB_GRAPH_NAME")
            client = GraphClient(graph_name)
            cypher = f"""CALL osgraph.get_repo_contribution('{{"repo_id":{repo_id},"start_timestamp":{start_time},"end_timestamp":{end_time},"top_n":{contribution_limit}}}') YIELD start_node, relationship, end_node return start_node, relationship, end_node"""
            result = client.run(cypher)
            return result