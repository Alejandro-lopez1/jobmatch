from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.sheets_service import SheetsService
from backend.models.schemas import MatchResult

router = APIRouter(prefix="/sheets", tags=["Sheets"])
_service = SheetsService()


class ExportRequest(BaseModel):
    results: list[dict]
    sheet_name: str | None = None


class ExportCSVRequest(BaseModel):
    results: list[dict]
    filepath: str = "jobmatch_results.csv"


@router.post("/export")
async def export_to_sheets(request: ExportRequest):
    try:
        match_results = [MatchResult(**r) for r in request.results]
        url = _service.append_results(match_results, request.sheet_name)
        return {"status": "ok", "url": url}
    except FileNotFoundError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Error exportando: {str(e)}")


@router.post("/export-csv")
async def export_to_csv(request: ExportCSVRequest):
    try:
        match_results = [MatchResult(**r) for r in request.results]
        filepath = _service.export_to_csv(match_results, request.filepath)
        return {"status": "ok", "filepath": filepath}
    except Exception as e:
        raise HTTPException(500, f"Error exportando CSV: {str(e)}")


@router.get("/status")
async def sheets_status():
    connected = _service.connect()
    return {"connected": connected}
