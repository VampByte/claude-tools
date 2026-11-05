import json
import tempfile
import unittest
from pathlib import Path

from installer.comun import Rutas, escribir, jsonc_cargar, jsonc_set, leer_texto


class JsoncTest(unittest.TestCase):
    BASE = '{\n    // comentario\n    "a": 1,\n    "url": "http://x//y",\n    "b": {"c": [1, 2]},\n}\n'

    def test_cargar_ignora_comentarios_y_coma_final(self):
        self.assertEqual(jsonc_cargar(self.BASE), {"a": 1, "url": "http://x//y", "b": {"c": [1, 2]}})

    def test_cargar_respeta_comas_dentro_de_strings(self):
        self.assertEqual(jsonc_cargar('{"a": ", }"}'), {"a": ", }"})

    def test_set_reemplaza_clave_existente_y_conserva_comentarios(self):
        t = jsonc_set(self.BASE, "a", "nuevo")
        self.assertIn("// comentario", t)
        self.assertEqual(jsonc_cargar(t)["a"], "nuevo")
        self.assertEqual(jsonc_cargar(t)["b"], {"c": [1, 2]})

    def test_set_reemplaza_objeto_anidado(self):
        t = jsonc_set(self.BASE, "b", {"d": True})
        self.assertEqual(jsonc_cargar(t)["b"], {"d": True})
        self.assertEqual(jsonc_cargar(t)["a"], 1)

    def test_set_reemplaza_ultima_clave_sin_coma(self):
        t = jsonc_set('{\n    "a": 1,\n    "z": [1, 2]\n}', "z", 5)
        self.assertEqual(jsonc_cargar(t), {"a": 1, "z": 5})

    def test_set_inserta_clave_nueva(self):
        t = jsonc_set(self.BASE, "nueva", ["x"])
        self.assertEqual(jsonc_cargar(t)["nueva"], ["x"])
        self.assertEqual(jsonc_cargar(t)["a"], 1)

    def test_set_en_objeto_vacio(self):
        self.assertEqual(jsonc_cargar(jsonc_set("{}", "k", 1)), {"k": 1})

    def test_set_sin_cambios_si_el_valor_es_igual(self):
        t = '{\n    "p": {"x": ["--login", "-i"]}\n}'
        self.assertEqual(jsonc_set(t, "p", {"x": ["--login", "-i"]}), t)

    def test_set_no_toca_claves_anidadas_con_el_mismo_nombre(self):
        t = jsonc_set('{"b": {"a": 1}, "a": 2}', "a", 3)
        self.assertEqual(jsonc_cargar(t), {"b": {"a": 1}, "a": 3})


class EscribirTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)
        self.rutas = Rutas(home=self.home, appdata=self.home / "AppData/Roaming", localappdata=self.home / "AppData/Local")

    def tearDown(self):
        self.tmp.cleanup()

    def test_archivo_nuevo_se_crea_sin_backup(self):
        f = self.home / "dir" / "nuevo.txt"
        self.assertTrue(escribir(self.rutas, f, "hola\n"))
        self.assertEqual(f.read_bytes(), b"hola\n")
        self.assertFalse(self.rutas.backup_dir.exists())

    def test_conserva_crlf_y_hace_backup(self):
        f = self.home / "a.json"
        f.write_bytes(b"{\r\n}\r\n")
        self.assertTrue(escribir(self.rutas, f, '{\n"x": 1\n}\n'))
        self.assertEqual(f.read_bytes(), b'{\r\n"x": 1\r\n}\r\n')
        self.assertEqual((self.rutas.backup_dir / "a.json").read_bytes(), b"{\r\n}\r\n")

    def test_forzar_lf(self):
        f = self.home / ".bashrc"
        f.write_bytes(b"viejo\r\n")
        escribir(self.rutas, f, "nuevo\n", forzar_lf=True)
        self.assertEqual(f.read_bytes(), b"nuevo\n")

    def test_sin_cambios_no_escribe_ni_hace_backup(self):
        f = self.home / "a.txt"
        f.write_bytes(b"igual\r\n")
        self.assertFalse(escribir(self.rutas, f, "igual\n"))
        self.assertFalse(self.rutas.backup_dir.exists())

    def test_conserva_bom(self):
        f = self.home / "b.json"
        f.write_bytes(b"\xef\xbb\xbf{}\n")
        self.assertEqual(leer_texto(f), "{}\n")
        escribir(self.rutas, f, '{"a": 1}\n')
        self.assertTrue(f.read_bytes().startswith(b"\xef\xbb\xbf"))
        self.assertEqual(json.loads(leer_texto(f)), {"a": 1})

    def test_backup_vive_en_el_perfil(self):
        self.assertEqual(self.rutas.backup_dir.parent, self.home / ".claude-tools-backup")


if __name__ == "__main__":
    unittest.main()
