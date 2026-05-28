# Remote Control Components

> (空描述)

| 属性 | 值 |
|---|---|
| 中文名 | 远程控制组件 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RemoteControlComponents` (Runtime), `RemoteControlComponentsEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-29 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RemoteControlComponents) | |

## 用途

RemoteControlComponents 插件是 Unreal Engine 远程控制框架的一个运行时扩展，主要用于**增强属性跟踪和管理的持久化与可维护性**。它解决了在远程控制（Remote Control）工作流中，手动管理哪些Actor的哪些属性已被暴露到远程控制预设（Remote Control Preset）中时遇到的痛点。

其核心机制是提供一个 `URemoteControlTrackerComponent`。当一个Actor被赋予此组件后，它能够：
1.  **跟踪已暴露的属性**：记录该Actor上哪些属性已被暴露到特定的远程控制预设中。
2.  **支持属性同步**：在复制（Duplicate）Actor时，自动将源Actor的远程控制属性配置应用到副本上。
3.  **提供集中管理**：通过 `URemoteControlComponentsSubsystem` 子系统，管理“哪个世界使用哪个远程控制预设”的映射关系，以及哪些Actor正在被跟踪。

简而言之，这个插件为远程控制属性提供了一个“胶水层”，使得属性配置能够与Actor组件生命周期绑定，便于批量管理、复制和维护。

## 使用场景

-   **虚拟制作 / 实时可视化**：当你在场景中放置了大量带有可控参数的Actor（如灯光、特效、材质实例），并需要将它们暴露给外部设备（如DMX控制器、手机App）进行实时控制时，使用此组件可以高效地管理所有暴露的属性，避免遗漏或配置不一致。
-   **需要复制已配置远程控制的Actor**：在编辑器中，如果你已经将一个Actor的多个属性暴露到远程控制面板，想复制这个Actor并保持相同的远程控制配置，添加 `RemoteControlTrackerComponent` 是实现此需求的最佳实践。
-   **构建可重用的“智能”Actor**：创建一些Actor蓝图，内置 `RemoteControlTrackerComponent`，预先配置好需要暴露的属性路径。这样，每次将此蓝图放入场景时，相关的属性会自动或通过一键操作暴露到当前世界的远程控制预设中。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get (Remote Control Components Subsystem)` | 获取远程控制组件子系统的单例。这是访问所有管理功能的入口。 | `URemoteControlComponentsSubsystem` |
| `Register Preset` | 将一个远程控制预设注册到子系统，并关联到其所在的世界。 | `URemoteControlComponentsSubsystem` |
| `Unregister Preset` | 取消注册一个远程控制预设。 | `URemoteControlComponentsSubsystem` |
| `Get Registered Preset` | 根据传入的世界或对象，获取当前关联的远程控制预设。 | `URemoteControlComponentsSubsystem` |
| `Is Actor Tracked` | 检查指定的Actor是否正在被子系统跟踪（即拥有并正确配置了TrackerComponent）。 | `URemoteControlComponentsSubsystem` |
| `Add Tracker Component` (静态) | 为一组Actor添加 `URemoteControlTrackerComponent`。 | `FRemoteControlComponentsUtils` |
| `Remove Tracker Component` (静态) | 从一组Actor上移除 `URemoteControlTrackerComponent`。 | `FRemoteControlComponentsUtils` |
| `Unexpose All Properties` (静态) | 取消指定Actor上所有已暴露的远程控制属性。 | `FRemoteControlComponentsUtils` |
| `Get Tracker Component` (静态) | 获取Actor上的TrackerComponent，可选择在不存在时自动创建。 | `FRemoteControlComponentsUtils` |
| `Get Current Preset` (静态) | 获取处理指定对象或世界的当前远程控制预设。 | `FRemoteControlComponentsUtils` |
| `Expose All Properties` | 调用此节点，将Tracker组件中记录的所有属性暴露到当前预设。 | `URemoteControlTrackerComponent` |
| `Unexpose All Properties` | 调用此节点，取消Tracker组件中记录的所有已暴露属性。 | `URemoteControlTrackerComponent` |
| `Has Tracked Properties` | 检查Tracker组件是否记录了至少一个属性。 | `URemoteControlTrackerComponent` |
| `Get Current Preset` | 获取Tracker组件当前指向的远程控制预设。 | `URemoteControlTrackerComponent` |

### 使用示例（蓝图描述）

**场景**：你有一个Actor蓝图 `BP_LightControl`，其中包含一个灯光组件和一个材质实例。你想在场景中放置多个此蓝图，并一键将它们的 `Intensity` 和 `Color` 属性暴露给远程控制。

1.  **在 `BP_LightControl` 蓝图中**：
    -   添加一个 `URemoteControlTrackerComponent`。
    -   （可选）在蓝图的构造脚本中，调用 `Add Tracked Property` 节点（属于Tracker组件），为 `Light Component` 的 `Intensity` 和 `Color` 属性添加跟踪路径。或者，你也可以在需要时动态添加。

2.  **在场景或管理器蓝图中**：
    -   首先，获取 `Remote Control Components Subsystem` 子系统。
    -   调用 `Register Preset`，确保你想要的 `RemoteControlPreset` 资产已被注册。
    -   当场景中有多个 `BP_LightControl` Actor时，你可以通过 `Get All Actors Of Class` 获取它们。
    -   使用 `FRemoteControlComponentsUtils` 静态函数中的 `Add Tracker Component`，为这些Actor批量添加Tracker组件（如果它们还没有）。
    -   对于每个Actor的Tracker组件，调用 `Expose All Properties`。这会将组件中记录的所有属性暴露到当前预设中。

3.  **复制Actor时**：直接在编辑器中复制一个已配置好的 `BP_LightControl` Actor。其副本上的 `URemoteControlTrackerComponent` 会通过 `PostDuplicate` 逻辑，自动将源Actor的远程控制属性配置复制到自身，实现了配置的无缝继承。

## C++ 用法

### 头文件引入

```cpp
#include "RemoteControlComponentsSubsystem.h"
#include "RemoteControlTrackerComponent.h"
#include "RemoteControlComponentsUtils.h"
```

### 基本用法

以下代码演示了如何在C++中为指定Actor添加Tracker并管理其远程控制属性。

```cpp
// 假设我们已经有一个 AActor* MyActor 指针

// 1. 获取子系统并注册预设（通常在游戏模式或初始化代码中）
URemoteControlComponentsSubsystem* Subsystem = URemoteControlComponentsSubsystem::Get();
if (Subsystem)
{
    // RemoteControlPresetAsset 是你的 URemoteControlPreset* 资产
    Subsystem->RegisterPreset(RemoteControlPresetAsset);
}

// 2. 为Actor添加Tracker组件
URemoteControlTrackerComponent* Tracker = FRemoteControlComponentsUtils::GetTrackerComponent(MyActor, true); // true表示如果不存在则添加
if (Tracker)
{
    // 3. 向Tracker添加一个想要跟踪的属性（例如，Actor的旋转属性）
    // 这需要构建一个 FRCFieldPathInfo 来描述属性路径
    FRCFieldPathInfo RotationPath;
    RotationPath.FromString(TEXT("RootComponent.RelativeRotation.Yaw"));
    Tracker->AddTrackedProperty(RotationPath, MyActor->GetRootComponent());

    // 4. 将Tracker中记录的所有属性暴露到远程控制预设
    Tracker->ExposeAllProperties();

    // 之后，你可以通过 Tracker->UnexposeAllProperties() 来取消暴露
    // 或者通过 Tracker->RemoveTrackedProperty(...) 来移除特定属性的跟踪
}
```

### 进阶用法

**监听事件**：子系统提供了委托，允许你监听Actor注册/注销和活跃预设变化的事件。

```cpp
// 在某个拥有生命周期的类中（如GameInstance）
URemoteControlComponentsSubsystem* Subsystem = URemoteControlComponentsSubsystem::Get();
if (Subsystem)
{
    // 绑定当有新的Actor被跟踪时
    TrackedActorRegisteredHandle = Subsystem->OnTrackedActorRegistered().AddLambda([this](AActor* Actor)
    {
        UE_LOG(LogTemp, Log, TEXT("Actor %s is now being tracked for Remote Control."), *Actor->GetName());
    });

    // 绑定当活跃预设改变时
    ActivePresetChangedHandle = Subsystem->OnActivePresetChanged().AddLambda([this](URemoteControlPreset* NewPreset)
    {
        UE_LOG(LogTemp, Log, TEXT("Active Remote Control Preset changed to: %s"), *NewPreset->GetName());
    });
}
```

**手动管理跟踪上下文**：子系统内部通过 `FRemoteControlComponentsContext` 维护世界与预设、跟踪Actor的映射。通常你不需要直接操作它，但了解其存在有助于理解系统运行逻辑。

## Demo 示例

以下是一个自定义Actor的最小实现，展示了如何将 `URemoteControlTrackerComponent` 嵌入到C++类中。

### MyRemoteControllableActor.h
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyRemoteControllableActor.generated.h"

class URemoteControlTrackerComponent;

UCLASS()
class MYPROJECT_API AMyRemoteControllableActor : public AActor
{
    GENERATED_BODY()

public:
    AMyRemoteControllableActor();

    // 暴露给蓝图和编辑器的属性，将被远程控制
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Remote Control")
    float MyFloatParameter = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Remote Control")
    FLinearColor MyColorParameter = FLinearColor::White;

protected:
    virtual void BeginPlay() override;

    // 用于跟踪上述属性的组件
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    TObjectPtr<URemoteControlTrackerComponent> PropertyTracker;

    // 在编辑器或游戏开始时，将属性添加到Tracker并暴露的逻辑
    UFUNCTION(BlueprintCallable, Category = "Remote Control")
    void SetupRemoteControlProperties();

private:
    bool bPropertiesExposed = false;
};
```

### MyRemoteControllableActor.cpp
```cpp
#include "MyRemoteControllableActor.h"
#include "RemoteControlTrackerComponent.h"
#include "RemoteControlComponentsUtils.h"
#include "RC/RemoteControlPreset.h"

AMyRemoteControllableActor::AMyRemoteControllableActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建Tracker组件作为默认子对象
    PropertyTracker = CreateDefaultSubobject<URemoteControlTrackerComponent>(TEXT("PropertyTracker"));
    PropertyTracker->bAutoActivate = true;
}

void AMyRemoteControllableActor::BeginPlay()
{
    Super::BeginPlay();
    // 在游戏开始时，如果尚未设置，则尝试暴露属性
    if (!bPropertiesExposed)
    {
        SetupRemoteControlProperties();
    }
}

void AMyRemoteControllableActor::SetupRemoteControlProperties()
{
    if (!PropertyTracker) return;

    // 为 MyFloatParameter 属性构建路径
    FRCFieldPathInfo FloatPath;
    // 假设属性直接在 Actor 上，路径即为属性名
    FloatPath.FromString(TEXT("MyFloatParameter"));

    // 为 MyColorParameter 属性构建路径
    FRCFieldPathInfo ColorPath;
    ColorPath.FromString(TEXT("MyColorParameter"));

    // 添加要跟踪的属性（第二个参数是属性的所有者对象，对于Actor自身的属性，就是this）
    PropertyTracker->AddTrackedProperty(FloatPath, this);
    PropertyTracker->AddTrackedProperty(ColorPath, this);

    // 将所有跟踪的属性暴露到远程控制预设
    PropertyTracker->ExposeAllProperties();
    bPropertiesExposed = true;

    UE_LOG(LogTemp, Log, TEXT("Exposed remote control properties for %s"), *GetName());
}
```

**使用说明**：
1.  将此类放入你的项目。
2.  在场景中放置一个 `AMyRemoteControllableActor`。
3.  确保场景中有一个 `URemoteControlPreset` 资产，并且已被 `URemoteControlComponentsSubsystem` 注册（通常在游戏模式初始化时完成）。
4.  游戏运行后（或在编辑器中，如果调用了 `SetupRemoteControlProperties`），`MyFloatParameter` 和 `MyColorParameter` 应该会出现在关联的远程控制预设中，可以被外部工具控制。

## 模块依赖

根据插件的功能和源码引用，其主要依赖于 Unreal Engine 的远程控制核心框架。

| 模块 | 用途 |
|---|---|
| `RemoteControl` | 远程控制核心模块，提供 `URemoteControlPreset`, `FRemoteControlProperty`, `FRCFieldPathInfo` 等基础类型和API。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-02-14 | `c579ba10` | Motion Design: | （更新信息未提供，可能与Motion Design插件联动相关） |
| 2024-02-13 | `723c2005` | [Remote Control Components] Remove “invalid” tracked properties from Tracker | 移除Tracker中的无效跟踪属性，增强了数据健壮性。 |
| 2024-02-12 | `10de4dbc` | Remote Control: | （更新信息未提供，可能为通用远程控制改进） |
| 2024-02-09 | `236f2d2f` | Remote Control Components: | （更新信息未提供） |
| 2024-02-07 | `1f30386d` | Motion Design RC: | （更新信息未提供，可能与Motion Design的远程控制功能相关） |

### 维护评价

-   **创建时间**：约1年前（2024年初），属于较新的插件。
-   **最近更新**：最后一批实质性更新集中在2024年2月上中旬，包含功能增强和Bug修复。**此后超过1年没有更新记录**。
-   **维护状态**：**维护不活跃**。该插件自2024年2月后似乎停止了主动开发。
-   **实验性**：插件明确标记为 `IsExperimentalVersion=true`，且默认未启用（`Installed: false`），表明它仍处于实验阶段，API和功能可能在未来版本中发生变化或被移除。
-   **推荐使用**：**谨慎使用**。如果你的项目**强依赖**上述功能（特别是Actor复制时属性同步），并且愿意承担API未来可能变动的风险，可以在实验性环境中使用。对于长期稳定项目，建议关注官方远程控制框架的演进，或考虑基于现有 RemoteControl 模块自行实现类似跟踪逻辑。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RemoteControlComponents)
-   [测试用例] (未在提供的源码结构中发现明确的测试文件路径。)