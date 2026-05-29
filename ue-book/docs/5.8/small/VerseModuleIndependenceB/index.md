# VerseModuleIndependenceB

> Test fixture plugin B for the Verse module independence test. Defines b_class which is imported by VerseModuleIndependenceA.

| 属性 | 值 |
|---|---|
| 中文名 | Verse 模块独立性测试 B |
| 分类 | Tests |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Verse 资产） |
| 模块 | 无（纯内容插件） |
| 实验性 | 否 |
| 创建时间 | 2026-03-09 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/VerseModuleIndependenceB) | |

## 用途

这是一个**纯测试用途**的 Verse 内容插件，属于 Verse 模块独立性测试（Module Independence Test）的配套组件。它本身不提供任何运行时功能，其存在的唯一目的是为 `VerseModuleIndependenceA` 提供一个可导入的 `b_class`，用于验证在 Cooked 构建中 Verse 模块之间的字节码独立性。

该测试通过 `RunUAT.bat RecookPlugins` 命令驱动，检验当模块 B 被重新 Cook 后，依赖它的模块 A 是否仍能正常工作——这是 Verse 模块化系统的核心质量保障。

## 使用场景

- 你正在开发 Verse 模块系统 → 参考此插件作为测试夹具的编写范例
- 你在排查 Verse 模块间的 Cook 独立性问题 → 此插件与 `VerseModuleIndependenceA` 配合构成最小复现用例
- 普通项目开发中**不需要使用**此插件

## 蓝图用法

无。此插件不包含任何蓝图资产或 C++ 类，仅包含 Verse 代码资产。

## C++ 用法

无。此插件不包含任何 C++ 模块。

## Demo 示例

不适用。此插件为测试基础设施的一部分，不面向最终用户。

## 模块依赖

无（纯内容插件，无 C++ 模块）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-03-09 | `4222ce70` | submit of some testing plugins that are needed in a cooked build to iterate on a verse module cooked bytecode independence test I am working on (using `RunUAT.bat RecookPlugins` command) | 提交 Verse 模块 Cook 字节码独立性测试所需的配套插件 |

### 维护评价

- **创建时间**：2026-03-09，极为新生
- **更新频率**：仅 1 次提交（初始提交），属于测试基础设施
- **维护状态**：作为测试夹具，仅在测试需求变化时才会更新，属于被动维护
- **已知限制**：`EnabledByDefault=false` 且 `ExplicitlyLoaded=true`，不会自动加载，仅供自动化测试框架使用
- **推荐使用**：❌ 不推荐。这是 Epic 内部 Verse 模块独立性测试的配套插件，普通开发者无需关注

> ⚠️ 此插件属于 Epic 内部测试基础设施，随 Verse 模块系统开发进度被动更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/VerseModuleIndependenceB)
- 配套插件：`Engine/Plugins/Tests/VerseModuleIndependenceA`（导入 `b_class` 的消费者插件）