# Metasounds Experimental

> Metasound developmental plugin, for new features before they are ready for prime time

| 属性 | 值 |
|---|---|
| 中文名 | 元声实验性功能 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（实验性节点与资产） |
| 模块 | `AudioExperimentalRuntime` (Runtime), `MetasoundExperimentalRuntime` (Runtime), `MetasoundExperimentalEngineRuntime` (Runtime), `MetasoundExperimentalEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental) | |

## 用途

该插件是 **MetaSound 音频引擎的实验性开发分支**，用于集成和测试尚未准备好进入正式版本的新特性与功能。它并非面向最终用户的生产工具，而是为 MetaSound 开发者和音效设计师提供一个平台，以便在正式发布前预览、测试并反馈最新的音频处理节点、数据类型和工作流改进。从近期提交记录来看，它正在开发诸如 **Channel Agnostic Types (CAT) Wave** 这样的新数据格式以及与之配套的实验性处理节点（如乘法器、梯形滤波器）。

## 使用场景

- 你是 MetaSound 系统的开发者或资深用户，希望尝试和反馈最新的实验性功能。
- 你需要使用尚未在主插件 `Metasound` 中发布的特定音频处理节点（如 Channel Agnostic Types 相关的节点）。
- 你正在为引擎贡献新功能或修复，需要在一个隔离的实验性模块中进行开发和测试。

## 蓝图用法

由于此插件性质特殊，其提供的蓝图功能主要是实验性的 MetaSound 节点。这些节点通常会在插件启用后，在 MetaSound 编辑器的节点列表中出现。

### 核心节点

基于模块和提交历史推断，可能包含的节点类型包括：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Multiply` (CAT) | 对通道无关类型 (CAT) 音频信号进行乘法运算的实验性节点。 | （实验性节点类） |
| `Ladder Filter` (CAT) | 一种梯形滤波器节点，用于处理 CAT 类型的音频信号。 | （实验性节点类） |
| Wave Player (CAT) | 用于播放 Channel Agnostic Types Wave 资产的节点。 | （实验性节点类） |

### 使用示例（蓝图描述）

1.  确保在项目设置中启用 `MetasoundExperimental` 插件。
2.  打开或创建一个 MetaSound 资产。
3.  在节点搜索面板中，输入 “CAT” 或具体的实验性节点名称（如 “Ladder Filter”）。
4.  将搜索到的实验性节点拖放到 MetaSound 图表中，即可像使用标准节点一样进行连线使用。

## C++ 用法

由于是实验性插件，其 C++ 接口主要用于内部开发或高级扩展。使用时需谨慎，因为 API 可能在后续版本中发生不兼容的更改。

### 头文件引入

根据要使用的模块，引入对应的头文件。
```cpp
// 示例：若需使用 AudioExperimentalRuntime 模块的功能
#include "AudioExperimentalRuntime/AudioExperimentalRuntime.h"
```

### 基本用法

该插件的代码主要用于扩展 MetaSound 引擎。以下为一个概念性示例，展示如何在一个自定义模块中依赖此插件的运行时模块。
```cpp
// 在你的模块的 Build.cs 文件中，添加对实验性模块的依赖。
// 假设你要创建一个使用 CAT 功能的自定义模块。
using UnrealBuildTool;

public class MyAwesomeModule : ModuleRules
{
    public MyAwesomeModule(ReadOnlyTargetRules Target) : base(Target)
    {
        PublicDependencyModuleNames.AddRange(new string[] {
            "Core",
            "Metasound",
            "MetasoundExperimentalRuntime" // 依赖实验性运行时模块
        });
    }
}
```
在代码中，你可能会遇到处理 `ChannelAgnosticType` 等新类型的类或函数，但这些通常被视为内部实现细节。

### 进阶用法

插件内部可能通过 `UE::Metasound::Experimental` 等命名空间来提供功能。开发者更可能的工作是**贡献代码**到这些模块，而非在自己的项目中直接调用其 API。查看 `Source/` 目录下的 `.Build.cs` 文件是了解模块间依赖关系的最可靠方式。

## Demo 示例

由于该插件是内部实验性框架，提供可直接调用的公开 API 示例较少。以下是一个概念性的、展示模块依赖关系的最小模块示例。

**MyExperimentalFeatureModule.Build.cs**
```csharp
using UnrealBuildTool;

public class MyExperimentalFeatureModule : ModuleRules
{
    public MyExperimentalFeatureModule(ReadOnlyTargetRules Target) : base(Target)
    {
        PublicDependencyModuleNames.AddRange(new string[] {
            "Core",
            "CoreUObject",
            "Engine",
            "Metasound", // 核心 MetaSound 模块
            "MetasoundExperimentalRuntime" // 依赖实验性运行时
        });
    }
}
```

**MyExperimentalNode.h** (概念性)
```cpp
#pragma once
#include "MetasoundNodeInterface.h"
// 假设这里会包含实验性类型相关的头文件

namespace UE::MyPlugin
{
    // 一个使用实验性CAT类型的自定义节点概念
    class FMyCustomCATNode : public Metasound::FNode
    {
        // ... 实现细节
    };
}
```

## 模块依赖

使用此插件前，你的项目或模块通常需要依赖其父插件 `Metasound`。

| 模块 | 用途 |
|---|---|
| `Metasound` | 父插件，提供核心的 MetaSound 引擎和节点框架。必须首先启用。 |
| `CoreUObject` | `AudioExperimentalRuntime`、`MetasoundExperimentalEngineRuntime`、`MetasoundExperimentalRuntime` 模块的基础依赖。 |
| *（其他标准模块）* | 作为运行时或编辑器插件，还隐含依赖 Core, Engine, Slate 等标准模块。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `e4fa3490` | Adds the experimental MetaSound Channel Agnostic Types (CAT) Wave | 新增实验性的 MetaSound 通道无关类型 (CAT) 波形功能 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决了与 FSoundWaveData API 弃用相关的合并冲突 |
| 2026-05-12 | `ca21145e` | [CAT] Multiply node | [CAT] 新增乘法节点 |
| 2026-05-12 | `2940bc45` | [CAT] Ladder Filter node | [CAT] 新增梯形滤波器节点 |
| 2026-04-17 | `f1f7082c` | Unshelved from pending changelist '52759261': | 从待处理变更列表中恢复 |

### 维护评价

**活跃维护**。

该插件创建于 2025 年 4 月，历史很短。从近期的提交记录（截至文档生成时）可以看出，开发活动非常密集，最新更新集中在 2026 年 5 月，持续添加新的实验性节点和数据类型（CAT）。这明确表明它正处于**积极开发阶段**，是 MetaSound 核心功能迭代的前沿阵地。

**风险提示**：
1.  **实验性**：该插件明确标记为实验性 (`IsExperimentalVersion`)，且默认未启用。这意味着其 API、功能和资产格式在正式版中可能被大幅修改甚至移除。
2.  **依赖性**：它强依赖于 `Metasound` 主插件，且其内部实现会紧跟 `Metasound` 的变化。
3.  **目标用户**：主要面向引擎开发者、音效工具链开发者以及希望试用最前沿功能的技术美术和音效设计师，不建议在需要稳定性的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental)
- 官方文档：无
- [测试用例]：插件目录下通常包含测试代码，可查阅 `Source/*/Tests/` 目录。