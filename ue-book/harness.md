# ue-book Harness

## 文档模板

每个 Plugin 的文档必须包含以下章节。

### 属性表格式规范（严格遵守）

属性表必须**严格按照以下格式**，不允许自由发挥：

```markdown
# {Plugin FriendlyName}

> {Description from .uplugin}（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | {简短中文名（2-6字，根据用途翻译）} |
| 分类 | {Category from .uplugin} |
| 默认启用 | ✅ 是 / ❌ 否 |
| 包含内容 | ❌ 无 / ✅ 有（简述内容类型） |
| 模块 | `ModuleName` (Type), `ModuleName2` (Type) |
| 实验性 | ⚠️ 是 / 否 |
| 创建时间 | YYYY-MM-DD |
| 年龄标签 | 🏛️ 文物 / 👴 老古董 / 🆕（约 N 年） |
| [源码](URL) | |
```

**字段格式规则**：

1. **默认启用**：只写 `✅ 是` 或 `❌ 否`，不要加括号解释
2. **包含内容**：只写 `❌ 无` 或 `✅ 有（类型）`，类型如"蓝图资产"、"材质模板"、"测试资源"
3. **模块**：用反引号包裹模块名，格式为 `` `Name` (Type) ``，多个用逗号分隔。Type 只写 Runtime/Editor/UncookedOnly/DeveloperTool，不写 LoadingPhase。如果没有模块写 `无（纯内容插件）`
4. **实验性**：如果 `IsBetaVersion=true` 或 `IsExperimentalVersion=true` 写 `⚠️ 是`，否则写 `否`。**必须有这一行**
5. **年龄标签**：格式固定为 `🏛️ 文物（约 N 年）` / `👴 老古董（约 N 年）` / `🆕（约 N 年）`，N 取整数
6. **源码链接**：目录用 `tree/{branch}`，文件用 `blob/{branch}`

**示例（CableComponent）**：

```markdown
# Cable Component

> A simulated cable component.

| 属性 | 值 |
|---|---|
| 中文名 | 绳索组件 |
| 分类 | Rendering |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `CableComponent` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/{branch}/Engine/Plugins/Runtime/CableComponent) | |
```

## 用途

基于源码分析 plugin 的实际功能，不要照抄 .uplugin 的 Description。
说清楚：这个 plugin 解决什么问题？为什么存在？

## 使用场景

具体的场景描述，例如：
- 你在做一个 2D 平台跳跃游戏 → 用 Paper2D
- 你需要自定义复杂的输入映射 → 用 EnhancedInput

## 蓝图用法

搜索 UFUNCTION(BlueprintCallable) 和 UPROPERTY(BlueprintReadWrite)。
按功能分组，不要罗列所有函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `函数名` | 一句话说明 | `UClassName` |

### 使用示例（蓝图描述）

用文字描述蓝图连接方式（无法截图）。

## C++ 用法

重点从 test case 中提取，贴近官方用法。

### 头文件引入

```cpp
#include "ModuleName.h"
```

### 基本用法

从 test case 提取的代码示例，加上注释。
标注来源文件路径。

### 进阶用法

更复杂的用法，来自多个 test case 组合。

## Demo 示例

一个完整的、可编译的最小示例。
包含 .h + .cpp。不需要展示 Build.cs 代码，依赖关系已在"模块依赖"章节说明。

## 模块依赖

从 Build.cs 的 PublicDependencyModuleNames 和 PrivateDependencyModuleNames 提取。
告诉读者：要用这个 plugin，你的模块需要依赖哪些东西。

**省略常见依赖**：以下模块几乎每个 plugin 都依赖，无需列出：
- Core, CoreUObject, Engine, Slate, SlateCore, UMG, InputCore
- UnrealEd, EditorStyle, PropertyEditor (编辑器插件常见)
- Projects, DeveloperSettings

只列出该 plugin **独特**的、不常见的依赖。如果全部都是常见依赖，写"无特殊依赖（仅标准 Core/Engine/Slate 等）"。

| 模块 | 用途 |
|---|---|
| `UniqueModule` | 一句话说明 |

## 维护状态

从 git log 分析该 plugin 的维护情况。

### 近期更新

从 git log 获取最近 3-5 次 commit，以**表格**形式展示，每行必须包含 hash 原文和中文解读。

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-10-03 | `abc1234` | Original commit message | 用中文概括这次改动的实际影响 |
| 2025-09-15 | `def5678` | Another commit message | 用中文概括这次改动的实际影响 |

- Hash 用反引号包裹（`abc1234`）
- 原文：原始 commit message（英文），不要截断关键信息
- 中文解读：用中文翻译并概括这次改动的实际影响，20 字以内

### 维护评价

基于以下信息给出综合评价：
- 创建时间（年龄）
- 最近更新频率和内容
- 是否还在活跃维护
- 是否有已知问题或限制
- 是否推荐使用

如果超过 1 年没有实质性更新，给出警告。

## 相关链接

- [源码]({GitHub path to plugin root})
- [官方文档]({DocsURL from .uplugin})（如果有）
- [测试用例]({GitHub path to test files})
```

## UE 源码阅读经验

- .uplugin 的 Description 字段通常很简短，需要从代码推断真正用途
- BlueprintCallable 在 UFUNCTION() 宏里，搜索 Public/*.h
- 测试用 IMPLEMENT_SIMPLE_AUTOMATION_TEST + GIVEN/WHEN/THEN BDD 风格
- 模块类型: Runtime(运行时) / Editor(编辑器) / UncookedOnly(仅未打包)
- EnabledByDefault=false 的 plugin 需要手动启用，文档要注明
- 有些 plugin 的 test 在 Engine/Tests/ 下面，不在 plugin 自己目录内
- Build.cs 中的 PublicDependencyModuleNames 是使用者需要引用的模块

## Git 信息获取

**重要**: UE 源码是 git worktree，必须在主仓库 `/mnt/x/UnrealEngine` 执行 git 命令。

### 获取创建时间

**不要用 `--follow`**：它会追踪文件内容相似度，可能追溯到完全不相关的文件（如 ModularGameplay 被追溯到 ScreenshotTools）。

正确策略：检查当前路径和 Experimental 路径，取最早的结果。

```bash
# 1. 当前路径
cd /mnt/x/UnrealEngine && git log --diff-filter=A --format='%ai' -- 'Engine/Plugins/{Category}/{Name}/{Name}.uplugin' | tail -1

# 2. Experimental 路径（很多 plugin 从 Experimental 迁移过来）
cd /mnt/x/UnrealEngine && git log --diff-filter=A --format='%ai' -- 'Engine/Plugins/Experimental/{Name}/{Name}.uplugin' | tail -1

# 3. 如果上面都没有结果，用通配符搜索（较慢）
cd /mnt/x/UnrealEngine && git log --all --diff-filter=A --format='%ai' -- 'Engine/Plugins/*/{Name}/{Name}.uplugin' | tail -1
```

- 输出格式: `2014-03-14 14:13:41 -0400`
- `--diff-filter=A` 只显示文件首次添加的 commit
- `| tail -1` 取最早的那条（如果有多次添加）
- 取三个结果中最早且非空的那个作为创建时间

### 获取最近 N 次 commit

```bash
cd /mnt/x/UnrealEngine && git log --format='%h|%ai|%s' -3 -- 'Engine/Plugins/{Category}/{Name}/'
```

- 输出格式: `hash|date|message`
- 用 plugin 目录路径（不是 .uplugin 文件），这样能捕获所有相关改动
- 解读 commit message 时关注：功能更新、bug 修复、重构、废弃标记等

### 年龄标签计算

```python
from datetime import datetime
created = datetime.strptime(date_str[:10], '%Y-%m-%d')
age_years = (datetime.now() - created).days / 365.25

if age_years > 10:
    tag = "🏛️ 文物"
elif age_years > 5:
    tag = "👴 老古董"
else:
    tag = "🆕"
```

### 维护评价标准

- **活跃维护**: 最近 6 个月内有功能性更新（不只是编译修复）
- **维护中**: 最近 1 年内有更新
- **维护不活跃**: 1-2 年没有实质性更新
- **可能废弃**: 2 年以上没有更新，或 commit message 中有 deprecated/obsolete 标记
- **实验性**: .uplugin 中 IsBetaVersion=true 或 EnabledByDefault=false

## GitHub 链接规范

## 杯型分类（按源码规模）

根据 plugin 的 .cpp + .h 文件数量分为 4 个等级，决定文档深度：

| 杯型 | 文件数 | 文档策略 |
|---|---|---|
| small | 1-20 | 完整文档，可一次读完所有源码 |
| medium | 21-50 | 完整文档，可能需要分模块阅读 |
| large | 51-100 | 按子模块拆分，每个模块单独文档 + 汇总页 |
| xlarge | 100+ | 必须按子模块拆分，每个模块独立 task |

文档输出路径: `docs/{size}/{PluginName}/index.md`

大型 plugin 的汇总页结构:
```
docs/large/SOMEPlugin/
├── index.md          ← 汇总页（用途总览、模块列表、维护状态）
├── ModuleA.md        ← 子模块文档
└── ModuleB.md
```

- 分支: {branch}
- 格式: `https://github.com/EpicGames/UnrealEngine/blob/{branch}/{相对路径}`
- 相对路径以 Engine/ 开头，例如: Engine/Plugins/2D/Paper2D/Paper2D.uplugin
- .uplugin 链接指向 plugin 根目录（用 tree/{branch}）
- 源码链接指向具体文件（用 blob/{branch}）

## 常见错误

<!-- Review Agent 发现系统性错误后追加到这里 -->

## 人工指引

<!-- 用户手动添加的规范 -->
