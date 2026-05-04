# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（动画资产、配置数据） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一个完整的工具包，旨在将真实的面部表演（通常来自视频捕捉）转换为可用于驱动 MetaHuman 角色的高质量动画数据。它不仅仅是一个单一的求解器，而是一个包含数据导入、处理、求解和输出的完整流程管线。

该插件解决的核心问题是：如何从原始的视频或深度数据中，精确地提取面部肌肉运动信息，并将其映射到 MetaHuman 的骨骼和控制装置上，从而生成逼真、可编辑的面部动画。它为动画师和技术美术提供了一套标准化的工具，简化了从表演捕捉到最终动画资产的制作流程。

## 使用场景

- **影视与游戏过场动画制作**：你有一段演员的面部表演视频，希望将其快速、准确地应用到你的 MetaHuman 角色上，用于制作高质量的过场动画。
- **实时虚拟人驱动**：你需要一个能够实时或近实时地将摄像头捕捉的面部数据转换为 MetaHuman 动画的系统，用于虚拟直播或实时交互应用。
- **批量动画处理**：你有大量的面部捕捉数据需要处理，希望使用自动化流程（如 MetaHumanBatchProcessor）来批量生成动画资产。
- **自定义动画求解**：你需要精细调整面部动画的求解参数，例如眼睛注视的平滑度、牙齿的运动模式，或者深度图对结果的影响程度，以获得最符合艺术要求的动画效果。

## 蓝图用法

`UMetaHumanFaceAnimationSolver` 主要是一个配置对象，其属性用于控制求解器的行为。在蓝图中，你通常会创建或获取一个该类的实例，并设置其属性，然后将其传递给动画处理流程。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set bOverrideDeviceConfig` | 是否覆盖默认的设备配置 | `UMetaHumanFaceAnimationSolver` |
| `Set DeviceConfig` | 设置用于求解的设备特定配置资产 | `UMetaHumanFaceAnimationSolver` |
| `Set DepthMapInfluence` | 设置深度图对求解结果的影响程度（无、低、高） | `UMetaHumanFaceAnimationSolver` |
| `Set EyeSolveSmoothness` | 设置眼睛注视控制结果的平滑度（0.0 - 1.0） | `UMetaHumanFaceAnimationSolver` |
| `Set TeethMode` | 设置牙齿运动模式（使用跟踪点 或 估算） | `UMetaHumanFaceAnimationSolver` |
| `GetSolverTemplateData` | 获取求解器模板数据的 JSON 字符串 | `UMetaHumanFaceAnimationSolver` |
| `GetSolverConfigData` | 获取求解器配置数据的 JSON 字符串 | `UMetaHumanFaceAnimationSolver` |

### 使用示例（蓝图描述）

1.  在你的动画处理蓝图（例如，一个处理 MetaHumanPerformance 资产的蓝图）中，添加一个 `UMetaHumanFaceAnimationSolver` 类型的变量。
2.  在构造函数或初始化事件中，为该变量创建一个实例（`Construct Object`）。
3.  根据你的需求，设置该求解器实例的属性。例如，将 `DepthMapInfluence` 设置为 `High`，将 `EyeSolveSmoothness` 设置为 `0.3` 以获得更平滑的眼睛运动。
4.  将配置好的求解器实例传递给后续的动画生成或处理节点（例如，`MetaHumanPipeline` 中的节点）。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanFaceAnimationSolver.h"
```

### 基本用法

创建一个求解器配置对象并设置其参数。

```cpp
// 来源：基于 MetaHumanFaceAnimationSolver.h 中的类定义
#include "MetaHumanFaceAnimationSolver.h"

// 创建求解器配置对象
UMetaHumanFaceAnimationSolver* SolverConfig = NewObject<UMetaHumanFaceAnimationSolver>();

// 配置求解器参数
SolverConfig->bOverrideDepthMapInfluence = true;
SolverConfig->DepthMapInfluence = EDepthMapInfluenceValue::High;

SolverConfig->bOverrideEyeSolveSmoothness = true;
SolverConfig->EyeSolveSmoothness = 0.2f; // 设置一个适中的平滑度

SolverConfig->bOverrideTeethMode = true;
SolverConfig->TeethMode = ETeethMode::Estimated; // 使用估算模式

// 检查配置是否有效
if (SolverConfig->CanProcess())
{
    // 获取配置数据，用于传递给底层求解器
    FString ConfigJson = SolverConfig->GetSolverConfigData();
    // ... 将 ConfigJson 传递给动画处理管线
}
```

### 进阶用法

监听求解器配置的变化，并根据特定的捕捉数据动态获取配置。

```cpp
// 来源：基于 MetaHumanFaceAnimationSolver.h 中的委托和函数
#include "MetaHumanFaceAnimationSolver.h"
#include "CaptureData.h" // 假设的捕捉数据类

// 假设我们有一个求解器实例和一份捕捉数据
UMetaHumanFaceAnimationSolver* Solver = ...;
UCaptureData* CurrentCaptureData = ...;

// 绑定配置变化的委托
FDelegateHandle ChangeHandle = Solver->OnInternalsChanged().AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("Face Animation Solver configuration changed."));
    // 在这里可以触发重新计算或更新UI
});

// 根据当前的捕捉数据获取特定的求解器模板数据
FString TemplateData = Solver->GetSolverTemplateData(CurrentCaptureData);
// 使用 TemplateData ...

// 获取配置的显示名称（用于UI）
FString DisplayName;
if (Solver->GetConfigDisplayName(CurrentCaptureData, DisplayName))
{
    UE_LOG(LogTemp, Log, TEXT("Using config: %s"), *DisplayName);
}

// 当不再需要监听时，解绑委托
Solver->OnInternalsChanged().Remove(ChangeHandle);
```

## Demo 示例

一个最小的示例，展示如何在 C++ 中创建、配置并使用 `UMetaHumanFaceAnimationSolver`。

**MyFaceAnimProcessor.h**
```cpp
// MyFaceAnimProcessor.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyFaceAnimProcessor.generated.h"

class UMetaHumanFaceAnimationSolver;
class UCaptureData;

UCLASS(BlueprintType)
class UMyFaceAnimProcessor : public UObject
{
    GENERATED_BODY()

public:
    UMyFaceAnimProcessor();

    /** 使用配置的求解器处理给定的捕捉数据 */
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    bool ProcessCaptureData(UCaptureData* InCaptureData);

private:
    /** 面部动画求解器配置 */
    UPROPERTY()
    TObjectPtr<UMetaHumanFaceAnimationSolver> FaceAnimSolver;
};
```

**MyFaceAnimProcessor.cpp**
```cpp
// MyFaceAnimProcessor.cpp
#include "MyFaceAnimProcessor.h"
#include "MetaHumanFaceAnimationSolver.h"
#include "CaptureData.h" // 假设的头文件

UMyFaceAnimProcessor::UMyFaceAnimProcessor()
{
    // 创建并初始化求解器配置
    FaceAnimSolver = NewObject<UMetaHumanFaceAnimationSolver>(this);
    FaceAnimSolver->DepthMapInfluence = EDepthMapInfluenceValue::High;
    FaceAnimSolver->EyeSolveSmoothness = 0.15f;
    FaceAnimSolver->TeethMode = ETeethMode::TrackingPoints;
}

bool UMyFaceAnimProcessor::ProcessCaptureData(UCaptureData* InCaptureData)
{
    if (!InCaptureData || !FaceAnimSolver)
    {
        return false;
    }

    // 检查求解器是否可以处理
    if (!FaceAnimSolver->CanProcess())
    {
        UE_LOG(LogTemp, Warning, TEXT("Face Animation Solver is not ready to process."));
        return false;
    }

    // 获取针对此捕捉数据的求解器配置
    FString SolverConfig = FaceAnimSolver->GetSolverConfigData(InCaptureData);
    FString SolverTemplate = FaceAnimSolver->GetSolverTemplateData(InCaptureData);

    // 在实际应用中，这里会将 SolverConfig 和 SolverTemplate 传递给
    // MetaHumanPipeline 或其他底层处理模块来执行真正的动画求解。
    UE_LOG(LogTemp, Log, TEXT("Processing capture data with solver config: %s"), *SolverConfig.Left(100));

    // ... 执行实际的动画求解逻辑 ...

    return true;
}
```

## 模块依赖

由于这是一个庞大的插件，其模块间依赖复杂。`MetaHumanFaceAnimationSolver` 模块本身可能依赖于 `MetaHumanCore` 和 `MetaHumanConfig` 等基础模块。要使用此插件的完整功能，你的项目模块通常需要依赖 `MetaHumanToolkit` 或 `MetaHumanPipeline` 等高级模块。具体的依赖关系请参考各模块的 `Build.cs` 文件。

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | MetaHuman 插件的核心基础功能和类型定义 |
| `MetaHumanConfig` | 管理 MetaHuman 相关的设备配置和预设 |
| `MetaHumanPipeline` | 驱动整个面部动画处理流程的管线框架 |
| `MetaHumanToolkit` | 提供面向用户的工具和编辑器集成 |

## 维护状态

### 近期更新

```
- 9803c443cfab Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
- 52e3dac151e1 Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 3/n
- 2a7f797f2bdd [MH-Plugin] Migrate the animator plugin from restricted #rb Jane.Haslam [REVIEW] thanasis.vogiannou
```

### 维护评价

MetaHuman Animator 是一个相对较新的插件（创建于 2024 年初），并且是 Epic Games 官方维护的核心 MetaHuman 工具链的一部分。从提交历史看，近期有代码质量改进（如添加 `UE_INLINE_GENERATED_CPP_BY_NAME`）和从内部仓库迁移的记录，表明它处于**活跃维护**状态。

作为 MetaHuman 生态的关键组件，它预计会随着引擎版本持续更新和优化。目前没有发现明显的废弃迹象。对于需要进行高质量面部动画制作的项目，**强烈推荐使用**此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档]() (待补充)
- [测试用例]() (待补充)