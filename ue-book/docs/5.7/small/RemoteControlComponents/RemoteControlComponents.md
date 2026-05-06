# Remote Control Components

> 

| 属性 | 值 |
|---|---|
| 中文名 | 远程控制组件 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RemoteControlComponents` (Runtime), `RemoteControlComponentsEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-02-07 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RemoteControlComponents) | |

## 用途

Remote Control Components 是 Remote Control 系统的补充，提供了一套组件和子系统，让开发者能够以声明式的方式管理 Actor 的属性远程控制暴露。核心思路：**在 Actor 上附加一个 `URemoteControlTrackerComponent` 组件，声明哪些属性需要暴露到指定的 Remote Control Preset 中**。该组件会自动处理 Actor 复制、加载、事务撤销/重做等场景下的暴露状态同步，无需手动调用预设的 Expose/Unexpose 接口。

该模块解决了以下问题：
- 传统 Remote Control 需要开发者在代码或蓝图中手动管理 Preset 与 Actor 属性的绑定，工作量大且容易出错。
- 属性暴露状态在 Actor 复制（`PostDuplicate`）、预存（`PreSave`）、加载（`PostLoad`）时会丢失或不同步。
- 缺乏一个统一的上下文（`FRemoteControlComponentsContext`）来关联特定 World、Preset 以及被跟踪的 Actor。

插件通过以下机制实现：
- `URemoteControlComponentsSubsystem`（引擎子系统）集中管理 Preset 注册与 Actor 跟踪。
- `FRemoteControlTrackerProperty` 结构体保存每个被暴露属性的字段路径、属主对象和暴露状态。
- `URemoteControlTrackerComponent` 在 Actor 上维护一个 `TrackedProperties` 数组，提供批量暴露/取消暴露、属性 ID 同步等功能。
- `FRemoteControlComponentsUtils` 提供静态辅助函数，快速添加/移除 Tracker 组件、刷新属性等。

## 使用场景

- **动态属性远程控制**：在游戏运行时，允许外部设备（如平板、Web 面板）通过 Remote Control 调整场景中 Actor 的属性（灯光颜色、材质参数等）。为每个相关 Actor 添加 Tracker 组件并指定要暴露的属性，系统自动保持同步。
- **关卡编辑/协同工作流**：多个开发者同时编辑一个关卡，通过 Remote Control 实时共享属性调整。Tracker 组件确保属性在被复制或粘贴到另一个 World 时能够自动重新暴露。
- **程序化生成内容**：当通过蓝图或 C++ 动态生成 Actor 并希望其某些属性暴露给 Remote Control 时，无需手动查找 Preset 和调用 Expose，只需给 Actor 附加 Tracker 组件并调用 `ExposeAllProperties()`。
- **包装现有功能**：对于已有的 Actor 蓝图，只需添加一个 Tracker 组件并勾选要暴露的属性（通过路径），即可迅速集成远程控制功能，无需修改原有逻辑。

## 蓝图用法

该插件主要面向 C++ 开发者，蓝图支持有限。在蓝图中可以通过组件引用调用 Tracker 组件的**公开方法**（但这些方法未标记 `BlueprintCallable`，因此无法直接调用）。唯一的蓝图交互方式是**通过 C++ 暴露的接口或通过 Remote Control 预设本身**。不过，以下是有用的信息：

| 节点 | 说明 | 所在类 |
|---|---|---|
| 无 | 该插件未提供任何 `UFUNCTION(BlueprintCallable)` 节点 | - |

若需在蓝图中使用 Tracker 组件，建议创建一个 C++ 函数库（`UBlueprintFunctionLibrary`），包装 `FRemoteControlComponentsUtils::AddTrackerComponent` 等方法并标记为 `BlueprintCallable`。该插件本身不提供此包装。

## C++ 用法

### 头文件引入

```cpp
#include "RemoteControlComponentsUtils.h"
#include "RemoteControlTrackerComponent.h"
#include "Subsystems/RemoteControlComponentsSubsystem.h"
```

### 基本用法

以下示例展示如何为场景中所有的 Light Actor 添加 Tracker 组件，并暴露其 Intensity 属性。

```cpp
// 获取当前 World 的 Remote Control Preset（假设已创建）
UWorld* World = GetWorld();
URemoteControlPreset* Preset = ...; 

// 注册 Preset 到子系统
URemoteControlComponentsSubsystem* RCSubsystem = URemoteControlComponentsSubsystem::Get();
RCSubsystem->RegisterPreset(Preset);

// 为所有点光源 Actor 添加 Tracker 组件
TArray<AActor*> Actors;
UGameplayStatics::GetAllActorsOfClass(World, APointLight::StaticClass(), Actors);
TSet<TWeakObjectPtr<AActor>> ActorSet;
for (AActor* Actor : Actors)
{
    ActorSet.Add(Actor);
}
FRemoteControlComponentsUtils::AddTrackerComponent(ActorSet);

// 遍历每个 Actor，手动跟踪其 Intensity 属性
for (AActor* Actor : Actors)
{
    URemoteControlTrackerComponent* Tracker = FRemoteControlComponentsUtils::GetTrackerComponent(Actor, false);
    if (Tracker)
    {
        // 指定属性路径: "PointLightComponent.Intensity"
        FRCFieldPathInfo FieldPath(TEXT("PointLightComponent.Intensity"));
        Tracker->AddTrackedProperty(FieldPath, Actor);
    }
}

// 最后，为所有此类 Actor 暴露属性
for (AActor* Actor : Actors)
{
    URemoteControlTrackerComponent* Tracker = FRemoteControlComponentsUtils::GetTrackerComponent(Actor);
    if (Tracker)
    {
        Tracker->ExposeAllProperties();
    }
}
```

> 来源：`RemoteControlTrackerComponent.h` 和 `RemoteControlComponentsUtils.h` 接口。

### 进阶用法

**1. 利用 Tracker 自动同步复制/粘贴**

当 Actor 被复制（`PostDuplicate`）后，`URemoteControlTrackerComponent` 会自动在 `PostDuplicate` 中调用 `OnTrackerDuplicated()`，将源 Actor 的 `TrackedProperties` 数组复制到新 Actor 上，并尝试重新暴露到当前 Preset。开发者无需额外处理。

**2. 手动刷新属性 ID**

在某些情况下（例如 Preset 被序列化后重载），属性 ID 可能会失效。可以调用 `RefreshAllPropertyIds()` 从 Tracker 向 Preset 同步 ID，或 `WriteAllPropertyIdsToPreset()` 从 Preset 向 Tracker 写回 ID。

```cpp
for (AActor* Actor : Actors)
{
    URemoteControlTrackerComponent* Tracker = FRemoteControlComponentsUtils::GetTrackerComponent(Actor, false);
    if (Tracker)
    {
        Tracker->RefreshAllPropertyIds(); // Tracker → Preset
        // 或者
        Tracker->WriteAllPropertyIdsToPreset(); // Preset → Tracker
    }
}
```

**3. 使用 `FRemoteControlComponentsUtils` 批量取消暴露**

```cpp
// 取消某个 Actor 的所有暴露属性（并停止跟踪）
FRemoteControlComponentsUtils::UnexposeAllProperties(Actor);
```

## Demo 示例

一个完整的最小 C++ 示例，创建一个 Actor 类，使其自动添加 Tracker 组件并暴露一个属性。

**MyTrackedActor.h**
```cpp
#pragma once

#include "GameFramework/Actor.h"
#include "MyTrackedActor.generated.h"

class URemoteControlTrackerComponent;

UCLASS()
class AMYTRACKEDACTOR : public AActor
{
    GENERATED_BODY()

public:
    AMYTRACKEDACTOR();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Remote Control")
    float MyTrackedFloat = 0.0f;

    UFUNCTION(BlueprintCallable, Category = "Remote Control")
    void ExposeMyFloat();

    // 在组件生命周期中暴露属性
    virtual void PostInitializeComponents() override;

private:
    UPROPERTY()
    URemoteControlTrackerComponent* TrackerComponent;
};
```

**MyTrackedActor.cpp**
```cpp
#include "MyTrackedActor.h"
#include "RemoteControlTrackerComponent.h"
#include "RemoteControlComponentsUtils.h"
#include "Subsystems/RemoteControlComponentsSubsystem.h"
#include "RemoteControlPreset.h"

AMYTRACKEDACTOR::AMYTRACKEDACTOR()
{
    // 创建 Tracker 组件（注意：必须由 Actor 创建，不能是子组件）
    TrackerComponent = CreateDefaultSubobject<URemoteControlTrackerComponent>(TEXT("RCTracker"));
}

void AMYTRACKEDACTOR::PostInitializeComponents()
{
    Super::PostInitializeComponents();

    // 获取子系统并注册 Preset（这里假设 Preset 已存在且被设置到某个全局变量中）
    URemoteControlComponentsSubsystem* RCSubsystem = URemoteControlComponentsSubsystem::Get();
    if (RCSubsystem)
    {
        // 示例：使用第一个已注册的 Preset 或创建一个新的
        // 实际项目中应该通过 World 查找或配置
        if (URemoteControlPreset* Preset = nullptr /* 获取 Preset */)
        {
            RCSubsystem->RegisterPreset(Preset);
        }
    }
}

void AMYTRACKEDACTOR::ExposeMyFloat()
{
    // 将 MyTrackedFloat 暴露给系统
    FRCFieldPathInfo FieldPath(TEXT("MyTrackedFloat"));
    TrackerComponent->AddTrackedProperty(FieldPath, this);
    TrackerComponent->ExposeAllProperties();
}
```

**注意**：实际运行时需要确保已创建了一个 `URemoteControlPreset` 并注册到子系统中。Demo 中仅为示意。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RemoteControl` | 提供 `URemoteControlPreset`、`FRCFieldPathInfo` 等核心 Remote Control 类型 |
| `RemoteControlCommon` | 可能依赖（作为 RemoteControl 的通用工具模块） |

其余依赖为常见模块（Core, Engine, CoreUObject, Slate 等），已省略。

## 维护状态

### 近期更新

- `2024-02-14` c579ba1  Motion Design: （与 Motion Design 集成相关）
- `2024-02-13` 723c200  [Remote Control Components] Remove "invalid" tracked properties from Tracker （清理无效的跟踪属性）
- `2024-02-12` 10de4db  Remote Control: （远程控制相关）
- `2024-02-09` 236f2d2  Remote Control Components: （组件功能改进）
- `2024-02-07` 1f30386  Motion Design RC: （首次提交？）

### 维护评价

- **创建时间**：2024-02-07，距今约 1 年。
- **近期更新频率**：在 2024 年 2 月期间有密集更新，之后无更多提交（截至当前分析时间）。可能属于一次性开发阶段。
- **活跃度**：从提交记录看，该插件在初始 2 周内活跃，之后可能转为稳定状态。无废弃标记。
- **已知问题**：该插件仍处于实验阶段，API 可能变更。文档中提到的 `FRemoteControlComponentsUtils::RefreshTrackedProperties` 等函数并未公开，可能功能未完全实现。
- **推荐度**：如果项目需要在 Actor 级别管理大量属性暴露，该插件可以大幅简化代码。但鉴于其实验性质，建议谨慎使用，并做好兼容性准备。

**警告**：超过 1 年未发现实质性更新，请在使用前确认引擎版本兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RemoteControlComponents)
- [官方文档](https://docs.unrealengine.com/5.3/en-US/remote-control-components-in-unreal-engine/)（可能需要更新）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RemoteControlComponents/Tests)（如果存在）