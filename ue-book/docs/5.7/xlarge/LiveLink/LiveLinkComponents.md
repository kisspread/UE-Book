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
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLink) | |

## 用途

Live Link 是 UE 的**实时动画数据流**框架，用于将外部设备或应用程序产生的动画数据（动作捕捉、面部追踪、摄像机跟踪、灯光控制等）实时传输到引擎中。

核心架构：
- **Subject（主题）**：一个数据流端点，代表一个被追踪的对象（如一个演员、一台摄像机）
- **Role（角色）**：定义数据类型（Transform、Camera、Light、Animation 等）
- **Controller（控制器）**：将接收到的数据应用到引擎中的组件上
- **Source（数据源）**：外部数据提供方（如 Vicon、OptiTrack、iPhone ARKit 等）

该插件默认不启用（`EnabledByDefault: false`），需要在项目设置中手动启用。它支持 `LiveLinkHub` 程序，这是一个独立的 Live Link 数据路由中心。

## 使用场景

- 你在做虚拟制片（Virtual Production），需要将 OptiTrack/Vicon 的动捕数据实时驱动场景中的角色 → 用 Live Link + Animation Role
- 你在做面部动画，需要将 iPhone ARKit 的面部追踪数据应用到 MetaHuman → 用 Live Link + Face AR Role
- 你需要将外部摄像机跟踪系统（如 Stype、Mo-Sys）的数据驱动 UE 中的 CineCamera → 用 Live Link + Camera Role
- 你需要将灯光控制台的 DMX 数据实时驱动场景中的灯光 → 用 Live Link + Light Role
- 你在做多用户协作编辑，需要在多个编辑器实例间同步 Live Link 数据 → 用 LiveLinkMultiUser 模块
- 你需要在 Sequencer 中录制 Live Link 数据用于后期编辑 → 用 LiveLinkSequencer 模块

## 子模块概览

本插件包含 7 个模块，按功能划分：

| 模块 | 类型 | 职责 |
|---|---|---|
| **LiveLink** | Runtime | 核心框架：Subject 管理、Role 定义、Source 接口、数据评估 |
| **LiveLinkComponents** | Runtime | Actor 组件：将 Live Link 数据驱动到场景中的组件（Transform、Light 等） |
| **LiveLinkEditor** | Runtime | 编辑器 UI：Live Link 面板、Subject 配置界面、自定义面板 |
| **LiveLinkGraphNode** | Runtime | 蓝图节点：AnimGraph 中的 Live Link 节点 |
| **LiveLinkMovieScene** | Runtime | Sequencer 集成：在 Sequencer 中录制和回放 Live Link 数据 |
| **LiveLinkMultiUser** | Runtime | 多用户协作：在多用户编辑会话中同步 Live Link 数据 |
| **LiveLinkSequencer** | Runtime | Sequencer 工具：Live Link 数据的批量录制和管理 |

## 蓝图用法

### 核心组件

#### ULiveLinkComponentController

这是最主要的蓝图组件，挂载到 Actor 上即可接收 Live Link 数据并驱动组件。

| 属性/节点 | 说明 | 类型 |
|---|---|---|
| `SubjectRepresentation` | 指定要接收数据的 Live Link Subject（主题名 + 角色） | 属性 (BlueprintReadWrite) |
| `ControllerMap` | 角色到控制器的映射，定义每种角色用哪个控制器处理 | 属性 (EditAnywhere) |
| `bEvaluateLiveLink` | 是否评估 Live Link 数据，设为 false 可暂停 | 属性 (BlueprintReadWrite) |
| `bUpdateInEditor` | 是否在编辑器中也更新 | 属性 |
| `bDisableEvaluateLiveLinkWhenSpawnable` | Sequencer 中 Spawnable 对象是否禁用评估 | 属性 (BlueprintReadWrite) |
| `OnLiveLinkUpdated` | 新数据到达时触发的委托 | 事件 (BlueprintAssignable) |
| `OnControllerMapUpdatedDelegate` | 控制器映射更新时触发 | 事件 (BlueprintAssignable) |
| `GetSubjectRepresentation` | 获取当前 Subject 表示 | BlueprintGetter |
| `SetSubjectRepresentation` | 设置 Subject 表示并更新控制器映射 | BlueprintSetter |
| `GetControlledComponent` | 获取指定 Role 控制的组件 | BlueprintPure |

### 控制器类

| 控制器 | 说明 | 目标组件 |
|---|---|---|
| `ULiveLinkTransformController` | 将 Transform 数据应用到 SceneComponent | USceneComponent |
| `ULiveLinkLightController` | 将灯光数据应用到灯光组件 | UPointLightComponent / USpotLightComponent |
| `ULiveLinkControllerBase` | 所有控制器的基类，可自定义扩展 | — |

### Transform 控制器配置

`FLiveLinkTransformControllerData` 结构体提供以下蓝图可编辑属性：

| 属性 | 说明 | 默认值 |
|---|---|---|
| `bWorldTransform` | 使用世界空间还是本地空间变换 | false |
| `bUseLocation` | 是否应用位置 | true |
| `bUseRotation` | 是否应用旋转 | true |
| `bUseScale` | 是否应用缩放 | true |
| `bSweep` | 移动时是否进行碰撞扫描 | false |
| `bTeleport` | 是否传送物理状态 | true |

### 使用示例（蓝图描述）

**基本用法 — 驱动 Actor 变换：**

1. 在目标 Actor 上添加 `LiveLink Component Controller` 组件
2. 在 Details 面板中设置 `Subject Representation`：
   - `Subject`：选择你的 Live Link Subject（如 "Body"）
   - `Role`：选择 `LiveLinkTransformRole`
3. `ControllerMap` 中会自动创建 `TransformRole → TransformController` 映射
4. 在 TransformController 中配置偏移（`OffsetTransform`）和空间选项
5. 运行后，Actor 的变换将实时跟随 Live Link 数据

**驱动灯光：**

1. 在灯光 Actor 上添加 `LiveLink Component Controller`
2. 设置 Subject 为灯光数据源
3. Role 选择 `LiveLinkLightRole`
4. 控制器会自动映射到 `LiveLinkLightController`，驱动灯光的颜色、强度、衰减等属性

**自定义控制器：**

1. 创建 `ULiveLinkControllerBase` 的子类
2. 重写 `Tick()` 处理数据、`IsRoleSupported()` 声明支持的 Role、`GetDesiredComponentClass()` 指定目标组件
3. 在 `Project Settings → Live Link → Component Settings` 中注册为默认控制器

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkComponentController.h"
#include "LiveLinkControllerBase.h"
#include "LiveLinkTransformController.h"
#include "LiveLinkLightController.h"
#include "LiveLinkComponentSettings.h"
```

### 基本用法 — 创建自定义控制器

```cpp
// MyCustomLiveLinkController.h
#pragma once

#include "LiveLinkControllerBase.h"
#include "MyCustomLiveLinkController.generated.h"

UCLASS()
class UMyCustomLiveLinkController : public ULiveLinkControllerBase
{
    GENERATED_BODY()

public:
    // 声明支持的 Role
    virtual bool IsRoleSupported(const TSubclassOf<ULiveLinkRole>& RoleToSupport) override
    {
        return RoleToSupport == ULiveLinkTransformRole::StaticClass();
    }

    // 指定要控制的组件类型
    virtual TSubclassOf<UActorComponent> GetDesiredComponentClass() const override
    {
        return USceneComponent::StaticClass();
    }

    // 每帧处理 Live Link 数据
    virtual void Tick(float DeltaTime, const FLiveLinkSubjectFrameData& SubjectData) override
    {
        // 从 SubjectData 中提取 Transform 数据
        // 应用到 GetAttachedComponent()
    }
};
```

### 进阶用法 — 监听 Live Link 组件注册

```cpp
// 监听 LiveLink 组件的注册事件
ILiveLinkComponentsModule& ComponentsModule = FModuleManager::GetModuleChecked<ILiveLinkComponentsModule>("LiveLinkComponents");
ComponentsModule.OnLiveLinkComponentRegistered().AddLambda([](ULiveLinkComponentController* Controller)
{
    // 对新注册的 LiveLink 组件执行自定义逻辑
    UE_LOG(LogTemp, Log, TEXT("LiveLink Controller registered on: %s"), 
        *Controller->GetOwner()->GetName());
});
```

### 进阶用法 — 编程方式设置 Subject

```cpp
// 在 C++ 中动态设置 LiveLink Subject
ULiveLinkComponentController* Controller = MyActor->FindComponentByClass<ULiveLinkComponentController>();
if (Controller)
{
    FLiveLinkSubjectRepresentation NewSubject;
    NewSubject.Subject = FLiveLinkSubjectName("MyMotionCaptureSubject");
    NewSubject.Role = ULiveLinkTransformRole::StaticClass();
    Controller->SetSubjectRepresentation(NewSubject);
}
```

### 进阶用法 — 获取受控组件

```cpp
// 获取特定 Role 控制的组件
ULiveLinkComponentController* Controller = MyActor->FindComponentByClass<ULiveLinkComponentController>();
if (Controller)
{
    UActorComponent* ControlledComp = Controller->GetControlledComponent(ULiveLinkTransformRole::StaticClass());
    if (USceneComponent* SceneComp = Cast<USceneComponent>(ControlledComp))
    {
        // 对受控的 SceneComponent 进行操作
    }
}
```

## Demo 示例

### 自定义 Live Link 控制器

```cpp
// MyLiveLinkScaleController.h
#pragma once

#include "LiveLinkControllerBase.h"
#include "Roles/LiveLinkTransformTypes.h"
#include "MyLiveLinkScaleController.generated.h"

/**
 * 自定义控制器：仅应用 Live Link 数据中的缩放值到目标组件
 */
UCLASS(BlueprintType, Blueprintable)
class UMyLiveLinkScaleController : public ULiveLinkControllerBase
{
    GENERATED_BODY()

public:
    virtual bool IsRoleSupported(const TSubclassOf<ULiveLinkRole>& RoleToSupport) override;
    virtual TSubclassOf<UActorComponent> GetDesiredComponentClass() const override;
    virtual void Tick(float DeltaTime, const FLiveLinkSubjectFrameData& SubjectData) override;
};
```

```cpp
// MyLiveLinkScaleController.cpp
#include "MyLiveLinkScaleController.h"
#include "Roles/LiveLinkTransformRole.h"
#include "Components/SceneComponent.h"

bool UMyLiveLinkScaleController::IsRoleSupported(const TSubclassOf<ULiveLinkRole>& RoleToSupport)
{
    return RoleToSupport == ULiveLinkTransformRole::StaticClass();
}

TSubclassOf<UActorComponent> UMyLiveLinkScaleController::GetDesiredComponentClass() const
{
    return USceneComponent::StaticClass();
}

void UMyLiveLinkScaleController::Tick(float DeltaTime, const FLiveLinkSubjectFrameData& SubjectData)
{
    USceneComponent* SceneComp = Cast<USceneComponent>(GetAttachedComponent());
    if (!SceneComp)
    {
        return;
    }

    // 从帧数据中提取 Transform 静态数据和动态数据
    const FLiveLinkTransformStaticData* StaticData = SubjectData.FrameData.Cast<FLiveLinkTransformStaticData>();
    const FLiveLinkTransformFrameData* FrameData = SubjectData.FrameData.Cast<FLiveLinkTransformFrameData>();

    if (StaticData && FrameData)
    {
        // 仅应用缩放，保留当前位置和旋转
        FVector CurrentLocation = SceneComp->GetComponentLocation();
        FRotator CurrentRotation = SceneComp->GetComponentRotation();
        FVector NewScale = FrameData->Transform.GetScale3D();

        FTransform NewTransform(CurrentRotation, CurrentLocation, NewScale);
        SceneComp->SetWorldTransform(NewTransform);
    }
}
```

## 模块依赖

### LiveLinkComponents 模块

| 模块 | 用途 |
|---|---|
| `LiveLink` | 核心 Live Link 框架（Role、Subject、FrameData 定义） |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

### 其他模块的典型依赖

| 模块 | 典型依赖 |
|---|---|
| `LiveLinkEditor` | `LiveLink`, `LiveLinkComponents`, `PropertyEditor` |
| `LiveLinkMovieScene` | `LiveLink`, `MovieScene` |
| `LiveLinkGraphNode` | `LiveLink`, `AnimGraph` |
| `LiveLinkMultiUser` | `LiveLink`, `MultiUserClient` |
| `LiveLinkSequencer` | `LiveLink`, `LiveLinkMovieScene` |

## 维护状态

### 近期更新

```
- fcd8083c3944 Used FortniteClient build target to find and convert all files to have dllstorage on methods/staticvar instead of on types.
- 98a8e0e0df23 Removed lots of UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes
- 038ccfea5c77 LiveLink - Adds a user exposed Offset transform to the controller component. The new member applies an offset transform in the local space of the controlled scene component.
```

- `fcd8083c`：构建系统维护，将 DLL 导出标记从类型级别迁移到方法/静态变量级别
- `98a8e0e0`：清理已废弃的头文件包含顺序宏
- `038ccfea`：**功能更新** — 为 Transform 控制器添加了用户可配置的偏移变换（`OffsetTransform`），在受控组件的本地空间中应用

### 维护评价

Live Link 是 UE 动画/虚拟制片管线的**核心基础设施**，自 2017 年创建以来持续维护。作为 Epic 官方维护的插件，它在每个引擎版本中都会收到更新和改进。

- **活跃维护**：作为 Virtual Production 工作流的关键组件，持续获得功能更新和 bug 修复
- **成熟稳定**：经过 8 年发展，API 已趋于稳定，但仍有新功能加入（如 Offset Transform）
- **默认不启用**：需要在项目设置中手动启用，适合明确需要实时数据流的项目
- **推荐使用**：任何需要外部设备实时驱动引擎数据的项目都应使用此插件

⚠️ 注意：由于模块数量多（7 个）且源码文件众多（366 个），建议根据实际需求选择性启用子模块。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLink)
- [官方文档](https://docs.unrealengine.com/en-US/AnimatingObjects/VirtualProduction/LiveLink/)（UE 官方 Live Link 文档）