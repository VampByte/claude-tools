"""Instala el mod clean-view desde el marketplace vampbyte/claude-tools."""
from __future__ import annotations

import json

from ..comun import Rutas
from . import Estado

MARKETPLACE_REPO = "vampbyte/claude-tools"
MARKETPLACE = "claude-tools"
PLUGIN = "clean-view@claude-tools"


def _json(ruta):
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


class CleanView:
    nombre = "Mod clean-view"

    def requisitos(self, sis) -> list[str]:
        return [] if sis.which("claude") else ["claude"]

    def _marketplace(self, rutas: Rutas) -> bool:
        return MARKETPLACE in _json(rutas.claude_plugins / "known_marketplaces.json")

    def _plugin(self, rutas: Rutas) -> bool:
        datos = _json(rutas.claude_plugins / "installed_plugins.json")
        return PLUGIN in datos.get("plugins", datos)

    def estado(self, rutas: Rutas, sis) -> Estado:
        return Estado(int(self._marketplace(rutas)) + int(self._plugin(rutas)), 2)

    def _claude(self, sis, *args) -> None:
        r = sis.run([sis.which("claude"), *args])
        if r.returncode != 0:
            raise RuntimeError(f"claude {' '.join(args)} falló: {(r.stderr or r.stdout).strip()[-300:]}")

    def instalar(self, rutas: Rutas, sis, ui) -> list[str]:
        if not sis.which("claude"):
            raise RuntimeError("no se encontró el comando claude (instala Claude Code primero)")
        registro = []
        if self._marketplace(rutas):
            registro.append("marketplace claude-tools: ya estaba")
        else:
            self._claude(sis, "plugin", "marketplace", "add", MARKETPLACE_REPO)
            registro.append("marketplace claude-tools: añadido")
        if self._plugin(rutas):
            registro.append("clean-view: ya estaba")
        else:
            self._claude(sis, "plugin", "install", PLUGIN, "--scope", "user")
            registro.append("clean-view: instalado (se activa en una sesión nueva de Claude Code)")
        return registro
