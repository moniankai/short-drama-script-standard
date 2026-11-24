#!/usr/bin/env python3
"""竖屏短剧与 AI 漫剧文字台本格式、小说腔与节奏自检命令行工具（零依赖·MIT）。

在线完整体检与实时全库基准对照：https://52juben.com/show/tools/
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import sys

SCENE_RE = re.compile(
    r"^【\s*(?P<ep>\d+)\s*[-－—]\s*(?P<scene>\d+)\s+(?P<body>[^】]+)】$"
)
EP_SPLIT_RE = re.compile(r"^\s*(?:第\s*(?P<num>\d+)\s*集|EP\s*(?P<ep>\d+))\b", re.I)
DIALOGUE_RE = re.compile(
    r"^(?P<name>[^△【\s（：:]{1,15}?)(?:\s*(?P<aside>OS|VO))?(?:（(?P<emo>[^（）]{1,12})）)?：(?P<text>.*)$"
)
CAPTION_RE = re.compile(r"^△?【字幕[：:](?P<inner>[^】]+)】")
TIME_CAPTION_RE = re.compile(
    r"(次日|翌日|转天|第\S+?[天日]|当夜|当晚|清晨|凌晨|早[上天]|上午|中午|午后|傍晚|黄昏|深夜|半夜|"
    r"[一二两三四五六七八九十几数半\d]+\s*(秒|分|小时|天|日|周|月|年|个时辰)|原世界|现代|过去|未来)"
)
FAKE_CAPTION_RE = re.compile(r"叮|系统|弹幕|弹窗|到账|账户|转账|余额|微信|^[^：:，。！？\s]{1,12}[：:]")
CLICHE_RE = re.compile(
    r"指节|瞳孔|指尖(?:敲|叩|点|蹭|摩挲|抠|掐|捏|发颤|颤|抖|收紧|泛白|一顿|一紧|一僵)"
    r"|嘴张着|张着嘴|张了张嘴|嘴唇(?:动|抖|颤|哆嗦)|得像冰|得像水|得能滴出水"
)
MENTAL_RE = re.compile(
    r"脑海(?:中|里)?(?:却)?(?:突然|反复)?(?:闪过|闪现|浮现|响起|回荡)"
    r"|脑中(?:飞速)?(?:盘算|思索|闪过|浮现)"
)
LITERARY_RE = re.compile(
    r"寒光凛冽|锋芒毕露|生人勿近|嘴角勾起一抹|眼底闪过一丝|如尖刺|如惊雷|宛如神明"
)
UNNAMED_REF_RE = re.compile(
    r"(?:一名|一个|一位)(?:身着|穿着|蒙面)?[^，。；\s]{1,8}(?:男子|女子|少年|少女|老者|大汉|妇人)"
    r"|神秘(?:男子|女子|少年|老者)"
)
SILENCE_RE = re.compile(
    r"没说话|没接话|没吭声|没作声|没应声|没答话|没吱声|没回答|没开口|不说话|沉默不语|一言不发|说不出话"
)
ANCIENT_RE = re.compile(
    r"三息|一息|半息|须臾|且慢|顷刻|莫要|休得|霎时|倘若|兀自|切莫|阁下|足下|旋即|不多时|三更|五更"
)
COMPOUND_RE = re.compile(r"与|及|、|^内外$|/|转|日至夜")

BENCHMARK = {
    "retrieved_at": "2026-11-24",
    "scenes_per_ep_median": 2,
    "dialogues_per_ep_p25": 9.0,
    "dialogues_per_ep_median": 13.0,
    "dialogues_per_ep_p75": 17.0,
    "avg_dialogue_len_median": 18.6,
    "emotion_pct_median": 44,
    "source_url": "https://52juben.com/show/stats/qa/",
}


def split_episodes(text: str) -> list[tuple[int, str]]:
    """按显式集头切分多集文本；单集则按首场集号或第 1 集处理。"""
    lines = (text or "").splitlines()
    buckets: list[tuple[int, list[str]]] = []
    current_ep: int | None = None
    buf: list[str] = []

    for line in lines:
        m_ep = EP_SPLIT_RE.match(line.strip())
        if m_ep:
            num = int(m_ep.group("num") or m_ep.group("ep"))
            if current_ep is not None and num != current_ep and buf:
                buckets.append((current_ep, buf))
                buf = []
            current_ep = num
        else:
            m_sc = SCENE_RE.match(line.strip())
            if m_sc:
                ep = int(m_sc.group("ep"))
                if current_ep is None:
                    current_ep = ep
                elif ep != current_ep and buf and any(SCENE_RE.match(x.strip()) for x in buf):
                    buckets.append((current_ep, buf))
                    buf = []
                    current_ep = ep
        buf.append(line)

    if buf:
        buckets.append((current_ep or 1, buf))
    return [(ep, "\n".join(chunk)) for ep, chunk in buckets]


def _adjacent_duplicate_blocks(non_empty: list[tuple[int, str]]) -> list[tuple[int, str]]:
    texts = [line for _, line in non_empty]
    positions: dict[str, list[int]] = defaultdict(list)
    for idx, line in enumerate(texts):
        positions[line].append(idx)
    n = len(texts)
    found: list[tuple[int, str]] = []
    for start, line in enumerate(texts):
        for second in positions[line]:
            size = second - start
            if size < 2 or second + size > n:
                continue
            if all(texts[start + off] == texts[second + off] for off in range(1, size)):
                found.append((non_empty[second][0], "\n".join(texts[start:second])))
                break
    return found


def check_episode(ep_no: int, body: str) -> tuple[dict, list[dict]]:
    lines = body.splitlines()
    issues: list[dict] = []
    non_empty: list[tuple[int, str]] = []
    scenes = 0
    dialogues = 0
    dlg_chars = 0
    emo_count = 0
    cast: list[str] = []

    for idx, raw in enumerate(lines):
        s = raw.strip()
        if not s:
            continue
        if non_empty and non_empty[-1][1] == s:
            issues.append(
                {
                    "ep_no": ep_no,
                    "line_no": idx + 1,
                    "category": "相邻重复行",
                    "severity": "error",
                    "quote": s,
                    "tip": "相邻非空行完全重复，请检查是否重复粘贴。",
                }
            )
        non_empty.append((idx + 1, s))

        m_sc = SCENE_RE.match(s)
        if m_sc:
            scenes += 1
            cast = []
            sc_ep = int(m_sc.group("ep"))
            sc_no = int(m_sc.group("scene"))
            if sc_ep != ep_no:
                issues.append(
                    {
                        "ep_no": ep_no,
                        "line_no": idx + 1,
                        "category": "场头集号不符",
                        "severity": "warn",
                        "quote": s,
                        "tip": f"场头标注为第 {sc_ep} 集，当前位于第 {ep_no} 集区间。",
                    }
                )
            if sc_no != scenes:
                issues.append(
                    {
                        "ep_no": ep_no,
                        "line_no": idx + 1,
                        "category": "场号不连贯",
                        "severity": "warn",
                        "quote": s,
                        "tip": f"按顺序应为第 {scenes} 场，实际标注为第 {sc_no} 场。",
                    }
                )
            if COMPOUND_RE.search(m_sc.group("body")):
                issues.append(
                    {
                        "ep_no": ep_no,
                        "line_no": idx + 1,
                        "category": "复合场头",
                        "severity": "warn",
                        "quote": s,
                        "tip": "场头应写单一地点、单一时段与单一内外景。",
                    }
                )
            continue

        if s.startswith("人物："):
            cast = [x.strip() for x in re.split(r"[、，,]", s[3:]) if x.strip()]
            continue

        if s.startswith("△"):
            m_cap = CAPTION_RE.match(s)
            if m_cap:
                inner = m_cap.group("inner").strip()
                if not TIME_CAPTION_RE.search(inner) and FAKE_CAPTION_RE.search(inner):
                    issues.append(
                        {
                            "ep_no": ep_no,
                            "line_no": idx + 1,
                            "category": "假字幕",
                            "severity": "warn",
                            "quote": s,
                            "tip": "手机消息、弹窗或到账提示不宜写成【字幕】，请改为普通动作行。",
                        }
                    )
            elif not s.startswith("△【特写】") and "特写" in s:
                issues.append(
                    {
                        "ep_no": ep_no,
                        "line_no": idx + 1,
                        "category": "特写未独立成行",
                        "severity": "warn",
                        "quote": s,
                        "tip": "AI 漫剧分镜中特写须按「△【特写】……」独立成行，避免缀在普通动作句中。",
                    }
                )
            if m_un := UNNAMED_REF_RE.search(s):
                issues.append(
                    {
                        "ep_no": ep_no,
                        "line_no": idx + 1,
                        "category": "人物指代不清",
                        "severity": "warn",
                        "quote": s,
                        "tip": f"出现悬念代指「{m_un.group(0)}」，请直写角色姓名以便分镜稳定出图。",
                    }
                )
            if m_lit := LITERARY_RE.search(s):
                issues.append(
                    {
                        "ep_no": ep_no,
                        "line_no": idx + 1,
                        "category": "文学修辞/抽象描写",
                        "severity": "warn",
                        "quote": s,
                        "tip": f"出现文学修辞「{m_lit.group(0)}」，请改写为可直接出图的客观动作、表情或道具变化。",
                    }
                )
            if m_cl := CLICHE_RE.search(s):
                issues.append(
                    {
                        "ep_no": ep_no,
                        "line_no": idx + 1,
                        "category": "套话微动作",
                        "severity": "warn",
                        "quote": s,
                        "tip": f"命中高频微动作套话「{m_cl.group(0)}」，建议改写为直接表情或道具动作。",
                    }
                )
            if m_mf := MENTAL_RE.search(s):
                issues.append(
                    {
                        "ep_no": ep_no,
                        "line_no": idx + 1,
                        "category": "脑内闪回/心理描写",
                        "severity": "warn",
                        "quote": s,
                        "tip": f"动作行含「{m_mf.group(0)}」难以直接出图，请改写为动作、对白或标准闪回场。",
                    }
                )
            if re.match(r"^△(?:【[^】]*】)?[他她](?!们)", s) and len(cast) >= 2:
                issues.append(
                    {
                        "ep_no": ep_no,
                        "line_no": idx + 1,
                        "category": "代词起句不清",
                        "severity": "warn",
                        "quote": s,
                        "tip": "同场有两名及以上角色时，动作行避免用「他/她」起句，请直写角色姓名。",
                    }
                )
            if SILENCE_RE.search(s):
                for nxt_raw in lines[idx + 1 :]:
                    nxt = nxt_raw.strip()
                    if not nxt:
                        continue
                    m_nxt = DIALOGUE_RE.match(nxt)
                    if m_nxt and m_nxt.group("name") != "人物" and not m_nxt.group("aside"):
                        speaker = m_nxt.group("name")
                        if s.startswith("△" + speaker):
                            issues.append(
                                {
                                    "ep_no": ep_no,
                                    "line_no": idx + 1,
                                    "category": "先沉默紧接开口",
                                    "severity": "warn",
                                    "quote": s,
                                    "tip": "刚写角色「没说话」紧接着本人又开口，建议删去前置停顿。",
                                }
                            )
                    break
            if m_anc := ANCIENT_RE.search(s):
                issues.append(
                    {
                        "ep_no": ep_no,
                        "line_no": idx + 1,
                        "category": "书面/文言套词",
                        "severity": "warn",
                        "quote": s,
                        "tip": f"出现「{m_anc.group(0)}」，请替换为自然口语。",
                    }
                )
            continue

        m_dlg = DIALOGUE_RE.match(s)
        if m_dlg and not EP_SPLIT_RE.match(s):
            speaker = m_dlg.group("name").strip()
            if "、" in speaker:
                issues.append(
                    {
                        "ep_no": ep_no,
                        "line_no": idx + 1,
                        "category": "多人顿号连写",
                        "severity": "warn",
                        "quote": s,
                        "tip": "多人发言建议改为「甲（与乙齐声）：」。",
                    }
                )
            if not m_dlg.group("aside"):
                dialogues += 1
                dlg_chars += len(m_dlg.group("text").strip())
                if m_dlg.group("emo"):
                    emo_count += 1
            if m_anc := ANCIENT_RE.search(m_dlg.group("text")):
                issues.append(
                    {
                        "ep_no": ep_no,
                        "line_no": idx + 1,
                        "category": "书面/文言套词",
                        "severity": "warn",
                        "quote": s,
                        "tip": f"台词中出现「{m_anc.group(0)}」，请替换为人物脱口而出的口语。",
                    }
                )

    if scenes == 0:
        issues.append(
            {
                "ep_no": ep_no,
                "line_no": 1,
                "category": "缺少标准场头",
                "severity": "error",
                "quote": non_empty[0][1] if non_empty else "",
                "tip": "未检测到【集-场 地点·时段·内外】格式场头。",
            }
        )

    for line_no, quote_block in _adjacent_duplicate_blocks(non_empty):
        issues.append(
            {
                "ep_no": ep_no,
                "line_no": line_no,
                "category": "相邻重复块",
                "severity": "error",
                "quote": quote_block,
                "tip": "连续多行动作或台词块重复，请清理多余副本。",
            }
        )

    stats = {
        "ep_no": ep_no,
        "chars": sum(len(s) for _, s in non_empty),
        "scenes": scenes,
        "dialogues": dialogues,
        "avg_dialogue_len": round(dlg_chars / dialogues, 1) if dialogues else 0.0,
        "emotion_pct": round(emo_count * 100 / dialogues) if dialogues else 0,
    }
    return stats, issues


def inspect_script(text: str) -> dict:
    episodes_data = []
    all_issues = []
    for ep_no, body in split_episodes(text):
        ep_stats, ep_issues = check_episode(ep_no, body)
        episodes_data.append(ep_stats)
        all_issues.extend(ep_issues)
    ep_count = len(episodes_data) or 1
    avg_scenes = round(sum(e["scenes"] for e in episodes_data) / ep_count, 1)
    avg_dlgs = round(sum(e["dialogues"] for e in episodes_data) / ep_count, 1)
    return {
        "episode_count": len(episodes_data),
        "scenes_per_ep": avg_scenes,
        "dialogues_per_ep": avg_dlgs,
        "issue_count": len(all_issues),
        "benchmark": BENCHMARK,
        "episodes": episodes_data,
        "issues": all_issues,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="竖屏短剧与 AI 漫剧台本格式与节奏自检工具（完整网页版见 https://52juben.com/show/tools/）"
    )
    parser.add_argument("path", help="台本纯文本文件路径（UTF-8）")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出结果")
    args = parser.parse_args(argv)
    content = Path(args.path).read_text(encoding="utf-8")
    report = inspect_script(content)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    print(
        f"共检查 {report['episode_count']} 集 | 平均 {report['scenes_per_ep']} 场/集 "
        f"(公开样本中位 {BENCHMARK['scenes_per_ep_median']} 场) | "
        f"平均 {report['dialogues_per_ep']} 句台词/集 "
        f"(P25-P75: {BENCHMARK['dialogues_per_ep_p25']}-{BENCHMARK['dialogues_per_ep_p75']} 句) | "
        f"发现问题 {report['issue_count']} 条"
    )
    for item in report["issues"]:
        print(
            f"- 第{item['ep_no']}集 第{item['line_no']}行 [{item['severity']}:{item['category']}] "
            f"{item['tip']} | 原文：{item['quote']}"
        )
    print("\n更多完整规则体检与实时数据参照：https://52juben.com/show/tools/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
