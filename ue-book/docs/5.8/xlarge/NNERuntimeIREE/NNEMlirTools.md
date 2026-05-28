# NNERuntimeIREE

> A runtime implementing the Neural Network Engine (NNE) API which is based on IREE, MLIR and LLVM and compiles neural networks directly to game code.

| 属性 | 值 |
|---|---|
| 中文名 | NNE IREE 运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `IREEDriverRDG` (Runtime), `IREETracing` (Runtime), `IREEUtils` (Runtime), `NNERuntimeIREE` (Runtime), `NNERuntimeIREEEditor` (Runtime), `NNERuntimeIREEShader` (Runtime), `IREE` (External), `NNEMlirTools` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeIREE) | |

## 用途

本插件是 Unreal Engine **Neural Network Engine (NNE)** 的一个运行时后端实现，其核心基于 **IREE**（基于 MLIR 和 LLVM 的机器学习编译器框架）。它的主要目标是将训练好的神经网络模型（如 ONNX 格式）**直接编译为高度优化的游戏原生代码**（CPU 或 GPU 着色器），以实现在游戏运行时进行高效、低延迟的神经网络推理。

与传统的运行时（如 ONNX Runtime CPU）相比，IREE 路径通过编译时优化，能为小规模网络提供更优的性能，并具有更好的跨平台兼容性。它解决了在实时游戏环境中部署和运行机器学习模型的技术挑战。

## 使用场景

- **实时 AI 增强玩法**：例如，使用一个轻量级网络根据玩家输入实时生成游戏环境变化，或用于智能 NPC 的决策。
- **游戏内风格化渲染**：实时将游戏画面风格化为特定艺术风格（如油画、卡通等）。
- **动画与物理增强**：使用神经网络来驱动或修正角色动画、模拟复杂的物理交互。
- **实验性游戏原型开发**：快速将研究中的神经网络模型集成到游戏原型中，验证想法。

## 蓝图用法

本插件的核心功能主要通过 C++ 接口暴露，旨在作为底层运行时被 UE 的 **NNE (Neural Network Engine)** 抽象层调用。直接的蓝图节点较少，通常开发者通过上层 NNE 蓝图接口间接使用此运行时。

### 核心节点（通过 NNE 间接使用）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Load Model` (NNE) | 加载神经网络模型资源，系统会根据模型格式和当前配置（如平台、性能需求）自动选择并初始化合适的运行时（如本插件的 NNERuntimeIREE）。 | `UNNEModelData` |
| `Create Runtime Instance` (NNE) | 为已加载的模型创建一个可执行的运行时实例（Session）。 | `UNNERuntime` |
| `Run Inference` (NNE) | 在运行时实例上执行一次推理，传入输入数据并获取输出结果。 | `UNNERuntime` |

### 使用示例（蓝图描述）

1.  **资产准备**：将训练好的 `.onnx` 模型文件导入 UE 内容浏览器，它将自动成为 `UNNEModelData` 资产。
2.  **蓝图配置**：
    *   在蓝图（如 Actor 或 Widget）中添加一个 `UNNEModelData` 变量，指向你的模型资产。
    *   使用 `Create Runtime Instance` 节点（需要传入模型数据）来创建一个 `UNNERuntime` 对象实例。系统在此阶段可能会调用 NNERuntimeIREE 的编译逻辑。
    *   准备输入张量（Tensor）数据。通常通过蓝图中的数组或专门的 `UNETensor` 类型构造。
    *   调用 `Run Inference` 节点，传入运行时实例和输入数据。
    *   解析输出张量数据，用于驱动游戏逻辑。

## C++ 用法

### 头文件引入

要使用本插件提供的运行时功能，通常需要通过 UE 的 NNE 抽象层。直接使用底层 IREE 接口需要引入相关头文件。

```cpp
// 引入 NNE 核心抽象
#include "NNE.h"
#include "NNEModelData.h"
#include "NNERuntime.h"

// 若需直接使用 IREE MLIR 工具（通常由引擎内部处理）
#include "IREEUtils.h"
#include "NNEMlirTools.h"
```

### 基本用法

通过 UE 的 NNE API 间接使用 IREE 运行时是推荐的方式。

```cpp
// 假设 `ModelData` 是一个指向已加载 UNNEModelData 的指针
void UseNERuntimeIREE(UNNEModelData* ModelData)
{
    // 1. 获取运行时实例（引擎将根据配置选择 NNERuntimeIREE 或其他后端）
    UNNERuntime* Runtime = NNE::GetRuntime(ModelData);
    if (!Runtime)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to get NNE Runtime"));
        return;
    }

    // 2. 为模型创建会话
    TWeakObjectPtr<UNNERuntime> RuntimeWeakPtr = Runtime;
    TWeakObjectPtr<UNNEModelData> ModelWeakPtr = ModelData;
    UNNE::FSessionCreateResult SessionResult = UNNE::CreateSession(RuntimeWeakPtr, ModelWeakPtr);
    if (SessionResult.Status != UNNE::EStatusCode::Success)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create session: %s"), *SessionResult.ErrorMessage);
        return;
    }
    TWeakObjectPtr<UNNE::FSession> Session = SessionResult.Session;

    // 3. 准备输入输出 (示例)
    TArray<float> InputData(10, 1.0f); // 示例输入
    TArray<float> OutputData;
    OutputData.SetNum(5); // 预分配输出空间

    // 4. 运行推理
    UNNE::FRunResult RunResult = UNNE::Run(Session, InputData, OutputData);
    if (RunResult.Status == UNNE::EStatusCode::Success)
    {
        // 处理 OutputData
        UE_LOG(LogTemp, Log, TEXT("Inference Success. Output[0]: %f"), OutputData[0]);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Inference Failed: %s"), *RunResult.ErrorMessage);
    }
}
```
*代码注释：展示了通过 `NNE::` 命名空间下的函数使用运行时的标准流程。*

### 进阶用法

更底层的控制或调试可能需要直接与 IREE 和 MLIR 工具交互。以下示例展示了如何解析一个 MLIR 模块（通常由编译链内部使用）。

```cpp
// 从 NNEMlirTools_cxx_api.h 中了解的 C++ 风格 API
void InspectMlirModule()
{
    // 1. 初始化 MLIR 上下文（假设 NNEMlirTools::Api 已被初始化）
    NNEMlirTools::Context MlirCtx;
    
    // 2. 从缓冲区解析 MLIR 模块（例如，从文件读取或编译器输出）
    // 假设 Buffer 包含 MLIR 字节码或文本
    const char* MlirBuffer = "..."; 
    size_t BufferSize = 1024;
    NNEMlirTools::Module MlirModule = NNEMlirTools::Module::ParseFromBuffer(MlirCtx, MlirBuffer, BufferSize);
    
    // 3. 检查模块中的函数（入口点）
    for (const auto& Func : MlirModule.GetFunctions())
    {
        UE_LOG(LogTemp, Log, TEXT("Function: %s"), *FString(Func.GetName().c_str()));
        
        // 检查输入
        for (const auto& Input : Func.GetInputs())
        {
            std::string ShapeText = Input.GetShapeTypeText(); // e.g., "1x3x224x224xf32"
            UE_LOG(LogTemp, Log, TEXT("  Input: %s, Shape: %s"), *FString(Input.GetName().c_str()), *FString(ShapeText.c_str()));
        }
        
        // 检查输出
        for (const auto& Result : Func.GetResults())
        {
            std::string ShapeText = Result.GetShapeTypeText();
            UE_LOG(LogTemp, Log, TEXT("  Result: Shape: %s"), *FString(ShapeText.c_str()));
        }
    }
    // Module, Context 会在作用域结束时自动释放
}
```
*代码注释：展示了使用 NNEMlirTools C++ API 进行 MLIR 模块内省的示例。此过程通常由插件内部的模型编译器自动完成。*

## Demo 示例

一个最小化的 C++ 示例，演示如何通过 NNE API 加载模型并执行一次推理。此示例假设模型已导入为 `UNNEModelData` 资产。

```cpp
// MyNNEDemoComponent.h
#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NNEModelData.h"
#include "NNERuntime.h"
#include "MyNNEDemoComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyNNEDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "NNE")
    UNNEModelData* MyModel;

    UFUNCTION(BlueprintCallable, Category = "NNE")
    void RunInferenceTest();

private:
    TWeakObjectPtr<UNNE::FSession> CurrentSession;
};
```

```cpp
// MyNNEDemoComponent.cpp
#include "MyNNEDemoComponent.h"
#include "NNE.h"

void UMyNNEDemoComponent::RunInferenceTest()
{
    if (!MyModel)
    {
        UE_LOG(LogTemp, Warning, TEXT("MyModel is not set."));
        return;
    }

    // 尝试创建或重用会话
    if (!CurrentSession.IsValid())
    {
        UNNERuntime* Runtime = NNE::GetRuntime(MyModel);
        if (!Runtime)
        {
            UE_LOG(LogTemp, Error, TEXT("No runtime found for model."));
            return;
        }
        
        UNNE::FSessionCreateResult Result = UNNE::CreateSession(Runtime, MyModel);
        if (Result.Status != UNNE::EStatusCode::Success)
        {
            UE_LOG(LogTemp, Error, TEXT("Session creation failed: %s"), *Result.ErrorMessage);
            return;
        }
        CurrentSession = Result.Session;
    }

    // 准备虚拟输入 (根据你的模型调整大小和数据)
    TArray<float> InputData;
    InputData.SetNumZeroed(1024); // 例如，一个长度为1024的一维输入

    TArray<float> OutputData;
    OutputData.SetNumZeroed(10); // 预分配输出

    // 执行推理
    UNNE::FRunResult RunResult = UNNE::Run(CurrentSession, InputData, OutputData);
    if (RunResult.Status == UNNE::EStatusCode::Success)
    {
        UE_LOG(LogTemp, Log, TEXT("Inference completed! First output: %f"), OutputData[0]);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Inference failed: %s"), *RunResult.ErrorMessage);
        // 可能需要重建会话
        CurrentSession.Reset();
    }
}
```
*代码注释：一个可放入 Actor 的组件示例，通过蓝图编辑器设置模型资产，并调用函数执行推理。*

## 模块依赖

要使用 `NNERuntimeIREE` 插件，你的项目模块需要在 `Build.cs` 文件中添加以下依赖。除了常见的 Core, Engine 等，以下是该插件特有的关键依赖：

| 模块 | 用途 |
|---|---|
| `NNE` | UE 神经网络引擎核心抽象层，是访问所有 NNE 运行时（包括本插件）的主接口。 |
| `IREE` | IREE 运行时的外部依赖封装模块。 |
| `IREEUtils` | 提供 IREE 相关的实用工具函数和类型。 |
| `IREETracing` | 可能提供 IREE 相关的性能追踪或调试功能。 |
| `NNEMlirTools` | 提供用于解析和检查 MLIR 模块的 C/C++ 工具接口。 |

在你的 `.Build.cs` 文件中，应类似如下添加：
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "Engine",
    "NNE", // 核心依赖
    "IREE",
    "IREEUtils",
    "NNEMlirTools"
});
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `9456b28d` | [NNE] NNERuntimeIREERdg fix cross-thread use-after-free during shader cook. | 修复了着色器编译期间跨线程的 use-after-free 内存错误。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了 32/64 位格式说明符与参数位数不匹配的错误，提高了代码健壮性。 |
| 2026-04-15 | `2a295e97` | Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 清理和统一了 GPU 命令提交与同步的接口。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到新的 UE_LOGF 格式。 |
| 2026-04-09 | `e0689004` | [shaders] remove explicit finalized/released flags from job struct, replace with extended/refactored | 重构了着色器作业管理，移除了显式的状态标志，使代码更清晰。 |

### 维护评价

- **活跃度**：该插件近期（2026年4-5月）有多次代码提交，包含重要的**错误修复**（内存安全、格式化）和**代码重构**，表明它仍处于**积极维护**中。
- **状态**：`.uplugin` 中 `IsExperimentalVersion = true`，`EnabledByDefault = false`，明确标记为**实验性功能**。这意味着 API 可能会发生变化，不建议在生产环境的核心功能中依赖它。
- **推荐度**：适合用于**研究、原型开发和学习**UE中的ML集成。由于其活跃维护和实验性质，它是一个了解前沿游戏AI集成技术的好途径。对于生产项目，需要密切关注版本更新和API变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeIREE)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeIREE/Tests) (路径推断，需确认是否存在)