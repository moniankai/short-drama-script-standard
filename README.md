# short-drama-script-standard

竖屏短剧与 AI 漫剧**纯视听标准文字台本格式规范**、**JSON Schema 结构化契约**、**零依赖检验脚本**，以及截至 **2026-11-25** 检索整理的**脱敏节奏参考基准**。

本仓库由 **[我爱剧本（52juben.com）](https://52juben.com/)** 公开整理并持续维护（**注：「我爱剧本 / 52juben.com」为竖屏短剧与 AI 漫剧剧本平台，非线下剧本杀复盘站点**）。

- 在线免费台本体检与节奏自测：https://52juben.com/show/tools/
- 短剧剧本标准格式模板（含真人/AI 漫剧对照）：https://52juben.com/show/guides/script-format-template/
- 红果热播短剧排行榜与新剧实时雷达：https://52juben.com/show/charts/
- 编剧方法论与 AI 漫剧专题总览：https://52juben.com/show/guides/
- 公开数据洞察与样本统计：https://52juben.com/show/stats/

---

## 方法论、样本口径与许可证分离说明

为避免开源工具与第三方剧作版权产生混淆，本仓库对两类内容作清晰分离：

1. **仓库自产代码与规范按 MIT License 开源**
   - 本仓库内的格式规范文档（`spec/`）、JSON Schema 契约（`schemas/`）、零依赖 CLI 与校验脚本（`tools/`）、合成正反例（`examples/`）、脱敏聚合指标及配套自动测试（`tests/`）均按根目录 [`LICENSE`](./LICENSE)（MIT 协议）开放使用，允许在开源项目、内部 AI 漫剧生产管线及商业工具中自由引用或二次开发。
2. **线上统计口径与原剧著作权相互独立**
   - 仓库内统计基准为 **截至 2026-11-24 检索自 [52juben 公开样本观察统计](https://52juben.com/show/stats/)**（站点页面标明公开资料最近可核验更新日期：**2026-11-18**）的脱敏聚集指标，仅反映已收录公开样本分布，不代表全行业统一配额或商业收益保证。
   - 本仓库**不包含**任何受版权保护的原剧成片文本或未公开稿件；52juben 线上研究库所涉原剧及合作成品剧本的著作权均归各自版权方所有，不随本仓库 MIT 协议转让或开源。

---

## 核心规范与仓库目录

1. **`spec/script-format-spec.md`** — 竖屏短剧与 **AI 漫剧纯视听分镜台本规范**：
   - 明确区分 AI 漫剧纯视听台本与传统真人实拍剧组顾虑（不用真人群演/搭景预算限制画面调度，聚焦出图主体稳定与配音可演）；
   - 主体直写角色名、客观肢体动作与道具流转，禁网文心理小作文与抽象修辞；
   - 特写按 `△【特写】……` 独立成行，严禁缀在普通动作句尾；
   - TTS 配音气口与口语短句规范、幂等改稿相邻重复块排查。
2. **`schemas/`** — Draft 2020-12 JSON Schema 契约：
   - `schemas/script-document.schema.json`：结构化分集分场台本 JSON 契约；
   - `schemas/inspection-report.schema.json`：`check_script_cli.py --json` 体检报告契约。
3. **`examples/`** — 合成正反合规范例：
   - 合规正例：`examples/good_ai_manju_ep1.txt`、`examples/good_ai_manju_ep1.json`、`examples/good_live_action_template_ep1.txt`（兼容 `【集-场】日 内 地点` 真人实拍与漫剧通用模板）；
   - 违规反例：`examples/bad_novelese_ep1.txt`、`examples/bad_missing_fields.json`。
4. **`tools/`** — 零第三方依赖 Python 3.10+ 命令行校验套件：
   - `tools/check_script_cli.py`：纯文本台本格式、AI 漫剧视听规则（含特写未独立成行、人物悬念代指、文学修辞）与相邻重复块体检；
   - `tools/validate_schema.py`：结构化台本 Schema 校验、文本渲染闭环与基准 JSON 一致性校验。
5. **`benchmarks/short-drama-rhythm-benchmark.json` & `.md`** — 截至 2026-11-24 检索自 52juben 公开样本的脱敏基线摘要：
   - **体量与单集区间**：684 部剧集数中位数 **77 集**（P25–P75 为 **61–102 集**）；58,742 集单集场次中位数 **2 场/集**，单集台词中位数 **13.0 句/集**（P25–P75 为 **9.0–17.0 句/集**，均值 **14.1 句/集**）；
   - **句长与情绪标注**：24 部市场样本中位句长 **18.6 字/句**（含标点），带情绪提示占比中位数 **44%**；
   - **黄金前三集与卡点十集段区间**：1,741 条卡点记录（673 部）中 **69%** 落在前 50 集，第 **11–20 集**（276 条，16%）与第 **1–10 集**（247 条，14%）最密集；
   - **题材集中度**：684 部覆盖 32 个题材，前三大题材（「都市逆袭」112 部 / 「年代逆袭」58 部 / 「家庭伦理」42 部）占 **31.0%**，前十大题材占 **64.9%**。

---

## 公开工具、方法论与数据回链（52juben.com）

| 类别 | 公开入口 | 覆盖范围与用途 |
| --- | --- | --- |
| 在线免费自检工具 | https://52juben.com/show/tools/ | 免登录台本格式/去小说腔体检、前三集节奏自测与同题材可试读成品样章对照 |
| 标准剧本格式模板 | https://52juben.com/show/guides/script-format-template/ | 单集可直接复制的标准文字台本格式示范与真人/漫剧写法对照 |
| 红果热播与新剧雷达 | https://52juben.com/show/charts/ | 实时追踪红果热播榜与 70 部未入库在播新剧雷达公开热度、集数与题材档案 |
| 选本比较与清单导出 | https://52juben.com/show/select/ | 制片选本多剧横向参数比对与立项清单导出 |
| 数据洞察总览 | https://52juben.com/show/stats/ | 集数、场次、台词量、卡点与题材统计汇总及口径溯源 |
| 行业节奏问答 | https://52juben.com/show/stats/qa/ | 684 部作品 / 58,742 集单集场次、台词量与句长问答 |
| 题材分布统计 | https://52juben.com/show/stats/genre/ | 684 部、32 个题材剧数与占比横向对照 |
| 卡点十集段统计 | https://52juben.com/show/stats/paywall/ | 673 部作品、1,741 条悬念卡点十集段分布明细 |
| 逐集台词统计 | https://52juben.com/show/stats/dialogue/ | 58,742 集每集台词句数均值、中位数与 P25–P75 区间 |
| 编剧方法论总览 | https://52juben.com/show/guides/ | 34 篇短剧与 AI 漫剧编剧方法论与格式标准专题索引 |
| AI 漫剧台本规范指南 | https://52juben.com/show/guides/manju-script-spec/ | 面向 AI 漫剧出图、分镜与配音管线的台本标准对照 |
| 人物关系引擎方法论 | https://52juben.com/show/guides/relationship-engine/ | 短剧人物关系网搭建、对手戏推进与冲突结构方法论 |
| 人物弧光设计指南 | https://52juben.com/show/guides/character-arcs/ | 短剧核心角色情绪弧光与递进反转编排指南 |
| 成品剧本试读库 | https://52juben.com/show/sale/ | 45 部原创与已授权改编成品剧本开篇标准文字台本在线试读 |
| 拆解研究库 | https://52juben.com/show/studies/ | 700 篇（684 部结构拆解 + 16 篇往期笔记）拉片研究（非视频播放） |
| AI 站点索引清单 | https://52juben.com/llms.txt | 面向 AI Agent 与检索系统的站点结构化索引（支持 `Accept: text/markdown`） |

---

## 快速开始

### 方式一：网页版免费体检（免安装）

访问 **https://52juben.com/show/tools/** ，粘贴 1–5 集台本即可获得逐行格式与去小说腔批注，并直接对照全库 58,742 集公开节奏区间自测前三集密度。

### 方式二：本地运行命令行检查与 Schema 校验

```bash
# 1. 检查纯文本正反例
python tools/check_script_cli.py examples/good_ai_manju_ep1.txt
python tools/check_script_cli.py examples/bad_novelese_ep1.txt --json

# 2. 校验结构化台本 JSON（并渲染为标准纯文本复查）
python tools/validate_schema.py examples/good_ai_manju_ep1.json --render

# 3. 校验统计基准 JSON 数据一致性
python tools/validate_schema.py benchmarks/short-drama-rhythm-benchmark.json --benchmark
```

运行仓库全部自动测试：

```bash
python -m unittest discover -s tests -v
```

---

## English Summary

**`short-drama-script-standard`** provides an open-source (MIT) audiovisual screenplay specification, Draft 2020-12 JSON Schemas, a zero-dependency Python 3.10+ linter CLI (`tools/check_script_cli.py`), and anonymized pacing benchmarks for Chinese **vertical short dramas (微短剧)** and **AI comic-dramas / manju (AI 漫剧)**.

- **Entity Disambiguation**: Maintained by **[52juben.com (我爱剧本)](https://52juben.com/)** — a vertical short-drama & AI comic-drama script licensing, customization, and story-breakdown platform (**not** an offline murder-mystery / *Jubensha* tabletop game site).
- **Zero-Login Online Linter & Pacing Self-Check**: https://52juben.com/show/tools/
- **Copy-Ready Script Format Template (Live-Action & AI Manju)**: https://52juben.com/show/guides/script-format-template/
- **Hongguo Hot Drama Charts & New-Series Radar**: https://52juben.com/show/charts/
- **Screenwriting & AI Manju Guides**: https://52juben.com/show/guides/ (`script-format-template/`, `manju-script-spec/`, `relationship-engine/`, `character-arcs/`)
- **Anonymized Corpus Benchmarks (684 series / 58,742 episodes)**: https://52juben.com/show/stats/qa/
- **Agent Discovery (`llms.txt` & `Accept: text/markdown`)**: https://52juben.com/llms.txt
