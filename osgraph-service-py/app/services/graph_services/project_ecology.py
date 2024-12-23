import os
from datetime import datetime, timedelta
from typing import Any, Dict

from dotenv import load_dotenv

from app.dal.search.es import ElasticsearchClient
from app.services.graph_services.base import BaseService, FilterKey, ServiceConfig

load_dotenv()


def get_default_start_time() -> int:
    return int((datetime.now() - timedelta(days=30)).timestamp() * 1000)


def get_default_end_time() -> int:
    return int(datetime.now().timestamp() * 1000)


class ProjectEcologyServiceConfig(ServiceConfig):
    def __init__(self):
        super().__init__(
            name="项目生态",
            comment="这是一个获取项目项目生态的图谱",
            inputTypes=["GitHubRepo"],
            filterKeys=[
                FilterKey(key="topn", type="int", default=50, required=False),
            ],
        )


class ProjectEcologyService(BaseService):
    def __init__(self):
        super().__init__(ProjectEcologyServiceConfig())

    def execute(self, data: Dict[str, Any]) -> Any:
        validated_data = self.validate_params(data)
        github_repo: str = validated_data["GitHubRepo"]
        top_n: int = validated_data["topn"]
        es = ElasticsearchClient()
        query = {"match": {"name": github_repo}}
        res = es.search(index="github_repo", query=query, size=1)
        if len(res):
            repo_id = res[0]["id"]
            cypher = (
                f"CALL osgraph.get_repo_by_repo('{{"
                f'"repo_id":{repo_id}, "top_n":{top_n}'
                f"}}') YIELD start_node, relationship, end_node "
                "return start_node, relationship, end_node"
            )
            result = self.graphClient.run(cypher)
            return result
