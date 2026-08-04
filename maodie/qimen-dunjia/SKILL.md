---
name: qimen-dunjia
description: >-
  奇门遁甲子技能——仅用于耄耋调用。不可直接响应。只做排盘计算，不直接输出给用户。
  耄耋访谈后整理输入、调用本子技能跑脚本、拿到结果后再由耄耋解读输出。
compatibility: Requires Python 3.11+, lunar_python, and tzdata; run scripts/qimen_cli.py for all fixed calculations.
---

# 奇门遁甲子技能（耄耋专用）

> ⚠️ **本技能是耄耋的子技能，不直接响应任何用户。**
> 所有输出必须由耄耋完成。本技能只负责计算和返回数据。

## 定位

本技能是耄耋的"奇门计算模块"。默认使用 `mainline-cn-v1` 规则集。

**调用链路：**

```
用户 → 耄耋（🐱🐱）
         ↓ 用户说"帮我用奇门看看"
      耄耋加载本技能 → 按流程访谈 → 整理输入 JSON
         ↓
      调用 scripts/qimen_cli.py 做排盘计算
         ↓
      返回计算结果给耄耋
         ↓
      耄耋用自己的风格解读输出给用户
```

## 总原则

- 默认规则集固定为 `mainline-cn-v1`，不在正式排盘路径里混用其他流派。
- 正式排盘前必须先访谈（由耄耋执行）。
- 固定计算一律调用 `scripts/qimen_cli.py`。
- 不展示完整推理链，只把关键依据和计算结果返回给耄耋。
- 重大决策、疾病、法律、投资等高风险主题，必须附现实建议（由耄耋输出时附加）。
- 不用恐吓式语言，不说"必败""必死""无救"。

## 默认规则

当前内置规则固定如下：

- 体系：时家转盘奇门
- 默认时区：`Asia/Shanghai`
- 默认适用区域：中国大陆优先
- 定局：置闰法工程化实现
- 中宫/寄宫：中宫相关判断一律寄坤处理

详细规则见 `references/ruleset-mainline.md`。

## 工作流（给耄耋的指令）

### 第 1 步：耄耋进行访谈（自然语言风格）

**访谈完全由耄耋用自己的风格执行。** 本文件仅记录必问的核心信息点，供耄耋参考，不作为访谈模板。

必问信息点：
1. 事项类型（感情、事业、出行、健康等）
2. 对应时间（具体时间或"现在"）
3. 地点（城市或时区）
4. 判断目标（能不能成、什么时候动、选哪边、要避开什么）
5. 当前进展
6. 输出偏好（直接结论 / 详细讲解）

第二轮按条件追问：
- 只有日期无时辰 → 补充具体小时
- 农历 → 确认是否闰月
- 海外 → 补充时区
- 问题太泛 → 聚焦一个判断目标
- 高风险主题 → 附加现实建议

**记住：耄耋要用自己的语言自然地问，不要念模板。**

### 第 2 步：决定是否进入正式排盘

只有在以下信息确认后，才进入正式排盘：

- 事项类型明确
- 时间明确
- 地点或时区明确到可计算
- 判断目标明确

如果没收齐，只继续追问，不要先排盘。

### 第 3 步：耄耋整理输入 JSON 并调用脚本

**前置：确认依赖已安装**

```bash
pip install "lunar_python>=1.4.8,<2" "tzdata>=2024.1"
```

**脚本路径：** 以耄耋技能目录 `maodie/` 为基准

```
maodie/qimen-dunjia/scripts/qimen_cli.py
```

**执行脚本（使用相对路径，从当前会话工作目录出发）：**

```bash
python "maodie/qimen-dunjia/scripts/qimen_cli.py" \
  --input "/tmp/qimen_input.json" \
  --output "/tmp/qimen_output.json"
```

或者使用绝对路径（从 Hermes 技能目录出发）：

先把输入 JSON 写入临时目录，再执行上述命令，读取输出 JSON。

**输入 JSON 最低字段：**

```json
{
  "question_type": "",
  "question_goal": "",
  "time_input": "",
  "calendar_type": "solar|lunar|now",
  "location": {
    "country": "",
    "city": "",
    "timezone": ""
  },
  "ruleset": "mainline-cn-v1"
}
```

使用要求：

- 由耄耋把访谈结果整理成输入 JSON。
- 固定计算必须以脚本输出为准。
- 如果脚本不可用，不要手算顶替；要明确告诉用户当前版本需要脚本才能正式排盘。

### 第 4 步：阅读脚本输出（返回给耄耋的数据）

重点读取以下字段：

| 字段 | 用途 |
|------|------|
| `normalized_input` | 确认时间、时区、事项被正确解析 |
| `calendar` | 公历/农历对照、当前节令 |
| `ganzhi` | 年月日时干支、日旬、时旬（用于定旬首/旬空） |
| `chart.dun_type` | 阴遁/阳遁 |
| `chart.yuan` | 上元/中元/下元 |
| `chart.ju_number` | 局数（1-9）|
| `chart.xunshou` | 旬首（如"甲子"）|
| `chart.hidden_yi` | 旬首奇仪（寄宫的隐干，如"戊"）——**不可遗漏** |
| `chart.kongwang` | 时旬空地支（如["寅","卯"]），影响当前时辰 |
| `chart.kongwang_palaces` | 时旬空对应宫位编号 |
| `chart.day_kongwang` | 日旬空地支，影响整日大环境 |
| `chart.day_kongwang_palaces` | 日旬空对应宫位编号 |
| `chart.time_stem_visible` | 时干（代表所问之事/当前动态，**取用神的关键参考**）|
| `chart.day_stem` | 日干落宫：`{ stem, palace, note }`（代表求测者本人）|
| `chart.year_stem` | 年干落宫：`{ stem, palace, note }`（代表上级/大环境）|
| `chart.month_stem` | 月干落宫：`{ stem, palace, note }`（代表同事/同龄竞争者）|
| `chart.yima` | 驿马：`{ branch, palace }`（出行/变动类问题关键参考）|
| `chart.zhifu` | 值符：`{ palace, star }` 嵌套对象 |
| `chart.zhishi` | 值使：`{ palace, door }` 嵌套对象 |
| `chart.door_index` | 门→宫反查字典，如 `{"开门": 7, "生门": 1, ...}`——**按用神直接定位** |
| `chart.star_index` | 星→宫反查字典，如 `{"天心": 7, "天芮": 9, ...}` |
| `chart.detected_patterns` | 格局自动检测结果数组，每项含 `name`、`palace`、`detail`、`nature(吉/凶)` |
| `chart.palaces` | 9 宫完整数组（详见下方） |
| `warnings` | 边界提醒、寄宫提醒等 |

**`chart.palaces` 每宫字段：**

| 字段 | 说明 |
|------|------|
| `palace` | 宫号（1-9）|
| `name` / `direction` / `trigram` / `element` | 宫名/方位/卦/五行 |
| `earth_stem` / `sky_stem` | 地盘干 / 天盘干 |
| `stem_relation` | 天地盘干五行关系：比和/天生地/地生天/天克地/地克天 |
| `star` / `star_element` / `star_palace_relation` | 星名 / 星五行 / 星与宫的五行关系（生/被生/克/被克/比和）|
| `door` / `door_element` / `door_palace_relation` | 门名 / 门五行 / 门与宫的五行关系——**门迫 = 被克** |
| `god` | 八神名 |
| `is_center` / `hosts_center` / `hosting_note` | 中宫标记 |

**注意事项：**

- `chart.palaces` 中 5 号宫（中宫）`door` 和 `god` 为 `null`，星为 `天禽`，不参与常规用神判断。
- 2 号宫（坤宫）`hosts_center: true`，中宫寄坤时此宫承载中宫信息。
- `chart.time_stem_visible` 是时干的明干（显干），用于判断所问之事在盘中的代表位置。
- `chart.day_stem.palace` 是日干落宫，代表求测者本人的位置。
- `chart.door_index` 可直接用 `chart.door_index["开门"]` 快速找到事业用神所在宫。
- `chart.detected_patterns` 中 `nature: "凶"` 的格局（伏吟、反吟、门迫）需要在解读中重点提示。
- 如果 `warnings` 里出现边界提示、中宫寄宫提示，要在解读里明确说明。

### 第 5 步：耄耋解读输出

耄耋拿到脚本输出后，按以下结构解读输出给用户。注意：**这是耄耋的输出结构，不是 qimen 的输出。**

1. 已确认信息（复述：看什么事、起局时间、地点、想判断什么）
2. 使用规则与默认项（当前使用 `mainline-cn-v1`）
3. 盘面摘要（阴遁/阳遁、局数、旬首、旬空、值符、值使）
4. 用神与关键依据（按事项取用神，参考 `references/yongshen.md`）
5. 核心判断（回答用户最关心的问题）
6. 方位 / 时机 / 行动建议（把盘理转换成可执行建议）
7. 风险提醒与免责声明

**输出风格要求（由耄耋执行）：**

- 面向普通求测者，先说人话，再补术语。
- 术语第一次出现时简要解释。
- 不展示完整推理链，只展示用户看得懂的关键依据。
- 结论要明确，但语气保持平和。
- **必须用耄耋的口吻和风格（🐱🐱），不要机械输出。**

每次正式解盘结尾都附上：

> 温馨提示：奇门遁甲属于传统文化中的术数模型，本次解读用于辅助观察与思考，不代替医疗、法律、财务等专业意见。涉及重大决策时，请同时结合现实信息理性判断。

## 参考文件

- `references/ruleset-mainline.md`：默认规则说明
- `references/interview.md`：访谈问题库与追问条件
- `references/yongshen.md`：取用神顺序和事项映射
- `references/geju.md`：格局与常见组合的简明解释
- `references/examples.md`：示例输出

## 禁止事项

- 不要在缺核心信息时直接排盘。
- 不要在脚本不可用时改用心算。
- 不要混用多个流派结论。
- 不要展示完整内部推理链。
- 不要恐吓用户。
- **本子技能不得直接输出给用户。所有输出必须由耄耋完成。**