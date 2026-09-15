import json
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import typer

from backend.services.cv_parser import CVParser
from backend.services.job_scraper import JobSearchService
from backend.services.matcher import MatchService
from backend.services.sheets_service import SheetsService
from backend.config import DATA_DIR

app = typer.Typer(name="jobmatch", help="JobMatch - Buscador de empleo con matching inteligente")
cv_app = typer.Typer(help="Gestionar CV")
app.add_typer(cv_app, name="cv")

_parser = None
_scraper = JobSearchService()
_matcher = MatchService()
_sheets = SheetsService()


def get_parser():
    global _parser
    if _parser is None:
        _parser = CVParser()
    return _parser


COLORS = {
    "bueno": "\033[92m",
    "regular": "\033[93m",
    "no_match": "\033[91m",
    "reset": "\033[0m",
    "bold": "\033[1m",
}


@app.command()
def search(
    query: str = typer.Argument(help="Palabra clave de búsqueda"),
    location: str = typer.Option("", "--location", "-l", help="Ubicación"),
    results: int = typer.Option(20, "--results", "-n", help="Número de resultados"),
    cv_path: str = typer.Option(None, "--cv", "-c", help="Ruta al CV (PDF/DOCX)"),
):
    """Buscar empleos y calcular match con tu CV"""
    cv_file = Path(cv_path) if cv_path else DATA_DIR / "current_cv.json"

    if not cv_file.exists():
        typer.echo("❌ No hay CV cargado. Usa: jobmatch cv upload <archivo>", err=True)
        raise typer.Exit(1)

    typer.echo(f"\n🔍 Buscando: '{query}' en '{location or 'todas las ubicaciones'}'...\n")

    from backend.models.schemas import ParsedCV
    cv_data = json.loads(cv_file.read_text(encoding="utf-8"))
    cv = ParsedCV(**cv_data)

    jobs = _scraper.search_all(query, location, results)
    typer.echo(f"   📥 {len(jobs)} ofertas encontradas")

    if not jobs:
        typer.echo("No se encontraron resultados.")
        raise typer.Exit(0)

    ranked = _matcher.rank_jobs(cv, jobs)

    typer.echo(f"\n{'─' * 80}")
    typer.echo(f" {'#':>3} │ {'Match':>7} │ {'Empresa':<20} │ {'Puesto':<25} │ Clasificación")
    typer.echo(f"{'─' * 80}")

    for i, result in enumerate(ranked[:10], 1):
        job = result.job
        score = result.scores.get("total", 0) * 100
        cls = result.classification
        color = COLORS.get(cls, "")
        reset = COLORS["reset"]

        typer.echo(
            f" {i:>3} │ {color}{score:>5.1f}%{reset} │ "
            f"{job.company[:20]:<20} │ {job.title[:25]:<25} │ {color}{cls.upper()}{reset}"
        )

    typer.echo(f"{'─' * 80}")

    if ranked:
        best = ranked[0]
        typer.echo(f"\n📋 Mejor match: {best.job.title} @ {best.job.company} ({best.scores['total']*100:.1f}%)")
        if best.missing_skills:
            typer.echo(f"   Skills faltantes: {', '.join(best.missing_skills[:5])}")

    DATA_DIR.mkdir(exist_ok=True)
    (DATA_DIR / "last_results.json").write_text(
        json.dumps([r.dict() for r in ranked], default=str, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    typer.echo("\n💾 Resultados guardados en data/last_results.json")


@cv_app.command("upload")
def cv_upload(file: str = typer.Argument(..., help="Ruta al archivo CV (PDF/DOCX/TXT)")):
    """Subir y parsear un CV"""
    path = Path(file)
    if not path.exists():
        typer.echo(f"❌ Archivo no encontrado: {file}", err=True)
        raise typer.Exit(1)

    typer.echo(f"📄 Parseando CV: {path.name}...")
    parser = get_parser()
    cv = parser.parse(str(path))

    typer.echo(f"\n{COLORS['bold']}✅ CV parseado correctamente{COLORS['reset']}")
    typer.echo(f"   Nombre: {cv.personal_info.name or 'No detectado'}")
    typer.echo(f"   Email: {cv.personal_info.email or 'No detectado'}")
    typer.echo(f"   Skills: {', '.join(cv.skills.technical) or 'No detectados'}")
    typer.echo(f"   Experiencia: {cv.experience.total_years} años")
    typer.echo(f"   Educación: {len(cv.education)} títulos encontrados")

    DATA_DIR.mkdir(exist_ok=True)
    out_path = DATA_DIR / "current_cv.json"
    import json
    out_path.write_text(json.dumps(cv.model_dump(), indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    typer.echo(f"\n💾 Guardado en: {out_path}")


@cv_app.command("show")
def cv_show():
    """Mostrar el CV actual"""
    cv_file = DATA_DIR / "current_cv.json"
    if not cv_file.exists():
        typer.echo("❌ No hay CV cargado. Usa: jobmatch cv upload <archivo>", err=True)
        raise typer.Exit(1)

    from backend.models.schemas import ParsedCV
    cv_data = json.loads(cv_file.read_text(encoding="utf-8"))
    cv = ParsedCV(**cv_data)

    typer.echo(f"\n{COLORS['bold']}👤 CV Actual{COLORS['reset']}")
    typer.echo(f"   Nombre: {cv.personal_info.name or 'N/A'}")
    typer.echo(f"   Email: {cv.personal_info.email or 'N/A'}")
    typer.echo(f"   Teléfono: {cv.personal_info.phone or 'N/A'}")
    typer.echo(f"\n{COLORS['bold']}🛠️  Skills:{COLORS['reset']}")
    for skill in cv.skills.technical:
        typer.echo(f"   • {skill}")
    typer.echo(f"\n{COLORS['bold']}💼 Experiencia:{COLORS['reset']}")
    typer.echo(f"   {cv.experience.total_years} años totales")


@app.command()
def export(
    to_sheets: bool = typer.Option(False, "--to-sheets", help="Exportar a Google Sheets"),
    to_csv: str = typer.Option(None, "--to-csv", help="Exportar a archivo CSV"),
):
    """Exportar resultados de la última búsqueda"""
    results_file = DATA_DIR / "last_results.json"
    if not results_file.exists():
        typer.echo("❌ No hay resultados. Ejecuta: jobmatch search <query>", err=True)
        raise typer.Exit(1)

    from backend.models.schemas import MatchResult
    data = json.loads(results_file.read_text(encoding="utf-8"))
    results = [MatchResult(**r) for r in data]

    if to_sheets:
        typer.echo("📤 Exportando a Google Sheets...")
        try:
            url = _sheets.append_results(results)
            typer.echo(f"✅ Exportado: {url}")
        except Exception as e:
            typer.echo(f"❌ Error: {e}", err=True)
            raise typer.Exit(1)

    if to_csv:
        typer.echo(f"📤 Exportando a {to_csv}...")
        filepath = _sheets.export_to_csv(results, to_csv)
        typer.echo(f"✅ Exportado: {filepath}")


@app.command()
def server(
    host: str = typer.Option("127.0.0.1", help="Host"),
    port: int = typer.Option(8000, help="Puerto"),
):
    """Iniciar el servidor web API"""
    import uvicorn
    typer.echo(f"🚀 Iniciando servidor en http://{host}:{port}")
    typer.echo(f"📖 Docs: http://{host}:{port}/docs")
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    app()
