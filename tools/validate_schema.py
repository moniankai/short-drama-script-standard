#!/usr/bin/env python3
"""竖屏短剧与 AI 漫剧结构化 JSON Schema 校验与文本渲染工具（零依赖·MIT）。

支持校验：
1. 结构化台本 JSON（对照 schemas/script-document.schema.json + 分场/角色/AI 漫剧纯视听规则）
2. check_script_cli.py --json 产出的体检报告（对照 schemas/inspection-report.schema.json）
3. benchmarks/short-drama-rhythm-benchmark.json 统计指标一致性
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

from check_script_cli import CLICHE_RE, LITERARY_RE, MENTAL_RE, UNNAMED_REF_RE, inspect_script

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_SCHEMA_PATH = ROOT / "schemas" / "script-document.schema.json"
REPORT_SCHEMA_PATH = ROOT / "schemas" / "inspection-report.schema.json"

ALLOWED_TIMES = {"日", "夜", "晨", "昏", "黄昏", "凌晨", "傍晚"}
ALLOWED_IE = {"内", "外"}
ALLOWED_LINE_KINDS = {"action", "closeup", "caption", "dialogue", "os", "vo"}
ALLOWED_FORMAT_MODES = {"ai_manju", "live_action"}
FORBIDDEN_TERMS_RE = re.compile(r"\u5728\u552e|\u8d2d\u4e70|\u552e\u5356|\u00a5|\u5143")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _check_forbidden_terms(obj: object, prefix: str, errors: list[str]) -> None:
    if isinstance(obj, str):
        hits = FORBIDDEN_TERMS_RE.findall(obj)
        if hits:
            errors.append(f"{prefix}: 命中禁用词 {hits}")
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            _check_forbidden_terms(item, f"{prefix}[{idx}]", errors)
    elif isinstance(obj, dict):
        for key, val in obj.items():
            _check_forbidden_terms(val, f"{prefix}.{key}", errors)


def validate_script_document(doc: object) -> list[str]:
    """校验结构化台本 JSON 是否满足 script-document.schema.json 及视听规则。"""
    errors: list[str] = []
    if not isinstance(doc, dict):
        return ["root: 顶层必须是 JSON 对象"]

    allowed_root = {"schema_version", "title", "format_mode", "genre", "episodes"}
    extra_root = set(doc) - allowed_root
    if extra_root:
        errors.append(f"root: 存在未定义字段 {sorted(extra_root)}")
    for req in ("schema_version", "title", "format_mode", "episodes"):
        if req not in doc:
            errors.append(f"root: 缺少必填字段 '{req}'")

    sv = doc.get("schema_version")
    if not isinstance(sv, str) or not re.match(r"^\d+\.\d+\.\d+$", sv):
        errors.append("schema_version: 必须是语义化版本号（如 '1.1.0'）")

    title = doc.get("title")
    if not isinstance(title, str) or not (1 <= len(title) <= 80):
        errors.append("title: 必须是 1–80 字的非空字符串")

    fm = doc.get("format_mode")
    if fm not in ALLOWED_FORMAT_MODES:
        errors.append(f"format_mode: 必须是 {sorted(ALLOWED_FORMAT_MODES)} 之一")

    if "genre" in doc and (not isinstance(doc["genre"], str) or not doc["genre"].strip()):
        errors.append("genre: 若提供必须为非空字符串")

    episodes = doc.get("episodes")
    if not isinstance(episodes, list) or not episodes:
        errors.append("episodes: 必须是非空数组")
        return errors

    for e_idx, ep in enumerate(episodes):
        ep_prefix = f"episodes[{e_idx}]"
        if not isinstance(ep, dict):
            errors.append(f"{ep_prefix}: 必须是对象")
            continue
        extra_ep = set(ep) - {"ep_no", "summary", "scenes"}
        if extra_ep:
            errors.append(f"{ep_prefix}: 存在未定义字段 {sorted(extra_ep)}")
        ep_no = ep.get("ep_no")
        if type(ep_no) is not int or ep_no < 1:
            errors.append(f"{ep_prefix}.ep_no: 必须是 >= 1 的整数")
        if "summary" in ep and (not isinstance(ep["summary"], str) or not ep["summary"].strip()):
            errors.append(f"{ep_prefix}.summary: 若提供必须为非空字符串")

        scenes = ep.get("scenes")
        if not isinstance(scenes, list) or not scenes:
            errors.append(f"{ep_prefix}.scenes: 必须是非空数组")
            continue

        for s_idx, sc in enumerate(scenes):
            sc_prefix = f"{ep_prefix}.scenes[{s_idx}]"
            if not isinstance(sc, dict):
                errors.append(f"{sc_prefix}: 必须是对象")
                continue
            allowed_sc = {
                "ep_no",
                "scene_no",
                "location",
                "time_of_day",
                "interior_exterior",
                "is_flashback",
                "characters",
                "lines",
            }
            extra_sc = set(sc) - allowed_sc
            if extra_sc:
                errors.append(f"{sc_prefix}: 存在未定义字段 {sorted(extra_sc)}")
            for req in (
                "ep_no",
                "scene_no",
                "location",
                "time_of_day",
                "interior_exterior",
                "characters",
                "lines",
            ):
                if req not in sc:
                    errors.append(f"{sc_prefix}: 缺少必填字段 '{req}'")

            if type(sc.get("ep_no")) is not int or sc.get("ep_no") != ep_no:
                errors.append(f"{sc_prefix}.ep_no: 必须等于所属集号 {ep_no}")
            expected_scene_no = s_idx + 1
            if sc.get("scene_no") != expected_scene_no:
                errors.append(
                    f"{sc_prefix}.scene_no: 按序应为 {expected_scene_no}，实际为 {sc.get('scene_no')!r}"
                )
            loc = sc.get("location")
            if not isinstance(loc, str) or not (1 <= len(loc) <= 40):
                errors.append(f"{sc_prefix}.location: 必须是 1–40 字的非空字符串")
            if sc.get("time_of_day") not in ALLOWED_TIMES:
                errors.append(
                    f"{sc_prefix}.time_of_day: 必须是 {sorted(ALLOWED_TIMES)} 之一"
                )
            if sc.get("interior_exterior") not in ALLOWED_IE:
                errors.append(
                    f"{sc_prefix}.interior_exterior: 必须是 {sorted(ALLOWED_IE)} 之一"
                )
            if "is_flashback" in sc and type(sc["is_flashback"]) is not bool:
                errors.append(f"{sc_prefix}.is_flashback: 必须是布尔值")

            chars = sc.get("characters")
            if (
                not isinstance(chars, list)
                or not chars
                or any(not isinstance(c, str) or not c.strip() for c in chars)
            ):
                errors.append(f"{sc_prefix}.characters: 必须是非空人物名数组")
                chars_set: set[str] = set()
            else:
                chars_set = {c.strip() for c in chars}

            lines = sc.get("lines")
            if not isinstance(lines, list) or not lines:
                errors.append(f"{sc_prefix}.lines: 必须是非空台本行数组")
                continue

            for l_idx, ln in enumerate(lines):
                ln_prefix = f"{sc_prefix}.lines[{l_idx}]"
                if not isinstance(ln, dict):
                    errors.append(f"{ln_prefix}: 必须是对象")
                    continue
                extra_ln = set(ln) - {"kind", "speaker", "emotion", "text"}
                if extra_ln:
                    errors.append(f"{ln_prefix}: 存在未定义字段 {sorted(extra_ln)}")
                kind = ln.get("kind")
                if kind not in ALLOWED_LINE_KINDS:
                    errors.append(
                        f"{ln_prefix}.kind: 必须是 {sorted(ALLOWED_LINE_KINDS)} 之一"
                    )
                text = ln.get("text")
                if not isinstance(text, str) or not text.strip():
                    errors.append(f"{ln_prefix}.text: 必须是非空字符串")
                    continue

                if kind in {"dialogue", "os", "vo"}:
                    speaker = ln.get("speaker")
                    if not isinstance(speaker, str) or not (1 <= len(speaker.strip()) <= 20):
                        errors.append(f"{ln_prefix}.speaker: '{kind}' 行必须填写说话角色名")
                    elif chars_set and speaker.strip() not in chars_set:
                        errors.append(
                            f"{ln_prefix}.speaker: '{speaker}' 未出现在本场 characters 列表中"
                        )
                    if "emotion" in ln and (
                        not isinstance(ln["emotion"], str)
                        or not (1 <= len(ln["emotion"].strip()) <= 12)
                    ):
                        errors.append(f"{ln_prefix}.emotion: 若提供必须是 1–12 字非空字符串")
                elif kind == "action":
                    if "特写" in text:
                        errors.append(
                            f"{ln_prefix}: 普通动作行不得夹带「特写」，请拆为 kind='closeup' 独立成行"
                        )
                    if m_un := UNNAMED_REF_RE.search(text):
                        errors.append(
                            f"{ln_prefix}: 禁止悬念代指「{m_un.group(0)}」，请直写人物姓名"
                        )
                    if m_lit := LITERARY_RE.search(text):
                        errors.append(
                            f"{ln_prefix}: 禁止文学抽象修辞「{m_lit.group(0)}」"
                        )
                    if m_cl := CLICHE_RE.search(text):
                        errors.append(f"{ln_prefix}: 命中微动作套话「{m_cl.group(0)}」")
                    if m_mf := MENTAL_RE.search(text):
                        errors.append(f"{ln_prefix}: 命中脑内心理描写「{m_mf.group(0)}」")

    _check_forbidden_terms(doc, "root", errors)
    return errors


def render_script_document_text(doc: dict) -> str:
    """将已校验通过的结构化台本 JSON 确定性渲染为标准纯文本台本。"""
    chunks: list[str] = []
    for ep in doc["episodes"]:
        ep_lines = [f"第{ep['ep_no']}集"]
        for sc in ep["scenes"]:
            fb = "（闪回）" if sc.get("is_flashback") else ""
            ep_lines.append(
                f"【{sc['ep_no']}-{sc['scene_no']} {sc['location']}·{sc['time_of_day']}·{sc['interior_exterior']}{fb}】"
            )
            ep_lines.append(f"人物：{'、'.join(sc['characters'])}")
            for ln in sc["lines"]:
                kind = ln["kind"]
                txt = ln["text"].strip()
                if kind == "action":
                    ep_lines.append(f"△{txt}")
                elif kind == "closeup":
                    ep_lines.append(f"△【特写】{txt}")
                elif kind == "caption":
                    ep_lines.append(f"△【字幕：{txt}】")
                else:
                    spk = ln["speaker"].strip()
                    aside = " OS" if kind == "os" else (" VO" if kind == "vo" else "")
                    emo = f"（{ln['emotion'].strip()}）" if ln.get("emotion") else ""
                    ep_lines.append(f"{spk}{aside}{emo}：{txt}")
            ep_lines.append("")
        chunks.append("\n".join(ep_lines).rstrip())
    return "\n\n".join(chunks) + "\n"


def validate_inspection_report(rep: object) -> list[str]:
    """校验 check_script_cli.py --json 输出是否满足 inspection-report.schema.json。"""
    errors: list[str] = []
    if not isinstance(rep, dict):
        return ["report: 顶层必须是对象"]
    req_top = {
        "episode_count",
        "scenes_per_ep",
        "dialogues_per_ep",
        "issue_count",
        "benchmark",
        "episodes",
        "issues",
    }
    if set(rep) != req_top:
        errors.append(f"report: 顶层键集合不符，期望 {sorted(req_top)}，实际 {sorted(rep)}")
    for int_k in ("episode_count", "issue_count"):
        if type(rep.get(int_k)) is not int or rep[int_k] < 0:
            errors.append(f"{int_k}: 必须是非负整数")
    for num_k in ("scenes_per_ep", "dialogues_per_ep"):
        if not isinstance(rep.get(num_k), (int, float)) or isinstance(rep.get(num_k), bool):
            errors.append(f"{num_k}: 必须是数字")
    bm = rep.get("benchmark")
    if not isinstance(bm, dict):
        errors.append("benchmark: 必须是对象")
    else:
        for bk in (
            "scenes_per_ep_median",
            "dialogues_per_ep_p25",
            "dialogues_per_ep_median",
            "dialogues_per_ep_p75",
            "avg_dialogue_len_median",
            "emotion_pct_median",
            "source_url",
        ):
            if bk not in bm:
                errors.append(f"benchmark: 缺少字段 '{bk}'")
    eps = rep.get("episodes")
    if not isinstance(eps, list):
        errors.append("episodes: 必须是数组")
    else:
        for i, ep in enumerate(eps):
            if not isinstance(ep, dict):
                errors.append(f"episodes[{i}]: 必须是对象")
                continue
            exp_keys = {"ep_no", "chars", "scenes", "dialogues", "avg_dialogue_len", "emotion_pct"}
            if set(ep) != exp_keys:
                errors.append(f"episodes[{i}]: 键集合不符 {sorted(ep)}")
    issues = rep.get("issues")
    if not isinstance(issues, list):
        errors.append("issues: 必须是数组")
    else:
        if len(issues) != rep.get("issue_count"):
            errors.append("issue_count: 与 issues 长度不一致")
        for i, iss in enumerate(issues):
            if not isinstance(iss, dict):
                errors.append(f"issues[{i}]: 必须是对象")
                continue
            if set(iss) != {"ep_no", "line_no", "category", "severity", "quote", "tip"}:
                errors.append(f"issues[{i}]: 字段集合不符")
            if iss.get("severity") not in {"error", "warn"}:
                errors.append(f"issues[{i}].severity: 必须是 error 或 warn")
    return errors


def validate_benchmark(bm: object) -> list[str]:
    """校验脱敏基准数据 JSON 总和与口径一致性。"""
    errors: list[str] = []
    if not isinstance(bm, dict):
        return ["benchmark: 必须是对象"]
    required = {
        "schema_version",
        "source_urls",
        "retrieved_at",
        "public_data_updated_at",
        "episode_count_distribution",
        "per_episode_rhythm",
        "dialogue_line_profile",
        "paywall_decade_distribution",
        "genre_concentration",
        "top_genres",
        "all_genres",
        "mainline_gratification_top3",
    }
    missing = required - set(bm)
    if missing:
        errors.append(f"benchmark: 缺少字段 {sorted(missing)}")
        return errors

    gc = bm["genre_concentration"]
    all_genres = bm["all_genres"]
    top_genres = bm["top_genres"]
    if len(all_genres) != gc.get("total_genres"):
        errors.append(
            f"all_genres 数量 {len(all_genres)} != total_genres {gc.get('total_genres')}"
        )
    total_count = sum(g["count"] for g in all_genres)
    if total_count != gc.get("total_dramas"):
        errors.append(
            f"all_genres 作品数总和 {total_count} != total_dramas {gc.get('total_dramas')}"
        )
    if sum(g["count"] for g in top_genres[:3]) != gc.get("top3_count"):
        errors.append("top3_count 与 top_genres[:3] 总和不一致")
    if sum(g["count"] for g in top_genres[:10]) != gc.get("top10_count"):
        errors.append("top10_count 与 top_genres[:10] 总和不一致")

    pw = bm["paywall_decade_distribution"]
    pw_sum = sum(d["count"] for d in pw["decades"])
    if pw_sum != pw.get("sample_records"):
        errors.append(f"paywall decades 总和 {pw_sum} != sample_records {pw.get('sample_records')}")

    _check_forbidden_terms(bm, "benchmark", errors)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="结构化短剧台本 JSON Schema、体检报告与统计基准校验脚本（零依赖）"
    )
    parser.add_argument("path", help="待校验的 JSON 文件路径")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--report", action="store_true", help="按体检报告契约校验")
    mode.add_argument("--benchmark", action="store_true", help="按公开统计基准文件校验")
    parser.add_argument("--render", action="store_true", help="将合规结构化台本渲染为标准纯文本并执行自检")
    args = parser.parse_args(argv)

    payload = _load_json(Path(args.path))
    if args.report:
        errors = validate_inspection_report(payload)
    elif args.benchmark:
        errors = validate_benchmark(payload)
    else:
        errors = validate_script_document(payload)

    if errors:
        for err in errors:
            print(f"[FAIL] {err}", file=sys.stderr)
        return 1

    if args.render and not args.report and not args.benchmark:
        rendered = render_script_document_text(payload)
        rep = inspect_script(rendered)
        if rep["issue_count"] != 0:
            print(f"[FAIL] 渲染后文本自检发现 {rep['issue_count']} 条问题", file=sys.stderr)
            return 1
        print(rendered, end="")
    else:
        print(f"[OK] {args.path} 校验通过（Schema 文件位于 {SCRIPT_SCHEMA_PATH.name} / {REPORT_SCHEMA_PATH.name}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
