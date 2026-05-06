# XR Creative Framework

> （Description 为空）

| 属性 | 值 |
|---|---|
| 中文名 | XR 创作框架 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `XRCreative` (Runtime), `XRCreativeEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-10-15 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/XRCreativeFramework/) | |

## 用途

本插件提供了一套**运行时 VR 交互框架**，旨在为 VR 应用（如虚拟制片、空间布局、VR 编辑）提供基础架构。它解决了在 VR 环境下进行场景交互（选择、变换、传送）、工具管理和输入映射的常见问题。

核心功能包括：
- **VR 摄像机（Avatar）**：负责头部追踪、控制器定位、输入绑定，并管理一组工具。
- **交互工具框架（ITF）**：基于 UE 的 `InteractiveToolsFramework`，提供鼠标/控制器射线点击、选择、变换（位移/旋转/缩放）Gizmo。
- **射线指针与平滑**：`UXRCreativePointerComponent` 实现从控制器发射的射线检测，并使用 1 Euro 滤波器平滑抖动。
- **工具集系统**：`UXRCreativeToolset` 蓝图数据资产可定义一组 `UXRCreativeTool`，每个工具自带输入映射上下文和 Palette UI。
- **传送器**：`AXRCreativeTeleporter` 实现基础的 VR 传送移动功能。
- **设置系统**：提供项目设置（`UXRCreativeSettings`）和编辑器用户设置（`UXRCreativeEditorSettings`），如惯用手偏好。

## 使用场景

- **虚拟制片**：需要在 VR 头盔中进行场景布局、物体选择和变换。
- **VR 创意工具**：构建像 Tilt Brush 或 Quill 一类的创作应用，需要射线交互、工具切换和 UI 面板。
- **室内设计 / 空间规划**：在 VR 中摆放家具并实时预览。
- **VR 编辑器扩展**：作为在编辑器中启动 VR 模式后进行交互的基础插件（插件中包含 `EnterVRMode` / `ExitVRMode` 静态函数）。

## 蓝图用法

以下列出插件对外暴露的常用蓝图节点（通过 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 访问）。

### 核心组件类

#### `UXRCreativeITFComponent`（交互工具框架组件）

| 节点 | 说明 | 返回/参数 |
|---|---|---|
| `LeftMousePressed` / `LeftMouseReleased` | 模拟鼠标左键按下/释放，通常通过 VR 手柄触发 | 无参数 |
| `GetSelectionSet` | 获取当前 Typed Element 选择集 | `UTypedElementSelectionSet*` |
| `HaveActiveTool` | 是否有激活的工具 | `bool` |
| `GetCurrentCoordinateSystem` | 获取当前变换坐标系（Local/World） | `EToolContextCoordinateSystem` |
| `SetCurrentCoordinateSystem` | 设置变换坐标系 | `EToolContextCoordinateSystem` |
| `GetCurrentTransformGizmoMode` | 获取当前 Gizmo 模式（Translate/Rotate/Scale/Combined） | `EToolContextTransformGizmoMode` |
| `SetCurrentTransformGizmoMode` | 设置 Gizmo 模式 | `EToolContextTransformGizmoMode` |
| `CanUndo` / `CanRedo` | 是否可以撤销/重做 | `bool` |
| `Undo` / `Redo` | 执行撤销/重做 | 无参数 |
| `IsInEditor` | 是否在编辑器环境下运行 | `bool` |

**事件**：`OnUndo` / `OnRedo`（动态多播委托）

#### `AXRCreativeAvatar`（VR 摄像机）

| 节点 | 说明 |
|---|---|
| `GetHeadTransform` | 获取头部在世界空间的变换 |
| `GetHeadTransformRoomSpace` | 获取头部在房间空间的变换 |
| `RegisterObjectForInput` | 注册对象以接收输入（动态绑定） |
| `UnregisterObjectForInput` | 取消注册 |
| `AddInputMappingContext` | 为 Avatar 添加输入映射上下文 |
| `RemoveInputMappingContext` | 移除输入映射上下文 |
| `ClearAllInputMappings` | 清除所有输入映射 |
| `SetComponentTickInEditor` | 设置组件在编辑器中是否 Tick |

**蓝图事件**：`BP_OnVRInitialize`（进入 VR 时调用）

#### `UXRCreativePointerComponent`（射线指针组件）

| 节点 | 说明 |
|---|---|
| `GetRawTraceEnd` | 获取未滤波的射线端点（可选截断到命中点） |
| `GetFilteredTraceEnd` | 获取经过 1 Euro 滤波后的射线端点 |
| `GetHitResult` | 获取当前命中结果 |
| `IsEnabled` / `SetEnabled` | 启用/禁用射线 |
| `IgnoredActors` / `IgnoredComponents`（变量） | 要忽略的 Actor/组件数组 |

#### `UXRCreativeTransformInteraction`（变换交互）

| 节点 | 说明 |
|---|---|
| `SetEnableScaling` | 启用/禁用缩放 Gizmo |
| `SetEnableNonUniformScaling` | 启用/禁用非均匀缩放 Gizmo |
| `ForceUpdateGizmoState` | 强制重建 Gizmo（选中物体变化时调用） |

#### `UXRCreativeCombinedTransformGizmoActor`（Gizmo Actor）

| 节点 | 说明 |
|---|---|
| `GetOwnerAvatar` | 获取拥有该 Gizmo 的 Avatar |

#### `UXRCreativeSubsystem`（引擎子系统）

| 节点 | 说明 |
|---|---|
| `GetViewModelCollection` | 获取 MVVM ViewModel 集合 |
| `EnterVRMode`（Editor 中） | 进入 VR 模式 |
| `ExitVRMode`（Editor 中） | 退出 VR 模式 |

### 工具集系统

`UXRCreativeToolset` 是数据资产，可在编辑器中配置一组工具。`UXRCreativeTool` 和 `UXRCreativeBlueprintableTool` 提供了在蓝图中定义工具的接口：

- `GetToolName`（纯虚）
- `GetDisplayName`（纯虚）
- `GetPaletteTabClass`（纯虚）
- `GetToolInputMappingContext`（仅 `UXRCreativeBlueprintableTool` 实现）

### 使用示例（蓝图描述）

**基本 VR 射线点击选择**：
1. 在 Avatar 蓝图的事件图表中，调用 `ITF Component` → `LeftMousePressed`（比如绑定到手柄 Trigger 键）。
2. ITF 组件内部的 `UXRCreativeSelectionInteraction` 会使用射线指针的命中结果进行选择。
3. 选择完成后，可通过 `GetSelectionSet` 获取被选的 Actor。

**切换变换 Gizmo 模式**：
1. 在 Avatar 蓝图中，调用 `ITF Component` → `SetCurrentTransformGizmoMode`，传入 `EToolContextTransformGizmoMode`（如 `Rotate` 或 `Scale`）。

**添加自定义工具**：
1. 创建一个继承自 `UXRCreativeBlueprintableTool` 的蓝图类。
2. 设置 `ToolName`、`DisplayName`、`PaletteTabClass`（可选）、`RightHandedInputMappingContext` 等属性。
3. 创建一个 `UXRCreativeToolset` 数据资产，将工具蓝图添加到工具列表。
4. 在 Avatar 的 `ConfigureToolset` 节点中传入该 Toolset。

## C++ 用法

### 头文件引入

```cpp
// 核心功能
#include "XRCreativeAvatar.h"
#include "XRCreativeITFComponent.h"
#include "XRCreativePointerComponent.h"
#include "XRCreativeSettings.h"
#include "XRCreativeSubsystem.h"

// 工具集与 Gizmo
#include "XRCreativeToolset.h"
#include "XRCreativeGizmos.h"
```

### 基本用法

**创建 Avatar 并设置工具集**（在游戏模式中）：

```cpp
// 文件路径: Source/XRCreative/Private/XRCreativeGameMode.cpp
void AXRCreativeGameMode::BeginPlay()
{
    Super::BeginPlay();
    if (ToolsetClass.IsValid())
    {
        UXRCreativeToolset* Toolset = ToolsetClass.LoadSynchronous();
        if (Toolset)
        {
            AActor* AvatarActor = GetWorld()->SpawnActor<AActor>(AvatarClass);
            AXRCreativeAvatar* Avatar = Cast<AXRCreativeAvatar>(AvatarActor);
            if (Avatar)
            {
                Avatar->ConfigureToolset(Toolset);
            }
        }
    }
}
```

**使用选择交互**（从 ITFComponent 获取选择集）：

```cpp
// 文件路径: Source/XRCreative/Private/ITF/SelectionInteraction.cpp
void UXRCreativeSelectionInteraction::Initialize(
    UTypedElementSelectionSet* InSelectionSet,
    FActorPredicate InCanSelectCallback,
    FTraceMethod InTraceCallback)
{
    // ...
    ClickBehavior = NewObject<USingleClickInputBehavior>();
    ClickBehavior->SetIsHitByClickFunction([this](const FInputDeviceRay& Ray) {
        return IsHitByClick(Ray);
    });
    // ...
}
```

**获取指针组件的射线端点**：

```cpp
// 文件路径: Source/XRCreative/Private/XRCreativePointerComponent.cpp
FVector UXRCreativePointerComponent::GetFilteredTraceEnd(const bool bScaledByImpact) const
{
    FVector End = SmoothingFilter ? SmoothingFilter->Filter(RawTraceEnd, ...) : RawTraceEnd;
    if (bScaledByImpact && HitResult.bBlockingHit)
    {
        End = End.GetSafeNormal() * (HitResult.Distance - HitResult.Time * (HitResult.Distance - End.Size()));
    }
    return End;
}
```

### 进阶用法

**自定义选择过滤**：传递一个 `FActorPredicate` 到 `UXRCreativeSelectionInteraction::Initialize` 中，控制哪些 Actor 可以被选择（例如锁定时拒绝选择）：

```cpp
// 创建自定义谓词
auto MyCanSelect = [](AActor* Actor) -> bool
{
    return Actor && Actor->IsA<AMySelectableActor>();
};

// 从 ITF 组件内部调用
Interaction->Initialize(SelectionSet, MoveTemp(MyCanSelect));
```

**在 VR 中手动触发撤销/重做**：

```cpp
if (UXRCreativeITFComponent* ITF = Avatar->FindComponentByClass<UXRCreativeITFComponent>())
{
    if (ITF->CanUndo())
        ITF->Undo();
}
```

## Demo 示例

以下是一个最小示例，展示如何在一个 Actor 中使用 `UXRCreativePointerComponent` 和 `UXRCreativeITFComponent` 实现 VR 射线选择与变换。

**MyVRActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyVRActor.generated.h"

class UXRCreativePointerComponent;
class UXRCreativeITFComponent;

UCLASS()
class AMyVRActor : public AActor
{
    GENERATED_BODY()

public:
    AMyVRActor();

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "XR Creative")
    UXRCreativePointerComponent* PointerComponent;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "XR Creative")
    UXRCreativeITFComponent* ITFComponent;

    virtual void BeginPlay() override;
};
```

**MyVRActor.cpp**
```cpp
#include "MyVRActor.h"
#include "XRCreativePointerComponent.h"
#include "XRCreativeITFComponent.h"
#include "XRCreativeAvatar.h"

AMyVRActor::AMyVRActor()
{
    PrimaryActorTick.bCanEverTick = true;

    PointerComponent = CreateDefaultSubobject<UXRCreativePointerComponent>(TEXT("Pointer"));
    RootComponent = PointerComponent;
    PointerComponent->SetRelativeLocation(FVector(100.f, 0.f, 0.f)); // 模拟控制器偏移

    ITFComponent = CreateDefaultSubobject<UXRCreativeITFComponent>(TEXT("ITF"));
    ITFComponent->SetPointerComponent(PointerComponent);
}

void AMyVRActor::BeginPlay()
{
    Super::BeginPlay();
    // 将 ITF 的选择集与场景默认选择集关联（需要自行获取）
    // 实际应用中可以从 UTypedElementSelectionSet* SelectionSet = ...;
    // ITFComponent->InitializeComponent(); 会自动初始化
}
```

注意：此 Demo 仅为概念展示，完整运行需要配套的 `AXRCreativeAvatar` 和游戏模式设置。请参考官方示例或插件内测试代码。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `HeadMountedDisplay` | 提供 UMotionControllerComponent 等 XR 设备支持 |
| `EnhancedInput` | 提供 UInputMappingContext 和动态输入绑定 |
| `InteractiveToolsFramework` | 提供变换 Gizmo、交互行为等核心框架 |
| `TypedElementFramework` | 提供 Typed Element 选择系统 |
| `CommonUI` | 提供 UCommonActivatableWidget 用于 Palette 界面 |
| `ViewModel` (MVVM) | 提供 UMVVMViewModelCollectionObject，支持 ViewModel 数据绑定 |

其他依赖（不列出常见模块）：无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

- 2025-09-23 `9feb681f` — VR Editor: Fix for failed check in UWidgetComponent unregister during engine pre-exit.
- 2024-11-28 `eca86263` — Remove the check for r.PostProcess.PropagateAlpha in the XR Creative ::ValidateSettings().
- 2024-11-28 `be437642` — Created missing Get/Set functions for the following member variables.
- 2024-10-30 `d4d88219` — Removed more includes of SceneManagement.h in favor of the needed includes.
- 2024-10-15 `08bf24fa` — VR Editor: Fixes a regression from CL 36864748 that led to FSlateRHIRenderer not correctly interoper.

### 维护评价

插件创建于 2024 年 10 月，距今约 1 年。最近一次实质性更新为 2025 年 9 月（修复 Widget 组件生命周期问题），但整体 commit 数量较少且集中在基础设施修复与头文件重构上。作为实验性插件（`IsBetaVersion=true`），它仍处于早期开发状态，核心 API 可能变动。已知未实现的功能包括：测试覆盖不足、部分功能（如 Teleporter）仅为骨架。推荐用于快速原型和内部工具开发，生产环境使用需谨慎并自行完善。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/XRCreativeFramework/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/XRCreativeFramework/Tests/)（如果存在）