"""Skills de terceros: abre Claude Code con un prompt que las instala siguiendo el README de su repo."""
from __future__ import annotations

from ..comun import Rutas, backup, quitar
from . import Estado


class SkillTercero:
    def __init__(self, carpeta: str, repo_url: str):
        self.carpeta, self.repo_url = carpeta, repo_url
        self.nombre = f"Skill {carpeta} (tercero)"
        self.icono = "🎨"

    def requisitos(self, sis) -> list[str]:
        return [] if sis.which("claude") else ["claude"]

    def _instalada(self, rutas: Rutas) -> bool:
        return (rutas.claude_skills / self.carpeta / "SKILL.md").exists()

    def estado(self, rutas: Rutas, sis) -> Estado:
        return Estado(int(self._instalada(rutas)), 1)

    def prompt(self) -> str:
        return (
            f"Instala la skill {self.carpeta} en Claude Code siguiendo las instrucciones del README de su "
            f"repositorio: {self.repo_url}. Léelas primero, instálala en ~/.claude/skills/ y, al terminar, "
            f"confirma que {self.carpeta}/SKILL.md existe y dime cómo se invoca."
        )

    def instalar(self, rutas: Rutas, sis, ui) -> list[str]:
        if self._instalada(rutas):
            return [f"{self.carpeta}: ya estaba"]
        if not sis.which("claude"):
            raise RuntimeError("no se encontró el comando claude (instala Claude Code primero)")
        ui.avisar(f"Se abre Claude Code con el prompt de instalación de {self.carpeta}; al terminar, sal con /exit.")
        sis.run_interactivo([sis.which("claude"), self.prompt()])
        if self._instalada(rutas):
            return [f"{self.carpeta}: instalada (se activa en una sesión nueva de Claude Code)"]
        return [f"{self.carpeta}: no se detectó en {rutas.claude_skills}; revisa si la instalación terminó"]


    def desinstalar(self, rutas: Rutas, sis, ui) -> list[str]:
        dst = rutas.claude_skills / self.carpeta
        if not dst.exists() and not dst.is_symlink():
            return [f"{self.carpeta}: no estaba instalada"]
        era_enlace = dst.is_symlink()
        backup(rutas, dst)
        quitar(dst)
        nota = " (era un enlace: el original sigue en su sitio; si lo gestiona Skillshare, quítala allí)" if era_enlace else ""
        return [f"{self.carpeta}: desinstalada, copia en el backup{nota}"]


def terceros() -> list[SkillTercero]:
    return [
        SkillTercero("hallmark", "https://github.com/Nutlope/hallmark"),
        SkillTercero("impeccable", "https://github.com/pbakaus/impeccable"),
    ]
