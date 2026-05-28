# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 元人类动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-09-21 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一套完整的工具包，旨在将外部捕获的面部表演数据（如 iPhone 的 TrueDepth 摄像头录制的视频）转换为 MetaHuman 角色的动画。它解决了从数据捕获、处理、解算到最终驱动角色的全流程问题。核心价值在于提供了一套标准化的工作流和算法（如面部轮廓追踪、动画解算、面部拟合），使用户能够高效地创建逼真、高质量的数字人类面部动画。该插件是 Epic Games 官方维护的 MetaHuman 生态系统的核心组件之一。

## 使用场景

-   **影视与游戏制作**：为影视角色或游戏角色创建基于真人表演的高保真面部动画。
-   **数字人驱动**：实时或离线地驱动 MetaHuman 角色的面部表情，用于虚拟主播、客户服务机器人等场景。
-   **资产创建**：基于扫描数据或照片，创建并调整 MetaHuman 角色的面部形态和动画蓝图。

## 蓝图用法

该插件的核心功能主要通过编辑器工具和数据资产来配置与驱动，直接暴露给蓝图的公开运行时节点相对较少。其工作流通常涉及在编辑器中配置身份、导入捕获数据、设置动画解算参数，最终生成可在运行时播放的动画序列或驱动蓝图。

### 核心资产与工具

| 资产/工具 | 说明 | 所在模块 |
|---|---|---|
| `UMetaHumanIdentity` | 用于定义和存储一个 MetaHuman 角色的面部身份、骨架和网格体。是整个工作流的起点。 | `MetaHumanIdentity` |
| `UMetaHumanPerformance` | 存储并管理从捕获数据（如视频）中提取的表演数据（动画曲线）。 | `MetaHumanPerformance` |
| `MetaHuman Animator 面板` | 编辑器中的主要工作界面，用于执行面部追踪、动画解算、预览和导出等操作。 | `MetaHumanCoreEditor`, `MetaHumanToolkit` |

## C++ 用法

**注意**：该插件的大部分核心算法和流程控制通过编辑器工具暴露，直接在运行时 C++ 代码中调用其高级功能（如创建完整身份、执行解算）的场景相对较少。以下示例展示了其底层数据结构的访问方式。

### 头文件引入

```cpp
#include "MetaHumanIdentity.h"
#include "MetaHumanPerformance.h"
#include "MetaHumanPipeline.h"
```

### 基本用法

**获取和检查一个已存在的 MetaHuman 身份资产。**

*来源: 模块 `MetaHumanIdentity` 的测试与工具代码*

```cpp
// 加载一个已有的 MetaHumanIdentity 资产
UMetaHumanIdentity* Identity = LoadObject<UMetaHumanIdentity>(nullptr, TEXT("/Game/MetaHumans/MyMH/MH_Identity"));

if (Identity)
{
    // 访问其面部参数
    const FMetaHumanFaceParameters& FaceParams = Identity->GetFaceParameters();
    UE_LOG(LogTemp, Log, TEXT("Identity Face Asset: %s"), *FaceParams.FaceMesh.GetAssetName());
}
```

### 进阶用法

**通过 Pipeline 模块处理捕获数据。**

*来源: 模块 `MetaHumanPipeline` 的公开接口与示例*

```cpp
#include "MetaHumanPipeline.h"
#include "MetaHumanCaptureSource.h"

// 假设我们有一个视频文件路径和对应的 MetaHuman 身份
FString VideoPath = TEXT("C:/Capture/Take001.mov");
UMetaHumanIdentity* TargetIdentity = ...;

// 创建一个 Pipeline 实例来驱动捕获处理流程
UMetaHumanPipeline* Pipeline = NewObject<UMetaHumanPipeline>();

// 配置 Pipeline 的输入（捕获源）和输出（性能数据）
// 注意：以下为概念性代码，具体 API 需查阅最新的模块头文件。
Pipeline->SetCaptureSource(VideoPath);
Pipeline->SetTargetIdentity(TargetIdentity);

// 异步执行 Pipeline
Pipeline->ExecutePipeline(FOnPipelineCompleted::CreateLambda([](bool bSuccess)
{
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Pipeline completed successfully. Performance data generated."));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Pipeline failed."));
    }
}));
```

## Demo 示例

一个演示如何使用 `MetaHumanIdentity` 和 `MetaHumanPerformance` 类型的最小示例。

*MetaHumanAnimatorDemo.h*
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MetaHumanAnimatorDemo.generated.h"

class UMetaHumanIdentity;
class UMetaHumanPerformance;

UCLASS()
class YOURPROJECT_API AMetaHumanAnimatorDemo : public AActor
{
    GENERATED_BODY()

public:
    AMetaHumanAnimatorDemo();

    // 要操作的 MetaHuman 身份资产引用
    UPROPERTY(EditAnywhere, Category = "MetaHuman")
    UMetaHumanIdentity* TargetIdentity;

    // 要使用的表演数据资产引用
    UPROPERTY(EditAnywhere, Category = "MetaHuman")
    UMetaHumanPerformance* PerformanceData;

    // 在蓝图或编辑器中调用，模拟一个加载和检查的过程
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    void LoadAndInspect();

    // 用于运行时播放的骨骼网格体组件
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MetaHuman")
    USkeletalMeshComponent* CharacterMesh;
};
```

*MetaHumanAnimatorDemo.cpp*
```cpp
#include "MetaHumanAnimatorDemo.h"
#include "MetaHumanIdentity.h"
#include "MetaHumanPerformance.h"
#include "Components/SkeletalMeshComponent.h"

AMetaHumanAnimatorDemo::AMetaHumanAnimatorDemo()
{
    PrimaryActorTick.bCanEverTick = false;

    CharacterMesh = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("CharacterMesh"));
    RootComponent = CharacterMesh;
}

void AMetaHumanAnimatorDemo::LoadAndInspect()
{
    if (TargetIdentity)
    {
        UE_LOG(LogTemp, Log, TEXT("Inspecting Identity: %s"), *TargetIdentity->GetName());

        // 在此处可以进一步访问 Identity 的详细参数，例如：
        // const FMetaHumanFaceParameters& FaceParams = TargetIdentity->GetFaceParameters();
        // UE_LOG(LogTemp, Log, TEXT("Face Asset: %s"), *FaceParams.FaceMesh.GetAssetName());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("TargetIdentity is null. Please assign a MetaHumanIdentity asset."));
    }

    if (PerformanceData)
    {
        UE_LOG(LogTemp, Log, TEXT("Performance data loaded: %s"), *PerformanceData->GetName());
        // 通常，Performance 数据会被用来驱动动画蓝图或动画序列。
        // 此处仅为示例，实际应用需要将 Performance 数据应用到角色的动画蓝图或动画实例中。
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("PerformanceData is null. Please assign a MetaHumanPerformance asset."));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | 提供底层的面部追踪、解算和网格体操作的核心算法库。 |
| `ControlRigDeveloper` | 用于编辑和操作 Control Rig 资产，这是驱动 MetaHuman 骨骼的关键技术。 |
| `SkeletalMeshUtilitiesCommon` | 提供骨骼网格体相关的通用工具函数。 |
| `MetaHumanSDKEditor` | 提供编辑器集成和工具的基础设施。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 禁用关卡序列导出，当启用身体追踪时 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复元人类角色的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复序列器缓存问题 |

### 维护评价

该插件创建于 2021 年，距今约 5 年，属于较新的功能插件。从近期（2026 年 5 月）的 Git 提交记录来看，该插件仍在被 **积极维护和迭代**。更新内容包括功能新增（身体追踪支持、网格体导出）、问题修复（渲染瑕疵、缓存问题）和工作流优化（可视化过滤）。考虑到 Epic Games 将 MetaHuman 作为其长期战略的重要组成部分，此插件是其核心工具链，预计将持续获得支持和更新。**强烈推荐**在涉及数字人类创作的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/en-US/metahuman-animator/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/Tests)