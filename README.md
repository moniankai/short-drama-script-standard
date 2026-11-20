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
