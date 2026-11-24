import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from check_script_cli import inspect_script  # noqa: E402
from validate_schema import (  # noqa: E402
    main as validate_main,
    render_script_document_text,
    validate_benchmark,
    validate_inspection_report,
    validate_script_document,
)


class SchemaAndBenchmarkTests(unittest.TestCase):
    def test_good_script_json_validates_and_renders_to_zero_issues(self):
        doc = json.loads((ROOT / "examples" / "good_ai_manju_ep1.json").read_text(encoding="utf-8"))
        self.assertEqual(validate_script_document(doc), [])
        rendered = render_script_document_text(doc)
        rep = inspect_script(rendered)
        self.assertEqual(rep["issue_count"], 0, rep["issues"])
        self.assertEqual(validate_inspection_report(rep), [])

    def test_bad_script_json_triggers_expected_errors(self):
        bad = json.loads((ROOT / "examples" / "bad_missing_fields.json").read_text(encoding="utf-8"))
        errors = validate_script_document(bad)
        joined = "\n".join(errors)
        self.assertIn("scene_no", joined)
        self.assertIn("interior_exterior", joined)
        self.assertIn("特写", joined)
        self.assertIn("神秘男子", joined)
        self.assertIn("speaker", joined)

    def test_benchmark_json_consistency_and_cli(self):
        bm_path = ROOT / "benchmarks" / "short-drama-rhythm-benchmark.json"
        bm = json.loads(bm_path.read_text(encoding="utf-8"))
        self.assertEqual(validate_benchmark(bm), [])
        self.assertEqual(validate_main([str(bm_path), "--benchmark"]), 0)

    def test_report_cli_mode_validates_check_output(self):
        good_text = (ROOT / "examples" / "good_ai_manju_ep1.txt").read_text(encoding="utf-8")
        rep = inspect_script(good_text)
        with tempfile.TemporaryDirectory() as tmp:
            rp = Path(tmp) / "rep.json"
            rp.write_text(json.dumps(rep, ensure_ascii=False), encoding="utf-8")
            self.assertEqual(validate_main([str(rp), "--report"]), 0)

    def test_repo_contains_zero_commercial_forbidden_words(self):
        forbidden = re.compile(r"\u5728\u552e|\u8d2d\u4e70|\u552e\u5356|\u00a5|\u5143")
        for p in sorted(ROOT.rglob("*")):
            if not p.is_file() or ".git" in p.parts or "__pycache__" in p.parts:
                continue
            txt = p.read_text(encoding="utf-8")
            self.assertFalse(
                forbidden.search(txt),
                f"{p.relative_to(ROOT)} hit forbidden words: {forbidden.findall(txt)}",
            )


if __name__ == "__main__":
    unittest.main()
