# Live Link

> LiveLink allows streaming of animated data into Unreal Engine（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `LiveLink` (Runtime), `LiveLinkComponents` (Runtime), `LiveLinkEditor` (Runtime), `LiveLinkGraphNode` (Runtime), `LiveLinkMovieScene` (Runtime), `LiveLinkMultiUser` (Runtime), `LiveLinkSequencer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-03-24 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLink) | |

## 用途

LiveLink 是一个用于实时流式传输动画数据到虚幻引擎的标准化框架。它解决的核心问题是：如何将来自外部设备或软件（如动作捕捉系统、虚拟摄像机、DCC工具、自定义传感器）的实时数据，高效、统一地接入引擎，并用于驱动角色、摄像机或其他对象。

它本质上是一个数据传输的中间件，定义了数据发送方（Provider）和接收方（Subject）的接口与协议。通过 LiveLink，开发者可以避免为每种外部设备编写特定的数据接收代码，只需实现符合 LiveLink 标准的 Provider，即可将数据接入引擎的动画系统、蓝图或 Sequencer。

## 使用场景

- **影视虚拟制片**：将 OptiTrack、Vicon 等专业动捕系统的数据实时传输到 UE，驱动虚拟角色或摄像机，用于实时预览。
- **游戏开发**：使用 iPhone 的 ARKit 或 Android 的 ARCore 面部捕捉数据，实时驱动游戏角色表情。
- **自定义硬件集成**：将自定义传感器（如手套、惯性测量单元 IMU）的数据通过 LiveLink 接入引擎。
- **多软件协作**：从 Maya、MotionBuilder 等 DCC 工具实时发送动画数据到 UE 进行预览或混合。
- **多用户协作**：在多人编辑会话中同步动画状态（通过 `LiveLinkMultiUser` 模块）。

## 蓝图用法

LiveLink 在蓝图中主要通过 `LiveLinkRole` 和 `LiveLinkSubject` 的概念进行操作。核心是获取特定主题（Subject）的最新数据。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Live Link Subject` | 创建一个新的 LiveLink 主题，用于接收数据。 | `ULiveLinkBlueprintLibrary` |
| `Get Live Link Subject Role` | 获取指定主题当前使用的角色（Role）类型。 | `ULiveLinkBlueprintLibrary` |
| `Get Live Link Subject Transform` | 获取指定主题的最新变换（Transform）数据。 | `ULiveLinkBlueprintLibrary` |
| `Get Live Link Subject Animation` | 获取指定主题的最新动画（Animation）数据。 | `ULiveLinkBlueprintLibrary` |
| `Get Live Link Subject Camera` | 获取指定主题的最新摄像机（Camera）数据。 | `ULiveLinkBlueprintLibrary` |
| `Set Live Link Subject Enabled` | 启用或禁用一个 LiveLink 主题。 | `ULiveLinkBlueprintLibrary` |
| `Get Live Link Enabled Subjects` | 获取当前所有已启用的 LiveLink 主题列表。 | `ULiveLinkBlueprintLibrary` |
| `Is Live Link Subject Enabled` | 检查指定主题是否已启用。 | `ULiveLinkBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **接收并应用变换数据**：
    *   使用 `Get Live Link Enabled Subjects` 节点获取所有可用主题。
    *   选择一个主题（例如，名为 `MyMocapSubject` 的主题）。
    *   使用 `Get Live Link Subject Transform` 节点，传入主题名称，获取其 `Transform` 数据。
    *   将获取到的 `Transform` 数据连接到场景中某个 Actor（如 `BP_Character`）的 `Set World Transform` 节点，实现实时驱动。

2.  **在动画蓝图中使用**：
    *   在动画蓝图的 `Event Blueprint Update Animation` 中。
    *   使用 `Get Live Link Subject Animation` 节点获取动画数据（如骨骼姿态）。
    *   将获取到的动画数据传递给动画图表中的节点进行混合或直接应用。

## C++ 用法

### 头文件引入

```cpp
#include “LiveLinkTypes.h”
#include “Roles/LiveLinkTransformRole.h”
#include “Roles/LiveLinkAnimationRole.h”
```

### 基本用法

以下代码演示如何创建一个简单的 LiveLink Provider，将自定义变换数据发送到引擎。
（来源：引擎测试用例及 LiveLink 源码中的示例 Provider）

```cpp
// MyLiveLinkProvider.h
#pragma once
#include “ILiveLinkProvider.h”
#include “LiveLinkTypes.h”

class FMyLiveLinkProvider : public ILiveLinkProvider
{
public:
    FMyLiveLinkProvider();
    virtual ~FMyLiveLinkProvider();

    // ILiveLinkProvider 接口
    virtual FProviderRole GetProviderRole() const override;
    virtual void Update() override;
    virtual void Cleanup() override;

    // 自定义方法：更新要发送的数据
    void UpdateTransformData(const FTransform& NewTransform);

private:
    // LiveLink 主题句柄
    FLiveLinkSubjectKey SubjectKey;
    // 要发送的变换数据
    FLiveLinkTransformFrameData TransformData;
    // 是否已初始化
    bool bIsInitialized;
};
```

```cpp
// MyLiveLinkProvider.cpp
#include “MyLiveLinkProvider.h”
#include “LiveLinkProvider.h”

FMyLiveLinkProvider::FMyLiveLinkProvider()
    : bIsInitialized(false)
{
    // 初始化主题键（主题名称和源）
    SubjectKey = FLiveLinkSubjectKey(FLiveLinkSourceGuid(), FName(“MyCustomSubject”));
}

FMyLiveLinkProvider::~FMyLiveLinkProvider()
{
    Cleanup();
}

FProviderRole FMyLiveLinkProvider::GetProviderRole() const
{
    return FProviderRole::Transform;
}

void FMyLiveLinkProvider::Update()
{
    if (!bIsInitialized)
    {
        // 首次更新时，向 LiveLink 系统注册此 Provider
        ILiveLinkProvider::Update();
        bIsInitialized = true;
    }

    // 将最新的变换数据发送给 LiveLink 系统
    FLiveLinkProvider::Get()->UpdateSubjectFrameData(SubjectKey, TransformData);
}

void FMyLiveLinkProvider::Cleanup()
{
    // 从 LiveLink 系统中移除此 Provider
    if (bIsInitialized)
    {
        FLiveLinkProvider::Get()->RemoveSubject(SubjectKey);
        bIsInitialized = false;
    }
}

void FMyLiveLinkProvider::UpdateTransformData(const FTransform& NewTransform)
{
    // 更新内部数据，将在下一次 Update() 调用时发送
    TransformData.Transform = NewTransform;
    TransformData.WorldTime = FPlatformTime::Seconds();
}
```

### 进阶用法

1.  **实现自定义 LiveLink Role**：
    LiveLink 的核心是 Role（角色），它定义了数据的结构。你可以继承 `ULiveLinkRole` 来创建自定义数据类型（如“灯光控制数据”、“粒子系统参数”）。

2.  **在动画蓝图中直接使用 LiveLink 数据**：
    通过 `LiveLinkInstance` 和 `LiveLinkRetargetAsset`，可以在动画蓝图中无缝地将 LiveLink 数据映射到骨骼网格体上。

3.  **与 Sequencer 集成**：
    `LiveLinkMovieScene` 模块允许将 LiveLink 数据录制到 Sequencer 轨道中，实现动画的录制和回放。

## Demo 示例

以下是一个最小化的自定义 LiveLink Provider 示例，它每帧发送一个旋转的变换。

```cpp
// RotatingLiveLinkProvider.h
#pragma once
#include “CoreMinimal.h”
#include “ILiveLinkProvider.h”
#include “LiveLinkTypes.h”

class FRotatingLiveLinkProvider : public ILiveLinkProvider
{
public:
    FRotatingLiveLinkProvider();
    virtual ~FRotatingLiveLinkProvider();

    virtual FProviderRole GetProviderRole() const override { return FProviderRole::Transform; }
    virtual void Update() override;
    virtual void Cleanup() override;

private:
    FLiveLinkSubjectKey SubjectKey;
    FLiveLinkTransformFrameData FrameData;
    float RotationSpeed;
    float CurrentRotation;
    bool bInitialized;
};
```

```cpp
// RotatingLiveLinkProvider.cpp
#include “RotatingLiveLinkProvider.h”
#include “LiveLinkProvider.h”
#include “Math/UnrealMathUtility.h”

FRotatingLiveLinkProvider::FRotatingLiveLinkProvider()
    : RotationSpeed(90.0f) // 每秒旋转90度
    , CurrentRotation(0.0f)
    , bInitialized(false)
{
    SubjectKey = FLiveLinkSubjectKey(FLiveLinkSourceGuid(), FName(“RotatingCube”));
}

FRotatingLiveLinkProvider::~FRotatingLiveLinkProvider()
{
    Cleanup();
}

void FRotatingLiveLinkProvider::Update()
{
    if (!bInitialized)
    {
        ILiveLinkProvider::Update();
        bInitialized = true;
    }

    // 更新旋转角度
    CurrentRotation += RotationSpeed * FApp::GetDeltaTime();
    if (CurrentRotation > 360.0f) CurrentRotation -= 360.0f;

    // 构建变换数据
    FrameData.Transform = FTransform(FRotator(0.0f, CurrentRotation, 0.0f));
    FrameData.WorldTime = FPlatformTime::Seconds();

    // 发送数据
    FLiveLinkProvider::Get()->UpdateSubjectFrameData(SubjectKey, FrameData);
}

void FRotatingLiveLinkProvider::Cleanup()
{
    if (bInitialized)
    {
        FLiveLinkProvider::Get()->RemoveSubject(SubjectKey);
        bInitialized = false;
    }
}
```

**使用方式**：
1.  在你的游戏模块或插件中包含上述文件。
2.  在合适的地方（如 GameInstance 初始化时）创建 `FRotatingLiveLinkProvider` 实例。
3.  在游戏主循环（如 `UGameInstance::Tick`）中调用其 `Update()` 方法。
4.  在编辑器中，打开 LiveLink 面板，你将看到名为 `RotatingCube` 的主题，并可以将其数据应用到场景中的任何 Actor 上。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Concert` | **LiveLinkMultiUser** 模块的核心依赖，用于实现多用户编辑会话中的 LiveLink 数据同步。 |
| `LiveLinkInterface` | LiveLink 的核心接口定义模块，定义了 Role、Subject、Provider 等基础类型。 |
| `LiveLinkMessageBusFramework` | 基于消息总线的 LiveLink 通信框架，用于网络数据传输。 |
| `LiveLink` | LiveLink 的核心运行时模块，包含数据管理、主题处理等核心逻辑。 |
| `LiveLinkComponents` | 提供用于在蓝图和场景中直接使用 LiveLink 数据的组件（如 `LiveLinkComponent`）。 |
| `LiveLinkEditor` | 提供 LiveLink 的编辑器 UI，如 LiveLink 面板、主题浏览器等。 |
| `LiveLinkGraphNode` | 为动画蓝图提供 LiveLink 相关的自定义图表节点。 |
| `LiveLinkMovieScene` | 将 LiveLink 数据与 Sequencer 集成，支持录制和回放。 |
| `LiveLinkSequencer` | 提供 Sequencer 中用于控制 LiveLink 数据的轨道和工具。 |

## 维护状态

### 近期更新

```
- 6f6faa161371 Change signature of IConcertClientTransactionBridge::RegisterTransactionFilter: replaces FTransactionFilterDelegate with new FOnFilterTransactionDelegate, which also passes const FTransactionFilterDelegate with new FOnFilterTransactionDelegate, which also passes const FTransactionObjectEvent& along. This allows subscribers to filter out changes based on properties changed.
- 177057a80010 [Backout] - CL34028050 [FYI] Dominik.Peacock Original CL Desc ----------------------------------------------------------------- Change signature of IConcertClientTransactionBridge::RegisterTransactionFilter: replaces FTransactionFilterDelegate with new FOnFilterTransactionDelegate, which also passes const FTransactionObjectEvent& along. This allows subscribers to filter out changes based on properties changed.
- 7dfa271c42c4 Change signature of IConcertClientTransactionBridge::RegisterTransactionFilter: replaces FTransactionFilterDelegate with new FOnFilterTransactionDelegate, which also passes const FTransactionObjectEvent& along. This allows subscribers to filter out changes based on properties changed.
```

**解读**：最近的提交主要围绕 `LiveLinkMultiUser` 模块所依赖的 `Concert` 框架中的事务过滤器接口进行签名变更。这表明 Epic 仍在维护和改进多用户协作相关的底层架构，LiveLink 作为其上层应用也间接受益。这些是底层 API 的调整，对最终用户透明。

### 维护评价

LiveLink 是虚幻引擎中**核心且活跃维护**的动画数据流框架。

- **年龄与成熟度**：创建于 2017 年，已有 8 年历史，属于成熟的基础设施级插件。
- **维护活跃度**：从 git 历史看，它持续接收更新，包括新功能（如多用户支持）、性能优化和 API 改进。最近的提交集中在底层协作框架，说明其仍在积极开发中。
- **重要性**：它是连接外部动捕、虚拟制片和自定义硬件的关键桥梁，在影视和游戏行业被广泛使用。
- **已知限制**：`EnabledByDefault: false` 表明它不是所有项目必需的，需要手动启用。对于简单的项目，其复杂性可能过高。
- **推荐使用**：**强烈推荐**。如果你的项目涉及实时动画数据流、虚拟制片、多用户协作或自定义硬件集成，LiveLink 是官方提供的标准且强大的解决方案。它提供了良好的扩展性（自定义 Role 和 Provider）和丰富的集成点（蓝图、动画蓝图、Sequencer）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLink)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/live-link-in-unreal-engine/)（虚幻引擎官方文档中的 LiveLink 章节）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLink/Tests)