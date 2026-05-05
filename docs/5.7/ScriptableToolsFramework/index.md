# Scriptable Tools Framework

> Blueprint-Scriptable extension to the Interactive Tools Framework

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ScriptableToolsFramework` (Runtime), `EditorScriptableToolsFramework` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-12-07 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ScriptableToolsFramework) | |

## 用途

Scriptable Tools Framework 是 UE5 Interactive Tools Framework (ITF) 的蓝图扩展层。ITF 本身是一个纯 C++ 框架，用于构建编辑器中的交互式工具（如建模模式中的各种工具）。这个 plugin 的存在意义是让开发者**无需编写 C++ 代码**就能创建交互式工具——通过蓝图子类化 `UScriptableInteractiveTool` 及其子类，即可获得完整的鼠标点击、拖拽、悬停、键盘输入、Gizmo 变换、HUD 绘制、几何体绘制等能力。

核心设计模式：每个蓝图工具是一个 `UScriptableInteractiveTool` 的子类，通过 `BlueprintImplementableEvent` 回调（如 `OnScriptSetup`、`OnScriptTick`、`OnScriptShutdown`）定义工具生命周期，通过 `BlueprintCallable` 方法注册输入行为（Behaviors）和属性集（Property Sets）。

该 plugin 从 2022 年的 Experimental 目录起步，2024 年迁移到 Runtime 目录，目前仍标记为 Beta。

## 使用场景

- 你在做关卡设计工具，需要一个"点击放置 Actor"的工具 → 子类化 `UScriptableSingleClickTool`，在 `OnHitByClick` 中 SpawnActor
- 你需要一个"拖拽移动物体"的自定义 Gizmo → 子类化 `UScriptableClickDragTool`，在 `OnDragUpdatePosition` 中更新目标位置
- 你需要一个多边形绘制工具，用户逐步点击定义顶点 → 子类化 `UScriptableModularBehaviorTool`，调用 `AddMultiClickSequenceBehavior`
- 你需要在编辑器 Mode 中创建一组带属性面板的工具 → 使用 `AddPropertySetOfType` 配合 `WatchFloatProperty` 等属性监听机制
- 你需要工具根据选中物体类型决定是否可用 → 设置 `ToolStartupRequirements` 为 `ToolTarget` 或 `Custom`，配合自定义 Builder

## 类层次结构

```
UInteractiveTool (ITF 基类)
└── UScriptableInteractiveTool                    ← 核心：蓝图可子类化的工具基类
    ├── UScriptableSingleClickTool                ← 单击工具（内置单击行为）
    │   └── UEditorScriptableSingleClickTool      ← Editor-only 变体
    ├── UScriptableClickDragTool                  ← 拖拽工具（内置拖拽行为）
    │   └── UEditorScriptableClickDragTool        ← Editor-only 变体
    └── UScriptableModularBehaviorTool            ← 模块化行为工具（运行时组合多种行为）
        └── UEditorScriptableModularBehaviorTool  ← Editor-only 变体

UInteractiveToolPropertySet
└── UScriptableInteractiveToolPropertySet         ← 蓝图可子类化的属性集
    └── UEditorScriptableInteractiveToolPropertySet

UInteractiveToolBuilder
└── UBaseScriptableToolBuilder                    ← 通用工具构建器
    └── UCustomScriptableToolBuilderContainer     ← 包装自定义 Builder 逻辑

UCustomScriptableToolBuilder                      ← 自定义 Builder（蓝图子类化）
UToolTargetScriptableToolBuilder                  ← 基于 ToolTarget 的 Builder

UScriptableToolSet                                ← 管理所有 Scriptable Tool 的发现和加载
```

### 三种工具基类的选择指南

| 基类 | 交互模式 | 适用场景 |
|---|---|---|
| `UScriptableSingleClickTool` | 单击 + 悬停 | 点击选择、放置、删除等一次性操作 |
| `UScriptableClickDragTool` | 拖拽 + 悬停 | 拖拽移动、绘制、框选等连续操作 |
| `UScriptableModularBehaviorTool` | 任意组合 | 需要同时支持多种输入（如点击+滚轮+键盘） |

## 蓝图用法

### 核心节点

#### 工具生命周期事件

| 事件 | 说明 | 所在类 |
|---|---|---|
| `OnScriptSetup` | 工具初始化，添加属性集/Gizmo/行为 | `UScriptableInteractiveTool` |
| `OnScriptTick` | 每帧调用 | `UScriptableInteractiveTool` |
| `OnScriptShutdown` | 工具关闭时调用（Accept/Cancel/Complete） | `UScriptableInteractiveTool` |
| `OnScriptCanAccept` | 返回 true 时 Accept 按钮可用 | `UScriptableInteractiveTool` |
| `OnScriptRender` | 每帧渲染 3D 几何体（线、点等） | `UScriptableInteractiveTool` |
| `OnScriptDrawHUD` | 每帧绘制 2D HUD（文字等） | `UScriptableInteractiveTool` |

#### Gizmo 相关事件

| 事件 | 说明 | 所在类 |
|---|---|---|
| `OnGizmoTransformChanged` | Gizmo 变换被修改时触发 | `UScriptableInteractiveTool` |
| `OnGizmoTransformStateChange` | Gizmo 开始/结束变换或 Undo/Redo 时触发 | `UScriptableInteractiveTool` |

#### 属性集管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddPropertySetOfType` | 创建并附加一个 PropertySet | `UScriptableInteractiveTool` |
| `RemovePropertySetByName` | 按标识符移除 PropertySet | `UScriptableInteractiveTool` |
| `SetPropertySetVisibleByName` | 设置 PropertySet 可见性 | `UScriptableInteractiveTool` |
| `ForcePropertySetUpdateByName` | 强制刷新 PropertySet（蓝图直接修改值后） | `UScriptableInteractiveTool` |
| `SavePropertySetSettings` | 保存 PropertySet 值（会话内持久化） | `UScriptableInteractiveTool` |
| `RestorePropertySetSettings` | 恢复之前保存的 PropertySet 值 | `UScriptableInteractiveTool` |

#### 属性监听（Watch）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `WatchFloatProperty` | 监听 Double 属性变化 | `UScriptableInteractiveTool` |
| `WatchIntProperty` | 监听 Int 属性变化 | `UScriptableInteractiveTool` |
| `WatchBoolProperty` | 监听 Bool 属性变化 | `UScriptableInteractiveTool` |
| `WatchEnumProperty` | 监听 Enum 属性变化（回调为 uint8） | `UScriptableInteractiveTool` |
| `WatchStringProperty` | 监听 String 属性变化 | `UScriptableInteractiveTool` |
| `WatchNameProperty` | 监听 FName 属性变化 | `UScriptableInteractiveTool` |
| `WatchObjectProperty` | 监听 UObject 属性变化 | `UScriptableInteractiveTool` |
| `WatchProperty` | 监听任意属性（含 Struct/Array，基于哈希检测） | `UScriptableInteractiveTool` |

#### Gizmo 管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateTRSGizmo` | 创建平移/旋转/缩放 Gizmo | `UScriptableInteractiveTool` |
| `DestroyTRSGizmo` | 销毁 Gizmo | `UScriptableInteractiveTool` |
| `SetGizmoVisible` | 设置 Gizmo 可见性 | `UScriptableInteractiveTool` |
| `SetGizmoTransform` | 设置 Gizmo 变换（可选 Undo 支持） | `UScriptableInteractiveTool` |
| `GetGizmoTransform` | 获取 Gizmo 当前变换 | `UScriptableInteractiveTool` |

#### 绘图 API

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetDefaultLineSet` | 获取默认线段集合 | `UScriptableInteractiveTool` |
| `AddLineSet` | 创建新的独立线段集合 | `UScriptableInteractiveTool` |
| `GetDefaultPointSet` | 获取默认点集合 | `UScriptableInteractiveTool` |
| `AddPointSet` | 创建新的独立点集合 | `UScriptableInteractiveTool` |
| `GetDefaultTriangleSet` | 获取默认三角面集合 | `UScriptableInteractiveTool` |
| `AddTriangleSet` | 创建新的独立三角面集合 | `UScriptableInteractiveTool` |
| `GetDrawableGeometryActor` | 获取拥有绘制几何体的 Actor | `UScriptableInteractiveTool` |

#### 消息与 UI

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddLogMessage` | 添加日志消息（可高亮为 Warning） | `UScriptableInteractiveTool` |
| `DisplayUserHelpMessage` | 显示底部帮助消息 | `UScriptableInteractiveTool` |
| `DisplayUserWarningMessage` | 显示警告消息 | `UScriptableInteractiveTool` |
| `ClearUserMessages` | 清除所有用户消息 | `UScriptableInteractiveTool` |
| `SetToolPanelToolHeaderWidget` | 设置工具面板头部 Widget（仅 OnScriptSetup 中有效） | `UScriptableInteractiveTool` |
| `SetOverlayWidget` | 设置视口叠加 Widget（可拖拽） | `UScriptableInteractiveTool` |
| `ClearOverlayWidget` | 清除视口叠加 Widget | `UScriptableInteractiveTool` |
| `SetFocusInViewport` | 将焦点设置到视口 | `UScriptableInteractiveTool` |

#### 工具目标与关闭

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetToolTargets` | 获取工具目标列表 | `UScriptableInteractiveTool` |
| `GetToolWorld` | 获取工具操作的 World | `UScriptableInteractiveTool` |
| `RequestToolShutdown` | 请求关闭工具（可选 Accept/Cancel 和弹窗消息） | `UScriptableInteractiveTool` |

#### 工具基类属性

| 属性 | 说明 | 所在类 |
|---|---|---|
| `ToolName` | 工具名称（显示在工具栏） | `UScriptableInteractiveTool` |
| `ToolLongName` | 工具长名称（显示在 Accept/Cancel 栏） | `UScriptableInteractiveTool` |
| `ToolCategory` | 工具分类（工具面板分组标题） | `UScriptableInteractiveTool` |
| `ToolTooltip` | 工具提示文本 | `UScriptableInteractiveTool` |
| `ToolIconTexture` | 工具图标纹理 | `UScriptableInteractiveTool` |
| `bShowToolInEditor` | 是否在编辑器中显示 | `UScriptableInteractiveTool` |
| `ToolShutdownType` | 关闭模式：Complete 或 AcceptCancel | `UScriptableInteractiveTool` |
| `ToolStartupRequirements` | 启动条件：None/ToolTarget/Custom | `UScriptableInteractiveTool` |
| `GroupTags` | 工具分组标签集合 | `UScriptableInteractiveTool` |

#### SingleClick 工具事件

| 事件 | 说明 | 所在类 |
|---|---|---|
| `TestIfHitByClick` | 测试点击是否命中（返回 FInputRayHit） | `UScriptableSingleClickTool` |
| `OnHitByClick` | 点击命中时触发 | `UScriptableSingleClickTool` |
| `OnHoverHitTest` | 测试悬停是否命中 | `UScriptableSingleClickTool` |
| `OnHoverBegin` | 悬停开始 | `UScriptableSingleClickTool` |
| `OnHoverUpdate` | 悬停更新（返回 false 停止） | `UScriptableSingleClickTool` |
| `OnHoverEnd` | 悬停结束 | `UScriptableSingleClickTool` |

#### ClickDrag 工具事件

| 事件 | 说明 | 所在类 |
|---|---|---|
| `TestIfCanBeginClickDrag` | 测试是否可以开始拖拽 | `UScriptableClickDragTool` |
| `OnDragBegin` | 拖拽开始 | `UScriptableClickDragTool` |
| `OnDragUpdatePosition` | 拖拽位置更新 | `UScriptableClickDragTool` |
| `OnDragEnd` | 拖拽结束 | `UScriptableClickDragTool` |
| `OnDragSequenceCancelled` | 拖拽序列被取消 | `UScriptableClickDragTool` |

#### ModularBehaviorTool 输入行为注册

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddSingleClickBehavior` | 注册单击行为 | `UScriptableModularBehaviorTool` |
| `AddDoubleClickBehavior` | 注册双击行为 | `UScriptableModularBehaviorTool` |
| `AddClickDragBehavior` | 注册拖拽行为 | `UScriptableModularBehaviorTool` |
| `AddSingleClickOrDragBehavior` | 注册单击或拖拽行为（阈值切换） | `UScriptableModularBehaviorTool` |
| `AddMouseWheelBehavior` | 注册鼠标滚轮行为 | `UScriptableModularBehaviorTool` |
| `AddMultiClickSequenceBehavior` | 注册多点击序列行为（如多边形绘制） | `UScriptableModularBehaviorTool` |
| `AddMouseHoverBehavior` | 注册鼠标悬停行为 | `UScriptableModularBehaviorTool` |
| `AddSingleKeyInputBehavior` | 注册单键输入行为 | `UScriptableModularBehaviorTool` |
| `AddMultiKeyInputBehavior` | 注册多键输入行为 | `UScriptableModularBehaviorTool` |

#### 修改键检测

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsShiftDown` | Shift 键是否按下 | `UScriptableModularBehaviorTool` |
| `IsCtrlDown` | Ctrl 键是否按下 | `UScriptableModularBehaviorTool` |
| `IsAltDown` | Alt 键是否按下 | `UScriptableModularBehaviorTool` |
| `GetActiveModifiers` | 获取所有修改键状态 | `UScriptableModularBehaviorTool` |

#### 绘图对象 API

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetLineStart` / `SetLineEnd` / `SetLineEndPoints` | 设置线段端点 | `UScriptableToolLine` |
| `SetLineColor` / `SetLineThickness` / `SetLineDepthBias` | 设置线段外观 | `UScriptableToolLine` |
| `AddLine` / `RemoveLine` / `RemoveAllLines` | 线段集合操作 | `UScriptableToolLineSet` |
| `SetAllLinesColor` / `SetAllLinesThickness` | 批量设置线段外观 | `UScriptableToolLineSet` |
| `SetPointPosition` / `SetPointColor` / `SetPointSize` | 设置点属性 | `UScriptableToolPoint` |
| `AddPoint` / `RemovePoint` / `RemoveAllPoints` | 点集合操作 | `UScriptableToolPointSet` |
| `SetTrianglePoints` / `SetTriangleMaterial` / `SetTriangleColors` | 设置三角面 | `UScriptableToolTriangle` |
| `SetQuadPoints` / `SetQuadMaterial` / `SetQuadColors` | 设置四边形 | `UScriptableToolQuad` |
| `AddTriangle` / `AddQuad` / `RemoveAllFaces` | 三角面集合操作 | `UScriptableToolTriangleSet` |

#### 工具属性集控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetOwningTool` | 获取所属 Tool | `UScriptableInteractiveToolPropertySet` |
| `SetPropertyAsReadOnly` | 设置属性为只读 | `UScriptableInteractiveToolPropertySet` |
| `SetPropertyAsHidden` | 设置属性为隐藏 | `UScriptableInteractiveToolPropertySet` |

#### 工具构建器事件

| 事件 | 说明 | 所在类 |
|---|---|---|
| `OnCanBuildTool` | 判断工具是否可构建（每帧调用，慎用） | `UCustomScriptableToolBuilder` |
| `OnSetupTool` | 工具构建时的额外设置 | `UCustomScriptableToolBuilder` |
| `GetToolTargetRequirements` | 返回 ToolTarget 需求 | `UToolTargetScriptableToolBuilder` |

#### 实用函数库

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MakeInputRayHit_Miss` | 创建未命中的 FInputRayHit | `UScriptableToolsUtilityLibrary` |
| `MakeInputRayHit_MaxDepth` | 创建最大深度的 FInputRayHit | `UScriptableToolsUtilityLibrary` |
| `MakeInputRayHit` | 创建指定深度的 FInputRayHit | `UScriptableToolsUtilityLibrary` |

### 使用示例（蓝图描述）

**示例 1：点击放置 Actor**

1. 创建蓝图，父类选择 `ScriptableSingleClickTool`
2. 设置 `ToolName` = "Place Actor"，`ToolShutdownType` = Complete
3. 在 `OnScriptSetup` 中：无需额外设置
4. 重写 `TestIfHitByClick`：用 `GetToolWorld` 获取 World，做射线检测，返回 `MakeInputRayHit(HitDistance, HitObject)`
5. 重写 `OnHitByClick`：从 ClickPos 提取位置，在该位置 SpawnActor
6. 在 `OnScriptRender` 中：用 RenderAPI 的 `DrawLine` 绘制预览线

**示例 2：带属性面板的拖拽工具**

1. 创建蓝图，父类选择 `ScriptableClickDragTool`
2. 创建 PropertySet 蓝图（父类 `ScriptableInteractiveToolPropertySet`），添加 `Speed` (float)、`bSnapToGrid` (bool) 等属性
3. 在 `OnScriptSetup` 中：调用 `AddPropertySetOfType` 添加 PropertySet，调用 `WatchFloatProperty` 监听 Speed 变化
4. 重写 `TestIfCanBeginClickDrag`：返回命中结果
5. 重写 `OnDragBegin`/`OnDragUpdatePosition`/`OnDragEnd`：根据属性值执行拖拽逻辑

**示例 3：模块化多边形绘制工具**

1. 创建蓝图，父类选择 `ScriptableModularBehaviorTool`
2. 在 `OnScriptSetup` 中：
   - 调用 `AddMultiClickSequenceBehavior`，绑定各回调委托
   - 调用 `CreateTRSGizmo` 添加 Gizmo
   - 调用 `GetDefaultLineSet` 获取线段集，用于绘制多边形边
3. 在 `OnBeginClickSequence` 中：记录第一个顶点
4. 在 `OnNextSequenceClick` 中：添加新顶点，更新线段集
5. 在 `OnNextSequencePreview` 中：用 `OnScriptRender` 绘制橡皮筋线
6. 在 `OnScriptShutdown` 中：清理或提交多边形

## C++ 用法

### 头文件引入

```cpp
// Runtime 模块
#include "ScriptableInteractiveTool.h"
#include "BaseTools/ScriptableSingleClickTool.h"
#include "BaseTools/ScriptableClickDragTool.h"
#include "BaseTools/ScriptableModularBehaviorTool.h"
#include "ScriptableToolBuilder.h"
#include "Behaviors/ScriptableToolBehaviorDelegates.h"

// Drawing
#include "Drawing/ScriptableToolLine.h"
#include "Drawing/ScriptableToolLineSet.h"
#include "Drawing/ScriptableToolPoint.h"
#include "Drawing/ScriptableToolPointSet.h"
#include "Drawing/ScriptableToolTriangle.h"
#include "Drawing/ScriptableToolTriangleSet.h"

// Editor 模块
#include "EditorScriptableInteractiveTool.h"
#include "ScriptableToolSet.h"
```

### 基本用法：创建 C++ 单击工具

从 `ScriptableSingleClickTool` 源码结构提取的典型用法：

```cpp
// MyClickTool.h
#pragma once
#include "BaseTools/ScriptableSingleClickTool.h"
#include "MyClickTool.generated.h"

UCLASS(Blueprintable)
class UMyClickTool : public UScriptableSingleClickTool
{
    GENERATED_BODY()
public:
    // 覆写点击命中测试
    virtual FInputRayHit TestIfHitByClick_Implementation(
        FInputDeviceRay ClickPos,
        const FScriptableToolModifierStates& Modifiers) override
    {
        // 做射线检测
        FHitResult Hit;
        if (GetToolWorld()->LineTraceSingleByChannel(Hit, ClickPos.WorldRay.Origin,
            ClickPos.WorldRay.PointAt(99999), ECC_WorldStatic))
        {
            return UScriptableToolsUtilityLibrary::MakeInputRayHit(Hit.Distance, Hit.GetActor());
        }
        return UScriptableToolsUtilityLibrary::MakeInputRayHit_Miss();
    }

    // 覆写点击处理
    virtual void OnHitByClick_Implementation(
        FInputDeviceRay ClickPos,
        const FScriptableToolModifierStates& Modifiers) override
    {
        // 在命中位置执行操作
    }
};
```

### 进阶用法：模块化行为工具 + PropertySet

从 `ScriptableModularBehaviorTool` 和 `ScriptableInteractiveTool` 源码提取：

```cpp
// MyModularTool.h
#pragma once
#include "BaseTools/ScriptableModularBehaviorTool.h"
#include "MyModularTool.generated.h"

// 自定义属性集
UCLASS(Blueprintable)
class UMyToolSettings : public UScriptableInteractiveToolPropertySet
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Settings")
    float BrushSize = 50.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Settings")
    bool bShowPreview = true;
};

// 模块化工具
UCLASS(Blueprintable)
class UMyModularTool : public UScriptableModularBehaviorTool
{
    GENERATED_BODY()
public:
    virtual void Setup() override
    {
        Super::Setup();
        // C++ 中也可以直接在 Setup 中添加行为（非蓝图方式）
    }
};
```

### 进阶用法：ToolSet 管理

```cpp
// 从 ScriptableToolSet.cpp 提取的工具发现逻辑
UScriptableToolSet* ToolSet = NewObject<UScriptableToolSet>();

// 异步加载所有 Scriptable Tool 蓝图
ToolSet->ReinitializeScriptableTools(
    FPreToolsLoadedDelegate(),   // 加载前回调
    FToolsLoadedDelegate(),      // 加载完成回调
    FToolsLoadingUpdateDelegate(), // 进度回调
    nullptr                       // 可选的 GroupTag 过滤器
);

// 遍历所有已加载工具
ToolSet->ForEachScriptableTool(
    [](UClass* ToolClass, UBaseScriptableToolBuilder* Builder)
    {
        // 处理每个工具类
    }
);
```

## Demo 示例

### 最小可编译示例：Blueprint-Style Single Click Tool

**Build.cs 依赖：**
```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "ScriptableToolsFramework",
    "InteractiveToolsFramework"
});
```

**MinimalClickTool.h：**
```cpp
#pragma once
#include "BaseTools/ScriptableSingleClickTool.h"
#include "ScriptableToolsUtilityLibrary.h"
#include "MinimalClickTool.generated.h"

UCLASS(Blueprintable, DisplayName = "Minimal Click Tool")
class UMinimalClickTool : public UScriptableSingleClickTool
{
    GENERATED_BODY()
public:
    UMinimalClickTool()
    {
        ToolName = FText::FromString(TEXT("Minimal Click Tool"));
        ToolShutdownType = EScriptableToolShutdownType::Complete;
    }

    virtual void OnScriptSetup_Implementation() override
    {
        // 设置悬停支持
        bWantMouseHover = true;
    }

    virtual FInputRayHit TestIfHitByClick_Implementation(
        FInputDeviceRay ClickPos,
        const FScriptableToolModifierStates& Modifiers) override
    {
        return UScriptableToolsUtilityLibrary::MakeInputRayHit_MaxDepth();
    }

    virtual void OnHitByClick_Implementation(
        FInputDeviceRay ClickPos,
        const FScriptableToolModifierStates& Modifiers) override
    {
        UE_LOG(LogTemp, Log, TEXT("Clicked at: %s"), *ClickPos.WorldRay.PointAt(1000).ToString());
        RequestToolShutdown(true, false, FText::GetEmpty());
    }

    virtual void OnScriptRender_Implementation(
        UScriptableTool_RenderAPI* RenderAPI) override
    {
        // 在原点画一条红色线
        RenderAPI->DrawLine(FVector::ZeroVector, FVector(100, 0, 0),
            FLinearColor::Red, 2.0f);
    }
};
```

### Editor 模块示例

**Build.cs 依赖（Editor 模块）：**
```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "ScriptableToolsFramework",
    "EditorScriptableToolsFramework",
    "InteractiveToolsFramework"
});
```

```cpp
// 使用 Editor-only 变体以获得编辑器蓝图函数访问权限
UCLASS(Blueprintable)
class UMyEditorTool : public UEditorScriptableSingleClickTool
{
    GENERATED_BODY()
    // 现在可以访问 Editor-only 的蓝图函数
};
```

## 模块依赖

### ScriptableToolsFramework (Runtime) 模块

| 模块 | 用途 |
|---|---|
| `Core` | 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `PhysicsCore` | 物理核心（射线检测等） |
| `RenderCore` | 渲染核心（绘制 API） |
| `GeometryCore` | 几何核心（点/线/三角面数据结构） |
| `InputCore` | 输入核心（按键定义） |
| `InteractiveToolsFramework` | ITF 基础框架（UInteractiveTool 等基类） |
| `ModelingComponents` | 建模组件（LineSetComponent/PointSetComponent 等） |
| `UMG` | UI 框架（Widget 支持） |

### EditorScriptableToolsFramework (Editor) 模块

| 模块 | 用途 |
|---|---|
| `Core` | 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `PhysicsCore` | 物理核心 |
| `RenderCore` | 渲染核心 |
| `GeometryCore` | 几何核心 |
| `InteractiveToolsFramework` | ITF 基础框架 |
| `ScriptableToolsFramework` | Runtime 模块（基类定义） |

### Plugin 依赖

| Plugin | 用途 |
|---|---|
| `MeshModelingToolset` | 网格建模工具集 |
| `MeshModelingToolsetExp` | 网格建模工具集实验版 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-09-30 | `90b191b9` | Fix LogTemp usage, add ScriptableTools log category | 将日志从 LogTemp 迁移到专用 `LogScriptableTools` 分类，非高亮消息现在也输出到控制台 |
| 2025-09-30 | `df5024b6` | Fixed tooltip typo | 文档修正 |
| 2025-09-30 | `8640e5b5` | Fixed AddSingleClickBehavior/AddDoubleClickBehavior tooltip error | 修正函数工具提示中的描述错误 |

### 维护评价

- **年龄**: 约 3 年（2022-12 创建），仍属于较新的 plugin
- **Beta 状态**: `.uplugin` 中 `IsBetaVersion=true`，API 可能在未来版本中发生变化
- **默认禁用**: `EnabledByDefault=false`，需要在项目设置中手动启用
- **近期活跃度**: 最近一次更新在 2025-09-30，属于文档和日志修正，非功能性更新
- **API 稳定性**: 从 5.6 开始有 deprecated 标记（如 `CustomIconPath` → `ToolIconTexture`，`SetLineSet` 等组件引用改为 WeakPtr），说明 API 正在逐步演进
- **无测试用例**: 插件目录内没有发现自动化测试文件
- **推荐程度**: ⚠️ 适合原型开发和内部工具，生产环境需注意 Beta 风险。框架设计合理，蓝图友好度高，但 API 可能在未来版本变动

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ScriptableToolsFramework)
- 官方文档（无，.uplugin 中 DocsURL 为空）
