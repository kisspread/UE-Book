# Motion Design

> Compositing, designer and broadcasting tool.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、场景模板、测试资源） |
| 模块 | `Avalanche` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheCamera` (Runtime), `AvalancheShapes` (Runtime), `AvalancheText` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheViewport` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheFunctionalTest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Motion Design（原名 Avalanche）是 UE5 虚拟制片管线中的**运动图形/动态设计**工具集。它为广播、现场活动和虚拟制片提供了一套完整的 2D/3D 动态图形创作工作流，涵盖以下核心能力：

- **场景设计**：内置几何体生成器（立方体、球体、圆柱、平面、穹顶等）、3D 文本、SVG 导入，无需外部建模工具即可快速构建运动图形场景
- **材质设计**：集成 Dynamic Material 系统，支持在编辑器内通过可视化节点图创建和编辑动态材质
- **克隆与效果器**：类似 Cinema 4D 的克隆器/效果器系统，可对 Actor 进行阵列复制并用效果器驱动变形动画
- **序列与时间线**：内置 Motion Design Sequencer，支持时间线动画、过渡逻辑和节目播出控制（Rundown）
- **场景大纲树**：专用的 Motion Design Outliner，支持层级管理、锁定、场景预设（Scene Rig）保存与加载
- **远程控制**：集成 Remote Control 框架，支持外部设备实时控制场景参数
- **遮罩系统**：几何遮罩（Geometry Mask），用于实现复杂的合成和裁剪效果
- **属性动画器**：通过节点堆栈（Operator Stack）对 Actor 属性进行程序化动画驱动
- **MRQ 集成**：与 Movie Render Queue 深度集成，支持离线渲染运动图形序列
- **播出控制**：支持页面加载、场景切换、过渡动画，面向现场直播和节目播出场景

该插件从 `/Engine/Plugins/Experimental` 迁移到 `/Engine/Plugins/VirtualProduction`，标志着其从实验性功能升级为虚拟制片的正式组成部分。

## 使用场景

- 你需要为广播/直播节目创建动态图形（Lower Third、Logo 动画、转场） → 使用 Motion Design 的形状、文本和序列系统
- 你在虚拟制片中需要快速搭建 LED 墙内容 → 使用内置几何体工具和材质设计
- 你需要类似 Cinema 4D 的 MoGraph 克隆阵列效果 → 使用 ClonerEffector 系统
- 你要对大量 Actor 进行批量重命名 → 使用 Advanced Renamer 集成
- 你需要通过外部设备（OSC/MIDI）实时控制场景参数 → 使用 Remote Control 集成
- 你要为演出设计场景过渡和节目编排 → 使用 Transition 系统和 Rundown 页面管理
- 你需要将 SVG 矢量图形导入为 3D 场景元素 → 使用 SVG Importer 集成
- 你需要对 Actor 属性进行程序化动画驱动（如随机化、噪声） → 使用 Property Animator 和 Operator Stack

## 蓝图用法

Motion Design 的大部分功能通过编辑器 UI 和命令系统暴露，蓝图可访问的 API 主要集中在设置和子系统层面。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `bEnableLevelContextSwitching` | 控制是否允许在不同 Level 之间切换设计上下文 | `UAvaEditorSettings` |
| `bAutoIncludeAttachedActorsInEditActions` | 剪切/复制/粘贴时是否自动包含附属 Actor | `UAvaEditorSettings` |
| `bKeepRelativeTransformWhenGrouping` | 分组时是否保持 Actor 的相对变换 | `UAvaEditorSettings` |
| `CameraDistance` | 新建 Actor 距离摄像机的距离（单位：厘米） | `UAvaEditorSettings` |
| `bAutoActivateMotionDesignViewport` | 打开 Motion Design Level 时是否自动切换到专用视口 | `UAvaEditorSettings` |
| `DefaultViewportQualitySettings` | 新建 Motion Design 蓝图的默认视口质量设置 | `UAvaEditorSettings` |
| `ViewportQualitySettingsPresets` | 视口质量设置的用户预设列表 | `UAvaEditorSettings` |

### 编辑器命令

Motion Design 在编辑器中注册了大量快捷命令，通过 `FAvaEditorCommands` 管理：

| 命令组 | 说明 |
|---|---|
| 视口切换 | 在 2D 和 3D 视口之间切换 |
| 分组/解组 | 通过 Null Actor 对选中 Actor 进行分组 |
| 轴心点设置 | 9 个平面位置 + 3 个深度位置，支持单个 Actor、Actor 及子项、选区三种模式 |
| 静态网格工具 | 一键创建 Cube、Sphere、Cylinder、Cone、Plane、Cyclorama |
| 摄像机工具 | 快速创建 Camera、CineCamera、Crane、Rail、Shake Source 等 |
| 灯光工具 | 快速创建 Point、Directional、Spot、Rect、Sky Light |
| 克隆效果器 | 启用/禁用克隆器和效果器，创建新克隆器 |

### 使用示例（蓝图描述）

**配置编辑器行为**：在 Project Settings → Plugins → Motion Design → Editor 中，可以设置 `bAutoActivateMotionDesignViewport` 为 true，这样打开包含 Motion Design 场景的 Level 时会自动进入专用视口。设置 `CameraDistance` 控制从工具箱拖入新 Actor 时的默认放置距离。

**调整视口质量**：通过 `DefaultViewportQualitySettings` 设置新创建的 Motion Design 蓝图的渲染质量，也可以创建自定义预设（`ViewportQualitySettingsPresets`）以快速在不同质量等级之间切换。

## C++ 用法

### 头文件引入

```cpp
#include "IAvaEditor.h"
#include "IAvaEditorModule.h"
#include "AvaEditorSettings.h"
#include "AvaEditorCommands.h"
#include "AvaSelectionProviderSubsystem.h"
#include "AvaBoundsProviderSubsystem.h"
```

### 基本用法：设置 Actor 轴心点

以下代码演示如何使用 `FAvaPivotSetOperation` 将选中 Actor 的轴心点设置到指定位置。

```cpp
// 来源: Source/AvalancheEditor/Private/Selection/AvaPivotSetOperation.h

UWorld* World = GEditor->GetEditorWorldContext().World();

// 定义轴心点设置回调：将轴心点设到边界框中心
FAvaPivotSetOperation::PivotSetCallbackType PivotCallback = [](const FBox& InBounds, FVector& OutPivot)
{
    OutPivot = InBounds.GetCenter();
};

// 创建轴心点操作，以选区整体边界为基准
FAvaPivotSetOperation PivotOp(World, EAvaPivotBoundsType::Selection, PivotCallback);
PivotOp.SetPivot();
```

`EAvaPivotBoundsType` 支持三种模式：
- `Actor`：基于单个 Actor 的边界
- `ActorAndChildren`：基于 Actor 及其所有子项的边界
- `Selection`：基于整个选区的边界

### 基本用法：访问编辑器设置

```cpp
// 来源: Source/AvalancheEditor/Private/AvaEditorSettings.h

// 获取编辑器设置单例
UAvaEditorSettings* Settings = UAvaEditorSettings::Get();

// 读取配置
float SpawnDistance = Settings->CameraDistance;
bool bAutoSwitch = Settings->bAutoActivateMotionDesignViewport;

// 修改配置（持久化到 EditorPerProjectUserSettings）
Settings->bKeepRelativeTransformWhenGrouping = true;
Settings->CameraDistance = 800.0f;
Settings->SaveConfig();
```

### 基本用法：注册编辑器命令

```cpp
// 来源: Source/AvalancheEditor/Private/AvaEditorCommands.h

// 注册所有 Motion Design 编辑器命令
FAvaEditorCommands::Register();

// 绑定视口切换命令到 CommandList
CommandList->MapAction(
    FAvaEditorCommands::Get().SwitchViewports,
    FExecuteAction::CreateLambda([this]() { OnSwitchViewports(); }),
    FCanExecuteAction()
);

// 绑定工具命令
CommandList->MapAction(
    FAvaEditorCommands::Get().CubeTool,
    FExecuteAction::CreateLambda([this]() { SpawnToolActor(EAvaToolType::Cube); }),
    FCanExecuteAction()
);
```

### 进阶用法：自定义编辑器扩展

Motion Design 编辑器基于扩展架构，可以通过继承 `FAvaEditorExtension` 来添加自定义功能。

```cpp
// 参考: Source/AvalancheEditor/Private/Outliner/AvaOutlinerExtension.h
// 参考: Source/AvalancheEditor/Private/Sequencer/AvaSequencerExtension.h

class FMyCustomExtension : public FAvaEditorExtension
{
public:
    UE_AVA_INHERITS(FMyCustomExtension, FAvaEditorExtension);

    virtual void Activate() override
    {
        // 扩展激活时的初始化逻辑
    }

    virtual void Deactivate() override
    {
        // 扩展停用时的清理逻辑
    }

    virtual void BindCommands(const TSharedRef<FUICommandList>& InCommandList) override
    {
        // 绑定自定义命令
    }

    virtual void ExtendToolbarMenu(UToolMenu& InMenu) override
    {
        // 向 Motion Design 工具栏添加自定义菜单项
    }

    virtual void NotifyOnSelectionChanged(const FAvaEditorSelection& InSelection) override
    {
        // 响应选区变化
    }
};
```

### 进阶用法：使用向量属性定制器

```cpp
// 来源: Source/AvalancheEditor/Private/DetailView/Customizations/AvaVectorPropertyTypeCustomization.h

// FAvaVectorPropertyTypeCustomization 提供了带比例锁定的向量编辑器
// 支持 Free、Lock XY、Lock YZ、Lock XZ、Lock XYZ 模式
// 通过属性元数据 "AllowPreserveRatio" 启用

// 在属性定义中使用：
UPROPERTY(EditAnywhere, meta = (AllowPreserveRatio))
FVector MyVector;
```

## Demo 示例

以下示例展示如何创建一个简单的 Motion Design 编辑器扩展，监听选区变化并操作轴心点。

```cpp
// MyMotionDesignExtension.h
#pragma once

#include "IAvaEditorExtension.h"

class FMyMotionDesignExtension : public FAvaEditorExtension
{
public:
    UE_AVA_INHERITS(FMyMotionDesignExtension, FAvaEditorExtension);

    virtual void Activate() override;
    virtual void Deactivate() override;
    virtual void NotifyOnSelectionChanged(const FAvaEditorSelection& InSelection) override;

    void CenterPivotOnSelection();

private:
    void LogSelectedActors(const FAvaEditorSelection& InSelection);
};
```

```cpp
// MyMotionDesignExtension.cpp
#include "MyMotionDesignExtension.h"
#include "Selection/AvaPivotSetOperation.h"
#include "AvaSelectionProviderSubsystem.h"
#include "AvaBoundsProviderSubsystem.h"

void FMyMotionDesignExtension::Activate()
{
    UE_LOG(LogTemp, Log, TEXT("MyMotionDesignExtension activated"));
}

void FMyMotionDesignExtension::Deactivate()
{
    UE_LOG(LogTemp, Log, TEXT("MyMotionDesignExtension deactivated"));
}

void FMyMotionDesignExtension::NotifyOnSelectionChanged(const FAvaEditorSelection& InSelection)
{
    LogSelectedActors(InSelection);
}

void FMyMotionDesignExtension::LogSelectedActors(const FAvaEditorSelection& InSelection)
{
    UE_LOG(LogTemp, Log, TEXT("Motion Design selection changed: %d actors"),
        InSelection.GetSelectedActors().Num());
}

void FMyMotionDesignExtension::CenterPivotOnSelection()
{
    UWorld* World = GEditor->GetEditorWorldContext().World();
    if (!World)
    {
        return;
    }

    // 将选区轴心点设置到边界框中心
    FAvaPivotSetOperation PivotOp(
        World,
        EAvaPivotBoundsType::Selection,
        [](const FBox& InBounds, FVector& OutPivot)
        {
            OutPivot = InBounds.GetCenter();
        }
    );
    PivotOp.SetPivot();
}
```

## 模块依赖

Motion Design 是一个重度集成的插件，依赖大量其他 UE 插件和模块。以下列出其**独特依赖**（不含标准 Core/Engine/Slate）：

| 模块 | 用途 |
|---|---|
| `AdvancedRenamer` | Actor 批量重命名工具 |
| `CustomDetailsView` | 自定义细节面板布局 |
| `DynamicMaterial` | 动态材质系统（可视化材质编辑器） |
| `GeometryCache` | 几何缓存支持 |
| `GeometryScripting` | 几何脚本操作 |
| `MediaCompositing` | 媒体合成 |
| `MediaIOFramework` | 媒体 I/O 框架 |
| `MeshModelingToolsetExp` | 网格建模工具集（实验性） |
| `RemoteControl` | 远程控制框架（OSC/MIDI 等） |
| `SVGImporter` | SVG 矢量图形导入 |
| `Text3D` | 3D 文本渲染 |
| `ActorModifierCore` | Actor 修改器核心框架 |
| `ClonerEffector` | 克隆器/效果器系统 |
| `GeometryMask` | 几何遮罩系统 |
| `OperatorStack` | 运算符堆栈（程序化节点编辑） |
| `PropertyAnimator` / `PropertyAnimatorCore` | 属性动画器 |
| `MaterialDesigner` | 材质设计工具 |
| `StormSync` / `StormSyncMotionDesignBridge` | 场景同步 |

## 模块结构概览

此插件包含 **43 个模块**，按功能域组织为 Runtime/Editor 成对模块：

| 功能域 | Runtime 模块 | Editor 模块 | 说明 |
|---|---|---|---|
| 核心 | `Avalanche`, `AvalancheCore` | `AvalancheEditor`, `AvalancheEditorCore` | 主模块和编辑器核心 |
| 形状 | `AvalancheShapes` | `AvalancheShapesEditor` | 几何体生成器（Cube、Sphere 等） |
| 文本 | `AvalancheText` | `AvalancheTextEditor` | 3D 文本支持 |
| 媒体 | `AvalancheMedia` | `AvalancheMediaEditor` | 媒体播放与合成 |
| 大纲 | `AvalancheOutliner` | — | Motion Design 专用场景大纲 |
| 序列 | `AvalancheSequence`, `AvalancheSequencer` | — | 时间线和序列编辑 |
| 修改器 | `AvalancheModifiers` | `AvalancheModifiersEditor` | Actor 属性修改器 |
| 效果器 | `AvalancheEffectors` | `AvalancheEffectorsEditor` | 克隆效果器 |
| 遮罩 | `AvalancheMask` | `AvalancheMaskEditor` | 几何遮罩系统 |
| 材质 | `AvalancheMaterial` | — | 材质管理 |
| MRQ | `AvalancheMRQ` | `AvalancheMRQEditor` | Movie Render Queue 集成 |
| 远程控制 | `AvalancheRemoteControl` | `AvalancheRemoteControlEditor` | 远程控制集成 |
| 场景预设 | `AvalancheSceneRig`, `AvalancheSceneTree` | `AvalancheSceneRigEditor` | 场景预设和场景树 |
| 过渡 | `AvalancheTransition` | `AvalancheTransitionEditor` | 场景过渡逻辑 |
| 属性动画 | `AvalanchePropertyAnimator` | `AvalanchePropertyAnimatorEditor` | 属性动画器 |
| 视口 | `AvalancheViewport`, `AvalancheLevelViewport` | — | 专用视口系统 |
| 标签 | `AvalancheTag` | `AvalancheTagEditor` | Actor 标签管理 |
| SVG | — | `AvalancheSVGEditor` | SVG 导入编辑器 |
| 相机 | `AvalancheCamera` | — | 相机管理 |
| 属性 | `AvalancheAttribute` | `AvalancheAttributeEditor` | 自定义属性系统 |
| 可视化 | `AvalancheComponentVisualizers` | — | 组件可视化器 |
| 测试 | `AvalancheFunctionalTest` | — | 功能测试 |
| 交互工具 | `AvalancheInteractiveTools`, `AvalancheInteractiveToolsRuntime` | — | 交互式编辑工具 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将场景设置和大纲标签页移至独立分组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 使用 Rundown 页面设置时新增 MRQ 分析数据收集 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 新增页面加载选项（全部/下一个/选中）到播出控制工具栏 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增项目设置以强制禁用 Text3D 和形状的碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联/取消关联的通知机制 |

### 维护评价

**活跃维护** ⭐⭐⭐⭐⭐

Motion Design 是 Epic Games 重点维护的虚拟制片核心工具。从近期提交记录看：

- **更新频率极高**：几乎每天都有功能更新和改进提交
- **功能持续扩展**：不断新增页面加载选项、MRQ 分析、碰撞控制等新功能
- **架构持续优化**：定期进行代码重构（如视口通知机制）
- **从实验性正式毕业**：2025 年 5 月从 Experimental 迁移到 VirtualProduction，表明 Epic 认为其已达到生产就绪状态
- **模块化设计良好**：43 个模块按 Runtime/Editor 成对组织，职责清晰

**推荐使用**：对于虚拟制片、广播动态图形、LED 墙内容制作场景，强烈推荐使用。该插件是 UE5 运动图形工作流的事实标准。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/motion-design-in-unreal-engine/)