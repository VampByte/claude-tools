"""Copia las skills del repo a Claude Code y a opencode."""
from __future__ import annotations

import filecmp
import shutil
from pathlib import Path

from ..comun import REPO, Rutas, backup
from . import Estado

SKILLS_REPO = REPO / "skills"
TODAS = ["entrevistador-procesos", "humanizador", "jsk-opencode",
         "optimizador-prompts", "presentaciones-visuales", "verificador-datos"]


def carpetas_iguales(a: Path, b: Path) -> bool:
    if not b.is_dir():
        return False
    c = filecmp.dircmp(a, b)
    if c.left_only or c.right_only or c.funny_files:
        return False
    _, distintos, errores = filecmp.cmpfiles(a, b, c.common_files, shallow=False)
    if distintos or errores:
        return False
    return all(carpetas_iguales(a / d, b / d) for d in c.common_dirs)


class _CopiaSkills:
    nombre = ""
    skills: list[str] = []

    def destino(self, rutas: Rutas) -> Path:
        raise NotImplementedError

    def requisitos(self, sis) -> list[str]:
        return []

    def estado(self, rutas: Rutas, sis) -> Estado:
        hechas = sum(carpetas_iguales(SKILLS_REPO / s, self.destino(rutas) / s) for s in self.skills)
        return Estado(hechas, len(self.skills))

    def instalar(self, rutas: Rutas, sis, ui) -> list[str]:
        registro = []
        for s in self.skills:
            origen, dst = SKILLS_REPO / s, self.destino(rutas) / s
            if carpetas_iguales(origen, dst):
                registro.append(f"{s}: ya estaba")
                continue
            if dst.exists():
                backup(rutas, dst)
                shutil.rmtree(dst)
                registro.append(f"{s}: actualizada (copia de la anterior en el backup)")
            else:
                registro.append(f"{s}: instalada")
            shutil.copytree(origen, dst)
        return registro


class SkillsClaude(_CopiaSkills):
    nombre = "Skills de Claude Code"
    skills = TODAS

    def destino(self, rutas):
        return rutas.claude_skills

    def requisitos(self, sis):
        return [] if sis.which("opencode") else ["opencode (solo para jsk-opencode)"]


class SkillsOpencode(_CopiaSkills):
    nombre = "Skills de opencode"
    skills = [s for s in TODAS if s != "jsk-opencode"]

    def destino(self, rutas):
        return rutas.opencode_skills

    def requisitos(self, sis):
        return [] if sis.which("opencode") else ["opencode"]
