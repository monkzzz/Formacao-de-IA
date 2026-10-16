import re
import unittest

from digitlab.ftp_deploy import ROOT, deployment_order


class DeploymentOrderTests(unittest.TestCase):
    def test_changed_modules_follow_their_imported_dependencies_and_html_is_last(self):
        names = ["index.html", "v3/app.js", "v3/inference.js", "v3/preprocess.js",
                 "v3/helper.js", "v3/helper-knowledge.js", "v3/residual.js", "model/captcha-v2/digits/weights.bin"]
        paths = sorted((ROOT / "dist" / name for name in names), key=deployment_order)
        positions = {path: i for i, path in enumerate(paths)}
        self.assertEqual(paths[-1].name, "index.html")
        self.assertLess(positions[ROOT / "dist/model/captcha-v2/digits/weights.bin"],
                        positions[ROOT / "dist/v3/inference.js"])
        edges = 0
        for path in paths:
            if path.suffix != ".js":
                continue
            for module in re.findall(r'from\s+["\'](\./[^"\']+)["\']', path.read_text(encoding="utf-8")):
                dependency = (path.parent / module.split("?")[0]).resolve()
                if dependency in positions:
                    self.assertLess(positions[dependency], positions[path], module)
                    edges += 1
        self.assertGreaterEqual(edges, 4)
