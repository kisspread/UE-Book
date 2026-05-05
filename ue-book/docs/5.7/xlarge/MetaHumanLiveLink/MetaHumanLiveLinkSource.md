# MetaHuman Live Link

> Live Link sources and associated utilities for streaming real time MetaHuman animation data.

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `LiveLinkFaceDiscovery` (Runtime), `LiveLinkFaceSource` (Runtime), `LiveLinkFaceSourceEditor` (Runtime), `MetaHumanLiveLinkSource` (Runtime), `MetaHumanLiveLinkSourceEditor` (Runtime), `MetaHumanLocalLiveLinkSource` (Runtime), `MetaHumanLocalLiveLinkSourceEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-05 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanLiveLink) | |

## 用途

MetaHuman Live Link 插件的核心功能是为 MetaHuman 角色提供实时的面部动画数据流支持。它解决的核心问题是：如何将来自外部设备（如 iPhone 的 ARKit、专业面部捕捉头盔）的实时面部捕捉数据，高效、低延迟地传输并应用到 UE5 中的 MetaHuman 角色上。

该插件不仅仅是一个数据传输通道，它还集成了关键的实时处理功能，包括：
1.  **实时校准 (Calibration)**：允许用户在运行时捕捉并应用“中性表情”基准，以校准动画数据，使其更贴合特定演员的面部特征。
2.  **实时平滑 (Smoothing)**：提供可配置的平滑算法，用于过滤捕捉数据中的抖动和噪声，使动画输出更稳定、自然。
3.  **头部姿态控制**：支持对头部平移和旋转的独立控制与校准。

它本质上是连接实时面部捕捉设备与 UE5 MetaHuman 角色动画系统的桥梁和处理器。

## 使用场景

-   **实时虚拟直播 (VTubing)**：主播使用 iPhone 或专业设备进行面部捕捉，实时驱动 MetaHuman 虚拟形象进行直播。
-   **影视预览与虚拟制片**：在拍摄现场，演员的面部表演可以实时预览在数字替身（MetaHuman）上，辅助导演和演员进行创作。
-   **游戏开发中的实时动捕预览**：在开发需要大量面部动画的游戏时，可以使用此插件快速预览动捕效果，而无需等待漫长的离线处理。
-   **任何需要将实时面部数据流式传输到 MetaHuman 角色的场景**。

## 蓝图用法

该插件提供了丰富的蓝图接口，主要用于在运行时控制 Live Link 主题的校准和平滑参数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Calibration Properties` | 设置需要校准的动画属性名称列表。 | `UMetaHumanLiveLinkSubjectSettings` |
| `Get Calibration Properties` | 获取当前设置的校准属性列表。 | `UMetaHumanLiveLinkSubjectSettings` |
| `Set Calibration Alpha` | 设置校准混合权重 (0-1)。 | `UMetaHumanLiveLinkSubjectSettings` |
| `Get Calibration Alpha` | 获取当前的校准混合权重。 | `UMetaHumanLiveLinkSubjectSettings` |
| `Set Calibration Neutral Frame` | 设置用于校准的中性表情帧数据。 | `UMetaHumanLiveLinkSubjectSettings` |
| `Get Calibration Neutral Frame` | 获取当前存储的中性表情帧数据。 | `UMetaHumanLiveLinkSubjectSettings` |
| `Set Smoothing` | 为当前主题设置实时平滑参数对象。 | `UMetaHumanLiveLinkSubjectSettings` |
| `Get Smoothing` | 获取当前主题使用的实时平滑参数对象。 | `UMetaHumanLiveLinkSubjectSettings` |
| `Set Neutral Head Translation` | 设置头部平移的中性基准位置。 | `UMetaHumanLiveLinkSubjectSettings` |
| `Get Neutral Head Translation` | 获取头部平移的中性基准位置。 | `UMetaHumanLiveLinkSubjectSettings` |
| `Set Neutral Head Orientation` | 设置头部旋转的中性基准朝向。 | `UMetaHumanLiveLinkSubjectSettings` |
| `Get Neutral Head Orientation` | 获取头部旋转的中性基准朝向。 | `UMetaHumanLiveLinkSubjectSettings` |

### 使用示例（蓝图描述）

1.  **初始化设置**：在游戏开始时，获取你的 MetaHuman 角色所使用的 `UMetaHumanLiveLinkSubjectSettings` 对象（通常通过 Live Link 主题蓝图或 C++ 代码获取）。
2.  **配置校准**：
    *   调用 `Set Calibration Properties`，传入一个包含你希望校准的面部混合形状名称（如 `EyeBlinkLeft`, `MouthSmileRight`）的数组。
    *   调用 `Set Calibration Alpha` 设置一个初始值（如 0.5）。
3.  **配置平滑**：
    *   创建或获取一个 `UMetaHumanRealtimeSmoothingParams` 资产，调整其参数（如平滑强度）。
    *   调用 `Set Smoothing` 将该参数对象应用到设置中。
4.  **运行时校准**：在游戏 UI 中放置一个按钮，当演员摆出中性表情时，点击该按钮。该按钮的点击事件应调用 `Set Calibration Neutral Frame`，并传入当前帧从 Live Link 获取的动画数据。随后，系统会自动应用校准。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanLiveLinkSubjectSettings.h"
#include "MetaHumanSmoothingPreProcessor.h"
#include "MetaHumanRealtimeSmoothingParams.h"
```

### 基本用法

以下代码展示了如何在 C++ 中获取并配置一个 MetaHuman Live Link 主题的设置。

```cpp
// 假设你已经通过某种方式（如 Live Link Client）获取到了一个 ULiveLinkSubjectSettings 对象
// 并且知道它是 UMetaHumanLiveLinkSubjectSettings 类型
ULiveLinkSubjectSettings* BaseSettings = ...;
UMetaHumanLiveLinkSubjectSettings* MHSettings = Cast<UMetaHumanLiveLinkSubjectSettings>(BaseSettings);

if (MHSettings)
{
    // 1. 配置校准属性
    TArray<FName> CalibrationProps = { TEXT("EyeBlinkLeft"), TEXT("EyeBlinkRight"), TEXT("JawOpen") };
    MHSettings->SetCalibrationProperties(CalibrationProps);

    // 2. 设置校准强度
    MHSettings->SetCalibrationAlpha(0.8f);

    // 3. 应用平滑参数
    // 假设你有一个 UMetaHumanRealtimeSmoothingParams 资产的引用
    UMetaHumanRealtimeSmoothingParams* SmoothingParams = LoadObject<UMetaHumanRealtimeSmoothingParams>(nullptr, TEXT("/Game/Path/To/MySmoothingParams.MySmoothingParams"));
    if (SmoothingParams)
    {
        MHSettings->SetSmoothing(SmoothingParams);
    }
}
```

### 进阶用法

你可以直接创建和使用 `UMetaHumanSmoothingPreProcessor` 作为 Live Link 帧预处理器，独立于主题设置。

```cpp
#include "LiveLinkComponent.h"
#include "MetaHumanSmoothingPreProcessor.h"

// 获取 Live Link 组件
ULiveLinkComponent* LiveLinkComp = GetOwner()->FindComponentByClass<ULiveLinkComponent>();
if (LiveLinkComp)
{
    // 创建一个平滑预处理器实例
    UMetaHumanSmoothingPreProcessor* SmoothingPreProcessor = NewObject<UMetaHumanSmoothingPreProcessor>(this);

    // 配置其内部的平滑参数（假设 Parameters 对象已存在）
    if (SmoothingPreProcessor->Parameters)
    {
        // 修改平滑参数...
    }

    // 将预处理器应用到特定的 Live Link 主题
    FLiveLinkSubjectKey SubjectKey = ...; // 你的主题键
    LiveLinkComp->SetSubjectPreProcessor(SubjectKey, SmoothingPreProcessor);
}
```

## Demo 示例

一个最小化的 C++ 示例，展示如何创建并配置一个 MetaHuman Live Link 主题设置。

**MyMetaHumanLiveLinkActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyMetaHumanLiveLinkActor.generated.h"

class UMetaHumanLiveLinkSubjectSettings;
class UMetaHumanRealtimeSmoothingParams;

UCLASS()
class AMyMetaHumanLiveLinkActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMetaHumanLiveLinkActor();

protected:
    virtual void BeginPlay() override;

    // 在编辑器中指定要使用的 Live Link 主题名称
    UPROPERTY(EditAnywhere, Category = "Live Link")
    FName LiveLinkSubjectName;

    // 在编辑器中指定平滑参数资产
    UPROPERTY(EditAnywhere, Category = "Live Link")
    TObjectPtr<UMetaHumanRealtimeSmoothingParams> SmoothingParameters;

private:
    UPROPERTY()
    TObjectPtr<UMetaHumanLiveLinkSubjectSettings> CachedSubjectSettings;
};
```

**MyMetaHumanLiveLinkActor.cpp**
```cpp
#include "MyMetaHumanLiveLinkActor.h"
#include "MetaHumanLiveLinkSubjectSettings.h"
#include "MetaHumanRealtimeSmoothingParams.h"
#include "LiveLinkSubsystem.h"

AMyMetaHumanLiveLinkActor::AMyMetaHumanLiveLinkActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMetaHumanLiveLinkActor::BeginPlay()
{
    Super::BeginPlay();

    // 获取 Live Link 子系统
    ULiveLinkSubsystem* LiveLinkSubsystem = GEngine->GetEngineSubsystem<ULiveLinkSubsystem>();
    if (!LiveLinkSubsystem)
    {
        UE_LOG(LogTemp, Error, TEXT("LiveLinkSubsystem not found!"));
        return;
    }

    // 尝试获取指定主题的设置
    ULiveLinkSubjectSettings* Settings = LiveLinkSubsystem->GetSubjectSettings(LiveLinkSubjectName);
    CachedSubjectSettings = Cast<UMetaHumanLiveLinkSubjectSettings>(Settings);

    if (CachedSubjectSettings)
    {
        UE_LOG(LogTemp, Log, TEXT("Found MetaHuman Live Link settings for subject: %s"), *LiveLinkSubjectName.ToString());

        // 应用平滑参数
        if (SmoothingParameters)
        {
            CachedSubjectSettings->SetSmoothing(SmoothingParameters);
            UE_LOG(LogTemp, Log, TEXT("Applied smoothing parameters."));
        }

        // 设置一些默认的校准属性
        TArray<FName> DefaultCalibrationProps = { TEXT("EyeBlinkLeft"), TEXT("EyeBlinkRight") };
        CachedSubjectSettings->SetCalibrationProperties(DefaultCalibrationProps);
        CachedSubjectSettings->SetCalibrationAlpha(1.0f);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Could not find MetaHuman Live Link settings for subject: %s. Ensure the subject is active and using the correct role."), *LiveLinkSubjectName.ToString());
    }
}
```

## 模块依赖

该插件由多个模块组成，各模块依赖关系较为内部化。对于使用者（你的项目模块）而言，主要需要依赖 `MetaHumanLiveLinkSource` 模块来访问核心设置类和预处理器。

| 模块 | 用途 |
|---|---|
| `MetaHumanLiveLinkSource` | 提供 `UMetaHumanLiveLinkSubjectSettings`, `UMetaHumanSmoothingPreProcessor` 等核心运行时类。 |
| `LiveLink` | UE5 的 Live Link 框架核心模块，必须依赖。 |
| `MetaHumanRealtimeSmoothing` | 提供实时平滑算法 (`FMetaHumanRealtimeSmoothing`) 和参数类 (`UMetaHumanRealtimeSmoothingParams`)。 |
| `MetaHumanRealtimeCalibration` | 提供实时校准算法 (`FMetaHumanRealtimeCalibration`)。 |

**注意**：`LiveLinkFaceDiscovery`, `LiveLinkFaceSource` 等模块主要用于发现和连接特定设备（如 iPhone），通常由插件内部使用，你的项目模块一般无需直接依赖它们。

## 维护状态

### 近期更新

-   2025-10-03 09c462f GUI pass #rb robert.hillary
    *解读：对插件的用户界面进行了优化和调整。*
-   2025-10-03 e2805c4 Support creating realtime Live Link sources via blueprint #rb robert.hillary
    *解读：增加了通过蓝图创建实时 Live Link 数据源的支持，提升了易用性。*
-   2025-10-03 8c52f4b Ability to calibrate head rotation #rb robert.hillary
    *解读：新增了头部旋转校准功能，完善了头部姿态控制。*

### 维护评价

**活跃维护**。

该插件创建于 2025 年 2 月，非常年轻。从最近的 Git 提交记录（2025 年 10 月）来看，它正处于密集的开发和完善阶段。近期的更新集中在功能增强（蓝图支持、头部旋转校准）和用户体验优化（GUI 调整）上，表明 Epic Games 正在积极投入开发。

作为 MetaHuman 生态系统的关键实时组件，它预计将得到持续的维护和更新。目前没有迹象表明它被废弃或存在严重已知问题。

**推荐使用**：对于任何需要实时驱动 MetaHuman 角色的项目，此插件是官方推荐且功能完备的解决方案，可以放心使用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanLiveLink)
-   [官方文档]() (暂无)
-   [测试用例]() (暂未在提供的路径中发现独立的测试文件)