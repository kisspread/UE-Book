# VerseModuleIndependenceA

> Test fixture plugin A for the Verse module independence test. Defines a_class which inherits from b_class in VerseModuleIndependenceB.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Verse模块独立性A |
| 分类 | VerseTests |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Verse源代码） |
| 模块 | 无（纯内容插件） |
| 实验性 | 否 |
| 创建时间 | 2026-03-09 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/VerseModuleIndependenceA) | |

## 用途

这是一个用于 **Verse 模块打包独立性测试** 的专用测试夹具插件。它不提供任何面向用户的运行时或编辑器功能，其存在的唯一目的是作为自动化测试基础设施的一部分。该插件定义了一个 Verse 类 `a_class`，该类继承自另一个测试插件 `VerseModuleIndependenceB` 中的 `b_class`，用于验证 Verse 编译器和打包工具（特别是 `RecookPlugins` 命令）是否能正确处理跨插件的 Verse 模块依赖关系，确保一个插件的 Verse 模块代码能够正确引用并链接到另一个插件的 Verse 模块。

## 使用场景

- 你是一名 Epic 内部的 Verse 工具链或打包流程开发者，需要编写或调试自动化测试用例，以确保 Verse 模块的独立性和可移植性在烹饪构建（Cooked Build）中得到保障。
- 你正在执行 `RunUAT.bat RecookPlugins` 命令来迭代测试插件的重新烹饪流程，需要此插件作为测试用例的一部分。

## 蓝图用法

此插件不包含任何 C++ 模块或蓝图资产，因此没有可供蓝图使用的节点。

### 核心节点

无。

### 使用示例（蓝图描述）

不适用。

## C++ 用法

此插件不包含任何 C++ 模块或头文件。

### 头文件引入

不适用。

### 基本用法

不适用。

### 进阶用法

不适用。

## Demo 示例

此插件本身不包含可执行的 C++ 代码。其核心是一个 Verse 源文件。以下是其可能包含的 Verse 代码逻辑的示例（基于其描述推断）：

```verse
using { /UnrealEngine.com/Tests/VerseModuleIndependenceB }

a_class := class(b_class):
    # 可能添加一些用于测试的本地函数或变量
    TestFunction<public>()<transacts>: void=
        Print("a_class function called")
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `VerseModuleIndependenceB` | 提供被此插件中 `a_class` 继承的基类 `b_class`。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-03-09 | `4222ce70` | submit of some testing plugins that are needed in a cooked build to iterate on a verse module cooked bytecode independence test I am working on (using `RunUAT.bat RecookPlugins` command) | 首次提交，作为 Verse 模块打包字节码独立性测试的必要测试插件。 |

### 维护评价

- **创建时间**：2026年3月，非常新的插件。
- **最近更新**：仅有一次提交，时间与创建时间相同。
- **活跃度**：此插件为一次性测试工具，其存在是为了支持特定的开发或测试流程。预计不会像通用功能插件那样频繁更新，除非底层测试需求发生变化。
- **已知限制**：这是一个内部测试插件，`EnabledByDefault=false`，普通项目不应启用。它本身不提供功能，只在特定的自动化测试上下文中才有意义。
- **推荐使用**：**不推荐普通开发者使用**。仅用于 Epic 内部 Verse 工具链和打包系统的开发与测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/VerseModuleIndependenceA)
- [Verse 路径](/UnrealEngine.com/Tests/VerseModuleIndependenceA)
- [测试用例] （可能位于 Engine/Tests/ 目录下，与此插件的使用方式相关，但非本插件直接包含）