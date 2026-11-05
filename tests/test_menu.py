import unittest

from installer.componentes import Estado
from installer.menu import Salir, elegir, linea


class ElegirTest(unittest.TestCase):
    def test_numeros(self):
        self.assertEqual(elegir("1 3", 4), [0, 2])

    def test_comas_repetidos_y_orden(self):
        self.assertEqual(elegir("3,1, 3", 4), [0, 2])

    def test_todo(self):
        self.assertEqual(elegir("todo", 4), [0, 1, 2, 3])
        self.assertEqual(elegir(" TODO ", 2), [0, 1])

    def test_salir(self):
        for t in ("q", "Q", "salir"):
            with self.assertRaises(Salir):
                elegir(t, 4)

    def test_invalidos(self):
        for t in ("", "0", "5", "a", "1 x"):
            with self.assertRaises(ValueError, msg=t):
                elegir(t, 4)


class LineaTest(unittest.TestCase):
    def test_marca_y_requisitos(self):
        self.assertIn("[x]", linea(1, "Skills", Estado(6, 6), []))
        l = linea(4, "Starship", Estado(2, 7), ["Herdr"])
        self.assertIn("[ ]", l)
        self.assertIn("2 de 7", l)
        self.assertIn("falta: Herdr", l)


if __name__ == "__main__":
    unittest.main()
