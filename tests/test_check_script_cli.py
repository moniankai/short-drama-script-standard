import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from check_script_cli import check_episode, inspect_script, main, split_episodes


class CheckScriptCliTests(unittest.TestCase):
    def test_detects_novelese_duplicates_and_missing_heading(self):
        bad = (
            "第1集\n"
            "△他没有说话。\n"
            "\n"
            "【1-1 办公室·日·内】\n"
            "人物：陈默、周宁\n"
            "△他指节泛白，脑海中闪过昨夜的一幕，没说话。\n"
            "△他指节泛白，脑海中闪过昨夜的一幕，没说话。\n"
            "△陈默没说话。\n"
            "陈默：签字吧。\n"
        )
        rep = inspect_script(bad)
        cats = {item["category"] for item in rep["issues"]}
        self.assertIn("相邻重复行", cats)
        self.assertIn("套话微动作", cats)
        self.assertIn("脑内闪回/心理描写", cats)
        self.assertIn("代词起句不清", cats)
        self.assertIn("先沉默紧接开口", cats)

    def test_splits_multiple_episodes_and_computes_rhythm(self):
        two_eps = (
            "第1集\n"
            "【1-1 客厅·夜·内】\n"
            "人物：林岚、顾川\n"
            "△林岚把钥匙扔在茶几上。\n"
            "林岚（冷声）：今晚必须说清楚。\n"
            "顾川（低声）：我没动过那份合同。\n"
            "\n"
            "第2集\n"
            "【2-1 公司走廊·日·内】\n"
            "人物：林岚、助理\n"
            "△【特写】林岚手机屏幕亮起一条转账回执。\n"
            "助理：林总，财务室门锁了。\n"
        )
        eps = split_episodes(two_eps)
        self.assertEqual([ep for ep, _ in eps], [1, 2])
        rep = inspect_script(two_eps)
        self.assertEqual(rep["episode_count"], 2)
        self.assertEqual(rep["scenes_per_ep"], 1.0)
        self.assertEqual(rep["dialogues_per_ep"], 1.5)
        self.assertEqual(rep["issue_count"], 0)

    def test_cli_json_output_runs_cleanly(self):
        sample = "第1集\n△纯对白缺场头。\n甲：你好。\n"
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "sample.txt"
            p.write_text(sample, encoding="utf-8")
            rc = main([str(p), "--json"])
        self.assertEqual(rc, 0)
        stats, issues = check_episode(1, sample)
        self.assertEqual(stats["scenes"], 0)
        self.assertTrue(any(i["category"] == "缺少标准场头" for i in issues))


if __name__ == "__main__":
    unittest.main()
