from fastapi import APIRouter

router = APIRouter(prefix="/paths", tags=["paths"])

PATHS_DATA = [
    {
        "slug": "python-ai",
        "title": "Python & AI",
        "subtitle": "Python fundamentals, DS & ML projects, deployment."
    },
    {
        "slug": "fullstack",
        "title": "Full-Stack Web (React + Node)",
        "subtitle": "Frontend, backend, APIs, auth, prod deploy."
    },
    {
        "slug": "aws-devops",
        "title": "AWS / DevOps",
        "subtitle": "Cloud basics, IaC, Docker, CI/CD, monitoring."
    },
    {
        "slug": "cybersec",
        "title": "Cybersecurity",
        "subtitle": "Threats, OWASP, labs, tools, blue/red basics."
    },
    {
        "slug": "flutter",
        "title": "Flutter (Mobile)",
        "subtitle": "Dart, UI patterns, state mgmt, store & publish."
    }
]

@router.get("/list")
def list_paths():
    """Return list of all career paths"""
    return PATHS_DATA

@router.get("/{slug}")
def get_path(slug: str):
    """Get a specific path by slug"""
    for path in PATHS_DATA:
        if path["slug"] == slug:
            return path
    return {"detail": "Path not found"}
