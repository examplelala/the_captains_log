from pathlib import Path
from fastapi import APIRouter,HTTPException, status
from starlette.responses import HTMLResponse, FileResponse
router = APIRouter()
FRONTEND_PATH=Path(__file__).parent.parent.joinpath("resource/index.html").resolve()

def safe_file_response(path: Path) -> FileResponse:
    if not path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {path.name}"
        )
    return FileResponse(path, media_type="text/html")


@router.get("/index.html", response_class=HTMLResponse, include_in_schema=False)
async def index():  
    return safe_file_response(FRONTEND_PATH)

