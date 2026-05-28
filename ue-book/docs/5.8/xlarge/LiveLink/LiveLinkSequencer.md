# Live Link

> LiveLink allows streaming of animated data into Unreal Engine（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 实时链接 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画资产、蓝图资产） |
| 模块 | `LiveLink` (Runtime), `LiveLinkComponents` (Runtime), `LiveLinkEditor` (Runtime), `LiveLinkGraphNode` (Runtime), `LiveLinkMovieScene` (Runtime), `LiveLinkMultiUser` (Runtime), `LiveLinkSequencer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-02-27 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink) | |

## 用途

Live Link 是一个用于实时数据流传输的框架系统。它解决了将外部设备（如动作捕捉设备、面部捕捉系统、外部动画软件如 Maya、MotionBuilder）或其他数据源产生的动画数据、变换数据、音频数据等实时传输到虚幻引擎中进行驱动的问题。其核心目标是为虚幻引擎提供一种标准化、可扩展的数据传输协议，使得不同来源、不同类型的数据能够被统一接收、处理和应用到场景中的角色、物体或相机上。它避免了为每个数据源编写特定的导入代码，极大地简化了实时数据集成的工作流。

## 使用场景

- 你正在使用 OptiTrack、Vicon、Xsens 等动作捕捉系统进行表演捕捉，希望将捕捉到的实时骨骼动画数据驱动 UE 中的角色。
- 你在 Maya 或 MotionBuilder 中进行动画编辑，希望将修改后的动画数据实时预览在 UE 的场景中。
- 你需要驱动 UE 中的灯光、摄像机或其他 Actor 的变换属性，数据来源是一个外部控制系统。
- 你正在开发一个虚拟制片（Virtual Production）项目，需要将 LED 墙上的追踪数据（如相机位置）实时同步到 UE 中的虚拟场景。
- 你希望将录制好的 Live Link 数据保存为动画序列，用于后期编辑或回放。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Live Link Subject` | 创建一个新的 Live Link 主体 | `ULiveLinkBlueprintLibrary` |
| `Set Live Link Subject Enabled` | 设置指定主体的启用状态 | `ULiveLinkBlueprintLibrary` |
| `Get Live Link Subject Role` | 获取指定主体的角色类型（如动画、变换等） | `ULiveLinkBlueprintLibrary` |
| `Get Live Link Subject Frame Data` | 获取指定主体在当前帧的数据（如骨骼变换） | `ULiveLinkBlueprintLibrary` |
| `Add Live Link Source` | 通过蓝图添加一个新的 Live Link 源 | `ULiveLinkBlueprintLibrary` |

### 使用示例（蓝图描述）

要在蓝图中实时应用 Live Link 数据到骨骼网格体组件：
1. 使用 `Create Live Link Subject` 节点，并传入外部设备提供的主体名称（如 “Maya_Char”）。
2. 将 `Get Live Link Subject Frame Data` 节点连接到事件 Tick 或使用定时器定期调用，获取最新的帧数据。
3. 从返回的 `FLiveLinkFrameData` 结构中提取骨骼变换数据（`Transforms` 数组）。
4. 将这些变换数据应用到你的 Skeletal Mesh Component 的 `Set Bone Transform By Name` 节点，以驱动骨骼动画。

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkComponentController.h"
#include "ILiveLinkClient.h"
```

### 基本用法

从 Live Link Client 获取指定主体的最新帧数据并应用。
*（来源：LiveLink 模块的典型使用模式）*

```cpp
// 假设已经获得了一个 Live Link Client 的引用
ILiveLinkClient* LiveLinkClient = /* ... */;

// 主体的唯一标识符
FLiveLinkSubjectKey SubjectKey = /* ... */;

// 获取主体的最新帧数据
FLiveLinkFrameDataStruct FrameData;
if (LiveLinkClient->EvaluateFrame_AnyThread(SubjectKey, ULiveLinkAnimationRole::StaticClass(), FrameData))
{
    // 如果是动画角色，可以获取骨骼变换
    if (const FLiveLinkAnimationFrameData* AnimationFrameData = FrameData.Cast<FLiveLinkAnimationFrameData>())
    {
        // 使用 AnimationFrameData->Transforms 来驱动骨骼
        // ...
    }
}
```

### 进阶用法

使用 Live Link Controller 组件自动驱动场景中的 Actor。
*（来源：LiveLinkComponents 模块）*

```cpp
// 在你的 Actor 类中声明一个 Live Link Controller 组件
UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
ULiveLinkTransformController* TransformController;

// 在构造函数中创建并初始化
AMyActor::AMyActor()
{
    // 创建组件
    TransformController = CreateDefaultSubobject<ULiveLinkTransformController>(TEXT("LiveLinkTransformController"));
    // 设置要驱动的组件（例如根组件）
    TransformController->SetAttachedComponent(GetRootComponent());
    // 设置 Live Link 主体名称
    TransformController->SubjectRepresentation = FLiveLinkSubjectRepresentation(/* Subject Name */, ULiveLinkTransformRole::StaticClass());
    // 启用组件
    TransformController->bUpdateInEditor = true;
    TransformController->bUpdateInGame = true;
}
```

## Demo 示例

一个最小示例，展示如何通过 C++ 创建一个由 Live Link 数据驱动的 Actor。

### MyLiveLinkDrivenActor.h
```cpp
// MyLiveLinkDrivenActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LiveLinkComponentController.h"
#include "MyLiveLinkDrivenActor.generated.h"

UCLASS()
class AMyLiveLinkDrivenActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMyLiveLinkDrivenActor();

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    USceneComponent* SceneRoot;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    UStaticMeshComponent* VisibleMesh;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    ULiveLinkTransformController* LiveLinkController;
};
```

### MyLiveLinkDrivenActor.cpp
```cpp
// MyLiveLinkDrivenActor.cpp
#include "MyLiveLinkDrivenActor.h"
#include "LiveLinkControllerBase.h"

AMyLiveLinkDrivenActor::AMyLiveLinkDrivenActor()
{
    SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("SceneRoot"));
    RootComponent = SceneRoot;

    VisibleMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("VisibleMesh"));
    VisibleMesh->SetupAttachment(SceneRoot);

    LiveLinkController = CreateDefaultSubobject<ULiveLinkTransformController>(TEXT("LiveLinkController"));
    // 将控制器与根组件关联，以便 Live Link 数据驱动此 Actor 的整个变换
    LiveLinkController->SetAttachedComponent(SceneRoot);
    // 设置默认主体名称（可在编辑器中修改）
    LiveLinkController->SubjectRepresentation = FLiveLinkSubjectRepresentation(FName("DefaultSubject"), ULiveLinkTransformRole::StaticClass());
    LiveLinkController->bUpdateInEditor = true;
    LiveLinkController->bUpdateInGame = true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLink` | Live Link 核心运行时，提供主体、源、客户端等核心框架 |
| `LiveLinkComponents` | 提供可拖拽的组件（如 LiveLinkTransformController），用于驱动场景中的 Actor |
| `LiveLinkEditor` | 编辑器扩展，提供 Live Link 面板、源管理等 UI |
| `LiveLinkGraphNode` | 蓝图节点扩展，提供用于在蓝图中操作 Live Link 数据的自定义节点 |
| `LiveLinkMovieScene` | 与 Sequencer 集成，用于在 Sequencer 中录制和编辑 Live Link 数据 |
| `LiveLinkMultiUser` | 多用户编辑支持，确保 Live Link 数据在多个编辑器实例间同步 |
| `LiveLinkSequencer` | 与 Take Recorder (Sequencer) 集成，专门用于将 Live Link 数据录制为动画序列 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cd46766d` | Fix crash in ULiveLinkBroadcastComponent::PostEditChangeProperty when the broadcast subsystem is una | 修复广播子系统未初始化时广播组件编辑属性导致的崩溃 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的警告 |
| 2026-05-13 | `057dbc69` | Fix crashes in PostEditChangeProperty overrides when MemberProperty is null, which occurs when Python scripts modify properties. | 修复当 Python 脚本修改属性导致 MemberProperty 为 null 时，PostEditChangeProperty 覆写中的崩溃 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the ... | 虚拟制片：将多个 VP 资产移至不同资产分类，并迁移到新的模块结构 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了在格式化函数中使用的作用域枚举可能导致输出乱码的问题 |

### 维护评价

Live Link 插件是一个成熟且核心的功能模块。自 2018 年创建以来，它已经成为虚幻引擎在虚拟制片、动画和实时技术领域的关键组件。

**优点**：
- **活跃维护**：从最近的提交记录看，Epic 团队仍在持续修复 bug 和进行优化（最近提交在 2026 年 5 月），表明它仍在被积极维护和改进。
- **核心功能**：作为连接外部数据与引擎的桥梁，其重要性在虚拟制片等工作流中日益凸显。
- **架构清晰**：模块化设计（核心、组件、编辑器、Sequencer 集成等），便于扩展和维护。

**注意事项**：
- **默认未启用**：在默认项目模板中是禁用的，需要手动在插件管理器中启用。
- **学习曲线**：涉及外部设备、网络通信和动画数据概念，对初学者有一定门槛。
- **依赖性**：实际使用效果高度依赖外部设备的兼容性和驱动。

**总体推荐**：**强烈推荐**。对于任何需要实时数据集成的项目，尤其是虚拟制片、动作捕捉或复杂的实时动画工作流，Live Link 是必不可少且高度可靠的选择。尽管有一些学习成本，但其稳定性和持续的维护支持使其成为生产环境中的首选方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/using-live-link-in-unreal-engine/) (根据公开知识补充)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink/Source/LiveLink/Private/Tests) (推测路径)