# Live Link

> LiveLink allows streaming of animated data into Unreal Engine（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 实时链接 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质、接口） |
| 模块 | `LiveLink` (Runtime), `LiveLinkComponents` (Runtime), `LiveLinkEditor` (Runtime), `LiveLinkGraphNode` (Runtime), `LiveLinkMovieScene` (Runtime), `LiveLinkMultiUser` (Runtime), `LiveLinkSequencer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-02-27 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink) | |

## 用途

LiveLink 是一个标准化、可扩展的实时数据流框架。其核心目标是解决**外部数据源**（如动作捕捉设备、虚拟摄像机、自定义传感器）与**虚幻引擎内部场景对象**（如骨骼网格体、摄像机、灯光）之间的实时同步问题。

它不仅仅是一个数据传输协议，更是一个完整的**数据管道（Pipeline）**：
1.  **Subject（主题）**：代表一个外部数据源（如一个人的动捕数据）。每个 Subject 都有特定的 **Role（角色）**，定义了它包含的数据类型（如 `LiveLinkTransformRole` 代表变换数据，`LiveLinkAnimationRole` 代表动画数据）。
2.  **Controller（控制器）**：位于引擎端，负责接收特定 Role 的 Subject 数据，并将其应用到场景中的组件（如 `LiveLinkTransformController` 将变换数据应用到 `SceneComponent`）。
3.  **LiveLinkComponentController**：一个挂载在 Actor 上的组件，作为 Subject 和 Controller 之间的桥梁。它允许用户选择要监听的 Subject，并管理一组控制器（`ControllerMap`），根据 Subject 的 Role 自动或手动地应用数据。

这个插件存在是为了**标准化外部设备接入流程**。开发者无需为每种设备编写特定的集成代码，只需实现一个符合 LiveLink 标准的源（Source），即可将数据以统一的格式传输到引擎，并利用引擎提供的丰富的内置控制器或自定义控制器来驱动场景。

## 使用场景

-   **虚拟制片/摄像机追踪**：使用像 Ncam、Stype 这样的摄像机追踪系统，通过 LiveLink 实时驱动 UE 中的虚拟摄像机。
-   **动作捕捉**：使用 Vicon、OptiTrack、Xsens 等动捕设备，将骨骼动画数据实时驱动 UE 中的 Metahuman 或游戏主角。
-   **面部捕捉**：使用 ARKit、iPhone 或专业面捕设备（如 Dynamixyz），实时驱动虚拟角色的面部表情。
-   **自定义硬件集成**：你有一个物理控制器、传感器阵列或自研的追踪设备，可以通过编写一个 LiveLink Source 来快速将其实时数据接入引擎。
-   **多用户协作**：在虚拟制片场景中，多个设备（摄像机、灯光控制台）的数据需要同步，LiveLink 可以作为中心数据总线。

## 蓝图用法

### 核心节点

`LiveLinkComponentController` 是蓝图中操作 LiveLink 的主要组件。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ConnectSubject` | 连接到指定的 LiveLink 主题（Subject），开始接收数据。 | `ULiveLinkComponentController` |
| `GetSubjectData` | 获取当前主题的最新一帧评估后的数据。 | `ULiveLinkComponentController` |
| `GetSubjectRepresentation` | 获取当前主题的表示信息（包含主题名和角色）。 | `ULiveLinkComponentController` |
| `SetSubjectRepresentation` | 设置要监听的主题表示信息。 | `ULiveLinkComponentController` |
| `GetControlledComponent` | 获取指定角色（Role）的控制器正在控制的组件。 | `ULiveLinkComponentController` |
| `SetControlledComponent` | 为指定角色（Role）的控制器设置要控制的目标组件。 | `ULiveLinkComponentController` |

### 使用示例（蓝图描述）

**场景：** 将一个外部动捕角色的变换数据应用到场景中的一个 `Static Mesh Actor`。

1.  在目标 `Static Mesh Actor` 上，添加一个 `Live Link Component Controller` 组件。
2.  在该组件的 `Details` 面板中，找到 `Subject Representation` 属性，从下拉列表中选择你的动捕设备发布出来的 Subject（例如 “Mannequin”）。
3.  在 `Controller Map` 中，通常会自动出现一个 `LiveLinkTransformController`。确保它被启用。
4.  运行游戏或在编辑器中启用 `Update In Editor`。如果 LiveLink 源正在发送数据，该 Static Mesh Actor 的变换就会实时被驱动。
5.  （可选）你可以通过蓝图节点 `SetSubjectRepresentation` 在运行时动态切换监听的 Subject。
6.  （可选）如果 `Controller Map` 中没有自动生成控制器，你可以调用 `SetControllerClassForRole` 手动为指定的 Role 创建并设置一个控制器类（例如 `LiveLinkTransformController`）。

## C++ 用法

### 头文件引入

使用 `LiveLinkComponents` 模块中的控制器和组件。
```cpp
#include "LiveLinkComponentController.h"
#include "Controllers/LiveLinkTransformController.h"
```

### 基本用法

以下示例展示了如何在 C++ 中创建一个 `LiveLinkComponentController` 并配置它。
（来源：引擎使用模式，类似于 `ULiveLinkComponentController::PostLoad`）

```cpp
// 在你的 Actor 类中
UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "LiveLink")
ULiveLinkComponentController* MyLiveLinkController;

// 在构造函数或 BeginPlay 中创建
MyLiveLinkController = CreateDefaultSubobject<ULiveLinkComponentController>(TEXT("LiveLinkController"));
// 设置要监听的主题和角色
MyLiveLinkController->SubjectRepresentation = FLiveLinkSubjectRepresentation(
    FName("MyMotionCaptureSubject"),
    ULiveLinkAnimationRole::StaticClass()
);
```

### 进阶用法

从控制器地图中获取特定角色的控制器，并对其进行自定义配置。
（来源：`ULiveLinkComponentController` 内部逻辑）

```cpp
// 假设 MyLiveLinkController 已经初始化并连接
TSubclassOf<ULiveLinkRole> TransformRole = ULiveLinkTransformRole::StaticClass();

// 检查控制器地图中是否存在 TransformRole 的控制器
if (MyLiveLinkController->ControllerMap.Contains(TransformRole))
{
    ULiveLinkControllerBase* BaseController = MyLiveLinkController->ControllerMap[TransformRole];
    // 尝试转换为具体的 TransformController
    ULiveLinkTransformController* TransformController = Cast<ULiveLinkTransformController>(BaseController);
    if (TransformController)
    {
        // 配置控制器，例如，只应用旋转，不应用位移和缩放
        TransformController->TransformData.bUseLocation = false;
        TransformController->TransformData.bUseScale = false;
        TransformController->TransformData.bUseRotation = true;
    }
}

// 或者，如果控制器不存在，为该角色创建一个新的控制器
if (!MyLiveLinkController->ControllerMap.Contains(TransformRole))
{
    MyLiveLinkController->SetControllerClassForRole(TransformRole, ULiveLinkTransformController::StaticClass());
    // 新创建的控制器会在下一个 Tick 开始工作
}
```

## Demo 示例

一个最小的自定义 LiveLink 控制器，用于接收 `Transform` 数据并以对数曲线衰减其旋转。

**MyLogarithmicRotatorController.h**
```cpp
// 版权所有 Epic Games, Inc. 保留所有权利。
#pragma once

#include "CoreMinimal.h"
#include "Controllers/LiveLinkTransformController.h"
#include "MyLogarithmicRotatorController.generated.h"

UCLASS(MinimalAPI, BlueprintType)
class UMyLogarithmicRotatorController : public ULiveLinkTransformController
{
    GENERATED_BODY()

public:
    // 重写 Tick 函数以应用自定义逻辑
    virtual void Tick(float DeltaTime, const FLiveLinkSubjectFrameData& SubjectData) override;

private:
    // 用于衰减的旋转值
    FRotator CurrentDecayedRotation;
};
```

**MyLogarithmicRotatorController.cpp**
```cpp
// 版权所有 Epic Games, Inc. 保留所有权利。
#include "MyLogarithmicRotatorController.h"

void UMyLogarithmicRotatorController::Tick(float DeltaTime, const FLiveLinkSubjectFrameData& SubjectData)
{
    // 首先调用父类的 Tick 来获取并存储最新的 CombinedTransform（包含偏移）。
    // 注意：父类 Tick 会将数据应用到组件。我们希望在应用前修改数据。
    Super::Tick(DeltaTime, SubjectData);

    // 从 SubjectData 中提取变换数据
    const FLiveLinkTransformFrameData* FrameData = SubjectData.FrameData.Cast<FLiveLinkTransformFrameData>();
    if (!FrameData)
    {
        return;
    }

    // 获取目标旋转（来自 LiveLink 的世界/本地旋转，取决于 TransformData.bWorldTransform）
    FRotator TargetRotation = CombinedTransform.GetRotation().Rotator();

    // 应用对数衰减（模拟一个阻尼效果）
    const float DecayRate = 5.0f; // 衰减速率
    CurrentDecayedRotation = FMath::RInterpTo(CurrentDecayedRotation, TargetRotation, DeltaTime, DecayRate);

    // 重新构建应用了衰减旋转的 Transform
    FTransform DecayedTransform = CombinedTransform;
    DecayedTransform.SetRotation(CurrentDecayedRotation.Quaternion());

    // 将修改后的 Transform 应用到附加的组件
    if (USceneComponent* SceneComponent = Cast<USceneComponent>(GetAttachedComponent()))
    {
        TransformData.ApplyTransform(SceneComponent, DecayedTransform, SubjectData.StaticData.Cast<FLiveLinkTransformStaticData>());
    }
}
```

## 模块依赖

从 `LiveLinkComponents.Build.cs` 分析，该模块依赖于：

| 模块 | 用途 |
|---|---|
| `LiveLink` | 核心的 LiveLink 框架，提供 Subject、Role 等基础定义。 |
| `MessageBus` | 用于 LiveLink 数据传输的底层消息总线机制。 |

（无其他特殊依赖，仅依赖标准 Core、Engine、Slate 等核心模块。）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cd46766d` | Fix crash in ULiveLinkBroadcastComponent::PostEditChangeProperty when the broadcast subsystem is una | 修复广播子系统不可用时 `ULiveLinkBroadcastComponent` 属性变更后的崩溃问题。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 `double` 常量截断为 `float` 导致的编译警告。 |
| 2026-05-13 | `057dbc69` | Fix crashes in PostEditChangeProperty overrides when MemberProperty is null, which occurs when Pytho | 修复 Python 脚本触发属性变更时，因 `MemberProperty` 为空导致的崩溃。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复用于格式化函数的 scoped enums，防止输出垃圾字符。 |

### 维护评价

LiveLink 插件**正在被积极维护**。它从 2018 年随 UE4.19 发布，从“实验性”状态毕业成为正式功能。作为虚幻引擎在虚拟制片、动画捕捉和实时数据集成领域的核心组件，它持续获得 Epic 的支持。

-   **创建时间**：约 7 年。
-   **更新频率**：非常活跃，近期（2026年5月）有多次修复提交。
-   **维护内容**：近期更新集中在修复崩溃、编译警告和提升稳定性，表明该插件已进入成熟期，主要进行维护性开发。
-   **状态**：稳定且被广泛使用。`EnabledByDefault` 为 `false` 可能是因为它是一个功能丰富的专业工具，通常在需要时由用户手动启用。
-   **推荐使用**：**强烈推荐**用于任何涉及实时外部数据驱动 UE 场景的项目，无论是虚拟制片、游戏开发还是仿真应用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink)
-   [官方文档](https://docs.unrealengine.com/5.8/en-US/live-link-in-unreal-engine/) （通过搜索可达，`.uplugin` 中未直接提供）
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink/Source/LiveLinkTests) （LiveLink 测试模块位于插件内）