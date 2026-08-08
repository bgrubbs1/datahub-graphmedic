from __future__ import annotations

import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .adapters import DataHubMCPAdapter, FixtureAdapter
from .service import GraphMedicService


STATIC = Path(__file__).with_name("static")


class ApplyRequest(BaseModel):
    finding_id: str
    action_kind: str
    approved: bool


def create_app(mode: str | None = None, audit_path: Path | None = None) -> FastAPI:
    selected = mode or os.environ.get("GRAPHMEDIC_MODE", "mcp")
    adapter = FixtureAdapter() if selected == "fixture" else DataHubMCPAdapter()
    service = GraphMedicService(adapter, audit_path or Path("runtime/audit.jsonl"))
    app = FastAPI(title="GraphMedic", version="0.1.0")

    @app.get("/")
    async def index() -> FileResponse:
        return FileResponse(STATIC / "index.html")

    @app.get("/app.js")
    async def javascript() -> FileResponse:
        return FileResponse(STATIC / "app.js", media_type="application/javascript")

    @app.get("/style.css")
    async def stylesheet() -> FileResponse:
        return FileResponse(STATIC / "style.css", media_type="text/css")

    @app.get("/health")
    async def health() -> dict[str, object]:
        return {"status": "ok", "mode": selected, "synthetic_data_only": True}

    @app.post("/api/scan")
    async def scan() -> dict[str, object]:
        try:
            return (await service.scan()).to_dict()
        except Exception as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    @app.post("/api/apply")
    async def apply(request: ApplyRequest) -> dict[str, object]:
        try:
            return await service.apply(request.finding_id, request.action_kind, request.approved)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except KeyError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    @app.get("/api/audit")
    async def audit() -> list[dict[str, object]]:
        return service.audit()

    return app


app = create_app()


def main() -> None:
    uvicorn.run("graphmedic.app:app", host="127.0.0.1", port=8765, reload=False)
