"""Piezas comunes del instalador: rutas, escritura segura, JSON con comentarios y acceso al sistema."""
from __future__ import annotations

import datetime
import json
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLANTILLAS = Path(__file__).resolve().parent / "plantillas"
BOM = b"\xef\xbb\xbf"


# --------------------------------------------------------------------------- rutas

def _sello() -> str:
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


@dataclass
class Rutas:
    """Carpetas del usuario. En los tests apuntan a una carpeta temporal."""
    home: Path
    appdata: Path
    localappdata: Path
    sello: str = field(default_factory=_sello)

    @classmethod
    def desde_entorno(cls, env=None) -> "Rutas":
        env = os.environ if env is None else env
        home = Path(env["USERPROFILE"])
        return cls(
            home=home,
            appdata=Path(env.get("APPDATA") or home / "AppData" / "Roaming"),
            localappdata=Path(env.get("LOCALAPPDATA") or home / "AppData" / "Local"),
        )

    @property
    def backup_dir(self) -> Path:
        return self.home / ".claude-tools-backup" / self.sello

    @property
    def claude_skills(self) -> Path:
        return self.home / ".claude" / "skills"

    @property
    def opencode_skills(self) -> Path:
        return self.home / ".config" / "opencode" / "skills"

    @property
    def claude_plugins(self) -> Path:
        return self.home / ".claude" / "plugins"

    @property
    def herdr(self) -> Path:
        return self.home / ".config" / "herdr-app"

    @property
    def vscode_settings(self) -> Path:
        return self.appdata / "Code" / "User" / "settings.json"

    @property
    def fuentes_usuario(self) -> Path:
        return self.localappdata / "Microsoft" / "Windows" / "Fonts"

    @property
    def menu_inicio(self) -> Path:
        return self.appdata / "Microsoft" / "Windows" / "Start Menu" / "Programs"


# --------------------------------------------------------------------------- escritura segura

def backup(rutas: Rutas, ruta: Path) -> Path | None:
    """Copia un archivo o carpeta existente a ~/.claude-tools-backup/<sello>/ con su ruta relativa."""
    if not ruta.exists():
        return None
    try:
        rel = ruta.resolve().relative_to(rutas.home.resolve())
    except ValueError:
        rel = Path(*ruta.resolve().parts[1:])  # fuera del perfil: ruta sin la unidad
    destino = rutas.backup_dir / rel
    destino.parent.mkdir(parents=True, exist_ok=True)
    if ruta.is_dir():
        shutil.copytree(ruta, destino, dirs_exist_ok=True)
    else:
        shutil.copy2(ruta, destino)
    return destino


def quitar(ruta: Path) -> None:
    """Borra un archivo, una carpeta o un enlace. Un enlace se quita sin tocar lo que apunta."""
    if ruta.is_symlink() or ruta.is_file():
        try:
            ruta.unlink()
        except OSError:
            os.rmdir(ruta)  # enlace a carpeta en Windows
    elif ruta.is_dir():
        shutil.rmtree(ruta)


def leer_texto(ruta: Path) -> str:
    """Lee UTF-8 (con o sin BOM) y devuelve el texto con saltos de línea LF."""
    datos = ruta.read_bytes()
    if datos.startswith(BOM):
        datos = datos[len(BOM):]
    return datos.decode("utf-8").replace("\r\n", "\n")


def escribir(rutas: Rutas, ruta: Path, contenido: str, *, forzar_lf: bool = False) -> bool:
    """Escribe `contenido` (con LF) respetando el CRLF y el BOM del archivo existente.

    Si el resultado es igual a lo que ya hay, no toca nada. Antes de sobrescribir hace backup.
    Devuelve True si escribió.
    """
    contenido = contenido.replace("\r\n", "\n")
    bom, crlf = b"", False
    if ruta.exists():
        viejo = ruta.read_bytes()
        bom = BOM if viejo.startswith(BOM) else b""
        crlf = b"\r\n" in viejo and not forzar_lf
    nuevo = bom + (contenido.replace("\n", "\r\n") if crlf else contenido).encode("utf-8")
    if ruta.exists():
        if ruta.read_bytes() == nuevo:
            return False
        backup(rutas, ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_bytes(nuevo)
    return True


def plantilla(nombre: str) -> str:
    return leer_texto(PLANTILLAS / nombre)


# --------------------------------------------------------------------------- JSON con comentarios (VS Code)

def _escanear(t: str):
    """Tokens significativos de un texto JSONC: (tipo, inicio, fin). Salta espacios y comentarios."""
    tokens, i, n = [], 0, len(t)
    while i < n:
        c = t[i]
        if c == '"':
            j = i + 1
            while j < n and t[j] != '"':
                j += 2 if t[j] == "\\" else 1
            tokens.append(("str", i, j + 1))
            i = j + 1
        elif t.startswith("//", i):
            j = t.find("\n", i)
            i = n if j < 0 else j
        elif t.startswith("/*", i):
            j = t.find("*/", i + 2)
            i = n if j < 0 else j + 2
        elif c.isspace():
            i += 1
        else:
            tokens.append(("chr", i, i + 1))
            i += 1
    return tokens


def jsonc_cargar(t: str):
    """Parsea JSON con comentarios y comas finales sin alterar el contenido de los strings."""
    tokens = _escanear(t)
    partes = []
    for k, (tipo, a, b) in enumerate(tokens):
        if tipo == "chr" and t[a] == "," and k + 1 < len(tokens) and t[tokens[k + 1][1]] in "}]":
            continue  # coma final
        if partes and tipo == "chr" and tokens[k - 1][0] == "chr" and tokens[k - 1][2] != a:
            partes.append(" ")  # separa literales que estaban separados (p. ej. números)
        partes.append(t[a:b])
    return json.loads("".join(partes))


def _formatear(valor, indent: str) -> str:
    return json.dumps(valor, indent=4, ensure_ascii=False).replace("\n", "\n" + indent)


def _clave_en(t: str, tokens, clave: str):
    """(k, m): índice del token de la clave de primer nivel y del que sigue a su valor; None si no está."""
    prof = 0
    for k, (tipo, a, b) in enumerate(tokens):
        if tipo == "chr" and t[a] in "{[":
            prof += 1
        elif tipo == "chr" and t[a] in "}]":
            prof -= 1
        elif (tipo == "str" and prof == 1 and k + 1 < len(tokens)
              and t[tokens[k + 1][1]] == ":" and json.loads(t[a:b]) == clave):
            d, m = 0, k + 2
            while m < len(tokens):
                ch = t[tokens[m][1]] if tokens[m][0] == "chr" else ""
                if ch in ("{", "["):
                    d += 1
                elif ch in ("}", "]"):
                    if d == 0:
                        break
                    d -= 1
                    if d == 0:
                        m += 1
                        break
                elif ch == "," and d == 0:
                    break
                m += 1
            return k, m
    return None


def jsonc_quitar(t: str, clave: str) -> str:
    """Quita `clave` de primer nivel de un JSONC, conservando comentarios y formato del resto."""
    tokens = _escanear(t)
    hallada = _clave_en(t, tokens, clave) if tokens else None
    if not hallada:
        return t
    k, m = hallada
    ini, fin = tokens[k][1], tokens[m - 1][2]
    if m < len(tokens) and t[tokens[m][1]] == ",":
        fin = tokens[m][2]  # con su coma
    elif k > 0 and t[tokens[k - 1][1]] == ",":
        ini = tokens[k - 1][1]  # era la última: se lleva la coma anterior
    a, z = t.rfind("\n", 0, ini) + 1, t.find("\n", fin)
    z = len(t) if z < 0 else z
    if t[a:ini].strip() == "" and t[fin:z].strip() == "":
        ini, fin = a, min(z + 1, len(t))  # la clave ocupaba toda su línea
    nuevo = t[:ini] + t[fin:]
    resto = jsonc_cargar(t)
    resto.pop(clave, None)
    if jsonc_cargar(nuevo) != resto:
        raise ValueError(f"no se pudo quitar {clave} del JSON")
    return nuevo


def jsonc_set(t: str, clave: str, valor) -> str:
    """Pone `clave` de primer nivel a `valor` en un JSONC, conservando comentarios y formato del resto."""
    if jsonc_cargar(t).get(clave, object()) == valor:
        return t
    tokens = _escanear(t)
    if not tokens or t[tokens[0][1]] != "{":
        raise ValueError("el JSON no es un objeto")
    hallada = _clave_en(t, tokens, clave)
    if hallada:
        k, m = hallada
        a = tokens[k][1]
        inicio, fin = tokens[k + 2][1], tokens[m - 1][2]
        linea = t.rfind("\n", 0, a) + 1
        indent = t[linea:a] if t[linea:a].strip() == "" else ""
        nuevo = t[:inicio] + _formatear(valor, indent) + t[fin:]
    else:
        apertura = tokens[0][2]
        indent = "    "
        if len(tokens) > 1 and tokens[1][0] == "str":
            linea = t.rfind("\n", 0, tokens[1][1]) + 1
            if t[linea:tokens[1][1]].strip() == "":
                indent = t[linea:tokens[1][1]]
        vacio = len(tokens) > 1 and t[tokens[1][1]] == "}"
        entrada = f"\n{indent}{json.dumps(clave)}: {_formatear(valor, indent)}" + ("\n" if vacio else ",")
        nuevo = t[:apertura] + entrada + t[apertura:]
    if jsonc_cargar(nuevo).get(clave) != valor:
        raise ValueError(f"no se pudo poner {clave} en el JSON")
    return nuevo


# --------------------------------------------------------------------------- sistema (se sustituye en los tests)

class Sistema:
    """Todo lo que toca el sistema real. Los tests usan una versión falsa."""

    def which(self, nombre: str) -> str | None:
        return shutil.which(nombre)

    def run(self, cmd: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")

    def run_interactivo(self, cmd: list[str]) -> int:
        """Ejecuta un programa con la consola de la persona (sin capturar la salida)."""
        return subprocess.run(cmd).returncode

    def descargar(self, url: str, destino: Path) -> None:
        import urllib.request
        urllib.request.urlretrieve(url, destino)

    def ruta_corta(self, ruta: str) -> str:
        try:
            import ctypes
            buf = ctypes.create_unicode_buffer(1024)
            if ctypes.windll.kernel32.GetShortPathNameW(ruta, buf, 1024):
                return buf.value
        except (AttributeError, OSError):
            pass
        return ruta

    _CLAVE_FUENTES = r"Software\Microsoft\Windows NT\CurrentVersion\Fonts"

    def reg_fuente(self, nombre: str) -> str | None:
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self._CLAVE_FUENTES) as k:
                return winreg.QueryValueEx(k, nombre)[0]
        except (ImportError, OSError):
            return None

    def reg_fuente_borrar(self, nombre: str) -> None:
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self._CLAVE_FUENTES, 0, winreg.KEY_SET_VALUE) as k:
                winreg.DeleteValue(k, nombre)
        except (ImportError, OSError):
            pass

    def reg_fuente_poner(self, nombre: str, valor: str) -> None:
        import winreg
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, self._CLAVE_FUENTES) as k:
            winreg.SetValueEx(k, nombre, 0, winreg.REG_SZ, valor)


class Interfaz:
    """Cómo habla un componente con la persona. Los tests usan una versión falsa."""

    def avisar(self, msg: str) -> None:
        print(f"  ⚠  {msg}")

    def seleccionar(self, titulo: str, opciones: list[str]) -> list[int] | None:
        """Lista numerada; Enter o "todo" elige todas. Devuelve índices (desde 0) o None si cancela."""
        from .menu import Salir, elegir  # import aquí: menu importa este módulo
        print(f"\n  {titulo}")
        for i, o in enumerate(opciones, 1):
            print(f"    {i}. {o}")
        while True:
            try:
                t = input('  Números separados por espacio, Enter o "todo" para todas, "q" para cancelar:\n  > ')
            except EOFError:
                return None
            if not t.strip():
                return list(range(len(opciones)))
            try:
                return elegir(t, len(opciones))
            except Salir:
                return None
            except ValueError as e:
                print(f"  {e}")

    def confirmar(self, msg: str) -> bool:
        return input(f"  {msg} [s/n] ").strip().lower() in ("s", "si", "sí", "y", "yes")
