"""Servidor FastAPI para dashboard interativo do CodeHealthAnalyzer."""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from ..analyzers.violations import ViolationsAnalyzer
from ..analyzers.templates import TemplatesAnalyzer
from ..analyzers.errors import ErrorsAnalyzer
from ..reports.generator import ReportGenerator


class DashboardServer:
    """Servidor do dashboard interativo."""
    
    def __init__(self, project_path: str = "."):
        self.app = FastAPI(
            title="CodeHealthAnalyzer Dashboard",
            description="Dashboard interativo para análise de qualidade de código",
            version="1.0.0"
        )
        self.project_path = Path(project_path)
        self.connected_clients: List[WebSocket] = []
        
        # Configurar arquivos estáticos e templates
        web_dir = Path(__file__).parent
        self.app.mount("/static", StaticFiles(directory=web_dir / "static"), name="static")
        self.templates = Jinja2Templates(directory=web_dir / "templates")
        
        # Configurar rotas
        self._setup_routes()
        
        # Inicializar analisadores
        self.violations_analyzer = ViolationsAnalyzer(str(self.project_path))
        self.templates_analyzer = TemplatesAnalyzer(str(self.project_path))
        self.errors_analyzer = ErrorsAnalyzer(str(self.project_path))
        self.report_generator = ReportGenerator()
    
    def _setup_routes(self):
        """Configura as rotas da aplicação."""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard(request: Request):
            """Página principal do dashboard."""
            return self.templates.TemplateResponse(
                "dashboard.html", 
                {"request": request, "project_path": str(self.project_path)}
            )
        
        @self.app.get("/api/metrics")
        async def get_metrics():
            """Retorna métricas atuais do projeto."""
            return await self._get_current_metrics()
        
        @self.app.get("/api/violations")
        async def get_violations():
            """Retorna violações detectadas."""
            violations = self.violations_analyzer.analyze()
            return violations
        
        @self.app.get("/api/templates")
        async def get_templates():
            """Retorna análise de templates."""
            templates = self.templates_analyzer.analyze()
            return templates
        
        @self.app.get("/api/errors")
        async def get_errors():
            """Retorna erros de linting."""
            errors = self.errors_analyzer.analyze()
            return errors
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket para atualizações em tempo real."""
            await self._handle_websocket(websocket)
    
    async def _get_current_metrics(self) -> Dict:
        """Obtém métricas atuais do projeto."""
        try:
            # Executar análises
            violations = self.violations_analyzer.analyze()
            templates = self.templates_analyzer.analyze()
            errors = self.errors_analyzer.analyze()
            
            # Gerar relatório consolidado
            report = self.report_generator.generate_full_report(
                violations=violations,
                templates=templates,
                errors=errors
            )
            
            # Extrair métricas principais a partir dos esquemas atuais
            vio_stats = violations.get("statistics", {})
            err_meta = errors.get("metadata", {})
            templates_list = templates.get("templates", [])

            # Combina arquivos com problemas (violations + warnings) e ordena
            files_items = (violations.get("violations", []) or []) + (violations.get("warnings", []) or [])
            def _prio_weight(p: str) -> int:
                return {"high": 3, "medium": 2, "low": 1}.get((p or "low").lower(), 0)
            files_items.sort(key=lambda it: (_prio_weight(it.get("priority")), len(it.get("violations", []))), reverse=True)

            metrics = {
                "timestamp": datetime.now().isoformat(),
                # quality_score está no nível superior do relatório consolidado
                "quality_score": report.get("quality_score", 0),
                "total_files": vio_stats.get("total_files", 0),
                "violation_files": vio_stats.get("violation_files", 0),
                "template_files": len(templates_list),
                "error_count": err_meta.get("total_errors", 0),
                "high_priority_issues": vio_stats.get("high_priority", 0),
                "violations_by_type": self._group_violations_by_type(violations),
                "score_trend": self._get_score_trend(),
                "priorities": report.get("priorities", []),
                "files": files_items,
                "generated_at": report.get("metadata", {}).get("generated_at", ""),
                "project": str(self.project_path),
            }
            
            return metrics
            
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _group_violations_by_type(self, violations: Dict) -> Dict:
        """Agrupa violações por categoria para gráficos (conforme esquema atual)."""
        types: Dict[str, int] = {}
        items = (violations.get("violations", []) or []) + (violations.get("warnings", []) or [])
        for item in items:
            category = item.get("category", "Outros")
            types[category] = types.get(category, 0) + 1
        return types
    
    def _get_score_trend(self) -> List[Dict]:
        """Obtém tendência do score (apenas ponto atual)."""
        # Retorna apenas o ponto atual - o histórico é gerenciado no frontend
        return []
    
    async def _handle_websocket(self, websocket: WebSocket):
        """Gerencia conexões WebSocket."""
        await websocket.accept()
        self.connected_clients.append(websocket)
        
        try:
            while True:
                # Enviar métricas atualizadas a cada 5 segundos
                metrics = await self._get_current_metrics()
                await websocket.send_text(json.dumps(metrics))
                await asyncio.sleep(5)
                
        except WebSocketDisconnect:
            self.connected_clients.remove(websocket)
    
    async def broadcast_update(self, data: Dict):
        """Envia atualizações para todos os clientes conectados."""
        if self.connected_clients:
            message = json.dumps(data)
            for client in self.connected_clients.copy():
                try:
                    await client.send_text(message)
                except Exception:
                    self.connected_clients.remove(client)
    
    def run(self, host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
        """Inicia o servidor."""
        uvicorn.run(
            "codehealthanalyzer.web.server:app",
            host=host,
            port=port,
            reload=reload
        )


# Instância global da aplicação
server = DashboardServer()
app = server.app


def start_dashboard(project_path: str = ".", host: str = "127.0.0.1", port: int = 8000):
    """Função conveniente para iniciar o dashboard."""
    dashboard_server = DashboardServer(project_path)
    dashboard_server.run(host=host, port=port)


if __name__ == "__main__":
    start_dashboard()