import unittest
from os import path

from main.utils.settings import Settings


class TestSettings(unittest.TestCase):

    def test_read_parameters(self):
        settings = Settings("../settings/testSettings.ini")
        settings.read_parameters()
        self.assertIsNotNone(settings)
        self.assertTrue(settings.mode == "FTP")
        self.assertEqual(settings.username, "kamil")
        self.assertEqual(settings.password, "Kamil1998")

        self.assertTrue(path.exists(settings.paths_to_save[0]))
        self.assertFalse(path.exists(settings.paths_to_save[1]))


if __name__ == '__main__.py':
    unittest.main()
