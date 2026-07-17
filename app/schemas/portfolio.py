from pydantic import BaseModel, ConfigDict


class ContentItem(BaseModel):
    model_config = ConfigDict(extra="allow")
