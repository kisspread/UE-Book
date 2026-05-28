# Visual Studio Integration

> Allows access to source code in Visual Studio.

| 属性 | 值 |
|---|---|
| 中文名 | VS源码访问 |
| 分类 | Programming |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `VisualStudioSourceCodeAccess` (Runtime), `VisualStudioSetup` (External) |
| 实验性 | 否 |
| 创建时间 | 2014-04-23 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/VisualStudioSourceCodeAccess) | |

## 用途

VisualStudioSourceCodeAccess 插件是 Unreal Engine 源代码访问框架的一个具体实现。它并非一个通用的开发工具，而是专门用于将 Unreal Editor 与 Microsoft Visual Studio IDE 进行深度集成。其主要功能是响应编辑器（如双击蓝图节点中的错误、点击编译错误信息）中的源代码导航请求，并自动在用户安装的 Visual Studio 中打开对应的源文件并跳转到指定行号。该插件是实现“在 Visual Studio 中编写 C++ 代码，通过 UE 编辑器进行编译和调试”这一核心工作流的关键一环。

## 使用场景

- **场景一：C++ 错误调试**：你在 UE 编辑器中编译项目时遇到 C++ 编译错误，在输出日志中双击错误信息。`VisualStudioSourceCodeAccess` 会调用系统中安装的 Visual Studio，并自动打开对应的 `.cpp` 或 `.h` 文件，同时将光标定位到出错的代码行。
- **场景二：蓝图与 C++ 交互**：你在蓝图图表中右键一个函数节点，选择“跳转到定义”，该插件负责在 Visual Studio 中打开该函数的 C++ 实现。
- **场景三：性能分析与代码审查**：使用 Unreal Insights 等工具分析性能数据时，如果某个函数耗时严重，点击该函数名可以直接在 Visual Studio 中查看其源代码，方便进行优化。

## 蓝图用法

该插件主要提供系统级的集成服务，其核心功能通过引擎内部的 `ISourceCodeAccessModule` 接口被调用，不直接暴露为蓝图可调用节点。对用户而言，其体验是自动化的，无需在蓝图中手动操作。

## C++ 用法

该插件不提供供游戏逻辑直接调用的公开 API。它的主要作用是被引擎的“源代码访问”模块 (`SourceCodeAccess`) 作为其中一个“访问器” (`Accessor`) 来管理和调用。

### 基本用法

通常，你不需要在你的游戏模块中直接引用或实例化此插件中的类。它的生命周期由 `SourceCodeAccess` 模块管理。以下示例展示了在理论上如何查询源代码访问模块，但实际使用中编辑器内部已自动处理。

```cpp
// 引擎内部使用（非游戏代码典型用法）
// 来自: Engine/Source/Developer/SourceCodeAccess/Public/ISourceCodeAccessModule.h
#include "ISourceCodeAccessModule.h"

// 在某个需要触发代码导航的地方
void SomeEditorFunction()
{
    IModuleInterface* Module = FModuleManager::Get().LoadModule(TEXT("SourceCodeAccess"));
    if (ISourceCodeAccessModule* SourceCodeAccessModule = static_cast<ISourceCodeAccessModule*>(Module))
    {
        // 获取当前活动的源代码访问器（可能是本插件，也可能是其他如RiderSourceCodeAccess）
        // 并通过它执行打开文件等操作。
        // 具体接口为 ICodeAccessAccessor。
    }
}
```

## Demo 示例

由于该插件的功能是引擎级别的集成，没有独立的、可嵌入游戏运行时的演示。其“演示”就是 UE 编辑器与 Visual Studio 的日常交互。开发者只需确保：

1.  已在系统中安装 Visual Studio。
2.  在 UE 编辑器的 **编辑(Editor) -> 编辑器偏好设置(Editor Preferences) -> 源代码(Source Code)** 中，将“源代码编辑器”设置为“Visual Studio”。
3.  进行包含 C++ 代码的项目操作时，相关文件会自动在 Visual Studio 中打开。

## 模块依赖

该插件的独特依赖体现在其与引擎热重载系统的集成上。

| 模块 | 用途 |
|---|---|
| `HotReload` | 提供热重载功能，允许在编辑器运行时重新编译 C++ 代码。此插件需要与热重载流程配合，以在代码更改后更新 Visual Studio 中的项目状态。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-16 | `270dc64a` | Fix unreachable code warnings | 修复了代码中无法到达的路径警告，属于代码清理。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏迁移至新格式，属于引擎日志系统适配。 |
| 2026-03-09 | `2be8aeed` | Remove experimental from Visual Studio 2026 support | 移除了对 Visual Studio 2026 支持的“实验性”标记，表明该支持已正式化。 |
| 2025-09-11 | `2b3128b4` | Experimental Visual Studio 2026 support | 增加了实验性的 Visual Studio 2026 版本支持。 |
| 2025-06-17 | `a2f48da5` | Fixed circular includes across the engine | 修复了跨引擎的循环头文件包含问题。 |

### 维护评价

**VisualStudioSourceCodeAccess** 是一个历史悠久且维护稳定的核心基础设施插件。自 2014 年创建以来，它一直是 UE 与 Visual Studio 集成的基石。

- **维护状态：活跃维护中**。尽管更新频率不高（最近一次功能性更新是添加 VS2026 支持），但近期（2026年）仍有编译警告修复和日志迁移等维护性提交，表明它仍处于持续维护状态。
- **核心价值**：对于使用 Visual Studio 进行 Unreal Engine C++ 开发的团队和开发者而言，此插件是**必不可少**的。它提供了无缝的代码导航体验，极大提升了开发效率。
- **稳定性**：作为一个长期存在的插件，其功能非常稳定，几乎不会引入破坏性变更。
- **注意事项**：该插件依赖于系统中正确安装的 Visual Studio。如果你使用其他 IDE（如 Rider、VSCode），则应使用对应的 `RiderSourceCodeAccess` 或 `VSCodeSourceCodeAccess` 插件。
- **推荐使用**：**强烈推荐**所有使用 Visual Studio 作为 C++ IDE 的 UE 开发者启用此插件。它是引擎的默认集成方案，开箱即用，无需额外配置（除了在编辑器偏好中选择 IDE）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/VisualStudioSourceCodeAccess)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/VisualStudioSourceCodeAccess/Tests) (如果存在)