# Live Link

> LiveLink allows streaming of animated data into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | 实时链接 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、动画节点、编辑器工具） |
| 模块 | `LiveLink` (Runtime), `LiveLinkComponents` (Runtime), `LiveLinkEditor` (Runtime), `LiveLinkGraphNode` (Runtime), `LiveLinkMovieScene` (Runtime), `LiveLinkMultiUser` (Runtime), `LiveLinkSequencer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-02-27 |
| 年龄标签 | 🏛️ 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink) | |

## 用途

Live Link 是一个**实时数据流框架**，用于将外部设备或应用程序（如动作捕捉系统、面部捕捉系统、虚拟制片工具）的实时数据流式传输到虚幻引擎中。它不仅仅是简单的数据传输，更是一个**标准化的数据接口和转换中心**。

核心解决的问题是：如何将来自不同厂商、不同协议的实时表演数据（动画、变换、布尔值、蓝图数据等）统一、同步、高效地应用到引擎内的角色、相机或任何物体上。它将外部数据封装为“主题”（Subject），每个主题包含静态数据（Static Data，如骨骼列表）和帧数据（Frame Data，如每帧的骨骼变换）。这样，动画蓝图、蓝图、Sequencer 等系统就可以通过统一的接口查询和消费这些实时数据。

## 使用场景

- **影视虚拟制片**：将专业动捕设备（如 Vicon、OptiTrack）的实时数据传输到虚幻引擎，驱动虚拟角色进行实时预览或直播。
- **实时动捕直播**：直播时，将表演者的面部或身体数据实时映射到虚拟主播或游戏角色。
- **MetaHuman Animator**：这是 Live Link 的一个具体应用，专门用于从 iPhone 录制的表演数据中提取高质量的面部动画。
- **多源数据同步**：同时接收来自身体动捕、面部捕捉、相机追踪等多个源的数据，并确保它们在引擎内同步播放。
- **编辑器内实时预览**：动画师可以一边进行现实世界的表演，一边在虚幻编辑器中实时看到角色动画的效果。

## 蓝图用法

Live Link 提供了丰富的蓝图节点，主要用于查询和消费实时数据。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Evaluate Live Link Frame` | 核心节点，根据角色（Role）和主题（Subject）实时获取一帧数据。支持按世界时间或场景时间求值。 | `UK2Node_EvaluateLiveLinkFrame` |
| `Update Virtual Subject Static Data` | 为虚拟主题（如蓝图创建的自定义主题）更新静态数据（如骨骼列表）。 | `UK2Node_UpdateVirtualSubjectStaticData` |
| `Update Virtual Subject Frame Data` | 为虚拟主题更新某一帧的数据。 | `UK2Node_UpdateVirtualSubjectFrameData` |
| `Live Link Pose` (动画蓝图节点) | 在动画蓝图中直接使用，将 Live Link 的动画数据作为姿态输出。 | `UAnimGraphNode_LiveLinkPose` |

### 使用示例（蓝图描述）

1.  **获取实时骨骼动画**：
    *   在角色的动画蓝图中，可以使用 **`Live Link Pose`** 节点。在节点细节面板中选择对应的角色（如 `LiveLinkAnimationRole`）和主题名称。该节点的输出可以直接连接到动画蓝图的最终姿态输入。
2.  **在蓝图中读取实时数据**：
    *   使用 **`Evaluate Live Link Frame (At Scene Time)`** 节点。为 “Role” 引脚指定一个角色类（例如 `LiveLinkTransformRole`）。为 “Subject” 引脚指定要监听的主题名称。
    *   该节点会输出两个执行引脚：“Frame Available” 和 “Frame Not Available”。当数据可用时，可以从 “Frame Data” 引脚输出一个结构体（例如 `FLiveLinkTransformFrameData`），其中包含了实时的位置、旋转等数据。
    *   你可以将这些数据直接设置给场景中的一个 Actor，实现跟随外部设备运动的效果。
3.  **创建自定义数据主题**：
    *   使用 **`Update Virtual Subject Static Data`** 节点为你的自定义主题定义数据结构（例如，一个包含多个布尔值的结构体）。
    *   在每一帧（例如，在 `Event Tick` 中），使用 **`Update Virtual Subject Frame Data`** 节点，传入新的布尔值数据，从而“发布”数据到 Live Link 系统。其他监听此主题的蓝图或组件就能接收到这些数据。

## C++ 用法

Live Link 的 C++ 接口主要围绕 `ULiveLinkClient`、`FLiveLinkSubjectKey`、`FLiveLinkStaticDataStruct` 和 `FLiveLinkFrameDataStruct` 等核心类型展开。

### 头文件引入

```cpp
#include “LiveLinkTypes.h”
#include “LiveLinkRole.h”
#include “LiveLinkClient.h”
// 通常通过 Subsystem 获取 Client
#include “Subsystems/LiveLinkClientSubsystem.h”
```

### 基本用法

以下代码展示了如何在 C++ 中查询 Live Link 主题数据。

```cpp
// (示例概念代码，请根据实际项目结构调整)
void AMyActor::QueryLiveLinkData()
{
    // 1. 获取 Live Link 客户端子系统
    ULiveLinkClientSubsystem* LiveLinkSubsystem = UGameplayStatics::GetGameInstance(this)->GetSubsystem<ULiveLinkClientSubsystem>();
    if (LiveLinkSubsystem)
    {
        ULiveLinkClient* Client = LiveLinkSubsystem->GetClient();
        if (Client)
        {
            // 2. 构造主题标识符
            FName SubjectName(“MyMotionCaptureSubject”);
            FLiveLinkSubjectKey SubjectKey(SubjectName);

            // 3. 获取角色 (例如，变换角色)
            TSubclassOf<ULiveLinkRole> Role = ULiveLinkTransformRole::StaticClass();

            // 4. 查询最新的一帧数据
            FLiveLinkSubjectFrameData FrameData;
            bool bSuccess = Client->EvaluateFrame_AnyThread(SubjectKey, Role, FrameData);

            if (bSuccess)
            {
                // 5. 将通用帧数据转换为具体类型
                if (const FLiveLinkTransformFrameData* TransformData = FrameData.FrameData.Cast<FLiveLinkTransformFrameData>())
                {
                    // 使用实时变换数据
                    FVector Translation = TransformData->Transform.GetLocation();
                    FRotator Rotation = TransformData->Transform.Rotator();
                    // ... 应用到当前 Actor
                }
            }
        }
    }
}
```

### 进阶用法：创建自定义角色和主题

你可以定义自己的 `ULiveLinkRole` 子类来标准化某种特定类型的数据流（如 “CarTelemetryRole”）。

1.  **定义角色**：
    ```cpp
    UCLASS()
    class ULiveLinkCarTelemetryRole : public ULiveLinkRole
    {
        GENERATED_BODY()
        // ... 实现 GetStaticDataStruct(), GetFrameDataStruct() 等
    };
    ```
2.  **定义静态数据和帧数据结构**：
    ```cpp
    USTRUCT(BlueprintType)
    struct FCarTelemetryStaticData : public FLiveLinkBaseStaticData
    {
        GENERATED_BODY()
        // 例如：TArray<FName> WheelNames;
    };

    USTRUCT(BlueprintType)
    struct FCarTelemetryFrameData : public FLiveLinkBaseFrameData
    {
        GENERATED_BODY()
        // 例如：TArray<float> WheelRPMs; float Speed; bool bIsBraking;
    };
    ```
3.  **发布数据**：在拥有自定义数据的模块中，使用 `ULiveLinkClient` 的 `PushStaticData` 和 `PushFrameData` 方法将数据推送到 Live Link 系统。

## Demo 示例

一个简单的示例，演示如何创建一个 Actor，它在 Tick 中持续从 Live Link 获取某个主题的变换数据并应用到自身。

**MyLiveLinkFollower.h**
```cpp
#pragma once
#include “GameFramework/Actor.h”
#include “LiveLinkTypes.h”
#include “MyLiveLinkFollower.generated.h”

class ULiveLinkClientSubsystem;

UCLASS()
class AMyLiveLinkFollower : public AActor
{
    GENERATED_BODY()

public:
    AMyLiveLinkFollower();

    UPROPERTY(EditAnywhere, Category = “Live Link”)
    FName SubjectNameToFollow = “Default”;

protected:
    virtual void Tick(float DeltaTime) override;

private:
    TWeakObjectPtr<ULiveLinkClientSubsystem> CachedSubsystem;
};
```

**MyLiveLinkFollower.cpp**
```cpp
#include “MyLiveLinkFollower.h”
#include “Kismet/GameplayStatics.h”
#include “Subsystems/LiveLinkClientSubsystem.h”
#include “Roles/LiveLinkTransformRole.h”
#include “Roles/LiveLinkTransformTypes.h”

AMyLiveLinkFollower::AMyLiveLinkFollower()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyLiveLinkFollower::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 尝试获取子系统（缓存起来）
    if (!CachedSubsystem.IsValid())
    {
        if (UGameInstance* GI = GetGameInstance())
        {
            CachedSubsystem = GI->GetSubsystem<ULiveLinkClientSubsystem>();
        }
    }

    if (ULiveLinkClientSubsystem* Subsystem = CachedSubsystem.Get())
    {
        if (ULiveLinkClient* Client = Subsystem->GetClient())
        {
            FLiveLinkSubjectKey Key(SubjectNameToFollow);
            TSubclassOf<ULiveLinkRole> Role = ULiveLinkTransformRole::StaticClass();

            FLiveLinkSubjectFrameData FrameData;
            if (Client->EvaluateFrame_AnyThread(Key, Role, FrameData))
            {
                if (const auto* Data = FrameData.FrameData.Cast<FLiveLinkTransformFrameData>())
                {
                    // 将 Live Link 数据应用到 Actor
                    SetActorTransform(Data->Transform);
                }
            }
        }
    }
}
```

## 模块依赖

要使用 Live Link 插件的功能，你的模块通常需要依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `LiveLink` | 核心模块，提供客户端、主题、数据结构和网络基础。 |
| `LiveLinkComponents` | 提供 `ULiveLinkComponent`，方便在蓝图和场景中快速绑定一个主题。 |
| `LiveLinkInterface` | 定义角色（Role）和主题接口，是扩展 Live Link 数据类型的关键。 |
| `LiveLinkMessageBusFramework` | 底层网络消息总线框架，用于主题的发现和数据传输。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cd46766d` | Fix crash in ULiveLinkBroadcastComponent::PostEditChangeProperty when the broadcast subsystem is una | 修复广播组件在属性修改时的崩溃 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下的编译警告 |
| 2026-05-13 | `057dbc69` | Fix crashes in PostEditChangeProperty overrides when MemberProperty is null, which occurs when Pytho | 修复属性编辑器中的崩溃 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制片资产分类和迁移 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复作用域枚举导致的格式化输出问题 |

### 维护评价

- **活跃维护**：从 Git 历史看，该插件在 2026 年 5 月仍有明确的 bug 修复和功能调整（如虚拟制片资产迁移），表明 Epic 仍在积极维护和适配新的工作流。
- **成熟稳定**：作为 UE4.19 时期（2018年）引入的核心功能，经过 8 年的迭代，架构和 API 已非常成熟稳定，是虚拟制片和实时动捕的行业标准解决方案。
- **推荐使用**：**强烈推荐**。如果你的项目涉及任何形式的实时数据采集（动捕、面捕、外部设备数据），Live Link 是官方且功能完备的选择。它不是实验性功能，而是被广泛验证的生产工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink)
- 官方文档（插件内无链接，但 Epic 官网有详细虚拟制片文档）