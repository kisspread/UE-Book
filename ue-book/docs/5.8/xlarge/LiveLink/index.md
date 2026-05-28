# Live Link

> LiveLink allows streaming of animated data into Unreal Engine（照抄，不翻译）

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

## 用途

Live Link 插件的核心功能是建立一条从外部应用程序（如 Maya、MotionBuilder）或硬件设备（如动作捕捉系统）到 Unreal Engine 的实时数据通道。它不仅仅是一个简单的数据导入工具，而是一个完整的客户端-服务器框架，用于在运行时或编辑器中“流式传输”动画数据（如骨骼变换、曲线值、相机参数等）。

它解决了传统工作流中需要先将动画数据导出为文件再导入 UE 的延迟和繁琐问题，实现了外部数据与引擎内场景的实时同步。这在影视虚拟制片、实时动画预览和复杂的动作捕捉工作流中至关重要。

## 使用场景

- **影视虚拟制片**：将现场表演（通过动作捕捉）或在 Maya 等 DCC 软件中实时调整的动画，驱动 UE 中的虚拟角色或摄像机。
- **动作捕捉驱动**：将来自 Xsens、Rokoko、OptiTrack 等动捕系统的骨骼数据实时映射到 UE 的 MetaHuman 或自定义骨架上。
- **实时动画预览**：在 Maya 中调整关键帧，UE 中的预览窗口能立即看到最终效果，无需反复导出。
- **多用户协作**：在大型虚拟制片项目中，多个工作站（如灯光、动画）可以通过 Live Link 共享和同步来自同一个“中心”（如 LiveLinkHub）的实时数据。

## 蓝图用法

Live Link 在蓝图中主要通过**数据源管理**和**主题数据访问**两大类节点进行操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Source` | 向 Live Link 系统添加一个新的数据源（如特定的网络地址或插件源）。 | `ULiveLinkSubsystem` |
| `Get Subject Data` | 通过主题名称（Subject Name）获取该主题的最新实时数据。 | `ULiveLinkSubsystem` |
| `Get Live Link Role` | 获取当前主题数据所遵循的角色类型（如动画、变换、相机）。 | `ULiveLinkRole` |
| `Evaluate Live Link Frame` | 对获取到的实时帧数据进行求值，以应用到目标组件或属性上。 | `ULiveLinkBlueprintVirtualSubject` |
| `Live Link Component` | 一个场景组件，可附加到 Actor 上，并自动驱动该 Actor 的变换或动画。 | `ULiveLinkComponent` |
| `Live Link Controller` | 用于在 Sequencer 中控制和录制 Live Link 数据。 | `ULiveLinkController` |

### 使用示例（蓝图描述）

**示例：在蓝图中设置一个由 Maya Live Link 实时驱动的角色**
1.  在角色蓝图中，添加一个 `Live Link Component`。
2.  在该组件的细节面板中，设置 `Subject Representation`，选择 Maya Live Link 插件在 UE 中注册的“主题名”（如 `MayaSubject`）。
3.  设置 `Role` 为 `Anim`（动画角色）。
4.  设置 `Skeletal Mesh` 引用你想要驱动的骨架网格体。
5.  确保 Maya 端 Live Link 插件已启动并连接到 UE（通过 `Add Source` 节点或 Live Link 面板手动添加）。
6.  播放 Maya 动画，蓝图中的角色将实时跟随。

**示例：在运行时动态添加数据源**
1.  在蓝图的 `BeginPlay` 事件中，获取 `LiveLink Subsystem` 对象。
2.  调用 `Add Source` 节点，选择源类型（如 `Message Bus Source`），并填入提供数据的主机 IP 地址。
3.  使用 `Get Subject Data` 节点，传入主题名来获取数据，并后续进行处理。

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkClient.h"
#include "LiveLinkTypes.h"
#include "Roles/LiveLinkAnimationRole.h"
```

### 基本用法

**来源文件：** `Engine/Plugins/Animation/LiveLink/Source/LiveLink/Private/LiveLinkClient.cpp` 及测试用例。

```cpp
// 获取全局的 Live Link 客户端实例
FLiveLinkClient& LiveLinkClient = ILiveLinkModule::Get().GetClient();

// 获取一个特定主题（Subject）的最新快照数据
const FName SubjectName = TEXT("MyCharacter");
FLiveLinkSubjectFrameData SubjectData;
bool bSuccess = LiveLinkClient.GetSubjectData(SubjectName, SubjectData);

if (bSuccess)
{
    // 检查数据是否为动画角色类型
    if (SubjectData.StaticData->Role->IsChildOf(ULiveLinkAnimationRole::StaticClass()))
    {
        // 获取动画数据
        const FSubjectFrameHandle& FrameData = SubjectData.FrameData;
        const FLiveLinkSkeletonStaticData* SkeletonData = SubjectData.StaticData->Cast<FLiveLinkSkeletonStaticData>();
        
        // 访问骨骼变换数据
        if (SkeletonData && FrameData.IsValid())
        {
            TArray<FTransform> BoneTransforms;
            FrameData.EvaluateBaseBones(BoneTransforms);
            // 将 BoneTransforms 应用到你的骨骼网格体组件上...
        }
    }
}
```

### 进阶用法

**来源文件：** 多个测试用例及 `LiveLinkAnimationVirtualSubject` 相关代码。

1.  **注册自定义数据处理器（Role）**：创建继承自 `ULiveLinkRole` 的类，以支持自定义的数据格式。
2.  **创建蓝图虚拟主题**：通过继承 `ULiveLinkBlueprintVirtualSubject`，在蓝图中组合多个源的数据或对数据进行转换。
3.  **与 Sequencer 深度集成**：使用 `ULiveLinkController` 在 Sequencer 轨道中录制和播放 Live Link 数据，实现后期编辑。
4.  **使用预处理器**：实现 `ILiveLinkClientPreProcessor` 接口，在数据到达应用（如动画蓝图）之前对其进行过滤或修改。

## Demo 示例

一个最小的 C++ 示例，演示如何监听并处理来自 Live Link 的骨骼动画数据。

**MyLiveLinkListener.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "LiveLinkClient.h"
#include "Roles/LiveLinkAnimationRole.h"

class FMyLiveLinkListener
{
public:
    FMyLiveLinkListener();
    ~FMyLiveLinkListener();

    void OnSubjectFrameUpdated(const FName& SubjectName, const FLiveLinkSubjectFrameData& FrameData);

private:
    FLiveLinkClient* LiveLinkClient = nullptr;
    FDelegateHandle FrameUpdateDelegateHandle;
};
```

**MyLiveLinkListener.cpp**
```cpp
#include "MyLiveLinkListener.h"
#include "ILiveLinkModule.h"

FMyLiveLinkListener::FMyLiveLinkListener()
{
    LiveLinkClient = &ILiveLinkModule::Get().GetClient();
    if (LiveLinkClient)
    {
        // 注册一个委托，在任何主题数据更新时调用
        FrameUpdateDelegateHandle = LiveLinkClient->OnLiveLinkSubjectFrameUpdated().AddRaw(this, &FMyLiveLinkListener::OnSubjectFrameUpdated);
    }
}

FMyLiveLinkListener::~FMyLiveLinkListener()
{
    if (LiveLinkClient && FrameUpdateDelegateHandle.IsValid())
    {
        LiveLinkClient->OnLiveLinkSubjectFrameUpdated().Remove(FrameUpdateDelegateHandle);
    }
}

void FMyLiveLinkListener::OnSubjectFrameUpdated(const FName& SubjectName, const FLiveLinkSubjectFrameData& FrameData)
{
    // 仅处理名为 “MyCharacter” 的动画主题
    if (SubjectName == TEXT("MyCharacter") && FrameData.StaticData.IsValid())
    {
        if (FrameData.StaticData->Role == ULiveLinkAnimationRole::StaticClass())
        {
            // 在此处理最新的骨骼动画帧数据
            UE_LOG(LogTemp, Log, TEXT("Received animation frame for subject: %s"), *SubjectName.ToString());
        }
    }
}
```

## 模块依赖

该插件的各个模块共同构建了一个复杂的数据流框架。要使用其核心功能，你的模块通常需要依赖以下独特模块：

| 模块 | 用途 |
|---|---|
| `LiveLink` | 核心客户端和数据管理框架，所有功能的基础。 |
| `LiveLinkComponents` | 提供易于使用的蓝图和C++组件（如 `ULiveLinkComponent`）。 |
| `LiveLinkMovieScene` | 实现 Live Link 与 Sequencer（关卡序列）的深度集成，用于录制和回放。 |
| `AnimationCore` | 提供底层的动画数学和变换工具，被 Live Link 数据处理广泛使用。 |
| `ControlRig` | 支持将 Live Link 数据直接输入到 Control Rig 系统中，用于复杂的程序化动画。 |
| `LevelSequence` | Sequencer 的核心模块，与 `LiveLinkMovieScene` 协同工作。 |

**注意**：`LiveLinkEditor`, `LiveLinkGraphNode`, `LiveLinkMultiUser`, `LiveLinkSequencer` 模块主要面向编辑器工具、视觉脚本节点、多人协作等高级或特定场景，普通运行时使用通常不直接依赖它们。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cd46766d` | Fix crash in ULiveLinkBroadcastComponent::PostEditChangeProperty when the broadcast subsystem is una | 修复当广播子系统未初始化时，编辑广播组件属性可能引发的崩溃。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量转换为浮点数产生的编译器警告。 |
| 2026-05-13 | `057dbc69` | Fix crashes in PostEditChangeProperty overrides when MemberProperty is null, which occurs when Pytho | 修复当 Python 修改属性时 MemberProperty 为 null 导致的编辑器属性更改后崩溃。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制片资产分类和迁移，涉及 Live Link 相关资产。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复在格式化函数中使用的枚举类型可能导致输出错误的问题。 |

### 维护评价

Live Link 是 Unreal Engine 动画和虚拟制片工作流的**核心支柱之一**。自 2018 年创建以来，它已经从一个实验性功能发展成为一套完整、成熟的实时数据流解决方案。

- **活跃维护**：从近期的 Git 记录（2026 年 5 月）可以看出，Epic Games 的开发团队仍在**非常活跃地维护**此插件，持续修复崩溃、警告和底层问题。
- **关键基础设施**：它深度集成于引擎的动画蓝图、Sequencer 和虚拟制片管线中，其稳定性对相关工作流至关重要。
- **推荐使用**：如果你的工作流涉及任何外部实时数据（动作捕捉、DCC 软件联动）或多人虚拟制片，**强烈推荐使用** Live Link。尽管它默认未启用（需要手动在插件管理器中打开），但其功能和成熟度无可替代。
- **无已知的重大废弃警告**：尽管历史悠久，但它仍在不断进化，是引擎中少数真正意义上的“文物级”但依旧核心且活跃的功能之一。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/animation-tools-in-unreal-engine/) (Live Link 是动画工具集的一部分)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink/Tests)