# Live Link

> LiveLink allows streaming of animated data into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | 实时数据链接 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、内容资产） |
| 模块 | `LiveLink` (Runtime), `LiveLinkComponents` (Runtime), `LiveLinkEditor` (Runtime), `LiveLinkGraphNode` (Runtime), `LiveLinkMovieScene` (Runtime), `LiveLinkMultiUser` (Runtime), `LiveLinkSequencer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-02-27 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink) | |

## 用途

Live Link 是一个用于将实时外部数据流（主要是动画数据，但不限于）引入虚幻引擎的框架。它不仅仅是一个简单的“流式传输”工具，而是一个完整的、可扩展的数据管道系统。其核心作用是建立一个标准化的接口，让任何外部应用程序（如动作捕捉软件、虚拟摄像机控制器、自定义传感器等）能够将数据（如骨骼变换、曲线值、场景时间码等）实时、高效地同步到虚幻引擎中。

它的存在解决了虚幻引擎与外部实时数据源之间的集成问题，为虚拟制片、实时动捕、自定义控制面板等高级工作流提供了基础支撑。

## 使用场景

- **虚拟制片 (Virtual Production)**：你正在使用摄像头追踪系统（如 OptiTrack、Vicon）驱动虚拟摄像机，需要将摄像机的位置、旋转实时映射到 UE 中的虚拟摄像机上。
- **动作捕捉 (Motion Capture)**：你在使用实时动捕软件（如 Vicon Shōgun、Xsens）捕捉演员表演，需要将骨骼数据实时驱动 UE 角色的动画。
- **外部控制器 (External Controller)**：你有一个自定义的物理控制器（如游戏手柄、硬件面板），希望通过它实时控制 UE 中某个物体的属性或触发事件。
- **数据采集与可视化 (Data Acquisition & Visualization)**：你正在接收来自传感器（如 IMU、温度传感器）的数据流，并希望在 UE 场景中实时可视化这些数据。
- **同步录制与回放 (Synchronized Recording & Playback)**：你使用 Live Link 录制了外部数据，并希望与 Sequencer 中的动画序列同步播放，以便进行精确的后期编辑。

## 蓝图用法

Live Link 为蓝图提供了丰富的节点，用于与实时数据流交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Evaluate Live Link Frame` | 核心评估节点，用于获取指定 Live Link 主体在某一时间点（引擎时间、世界时间或场景时间）的静态数据或帧数据。 | `UK2Node_EvaluateLiveLinkFrame` (及子类) |
| `Update Virtual Subject Static Data` | 向一个虚拟主体推送静态数据更新。 | `UK2Node_UpdateVirtualSubjectStaticData` |
| `Update Virtual Subject Frame Data` | 向一个虚拟主体推送帧数据更新。 | `UK2Node_UpdateVirtualSubjectFrameData` |
| `Live Link Pose` (动画蓝图节点) | 动画蓝图中的一个特殊节点，可直接使用 Live Link 骨骼数据来驱动骨骼网格体的姿势。 | `UAnimGraphNode_LiveLinkPose` |

### 使用示例（蓝图描述）

1.  **评估数据**：在蓝图中，拖拽出 `Evaluate Live Link Frame At World Time` 节点。连接 `Subject` 引脚到一个 `Live Link Subject Name` 变量。将 `Role` 引脚设置为期望的数据类型（如 `Live Link Animation Role`）。`Static Data` 和 `Frame Data` 输出引脚将包含解析后的具体数据结构，可进一步拆解使用。连接 `Frame Not Available` 执行引脚以处理数据缺失情况。
2.  **驱动角色**：在动画蓝图中，添加 `Live Link Pose` 节点。在节点的细节面板中，指定 `Subject` 和 `Role`。将节点的输出姿势连接到 `Output Pose` 或其他动画节点，即可用实时数据驱动角色。
3.  **更新虚拟主体**：创建一个虚拟主体后，使用 `Update Virtual Subject Frame Data` 节点。连接 `Live Link Transform` 数据和 `Timestamp`，即可向引擎中注册的虚拟主体推送数据，其他蓝图可以像使用真实数据源一样评估它。

## C++ 用法

Live Link 的 C++ API 允许开发者创建自定义的源、评估器和客户端来深度集成。

### 头文件引入

```cpp
#include "ILiveLinkClient.h"
#include "LiveLinkRole.h"
#include "LiveLinkTypes.h"
```

### 基本用法（评估帧数据）

```cpp
// 获取 Live Link 客户端单例
ILiveLinkClient* LiveLinkClient = ILiveLinkClient::Get();

// 构造一个要评估的主体信息
FLiveLinkSubjectKey SubjectKey;
SubjectKey.SubjectName = FName("MySubject");
SubjectKey.ConnectorName = FName("MyConnector");

// 构造评估策略
FLiveLinkSubjectFrameData FrameData;
FLiveLinkStaticDataStruct StaticData;
FLiveLinkFrameDataStruct EvaluatedFrameData;

// 在引擎时间 0.5 秒时评估
if (LiveLinkClient->EvaluateFrame_AnyThread(SubjectKey, StaticData, EvaluatedFrameData, 0.5f))
{
    // 成功获取帧数据，EvaluatedFrameData 现在包含了具体角色的数据
    if (const FAnimFrameData* AnimData = EvaluatedFrameData.Cast<FAnimFrameData>())
    {
        // 使用 AnimData->Transforms 访问骨骼变换数组
    }
}
```
*(来源：公开 API 推断，常见用法)*

### 进阶用法（创建自定义数据源）

创建自定义数据源需要实现 `ILiveLinkSource` 接口，并在模块启动时注册到 `ILiveLinkClient`。你需要负责连接外部数据、将其转换为 Live Link 标准格式，并定时推送到客户端。这通常用于接入新的动捕设备或自定义协议。

## Demo 示例

以下是一个最小化的示例，展示如何创建一个简单的 Live Link 源，向引擎推送一个立方体的变换数据。

**MyLiveLinkSource.h**
```cpp
#pragma once
#include "ILiveLinkSource.h"

class FMyLiveLinkSource : public ILiveLinkSource
{
public:
    virtual ~FMyLiveLinkSource() {}
    virtual void ReceiveClient(ILiveLinkClient* InClient, FGuid InSourceGuid) override;
    virtual void InitializeSettings(ULiveLinkSourceSettings* Settings) override;
    virtual void Update() override;
    virtual bool CanBeDisplayedInUI() const override { return true; }
    virtual FText GetSourceType() const override;
    virtual FText GetSourceMachineName() const override { return FText::FromString(FPlatformProcess::ComputerName()); }
    virtual FText GetSourceStatus() const override;

private:
    ILiveLinkClient* Client = nullptr;
    FGuid SourceGuid;
    FLiveLinkSubjectKey SubjectKey;
    float TimeElapsed = 0.f;
};
```

**MyLiveLinkSource.cpp**
```cpp
#include "MyLiveLinkSource.h"
#include "ILiveLinkClient.h"
#include "Roles/LiveLinkTransformRole.h"
#include "Roles/LiveLinkTransformTypes.h"

void FMyLiveLinkSource::ReceiveClient(ILiveLinkClient* InClient, FGuid InSourceGuid)
{
    Client = InClient;
    SourceGuid = InSourceGuid;
    // 定义我们提供数据的“主体”
    SubjectKey = FLiveLinkSubjectKey(SourceGuid, FName("MyBox"));
    // 告诉客户端我们将提供 Transform 角色的静态数据
    FLiveLinkStaticDataStruct StaticDataStruct(FLiveLinkTransformStaticData::StaticStruct());
    Client->PushSubjectStaticData_AnyThread(SubjectKey, ULiveLinkTransformRole::StaticClass(), StaticDataStruct);
}

void FMyLiveLinkSource::Update()
{
    if (!Client) return;

    TimeElapsed += 0.016f; // 假设约60fps更新

    // 构造并推送帧数据
    FLiveLinkFrameDataStruct FrameDataStruct(FLiveLinkTransformFrameData::StaticStruct());
    FLiveLinkTransformFrameData& FrameData = *FrameDataStruct.Cast<FLiveLinkTransformFrameData>();
    // 创建一个绕Z轴旋转的变换
    FrameData.Transform = FTransform(FRotator(0.f, TimeElapsed * 180.f, 0.f), FVector(100.f, 0.f, 0.f));
    Client->PushSubjectFrameData_AnyThread(SubjectKey, FrameDataStruct);
}

FText FMyLiveLinkSource::GetSourceType() const { return FText::FromString(TEXT("My Custom Source")); }
FText FMyLiveLinkSource::GetSourceStatus() const { return FText::FromString(TEXT("Running")); }
```
*(此示例综合了典型源创建逻辑)*

## 模块依赖

要使用 Live Link 插件，你的模块通常只需要依赖其核心运行时模块。

| 模块 | 用途 |
|---|---|
| `LiveLink` | 核心运行时框架，提供客户端、源接口、数据类型等基础功能。这是必须的依赖。 |
| `LiveLinkComponents` | 提供用于在 Actor 和 Component 中轻松集成 Live Link 数据的实用组件（如 `ULiveLinkComponentController`）。 |
| `LiveLinkSequencer` | 提供与 Sequencer 的深度集成，用于录制、回放和编辑 Live Link 数据。 |

*说明：`LiveLinkEditor`、`LiveLinkGraphNode`、`LiveLinkMovieScene`、`LiveLinkMultiUser` 等模块主要服务于编辑器功能、蓝图节点扩展、Sequencer 内部逻辑和多用户编辑，对于仅消费数据的运行时项目非必需。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cd46766d` | Fix crash in ULiveLinkBroadcastComponent::PostEditChangeProperty when the broadcast subsystem is una | 修复广播组件在广播子系统未初始化时进行属性编辑导致的崩溃 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量转换为浮点数时产生的编译器警告 |
| 2026-05-13 | `057dbc69` | Fix crashes in PostEditChangeProperty overrides when MemberProperty is null, which occurs when Pytho | 修复当 MemberProperty 为空时（如从 Python 脚本触发）PostEditChangeProperty 重载函数崩溃的问题 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制片：将多种虚拟制片资产归类到不同资产类别，并迁移至新位置，可能涉及路径变更 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了在格式化函数中使用作用域枚举可能导致输出乱码的问题 |

### 维护评价

**活跃维护**。Live Link 是虚幻引擎虚拟制片和高级动画工作流的核心组件。从 git 历史看，它持续接受维护和 Bug 修复，最近的更新（2026年）集中在提高稳定性、修复崩溃和改进代码质量。尽管插件本身创建于2018年，但其架构可扩展且功能关键，Epic 仍在积极维护。对于需要实时数据集成的项目，**强烈推荐使用**。唯一需注意的是，由于默认未启用 (`EnabledByDefault: false`)，需要在项目设置中手动开启。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/live-link-in-unreal-engine/) (通用文档链接，非 .uplugin 指定)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink/Source/LiveLink) (测试文件通常位于模块源码的Tests子目录中)