# Niagara MRQ Support

> Contains a data interface that can be used to read Movie Render Queue information in Niagara simulations.

| 属性 | 值 |
|---|---|
| 中文名 | MRQ数据接口 |
| 分类 | FX |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NiagaraMRQ` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-07-27 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/NiagaraMRQ) | |

## 用途

此插件为 Niagara 粒子系统提供了一个专用的数据接口，用于在 **Movie Render Queue (MRQ)** 进行高质量离线渲染时，读取与渲染序列相关的关键时间信息。它解决的核心问题是：在使用 MRQ 进行电影级渲染时，Niagara 粒子系统的模拟需要与渲染队列的时间线（如当前时间采样索引、总采样数、序列帧率等）精确同步，以确保粒子效果（如烟雾、火焰）在最终渲染的每一帧或每个时间采样点上都表现正确，特别是当粒子行为依赖于时间（如动画、物理模拟）时。

## 使用场景

-   **电影级过场动画渲染**：当你使用 Movie Render Queue 来渲染包含 Niagara 粒子效果的过场动画或宣传视频时，你需要确保粒子效果在 MRQ 的高质量、高采样率渲染流程中表现正确，而不是依赖于实时游戏帧率。
-   **运动模糊与时间抗锯齿 (TAA)**：MRQ 通过在同一帧内进行多次时间采样来实现运动模糊等高级效果。此插件能让 Niagara 粒子系统感知到 `TemporalSampleIndex` 和 `TemporalSampleCount`，从而在粒子生成、运动和着色等环节做出相应调整，保证最终合成图像的正确性。
-   **基于序列帧率的精确模拟**：如果粒子系统的生命周期或行为动画需要以固定的电影帧率（如24fps）播放，而不是依赖游戏的可变帧率，此插件提供的 `SequenceFPS` 信息至关重要。

## 蓝图用法

该插件的核心功能通过 Niagara 数据接口暴露给蓝图。在 Niagara 编辑器中，你可以将 `MovieRenderQueue` 数据接口添加到你的发射器或系统中，然后通过蓝图节点读取其属性。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Temporal Sample Count` | 获取当前渲染帧在 MRQ 中配置的总时间采样数。 | `UNiagaraDataInterfaceMRQ` |
| `Get Temporal Sample Index` | 获取当前模拟正在处理的该帧的第几个时间采样（从0开始）。 | `UNiagaraDataInterfaceMRQ` |
| `Get Sequence FPS` | 获取 MRQ 序列配置的电影帧率。 | `UNiagaraDataInterfaceMRQ` |

### 使用示例（蓝图描述）

1.  在 Niagara 系统的发射器或系统脚本中，添加一个 `MovieRenderQueue` 数据接口。
2.  在蓝图模块或事件图中，通过 `Get Temporal Sample Count` 节点获取总采样数。
3.  你可以将这个值用于逻辑判断，例如，仅在第一个时间采样 (`Temporal Sample Index == 0`) 时生成大量粒子，以避免在后续采样点重复生成，从而优化性能或实现特定的视觉效果。
4.  使用 `Get Sequence FPS` 来驱动基于秒的粒子生命周期或动画，使其在离线渲染时与实时游戏中的行为保持一致。

## C++ 用法

此插件主要通过数据接口被 Niagara 系统内部调用，使用者通常无需直接编写 C++ 代码。但了解其工作原理有助于排查问题。数据接口 `UNiagaraDataInterfaceMRQ` 在每实例数据 (`PerInstanceData`) 中存储了从 MRQ 收集到的当前帧信息。

### 头文件引入

```cpp
#include "NiagaraDataInterfaceMRQ.h"
```

### 基本用法

虽然使用者主要通过蓝图交互，但下述代码片段展示了数据接口如何在内部更新其状态（基于 `Source/NiagaraMRQ/Private/NiagaraDataInterfaceMRQ.cpp` 中的逻辑）：

```cpp
// 在 PerInstanceTick 中，接口会查询当前的 MRQ 状态
bool UNiagaraDataInterfaceMRQ::PerInstanceTick(void* PerInstanceData, FNiagaraSystemInstance* SystemInstance, float DeltaSeconds)
{
    // 实际实现在 .cpp 中，此处为逻辑示例
    FPerInstanceData* InstanceData = static_cast<FPerInstanceData*>(PerInstanceData);
    if (SystemInstance)
    {
        // 从全局或渲染线程上下文获取 MRQ 信息
        // InstanceData->Active = MRQ 当前是否处于活动状态
        // InstanceData->TemporalSampleCount = MRQ 当前帧的总采样数
        // InstanceData->TemporalSampleIndex = 当前处理的采样索引
        // InstanceData->SequenceFPS = MRQ 序列的帧率
    }
    return true;
}
```

### 进阶用法

数据接口通过 `ProvidePerInstanceDataForRenderThread` 将这些信息从游戏线程传递到渲染线程，使得粒子模拟和渲染着色器 (GPU) 能够使用这些参数。GPU 端通过 `FShaderParameters` 结构体接收数据：

```cpp
// 着色器参数结构体定义 (NiagaraDataInterfaceMRQ.h)
BEGIN_SHADER_PARAMETER_STRUCT(FShaderParameters, )
    SHADER_PARAMETER(int32, Active)
    SHADER_PARAMETER(int32, TemporalSampleCount)
    SHADER_PARAMETER(int32, TemporalSampleIndex)
    SHADER_PARAMETER(float,  SequenceFPS)
END_SHADER_PARAMETER_STRUCT()
```

GPU 模拟脚本可以直接读取这些 `int32` 和 `float` 参数来控制粒子行为。

## Demo 示例

以下是一个最小示例，展示如何创建一个依赖 MRQ 时间信息的 Niagara 系统脚本（概念描述）。

**目标**：在每个新时间采样点（`TemporalSampleIndex == 0`）生成一批粒子。

**步骤**：
1.  创建一个新的 Niagara 系统和发射器。
2.  在发射器的“属性”面板中，添加一个“数据接口”模块，选择“Movie Render Queue”类型。
3.  在发射器的“生成”(Spawn) 事件中，添加一个“蓝图模块”。
4.  在蓝图模块中：
    -   从数据接口对象调用 `Get Temporal Sample Index`。
    -   使用“分支”(Branch) 节点，条件为 `返回值 == 0`。
    -   在 `True` 分支中，设置生成速率(Spawn Rate)为一个正值（如 100）。
    -   在 `False` 分支中，设置生成速率为 0。
5.  这样，粒子只会在每个渲染帧的第一次时间采样时被生成，避免了在运动模糊的后续采样点中重复生成。

## 模块依赖

从 `NiagaraMRQ.Build.cs` 文件可知，使用者需要依赖以下特殊模块：

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 该插件仅在编辑器环境下提供功能（用于设置、编译等），因此依赖此编辑器核心模块。 |

**注意**：由于此插件标记为 `EnabledByDefault: false`，你需要在项目的插件列表中手动启用它才能使用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-11-22 | `36771d79` | Updated uplugin descriptor files marked as both Experimental and Beta. Plugins with both flags in th... | 清理了同时标记为实验性和测试版的插件描述文件，进行了格式或状态调整。 |
| 2023-12-13 | `608f1437` | UNiagaraDataInterface::GetFunctions() improvements - part 1 | 对数据接口基类的函数获取机制进行了改进，可能影响本插件的功能注册。 |
| 2023-07-27 | `4f537bda` | - Niagara MovieRenderQueue plugin - Contains a data interface for inspecting MRQ information | 插件初始创建提交。 |

### 维护评价

-   **创建时间**：插件于 2023 年 7 月创建，相对较新。
-   **最近更新**：最近一次实质性功能更新（非格式调整）停留在 2023 年 12 月。过去一年内仅有一次描述文件的格式清理，**没有新功能或 bug 修复**。
-   **状态**：插件仍处于 **Beta** 实验阶段（`IsBetaVersion: true`），且默认未启用（`EnabledByDefault: false`）。这表明 Epic 可能仍在评估其 API 稳定性和必要性，但尚未正式将其投入生产级支持。
-   **推荐度**：**谨慎推荐**。如果你的项目依赖 Movie Render Queue 进行高质量渲染且包含粒子效果，这是实现时间同步的**唯一官方插件**，你**必须使用**它。但由于其 Beta 状态和低频维护，你可能需要自行承担一定的风险，并关注未来版本是否会有 API 变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/NiagaraMRQ)
- [官方文档]()（无）