"""Componentes que el menú puede instalar, en el orden en que se muestran."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Estado:
    hecho: int
    total: int
    nota: str = ""

    @property
    def completo(self) -> bool:
        return self.total > 0 and self.hecho >= self.total

    @property
    def texto(self) -> str:
        if self.completo:
            base = "instalado"
        elif self.hecho == 0:
            base = "no instalado"
        else:
            base = f"{self.hecho} de {self.total}"
        return f"{base}; {self.nota}" if self.nota else base


def componentes():
    from .clean_view import CleanView
    from .skills import SkillsClaude, SkillsOpencode
    from .starship import Starship
    return [SkillsClaude(), SkillsOpencode(), CleanView(), Starship()]
