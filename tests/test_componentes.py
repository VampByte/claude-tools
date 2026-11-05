import io
import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

from installer.comun import Rutas, jsonc_cargar, leer_texto, plantilla
from installer.componentes.clean_view import CleanView
from installer.componentes.skills import SkillsClaude, SkillsOpencode
from installer.componentes.starship import FUENTE, FUENTES, LNK, Starship


class SistemaFalso:
    def __init__(self, git_root: Path, programas=("git", "herdr-app", "code", "claude", "winget")):
        self.git_root = git_root
        self.programas = set(programas)
        self.llamadas, self.reg, self.descargas = [], {}, 0

    def which(self, nombre):
        if nombre not in self.programas:
            return None
        if nombre == "git":
            return str(self.git_root / "cmd" / "git.exe")
        return f"/bin/{nombre}"

    def run(self, cmd):
        self.llamadas.append(cmd)
        if cmd[0] == "winget":
            self.programas.add("starship")
        if cmd[0] == "powershell.exe":  # simula el acceso directo
            ruta = cmd[-1].split("CreateShortcut('")[1].split("')")[0]
            Path(ruta).write_bytes(b"lnk")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    def descargar(self, url, destino):
        self.descargas += 1
        with zipfile.ZipFile(destino, "w") as z:
            for f in FUENTES:
                z.writestr(f, b"ttf-" + f.encode())

    def ruta_corta(self, ruta):
        return ruta.replace("Program Files", "PROGRA~1")

    def reg_fuente(self, nombre):
        return self.reg.get(nombre)

    def reg_fuente_poner(self, nombre, valor):
        self.reg[nombre] = valor


class InterfazFalsa:
    def __init__(self, respuesta=True):
        self.respuesta, self.avisos = respuesta, []

    def avisar(self, msg):
        self.avisos.append(msg)

    def confirmar(self, msg):
        return self.respuesta


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        raiz = Path(self.tmp.name)
        self.home = raiz / "home"
        self.home.mkdir()
        self.rutas = Rutas(home=self.home, appdata=self.home / "AppData" / "Roaming",
                           localappdata=self.home / "AppData" / "Local")
        self.git = raiz / "Program Files" / "Git"
        (self.git / "bin").mkdir(parents=True)
        (self.git / "bin" / "bash.exe").write_bytes(b"")
        (self.git / "cmd").mkdir()
        self.sis = SistemaFalso(self.git)
        self.ui = InterfazFalsa()

    def tearDown(self):
        self.tmp.cleanup()

    def sin_backups(self):
        return not (self.home / ".claude-tools-backup").exists()


class SkillsTest(Base):
    def test_instala_y_repetir_no_cambia_nada(self):
        c = SkillsClaude()
        self.assertEqual(c.estado(self.rutas, self.sis).hecho, 0)
        c.instalar(self.rutas, self.sis, self.ui)
        self.assertTrue(c.estado(self.rutas, self.sis).completo)
        self.assertTrue((self.rutas.claude_skills / "humanizador" / "SKILL.md").exists())
        registro = c.instalar(self.rutas, self.sis, self.ui)
        self.assertTrue(all("ya estaba" in r for r in registro))
        self.assertTrue(self.sin_backups())

    def test_skill_modificada_se_actualiza_con_backup(self):
        c = SkillsOpencode()
        c.instalar(self.rutas, self.sis, self.ui)
        (self.rutas.opencode_skills / "humanizador" / "SKILL.md").write_text("editada")
        self.assertEqual(c.estado(self.rutas, self.sis).hecho, 4)
        c.instalar(self.rutas, self.sis, self.ui)
        self.assertTrue(c.estado(self.rutas, self.sis).completo)
        respaldo = self.rutas.backup_dir / ".config" / "opencode" / "skills" / "humanizador" / "SKILL.md"
        self.assertEqual(respaldo.read_text(), "editada")

    def test_opencode_no_lleva_jsk_opencode(self):
        self.assertNotIn("jsk-opencode", SkillsOpencode().skills)
        self.assertEqual(len(SkillsOpencode().skills), 5)
        self.assertEqual(len(SkillsClaude().skills), 6)


class CleanViewTest(Base):
    def test_instala_marketplace_y_plugin(self):
        CleanView().instalar(self.rutas, self.sis, self.ui)
        cmds = [c[1:] for c in self.sis.llamadas]
        self.assertEqual(cmds, [["plugin", "marketplace", "add", "vampbyte/claude-tools"],
                                ["plugin", "install", "clean-view@claude-tools", "--scope", "user"]])

    def test_no_repite_lo_que_ya_esta(self):
        p = self.rutas.claude_plugins
        p.mkdir(parents=True)
        (p / "known_marketplaces.json").write_text('{"claude-tools": {}}')
        (p / "installed_plugins.json").write_text('{"version": 2, "plugins": {"clean-view@claude-tools": []}}')
        self.assertTrue(CleanView().estado(self.rutas, self.sis).completo)
        CleanView().instalar(self.rutas, self.sis, self.ui)
        self.assertEqual(self.sis.llamadas, [])

    def test_sin_claude_falla_con_mensaje(self):
        self.sis.programas.discard("claude")
        self.assertEqual(CleanView().requisitos(self.sis), ["claude"])
        with self.assertRaises(RuntimeError):
            CleanView().instalar(self.rutas, self.sis, self.ui)


class StarshipTest(Base):
    VSCODE = '{\n    // mi comentario\n    "editor.fontFamily": "Cascadia Code",\n    "terminal.integrated.defaultProfile.windows": "Command Prompt",\n}\n'

    def preparar(self):
        self.rutas.herdr.mkdir(parents=True)
        (self.rutas.herdr / "settings.json").write_text('{\n  "zoom": 1,\n  "font": "Cascadia Code"\n}\n')
        (self.rutas.herdr / "programs.json").write_text('{"programs": {"otro": {"name": "Otro", "run": ["x"]}}}')
        (self.rutas.herdr / "keys.json").write_bytes(b'{"global": {}}\r\n')
        self.rutas.vscode_settings.parent.mkdir(parents=True)
        self.rutas.vscode_settings.write_bytes(self.VSCODE.replace("\n", "\r\n").encode())

    def test_instalacion_completa_e_idempotente(self):
        self.preparar()
        c = Starship()
        self.assertEqual(c.estado(self.rutas, self.sis).hecho, 0)
        c.instalar(self.rutas, self.sis, self.ui)
        self.assertTrue(c.estado(self.rutas, self.sis).completo, c.estado(self.rutas, self.sis))

        # archivos de shell con LF
        self.assertEqual((self.home / ".bashrc").read_bytes().count(b"\r"), 0)
        self.assertEqual(leer_texto(self.home / ".config" / "starship.toml"), plantilla("starship.toml"))
        # Herdr: fuente, entrada git-bash con ruta corta, otros programas y keys.json intactos
        self.assertEqual(json.loads(leer_texto(self.rutas.herdr / "settings.json")),
                         {"zoom": 1, "font": FUENTE})
        prog = json.loads(leer_texto(self.rutas.herdr / "programs.json"))["programs"]
        self.assertIn("otro", prog)
        self.assertIn("PROGRA~1", prog["git-bash"]["run"][0])
        self.assertNotIn("\\", prog["git-bash"]["run"][0])
        self.assertEqual((self.rutas.herdr / "keys.json").read_bytes(), b'{"global": {}}\r\n')
        # fuentes en los dos sitios y en el registro
        for f in FUENTES:
            self.assertTrue((self.rutas.fuentes_usuario / f).exists())
            self.assertTrue((self.rutas.herdr / "fonts" / f).exists())
        self.assertEqual(len(self.sis.reg), 2)
        # VS Code: comentario y CRLF conservados, valores puestos
        crudo = self.rutas.vscode_settings.read_bytes()
        self.assertIn(b"// mi comentario", crudo)
        self.assertIn(b"\r\n", crudo)
        vs = jsonc_cargar(leer_texto(self.rutas.vscode_settings))
        self.assertEqual(vs["terminal.integrated.defaultProfile.windows"], "Git Bash")
        self.assertEqual(vs["terminal.integrated.profiles.windows"]["Git Bash"]["args"], ["--login", "-i"])
        self.assertNotIn("\\", vs["terminal.integrated.profiles.windows"]["Git Bash"]["path"])
        self.assertEqual(vs["editor.fontFamily"], "Cascadia Code")
        self.assertTrue((self.rutas.menu_inicio / LNK).exists())

        # segunda vez: nada cambia, no hay descargas nuevas
        antes = {p: p.read_bytes() for p in self.home.rglob("*") if p.is_file()}
        registro = c.instalar(self.rutas, self.sis, self.ui)
        self.assertTrue(all("ya estaba" in r for r in registro), registro)
        despues = {p: p.read_bytes() for p in self.home.rglob("*") if p.is_file()}
        self.assertEqual(antes, despues)
        self.assertEqual(self.sis.descargas, 1)

    def test_mintty_existente_se_fusiona(self):
        self.preparar()
        (self.home / ".minttyrc").write_text("Font=Consolas\nScrollbar=none\n")
        Starship().instalar(self.rutas, self.sis, self.ui)
        rc = leer_texto(self.home / ".minttyrc")
        self.assertIn("Scrollbar=none", rc)
        self.assertIn(f"Font={FUENTE}", rc)
        self.assertNotIn("Consolas", rc)

    def test_sin_herdr_ni_vscode_avisa_y_omite(self):
        self.sis.programas -= {"herdr-app", "code"}
        registro = Starship().instalar(self.rutas, self.sis, self.ui)
        self.assertTrue(self.ui.avisos)
        self.assertIn("Herdr", self.ui.avisos[0])
        self.assertEqual(sum("omitido" in r for r in registro), 2)
        self.assertFalse(self.rutas.herdr.exists())
        self.assertTrue(Starship().estado(self.rutas, self.sis).completo)

    def test_cancelar_si_faltan_programas(self):
        self.sis.programas.discard("code")
        self.ui.respuesta = False
        self.assertEqual(Starship().instalar(self.rutas, self.sis, self.ui), ["cancelado"])
        self.assertFalse((self.home / ".bashrc").exists())


if __name__ == "__main__":
    unittest.main()
