from pydantic import BaseModel

class CourseItem(BaseModel):
    id: str
    path: str          # e.g., "python-ai"
    title: str
    youtubeId: str
    duration: str | None = None
