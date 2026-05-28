# XR Creative Framework

> 

| 属性 | 值 |
|---|---|
| 中文名 | XR 创意框架 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `XRCreative` (Runtime), `XRCreativeEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-02-14 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/XRCreativeFramework) | |

## 用途

XRCreativeFramework 是一个面向虚拟制作（Virtual Production）场景的 VR 创意工具框架。它提供了一整套在 VR 环境中进行场景编辑和交互的基础设施：

- **VR 化身系统**（`AXRCreativeAvatar`）：带有双手运动控制器、激光指针、菜单 Widget 的完整 VR Pawn
- **交互式工具框架**（ITF）：将 UE5 的 Interactive Tools Framework 移植到 VR 环境，支持物体选择、变换 Gizmo、撤销/重做
- **工具系统**：可扩展的工具架构，支持自定义工具定义（`UXRCreativeTool`）和工具集配置（`UXRCreativeToolset`）
- **VR 模式管理**：通过子系统在编辑器中进入/退出 VR 模式

本质上，这个 plugin 解决的是"如何在 VR 头显中像桌面编辑器一样操控 UE5 场景"的问题。它把编辑器中的选择、变换、工具切换等功能封装成了 VR 可用的交互方式。

## 使用场景

- 你是一个虚拟制片工作者，需要在 VR 中直接预览和调整场景布局
- 你正在开发 VR 创意应用，需要一套现成的 VR 控制器交互和工具选择框架
- 你需要在 VR 中对 Actor 进行移动/旋转/缩放，同时保留撤销重做能力
- 你想基于此框架扩展自定义 VR 工具（如画笔、测量等）

## 蓝图用法

### 核心节点 — 头部与控制器

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetHeadTransform` | 获取 VR 头显的世界变换 | `AXRCreativeAvatar` |
| `GetHeadTransformRoomSpace` | 获取头显的房间空间变换 | `AXRCreativeAvatar` |
| `PlayHapticEffect` | 在指定手柄上播放触觉反馈 | `AXRCreativeAvatar` |
| `StopHapticEffect` | 停止指定手柄的触觉反馈 | `AXRCreativeAvatar` |
| `SpawnTransientActor` | 创建临时 Actor（不污染编辑器世界） | `AXRCreativeAvatar` |
| `OpenLevelSequence` | 在 VR 中打开关卡序列 | `AXRCreativeAvatar` |

### 核心节点 — 输入系统

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddInputMappingContext` | 添加输入映射上下文 | `AXRCreativeAvatar` |
| `RemoveInputMappingContext` | 移除输入映射上下文 | `AXRCreativeAvatar` |
| `ClearAllInputMappings` | 清除所有输入映射 | `AXRCreativeAvatar` |
| `RegisterObjectForInput` | 注册对象到输入组件以接收蓝图输入事件 | `AXRCreativeAvatar` |
| `UnregisterObjectForInput` | 取消对象的输入注册 | `AXRCreativeAvatar` |

### 核心节点 — 工具与选择

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Undo` / `Redo` | 执行撤销/重做操作 | `UXRCreativeITFComponent` |
| `CanUndo` / `CanRedo` | 查询是否可撤销/重做 | `UXRCreativeITFComponent` |
| `GetSelectionSet` | 获取当前选择集 | `UXRCreativeITFComponent` |
| `GetCurrentCoordinateSystem` | 获取当前坐标系（世界/局部） | `UXRCreativeITFComponent` |
| `SetCurrentCoordinateSystem` | 设置坐标系 | `UXRCreativeITFComponent` |
| `GetCurrentTransformGizmoMode` | 获取 Gizmo 模式 | `UXRCreativeITFComponent` |
| `GetGizmoActor` | 获取变换 Gizmo Actor | `UXRCreativeITFComponent` |

### 核心节点 — 指针与射线

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetRawTraceEnd` | 获取原始射线终点（可选按碰撞距离缩放） | `UXRCreativePointerComponent` |
| `GetFilteredTraceEnd` | 获取平滑后的射线终点 | `UXRCreativePointerComponent` |
| `GetHitResult` | 获取射线命中结果 | `UXRCreativePointerComponent` |
| `SetEnabled` / `IsEnabled` | 启用/禁用指针 | `UXRCreativePointerComponent` |

### 核心节点 — 变换交互

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetEnableScaling` | 启用/禁用缩放功能 | `UXRCreativeTransformInteraction` |
| `SetEnableNonUniformScaling` | 启用/禁用非均匀缩放 | `UXRCreativeTransformInteraction` |
| `ForceUpdateGizmoState` | 强制刷新 Gizmo 状态（选择变化后调用） | `UXRCreativeTransformInteraction` |

### 核心节点 — 系统级

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetViewModelCollection` | 获取 MVVM ViewModel 集合 | `UXRCreativeSubsystem` |
| `EnterVRMode` | 进入编辑器 VR 模式（仅编辑器） | `UXRCreativeSubsystem` |
| `ExitVRMode` | 退出编辑器 VR 模式（仅编辑器） | `UXRCreativeSubsystem` |

### 使用示例（蓝图描述）

**创建自定义 VR 工具**：
1. 创建一个继承自 `UXRCreativeBlueprintableTool` 的蓝图子类
2. 设置 `ToolName`（如 "MyBrushTool"）和 `DisplayName`（如 "画笔工具"）
3. 配置 `PaletteTabClass` 为对应的 UI 标签页类
4. 创建 `UInputMappingContext` 并分别设置到 `RightHandedInputMappingContext` 和 `LeftHandedInputMappingContext`
5. 创建 `UXRCreativeToolset` 数据资产，在 `Tools` 数组中添加你的工具条目
6. 在 `AXRCreativeGameMode` 中指定该 `Toolset`

**配置 VR 化身**：
1. 创建继承自 `AXRCreativeAvatar` 的蓝图
2. `LeftController`、`RightController`、`LeftControllerPointer`、`RightControllerPointer` 等组件在构造时自动创建
3. 在 GameMode 或子系统中调用 `EnterVRMode` 启动 VR

## C++ 用法

### 头文件引入

```cpp
#include "XRCreativeAvatar.h"
#include "XRCreativeSubsystem.h"
#include "XRCreativeITFComponent.h"
#include "XRCreativeToolset.h"
#include "XRCreativePointerComponent.h"
#include "XRCreativeGizmos.h"
```

### 基本用法 — 创建自定义工具

```cpp
// 继承 UXRCreativeBlueprintableTool 创建 C++ 工具
// 来源: Public/XRCreativeToolset.h

UCLASS(Blueprintable)
class UMyVRCreativeTool : public UXRCreativeBlueprintableTool
{
    GENERATED_BODY()

public:
    UMyVRCreativeTool()
    {
        ToolName = FName("MeasureTool");
        DisplayName = FText::FromString(TEXT("Measure Tool"));
    }
};
```

### 基本用法 — 访问 Avatar 头部变换

```cpp
// 在蓝图或 C++ 中获取 VR 头部位置
// 来源: Public/XRCreativeAvatar.h

AXRCreativeAvatar* Avatar = /* 获取 Avatar 引用 */;
FTransform HeadTransform = Avatar->GetHeadTransform();
FTransform HeadRoomTransform = Avatar->GetHeadTransformRoomSpace();

// 获取控制器的激光射线
FVector LaserStart, LaserEnd;
if (Avatar->GetLaserForHand(EControllerHand::Right, LaserStart, LaserEnd))
{
    // 执行射线检测或其他操作
    DrawDebugLine(GetWorld(), LaserStart, LaserEnd, FColor::Green, false, 0.1f);
}
```

### 进阶用法 — ITF 工具系统交互

```cpp
// 通过 ITF 组件控制工具系统
// 来源: Public/XRCreativeITFComponent.h

UXRCreativeITFComponent* ITFComponent = Avatar->FindComponentByClass<UXRCreativeITFComponent>();

// 切换坐标系
ITFComponent->SetCurrentCoordinateSystem(EToolContextCoordinateSystem::Local);

// 切换 Gizmo 模式
ITFComponent->SetCurrentTransformGizmoMode(EToolContextTransformGizmoMode::Combined);

// 撤销/重做
if (ITFComponent->CanUndo())
{
    ITFComponent->Undo();
}

// 获取选择集
UTypedElementSelectionSet* Selection = ITFComponent->GetSelectionSet();
```

### 进阶用法 — 指针射线检测

```cpp
// 来源: Public/XRCreativePointerComponent.h

UXRCreativePointerComponent* Pointer = Avatar->LeftControllerPointer;

// 获取平滑后的射线终点（按碰撞距离缩放）
FVector TraceEnd = Pointer->GetFilteredTraceEnd(true);

// 获取碰撞结果
const FHitResult& Hit = Pointer->GetHitResult();
if (Hit.bBlockingHit)
{
    AActor* HitActor = Hit.GetActor();
    FVector HitPoint = Hit.ImpactPoint;
}

// 启用/禁用指针
Pointer->SetEnabled(false);
```

## Demo 示例

### 自定义 VR 工具 Actor

```cpp
// MyVRCreativeToolActor.h
#pragma once

#include "CoreMinimal.h"
#include "XRCreativeToolActor.h"
#include "MyVRCreativeToolActor.generated.h"

UCLASS(Blueprintable)
class MYPROJECT_API AMyVRCreativeToolActor : public AXRCreativeToolActor
{
    GENERATED_BODY()

public:
    AMyVRCreativeToolActor();

    // 由 Avatar 调用以初始化工具
    UFUNCTION(BlueprintImplementableEvent, BlueprintCallable, Category="XR Creative")
    void InitializeTool();

    // 每帧由 Avatar 调用
    UFUNCTION(BlueprintImplementableEvent, BlueprintCallable, Category="XR Creative")
    void TickTool(float DeltaSeconds);

    // 工具关闭时调用
    UFUNCTION(BlueprintImplementableEvent, BlueprintCallable, Category="XR Creative")
    bool ShutDownTool();
};
```

```cpp
// MyVRCreativeToolActor.cpp
#include "MyVRCreativeToolActor.h"

AMyVRCreativeToolActor::AMyVRCreativeToolActor()
{
    PrimaryActorTick.bCanEverTick = true;
}
```

### 通过 Subsystem 管理 VR 模式

```cpp
// 来源: Public/XRCreativeSubsystem.h

// 在编辑器工具中进入 VR 模式
#if WITH_EDITOR
UXRCreativeSubsystem* Subsystem = GEngine->GetEngineSubsystem<UXRCreativeSubsystem>();
if (Subsystem)
{
    bool bSuccess = UXRCreativeSubsystem::EnterVRMode();
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("VR Mode entered successfully"));
    }
}

// 退出 VR 模式
UXRCreativeSubsystem::ExitVRMode();

// 获取 MVVM ViewModel 集合
UMVVMViewModelCollectionObject* ViewModelCollection = Subsystem->GetViewModelCollection();
#endif
```

## 模块依赖

从 Build.cs 分析，该插件依赖以下独特模块：

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | 增强输入系统，用于 VR 控制器输入映射 |
| `InteractiveToolsFramework` | UE5 交互式工具框架，提供 Gizmo 和工具基础设施 |
| `ToolWidgets` | 工具 UI 组件 |
| `CommonUI` | 通用 UI 框架，用于工具面板和菜单 |
| `ModelViewViewModel` (MVVM) | MVVM 架构，用于工具 UI 与数据绑定 |
| `Concert` | Multi-User 协作会话支持 |
| `LevelSequence` | 关卡序列支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-18 | `998bea39` | [XR Creative] - Fix regression where actors moved with the VR Gizmo then can't be selected because t | 修复 VR Gizmo 移动 Actor 后无法再次选中的回归 bug |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中作用域枚举导致的乱码输出 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移 UE_LOG 宏到 UE_LOGF 新格式 |
| 2026-03-04 | `32fcdd48` | Remove includes guarded by `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_4`. | 清理 5.4 版本废弃的头文件包含守卫 |
| 2026-02-06 | `119111a0` | Complete refactor in 50451248 and deprecate old methods | 完成重构并废弃旧方法 |

### 维护评价

**活跃维护中**。该插件创建于 2023 年 2 月，虽然标记为实验性（Beta）且默认未启用，但从提交历史来看持续有实质性更新：

- 2026 年仍有功能性 bug 修复（Gizmo 选择回归问题）和代码质量改进
- 有完整的架构重构，说明 Epic 仍在积极迭代该框架
- 作为 Virtual Production 领域的 VR 创作工具，属于 Epic 重点投入方向
- `IsBetaVersion=true` 和 `EnabledByDefault=false` 表明尚未正式发布，API 可能继续变动
- `CanContainContent=false` 表明纯代码插件，无资产依赖

**建议**：适合在虚拟制片项目中探索性使用，不建议在生产环境中作为核心依赖。关注其从 Experimental 迁移到正式目录的时间点。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/XRCreativeFramework)