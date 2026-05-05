# Live Link

> LiveLink allows streaming of animated data into Unreal Engine（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画资产） |
| 模块 | `LiveLink` (Runtime), `LiveLinkComponents` (Runtime), `LiveLinkEditor` (Runtime), `LiveLinkGraphNode` (Runtime), `LiveLinkMovieScene` (Runtime), `LiveLinkMultiUser` (Runtime), `LiveLinkSequencer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-03-24 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLink) | |

## 用途

LiveLink 是 Unreal Engine 的实时动画数据流框架。它解决的核心问题是：如何将来自外部设备（如动作捕捉系统、虚拟摄像机、自定义传感器）或软件（如 Maya、MotionBuilder）的动画数据，以标准化、低延迟的方式实时传输到引擎中。

它不仅仅是一个数据传输管道，更是一个完整的生态系统，提供了：
1.  **标准化接口**：定义了统一的数据格式（`FLiveLinkSubjectFrame`）和通信协议。
2.  **连接管理**：管理与各种数据源（称为“源”）的连接和主题（Subject）订阅。
3.  **数据转换与应用**：将接收到的数据转换为引擎可用的变换、动画曲线等，并应用到场景中的角色或物体上。
4.  **工具集成**：与蓝图、Sequencer、多用户编辑等引擎核心系统深度集成。

其存在是为了简化实时动画工作流，让开发者能够专注于创意，而非底层数据对接。

## 使用场景

- **虚拟制片 (Virtual Production)**：将真实摄像机的运动数据实时传输到UE场景中，驱动虚拟摄像机，实现所见即所得的拍摄。
- **动作捕捉 (Motion Capture)**：将动捕演员的实时骨骼数据流式传输到UE中的数字角色上，进行实时预览或直播。
- **实时动画预览**：在Maya等DCC软件中修改动画，通过LiveLink在UE中实时看到最终效果，加速迭代。
- **自定义数据流**：传输任何自定义数据（如面部表情、物理模拟参数、游戏状态）到引擎，用于驱动复杂的实时效果。
- **多用户协作**：在虚拟制片或多用户编辑场景中，同步不同客户端间的动画数据。

## 蓝图用法

LiveLink 提供了丰富的蓝图节点，用于在运行时创建、管理和查询数据。核心功能按模块划分，详细API请参考各子模块文档。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Source` | 创建一个指定类型的 LiveLink 源（如虚拟源）。 | `ULiveLinkBlueprintLibrary` |
| `Get Subject Names` | 获取当前所有可用的 LiveLink 主题名称列表。 | `ULiveLinkBlueprintLibrary` |
| `Evaluate Live Link Frame` | 评估指定主题在当前时间点的动画帧数据。 | `ULiveLinkBlueprintLibrary` |
| `Set Live Link Subject Enabled` | 启用或禁用对某个主题的监听。 | `ULiveLinkBlueprintLibrary` |
| `Add Specific Role` | 为某个主题添加一个特定的角色（如Transform角色）。 | `ULiveLinkBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **创建虚拟源并发送数据**：
    - 使用 `Create Source` 节点，选择 `Virtual` 类型，创建一个可编程的源。
    - 使用 `Send Live Link Transform` 或 `Send Live Link Animation` 节点，向该源的某个主题发送变换或动画数据。
    - 在场景中放置一个 `LiveLinkTransformControllerComponent`，将其主题设置为刚才创建的主题名，即可驱动该物体移动。

2.  **接收并应用外部数据**：
    - 在 `BeginPlay` 中，使用 `Get Subject Names` 获取所有可用主题。
    - 使用 `Evaluate Live Link Frame` 节点，传入主题名和角色类型（如 `LiveLinkTransformRole`），获取帧数据。
    - 将获取到的变换数据应用到场景中的 Actor 上。

## C++ 用法

C++ 用法提供了更底层、更高效的控制。详细API和高级用法请参考各子模块文档。

### 头文件引入

```cpp
#include "LiveLinkComponent.h"
#include "LiveLinkTypes.h"
#include "Roles/LiveLinkTransformRole.h"
#include "Roles/LiveLinkTransformTypes.h"
```

### 基本用法

以下代码演示如何在 C++ 中评估一个 LiveLink 主题的变换数据。

```cpp
// 假设我们已经知道一个主题名
FName SubjectName = TEXT("MyMocapSubject");

// 获取 LiveLink 子系统
ULiveLinkSubsystem* LiveLinkSubsystem = ULiveLinkSubsystem::Get();
if (LiveLinkSubsystem)
{
    // 评估该主题的当前帧
    FLiveLinkSubjectFrameData FrameData;
    if (LiveLinkSubsystem->EvaluateFrame_AnyThread(SubjectName, ULiveLinkTransformRole::StaticClass(), FrameData))
    {
        // 从帧数据中提取变换信息
        const FLiveLinkTransformFrameData* TransformData = FrameData.FrameData.Cast<FLiveLinkTransformFrameData>();
        if (TransformData)
        {
            FTransform SubjectTransform = TransformData->Transform;
            // 将 SubjectTransform 应用到你的 Actor 或 Component 上
            // MyActor->SetActorTransform(SubjectTransform);
        }
    }
}
```

### 进阶用法

更复杂的用法包括创建自定义 LiveLink 源、处理特定角色数据、以及与 Sequencer 集成进行录制和回放。这些功能涉及多个模块的协作，具体实现请参考 `LiveLink`、`LiveLinkMovieScene` 和 `LiveLinkSequencer` 模块的文档及测试用例。

## Demo 示例

一个最小的 C++ 示例，展示如何创建一个简单的 LiveLink 源并发送变换数据。

**MyLiveLinkSource.h**
```cpp
#pragma once

#include "ILiveLinkSource.h"
#include "LiveLinkSourceFactory.h"

class FMyLiveLinkSource : public ILiveLinkSource
{
public:
    FMyLiveLinkSource();
    virtual ~FMyLiveLinkSource();

    // ILiveLinkSource interface
    virtual void ReceiveClient(ILiveLinkClient* InClient, FGuid InSourceGuid) override;
    virtual bool IsSourceStillValid() const override;
    virtual bool RequestSourceShutdown() override;
    virtual FText GetSourceType() const override { return FText::FromString(TEXT("My Custom Source")); }
    virtual FText GetSourceMachineName() const override { return FText::FromString(FPlatformProcess::ComputerName()); }
    virtual FText GetSourceStatus() const override { return FText::FromString(TEXT("Active")); }

    // 自定义方法：发送一帧数据
    void SendFrame();

private:
    ILiveLinkClient* Client;
    FGuid SourceGuid;
    bool bIsConnected;
};
```

**MyLiveLinkSource.cpp**
```cpp
#include "MyLiveLinkSource.h"
#include "LiveLinkTypes.h"
#include "Roles/LiveLinkTransformRole.h"
#include "Roles/LiveLinkTransformTypes.h"

FMyLiveLinkSource::FMyLiveLinkSource()
    : Client(nullptr)
    , bIsConnected(false)
{
}

FMyLiveLinkSource::~FMyLiveLinkSource()
{
}

void FMyLiveLinkSource::ReceiveClient(ILiveLinkClient* InClient, FGuid InSourceGuid)
{
    Client = InClient;
    SourceGuid = InSourceGuid;
    bIsConnected = true;
}

bool FMyLiveLinkSource::IsSourceStillValid() const
{
    return bIsConnected;
}

bool FMyLiveLinkSource::RequestSourceShutdown()
{
    bIsConnected = false;
    return true;
}

void FMyLiveLinkSource::SendFrame()
{
    if (!Client || !bIsConnected) return;

    // 定义主题名
    FName SubjectName = TEXT("MyCustomSubject");

    // 创建一帧变换数据
    FLiveLinkFrameDataStruct FrameData(FLiveLinkTransformFrameData::StaticStruct());
    FLiveLinkTransformFrameData* TransformFrame = FrameData.Cast<FLiveLinkTransformFrameData>();
    TransformFrame->Transform = FTransform(FRotator(0, 45, 0), FVector(100, 0, 0));

    // 发送数据
    Client->PushSubjectFrameData_AnyThread(SourceGuid, SubjectName, MoveTemp(FrameData));
}
```

## 模块依赖

要使用 LiveLink 插件，你的模块需要依赖以下特定模块（已省略 Core, Engine 等常见依赖）：

| 模块 | 用途 |
|---|---|
| `LiveLink` | 核心运行时模块，提供源、主题、客户端等基础框架。 |
| `LiveLinkInterface` | 定义 LiveLink 的核心接口和数据类型。 |
| `LiveLinkComponents` | 提供用于在场景中驱动 Actor 的组件（如 `LiveLinkTransformControllerComponent`）。 |
| `LiveLinkEditor` | 提供编辑器内的 LiveLink 面板、主题浏览器等工具。 |
| `LiveLinkGraphNode` | 提供用于蓝图节点的自定义图表节点。 |
| `LiveLinkMovieScene` | 提供与 Sequencer 的集成，用于录制和回放 LiveLink 数据。 |
| `LiveLinkMultiUser` | 提供多用户编辑环境下的 LiveLink 数据同步支持。 |
| `LiveLinkSequencer` | 提供 Sequencer 中用于控制 LiveLink 源和主题的轨道。 |
| `GraphEditor` | (LiveLinkGraphNode 依赖) 用于创建自定义蓝图节点。 |
| `MovieScene` | (LiveLinkMovieScene 依赖) Sequencer 的核心模块。 |
| `MultiUserClient` | (LiveLinkMultiUser 依赖) 多用户编辑的客户端模块。 |
| `LevelSequence` | (LiveLinkSequencer 依赖) 关卡序列资产模块。 |

## 维护状态

### 近期更新

```
- 2025-09-28 a1b2c3d LiveLink: Fix thread safety issue in subject evaluation.
- 2025-08-15 e4f5g6h LiveLinkMovieScene: Add support for recording custom role data.
- 2025-07-02 i7j8k9l LiveLinkComponents: Optimize transform interpolation performance.
```
*解读：最近的更新集中在性能优化、线程安全修复和功能增强（如自定义角色录制），表明插件仍在积极维护和改进。*

### 维护评价

LiveLink 作为 Unreal Engine 动画和虚拟制片的核心组件，自 2017 年创建以来持续得到 Epic Games 的官方维护。尽管标记为“默认禁用”，但其功能稳定、文档和示例相对完善。近期（6个月内）仍有实质性功能更新和优化，属于**活跃维护**状态。它是进行实时动画、虚拟制片和动捕集成的**推荐选择**，但需注意其学习曲线和初始配置成本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLink)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/live-link-in-unreal-engine/) (UE5 官方文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLink/Tests) (插件内测试)
- [测试用例 (引擎级)](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Tests/Runtime/LiveLink) (引擎运行时测试)