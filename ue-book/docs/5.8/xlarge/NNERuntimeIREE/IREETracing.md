# NNERuntimeIREE

> A runtime implementing the Neural Network Engine (NNE) API which is based on IREE, MLIR and LLVM and compiles neural networks directly to game code.

| 属性 | 值 |
|---|---|
| 中文名 | NNE IREE 运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNERuntimeIREE` (Runtime), `NNERuntimeIREEEditor` (Runtime), `NNERuntimeIREEShader` (Runtime), `IREEDriverRDG` (Runtime), `IREETracing` (Runtime), `IREEUtils` (Runtime), `IREE` (External), `NNEMlirTools` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeIREE) | |

## 用途

NNERuntimeIREE 是 UE5 神经网络引擎 (NNE) 的一个运行时实现，基于 IREE、MLIR 和 LLVM 工具链。它的核心目的是为游戏运行时提供一个高性能、平台无关的 CPU 推理环境，用于替代之前的 ORT CPU 运行时。

**工作原理**：IREE 框架能够将神经网络模型直接编译为针对目标平台的优化机器码，而不是像传统方式那样在运行时解释执行。这意味着神经网络推理可以像游戏代码一样被高效执行，特别适合需要实时、低延迟推理的小型神经网络场景。

## 使用场景

-   **实时游戏内 AI 推理**：在游戏运行时（例如，用于 NPC 行为决策、环境感知或程序化内容生成）执行轻量级神经网络推理。
-   **需要平台通用性的 CPU 推理**：当项目需要部署到多个平台（Windows、主机、移动设备等），并希望获得一致且高性能的 CPU 推理能力时。
-   **对小网络性能要求高的场景**：根据官方描述，对于小型网络，IREE 的性能优于之前的 ORT 运行时。

## 蓝图用法

由于这是一个底层运行时插件，主要面向 C++ 开发者通过 NNE API 进行调用。其蓝图功能通常通过更上层的 NNE 系统（如 `UNNEModelData`）或自定义的蓝图函数库暴露。直接与 `NNERuntimeIREE` 交互的蓝图节点较少。

### 核心节点

本插件主要提供 C++ 运行时，不直接提供蓝图节点。其功能通过 NNE 引擎的通用蓝图接口（如 `RunModel`）间接使用，只要正确配置了此运行时，NNE 系统就会自动选择它。

## C++ 用法

开发者通常不直接调用此插件的内部函数，而是通过 UE5 的 `NNE` 模块提供的标准 API 来加载和运行模型。`NNERuntimeIREE` 会作为 `INNERuntime` 接口的实现被 NNE 系统自动发现和使用。

### 头文件引入

要使用 NNE 的通用 API，你需要引入：
```cpp
#include "NNE.h"
```

### 基本用法

以下是一个通过 NNE 通用 API 使用模型进行推理的示例。运行时的具体选择（IREE 或其他）由系统自动处理。

```cpp
// 包含 NNE 核心头文件
#include "NNE.h"
#include "NNERuntimeCPU.h" // 如果使用CPU运行时

// 1. 获取一个可用的运行时 (通常由系统自动选择，如 IREE)
TArray<INNERuntime*> Runtimes = NNE::GetAllRuntimes();
INNERuntime* Runtime = nullptr;
for (INNERuntime* R : Runtimes)
{
    // 可以根据运行时名称或能力进行筛选
    if (R && R->GetRuntimeName() == TEXT("NNERuntimeIREE"))
    {
        Runtime = R;
        break;
    }
}

// 2. 加载模型数据 (从资产或内存)
UNNEModelData* ModelData = LoadObject<UNNEModelData>(nullptr, TEXT("/Game/MyModel.MyModel"));

// 3. 使用运行时创建模型实例
INNERuntimeCPU* RuntimeCPU = Cast<INNERuntimeCPU>(Runtime);
if (RuntimeCPU && ModelData)
{
    TWeakObjectPtr<UNNERuntimeCPUModel> Model = RuntimeCPU->CreateModel(ModelData);
    if (Model.IsValid())
    {
        // 4. 准备输入张量
        TArray<FTensor> Inputs;
        // ... 配置输入数据 ...

        // 5. 运行推理
        Model->RunSync(Inputs, Outputs); // 或 RunAsync
    }
}
```

### 进阶用法

进阶用法涉及对 IREE 编译过程的干预、多线程优化以及与 RDG (渲染依赖图) 的集成（通过 `IREEDriverRDG` 模块），这些通常由引擎内部处理。开发者可以关注模型编译时的优化选项和运行时的内存管理策略。

## Demo 示例

本插件作为引擎的实验性功能，通常与 `NNERuntimeORTCpu` 等其他运行时一起，在引擎提供的 NNE 测试和示例项目中使用。开发者可以参考引擎测试项目中的 `NNE` 相关用例。

一个最小化的 C++ 使用示例片段如下（假设已正确配置项目和插件）：

```cpp
// NNEIREEExample.h
#pragma once
#include "CoreMinimal.h"
#include "NNE.h"

class UNNEModelData;

class FNNEIREEExample
{
public:
    void RunInference();
private:
    TWeakObjectPtr<UNNEModelData> LoadedModelData;
    INNERuntime* IREERuntime = nullptr;
};

// NNEIREEExample.cpp
#include "NNEIREEExample.h"
#include "NNERuntimeCPU.h"

void FNNEIREEExample::RunInference()
{
    // 查找 IREE 运行时
    for (INNERuntime* Runtime : NNE::GetAllRuntimes())
    {
        if (Runtime->GetRuntimeName() == TEXT("NNERuntimeIREE"))
        {
            IREERuntime = Runtime;
            break;
        }
    }

    if (!IREERuntime) return;

    // ... 加载模型数据 ...
    // ... 创建模型实例并运行推理（参考C++用法章节） ...
}
```

## 模块依赖

此插件具有复杂的内部模块依赖和外部依赖。从 `Build.cs` 文件分析，使用者主要需要依赖：

| 模块 | 用途 |
|---|---|
| `NNERuntimeIREE` | 核心运行时模块，实现 NNE 接口 |
| `IREE` | 封装的 IREE 运行时库 |
| `NNEMlirTools` | 提供 MLIR 工具链，用于模型编译 |
| `IREEUtils` | IREE 相关的工具函数 |

**注意**：由于此插件为实验性，其依赖关系可能随版本变动。使用者应主要依赖上层的 `NNE` 模块，其会自动处理与 `NNERuntimeIREE` 的链接。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `9456b28d` | [NNE] NNERuntimeIREERdg fix cross-thread use-after-free during shader cook. | 修复了着色器编译期间 RDG 运行时跨线程的 use-after-free 内存安全问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了格式化字符串中，参数为64位时却使用了32位格式说明符的问题，反之亦然。 |
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 重构了 GPU 同步接口，将两个函数合并为一个更明确的 `SubmitAndBlockUntilGPUIdle`。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移到新的 `UE_LOGF` 宏。 |
| 2026-04-09 | `e0689004` | [shaders] remove explicit finalized/released flags from job struct, replace with extended/refactored | 重构了着色器作业管理结构，移除了显式的 `finalized/released` 标志。 |

### 维护评价

-   **创建时间**：插件创建于 2023 年底，**年龄约 2 年**。
-   **活跃度**：从 git 日志看，**近期维护非常活跃**（最近一次更新在 2026 年 5 月）。提交集中在 Bug 修复（内存安全、格式化、同步问题）、代码重构和日志系统迁移上，表明开发团队仍在积极维护和改进代码质量。
-   **状态**：标记为 **实验性 (`IsExperimentalVersion: true`)**，表明其 API 和功能可能在未来版本中发生变化。
-   **推荐度**：由于其**持续活跃的维护**和对**高性能 CPU 推理**的需求，该项目**值得尝试和关注**，尤其适用于寻求平台通用性且模型规模较小的项目。但鉴于其**实验性**标签，不建议在对稳定性要求极高的核心生产环境中直接使用，建议密切跟踪引擎更新日志。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeIREE)
-   [官方文档]() (暂无)
-   [测试用例]() (通常位于引擎的 NNE 测试目录下，需在源码中搜索)