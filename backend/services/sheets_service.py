from datetime import datetime
from pathlib import Path

import gspread

from backend.config import GOOGLE_SERVICE_ACCOUNT_PATH, GOOGLE_SHEET_NAME
from backend.models.schemas import MatchResult


class SheetsService:
    def __init__(self):
        self._client = None

    def _get_client(self) -> gspread.Client:
        if self._client is None:
            sa_path = Path(GOOGLE_SERVICE_ACCOUNT_PATH)
            if not sa_path.exists():
                raise FileNotFoundError(
                    f"Service account no encontrado: {sa_path}\n"
                    "Descarga el JSON de Google Cloud Console y guárdalo como service_account.json"
                )
            self._client = gspread.service_account(filename=str(sa_path))
        return self._client

    def connect(self) -> bool:
        try:
            self._get_client()
            return True
        except Exception as e:
            print(f"[Sheets] Error de conexión: {e}")
            return False

    def get_or_create_sheet(self, sheet_name: str = None) -> gspread.Worksheet:
        name = sheet_name or GOOGLE_SHEET_NAME
        client = self._get_client()
        try:
            spreadsheet = client.open(name)
            worksheet = spreadsheet.sheet1
        except gspread.SpreadsheetNotFound:
            spreadsheet = client.create(name)
            worksheet = spreadsheet.sheet1
            worksheet.update(
                "A1:I1",
                [[
                    "Fecha", "Empresa", "Puesto", "Match%",
                    "Clasificación", "Skills Faltantes", "URL",
                    "Fuente", "Estado"
                ]]
            )
            worksheet.format("A1:I1", {"textFormat": {"bold": True}})
        return worksheet

    def append_results(self, results: list[MatchResult], sheet_name: str = None) -> str:
        worksheet = self.get_or_create_sheet(sheet_name)
        rows = []
        for r in results:
            job = r.job
            rows.append([
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                job.company if job else "",
                job.title if job else "",
                f'{r.scores.get("total", 0) * 100:.1f}%',
                r.classification.upper(),
                ", ".join(r.missing_skills[:5]),
                job.url if job else "",
                job.source if job else "",
                "Pendiente",
            ])
        worksheet.append_rows(rows)
        return worksheet.spreadsheet.url

    def export_to_csv(self, results: list[MatchResult], filepath: str) -> str:
        import csv
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Fecha", "Empresa", "Puesto", "Match%",
                "Clasificación", "Skills Faltantes", "URL", "Fuente"
            ])
            for r in results:
                job = r.job
                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                    job.company if job else "",
                    job.title if job else "",
                    f'{r.scores.get("total", 0) * 100:.1f}%',
                    r.classification.upper(),
                    ", ".join(r.missing_skills[:5]),
                    job.url if job else "",
                    job.source if job else "",
                ])
        return filepath
