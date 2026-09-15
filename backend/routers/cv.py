import tempfile
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.services.cv_parser import CVParser
from backend.models.schemas import ParsedCV

router = APIRouter(prefix="/cv", tags=["CV"])
_parser = None


def get_parser() -> CVParser:
    global _parser
    if _parser is None:
        _parser = CVParser()
    return _parser


@router.post("/upload", response_model=ParsedCV)
async def upload_cv(file: UploadFile = File(...)):
    allowed = {".pdf", ".docx", ".txt"}
    suffix = Path(file.filename).suffix.lower()
    if suffix not in allowed:
        raise HTTPException(400, f"Formato no soportado: {suffix}. Usa PDF, DOCX o TXT")

    try:
        content = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        parser = get_parser()
        result = parser.parse(tmp_path)
        Path(tmp_path).unlink(missing_ok=True)
        return result
    except Exception as e:
        raise HTTPException(500, f"Error al parsear CV: {str(e)}")
