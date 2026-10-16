import hashlib
import io
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from serve import prepare_models


class ModelSetupTests(unittest.TestCase):
    def setUp(self):
        self.data = b"release weights"
        self.manifest = json.dumps({
            "bytes": len(self.data),
            "sha256": hashlib.sha256(self.data).hexdigest(),
        })
        for target, options in [
            ("pathlib.Path.read_text", {"return_value": self.manifest}),
            ("pathlib.Path.exists", {"return_value": False}),
        ]:
            mock = patch(target, **options)
            mock.start()
            self.addCleanup(mock.stop)

    def test_missing_models_print_setup_command_without_network(self):
        with patch("serve.urlopen") as request, patch("builtins.print") as output:
            prepare_models(Path("dist"))
        request.assert_not_called()
        output.assert_any_call("Run: python serve.py --download-models", flush=True)

    def test_verified_downloads_are_written_for_both_modes(self):
        with patch("serve.urlopen", side_effect=lambda *a, **k: io.BytesIO(self.data)), \
                patch.object(Path, "write_bytes") as write, \
                patch.object(Path, "replace") as replace:
            prepare_models(Path("dist"), download=True)
        self.assertEqual(write.call_count, 2)
        write.assert_called_with(self.data)
        self.assertEqual(replace.call_count, 2)

    def test_wrong_hash_or_size_never_writes_weights(self):
        for data in (b"x" * len(self.data), self.data + b"x"):
            with self.subTest(data=data), \
                    patch("serve.urlopen", return_value=io.BytesIO(data)), \
                    patch.object(Path, "write_bytes") as write:
                with self.assertRaisesRegex(ValueError, "do not match"):
                    prepare_models(Path("dist"), download=True)
                write.assert_not_called()
