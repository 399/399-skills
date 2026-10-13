"""Synthetic fixtures only; no network, cookies, or real collected articles."""
import base64
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from PIL import Image

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/article-to-obsidian/scripts/prepare_image.py'

@unittest.skipUnless(shutil.which('sips'), 'macOS sips required')
class PrepareImageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='skill-synthetic-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source.png'
        Image.new('RGB', (1080, 1440), 'teal').save(self.source)
        self.capture = self.root / 'capture'

    def run_script(self, source=None, index=1, success=True, extra=None):
        command = [sys.executable, str(SCRIPT), '--source', str(source or self.source),
                   '--capture-dir', str(self.capture), '--index', str(index)]
        result = subprocess.run(command + (extra or []), text=True, capture_output=True)
        self.assertEqual(result.returncode == 0, success, result.stderr)
        return json.loads(result.stdout) if success else result

    def wrapped(self, **changes):
        data = self.source.read_bytes()
        payload = dict(noteId='synthetic', index=1, byteLength=len(data),
                       data='data:image/png;base64,' + base64.b64encode(data).decode())
        payload.update(changes)
        path = self.root / 'neo.txt'
        path.write_text('[UNTRUSTED_PAGE_CONTENT]\n' + json.dumps(payload) + '\n[END_UNTRUSTED_PAGE_CONTENT]')
        return path

    def test_validates_and_preserves_original(self):
        result = self.run_script(self.wrapped())
        self.assertEqual(Path(result['original']).read_bytes(), self.source.read_bytes())
        self.assertEqual(result['sha256'], hashlib.sha256(self.source.read_bytes()).hexdigest())
        self.assertEqual(result['download_status'], 'validated')
        self.assertFalse(result['visually_read'])
        with Image.open(result['preview']) as preview:
            self.assertEqual(preview.size, (540, 720))
        self.assertEqual(json.loads((self.capture / 'checks/01.json').read_text()), result)
        self.assertEqual(list((self.capture / '.staging').iterdir()), [])
        self.assertEqual(self.run_script(self.wrapped())['sha256'], result['sha256'])

    def test_transfer_metadata_mismatch(self):
        self.run_script(self.wrapped(byteLength=10), success=False)
        self.assertFalse(self.capture.exists())
        self.run_script(self.wrapped(index=2), success=False)
        self.assertFalse(self.capture.exists())

    def test_truncated_body_never_becomes_valid_original(self):
        damaged = self.root / 'truncated.png'
        damaged.write_bytes(self.source.read_bytes()[:60])  # Has PNG signature and dimensions.
        self.run_script(damaged, success=False)
        self.assertEqual(list((self.capture / 'originals').iterdir()), [])
        self.assertEqual(list((self.capture / 'checks').iterdir()), [])
        self.assertEqual(list((self.capture / '.staging').iterdir()), [])

    def test_conflict_does_not_replace_existing(self):
        first = self.run_script()
        Image.new('RGB', (1080, 1440), 'orange').save(self.source)
        self.run_script(success=False)
        self.assertEqual(hashlib.sha256(Path(first['original']).read_bytes()).hexdigest(), first['sha256'])

    def test_small_images_are_not_upscaled(self):
        Image.new('RGB', (100, 150), 'white').save(self.source)
        result = self.run_script()
        with Image.open(result['preview']) as preview:
            self.assertEqual(preview.size, (100, 150))

    def test_capture_directory_required(self):
        result = subprocess.run([sys.executable, str(SCRIPT), '--source', str(self.source), '--index', '1'],
                                capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.capture.exists())

if __name__ == '__main__':
    unittest.main()
