# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（MetaHuman资产、配置、蓝图等） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 角色动画制作工具集。它不仅仅是一个简单的工具，而是一个完整的、端到端的面部动画解决方案。该插件的核心目的是将真实演员的面部表演（通常通过 iPhone 或其他专业设备捕获的视频）转换为驱动 MetaHuman 角色的高质量动画数据。它解决了从原始视频素材到最终可用于引擎中实时驱动的动画数据之间的复杂转换流程，包含了面部追踪、求解器、身份管理、性能处理等一整套专业管线。

## 使用场景

- **从 iPhone 视频创建动画**：你使用 iPhone 的前置摄像头录制了一段演员的面部表演视频，希望将其快速转换为驱动 UE5 中 MetaHuman 角色的动画序列。
- **专业面部动作捕捉集成**：你的工作室使用专业的面部动作捕捉设备（如 HMC），需要将捕获的数据导入 UE5 并用于驱动 MetaHuman。
- **批量处理动画资产**：你有大量的面部表演视频需要转换为动画，希望使用批处理工具自动化这一过程。
- **创建和管理 MetaHuman 身份**：你需要为你的 MetaHuman 角色创建一个“身份”，用于后续的动画求解和适配。
- **音频驱动面部动画**：你希望仅通过一段音频文件（如对话），自动生成对应的面部口型动画。

## 蓝图用法

该插件提供了丰富的蓝图接口，主要围绕“身份（Identity）”和“性能（Performance）”这两个核心概念展开。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create New Identity` | 创建一个新的 MetaHuman 身份资产。 | `UMetaHumanIdentity` |
| `Import Footage` | 将视频或图像序列导入为捕获数据资产。 | `UMetaHumanFootageIngest` |
| `Create Performance From Footage` | 从导入的捕获数据创建一个新的性能（动画）资产。 | `UMetaHumanPerformance` |
| `Solve Performance` | 对性能资产运行面部动画求解器，生成动画曲线数据。 | `UMetaHumanPerformance` |
| `Export to Control Rig` | 将求解后的性能数据导出为 Control Rig 可用的格式。 | `UMetaHumanPerformance` |
| `Batch Process` | 使用批处理器对多个性能资产执行自动化处理流程。 | `UMetaHumanBatchProcessor` |

### 使用示例（蓝图描述）

1.  **创建身份**：在内容浏览器中右键，选择 `Animation > MetaHuman > Identity` 创建一个 `MetaHumanIdentity` 资产。打开它，在蓝图图表中使用 `Create New Identity` 节点初始化。
2.  **导入视频**：将 iPhone 录制的 `.mov` 文件拖入内容浏览器，会自动创建一个 `MetaHumanCaptureData` 资产。或者使用 `Import Footage` 节点通过蓝图导入。
3.  **创建并求解性能**：基于捕获数据资产，使用 `Create Performance From Footage` 节点创建性能资产。然后，对该资产调用 `Solve Performance` 节点。求解完成后，性能资产中将包含动画曲线。
4.  **应用动画**：将求解后的性能资产拖拽到场景中的 MetaHuman 角色上，或通过 `Export to Control Rig` 节点将其数据连接到角色的 Control Rig，即可驱动角色面部。

## C++ 用法

该插件的 C++ API 主要用于扩展其管线或进行更底层的控制。以下示例基于插件内部测试用例和模块结构推导。

### 头文件引入

```cpp
#include "MetaHumanIdentity.h"
#include "MetaHumanPerformance.h"
#include "MetaHumanPipeline.h"
```

### 基本用法

以下代码展示了如何以编程方式创建一个 MetaHuman 身份并关联一个捕获数据资产。
*（来源：基于 `MetaHumanIdentity` 模块的资产创建逻辑）*

```cpp
// 创建一个新的 MetaHumanIdentity 资产
UMetaHumanIdentity* NewIdentity = NewObject<UMetaHumanIdentity>(GetTransientPackage(), TEXT("MyNewIdentity"));
NewIdentity->AddToRoot(); // 防止被垃圾回收

// 假设我们已经有一个捕获数据资产
UMetaHumanCaptureData* CaptureData = LoadObject<UMetaHumanCaptureData>(nullptr, TEXT("/Game/MetaHuman/Captures/MyCaptureData"));

if (CaptureData)
{
    // 将捕获数据与身份关联
    NewIdentity->SetCaptureData(CaptureData);
    UE_LOG(LogTemp, Log, TEXT("Identity '%s' linked to capture data."), *NewIdentity->GetName());
}
```

### 进阶用法

以下代码展示了如何访问和处理一个性能资产中的动画数据。
*（来源：基于 `MetaHumanPerformance` 模块的数据访问接口）*

```cpp
// 加载一个已求解的性能资产
UMetaHumanPerformance* Performance = LoadObject<UMetaHumanPerformance>(nullptr, TEXT("/Game/MetaHuman/Performances/MySolvedPerformance"));

if (Performance && Performance->IsSolved())
{
    // 获取动画曲线数据
    const FMetaHumanAnimationData& AnimData = Performance->GetAnimationData();

    // 遍历并打印一些曲线值
    for (const TPair<FName, FFloatCurve>& CurvePair : AnimData.Curves)
    {
        const FName& CurveName = CurvePair.Key;
        const FFloatCurve& Curve = CurvePair.Value;

        // 获取曲线在时间 0.0 秒的值
        float ValueAtTimeZero = Curve.Evaluate(0.0f);
        UE_LOG(LogTemp, Log, TEXT("Curve '%s' value at t=0: %f"), *CurveName.ToString(), ValueAtTimeZero);
    }
}
```

## Demo 示例

一个最小的 C++ 示例，演示如何创建身份和性能资产的基本流程。

```cpp
// MyMetaHumanDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyMetaHumanDemo.generated.h"

class UMetaHumanIdentity;
class UMetaHumanPerformance;
class UMetaHumanCaptureData;

UCLASS()
class MYPROJECT_API AMyMetaHumanDemo : public AActor
{
    GENERATED_BODY()

public:
    AMyMetaHumanDemo();

    UFUNCTION(BlueprintCallable, Category = "MetaHuman Demo")
    void RunDemoPipeline();

private:
    UPROPERTY()
    TObjectPtr<UMetaHumanIdentity> DemoIdentity;

    UPROPERTY()
    TObjectPtr<UMetaHumanPerformance> DemoPerformance;

    UPROPERTY()
    TObjectPtr<UMetaHumanCaptureData> DemoCaptureData;
};
```

```cpp
// MyMetaHumanDemo.cpp
#include "MyMetaHumanDemo.h"
#include "MetaHumanIdentity.h"
#include "MetaHumanPerformance.h"
#include "MetaHumanCaptureData.h"

AMyMetaHumanDemo::AMyMetaHumanDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMetaHumanDemo::RunDemoPipeline()
{
    // 1. 创建身份
    DemoIdentity = NewObject<UMetaHumanIdentity>(this, TEXT("DemoIdentity"));

    // 2. 模拟加载捕获数据（实际项目中应从磁盘加载）
    DemoCaptureData = NewObject<UMetaHumanCaptureData>(this, TEXT("DemoCaptureData"));
    // ... 配置捕获数据属性 ...

    // 3. 关联身份与捕获数据
    if (DemoIdentity && DemoCaptureData)
    {
        DemoIdentity->SetCaptureData(DemoCaptureData);
        UE_LOG(LogTemp, Warning, TEXT("Demo Identity created and linked to capture data."));
    }

    // 4. 创建性能资产
    DemoPerformance = NewObject<UMetaHumanPerformance>(this, TEXT("DemoPerformance"));
    if (DemoPerformance && DemoCaptureData)
    {
        DemoPerformance->InitializeFromCaptureData(DemoCaptureData);
        UE_LOG(LogTemp, Warning, TEXT("Demo Performance created from capture data."));

        // 注意：实际的求解过程（Solve）是异步且计算密集型的，
        // 通常通过编辑器UI或批处理器触发，此处仅为演示API调用。
        // DemoPerformance->StartSolve();
    }
}
```

## 模块依赖

该插件依赖于多个内部和外部模块。以下是其**独特**的、不常见的依赖项：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心算法库，包含面部追踪、求解器等底层技术实现。 |
| `ControlRig` / `ControlRigDeveloper` | 用于将求解出的动画数据转换为 Control Rig 可用的格式，并驱动骨骼。 |
| `MetaHumanSDKEditor` | MetaHuman SDK 的编辑器部分，提供资产管理和工作流支持。 |
| `SkeletalMeshUtilitiesCommon` | 提供骨骼网格体相关的通用工具函数，用于处理 MetaHuman 的网格体。 |
| `MeshTrackerInterface` | 提供网格体追踪的抽象接口，可能用于支持不同的追踪后端。 |
| `MediaUtils` / `MediaAssets` | 用于处理视频媒体文件的导入和播放。 |

## 维护状态

### 近期更新

```
- 6201ee5377e8 Addressing localisation build warnings. Fixes spelling error on the word “Suppress”.
- 1827aa40c19a [UEMHC] Fixed issue of Save Dialog not opening on Mac
- 148337bfc50f [MHA, UEMHC] [Mac, Linux] Disabling Identity/Performance creation, disabled Conform from Identity in the UEMHC editor
```

### 维护评价

- **创建时间**：2024年2月，是一个非常新的插件。
- **近期更新**：最近的提交集中在修复本地化警告和跨平台（Mac, Linux）兼容性问题，表明插件正在积极适配多平台并修复已知问题。
- **活跃度**：作为 Epic Games 官方维护的核心 MetaHuman 工具，预计会持续获得功能更新和 bug 修复。目前处于**活跃维护**状态。
- **已知限制**：从提交信息看，在 Mac 和 Linux 平台上，部分功能（如从身份创建性能）可能被禁用，表明跨平台支持仍在完善中。
- **推荐使用**：**强烈推荐**。这是创建和驱动 MetaHuman 角色动画的官方标准工具，功能完整，与引擎集成度高。尽管是新插件，但由 Epic 直接维护，可靠性有保障。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/metahuman-animator-in-unreal-engine/) (Epic 官方文档站)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest) (插件内包含测试模块)