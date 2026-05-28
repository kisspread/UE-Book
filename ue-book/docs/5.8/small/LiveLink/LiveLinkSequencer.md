# Live Link

> LiveLink allows streaming of animated data into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | 实时链接 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `LiveLink` (Runtime), `LiveLinkComponents` (Runtime), `LiveLinkEditor` (Runtime), `LiveLinkGraphNode` (Runtime), `LiveLinkMovieScene` (Runtime), `LiveLinkMultiUser` (Runtime), `LiveLinkSequencer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-02-27 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink) | |

**重要提示**：本插件默认未启用 (`EnabledByDefault: false`)，需在插件管理器或项目设置中手动启用。

### 用途

Live Link 是 UE5 中一个强大且灵活的数据流送框架，其核心作用是**将外部应用程序（如动捕软件、DCC工具、虚拟摄像机系统等）产生的实时数据（动画、变换、曲线、属性等）流式传输到引擎中**，用于驱动虚拟角色、摄像机、灯光或任意参数。

它解决的问题是：消除 DCC 工具与 UE 之间的手动导出/导入步骤，实现**跨应用程序的、低延迟的实时数据同步**。通过定义标准化的“角色”(Role) 和“主题”(Subject) 概念，它可以接受来自不同源、不同数据类型的流，并将其转化为引擎内可用的资产或参数。

**为什么存在？** 现代虚拟制片和动画管线要求实时反馈。动捕数据需要即时驱动游戏角色，DCC工具中的灯光和材质调整需要在引擎中实时预览。Live Link 提供了一个标准化的桥接层，使得这些集成成为可能。

### 使用场景

-   **动画师使用动捕设备驱动角色**：将 MotionBuilder 或其他动捕软件的数据实时流送到 UE 中的骨骼网格体。
-   **虚拟制片**：将专业虚拟摄像机系统（如 nDisplay、Stype、Mo-Sys）的摄像机变换数据流送至引擎，驱动虚拟场景中的摄像机。
-   **DCC 工具实时预览**：在 Maya 或 3ds Max 中调整模型或材质时，将更改实时同步到 UE 的编辑器视口中。
-   **自定义设备集成**：编写 Live Link 源插件，将任何自定义硬件或软件（如游戏手柄、IoT 传感器）的数据作为动画或属性流送。

### 蓝图用法

Live Link 在蓝图中主要通过其数据流和组件暴露功能。核心交互围绕“主题”(Subject) 展开。

#### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Live Link Subjects` | 获取当前所有可用 Live Link 主题的名称列表。 | `ULiveLinkBlueprintLibrary` |
| `Get Live Link Subject Frame Data` | 获取指定主题在某一时刻的静态和帧数据。 | `ULiveLinkBlueprintLibrary` |
| `Is Source Still Valid` | 检查指定的 Live Link 源是否仍然有效连接。 | `ULiveLinkBlueprintLibrary` |
| `Get Live Link Subject Role` | 获取指定主题当前绑定的角色类型。 | `ULiveLinkBlueprintLibrary` |
| `Evaluate Live Link Frame` | 对指定主题的帧数据进行求值，输出特定通道（如变换）的数据。 | `ULiveLinkBlueprintLibrary` |

#### 使用示例（蓝图描述）

1.  **获取所有主题**：在蓝图中拖拽 `Get Live Link Subjects` 节点，可获取当前连接的所有 Live Link 源提供的主题名称数组。
2.  **驱动场景物体**：
    -   使用 `Get Live Link Subject Frame Data` 节点，输入主题名（如 “Camera_01”）。
    -   将其输出连接到 `Evaluate Live Link Frame` 节点，并指定要评估的角色类型（如 `LiveLinkCameraRole`）。
    -   `Evaluate` 节点会输出一个结构体，其中包含 `Transform`、`FieldOfView` 等具体数据。
    -   将这些数据（如 `Transform`）连接到你场景中某个 Actor（如 CineCameraActor）的 `Set World Transform` 或其组件的相对变换节点上。
3.  **监听数据**：可以通过 `Event` > `Live Link` > `On Live Link Subject Added/Removed` 等事件来监听主题的动态变化。

### C++ 用法

在 C++ 中，主要使用 `ULiveLinkSubsystem` 和 `ULiveLinkBlueprintLibrary` 的 API 来获取数据，或者实现自定义的 `LiveLink Role` 和 `Controller`。

#### 头文件引入

```cpp
// 核心接口
#include “LiveLinkInterface/Public/LiveLinkTypes.h”

// 蓝图函数库（最常用）
#include “LiveLinkComponents/Public/LiveLinkBlueprintLibrary.h”

// 用于处理特定角色（如动画）
#include “LiveLink/Public/LiveLinkRemapAsset.h”

// 访问子系统
#include “Subsystems/LiveLinkSubsystem.h”

// 如果是编写自定义源或角色
#include “LiveLinkInterface/Public/ILiveLinkClient.h”
#include “LiveLinkInterface/Public/ILiveLinkSource.h”
```

#### 基本用法

从测试用例中提取的获取 Live Link 数据的标准方式。
```cpp
// 假设我们要获取名为 “MyMotionCapture” 的骨骼动画主题数据
FName SubjectName = “MyMotionCapture”;

// 通过蓝图函数库获取静态数据和最新帧数据
FLiveLinkStaticDataStruct StaticData;
FLiveLinkFrameDataStruct FrameData;
bool bSuccess = ULiveLinkBlueprintLibrary::GetLiveLinkSubjectStaticData(SubjectName, StaticData);
bSuccess &= ULiveLinkBlueprintLibrary::GetLiveLinkSubjectFrameData(SubjectName, FrameData);

if (bSuccess)
{
    // 检查角色是否为我们需要的类型（例如骨骼）
    TSubclassOf<ULiveLinkRole> Role = ULiveLinkBlueprintLibrary::GetLiveLinkSubjectRole(SubjectName);
    if (Role == ULiveLinkBasicRole::StaticClass())
    {
        // 将通用帧数据转换为具体角色类型的数据
        const FLiveLinkBaseStaticData* BaseStaticData = StaticData.GetStaticData<FLiveLinkBaseStaticData>();
        const FLiveLinkBaseFrameData* BaseFrameData = FrameData.GetFrameData<FLiveLinkBaseFrameData>();

        // 对于骨骼角色，可以进一步转换为 FLiveLinkSkeletonStaticData 和 FLiveLinkAnimationFrameData
        // ...
    }
}
```

#### 进阶用法

1.  **监听主题生命周期变化**：
    ```cpp
    // 在你的模块启动时或 Actor 初始化时
    ULiveLinkSubsystem* LiveLinkSubsystem = GEngine->GetEngineSubsystem<ULiveLinkSubsystem>();
    if (LiveLinkSubsystem)
    {
        // 绑定主题添加/移除的委托
        LiveLinkSubsystem->OnSubjectAdded().AddUObject(this, &AMyActor::OnLiveLinkSubjectAdded);
        LiveLinkSubsystem->OnSubjectRemoved().AddUObject(this, &AMyActor::OnLiveLinkSubjectRemoved);
    }

    void AMyActor::OnLiveLinkSubjectAdded(const FLiveLinkSubjectKey& SubjectKey)
    {
        UE_LOG(LogTemp, Log, TEXT(“Live Link 主题已添加: %s (来自源: %s)”), *SubjectKey.SubjectName.ToString(), *SubjectKey.Source.ToString());
        // 在这里可以开始自动订阅该主题的数据
    }
    ```

2.  **在组件中驱动变换（类似 AnimDataController）**：
    使用 `ULiveLinkTransformController` 组件或类似的逻辑，绑定到某个组件上，自动将其变换与 Live Link 主题同步。

### Demo 示例

以下是一个最小示例，展示如何在 C++ 中从 Live Link 获取一个名为 “VirtualCamera” 的主题的变换数据，并应用到当前 Actor 上。

**MyLiveLinkDrivenActor.h**
```cpp
// 版权所有 Epic Games, Inc. 保留所有权利。

#pragma once

#include “CoreMinimal.h”
#include “GameFramework/Actor.h”
#include “LiveLinkTypes.h”
#include “MyLiveLinkDrivenActor.generated.h”

UCLASS()
class AMyLiveLinkDrivenActor : public AActor
{
    GENERATED_BODY()

public:
    AMyLiveLinkDrivenActor();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

private:
    // 用于驱动此 Actor 的 Live Link 主题名
    UPROPERTY(EditAnywhere, Category = “Live Link”)
    FName LiveLinkSubjectName = “VirtualCamera”;

    // 缓存的主题键，用于检查主题是否仍然存在
    FLiveLinkSubjectKey CachedSubjectKey;

    // 查找并更新变换的函数
    void UpdateTransformFromLiveLink();
};
```

**MyLiveLinkDrivenActor.cpp**
```cpp
// 版权所有 Epic Games, Inc. 保留所有权利。

#include “MyLiveLinkDrivenActor.h”
#include “LiveLinkBlueprintLibrary.h”

AMyLiveLinkDrivenActor::AMyLiveLinkDrivenActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyLiveLinkDrivenActor::BeginPlay()
{
    Super::BeginPlay();
    // 在开始播放时，尝试查找一次主题以缓存 SubjectKey
    CachedSubjectKey = ULiveLinkBlueprintLibrary::FindSubject(LiveLinkSubjectName);
}

void AMyLiveLinkDrivenActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    UpdateTransformFromLiveLink();
}

void AMyLiveLinkDrivenActor::UpdateTransformFromLiveLink()
{
    // 1. 检查主题是否还有效（源可能已断开）
    if (!CachedSubjectKey.IsValid())
    {
        // 重新尝试查找
        CachedSubjectKey = ULiveLinkBlueprintLibrary::FindSubject(LiveLinkSubjectName);
        if (!CachedSubjectKey.IsValid()) return;
    }

    // 2. 获取该主题的最新帧数据
    FLiveLinkFrameDataStruct FrameData;
    if (ULiveLinkBlueprintLibrary::GetLiveLinkSubjectFrameData(LiveLinkSubjectName, FrameData))
    {
        // 3. 获取此主题的角色类型（假设我们知道它是变换类型）
        TSubclassOf<ULiveLinkRole> Role = ULiveLinkBlueprintLibrary::GetLiveLinkSubjectRole(LiveLinkSubjectName);
        if (Role == ULiveLinkTransformRole::StaticClass())
        {
            // 4. 将通用帧数据安全转换为变换角色的帧数据
            const FLiveLinkTransformFrameData* TransformFrameData = FrameData.GetFrameData<FLiveLinkTransformFrameData>();
            if (TransformFrameData)
            {
                // 5. 应用变换到当前 Actor
                // 注意：Live Link 通常提供世界空间变换，这里直接设置
                SetActorTransform(TransformFrameData->Transform);
            }
        }
    }
}
```

### 模块依赖

Live Link 插件结构复杂，模块间依赖清晰。使用特定功能需要依赖相应模块。

| 模块 | 用途 |
|---|---|
| `LiveLink` | 核心运行时模块，包含客户端、角色定义和数据结构。 |
| `LiveLinkComponents` | 提供蓝图函数库 (`ULiveLinkBlueprintLibrary`) 和可附加的 Live Link 组件。 |
| `LiveLinkSequencer` | 集成 Sequencer 和 Take Recorder，用于录制 Live Link 数据为动画轨道。 |
| `LiveLinkEditor` | 编辑器工具，如 Live Link 主题浏览器面板。 |
| `LiveLinkMovieScene` | 将 Live Link 数据映射到 Sequencer 轨道和通道。 |

你的模块 `Build.cs` 中需要添加：
```csharp
PublicDependencyModuleNames.AddRange(new string[] { “LiveLinkComponents” }); // 获取蓝图API
// 如果需要录制功能，则添加
// PublicDependencyModuleNames.AddRange(new string[] { “LiveLinkSequencer” });
```

### 维护状态

#### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cd46766d` | Fix crash in ULiveLinkBroadcastComponent::PostEditChangeProperty when the broadcast subsystem is una | 修复广播子系统未初始化时，广播组件属性编辑导致的崩溃。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量截断为浮点数产生的编译警告。 |
| 2026-05-13 | `057dbc69` | Fix crashes in PostEditChangeProperty overrides when MemberProperty is null, which occurs when Pytho | 修复 Python 脚本调用或特定反射操作时成员属性为空导致的崩溃。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制片优化：将多个 VP 资产迁移到新的资产分类和目录结构。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复作用域枚举在格式化函数中可能导致错误输出的问题。 |

#### 维护评价

Live Link 是 UE 虚拟制片和动画管线的核心支柱之一。尽管创建于 **2018 年（约 8 年前）**，属于 **老古董** 插件，但它**一直受到 Epic Games 的积极维护和功能更新**。从近期提交记录可以看出，团队仍在持续修复其稳定性和兼容性问题。

**推荐使用**。该插件是连接外部实时数据源与 UE 的标准且官方的解决方案，功能成熟，文档和社区支持完善。唯一需要注意的是，它**默认未启用**，需要手动开启。对于任何涉及实时数据驱动的项目（如动捕、虚拟制片、数字孪生），Live Link 都是首选工具。

### 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/live-link-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Animation/LiveLink/Source/LiveLinkEditor/Private/LiveLinkClient.cpp) （示例：客户端核心代码）