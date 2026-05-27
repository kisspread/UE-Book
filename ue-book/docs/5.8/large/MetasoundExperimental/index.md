# Metasounds Experimental

> Metasound developmental plugin, for new features before they are ready for prime time

| 属性 | 值 |
|---|---|
| 中文名 | 元声音实验性插件 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产，可能包含实验性节点、波形资产等） |
| 模块 | `AudioExperimentalRuntime` (Runtime), `MetasoundExperimentalRuntime` (Runtime), `MetasoundExperimentalEngineRuntime` (Runtime), `MetasoundExperimentalEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental) | |

## 用途

本插件是 **MetaSound 音频系统的实验性扩展**。它主要用于开发和测试尚未准备就绪、不面向正式发布的新 MetaSound 功能和节点。其核心价值在于为音频设计师和程序员提供一个安全的沙盒环境，以提前探索和验证下一代音频处理功能，例如新的波形类型（如通道无关类型 CAT）、信号生成与处理节点。

## 使用场景

-   **音频原型设计**：你想在项目中尝试一种全新的声音合成或处理方式，但该功能尚未集成到稳定的 MetaSound 核心中。
-   **参与早期功能测试**：作为音频开发者，你希望提前使用 Epic 正在开发的新音频节点（如 CAT 波形处理、新型滤波器），并提供反馈。
-   **内部技术预研**：在生产环境的 MetaSound 图稳定之前，使用本插件的功能进行可行性验证和概念证明。

## 蓝图用法

本插件中的实验性功能通常以新的 MetaSound 节点（算子）和数据类型的形式提供，而非传统的蓝图节点。其用法主要体现在 MetaSound 编辑器的图表中。

### 核心节点 (MetaSound 算子)

| 节点 | 说明 | 所在类/系统 |
|---|---|---|
| `CAT Wave` | 处理或生成 Channel Agnostic Type（CAT）波形数据 | `AudioExperimentalRuntime` |
| `Multiply` (CAT) | 对 CAT 类型数据进行乘法运算 | `MetasoundExperimentalRuntime` |
| `Ladder Filter` | 一种梯形滤波器实验性节点 | `MetasoundExperimentalRuntime` |
| `...` | 其他实验性音频处理算子 | 各运行时模块 |

### 使用示例（MetaSound 图描述）

1.  在 MetaSound 编辑器中，右键点击图表，从“实验性”类别中拖入新的 `CAT Wave` 节点。
2.  将 `Ladder Filter` 节点连接到某个音频输出，调整其参数以观察不同的滤波效果。
3.  使用 `Multiply` (CAT) 节点对两个 CAT 信号进行调制或混合。

## C++ 用法

在 C++ 中，你通常需要包含对应模块的头文件来访问实验性的数据类型和底层功能。

### 头文件引入

```cpp
#include "MetasoundExperimentalRuntime.h" // 访问实验性运行时类型和节点
#include "AudioExperimentalRuntime.h"     // 访问基础实验性音频功能
```

### 基本用法

实验性插件的核心用法在于**实现新的 MetaSound 节点（算子）**。你需要在自己的模块中定义新的算子类，并利用本插件提供的实验性数据类型（如 `FWaveAsset` 的 CAT 变体）。

```cpp
// 示例：声明一个使用实验性 CAT 数据类型的自定义 MetaSound 算子
#include "MetasoundVertex.h"
#include "MetasoundParamHelper.h"

class FMyExperimentalOperator : public TExecutableOperator<FMyExperimentalOperator>
{
public:
    // 定义使用实验性 CAT 波形数据的输入输出顶点
    static const FVertexInterface& GetVertexInterface()
    {
        static const FVertexInterface Interface(
            FInputVertexInterface(
                // 假设有一个名为 “InCATWave” 的实验性 CAT 波形输入
                TInputDataVertex<FWaveAsset>(METASOUND_GET_PARAM_NAME_AND_METADATA(TEXT("InCATWave")))
            ),
            FOutputVertexInterface(
                // ...输出定义
            )
        );
        return Interface;
    }
    // ... 算子逻辑实现
};
```

## Demo 示例

由于插件本身包含测试用例，一个最小的使用示例是参考其单元测试来创建新的算子。

**MyExperimentalOperator.h**
```cpp
#pragma once
#include "MetasoundOperatorInterface.h"
#include "MetasoundNodeInterface.h"

// 一个实验性算子，可能处理某种新型波形数据
class FMyCATWaveProcessorOperator : public Metasound::FMetaSoundOperator
{
public:
    FMyCATWaveProcessorOperator(/* 依赖项 */);
    virtual ~FMyCATWaveProcessorOperator() = default;

    // 执行处理
    virtual void Execute() override;

    // ... 其他必要接口实现
};
```

**MyExperimentalOperator.cpp**
```cpp
#include "MyExperimentalOperator.h"

FMyCATWaveProcessorOperator::FMyCATWProcessorOperator(/* 依赖项 */)
{
    // 初始化
}

void FMyCATWaveProcessorOperator::Execute()
{
    // 从输入获取实验性 CAT 波形数据
    // 应用某种实验性处理算法
    // 将结果写入输出
}
```

## 模块依赖

无特殊依赖（仅标准 Core/CoreUObject）。

| 模块 | 用途 |
|---|---|
| `Metasound` | **必需**。作为本插件的父系统，提供 MetaSound 框架的核心类型、接口和图编辑功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `e4fa3490` | Adds the experimental MetaSound Channel Agnostic Types (CAT) Wave | 添加了实验性的 MetaSound 通道无关类型（CAT）波形 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决了与 FSoundWaveData API 废弃修正相关的合并冲突 |
| 2026-05-12 | `ca21145e` | [CAT] Multiply node | [CAT] 乘法节点 |
| 2026-05-12 | `2940bc45` | [CAT] Ladder Filter node | [CAT] 梯形滤波器节点 |
| 2026-04-17 | `f1f7082c` | Unshelved from pending changelist '52759261': | 从待处理变更列表‘52759261’中取出 |

### 维护评价

该插件创建于2025年4月，**目前处于活跃开发中**。最近的提交集中在2026年5月，主要是围绕“通道无关类型（CAT）”这一新特性的波形支持和节点开发（如Multiply和Ladder Filter），表明 Epic 正在持续为其注入新的实验性音频功能。

**注意事项**：
1.  **高度实验性**：作为 `IsExperimentalVersion = true` 且 `EnabledByDefault = false` 的插件，其API和功能在引擎版本更新时**可能发生变化、被移除或合并到主系统中**，不适合作为长期生产依赖。
2.  **适用人群**：适合**敢于尝试、且能够应对不稳定变化**的音频技术探索者、Epic 内部开发者或希望参与早期功能测试的社区成员。
3.  **推荐使用**：如果你希望**提前体验和测试 MetaSound 的未来发展方向**，此插件是必装项。对于追求稳定性的正式项目，应避免依赖此插件的功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetasoundExperimental/Tests) (假设位于 `Tests` 目录)