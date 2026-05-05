# Sample Tools Editor Mode

> Sample Tools Mode includes a set of sample Tools demonstrating capabilities of the Interactive Tools Framework

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | SampleToolsEditorMode (Editor) |
| 创建时间 | 2019-04-08 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Editor/SampleToolsEditorMode) | |

## 用途

这是 Epic 官方提供的 Interactive Tools Framework **教学示例** plugin。它不是面向最终用户的工具，而是面向开发者的参考实现，展示了如何通过 `UEdMode` + `UInteractiveTool` 的模式构建自定义编辑器交互工具。

plugin 注册了一个编辑器模式（Editor Mode），进入该模式后会在工具栏中显示一组示例工具按钮。每个工具演示了 Interactive Tools Framework 的不同方面：单击输入、拖拽输入、Mesh 表面交互、属性面板绑定等。

## 使用场景

- 你想学习如何为 UE5 创建自定义 Editor Mode 和交互工具 → 参考此 plugin
- 你想了解 `USingleClickTool`、`UClickDragInputBehavior`、`UMeshSurfacePointTool` 的用法 → 此 plugin 包含这三种典型工具的完整实现
- 你想为编辑器添加自定义 3D 交互功能（测量、绘制、放置等）→ 以此为模板开始开发

## 包含的示例工具

此 plugin 注册了 4 个工具，通过编辑器模式工具栏的 Toggle 按钮切换：

### 1. Create Actor on Click（点击创建 Actor）

基于 `USingleClickTool`，演示最简单的单击交互。用户在视口中点击左键，工具通过射线检测确定点击位置，然后在该位置生成一个空的 `AActor`。

**属性面板选项：**
- **Place On Objects** (`bool`)：是否将 Actor 放置在已有物体表面（射线命中点），否则放置在地面上
- **Ground Height** (`float`)：地面高度，范围 -1000 ~ 1000

### 2. Draw Curve On Mesh（在 Mesh 上绘制曲线）

基于 `UMeshSurfacePointTool`，演示 Mesh 表面点交互。用户在选中的 Mesh 表面拖拽鼠标，工具会记录拖拽轨迹并实时渲染为一条彩色曲线。曲线仅用于展示，退出工具时丢弃。

**属性面板选项：**
- **Color** (`FLinearColor`)：曲线颜色
- **Thickness** (`float`)：线宽，范围 0.25 ~ 10.0
- **Min Spacing** (`float`)：采样点最小间距，范围 0.01 ~ 10.0
- **Offset** (`float`)：沿法线方向偏移量，范围 -1000 ~ 1000
- **Depth Bias** (`float`)：深度偏移，范围 -10.0 ~ 10.0
- **bScreenSpace** (`bool`)：是否使用屏幕空间线宽

### 3. Measure Distance（测量距离）

基于 `UInteractiveTool` + `IClickDragBehaviorTarget`，演示拖拽交互和修饰键。用户拖拽设置第一个点，按住 Shift 拖拽设置第二个点，工具实时显示两点间的距离。

**属性面板选项：**
- **StartPoint** (`FVector`)：测量起点
- **EndPoint** (`FVector`)：测量终点
- **Distance** (`float`)：当前测量距离（只读/自动更新）

### 4. Surface Point Tool（表面点工具）

直接使用框架内置的 `UMeshSurfacePointToolBuilder`，作为默认选中的工具类型。

## 蓝图用法

此 plugin 不暴露任何 `BlueprintCallable` 接口。它是一个纯 Editor 模块，所有功能通过编辑器 UI 操作。

## C++ 用法

此 plugin 的核心价值在于作为**代码参考**。以下是每个工具的关键架构模式。

### 头文件引入

```cpp
#include "Tools/UEdMode.h"
#include "InteractiveToolManager.h"
#include "InteractiveToolBuilder.h"
#include "BaseTools/SingleClickTool.h"
#include "BaseTools/MeshSurfacePointTool.h"
#include "BaseBehaviors/ClickDragBehavior.h"
```

### 创建自定义 Editor Mode

核心模式：继承 `UEdMode`，在 `Enter()` 中注册工具 Builder。

```cpp
// 来源: SampleToolsEditorMode.h / .cpp
UCLASS()
class UMyEditorMode : public UEdMode
{
    GENERATED_BODY()
public:
    const static FEditorModeID EM_MyEditorModeId;
    virtual void Enter() override;
    virtual void CreateToolkit() override;
    virtual TMap<FName, TArray<TSharedPtr<FUICommandInfo>>> GetModeCommands() const override;
};

void UMyEditorMode::Enter()
{
    UEdMode::Enter();
    // 注册工具：第一个参数是 UI 命令，第二个是工具名称字符串，第三个是 Builder 实例
    RegisterTool(MyCommands.MyTool, TEXT("MyTool"), NewObject<UMyToolBuilder>(this));
}
```

### 创建单击工具（SingleClickTool）

最简单的工具模式——点击即执行操作：

```cpp
// 来源: CreateActorSampleTool.h / .cpp
UCLASS()
class UMyToolBuilder : public UInteractiveToolBuilder
{
    GENERATED_BODY()
public:
    virtual bool CanBuildTool(const FToolBuilderState& SceneState) const override { return true; }
    virtual UInteractiveTool* BuildTool(const FToolBuilderState& SceneState) const override;
};

UCLASS()
class UMyTool : public USingleClickTool
{
    GENERATED_BODY()
public:
    virtual void Setup() override;
    virtual void OnClicked(const FInputDeviceRay& ClickPos) override;
protected:
    UPROPERTY()
    TObjectPtr<UMyToolProperties> Properties;
};

void UMyTool::Setup()
{
    USingleClickTool::Setup();
    Properties = NewObject<UMyToolProperties>(this);
    AddToolPropertySource(Properties);  // 绑定到 Details 面板
}
```

### 创建拖拽工具（ClickDragBehavior）

演示如何处理拖拽输入和修饰键：

```cpp
// 来源: MeasureDistanceSampleTool.h / .cpp
UCLASS()
class UMyDragTool : public UInteractiveTool, public IClickDragBehaviorTarget
{
    GENERATED_BODY()
public:
    virtual void Setup() override;
    // IClickDragBehaviorTarget
    virtual FInputRayHit CanBeginClickDragSequence(const FInputDeviceRay& PressPos) override;
    virtual void OnClickPress(const FInputDeviceRay& PressPos) override;
    virtual void OnClickDrag(const FInputDeviceRay& DragPos) override;
    virtual void OnClickRelease(const FInputDeviceRay& ReleasePos) override {}
    virtual void OnTerminateDragSequence() override {}
    // 修饰键支持
    virtual void OnUpdateModifierState(int ModifierID, bool bIsOn) override;
};

void UMyDragTool::Setup()
{
    UInteractiveTool::Setup();
    UClickDragInputBehavior* MouseBehavior = NewObject<UClickDragInputBehavior>();
    MouseBehavior->Modifiers.RegisterModifier(1, FInputDeviceState::IsShiftKeyDown);
    MouseBehavior->Initialize(this);
    AddInputBehavior(MouseBehavior);
}
```

### 进阶：自定义工具属性面板

通过继承 `UInteractiveToolPropertySet` 创建属性集，属性会自动出现在 Details 面板中：

```cpp
// 来源: CreateActorSampleTool.h
UCLASS(Transient)
class UMyToolProperties : public UInteractiveToolPropertySet
{
    GENERATED_BODY()
public:
    /** 在属性面板中显示的描述 */
    UPROPERTY(EditAnywhere, Category = Options, meta = (DisplayName = "My Option"))
    bool bMyOption;

    /** 带范围限制的浮点属性 */
    UPROPERTY(EditAnywhere, Category = Options, 
              meta = (UIMin = "0.0", UIMax = "100.0", ClampMin = "0.0", ClampMax = "1000.0"))
    float MyValue;
};
```

## Demo 示例

创建一个最小的自定义 Editor Mode + 单击工具：

**MySampleTool.Build.cs**
```csharp
PublicDependencyModuleNames.AddRange(new string[] { "Core" });
PrivateDependencyModuleNames.AddRange(new string[] {
    "CoreUObject", "Engine", "Slate", "SlateCore",
    "UnrealEd", "InteractiveToolsFramework", "EditorInteractiveToolsFramework"
});
```

**MySampleTool.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "BaseTools/SingleClickTool.h"
#include "MySampleTool.generated.h"

UCLASS()
class UMySampleToolBuilder : public UInteractiveToolBuilder
{
    GENERATED_BODY()
public:
    virtual bool CanBuildTool(const FToolBuilderState&) const override { return true; }
    virtual UInteractiveTool* BuildTool(const FToolBuilderState& SceneState) const override;
};

UCLASS()
class UMySampleTool : public USingleClickTool
{
    GENERATED_BODY()
public:
    void SetWorld(UWorld* World) { TargetWorld = World; }
    virtual void Setup() override;
    virtual void OnClicked(const FInputDeviceRay& ClickPos) override;
protected:
    UWorld* TargetWorld = nullptr;
};
```

**MySampleTool.cpp**
```cpp
#include "MySampleTool.h"
#include "InteractiveToolManager.h"
#include "Engine/World.h"

UInteractiveTool* UMySampleToolBuilder::BuildTool(const FToolBuilderState& SceneState) const
{
    UMySampleTool* Tool = NewObject<UMySampleTool>(SceneState.ToolManager);
    Tool->SetWorld(SceneState.World);
    return Tool;
}

void UMySampleTool::Setup() { USingleClickTool::Setup(); }

void UMySampleTool::OnClicked(const FInputDeviceRay& ClickPos)
{
    FHitResult Hit;
    FVector End = ClickPos.WorldRay.PointAt(999999);
    if (TargetWorld->LineTraceSingleByObjectType(Hit, ClickPos.WorldRay.Origin, End, 
            FCollisionObjectQueryParams(FCollisionObjectQueryParams::AllObjects)))
    {
        UE_LOG(LogTemp, Log, TEXT("Clicked at: %s"), *Hit.ImpactPoint.ToString());
    }
}
```

## 模块依赖

此 plugin 本身是示例，不建议直接依赖。如果你要创建类似的自定义 Editor Mode，你的 Build.cs 需要以下依赖：

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型和宏 |
| `CoreUObject` | UObject 系统 |
| `Engine` | World、Actor、组件等 |
| `Slate` / `SlateCore` | UI 框架 |
| `InputCore` | 输入系统 |
| `UnrealEd` | 编辑器框架（UEdMode） |
| `InteractiveToolsFramework` | 交互工具核心框架（Tool、Behavior、InputRouter） |
| `EditorInteractiveToolsFramework` | 编辑器专用的交互工具扩展 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2024-10-30 | `f2983507` | Replaced include SceneManagement.h with PrimitiveDrawingUtils.h | 头文件依赖重构，非功能性变更 |
| 2024-02-14 | `0d5635a9` | Removed some headers dependencies on FHitResult and FOverlapResult | 头文件依赖清理，非功能性变更 |
| 2024-01-30 | `681cf949` | Move SampleToolsEditorMode into Editor plugins folder | 从 Experimental 迁移到 Editor 目录，结构调整 |

### 维护评价

- **创建时间**：2019-04-08（最初位于 `Engine/Experimental` 目录）
- **最近更新**：2024 年 10 月，但都是编译依赖的调整，无功能性更新
- **最后实质性功能更新**：2019 年创建时的初始版本
- **Beta 状态**：`.uplugin` 中 `IsBetaVersion: true`
- **默认未启用**：`Installed: false`
- **总体评价**：这是一个**稳定的教学示例**，不是活跃开发的功能性工具。自 2019 年创建以来代码结构基本未变，仅随引擎 API 变化做了必要的头文件调整。Interactive Tools Framework 本身仍在活跃维护（有独立的 plugin），此示例的价值在于展示框架的基本用法。

⚠️ **注意**：此 plugin 作为教学参考仍然有效，但 Interactive Tools Framework 在后续版本中可能有新的最佳实践。建议同时参考引擎中其他使用该框架的工具（如 Modeling Tools）以了解更现代的用法。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Editor/SampleToolsEditorMode)
- [InteractiveToolsFramework plugin](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/InteractiveToolsFramework) — 此示例所演示的核心框架
- [EditorInteractiveToolsFramework](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/EditorInteractiveToolsFramework) — 编辑器专用的交互工具框架扩展
