# Live Link

> LiveLink allows streaming of animated data into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | 实时链接 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `LiveLink` (Runtime), `LiveLinkComponents` (Runtime), `LiveLinkEditor` (Runtime), `LiveLinkGraphNode` (Runtime), `LiveLinkMovieScene` (Runtime), `LiveLinkMultiUser` (Runtime), `LiveLinkSequencer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-02-27 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink) | |

## 用途

Live Link 是一个实时数据流传输框架，用于将外部设备和应用程序（如动捕系统、虚拟摄像机、3D建模软件等）产生的动画、姿态、变换、摄像机、光照等数据，实时、低延迟地引入到 Unreal Engine 中。它不仅仅是简单的数据管道，更是一个统一的框架，通过定义“角色（Role）”、“主体（Subject）”和“主题（Topic）”等概念，将各种来源、不同类型的数据标准化，使其能够被引擎中的各种组件和系统（如动画蓝图、Sequencer、组件控制器）直接消费。

**它解决的核心问题是：** 如何将异构的外部实时数据源，以统一、可扩展的方式集成到引擎中，并驱动场景中的对象。这使得用户可以方便地连接动捕工作室的实时数据、使用虚拟摄像机控制游戏内摄像机、或通过外部设备实时控制灯光和物体。

## 使用场景

- **实时动捕驱动角色动画**：将来自 Vicon、OptiTrack、Xsens 等动捕系统的骨骼数据，实时驱动引擎中角色的骨骼网格体。
- **虚拟制片 (Virtual Production)**：使用虚拟摄像机（如 iPhone 的 ARKit）或外部跟踪系统（如 Steadicam）实时控制 Sequencer 中的摄像机Actor。
- **第三方软件联动**：接收来自 Maya、Blender、MotionBuilder 等 3D 软件中物体的实时变换数据，用于同步场景或进行协同创作。
- **实时灯光与特效控制**：通过外部设备（如物理灯光控制台、iPad App）实时调整场景中光源的参数（如颜色、强度）或 Actor 的变换。
- **动画重定向与混合**：将动捕数据实时重定向到不同比例的虚拟角色上，并与程序化动画进行混合。

## 蓝图用法

Live Link 主要通过 `ULiveLinkComponentController` 组件在蓝图中使用。该组件充当“控制器”，将接收的 Live Link 数据应用到它所附加的 Actor 或其子组件上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SubjectRepresentation` | 属性（Getter/Setter）。指定要接收数据的 Live Link 主体（Subject）及其角色（Role）。 | `ULiveLinkComponentController` |
| `ControllerMap` | 属性。映射不同角色（Role）到具体的控制器类（如 TransformController， LightController）。 | `ULiveLinkComponentController` |
| `GetControlledComponent` | 函数。获取指定角色对应的控制器所驱动的组件。 | `ULiveLinkComponentController` |
| `SetControlledComponent` | 函数。设置指定角色对应的控制器要驱动的组件。 | `ULiveLinkComponentController` |
| `OnLiveLinkUpdated` | 事件。当有新的 Live Link 数据到达时触发。 | `ULiveLinkComponentController` |

### 使用示例（蓝图描述）

1. **设置 Live Link 主体**：
   - 在 Actor 的组件列表中添加 `LiveLink Controller` 组件。
   - 在组件的 `Details` 面板中，找到 `Subject Representation` 属性。点击下拉菜单，从已发现的 Live Link 主体列表中选择一个（例如，“MyMocapSystem: Subject1”）。

2. **配置控制器**：
   - 展开 `Controller Map` 属性。这是一个从 `Role` 到 `Controller` 的映射。
   - 默认情况下，已为常见的 `TransformRole` 配置了 `LiveLinkTransformController`。你可以为其他角色（如 `LightRole`）添加条目，并选择对应的控制器（如 `LiveLinkLightController`）。
   - 对于 `TransformController`，可以在其下方的详细设置中调整偏移（`OffsetTransform`）、是否使用世界空间变换（`bWorldTransform`）等。

3. **响应数据更新（可选）**：
   - 如果需要在收到新数据时执行自定义逻辑，可以绑定 `OnLiveLinkUpdated` 事件。
   - 例如，每当有新的变换数据时，打印一条日志或更新一个UI元素。

## C++ 用法

在 C++ 中，`LiveLinkComponents` 模块提供了对 Live Link 数据驱动组件的底层访问能力。

### 头文件引入

```cpp
#include "LiveLinkComponentController.h"
#include "LiveLinkTransformController.h"
#include "Roles/LiveLinkTransformRole.h"
```

### 基本用法

```cpp
// 假设你已经有一个 AActor* Actor， 并且 LiveLinkComponents 模块已加载。
// 来源：根据 Public/LiveLinkComponentController.h 和 Public/LiveLinkTransformController.h 推断。

// 1. 动态创建并配置 LiveLinkComponentController
ULiveLinkComponentController* LLController = NewObject<ULiveLinkComponentController>(Actor);
LLController->RegisterComponent();

// 2. 设置要监听的 Live Link 主体 (通过 FSubjectName 和 Role)
// 假设你知道一个主体的名称是 "MyCameraSubject"， 其角色是 CameraRole。
// FSubjectName 可以通过 FLiveLinkClient::GetSubjectNames 获取， 或在蓝图编辑器中查看。
FLiveLinkSubjectRepresentation CameraSubject(TEXT("MyCameraSubject"), ULiveLinkCameraRole::StaticClass());
LLController->SetSubjectRepresentation(CameraSubject);

// 3. 确保对应角色的控制器已配置
// 通常引擎会根据 DefaultControllerForRole 设置（在 ULiveLinkComponentSettings 中）自动创建默认控制器。
// 你也可以手动指定：
TSubclassOf<ULiveLinkControllerBase> CameraControllerClass = ULiveLinkCameraController::StaticClass(); // 假设存在这样的类
LLController->SetControllerClassForRole(ULiveLinkCameraRole::StaticClass(), CameraControllerClass);

// 4. （可选）处理每帧更新
// 如果需要自定义逻辑， 可以绑定到 OnLiveLinkUpdated 委托。
LLController->OnLiveLinkUpdated.AddDynamic(this, &UMyClass::HandleLiveLinkUpdate);
```

### 进阶用法

```cpp
// 进阶用法： 直接使用控制器数据而不依赖组件
// 来源： 结合 Public/LiveLinkControllerBase.h 和通用 LiveLink API。

// 1. 获取一个已存在的控制器实例
ULiveLinkTransformController* TransformCtrl = /* 从组件控制器或直接创建 */;

// 2. 在控制器的 Tick 中， 你已经收到了 FLiveLinkSubjectFrameData& SubjectData
// SubjectData 包含了这一帧所有的属性数据（Transform， Light， Camera 等）。
// 你可以在自定义的控制器子类中重写 Tick 函数来解析这些数据。
void UMyCustomController::Tick(float DeltaTime, const FLiveLinkSubjectFrameData& SubjectData)
{
    Super::Tick(DeltaTime, SubjectData);

    // 从 SubjectData.StaticData 和 SubjectData.FrameData 中提取特定数据
    if (const FLiveLinkTransformStaticData* TransformStaticData = SubjectData.StaticData.Cast<FLiveLinkTransformStaticData>())
    {
        const FLiveLinkTransformFrameData* TransformFrameData = SubjectData.FrameData.Cast<FLiveLinkTransformFrameData>();
        if (TransformStaticData && TransformFrameData)
        {
            FTransform ReceivedTransform = TransformFrameData->Transform;
            // ... 应用变换到你想要的目标
        }
    }
}
```

## Demo 示例

一个最小化的 C++ 示例，展示如何创建一个自定义的 Live Link 控制器。

### MyLiveLinkMovementController.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Controllers/LiveLinkTransformController.h"
#include "MyLiveLinkMovementController.generated.h"

UCLASS(MinimalAPI, BlueprintType)
class UMyLiveLinkMovementController : public ULiveLinkTransformController
{
    GENERATED_BODY()

public:
    // 只支持 Transform 角色
    virtual bool IsRoleSupported(const TSubclassOf<ULiveLinkRole>& RoleToSupport) override;

    // 重写 Tick， 添加自定义移动逻辑
    virtual void Tick(float DeltaTime, const FLiveLinkSubjectFrameData& SubjectData) override;

protected:
    UPROPERTY(EditAnywhere, Category="Movement")
    float MoveSpeedMultiplier = 1.0f;

private:
    FVector LastLocation;
    FVector CurrentVelocity;
};
```

### MyLiveLinkMovementController.cpp

```cpp
#include "MyLiveLinkMovementController.h"
#include "Roles/LiveLinkTransformRole.h"

bool UMyLiveLinkMovementController::IsRoleSupported(const TSubclassOf<ULiveLinkRole>& RoleToSupport)
{
    return RoleToSupport == ULiveLinkTransformRole::StaticClass();
}

void UMyLiveLinkMovementController::Tick(float DeltaTime, const FLiveLinkSubjectFrameData& SubjectData)
{
    // 先调用父类处理标准变换应用
    Super::Tick(DeltaTime, SubjectData);

    // 在此基础上添加自定义移动逻辑
    if (USceneComponent* SceneComp = Cast<USceneComponent>(GetAttachedComponent()))
    {
        FVector CurrentLocation = SceneComp->GetComponentLocation();
        if (!LastLocation.IsZero()) // 避免第一帧计算出巨大速度
        {
            CurrentVelocity = (CurrentLocation - LastLocation) / FMath::Max(DeltaTime, SMALL_NUMBER);
            CurrentVelocity *= MoveSpeedMultiplier;

            // 例如， 你可以将速度存储起来， 供其他系统使用
            // 你也可以在这里根据速度触发事件或播放动画
        }
        LastLocation = CurrentLocation;
    }
}
```

## 模块依赖

根据 `LiveLinkComponents.Build.cs` 和常见的 Live Link 用法， 使用此模块无需特殊依赖。其内部依赖于核心的 `LiveLink` 模块， 但当你在你的 `Build.cs` 中使用 `PublicDependencyModuleNames.Add("LiveLinkComponents");` 时， UBT 会自动处理这些传递依赖。

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cd46766d` | Fix crash in ULiveLinkBroadcastComponent::PostEditChangeProperty when the broadcast subsystem is una | 修复广播子系统未初始化时，编辑属性可能导致的崩溃问题。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量赋值给浮点数时产生的编译警告。 |
| 2026-05-13 | `057dbc69` | Fix crashes in PostEditChangeProperty overrides when MemberProperty is null, which occurs when Pytho | 修复了在编辑器属性变更时，成员属性为nullptr（例如通过 Python 脚本修改时）导致的崩溃。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the ... | 将虚拟制片相关资产整理到了不同的资产类别，并迁移到新的目录结构下。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了在格式化函数中使用的作用域枚举可能导致输出乱码的问题。 |

### 维护评价

- **活跃维护**：插件仍在积极更新。最近的提交（2026年5月）主要集中在修复编辑器交互相关的崩溃、警告以及代码质量改进，这表明它在持续优化以支持最新的引擎版本和编辑器工作流。
- **稳定性**：作为 Epic 官方支持的虚拟制片和实时动捕的关键基础设施，其稳定性和可靠性受到高度关注，近期的更新也印证了这一点。
- **推荐使用**：**强烈推荐**。对于任何需要实时外部数据驱动场景的项目（特别是虚拟制片、实时动捕、体感交互），Live Link 是官方且功能完善的解决方案。尽管需要手动启用（`EnabledByDefault=false`），但其文档和社区支持都很好。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/live-link-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Developer/LiveLink)