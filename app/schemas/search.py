from pydantic import BaseModel


class SearchResultOut(BaseModel):
    kind: str
    title: str
    path: str
    subtitle: str
    excerpt: str | None = None
    image_url: str | None = None


class SearchResponseOut(BaseModel):
    query: str
    recommended: list[SearchResultOut]
    results: list[SearchResultOut]
    total: int
