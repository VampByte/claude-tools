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
from installer.componentes.terceros import terceros


class SistemaFalso:
    def __init__(self, git_root: Path, programas=("git", "herdr-app", "code", "claude", "winget")):
        self.git_root = git_root
        self.programas = set(programas)
        self.llamadas, self.reg, self.descargas = [], {}, 0
        self.instala_tercero, self.home_falso = False, ""

    def which(self, nombre):
        if nombre not in self.programas:
            return None
        if nombre == "git":
            return str(self.git_root / "cmd" / "git.exe")
        return f"/bin/{nombre}"

    def run(self, cmd):
        self.llamadas.append(cmd)
        if cmd[0] == "winget":
            (self.programas.discard if cmd[1] == "uninstall" else self.programas.add)("starship")
        if cmd[0] == "powershell.exe":  # simula el acceso directo
            ruta = cmd[-1].split("CreateShortcut('")[1].split("')")[0]
            Path(ruta).write_bytes(b"lnk")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    def run_interactivo(self, cmd):
        self.llamadas.append(cmd)
        if self.instala_tercero:  # simula que Claude Code dejó la skill instalada
            carpeta = Path(self.home_falso) / ".claude" / "skills" / "hallmark"
            carpeta.mkdir(parents=True)
            (carpeta / "SKILL.md").write_text("---\nname: hallmark\n---\n")
        return 0

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

    def reg_fuente_borrar(self, nombre):
        self.reg.pop(nombre, None)


class InterfazFalsa:
    def __init__(self, respuesta=True, elegir=None):
        self.respuesta, self.avisos, self.elegir, self.ofrecido = respuesta, [], elegir, []

    def avisar(self, msg):
        self.avisos.append(msg)

    def seleccionar(self, titulo, opciones):
        self.ofrecido = opciones
        return list(range(len(opciones))) if self.elegir is None else self.elegir

    def confirmar(self, msg):
        return self.respuesta


class _Cancela(InterfazFalsa):
    def seleccionar(self, titulo, opciones):
        return None


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
        self.assertEqual(c.estado(self.rutas, self.sis).hecho, 5)
        c.instalar(self.rutas, self.sis, self.ui)
        self.assertTrue(c.estado(self.rutas, self.sis).completo)
        respaldo = self.rutas.backup_dir / ".config" / "opencode" / "skills" / "humanizador" / "SKILL.md"
        self.assertEqual(respaldo.read_text(), "editada")

    def test_instala_solo_las_elegidas(self):
        c = SkillsClaude()
        ui = InterfazFalsa(elegir=[1, 2])  # humanizador y jsk-opencode
        registro = c.instalar(self.rutas, self.sis, ui)
        self.assertEqual(len(registro), 2)
        self.assertTrue((self.rutas.claude_skills / "humanizador").exists())
        self.assertFalse((self.rutas.claude_skills / "entrevistador-procesos").exists())
        self.assertEqual(c.estado(self.rutas, self.sis).hecho, 2)

    def test_ofrece_el_estado_de_cada_skill(self):
        c = SkillsClaude()
        c.instalar(self.rutas, self.sis, InterfazFalsa(elegir=[0]))
        (self.rutas.claude_skills / "entrevistador-procesos" / "SKILL.md").write_text("editada")
        ui = InterfazFalsa(elegir=[])
        c.instalar(self.rutas, self.sis, ui)
        self.assertIn("difiere del repo", ui.ofrecido[0])
        self.assertIn("no instalada", ui.ofrecido[1])

    def test_cancelar_no_toca_nada(self):
        registro = SkillsClaude().instalar(self.rutas, self.sis, _Cancela())
        self.assertEqual(registro, ["cancelado"])
        self.assertFalse(self.rutas.claude_skills.exists())

    def test_opencode_no_lleva_jsk_opencode(self):
        self.assertNotIn("jsk-opencode", SkillsOpencode().skills)
        self.assertEqual(len(SkillsOpencode().skills), 6)
        self.assertEqual(len(SkillsClaude().skills), 7)


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


class TercerosTest(Base):
    def test_lanza_claude_con_el_prompt_del_repo(self):
        self.sis.instala_tercero, self.sis.home_falso = True, self.home
        hallmark = terceros()[0]
        self.assertFalse(hallmark.estado(self.rutas, self.sis).completo)
        registro = hallmark.instalar(self.rutas, self.sis, self.ui)
        cmd = self.sis.llamadas[0]
        self.assertEqual(cmd[0], "/bin/claude")
        self.assertIn("https://github.com/Nutlope/hallmark", cmd[1])
        self.assertIn("instalada", registro[0])
        self.assertTrue(hallmark.estado(self.rutas, self.sis).completo)

    def test_si_ya_esta_no_lanza_nada(self):
        carpeta = self.rutas.claude_skills / "impeccable"
        carpeta.mkdir(parents=True)
        (carpeta / "SKILL.md").write_text("x")
        impeccable = terceros()[1]
        self.assertEqual(impeccable.instalar(self.rutas, self.sis, self.ui), ["impeccable: ya estaba"])
        self.assertEqual(self.sis.llamadas, [])

    def test_avisa_si_no_quedo_instalada(self):
        registro = terceros()[0].instalar(self.rutas, self.sis, self.ui)
        self.assertIn("no se detectó", registro[0])

    def test_sin_claude_falla_con_mensaje(self):
        self.sis.programas.discard("claude")
        self.assertEqual(terceros()[0].requisitos(self.sis), ["claude"])
        with self.assertRaises(RuntimeError):
            terceros()[0].instalar(self.rutas, self.sis, self.ui)


class DesinstalarTest(Base):
    def test_skills_solo_las_elegidas_y_con_backup(self):
        c = SkillsClaude()
        c.instalar(self.rutas, self.sis, self.ui)
        registro = c.desinstalar(self.rutas, self.sis, InterfazFalsa(elegir=[0, 1]))
        self.assertEqual(len(registro), 2)
        self.assertFalse((self.rutas.claude_skills / "entrevistador-procesos").exists())
        self.assertFalse((self.rutas.claude_skills / "humanizador").exists())
        self.assertTrue((self.rutas.claude_skills / "jsk-opencode" / "SKILL.md").exists())
        respaldo = self.rutas.backup_dir / ".claude" / "skills" / "humanizador" / "SKILL.md"
        self.assertTrue(respaldo.exists())

    def test_skills_sin_nada_instalado_o_cancelando(self):
        c = SkillsClaude()
        self.assertIn("no hay skills", c.desinstalar(self.rutas, self.sis, self.ui)[0])
        c.instalar(self.rutas, self.sis, self.ui)
        self.assertEqual(c.desinstalar(self.rutas, self.sis, _Cancela()), ["cancelado"])
        self.assertTrue(c.estado(self.rutas, self.sis).completo)

    def test_tercero_borra_su_carpeta_con_backup(self):
        carpeta = self.rutas.claude_skills / "hallmark"
        carpeta.mkdir(parents=True)
        (carpeta / "SKILL.md").write_text("x")
        registro = terceros()[0].desinstalar(self.rutas, self.sis, self.ui)
        self.assertIn("desinstalada", registro[0])
        self.assertFalse(carpeta.exists())
        self.assertTrue((self.rutas.backup_dir / ".claude" / "skills" / "hallmark" / "SKILL.md").exists())
        self.assertIn("no estaba", terceros()[0].desinstalar(self.rutas, self.sis, self.ui)[0])

    def test_clean_view_quita_plugin_y_marketplace(self):
        p = self.rutas.claude_plugins
        p.mkdir(parents=True)
        (p / "known_marketplaces.json").write_text('{"claude-tools": {}}')
        (p / "installed_plugins.json").write_text('{"plugins": {"clean-view@claude-tools": []}}')
        CleanView().desinstalar(self.rutas, self.sis, self.ui)
        self.assertEqual([c[1:] for c in self.sis.llamadas],
                         [["plugin", "uninstall", "clean-view@claude-tools", "--scope", "user"],
                          ["plugin", "marketplace", "remove", "claude-tools"]])

    def test_clean_view_no_instalado_no_llama_a_claude(self):
        self.assertIn("no estaba", CleanView().desinstalar(self.rutas, self.sis, self.ui)[0])
        self.assertEqual(self.sis.llamadas, [])


class DesinstalarStarshipTest(Base):
    VSCODE = '{\n    // mi comentario\n    "editor.fontFamily": "Cascadia Code",\n}\n'

    def instalado(self):
        self.rutas.herdr.mkdir(parents=True)
        (self.rutas.herdr / "settings.json").write_text('{\n  "zoom": 1,\n  "font": "Cascadia Code"\n}\n')
        (self.rutas.herdr / "programs.json").write_text('{"programs": {"otro": {"name": "Otro", "run": ["x"]}}}')
        self.rutas.vscode_settings.parent.mkdir(parents=True)
        self.rutas.vscode_settings.write_text(self.VSCODE)
        (self.rutas.localappdata / "Microsoft" / "WinGet" / "Packages" / "Starship.Starship_x").mkdir(parents=True)
        c = Starship()
        c.instalar(self.rutas, self.sis, self.ui)
        return c

    def test_quita_todo_y_conserva_lo_ajeno(self):
        c = self.instalado()
        registro = c.desinstalar(self.rutas, self.sis, self.ui)
        self.assertFalse(any("ERROR" in r for r in registro), registro)
        self.assertFalse((self.home / ".bashrc").exists())
        self.assertFalse((self.home / ".config" / "starship.toml").exists())
        self.assertFalse((self.home / ".minttyrc").exists())
        self.assertFalse((self.rutas.menu_inicio / LNK).exists())
        for f in FUENTES:
            self.assertFalse((self.rutas.fuentes_usuario / f).exists())
            self.assertFalse((self.rutas.herdr / "fonts" / f).exists())
        self.assertEqual(self.sis.reg, {})
        self.assertIn(["winget", "uninstall", "--id", "Starship.Starship", "--exact", "--silent",
                       "--disable-interactivity"], self.sis.llamadas)
        # Herdr: vuelve la fuente anterior (estaba en la copia de seguridad) y se conserva "otro"
        self.assertEqual(json.loads(leer_texto(self.rutas.herdr / "settings.json")),
                         {"zoom": 1, "font": "Cascadia Code"})
        self.assertEqual(list(json.loads(leer_texto(self.rutas.herdr / "programs.json"))["programs"]), ["otro"])
        # VS Code: queda lo ajeno, con su comentario, y sin las claves del instalador
        vs = leer_texto(self.rutas.vscode_settings)
        self.assertEqual(jsonc_cargar(vs), {"editor.fontFamily": "Cascadia Code"})
        self.assertIn("// mi comentario", vs)

    def test_archivo_de_shell_modificado_no_se_borra(self):
        c = self.instalado()
        with open(self.home / ".bashrc", "a") as f:
            f.write("export MIO=1\n")
        registro = c.desinstalar(self.rutas, self.sis, self.ui)
        self.assertTrue((self.home / ".bashrc").exists())
        self.assertTrue(any("tiene cambios tuyos" in r for r in registro), registro)
        self.assertFalse((self.home / ".bash_profile").exists())

    def test_elegir_solo_algunas_partes(self):
        c = self.instalado()
        ui = InterfazFalsa(elegir=[1])  # solo "Acceso directo" (la 2.ª de la lista inversa)
        c.desinstalar(self.rutas, self.sis, ui)
        self.assertFalse((self.rutas.menu_inicio / LNK).exists())
        self.assertTrue((self.home / ".bashrc").exists())
        self.assertEqual(ui.ofrecido[0].split(":")[0], "VS Code")

    def test_mintty_con_claves_propias_conserva_el_resto(self):
        c = self.instalado()
        with open(self.home / ".minttyrc", "a") as f:
            f.write("Columns=140\n")
        c.desinstalar(self.rutas, self.sis, InterfazFalsa(elegir=[2]))  # mintty
        self.assertEqual(leer_texto(self.home / ".minttyrc").strip(), "Columns=140")

    def test_sin_nada_instalado(self):
        self.assertIn("nada", Starship().desinstalar(self.rutas, self.sis, self.ui)[0])


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
