# Scriptable Tools Framework

> Blueprint-Scriptable extension to the Interactive Tools Framework

| 属性 | 值 |
|---|---|
| 中文名 | 脚本化工具框架 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ScriptableToolsFramework` (Runtime), `EditorScriptableToolsFramework` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-26 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ScriptableToolsFramework) | |

## 用途

该插件将 UE 的 **Interactive Tools Framework**（交互工具框架）暴露给蓝图，使得开发者无需编写 C++ 即可创建完整的编辑器交互工具。

核心解决的问题是：UE 原生的 `UInteractiveTool` 体系完全基于 C++ 虚函数，蓝图开发者无法直接接入。本插件通过提供一组 `Blueprintable` 基类（`UScriptableInteractiveTool`、`UScriptableSingleClickTool`、`UScriptableClickDragTool`、`UScriptableModularBehaviorTool`），将点击、拖拽、悬停、滚轮、键盘等输入行为全部封装为蓝图可实现的事件和可调用函数，同时提供 Property Set 机制来自动将工具设置暴露到 Details 面板，以及 3D/2D 绘制 API 来实现可视反馈。

该插件从 Experimental 迁移到 Beta，目前仍处于 Beta 状态且默认未启用。

## 使用场景

- 你需要在编辑器中快速原型化一个自定义交互工具（如自定义选择、测量、标注工具）→ 用 `UScriptableInteractiveTool` 的子类
- 你需要组合多种输入行为（点击 + 拖拽 + 快捷键）到同一个工具 → 用 `UScriptableModularBehaviorTool`
- 你需要让工具的参数自动显示在编辑器 Details 面板中 → 用 `UScriptableInteractiveToolPropertySet`
- 你需要在工具中绘制调试线条、点、三角形来提供可视反馈 → 用 `AddLineSet()` / `AddPointSet()` / `AddTriangleSet()`
- 你需要在工具面板头部或视口上叠加自定义 UMG Widget → 用 `SetToolPanelToolHeaderWidget()` / `SetOverlayWidget()`

## 蓝图用法

### 核心节点 — 工具生命周期（UScriptableInteractiveTool）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OnScriptSetup` | 工具初始化，用于添加 Property Set、创建 Gizmo 等 | `UScriptableInteractiveTool` |
| `OnScriptTick` | 每帧调用，实现逐帧处理逻辑 | `UScriptableInteractiveTool` |
| `OnScriptShutdown` | 工具关闭时调用，根据 ShutdownType 决定提交或回滚 | `UScriptableInteractiveTool` |
| `OnScriptRender` | 每帧调用，使用 RenderAPI 绘制 3D 几何体 | `UScriptableInteractiveTool` |
| `OnScriptDrawHUD` | 每帧调用，使用 DrawHUDAPI 绘制 2D HUD 元素 | `UScriptableInteractiveTool` |
| `OnScriptCanAccept` | 控制 Accept 按钮是否可用（Accept/Cancel 类型） | `UScriptableInteractiveTool` |
| `RequestToolShutdown` | 主动请求关闭工具 | `UScriptableInteractiveTool` |

### 核心节点 — 输入行为（UScriptableModularBehaviorTool）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddSingleClickBehavior` | 添加单击行为 | `UScriptableModularBehaviorTool` |
| `AddDoubleClickBehavior` | 添加双击行为 | `UScriptableModularBehaviorTool` |
| `AddClickDragBehavior` | 添加点击拖拽行为 | `UScriptableModularBehaviorTool` |
| `AddSingleClickOrDragBehavior` | 添加"单击或拖拽"组合行为 | `UScriptableModularBehaviorTool` |
| `AddMouseWheelBehavior` | 添加鼠标滚轮行为 | `UScriptableModularBehaviorTool` |
| `AddMultiClickSequenceBehavior` | 添加多击序列行为（如多边形绘制） | `UScriptableModularBehaviorTool` |
| `AddMouseHoverBehavior` | 添加鼠标悬停行为 | `UScriptableModularBehaviorTool` |
| `AddSingleKeyInputBehavior` | 添加单键监听行为（快捷键） | `UScriptableModularBehaviorTool` |
| `AddMultiKeyInputBehavior` | 添加多键组合监听行为 | `UScriptableModularBehaviorTool` |

### 核心节点 — 单击工具事件（UScriptableSingleClickTool）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `TestIfHitByClick` | 判断是否命中点击位置（返回深度用于优先级比较） | `UScriptableSingleClickTool` |
| `OnHitByClick` | 点击命中时触发 | `UScriptableSingleClickTool` |

### 核心节点 — 拖拽工具事件（UScriptableClickDragTool）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `TestIfCanBeginClickDrag` | 判断是否可以开始拖拽 | `UScriptableClickDragTool` |
| `OnDragBegin` | 拖拽开始 | `UScriptableClickDragTool` |
| `OnDragUpdatePosition` | 拖拽位置更新 | `UScriptableClickDragTool` |
| `OnDragEnd` | 拖拽结束 | `UScriptableClickDragTool` |
| `OnDragSequenceCancelled` | 拖拽序列被取消 | `UScriptableClickDragTool` |

### 核心节点 — 悬停事件（ClickDragTool / SingleClickTool 共有）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OnHoverHitTest` | 判断是否接管悬停输入 | `UScriptableClickDragTool` |
| `OnHoverBegin` | 悬停开始 | `UScriptableClickDragTool` |
| `OnHoverUpdate` | 悬停更新，返回 false 可终止悬停 | `UScriptableClickDragTool` |
| `OnHoverEnd` | 悬停结束 | `UScriptableClickDragTool` |

### 核心节点 — Property Set

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddPropertySetOfType` | 创建并附加一个 Property Set 到工具 | `UScriptableInteractiveTool` |
| `RemovePropertySetByName` | 按标识移除 Property Set | `UScriptableInteractiveTool` |
| `SetPropertySetVisibleByName` | 设置 Property Set 可见性 | `UScriptableInteractiveTool` |
| `WatchFloatProperty` | 监听 float 属性变化 | `UScriptableInteractiveTool` |
| `WatchBoolProperty` | 监听 bool 属性变化 | `UScriptableInteractiveTool` |
| `WatchIntProperty` | 监听 int 属性变化 | `UScriptableInteractiveTool` |
| `GetOwningTool` | 从 Property Set 获取所属工具 | `UScriptableInteractiveToolPropertySet` |
| `SetPropertyAsReadOnly` | 设置属性为只读 | `UScriptableInteractiveToolPropertySet` |
| `SetPropertyAsHidden` | 设置属性为隐藏 | `UScriptableInteractiveToolPropertySet` |

### 核心节点 — 绘制 API

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddLineSet` | 创建一组可绘制线条 | `UScriptableInteractiveTool` |
| `AddPointSet` | 创建一组可绘制点 | `UScriptableInteractiveTool` |
| `AddTriangleSet` | 创建一组可绘制三角形/四边形 | `UScriptableInteractiveTool` |
| `DrawLine` | 在 RenderAPI 中画线 | `UScriptableTool_RenderAPI` |
| `DrawRectWidthHeightXY` | 在 RenderAPI 中画矩形 | `UScriptableTool_RenderAPI` |
| `DrawTextAtLocation` | 在 HUD 中指定位置绘制文字 | `UScriptableTool_HUDAPI` |
| `DrawTextArrayAtLocation` | 在 HUD 中指定位置绘制多行文字 | `UScriptableTool_HUDAPI` |

### 核心节点 — Gizmo

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateTRSGizmo` | 创建平移/旋转/缩放 Gizmo | `UScriptableInteractiveTool` |
| `SetGizmoTransform` | 设置 Gizmo 变换 | `UScriptableInteractiveTool` |
| `GetGizmoTransform` | 获取 Gizmo 变换 | `UScriptableInteractiveTool` |
| `SetGizmoVisible` | 设置 Gizmo 可见性 | `UScriptableInteractiveTool` |

### 核心节点 — 修饰键 & 工具状态

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsShiftDown` | 当前是否按下 Shift | `UScriptableModularBehaviorTool` / `UScriptableClickDragTool` |
| `IsCtrlDown` | 当前是否按下 Ctrl | `UScriptableModularBehaviorTool` / `UScriptableClickDragTool` |
| `IsAltDown` | 当前是否按下 Alt | `UScriptableModularBehaviorTool` / `UScriptableClickDragTool` |
| `InActiveClickDrag` | 是否处于拖拽状态中 | `UScriptableClickDragTool` |
| `InActiveHover` | 是否处于悬停状态中 | `UScriptableClickDragTool` |
| `GetToolWorld` | 获取工具运行的世界 | `UScriptableInteractiveTool` |
| `SetFocusInViewport` | 将焦点设置到视口 | `UScriptableInteractiveTool` |

### 使用示例（蓝图描述）

**创建一个简单的点击放置工具**：

1. 创建新蓝图类，父类选择 `UScriptableSingleClickTool`
2. 在 `OnScriptSetup` 中调用 `AddPropertySetOfType` 添加自定义设置（如放置的 Actor 类型）
3. 实现 `TestIfHitByClick`：使用 `MakeInputRayHit` 返回命中结果
4. 实现 `OnHitByClick`：在命中位置 Spawn Actor
5. 在编辑器中通过工具管理器（Tool Set）注册该工具

**创建一个带拖拽的自定义工具**：

1. 创建新蓝图类，父类选择 `UScriptableModularBehaviorTool`
2. 在 `OnScriptSetup` 中调用 `AddClickDragBehavior`，绑定 `TestCanBeginClickDragSequence`、`OnClickPress`、`OnClickDrag`、`OnClickRelease` 等委托
3. 可选：调用 `AddSingleKeyInputBehavior` 为 Escape 键添加取消功能
4. 调用 `AddLineSet` / `AddPointSet` 创建绘制集合，在 `OnScriptRender` 中更新绘制内容
5. 设置 `ToolShutdownType` 为 `AcceptCancel` 以支持确认/取消模式

## C++ 用法

### 头文件引入

```cpp
#include "ScriptableInteractiveTool.h"
#include "ScriptableClickDragTool.h"
#include "ScriptableSingleClickTool.h"
#include "ScriptableModularBehaviorTool.h"
#include "ScriptableToolBuilder.h"
```

### 基本用法 — 创建自定义单击工具

从 `UScriptableSingleClickTool` 继承（来源：`Public/BaseTools/ScriptableSingleClickTool.h`）：

```cpp
#include "ScriptableSingleClickTool.h"

UCLASS()
class UMySingleClickTool : public UScriptableSingleClickTool
{
    GENERATED_BODY()

public:
    virtual void Setup() override
    {
        UScriptableSingleClickTool::Setup();
        ToolName = FText::FromString(TEXT("My Click Tool"));
        bWantMouseHover = true;
    }

    // 判断是否命中（返回深度用于优先级比较，0=总是捕获）
    virtual FInputRayHit TestIfHitByClick_Implementation(
        FInputDeviceRay ClickPos,
        const FScriptableToolModifierStates& Modifiers) override
    {
        // 返回 MaxDepth 表示不命中
        return UScriptableToolsUtilityLibrary::MakeInputRayHit_MaxDepth();
    }

    // 点击命中后执行操作
    virtual void OnHitByClick_Implementation(
        FInputDeviceRay ClickPos,
        const FScriptableToolModifierStates& Modifiers) override
    {
        // 在命中位置执行操作
    }
};
```

### 基本用法 — 创建工具 Builder

从 `UCustomScriptableToolBuilder` 继承来定义工具的启动条件和初始化逻辑（来源：`Public/ScriptableToolBuilder.h`）：

```cpp
#include "ScriptableToolBuilder.h"
#include "ScriptableInteractiveTool.h"

UCLASS()
class UMyToolBuilder : public UCustomScriptableToolBuilder
{
    GENERATED_BODY()

public:
    // 判断工具是否可以启动
    virtual bool OnCanBuildTool_Implementation(
        const TArray<AActor*>& SelectedActors,
        const TArray<UActorComponent*>& SelectedComponents) const override
    {
        // 至少选择一个 Actor 才能启动
        return SelectedActors.Num() > 0;
    }

    // 设置工具的初始状态
    virtual void OnSetupTool_Implementation(
        UScriptableInteractiveTool* Tool,
        const TArray<AActor*>& SelectedActors,
        const TArray<UActorComponent*>& SelectedComponents) const override
    {
        // 可以在此设置工具的初始参数
    }
};
```

### 进阶用法 — 创建模块化行为工具

使用 `UScriptableModularBehaviorTool` 组合多种输入行为（来源：`Public/BaseTools/ScriptableModularBehaviorTool.h`）：

```cpp
#include "ScriptableModularBehaviorTool.h"

UCLASS()
class UMyModularTool : public UScriptableModularBehaviorTool
{
    GENERATED_BODY()

public:
    virtual void Setup() override
    {
        UScriptableModularBehaviorTool::Setup();

        // 添加点击拖拽行为
        AddClickDragBehavior(
            FTestCanBeginClickDragSequenceDelegate(),   // CanBegin
            FOnClickPressDelegate(),                     // OnPress
            FOnClickDragDelegate(),                      // OnDrag
            FOnClickReleaseDelegate(),                   // OnRelease
            FOnTerminateDragSequenceDelegate(),          // OnTerminate
            FMouseBehaviorModiferCheckDelegate(),        // CaptureCheck
            100,                                         // CapturePriority
            EScriptableToolMouseButton::LeftButton       // Mouse Button
        );

        // 添加 Escape 键监听
        AddSingleKeyInputBehavior(
            FOnKeyStateToggleDelegate(),                 // OnKeyPressed
            FOnKeyStateToggleDelegate(),                 // OnKeyReleased
            FOnForceEndCaptureDelegate_ScriptableTools(),// OnForceEndCapture
            EKeys::Escape,
            FMouseBehaviorModiferCheckDelegate(),
            100
        );
    }
};
```

### 进阶用法 — 使用 Property Set

Property Set 用于将工具设置自动暴露到编辑器面板（来源：`Public/ScriptableInteractiveTool.h`）：

```cpp
#include "ScriptableInteractiveTool.h"

// 定义 Property Set（蓝图中同样可以创建子类）
UCLASS()
class UMyToolSettings : public UScriptableInteractiveToolPropertySet
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Settings")
    float Radius = 100.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Settings")
    bool bShowPreview = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Settings")
    FLinearColor PreviewColor = FLinearColor::Red;
};

// 在工具的 Setup 中添加
virtual void Setup() override
{
    UScriptableInteractiveTool::Setup();

    EToolsFrameworkOutcomePins Outcome;
    auto* Settings = AddPropertySetOfType(
        UMyToolSettings::StaticClass(),
        TEXT("MySettings"),
        Outcome
    );

    // 监听属性变化
    WatchFloatProperty(
        Cast<UMyToolSettings>(Settings),
        TEXT("Radius"),
        FToolFloatPropertyModifiedDelegate()
    );
}
```

## Demo 示例

一个最小的可编译自定义工具示例，实现点击选中 Actor 高亮显示：

```cpp
// MyHighlightTool.h
#pragma once

#include "CoreMinimal.h"
#include "ScriptableSingleClickTool.h"
#include "MyHighlightTool.generated.h"

UCLASS(Blueprintable)
class MYPROJECT_API UMyHighlightTool : public UScriptableSingleClickTool
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadWrite, EditAnywhere, Category = "Highlight")
    FLinearColor HighlightColor = FLinearColor::Yellow;

    virtual void Setup() override;

    virtual FInputRayHit TestIfHitByClick_Implementation(
        FInputDeviceRay ClickPos,
        const FScriptableToolModifierStates& Modifiers) override;

    virtual void OnHitByClick_Implementation(
        FInputDeviceRay ClickPos,
        const FScriptableToolModifierStates& Modifiers) override;

    virtual void OnHoverBegin_Implementation(
        FInputDeviceRay HoverPos,
        const FScriptableToolModifierStates& Modifiers) override;

    virtual void OnHoverEnd_Implementation(
        const FScriptableToolModifierStates& Modifiers) override;

    virtual void OnScriptShutdown_Implementation(EToolShutdownType ShutdownType) override;

private:
    UPROPERTY()
    AActor* HoveredActor = nullptr;

    UPROPERTY()
    TArray<AActor*> HighlightedActors;
};
```

```cpp
// MyHighlightTool.cpp
#include "MyHighlightTool.h"
#include "ScriptableToolsUtilityLibrary.h"
#include "Engine/World.h"
#include "Engine/OverlapResult.h"
#include "DrawDebugHelpers.h"

void UMyHighlightTool::Setup()
{
    UScriptableSingleClickTool::Setup();

    ToolName = FText::FromString(TEXT("Highlight Tool"));
    ToolCategory = FText::FromString(TEXT("Custom Tools"));
    ToolShutdownType = EScriptableToolShutdownType::AcceptCancel;
    bWantMouseHover = true;
}

FInputRayHit UMyHighlightTool::TestIfHitByClick_Implementation(
    FInputDeviceRay ClickPos,
    const FScriptableToolModifierStates& Modifiers)
{
    UWorld* World = GetToolWorld();
    if (!World)
    {
        return UScriptableToolsUtilityLibrary::MakeInputRayHit_Miss();
    }

    // 简单射线检测
    FHitResult HitResult;
    bool bHit = World->LineTraceSingleByChannel(
        HitResult,
        ClickPos.WorldRay.Origin,
        ClickPos.WorldRay.Origin + ClickPos.WorldRay.Direction * 100000.0f,
        ECC_Visibility
    );

    if (bHit && HitResult.GetActor())
    {
        return UScriptableToolsUtilityLibrary::MakeInputRayHit(
            HitResult.Distance, HitResult.GetActor());
    }

    return UScriptableToolsUtilityLibrary::MakeInputRayHit_Miss();
}

void UMyHighlightTool::OnHitByClick_Implementation(
    FInputDeviceRay ClickPos,
    const FScriptableToolModifierStates& Modifiers)
{
    UWorld* World = GetToolWorld();
    if (!World) return;

    FHitResult HitResult;
    bool bHit = World->LineTraceSingleByChannel(
        HitResult,
        ClickPos.WorldRay.Origin,
        ClickPos.WorldRay.Origin + ClickPos.WorldRay.Direction * 100000.0f,
        ECC_Visibility
    );

    if (bHit && HitResult.GetActor())
    {
        AActor* HitActor = HitResult.GetActor();
        if (IsCtrlDown())
        {
            // Ctrl+点击：取消高亮
            HighlightedActors.Remove(HitActor);
        }
        else
        {
            // 普通点击：添加到高亮列表
            HighlightedActors.AddUnique(HitActor);
        }
    }
}

void UMyHighlightTool::OnHoverBegin_Implementation(
    FInputDeviceRay HoverPos,
    const FScriptableToolModifierStates& Modifiers)
{
    HoveredActor = nullptr;
}

void UMyHighlightTool::OnHoverEnd_Implementation(
    const FScriptableToolModifierStates& Modifiers)
{
    HoveredActor = nullptr;
}

void UMyHighlightTool::OnScriptShutdown_Implementation(EToolShutdownType ShutdownType)
{
    // 清理高亮状态
    HighlightedActors.Empty();
    HoveredActor = nullptr;
}
```

## 模块依赖

从插件的 `.uplugin` 和源码结构推断的依赖关系。省略标准 Core/Engine/Slate 等常见模块。

| 模块 | 用途 |
|---|---|
| `InteractiveToolsFramework` | UE 原生交互工具框架，本插件的核心扩展对象 |
| `ToolWidgets` | 工具面板 Widget 和视口叠加支持 |

插件级依赖（`.uplugin` 中声明）：

| 插件 | 用途 |
|---|---|
| `MeshModelingToolset` | 网格建模工具集，提供基础工具类型支持 |
| `MeshModelingToolsetExp` | 网格建模工具集实验版，提供实验性工具类型支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `6cab4de5` | ScriptableTools: Refactor SDraggableBoxOverlay usage to isolate ToolWidgets dependency to Scriptable | 重构可拖拽叠加框，将 ToolWidgets 依赖隔离到 Scriptable 模块 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移为新格式 |
| 2026-02-06 | `fca152ce` | ScriptableToolsFramework: Only reference ToolWidgets if building developer tools | 仅在构建开发工具时引用 ToolWidgets 模块 |
| 2026-02-06 | `ac856ee6` | Updating tooltips to make Capture Priority values clearer. | 更新捕获优先级参数的提示文本 |
| 2026-02-04 | `80b637db` | Fixed printf format specifiers. | 修复 printf 格式化说明符 |

### 维护评价

**活跃维护中** ✅

- 创建于 2024 年 1 月，从 Experimental 迁移到 Beta（首次 commit: `1ac0d54`）
- 最近更新为 2026 年 4 月，持续有功能性改进和代码质量优化
- 多次 commit 涉及模块依赖隔离、编译兼容性修复，表明在积极适配引擎变更
- 仍标记为 `IsBetaVersion=true` 且 `EnabledByDefault=false`，说明 API 可能仍有变动
- 部分类（如 `UScriptableSingleClickTool`）标记为 `Hidden`，暗示推荐使用更灵活的 `UScriptableModularBehaviorTool` 替代方案
- 已有 deprecated 标记的属性（如 `CustomIconPath` → `ToolIconTexture`），API 仍在演进
- **推荐用于原型开发和快速迭代**，但生产环境需注意 Beta API 的潜在破坏性变更

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ScriptableToolsFramework)
- [官方文档]()（暂无）