"""Keep the standalone README aligned with the supported adapter contract."""
from pathlib import Path
import unittest


class DocumentationTests(unittest.TestCase):
    def test_readme_covers_backends_and_verified_limits(self):
        source = (Path(__file__).resolve().parents[1] / 'README.md').read_text(encoding='utf-8')
        for text in ('tekscope-mso2', 'tekscope-mso6', 'C:/baldee', '8,000 bytes',
                     '131,072 points', '250 MS/s', '25 MHz', '100,000 points',
                     'install.py --adapter tekscope', 'python -m python_bridge --idn 192.168.128.233'):
            self.assertIn(text, source)
        self.assertRegex(source, r'MSO6[\s\S]*hardware validation')
        self.assertTrue((Path(__file__).resolve().parents[1] / 'skills/tekscope-file-commands/SKILL.md').is_file())
