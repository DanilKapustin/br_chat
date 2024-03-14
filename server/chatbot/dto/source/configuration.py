from typing import Optional

from pydantic import BaseModel


class SourceConfiguration(BaseModel):
    """Base source configuration"""

    def dict(self, *args, **kwargs):
        """Get dictionary representation"""
        result: dict = super().dict(*args, **kwargs)

        for k, v in result.items():
            result[k] = str(v)

        return result


class ConfluenceConfiguration(SourceConfiguration):
    """Confluence configuration"""

    url: str
    username: str
    password: str
    is_cloud: Optional[bool] = False
    space_key: str


class JiraConfiguration(SourceConfiguration):
    """Jira configuration"""

    url: str
    username: str
    password: str
    is_cloud: Optional[bool] = False
    search_query: str
