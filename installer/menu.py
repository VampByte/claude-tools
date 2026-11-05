"""Menú de consola: muestra el estado de cada componente y deja elegir qué instalar."""
from __future__ import annotations

import sys

from .comun import Interfaz, Rutas, Sistema
from .componentes import Estado, componentes


class Salir(Exception):
    pass


def elegir(texto: str, total: int) -> list[int]:
    """Convierte "1 3", "todo" o "q" en índices (desde 0). Lanza ValueError si no es válido."""
    t = texto.strip().lower()
    if t in ("q", "salir"):
        raise Salir
    if t in ("todo", "t"):
        return list(range(total))
    partes = t.replace(",", " ").split()
    if not partes:
        raise ValueError("no elegiste nada")
    indices = set()
    for p in partes:
        if not p.isdigit() or not 1 <= int(p) <= total:
            raise ValueError(f'"{p}" no es una opción (usa números del 1 al {total})')
        indices.add(int(p) - 1)
    return sorted(indices)


def linea(n: int, nombre: str, estado: Estado, faltan: list[str]) -> str:
    marca = "[x]" if estado.completo else "[ ]"
    extra = f"; falta: {', '.join(faltan)}" if faltan else ""
    return f"  {n}. {marca} {nombre:<24} ({estado.texto}{extra})"


def _estado_seguro(c, rutas, sis) -> Estado:
    try:
        return c.estado(rutas, sis)
    except Exception as e:  # un estado roto no debe tumbar el menú
        return Estado(0, 1, f"no se pudo comprobar: {e}")


def dibujar(comps, rutas, sis) -> None:
    print("\nclaude-tools: instalador\n")
    for i, c in enumerate(comps, 1):
        print(linea(i, c.nombre, _estado_seguro(c, rutas, sis), c.requisitos(sis)))
    print()


def main(rutas: Rutas | None = None, sis=None, ui=None) -> int:
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    rutas = rutas or Rutas.desde_entorno()
    sis, ui = sis or Sistema(), ui or Interfaz()
    comps = componentes()
    while True:
        dibujar(comps, rutas, sis)
        try:
            elegidos = elegir(input('Elige números separados por espacio, "todo" o "q" para salir:\n> '), len(comps))
        except Salir:
            return 0
        except EOFError:
            return 0
        except ValueError as e:
            print(f"  {e}")
            continue
        print("\nSe va a instalar: " + ", ".join(comps[i].nombre for i in elegidos))
        if not ui.confirmar("¿Continuar?"):
            continue
        hubo_cambios = False
        for i in elegidos:
            c = comps[i]
            print(f"\n== {c.nombre}")
            try:
                for r in c.instalar(rutas, sis, ui):
                    print(f"  - {r}")
                    hubo_cambios |= "ya estaba" not in r and "omitido" not in r and r != "cancelado"
            except Exception as e:  # sigue con el siguiente componente
                print(f"  ERROR: {e}")
        if rutas.backup_dir.exists():
            print(f"\nCopias de los archivos anteriores en: {rutas.backup_dir}")
        if hubo_cambios:
            print("\nPara ver los cambios: reinicia Herdr y VS Code, y abre una sesión nueva de Claude Code.")
