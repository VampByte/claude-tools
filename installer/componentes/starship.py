"""Starship en Git Bash, con Nerd Font en Herdr, mintty y VS Code (ver docs/herdr-git-bash-starship.md)."""
from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from pathlib import Path

from ..comun import Rutas, escribir, jsonc_cargar, jsonc_set, leer_texto, plantilla
from . import Estado

FUENTE = "FiraCode Nerd Font Mono"
FUENTE_ZIP = "https://github.com/ryanoasis/nerd-fonts/releases/download/v3.5.1/FiraCode.zip"
FUENTES = {
    "FiraCodeNerdFontMono-Regular.ttf": "FiraCode Nerd Font Mono Regular (TrueType)",
    "FiraCodeNerdFontMono-Bold.ttf": "FiraCode Nerd Font Mono Bold (TrueType)",
}
WINGET_STARSHIP = ["winget", "install", "--id", "Starship.Starship", "--exact", "--scope", "user",
                   "--accept-package-agreements", "--accept-source-agreements", "--disable-interactivity"]
ARCHIVOS_SHELL = {".bashrc": "bashrc", ".bash_profile": "bash_profile", ".config/starship.toml": "starship.toml"}
LNK = "Git Bash (C).lnk"
VS_PERFIL = "terminal.integrated.profiles.windows"
VS_DEFECTO = "terminal.integrated.defaultProfile.windows"
VS_FUENTE = "terminal.integrated.fontFamily"


def git_root(sis) -> Path:
    """Carpeta de Git for Windows, a partir de `git` en el PATH."""
    g = sis.which("git")
    if g:
        p = Path(g).resolve().parent
        for c in (p.parent, p.parent.parent):
            if (c / "bin" / "bash.exe").exists():
                return c
    return Path(r"C:\Program Files\Git")


def _barras(p) -> str:
    return str(p).replace("\\", "/")


def _cargar_json(ruta: Path) -> dict:
    return json.loads(leer_texto(ruta)) if ruta.exists() else {}


def _ini(texto: str) -> dict[str, str]:
    return {k.strip(): v.strip() for k, _, v in
            (l.partition("=") for l in texto.splitlines()) if _ and not k.strip().startswith("#")}


class _Ctx:
    def __init__(self, rutas: Rutas, sis):
        self.rutas, self.sis = rutas, sis
        self.hay_git = bool(sis.which("git"))
        self.hay_herdr = bool(sis.which("herdr-app")) or rutas.herdr.is_dir()
        self.hay_vscode = bool(sis.which("code")) or rutas.vscode_settings.parent.is_dir()
        self.git = git_root(sis)

    # --- 1. Starship
    def starship_hecho(self):
        paquetes = self.rutas.localappdata / "Microsoft" / "WinGet" / "Packages"
        return bool(self.sis.which("starship")) or any(paquetes.glob("Starship.Starship_*"))

    def starship_hacer(self):
        if not self.sis.which("winget"):
            raise RuntimeError("no se encontró winget")
        r = self.sis.run(WINGET_STARSHIP)
        if r.returncode != 0 and not self.starship_hecho():
            raise RuntimeError(f"winget falló: {(r.stdout or r.stderr).strip()[-300:]}")

    # --- 2. Nerd Font
    def _destinos_fuente(self):
        dirs = [self.rutas.fuentes_usuario]
        if self.hay_herdr:
            dirs.append(self.rutas.herdr / "fonts")
        return dirs

    def fuente_hecho(self):
        u = self.rutas.fuentes_usuario
        return (all((d / f).exists() for d in self._destinos_fuente() for f in FUENTES)
                and all(self.sis.reg_fuente(n) == str(u / f) for f, n in FUENTES.items()))

    def fuente_hacer(self):
        origen = next((d for d in self._destinos_fuente() if all((d / f).exists() for f in FUENTES)), None)
        tmp = None
        if origen is None:
            tmp = Path(tempfile.mkdtemp(prefix="nerd-font-"))  # carpeta nueva y vacía
            zip_path = tmp / "FiraCode.zip"
            self.sis.descargar(FUENTE_ZIP, zip_path)
            with zipfile.ZipFile(zip_path) as z:
                for f in FUENTES:
                    (tmp / f).write_bytes(z.read(f))  # solo los dos .ttf, sin extraer todo el zip
            origen = tmp
        try:
            for d in self._destinos_fuente():
                d.mkdir(parents=True, exist_ok=True)
                for f in FUENTES:
                    if not (d / f).exists():
                        shutil.copy2(origen / f, d / f)
            for f, n in FUENTES.items():
                self.sis.reg_fuente_poner(n, str(self.rutas.fuentes_usuario / f))
        finally:
            if tmp:
                shutil.rmtree(tmp, ignore_errors=True)

    # --- 3. .bashrc, .bash_profile, starship.toml
    def shell_hecho(self):
        return all((self.rutas.home / d).exists() and leer_texto(self.rutas.home / d) == plantilla(p)
                   for d, p in ARCHIVOS_SHELL.items())

    def shell_hacer(self):
        for d, p in ARCHIVOS_SHELL.items():
            escribir(self.rutas, self.rutas.home / d, plantilla(p), forzar_lf=True)

    # --- 4. Herdr: fuente y entrada Git Bash en el menú "+"
    def _entrada_herdr(self):
        e = json.loads(plantilla("programs.json"))["programs"]["git-bash"]
        e["run"][0] = _barras(self.sis.ruta_corta(str(self.git / "bin" / "bash.exe")))
        return e

    def herdr_hecho(self):
        s = _cargar_json(self.rutas.herdr / "settings.json")
        p = _cargar_json(self.rutas.herdr / "programs.json")
        return s.get("font") == FUENTE and p.get("programs", {}).get("git-bash") == self._entrada_herdr()

    def herdr_hacer(self):
        ruta = self.rutas.herdr / "settings.json"
        s = _cargar_json(ruta)
        if s.get("font") != FUENTE:
            s["font"] = FUENTE
            escribir(self.rutas, ruta, json.dumps(s, indent=2, ensure_ascii=False) + "\n")
        ruta = self.rutas.herdr / "programs.json"
        p = _cargar_json(ruta)
        p.setdefault("programs", {})["git-bash"] = self._entrada_herdr()  # conserva los demás programas
        escribir(self.rutas, ruta, json.dumps(p, indent=2, ensure_ascii=False) + "\n")

    # --- 5. mintty
    def _minttyrc(self):
        return self.rutas.home / ".minttyrc"

    def mintty_hecho(self):
        r = self._minttyrc()
        if not r.exists():
            return False
        actual = _ini(leer_texto(r))
        return all(actual.get(k) == v for k, v in _ini(plantilla("minttyrc")).items())

    def mintty_hacer(self):
        r = self._minttyrc()
        if not r.exists():
            escribir(self.rutas, r, plantilla("minttyrc"))
            return
        lineas = leer_texto(r).splitlines()
        faltan = dict(_ini(plantilla("minttyrc")))
        for i, l in enumerate(lineas):
            k = l.partition("=")[0].strip()
            if k in faltan:
                lineas[i] = f"{k}={faltan.pop(k)}"
        lineas += [f"{k}={v}" for k, v in faltan.items()]
        escribir(self.rutas, r, "\n".join(lineas) + "\n")

    # --- 6. Acceso directo "Git Bash (C)"
    def lnk_hecho(self):
        return (self.rutas.menu_inicio / LNK).exists()

    def lnk_hacer(self):
        q = lambda s: str(s).replace("'", "''")
        exe = self.git / "git-bash.exe"
        lnk = self.rutas.menu_inicio / LNK
        lnk.parent.mkdir(parents=True, exist_ok=True)
        ps = (f"$s=New-Object -ComObject WScript.Shell; $l=$s.CreateShortcut('{q(lnk)}'); "
              f"$l.TargetPath='{q(exe)}'; $l.Arguments=''; $l.WorkingDirectory='C:\\'; "
              f"$l.IconLocation='{q(exe)},0'; $l.Save()")
        r = self.sis.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps])
        if r.returncode != 0:
            raise RuntimeError(f"no se pudo crear el acceso directo: {r.stderr.strip()[-300:]}")

    # --- 7. VS Code
    def _vscode_valores(self, actual: dict) -> dict:
        perfiles = dict(actual.get(VS_PERFIL) or {})
        perfiles["Git Bash"] = {"path": _barras(self.git / "bin" / "bash.exe"),
                                "args": ["--login", "-i"], "icon": "terminal-bash"}
        return {VS_DEFECTO: "Git Bash", VS_PERFIL: perfiles, VS_FUENTE: FUENTE}

    def vscode_hecho(self):
        r = self.rutas.vscode_settings
        if not r.exists():
            return False
        actual = jsonc_cargar(leer_texto(r))
        return all(actual.get(k) == v for k, v in self._vscode_valores(actual).items())

    def vscode_hacer(self):
        r = self.rutas.vscode_settings
        texto = leer_texto(r) if r.exists() and leer_texto(r).strip() else "{\n}\n"
        for k, v in self._vscode_valores(jsonc_cargar(texto)).items():
            texto = jsonc_set(texto, k, v)
        escribir(self.rutas, r, texto)

    def pasos(self):
        """(nombre, aplica, hecho, hacer). `aplica` es False si falta el programa que lo necesita."""
        return [
            ("Starship (winget)", True, self.starship_hecho, self.starship_hacer),
            ("Nerd Font", True, self.fuente_hecho, self.fuente_hacer),
            (".bashrc, .bash_profile y starship.toml", True, self.shell_hecho, self.shell_hacer),
            ("Herdr: fuente y Git Bash en el menú +", self.hay_herdr, self.herdr_hecho, self.herdr_hacer),
            ("mintty (.minttyrc)", self.hay_git, self.mintty_hecho, self.mintty_hacer),
            ('Acceso directo "Git Bash (C)"', self.hay_git, self.lnk_hecho, self.lnk_hacer),
            ("VS Code: Git Bash por defecto y fuente", self.hay_git and self.hay_vscode,
             self.vscode_hecho, self.vscode_hacer),
        ]


class Starship:
    nombre = "Starship y terminales"
    PROGRAMAS = {"git": "Git", "herdr-app": "Herdr", "code": "VS Code"}

    def requisitos(self, sis) -> list[str]:
        return [n for c, n in self.PROGRAMAS.items() if not sis.which(c)]

    def estado(self, rutas: Rutas, sis) -> Estado:
        ctx = _Ctx(rutas, sis)
        aplican = [p for p in ctx.pasos() if p[1]]
        omitidos = len(ctx.pasos()) - len(aplican)
        return Estado(sum(bool(p[2]()) for p in aplican), len(aplican),
                      f"{omitidos} paso(s) no aplican" if omitidos else "")

    def instalar(self, rutas: Rutas, sis, ui) -> list[str]:
        faltan = self.requisitos(sis)
        if faltan:
            ui.avisar(f"Falta: {', '.join(faltan)}. Se saltarán las partes que lo necesitan.")
            if not ui.confirmar("¿Seguir sin esas partes?"):
                return ["cancelado"]
        ctx = _Ctx(rutas, sis)
        registro = []
        for nombre, aplica, hecho, hacer in ctx.pasos():
            if not aplica:
                registro.append(f"{nombre}: omitido (falta el programa)")
            elif hecho():
                registro.append(f"{nombre}: ya estaba")
            else:
                hacer()
                registro.append(f"{nombre}: hecho")
        return registro
