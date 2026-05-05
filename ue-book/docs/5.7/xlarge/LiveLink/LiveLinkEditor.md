# Live Link

> LiveLink allows streaming of animated data into Unreal Engine

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `LiveLink` (Runtime), `LiveLinkComponents` (Runtime), `LiveLinkEditor` (Runtime), `LiveLinkGraphNode` (Runtime), `LiveLinkMovieScene` (Runtime), `LiveLinkMultiUser` (Runtime), `LiveLinkSequencer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-03-24 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLink) | |

## 用途

Live Link 是 Unreal Engine 中用于实时数据流传输的核心框架。它不仅仅是一个简单的动画数据传输工具，而是一个**标准化的数据流管道**。其核心价值在于：

1.  **解耦数据源与消费端**：它定义了一套标准化的接口（`ULiveLinkRole`， `ULiveLinkSubject`），使得任何能够产生结构化数据（如动画、变换、相机参数、灯光属性等）的外部应用程序或设备（如动作捕捉系统、虚拟摄像机、DCC软件、自定义传感器）都可以通过实现一个 `ULiveLinkSourceFactory` 来接入 UE。
2.  **统一的数据管理**：所有通过 Live Link 接入的数据都以“主题”（Subject）的形式在引擎内统一管理。用户可以在一个集中的面板（Live Link 面板）中查看、调试、过滤和管理所有活跃的数据流。
3.  **深度引擎集成**：Live Link 的数据可以直接驱动引擎内的各种系统，包括：
    *   **动画系统**：驱动骨骼网格体、动画蓝图。
    *   **Sequencer**：录制和回放实时数据流，用于虚拟制片。
    *   **蓝图**：通过 `LiveLinkComponent` 或蓝图节点直接读取实时数据。
    *   **多用户编辑**：在多人协作环境中同步 Live Link 数据。

简而言之，Live Link 解决了**将外部实时数据标准化、高效地接入并深度集成到 UE 各个子系统**的问题，是虚拟制片、实时动画、仿真和数据可视化等领域的基石。

## 使用场景

-   **虚拟制片 (Virtual Production)**：将真实摄像机的跟踪数据（位置、旋转、镜头参数）通过 Live Link 实时传输到 UE 中，驱动虚拟摄像机，实现所见即所得的拍摄。
-   **动作捕捉 (Motion Capture)**：将来自 Vicon、OptiTrack、Xsens 等动捕系统的骨骼数据实时流式传输到 UE 中，驱动数字角色。
-   **面部捕捉 (Facial Capture)**：将 iPhone ARKit、Faceware 等设备的面部表情数据实时映射到角色面部。
-   **DCC 软件实时预览**：在 Maya、3ds Max、Blender 中修改模型或动画，通过 Live Link 插件实时在 UE 中看到更新效果。
-   **自定义数据流**：开发自定义的 Live Link 源，将游戏手柄输入、传感器数据、网络数据包等任何结构化信息实时传入引擎。
-   **多用户协作**：在虚拟制片片场，多个工作站（如导演监视器、灯光控制台）需要同步接收相同的摄像机或角色数据。
-   **动画录制与回放**：在 Sequencer 中录制通过 Live Link 接收的实时动画数据，用于后期编辑或创建过场动画。

## 蓝图用法

Live Link 提供了丰富的蓝图接口，主要集中在 `LiveLinkComponents` 模块和核心蓝图库中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Live Link Subjects` | 获取当前所有可用的 Live Link 主题名称列表。 | `ULiveLinkBlueprintLibrary` |
| `Get Live Link Subject Role` | 获取指定主题当前使用的角色（Role）类型。 | `ULiveLinkBlueprintLibrary` |
| `Get Live Link Transform` | 从指定主题获取最新的变换（位置、旋转、缩放）数据。 | `ULiveLinkBlueprintLibrary` |
| `Get Live Link Animation` | 从指定主题获取最新的动画曲线数据（用于驱动 Morph Target 或材质参数）。 | `ULiveLinkBlueprintLibrary` |
| `Evaluate Live Link Frame` | 评估指定主题在特定时间点的帧数据，返回一个包含所有属性的结构体。 | `ULiveLinkBlueprintLibrary` |
| `Live Link Component` | 一个组件，可以附加到 Actor 上，自动接收并缓存指定主题的数据。 | `ULiveLinkComponent` |
| `Get Live Link Data` | 从 `LiveLinkComponent` 获取其缓存的最新数据。 | `ULiveLinkComponent` |

### 使用示例（蓝图描述）

**示例1：在蓝图中直接获取实时变换数据**
1.  在蓝图中，使用 `Get Live Link Subjects` 节点获取所有主题列表。
2.  将目标主题名称（例如 “Camera_01”）连接到 `Get Live Link Transform` 节点的 `Subject Name` 输入。
3.  `Get Live Link Transform` 节点的输出 `Transform` 即为该主题最新的世界变换数据，可以直接用于设置某个 Actor 的位置和旋转。

**示例2：使用 LiveLinkComponent 驱动 Actor**
1.  在你的 Actor 蓝图中，添加一个 `LiveLinkComponent`。
2.  在组件的细节面板中，设置 `Subject Representation`（主题表示），选择你要监听的主题和角色（例如，一个摄像机主题和 `LiveLinkCameraRole`）。
3.  在事件图表中，使用 `Get Live Link Data` 节点从该组件获取数据。
4.  将返回的数据结构体（例如 `FLiveLinkCameraFrameData`）拆解，用其中的 `Transform`、`FieldOfView` 等属性来更新你 Actor 的摄像机组件。

## C++ 用法

C++ 用法提供了更底层、更灵活的控制，适合创建自定义源、角色或进行高性能数据处理。

### 头文件引入

```cpp
// 核心 Live Link 类型和客户端
#include "LiveLinkClient.h"
#include "LiveLinkTypes.h"
#include "Roles/LiveLinkTransformRole.h"
#include "Roles/LiveLinkTransformTypes.h"

// 如果需要创建自定义源
#include "ILiveLinkClient.h"
#include "LiveLinkSourceFactory.h"

// 如果需要创建自定义角色
#include "LiveLinkRole.h"
#include "LiveLinkFrameInterpolationProcessor.h"
```

### 基本用法

**获取 Live Link 客户端并查询主题数据**
```cpp
// 来源：引擎内部或自定义模块
#include "ILiveLinkClient.h"
#include "LiveLinkTypes.h"

void QueryLiveLinkData()
{
    // 获取 Live Link 客户端单例
    ILiveLinkClient* LiveLinkClient = ILiveLinkClient::Get();
    if (!LiveLinkClient)
    {
        return;
    }

    // 获取所有主题键
    TArray<FLiveLinkSubjectKey> SubjectKeys;
    LiveLinkClient->GetSubjects(SubjectKeys);

    // 遍历查找目标主题
    for (const FLiveLinkSubjectKey& Key : SubjectKeys)
    {
        if (Key.SubjectName == FName("MyCameraSubject"))
        {
            // 获取该主题的最新静态数据（如骨骼列表、属性定义）
            FLiveLinkStaticDataStruct StaticData;
            LiveLinkClient->GetSubjectStaticData(Key, StaticData);

            // 获取该主题的最新帧数据
            FLiveLinkFrameDataStruct FrameData;
            LiveLinkClient->GetSubjectFrameData(Key, FrameData);

            // 如果是变换角色，可以安全地转换数据
            if (FrameData.IsValid() && FrameData.GetStruct()->IsChildOf(FLiveLinkTransformFrameData::StaticStruct()))
            {
                const FLiveLinkTransformFrameData* TransformData = FrameData.Cast<FLiveLinkTransformFrameData>();
                FTransform CurrentTransform = TransformData->Transform;
                // ... 使用 CurrentTransform
            }
            break;
        }
    }
}
```

### 进阶用法

**创建自定义的 Live Link 源工厂**
你需要继承 `ULiveLinkSourceFactory` 并实现其接口，以允许用户在 Live Link 面板中添加你的自定义数据源。
```cpp
// MyCustomSourceFactory.h
#pragma once
#include "LiveLinkSourceFactory.h"
#include "MyCustomSourceFactory.generated.h"

UCLASS()
class UMyCustomSourceFactory : public ULiveLinkSourceFactory
{
    GENERATED_BODY()

public:
    // 在 Live Link 面板“添加源”菜单中显示的名称
    virtual FText GetDisplayName() const override;

    // 创建并返回你的自定义源实例
    virtual TSharedPtr<ILiveLinkSource> CreateSource(const FString& ConnectionString) const override;

    // 可选：提供一个自定义的 UI 面板让用户配置源
    virtual TSharedPtr<SWidget> BuildCreationPanel(FOnLiveLinkSourceCreated OnLiveLinkSourceCreated) const override;
};
```

**为自定义数据类型创建角色**
你需要继承 `ULiveLinkRole` 并定义该角色所携带的数据结构。
```cpp
// MyCustomRole.h
#pragma once
#include "LiveLinkRole.h"
#include "MyCustomRole.generated.h"

UCLASS()
class UMyCustomRole : public ULiveLinkRole
{
    GENERATED_BODY()

public:
    // 获取此角色对应的静态数据结构类型
    virtual UScriptStruct* GetStaticDataStruct() const override;
    // 获取此角色对应的帧数据结构类型
    virtual UScriptStruct* GetFrameDataStruct() const override;
    // 获取此角色对应的蓝图数据结构类型（用于蓝图节点）
    virtual UScriptStruct* GetBlueprintDataStruct() const override;
};
```

## Demo 示例

以下是一个最小化的自定义 Live Link 主题消费者示例，它创建一个 Actor，通过 Live Link 实时接收并应用变换数据。

**MyLiveLinkDrivenActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "LiveLinkTypes.h"
#include "MyLiveLinkDrivenActor.generated.h"

UCLASS()
class AMyLiveLinkDrivenActor : public AActor
{
    GENERATED_BODY()

public:
    AMyLiveLinkDrivenActor();

    virtual void Tick(float DeltaTime) override;

    // 在编辑器中设置要监听的主题名称
    UPROPERTY(EditAnywhere, Category = "Live Link")
    FName SubjectName = "MySubject";

private:
    // 缓存主题键，避免每帧查找
    FLiveLinkSubjectKey CachedSubjectKey;
    bool bSubjectKeyCached = false;
};
```

**MyLiveLinkDrivenActor.cpp**
```cpp
#include "MyLiveLinkDrivenActor.h"
#include "ILiveLinkClient.h"
#include "Roles/LiveLinkTransformRole.h"
#include "Roles/LiveLinkTransformTypes.h"

AMyLiveLinkDrivenActor::AMyLiveLinkDrivenActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyLiveLinkDrivenActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    ILiveLinkClient* LiveLinkClient = ILiveLinkClient::Get();
    if (!LiveLinkClient)
    {
        return;
    }

    // 首次 Tick 时缓存主题键
    if (!bSubjectKeyCached)
    {
        TArray<FLiveLinkSubjectKey> AllKeys;
        LiveLinkClient->GetSubjects(AllKeys);
        for (const FLiveLinkSubjectKey& Key : AllKeys)
        {
            if (Key.SubjectName == SubjectName)
            {
                CachedSubjectKey = Key;
                bSubjectKeyCached = true;
                break;
            }
        }
        if (!bSubjectKeyCached) return; // 主题尚未出现
    }

    // 获取最新帧数据
    FLiveLinkFrameDataStruct FrameData;
    if (LiveLinkClient->GetSubjectFrameData(CachedSubjectKey, FrameData))
    {
        // 假设我们监听的是一个变换角色
        if (FrameData.GetStruct()->IsChildOf(FLiveLinkTransformFrameData::StaticStruct()))
        {
            const FLiveLinkTransformFrameData* TransformFrame = FrameData.Cast<FLiveLinkTransformFrameData>();
            if (TransformFrame)
            {
                // 将接收到的变换应用到本 Actor
                SetActorTransform(TransformFrame->Transform);
            }
        }
    }
}
```

## 模块依赖

要使用 Live Link 的核心功能，你的模块通常需要依赖 `LiveLink` 模块。如果需要使用蓝图组件，则依赖 `LiveLinkComponents`。

| 模块 | 用途 |
|---|---|
| `LiveLink` | 核心运行时库，包含客户端、主题、角色等基础类。 |
| `LiveLinkComponents` | 提供 `ULiveLinkComponent` 等蓝图友好的组件。 |
| `LiveLinkEditor` | 编辑器 UI，包括 Live Link 面板、主题选择器等。 |
| `LiveLinkMovieScene` | 与 Sequencer 集成，用于录制和回放 Live Link 数据。 |
| `LiveLinkMultiUser` | 支持多用户编辑环境下的 Live Link 数据同步。 |

## 维护状态

### 近期更新

```
- f18c90b57480 LiveLink - Fix Settings icon not leading to right settings section
- 27ec2e40ee17 LiveLink - Fix Settings and Visibility icons
- 7937b868b835 LiveLink - Fix possible ensure caused by accessing Subject dropdwon with no valid objects
```
最近的提交集中在修复编辑器 UI 的小问题（图标、设置跳转、空指针保护），表明插件处于稳定的维护状态，主要进行缺陷修复和体验优化。

### 维护评价

Live Link 是 Unreal Engine 虚拟制片和实时动画工作流的**核心支柱**插件。它创建于 2017 年，历史悠久，但至今仍是引擎中活跃且关键的一部分。
- **活跃维护**：尽管最近的更新主要是 UI 修复，但考虑到其核心地位和广泛使用，Epic Games 会持续维护它以确保稳定性和兼容性。
- **功能成熟**：经过多年发展，其核心架构（源、主题、角色）已经非常稳定和强大。
- **生态丰富**：围绕 Live Link 已经建立了庞大的生态系统，包括官方和第三方的各种源插件。
- **推荐使用**：对于任何涉及实时外部数据集成到 UE 的项目，Live Link 都是**首选且推荐**的解决方案。它功能全面、文档相对完善（尽管分散）、社区支持广泛。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLink)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/live-link-in-unreal-engine/) (通用文档链接，具体页面可能变化)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLink/Tests) (如果存在)