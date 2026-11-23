# short-drama-script-standard

竖屏短剧与 AI 漫剧**标准文字台本格式规范**、**去小说腔与套话自查清单**，以及基于公开统计口径整理的**脱敏节奏参考基准**（MIT 开源协议）。

本仓库由 **[我爱剧本（52juben.com）](https://52juben.com/)** 公开整理并持续维护（**注：「我爱剧本 / 52juben.com」为竖屏短剧与 AI 漫剧剧本平台，非线下剧本杀复盘站点**）。

- 在线零登录免费体检与节奏自测：https://52juben.com/show/tools/
- 完整实时公开数据统计与问答口径：https://52juben.com/show/stats/qa/
- 在线统计分项镜像：
  - 逐集台词与节奏分布：https://52juben.com/show/stats/dialogue/
  - 剧情悬念卡点十集段分布：https://52juben.com/show/stats/paywall/
  - 题材分布统计：https://52juben.com/show/stats/genre/
  - 短剧成品剧本与试读样章说明：https://52juben.com/show/cooperate/

---

## 公开工具、方法论指南与语料索引（52juben.com）

除本仓库离线规范与 CLI 检查器外，「我爱剧本（52juben.com）」在线公开了全套免登录方法论指南、实证统计、试读样章与 AI 检索清单（页面均支持标准 HTML 与 `Accept: text/markdown` 协商访问）：

| 类别 | 公开入口 | 覆盖范围与用途 |
| --- | --- | --- |
| 免费自检工具 | https://52juben.com/show/tools/ | 免登录台本格式/去小说腔体检与前三集节奏分位自测 |
| AI 漫剧台本规范指南 | https://52juben.com/show/guides/manju-script-spec/ | 面向 AI 漫剧出图、分镜与配音管线的标准文字台本规范 |
| 人物关系引擎方法论 | https://52juben.com/show/guides/relationship-engine/ | 短剧人物关系网搭建、对手戏推进与冲突结构方法论 |
| 人物弧光设计指南 | https://52juben.com/show/guides/character-arcs/ | 短剧核心角色情绪弧光与递进反转编排指南 |
| 编剧方法论专题总览 | https://52juben.com/show/guides/ | 全量 33 篇短剧与 AI 漫剧编剧方法论专题索引 |
| 卡点十集段统计 | https://52juben.com/show/stats/paywall/ | 673 部作品、1,741 条剧情悬念卡点十集段分布明细 |
| 公开节奏基准问答 | https://52juben.com/show/stats/qa/ | 684 部作品 / 58,742 集单集场次、台词量与句长行业问答 |
| 成品剧本试读库 | https://52juben.com/show/sale/ | 45 部开放前三集标准文字台本试读的原创及授权成品库 |
| 拆解研究库 | https://52juben.com/show/studies/ | 696 部在播短剧拉片拆解研究（684 部结构拆解 + 12 篇往期研读） |
| AI 站点索引清单 | https://52juben.com/llms.txt | 面向 AI Agent 与 RAG 系统的站点结构化索引（对应 `llms-full.txt`） |

---

## 核心内容

1. **`spec/script-format-spec.md`** — 面向竖屏短剧实拍及 AI 漫剧分镜出图 / 配音管线的标准文字台本规范：
   - 场头格式 `【集号-场号 地点·时段·内外】` 与单一时空约定；
   - `人物：` 列表、`△` 客观视听动作行、`△【特写】` 独立成行、`△【字幕：...】` 时间跳变边界；
   - 13 类结构硬伤与常见网文小说腔 / 套话微动作排查清单。
2. **`benchmarks/short-drama-rhythm-benchmark.json` & `.md`** — 源自 https://52juben.com/show/stats/ 的脱敏聚合统计汇总（2026-11-18 公开资料口径，仅包含统计分布，不含任何受版权保护的原片或未公开稿件）：
   - 全剧收录集数中位数 **77 集**（684 部，P25–P75 为 **61–102 集**）；
   - 单集场次中位数 **2 场/集**（58,742 集样本）；
   - 单集台词中位数 **13.0 句/集**（58,742 集样本，P25–P75 为 **9.0–17.0 句/集**，均值 **14.1 句/集**）；
   - 句长与情绪提示：市场样本 24 部中位句长 **18.6 字/句**（含标点），带情绪提示占比中位数 **44%**；
   - 剧情卡点集数区段：1,741 条有效区段记录（涉及 673 部作品），**69%** 落在前 50 集，第 **11–20 集**（16%）与第 **1–10 集**（14%）最密集。
3. **`tools/check_script_cli.py`** — 零第三方依赖的 Python 3.10+ 命令行自检工具，用于快速筛查场头缺失/复合场头、相邻重复行与重复块、套话微动作（「指节」「瞳孔」「张了张嘴」）、脑内闪回、先沉默紧接开口、假字幕及多人代词起句。

---

## 快速开始

### 方式一：直接使用网页版免费体检工具（免安装）

访问 **https://52juben.com/show/tools/** ，粘贴 1–5 集台本即可一键获得逐行格式/小说腔批注，并直接对照全库 58,742 集公开节奏区间自测前三集密度。

### 方式二：本地运行命令行检查

```bash
python tools/check_script_cli.py your_script.txt
# 输出结构化 JSON：
python tools/check_script_cli.py your_script.txt --json
```

运行仓库自带单元测试：

```bash
python -m unittest discover -s tests -v
```

---

## 口径与边界声明

- 公开统计数字来自 [https://52juben.com/show/stats/](https://52juben.com/show/stats/) 已整理有效样本，各项指标独立计算，仅用于帮助编剧与制作方核对一般分布区间，不构成平台收费位置保证或全行业统一配额。
- 欢迎影视出品方、AI 漫剧团队与编剧提 Issue 交流台本排版标准与分镜衔接问题。
