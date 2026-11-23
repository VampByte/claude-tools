"""Starship en Git Bash, con Nerd Font en Herdr, mintty y VS Code (ver docs/herdr-git-bash-starship.md)."""
from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from pathlib import Path

from ..comun import Rutas, backup, escribir, jsonc_cargar, jsonc_quitar, jsonc_set, leer_texto, plantilla, quitar
from . import Estado

FUENTE = "FiraCode Nerd Font Mono"
FUENTE_ZIP = "https://github.com/ryanoasis/nerd-fonts/releases/download/v3.5.1/FiraCode.zip"
FUENTES = {
    "FiraCodeNerdFontMono-Regular.ttf": "FiraCode Nerd Font Mono Regular (TrueType)",
    "FiraCodeNerdFontMono-Bold.ttf": "FiraCode Nerd Font Mono Bold (TrueType)",
}
WINGET_STARSHIP = ["winget", "install", "--id", "Starship.Starship", "--exact", "--scope", "user",
                   "--accept-package-agreements", "--accept-source-agreements", "--disable-interactivity"]
WINGET_QUITAR = ["winget", "uninstall", "--id", "Starship.Starship", "--exact", "--silent",
                 "--disable-interactivity"]
ARCHIVOS_SHELL ={".bashrc": "bashrc", ".bash_profile": "bash_profile", ".config/starship.toml": "starship.toml"}
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

    # --- Desinstalar: cada `quitar_*` deshace solo lo que puso el instalador y devuelve una nota
    def _paquete_winget(self):
        return any((self.rutas.localappdata / "Microsoft" / "WinGet" / "Packages").glob("Starship.Starship_*"))

    def starship_quitar(self):
        if not self._paquete_winget():
            return "no se instaló con winget: no se toca"
        if not self.sis.which("winget"):
            raise RuntimeError("no se encontró winget")
        r = self.sis.run(WINGET_QUITAR)
        if r.returncode != 0 and self._paquete_winget():
            raise RuntimeError(f"winget falló: {(r.stdout or r.stderr).strip()[-300:]}")
        return "desinstalado"

    def _carpetas_fuente(self):
        return [self.rutas.fuentes_usuario, self.rutas.herdr / "fonts"]

    def fuente_presente(self):
        return (any((d / f).exists() for d in self._carpetas_fuente() for f in FUENTES)
                or any(self.sis.reg_fuente(n) for n in FUENTES.values()))

    def fuente_quitar(self):
        en_uso = []
        for d in self._carpetas_fuente():
            for f in FUENTES:
                try:
                    (d / f).unlink(missing_ok=True)
                except PermissionError:
                    en_uso.append(f)
        for n in FUENTES.values():
            self.sis.reg_fuente_borrar(n)
        if en_uso:
            raise RuntimeError("archivos en uso (cierra Herdr y VS Code, o reinicia Windows, y repite)")
        return "quitada"

    def shell_presente(self):
        return any((self.rutas.home / d).exists() for d in ARCHIVOS_SHELL)

    def shell_quitar(self):
        notas = []
        for d, p in ARCHIVOS_SHELL.items():
            ruta = self.rutas.home / d
            if not ruta.exists():
                continue
            if leer_texto(ruta) == plantilla(p):
                backup(self.rutas, ruta)
                quitar(ruta)
            else:
                notas.append(f"{d} tiene cambios tuyos: se deja")
        return "; ".join(notas) or "borrados"

    def _fuente_herdr_anterior(self):
        """Fuente de Herdr que había antes del instalador, si quedó en alguna copia de seguridad."""
        raiz = self.rutas.home / ".claude-tools-backup"
        for copia in sorted(raiz.glob("*/.config/herdr-app/settings.json")):
            try:
                f = json.loads(leer_texto(copia)).get("font")
            except ValueError:
                continue
            if f and f != FUENTE:
                return f
        return None

    def herdr_presente(self):
        p = _cargar_json(self.rutas.herdr / "programs.json")
        return (_cargar_json(self.rutas.herdr / "settings.json").get("font") == FUENTE
                or "git-bash" in p.get("programs", {}))

    def herdr_quitar(self):
        ruta = self.rutas.herdr / "settings.json"
        s = _cargar_json(ruta)
        nota = ""
        if s.get("font") == FUENTE:
            anterior = self._fuente_herdr_anterior()
            if anterior:
                s["font"] = anterior
                nota = f"; fuente restaurada a {anterior}"
            else:
                del s["font"]
                nota = "; fuente de Herdr a la predeterminada"
            escribir(self.rutas, ruta, json.dumps(s, indent=2, ensure_ascii=False) + "\n")
        ruta = self.rutas.herdr / "programs.json"
        p = _cargar_json(ruta)
        if p.get("programs", {}).pop("git-bash", None) is not None:
            escribir(self.rutas, ruta, json.dumps(p, indent=2, ensure_ascii=False) + "\n")
        return "quitado" + nota

    def mintty_presente(self):
        r = self._minttyrc()
        if not r.exists():
            return False
        actual = _ini(leer_texto(r))
        return any(actual.get(k) == v for k, v in _ini(plantilla("minttyrc")).items())

    def mintty_quitar(self):
        r = self._minttyrc()
        propias = _ini(plantilla("minttyrc"))
        quedan = [l for l in leer_texto(r).splitlines()
                  if propias.get(l.partition("=")[0].strip()) != l.partition("=")[2].strip()]
        if any(l.strip() for l in quedan):
            escribir(self.rutas, r, "\n".join(quedan) + "\n")
            return "claves del instalador quitadas; el resto se conserva"
        backup(self.rutas, r)
        quitar(r)
        return ".minttyrc borrado"

    def lnk_quitar(self):
        quitar(self.rutas.menu_inicio / LNK)
        return "quitado"

    def vscode_presente(self):
        r = self.rutas.vscode_settings
        if not r.exists():
            return False
        a = jsonc_cargar(leer_texto(r))
        return (a.get(VS_DEFECTO) == "Git Bash" or a.get(VS_FUENTE) == FUENTE
                or "Git Bash" in (a.get(VS_PERFIL) or {}))

    def vscode_quitar(self):
        r = self.rutas.vscode_settings
        texto = leer_texto(r)
        a = jsonc_cargar(texto)
        if a.get(VS_DEFECTO) == "Git Bash":
            texto = jsonc_quitar(texto, VS_DEFECTO)
        if a.get(VS_FUENTE) == FUENTE:
            texto = jsonc_quitar(texto, VS_FUENTE)
        perfiles = dict(a.get(VS_PERFIL) or {})
        if perfiles.pop("Git Bash", None) is not None:
            texto = jsonc_set(texto, VS_PERFIL, perfiles) if perfiles else jsonc_quitar(texto, VS_PERFIL)
        escribir(self.rutas, r, texto)
        return "claves quitadas"

    def pasos_quitar(self):
        """(nombre, presente, quitar), en el orden inverso al de instalación."""
        return [
            ("VS Code: Git Bash por defecto y fuente", self.vscode_presente, self.vscode_quitar),
            ('Acceso directo "Git Bash (C)"', lambda: (self.rutas.menu_inicio / LNK).exists(), self.lnk_quitar),
            ("mintty (.minttyrc)", self.mintty_presente, self.mintty_quitar),
            ("Herdr: fuente y Git Bash en el menú +", self.herdr_presente, self.herdr_quitar),
            (".bashrc, .bash_profile y starship.toml", self.shell_presente, self.shell_quitar),
            ("Nerd Font", self.fuente_presente, self.fuente_quitar),
            ("Starship (winget)", self._paquete_winget, self.starship_quitar),
        ]

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
    icono = "🚀"
    PROGRAMAS = {"git": "Git", "herdr-app": "Herdr", "code": "VS Code"}

    def requisitos(self, sis) -> list[str]:
        return [n for c, n in self.PROGRAMAS.items() if not sis.which(c)]

    def estado(self, rutas: Rutas, sis) -> Estado:
        ctx = _Ctx(rutas, sis)
        aplican = [p for p in ctx.pasos() if p[1]]
        omitidos = len(ctx.pasos()) - len(aplican)
        return Estado(sum(bool(p[2]()) for p in aplican), len(aplican),
                      f"{omitidos} paso(s) no aplican" if omitidos else "")

    def desinstalar(self, rutas: Rutas, sis, ui) -> list[str]:
        ctx = _Ctx(rutas, sis)
        presentes = [(n, q) for n, hay, q in ctx.pasos_quitar() if hay()]
        if not presentes:
            return ["no hay nada de Starship y terminales instalado"]
        elegidos = ui.seleccionar("¿Qué partes quitar?", [n for n, _ in presentes])
        if elegidos is None:
            return ["cancelado"]
        registro = []
        for i in elegidos:
            nombre, quitar_paso = presentes[i]
            try:
                registro.append(f"{nombre}: {quitar_paso()}")
            except Exception as e:  # un paso que falla no impide los demás
                registro.append(f"{nombre}: ERROR, {e}")
        return registro

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
