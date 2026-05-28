# NNERuntime IREE

> A runtime implementing the Neural Network Engine (NNE) API which is based on IREE, MLIR and LLVM and compiles neural networks directly to game code.

| 属性 | 值 |
|---|---|
| 中文名 | IREE 神经网络运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNERuntimeIREE` (Runtime), `NNERuntimeIREEEditor` (Runtime), `NNERuntimeIREEShader` (Runtime), `IREEDriverRDG` (Runtime), `IREETracing` (Runtime), `IREEUtils` (Runtime), `IREE` (External), `NNEMlirTools` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeIREE) | |

## 用途

NNERuntimeIREE 是 UE5 神经网络引擎（NNE）的一个后端运行时实现，基于 Google 的 IREE（Intermediate Representation Execution Environment）框架。它的核心价值在于：**将训练好的神经网络模型直接编译为原生机器码**，而非传统的解释执行方式。

与 UE5 内置的 ONNX Runtime CPU 后端（NNEORTCpu）相比，IREE 后端有以下优势：

- **平台无关的高性能 CPU 执行**：基于 MLIR/LLVM 编译流水线，生成针对目标平台优化的原生代码
- **更广泛的平台支持**：超出 ORT CPU 后端的平台覆盖范围
- **更优的小模型性能**：对游戏实时推理场景中的小型神经网络，性能优于 ORT
- **持续扩展的模型支持**：基于 MLIR 的模块化架构，模型算子支持在不断增长
- **GPU 计算着色器支持**：通过 NNERuntimeIREEShader 和 IREEDriverRDG 模块，支持将神经网络编译为 RDG（Render Dependency Graph）计算着色器在 GPU 上执行

本质上，这个插件解决的问题是：**在游戏运行时以最低延迟执行小型神经网络推理**，适用于需要实时 AI 推理的游戏场景。

## 使用场景

- 你需要在游戏运行时实时执行神经网络推理（如 NPC 行为决策、图像处理后效、程序化内容生成）
- 你需要一个比 ONNX Runtime CPU 后端更快的 CPU 推理后端
- 你需要将神经网络编译为 GPU 计算着色器以获得更高吞吐量
- 你需要跨平台部署已训练的 ML 模型（PC、主机、移动端）
- 你的项目需要在 CPU 和 GPU 之间灵活选择推理后端

**注意**：这是一个实验性插件，`IsExperimentalVersion=true`，默认未启用。需在项目设置中手动启用。

## 蓝图用法

本插件作为 NNE 后端运行时，不直接暴露蓝图节点。它通过 NNE（Neural Network Engine）插件的统一 API 间接使用。用户通过 NNE 的 `UNNEModelData` 资产和 `INNERuntimeInstance` 接口加载模型并执行推理，NNERuntimeIREE 会自动被 NNE 系统发现并作为可用后端之一。

### 核心交互方式

| 操作 | 说明 |
|---|---|
| 加载模型 | 通过 NNE 的 `LoadModel` API 加载 ONNX 格式的模型数据 |
| 创建运行时实例 | NNE 系统自动选择 IREE 后端（如果可用） |
| 执行推理 | 通过 NNE 统一 API 设置输入张量并执行推理 |
| 选择 CPU/GPU 后端 | IREE CPU 后端和 IREE Shader 后端分别对应不同的后端标识符 |

### 使用示例（蓝图描述）

1. 在项目设置中启用 NNERuntimeIREE 插件
2. 导入 ONNX 格式的神经网络模型资产
3. 通过 NNE 的 `CreateModelData` / `LoadModel` 蓝图节点加载模型
4. 使用 NNE 的推理节点执行前向传播

## C++ 用法

### 头文件引入

```cpp
#include "NNERuntimeIREE.h"
```

### 基本用法

NNERuntimeIREE 作为 NNE 后端运行时，通过 NNE 插件的统一 C++ API 使用。以下是通过 IREE 运行时执行推理的典型流程：

```cpp
// 来源: NNE 框架统一接口
#include "NNE.h"
#include "NNERuntimeIREE.h"

// 获取 NNE 运行时实例
TArray<INNERuntime*> Runtimes = UE::NNE::GetAllRuntimes();
INNERuntime* IRuntime = nullptr;
for (INNERuntime* Runtime : Runtimes)
{
    if (Runtime->GetName() == TEXT("NNERuntimeIREE"))
    {
        IRuntime = Runtime;
        break;
    }
}

// 创建模型数据
TArray<uint8> ModelData; // 从 .onnx 文件加载的原始数据
TArray<INNERuntime::FTensorDesc> InputDescs;
TArray<INNERuntime::FTensorDesc> OutputDescs;

// 创建运行时模型
TObjectPtr<INNERuntimeModel> Model = IRuntime->CreateModel(ModelData, InputDescs, OutputDescs);
```

### 进阶用法：GPU 计算着色器路径

通过 IREE 的 RDG 驱动模块，神经网络可被编译为 UE5 渲染管线中的计算着色器：

```cpp
// NNERuntimeIREEShader 模块提供 GPU 推理路径
// IREEDriverRDG 负责将 IREE 编译结果桥接到 UE5 的 RDG 系统
// 具体使用方式取决于 NNE Shader 后端的集成方式
```

## Demo 示例

由于 NNERuntimeIREE 是 NNE 的后端运行时，完整示例需要配合 NNE 插件使用。以下是一个最小可编译示例，展示如何在代码中引用并测试 IREE 后端是否可用：

```cpp
// NNERuntimeIREETest.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NNERuntimeIREETest.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UNNERuntimeIREETest : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "ML|Test")
    bool IsIRERuntimeAvailable() const;
};
```

```cpp
// NNERuntimeIREETest.cpp
#include "NNERuntimeIREETest.h"
#include "NNE.h"

void UNNERuntimeIREETest::BeginPlay()
{
    Super::BeginPlay();
    
    if (IsIRERuntimeAvailable())
    {
        UE_LOG(LogTemp, Log, TEXT("IREE Neural Network Runtime is available"));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("IREE Neural Network Runtime is NOT available"));
    }
}

bool UNNERuntimeIREETest::IsIRERuntimeAvailable() const
{
    TArray<INNERuntime*> Runtimes = UE::NNE::GetAllRuntimes();
    for (const INNERuntime* Runtime : Runtimes)
    {
        if (Runtime && Runtime->GetName().Contains(TEXT("IREE")))
        {
            return true;
        }
    }
    return false;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NNE` | Neural Network Engine 核心框架，提供统一的模型加载和推理 API |
| `RenderCore` | 渲染核心模块，IREEDriverRDG 需要通过 RDG 提交计算着色器 |
| `RHI` | 渲染硬件接口，GPU 推理路径需要 |
| `IREETracing` | IREE 内部追踪/性能分析基础设施 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `9456b28d` | [NNE] NNERuntimeIREERdg fix cross-thread use-after-free during shader cook. | 修复 RDG 模块在着色器编译期间的跨线程 use-after-free 内存安全问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式化字符串不匹配问题 |
| 2026-04-15 | `2a295e97` | Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 重构 GPU 同步接口，合并为统一的提交并等待方法 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF 新格式 |
| 2026-04-09 | `e0689004` | [shaders] remove explicit finalized/released flags from job struct, replace with extended/refactored | 重构着色器作业的状态管理，移除冗余标志位 |

### 维护评价

**活跃维护中** ✅

- **年龄**：约 2.5 年（2023-11 创建），属于较新的实验性插件
- **更新频率**：非常活跃，2026 年 4-5 月连续有多次实质性更新，涵盖内存安全修复、API 重构和平台兼容性修复
- **维护质量**：commit 涉及关键的内存安全修复（use-after-free）和 API 统一化，表明 Epic 内部在持续推进质量
- **实验性状态**：仍标记为 `IsExperimentalVersion=true`，尚未达到稳定版本
- **平台支持**：从初始 commit 可知支持主要平台，且基于 IREE/LLVM 的跨平台编译能力持续扩展

**推荐使用**：如果你的项目需要实时神经网络推理且能接受实验性 API 可能发生变化的风险，这是一个高质量且积极维护的后端选择。建议关注 NNE 主框架的稳定性，NNERuntimeIREE 作为后端会跟随 NNE 接口演进。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeIREE)
- [IREE 官方项目](https://iree.dev/)
- [MLIR 项目](https://mlir.llvm.org/)