# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（MetaHuman资产、模型数据） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 角色动画制作工具集。它解决的核心问题是：**如何将真实演员的面部表演（视频/音频）高效、自动化地转换为高质量的 MetaHuman 角色面部动画**。

该插件不仅仅是一个简单的录制工具，而是一个完整的、基于 AI 和机器学习的动画生成管线。它包含从原始素材导入、面部特征追踪、深度估计、动画求解到最终动画应用的全套工具。其存在是为了大幅降低创建逼真数字人动画的技术门槛和时间成本，使开发者能够专注于创意而非繁琐的技术实现。

## 使用场景

- **数字人内容创作**：你正在开发一个需要大量对话和表情动画的虚拟主播、数字员工或游戏角色，使用 MetaHuman Animator 可以快速从演员表演视频生成动画。
- **游戏过场动画制作**：你需要为游戏中的 MetaHuman 角色制作电影级的过场动画，该插件可以自动化处理面部动画，节省大量手动关键帧时间。
- **语音驱动动画**：你希望根据配音演员的音频文件自动生成角色的口型和面部表情动画，可以使用 `MetaHumanSpeech2Face` 模块。
- **批量处理**：你有大量的表演素材需要处理，`MetaHumanBatchProcessor` 模块支持自动化批量处理流程。
- **自定义动画管线**：你需要将 MetaHuman Animator 的追踪和求解能力集成到自己工作室的动画管线中，其模块化设计允许单独使用特定功能（如轮廓追踪、深度生成）。

## 蓝图用法

MetaHuman Animator 主要通过编辑器工具和资产进行操作，其核心功能通常封装在编辑器工具和资产类中。以下是一些关键的蓝图可访问类和节点：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `LoadTrackers` | 异步加载面部轮廓追踪器所需的神经网络模型数据 | `UMetaHumanFaceContourTrackerAsset` |
| `LoadTrackersSynchronous` | 同步加载面部轮廓追踪器模型数据（可能阻塞） | `UMetaHumanFaceContourTrackerAsset` |
| `CanProcess` | 检查追踪器资产是否已准备好进行处理（模型数据是否已加载） | `UMetaHumanFaceContourTrackerAsset` |
| `IsLoadingTrackers` | 检查追踪器模型是否正在加载中 | `UMetaHumanFaceContourTrackerAsset` |
| `CancelLoadTrackers` | 取消正在进行的追踪器模型加载 | `UMetaHumanFaceContourTrackerAsset` |

### 使用示例（蓝图描述）

1.  **准备追踪器资产**：在内容浏览器中找到或创建一个 `MetaHumanFaceContourTrackerAsset` 资产。在蓝图中，获取对该资产的引用。
2.  **异步加载模型**：调用 `LoadTrackers` 节点。该节点会异步加载资产中配置的多个神经网络模型（如人脸检测器、眉毛追踪器等）。你可以传入一个回调委托，在加载完成时收到通知。
3.  **检查状态**：在加载过程中，可以使用 `IsLoadingTrackers` 节点检查状态。加载完成后，使用 `CanProcess` 节点确认资产是否就绪。
4.  **应用到处理流程**：将准备好的追踪器资产传递给 `MetaHumanIdentity` 或 `MetaHumanPerformance` 等更高层的资产或处理节点，用于实际的面部特征追踪和动画生成。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanFaceContourTrackerAsset.h"
```

### 基本用法

以下代码演示了如何以编程方式加载和使用面部轮廓追踪器资产。

```cpp
// 来源：基于 MetaHumanFaceContourTrackerAsset.h 的 API 设计
#include "MetaHumanFaceContourTrackerAsset.h"

// 假设你已经通过资产路径或编辑器获取了追踪器资产的指针
UMetaHumanFaceContourTrackerAsset* TrackerAsset = LoadObject<UMetaHumanFaceContourTrackerAsset>(nullptr, TEXT("/Game/MetaHuman/MyTrackerAsset"));

if (TrackerAsset)
{
    // 1. 检查资产是否已就绪（模型数据是否已加载）
    if (TrackerAsset->CanProcess())
    {
        UE_LOG(LogTemp, Log, TEXT("追踪器资产已就绪，可以开始处理。"));
        // 在此可以将 TrackerAsset 传递给其他处理模块
    }
    else
    {
        // 2. 异步加载模型数据
        TrackerAsset->LoadTrackers(true, [TrackerAsset](bool bSuccess)
        {
            if (bSuccess)
            {
                UE_LOG(LogTemp, Log, TEXT("追踪器模型加载成功！"));
                // 加载成功后，可以开始使用
            }
            else
            {
                UE_LOG(LogTemp, Error, TEXT("追踪器模型加载失败。"));
            }
        });
    }
}
```

### 进阶用法

在实际的 MetaHuman Animator 管线中，`UMetaHumanFaceContourTrackerAsset` 通常作为 `UMetaHumanIdentity` 或 `UMetaHumanPerformance` 资产的一部分被使用。以下是一个概念性的流程，展示了如何将追踪器集成到身份创建流程中。

```cpp
// 概念性代码，展示模块间协作
#include "MetaHumanIdentity.h"
#include "MetaHumanFaceContourTrackerAsset.h"

void CreateMetaHumanIdentityFromFootage(UFootageAsset* Footage)
{
    // 1. 创建或获取一个 MetaHuman Identity 资产
    UMetaHumanIdentity* Identity = NewObject<UMetaHumanIdentity>();

    // 2. 为 Identity 配置面部轮廓追踪器
    UMetaHumanFaceContourTrackerAsset* Tracker = LoadObject<UMetaHumanFaceContourTrackerAsset>(...);
    Identity->SetFaceContourTracker(Tracker);

    // 3. 确保追踪器模型已加载
    if (!Tracker->CanProcess())
    {
        // 同步加载（注意：可能阻塞，仅用于示例）
        Tracker->LoadTrackersSynchronous();
    }

    // 4. 使用 Identity 资产处理素材，生成面部网格和动画
    // Identity->ProcessFootage(Footage); // 假设的 API
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何加载并检查一个 `MetaHumanFaceContourTrackerAsset`。

**MyTrackerUser.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyTrackerUser.generated.h"

class UMetaHumanFaceContourTrackerAsset;

UCLASS(BlueprintType)
class UMyTrackerUser : public UObject
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MetaHuman")
    TSoftObjectPtr<UMetaHumanFaceContourTrackerAsset> TrackerAssetSoftPtr;

    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    void InitializeTracker();

    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    bool IsTrackerReady() const;

private:
    UPROPERTY(Transient)
    TObjectPtr<UMetaHumanFaceContourTrackerAsset> LoadedTracker;
};
```

**MyTrackerUser.cpp**
```cpp
#include "MyTrackerUser.h"
#include "MetaHumanFaceContourTrackerAsset.h"

void UMyTrackerUser::InitializeTracker()
{
    if (TrackerAssetSoftPtr.IsPending() || TrackerAssetSoftPtr.IsValid())
    {
        // 异步加载资产
        TrackerAssetSoftPtr.LoadSynchronous();
        LoadedTracker = TrackerAssetSoftPtr.Get();

        if (LoadedTracker)
        {
            // 异步加载资产内部的神经网络模型
            LoadedTracker->LoadTrackers(false, [WeakThis = MakeWeakObjectPtr(this)](bool bSuccess)
            {
                if (bSuccess && WeakThis.IsValid())
                {
                    UE_LOG(LogTemp, Log, TEXT("追踪器资产及其模型加载完成。"));
                }
            });
        }
    }
}

bool UMyTrackerUser::IsTrackerReady() const
{
    return LoadedTracker && LoadedTracker->CanProcess();
}
```

## 模块依赖

从各模块的 Build.cs 分析，该插件依赖于多个内部和外部模块。以下列出其**独特**的依赖项（已省略 Core, CoreUObject, Engine, Slate, UnrealEd 等常见依赖）：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库，提供底层算法支持 |
| `MetaHumanSDKEditor` | MetaHuman SDK 的编辑器部分，用于资产集成和编辑器工具 |
| `ControlRigDeveloper` | 用于创建和编辑 Control Rig，驱动 MetaHuman 骨骼动画 |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格体通用工具，用于处理 MetaHuman 的网格体数据 |
| `NNE` (Neural Network Engine) | UE 的神经网络引擎，用于运行面部追踪和动画求解的 AI 模型 |
| `NNERuntimeGPU` | NNE 的 GPU 运行时，加速神经网络推理 |

## 维护状态

### 近期更新

```
- 2024-02-02 52e3dac151e1 Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 3/n
- 2024-02-02 2a7f797f2bdd [MH-Plugin] Migrate the animator plugin from restricted #rb Jane.Haslam [REVIEW] thanasis.vogiannou
```

### 维护评价

- **创建时间**：该插件于 2024 年 2 月首次提交，是一个相对较新的插件。
- **最近更新频率**：从提供的 git 历史看，最近的提交集中在 2024 年 2 月，主要是代码迁移和头文件修复。**自创建以来，没有看到持续的功能性更新记录**。
- **活跃维护状态**：基于有限的 git 信息，**无法判断其是否处于活跃维护状态**。作为 Epic Games 的官方工具，它可能在 Epic 内部的私有仓库中进行更频繁的更新，但公开的 UE 源码仓库中更新不频繁。
- **已知问题或限制**：该插件依赖于特定的神经网络模型数据（通过 `UNNEModelData` 资产），这些模型数据可能需要从 Epic 的 MetaHuman 服务或特定渠道获取，并非完全开源。其功能高度依赖于 AI 模型的性能和准确性。
- **推荐使用**：如果你正在使用 MetaHuman 技术栈并需要自动化面部动画生成，**这是官方推荐的工具**。尽管公开仓库更新不频繁，但其作为官方插件，稳定性和与引擎的兼容性是有保障的。建议关注 Epic 的官方发布说明和 MetaHuman 文档以获取最新功能信息。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/metahuman-animator-in-unreal-engine/)（MetaHuman 官方文档页面）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest)（包含一个测试模块）