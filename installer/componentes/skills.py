"""Copia las skills del repo a Claude Code y a opencode."""
from __future__ import annotations

import filecmp
import shutil
from pathlib import Path

from ..comun import REPO, Rutas, backup, quitar
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

    def _situacion(self, rutas: Rutas, skill: str) -> str:
        dst = self.destino(rutas) / skill
        if carpetas_iguales(SKILLS_REPO / skill, dst):
            return "ya instalada y al día"
        return "difiere del repo: se actualizaría" if dst.exists() else "no instalada"

    def instalar(self, rutas: Rutas, sis, ui) -> list[str]:
        registro = []
        opciones = [f"{s}  ({self._situacion(rutas, s)})" for s in self.skills]
        elegidas = ui.seleccionar(f"¿Qué skills instalar en {self.destino(rutas)}?", opciones)
        if elegidas is None:
            return ["cancelado"]
        for s in (self.skills[i] for i in elegidas):
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


    def desinstalar(self, rutas: Rutas, sis, ui) -> list[str]:
        presentes = [s for s in self.skills if (self.destino(rutas) / s).exists()]
        if not presentes:
            return [f"no hay skills del repo en {self.destino(rutas)}"]
        opciones = [f"{s}  ({self._situacion(rutas, s)})" for s in presentes]
        elegidas = ui.seleccionar(f"¿Qué skills quitar de {self.destino(rutas)}?", opciones)
        if elegidas is None:
            return ["cancelado"]
        registro = []
        for s in (presentes[i] for i in elegidas):
            dst = self.destino(rutas) / s
            backup(rutas, dst)
            quitar(dst)
            registro.append(f"{s}: desinstalada (copia en el backup)")
        return registro


class SkillsClaude(_CopiaSkills):
    nombre = "Skills de Claude Code"
    icono = "🧠"
    skills = TODAS

    def destino(self, rutas):
        return rutas.claude_skills

    def requisitos(self, sis):
        return [] if sis.which("opencode") else ["opencode (solo para jsk-opencode)"]


class SkillsOpencode(_CopiaSkills):
    nombre = "Skills de opencode"
    icono = "🤖"
    skills = [s for s in TODAS if s != "jsk-opencode"]

    def destino(self, rutas):
        return rutas.opencode_skills

    def requisitos(self, sis):
        return [] if sis.which("opencode") else ["opencode"]
