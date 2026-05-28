# MassAI Test Suite

> AI-specific functionality extending MassGameplay

| 属性 | 值 |
|---|---|
| 中文名 | MassAI 测试套件 |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试框架与工具） |
| 模块 | `MassAITestSuite` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 👴 老古董（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI/Source/MassAITestSuite) | |

**注：此文档专注于 `MassAITestSuite` 模块。`MassAI` 是一个大型插件，包含多个功能模块（如 `MassNavigation`、`MassAIBehavior` 等），请参阅相关章节获取更多信息。**

## 用途

`MassAITestSuite` 是 `MassAI` 插件中的自动化测试模块。它并非面向最终用户的功能模块，而是为 UE5 的自动化测试框架（Automation Test Framework）提供针对 `MassAI` 插件（尤其是其导航与群体 AI 功能）的测试套件、工具和基础设施。其主要目的是验证 `MassAI` 相关系统（如 `MassNavigation`, `MassZoneGraphNavigation` 等）在各种条件下的正确性、性能和鲁棒性。

## 使用场景

*   **插件开发者/引擎开发者**：在修改 `MassAI` 或 `MassGameplay` 核心代码后，运行此测试套件以确保改动没有引入回归错误。
*   **需要深入验证 MassAI 行为的集成测试**：当项目重度依赖 `MassAI` 的群体移动、避障或区域图导航功能时，可以参考或扩展此模块中的测试用例，创建针对特定游戏逻辑的自动化测试。

## 蓝图用法

此模块主要为 C++ 测试服务，不直接暴露 `BlueprintCallable` 节点给蓝图使用。其工具和框架主要在自动化测试宏和测试夹具中使用。

## C++ 用法

### 头文件引入

```cpp
#include "MassAITestSuiteModule.h"
```

### 基本用法

此模块的核心用途是**编写和运行自动化测试**。通常，测试用例使用 `IMPLEMENT_SIMPLE_AUTOMATION_TEST` 或类似的宏定义，并使用 `GIVEN`/`WHEN`/`THEN` 的 BDD 风格进行组织。

从模块定义中可以看到其标准接口。一个典型的测试可能会使用此模块提供的任何特定工具或夹具（Fixtures），并依赖 `MassNavigation`、`MassZoneGraphNavigation` 等被测模块。

**示例：检查模块可用性 (来自 `MassAITestSuiteModule.h`)**
```cpp
// 在一个测试开始前，可以检查相关模块是否可用
if (IMassAITestSuiteModule::IsAvailable())
{
    // 模块已加载，可以使用其提供的测试工具（如果有的话）
    // 通常，测试工具是通过特定的 #include 和类来使用的
}
```

### 进阶用法

实际的测试代码将依赖于具体的测试场景。例如，一个测试 `MassNavigation` 动态避障的测试用例可能需要：
1. 创建一个临时的世界（World）。
2. 生成多个带有 `MassMovement` 和 `MassAvoidance` 组件的实体。
3. 给它们设置碰撞或移动目标。
4. 运行一个或多个 Tick。
5. 验证实体的最终位置、速度或轨迹是否符合预期的避障逻辑。

具体的测试用例文件（通常位于类似 `Tests/` 的目录中）是理解如何编写此类测试的最佳参考。

## Demo 示例

此模块是测试工具集，没有传统意义上的“可运行 Demo”。其“示例”就是其内部包含的众多自动化测试用例。要查看和运行这些测试，可以在 UE5 编辑器的“Session Frontend”或命令行中使用自动化测试命令。

## 模块依赖

从 `MassAITestSuite.Build.cs` 可以看到其唯一明确列出的特殊依赖：

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 提供编辑器和测试框架所需的基础支持，因为自动化测试通常运行在编辑器环境或特定的测试构建中。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8e83e6bf` | Remove use of INFINITY to fix compile error on latest Windows SDK | 修复在新 Windows SDK 下的编译错误。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下的双精度常量截断警告。 |
| 2026-05-12 | `328c7999` | [Mass] PR #14001: Fix Mass debugger running with invalid entity | 修复 Mass 调试器处理无效实体时的运行问题。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复用于格式化函数的作用域枚举可能导致的乱码输出。 |
| 2026-04-15 | `4b250a9d` | [RewindDebugger] | （提交信息不完整）与回放调试器相关的改动。 |

### 维护评价

*   **活跃维护**：从 git 日志看，`MassAI` 插件整体（包括此测试模块）在 2026 年 5 月仍有活跃的代码提交，主要是编译器警告修复、调试器改进和兼容性修复。这表明 Epic 仍在积极维护此插件。
*   **实验性状态**：`IsExperimentalVersion: true` 且默认禁用 (`EnabledByDefault: false`)，说明此插件（及其模块）仍被视为实验性功能，API 和实现可能在未来版本中发生变化。
*   **重要性**：虽然此模块不直接产生游戏逻辑，但它是保证 `MassAI` 可靠性的关键组成部分。随着 `MassAI` 的持续开发，此测试套件也会同步更新。
*   **推荐使用**：对于需要深入定制或验证 `MassAI` 行为的高级用户，参考并扩展此测试套件是理解系统内部机制的有效方式。但对于普通游戏逻辑开发，无需直接与此模块交互。

## 相关链接

*   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI/Source/MassAITestSuite)
*   [父级插件 MassAI 文档](./MassAI/index.md)
*   [相关模块 MassNavigation 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI/Source/MassNavigation)
*   [UE5 自动化测试框架文档](https://docs.unrealengine.com/5.0/en-US/automation-testing-in-unreal-engine/)