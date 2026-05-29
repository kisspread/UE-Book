# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置资源） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-05-28 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一套用于从现实世界捕获的表演数据（如视频、深度信息、音频）驱动高保真 MetaHuman 数字角色的完整工具链。它解决的核心问题是**如何将演员的面部表情、口型、身体动作精确地映射并应用到虚拟的 MetaHuman 模型上**，从而创建出逼真、富有表现力的数字人类。该插件不仅包含用于处理捕获数据（如拟合、求解、追踪）的底层算法模块，还提供了用于资产管理、编辑器集成和批处理的上层工具。

## 使用场景

- 你需要将 iPhone 或专业动作捕捉设备录制的面部表演，实时或后期驱动一个 MetaHuman 角色。
- 你拥有一段演员说话的音频，希望基于此生成对应的口型和表情动画。
- 你想要从一段已有的表演视频中提取动作数据，并应用到另一个 MetaHuman 角色上。
- 你需要在编辑器中预览和调试面部追踪、拟合的效果，并批量处理多个捕获片段。

## 蓝图用法

由于该插件庞大且复杂，核心功能通常通过编辑器工具或 C++ 调用。以下是基于分析得出的关键蓝图可调用类和函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `LoadFaceFittingSolvers` | 加载用于面部拟合的求解器模型 | `UMetaHumanFaceFittingSolver` |
| `LoadPredictiveSolver` | 加载用于性能准备阶段的预测求解器 | `UMetaHumanFaceFittingSolver` |
| `CanProcess` | 检查当前求解器配置是否准备好进行处理 | `UMetaHumanFaceFittingSolver` |
| `GetFittingConfigData` | 获取用于面部拟合的配置数据（JSON字符串） | `UMetaHumanFaceFittingSolver` |
| `GetFittingIdentityModelData` | 获取用于面部拟合的身份模型数据 | `UMetaHumanFaceFittingSolver` |

### 使用示例（蓝图描述）

1.  **准备身份**：在 MetaHuman Identity 资产中，配置好 `Face Fitting Solver` 属性，指向一个 `MetaHumanFaceFittingSolver` 配置资产。
2.  **加载求解器**：在蓝图中，获取该 `MetaHumanFaceFittingSolver` 对象的引用，调用 `LoadFaceFittingSolvers` 节点。
3.  **获取数据**：调用 `GetFittingConfigData` 或类似节点，获取处理捕获数据所需的配置信息。
4.  **应用与驱动**：将获取的数据用于后续的 MetaHuman Performance 或 Pipeline 节点，以驱动角色动画。

## C++ 用法

### 头文件引入

```cpp
#include “MetaHumanFaceFittingSolver.h”
```

### 基本用法

以下示例展示了如何配置和使用 `UMetaHumanFaceFittingSolver`。
（来源： `Source/MetaHumanFaceFittingSolver/MetaHumanFaceFittingSolver.h`）

```cpp
// 创建求解器实例（通常在编辑器上下文中）
UMetaHumanFaceFittingSolver* FaceFittingSolver = NewObject<UMetaHumanFaceFittingSolver>();

// 设置配置（可选）
// FaceFittingSolver->DeviceConfig = MyCustomDeviceConfig;
// FaceFittingSolver->PredictiveSolver = MyPredictiveSolver;

// 加载求解器
FaceFittingSolver->LoadFaceFittingSolvers();
FaceFittingSolver->LoadPredictiveSolver();

// 检查是否可处理
if (FaceFittingSolver->CanProcess())
{
    // 获取配置数据（例如，传递给外部处理工具或用于内部Pipeline）
    FString ConfigJson = FaceFittingSolver->GetFittingConfigData(/* CaptureData */);
    FString IdentityModelData = FaceFittingSolver->GetFittingIdentityModelData(/* CaptureData */);

    // 使用 ConfigJson 和 IdentityModelData 进行后续处理...
}
```

### 进阶用法

结合 `UMetaHumanFaceAnimationSolver` 和 `UMetaHumanPipeline` 来构建完整的处理流程。

```cpp
// 假设已拥有 MetaHuman Pipeline 和相关的求解器实例
UMetaHumanPipeline* Pipeline = ...;
UMetaHumanFaceFittingSolver* FittingSolver = ...;
UMetaHumanFaceAnimationSolver* AnimationSolver = FittingSolver->FaceAnimationSolver;

// 从求解器获取预测训练数据（用于个性化求解器训练）
TArray<uint8> PredictiveTrainingData = FittingSolver->GetPredictiveTrainingData();

// 配置Pipeline并处理捕获数据
// Pipeline->SetSolverData(...);
// Pipeline->ProcessCaptureData(MyCaptureData);
```

## Demo 示例

一个用于初始化并查询面部拟合求解器配置的简单示例。

### MetaHumanFittingDemo.h
```cpp
#pragma once
#include "CoreMinimal.h”
#include “GameFramework/Actor.h”
#include “MetaHumanFaceFittingDemo.generated.h”

class UMetaHumanFaceFittingSolver;

UCLASS()
class AMetaHumanFaceFittingDemo : public AActor
{
    GENERATED_BODY()

public:
    AMetaHumanFaceFittingDemo();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = “MetaHuman”)
    TObjectPtr<UMetaHumanFaceFittingSolver> SolverConfig;

    UFUNCTION(BlueprintCallable, Category = “MetaHuman”)
    void PrintSolverStatus() const;
};
```

### MetaHumanFittingDemo.cpp
```cpp
#include “MetaHumanFaceFittingDemo.h”
#include “MetaHumanFaceFittingSolver.h”

AMetaHumanFaceFittingDemo::AMetaHumanFaceFittingDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMetaHumanFaceFittingDemo::BeginPlay()
{
    Super::BeginPlay();
    if (SolverConfig)
    {
        SolverConfig->LoadFaceFittingSolvers();
        PrintSolverStatus();
    }
}

void AMetaHumanFaceFittingDemo::PrintSolverStatus() const
{
    if (!SolverConfig)
    {
        UE_LOG(LogTemp, Warning, TEXT(“SolverConfig is null.”));
        return;
    }

    bool bReady = SolverConfig->CanProcess();
    FString ConfigData = SolverConfig->GetFittingConfigData();

    UE_LOG(LogTemp, Log, TEXT(“Face Fitting Solver Status: %s”), bReady ? TEXT(“Ready”) : TEXT(“Not Ready”));
    if (!ConfigData.IsEmpty())
    {
        UE_LOG(LogTemp, Log, TEXT(“Config Data (first 200 chars): %s”), *ConfigData.Left(200));
    }
}
```

## 模块依赖

由于插件内部模块众多，以下列出使用者可能直接依赖的关键模块。绝大多数功能通过编辑器工具或上层模块调用，直接使用底层模块的情况较少。

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | MetaHuman系统的核心类型、资产和通用功能 |
| `MetaHumanConfig` | 管理和加载MetaHuman求解器的配置数据（如`UMetaHumanConfig`） |
| `MetaHumanIdentity` | 处理MetaHuman身份资产（Identity Asset）的创建与管理 |
| `MetaHumanPipeline` | 定义和执行处理捕获数据的管线（Pipeline） |
| `MetaHumanPerformance` | 管理与MetaHuman表演（Performance）相关的资产和数据 |
| `MetaHumanToolkit` | 提供编辑器内的综合工具集 |
| `MetaHumanCaptureUtils` | 提供用于处理捕获数据（视频、深度、音频）的工具函数 |

**注意**：使用本插件通常需要同时启用 `MetaHumanSDK` 或 `MetaHumanCore` 作为基础。具体依赖需根据你要构建的功能（如仅使用求解器，或构建完整管线）进行选择。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复MetaHuman身上的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 为已有网格导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复Sequencer缓存问题 |

### 维护评价

MetaHuman Animator 是 Epic Games 官方维护的核心数字人工具，**维护非常活跃**。从 Git 历史看，近期（2026年5月）仍有密集的功能提交、Bug修复和优化。该插件自发布以来持续更新，以支持新的硬件（如专业动捕设备）、优化工作流程并修复问题。

**优点**：
- 官方支持，长期维护有保障。
- 功能全面，覆盖从数据捕获到角色驱动的全流程。
- 与UE5 Sequencer、Control Rig等核心系统深度集成。

**注意**：
- 插件庞大且复杂，学习曲线较陡。
- 部分高级功能（如专业捕捉协议集成）可能需要特定的外部软件或设备支持。
- 对于简单的面部动画，标准方案可能已足够，此插件更适合追求影视级或高精度数字人应用的场景。

**推荐使用**：对于需要创建高保真、基于真实表演驱动的 MetaHuman 数字人项目，**强烈推荐使用**此插件。它是实现这一目标的官方标准工具链。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/meta-humans-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest) (部分测试模块)