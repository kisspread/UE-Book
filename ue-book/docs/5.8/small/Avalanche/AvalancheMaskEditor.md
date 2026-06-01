# Motion Design

> Compositing, designer and broadcasting tool.
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、编辑器工具） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 文档结构

本插件包含 **42+ 个模块**，源码规模超过 2000 个文件，属于 **xlarge** 级别。以下为各子模块文档索引：

| 子模块 | 文档 |
|---|---|
| [AvalancheMaskEditor](./AvalancheMaskEditor.md) | 遮罩编辑器模块 |

---

# AvalancheMaskEditor

## 用途

AvalancheMaskEditor 是 Motion Design 插件中负责 **几何遮罩（Geometry Mask）可视化与编辑** 的编辑器模块。

在虚拟制片和动态图形设计中，创作者经常需要将几何形状用作遮罩来控制材质、特效或渲染管线中的可见性区域。该模块提供了一个专用的 **编辑器模式（Editor Mode）**，让用户可以在视口中直观地：
- 预览当前场景中所有几何遮罩的渲染效果
- 选择并编辑特定 Actor 上的遮罩修饰器（Mask Modifier）
- 隔离查看某个遮罩的独立效果
- 启用/禁用单个遮罩进行 A/B 对比

该模块通过 Scene View Extension 在渲染管线中注入后处理材质，实现编辑器内的实时遮罩可视化。

## 使用场景

- 你在使用 Motion Design 创建动态图形，需要将一个形状 Actor 用作材质遮罩 → 启用 Mask Editor Mode 进行可视化调试
- 你需要检查场景中多个遮罩的叠加效果 → 使用"显示所有遮罩"功能
- 你需要单独调整某个 Actor 的遮罩属性 → 选中该 Actor 后使用"隔离选中遮罩"功能
- 你在调试遮罩问题，想临时禁用某个遮罩查看无遮罩的效果 → 使用"启用/禁用选中遮罩"功能

## 蓝图用法

本模块主要为编辑器模式（Editor Mode），大部分功能通过编辑器 UI 和快捷键操作，不暴露为蓝图节点。

### 核心编辑器命令

| 命令 | 说明 | 所在类 |
|---|---|---|
| `ToggleMaskMode` | 切换遮罩编辑器模式的启用/禁用 | `FAvaMaskEditorCommands` |
| `ShowVisualizeMasks` | 显示遮罩可视化预览窗口 | `UAvaMaskEditorSubsystem` |
| `ToggleShowAllMasks` | 切换是否显示场景中所有遮罩 | `UAvaMaskEditorSubsystem` |
| `ToggleIsolateMask` | 切换是否只显示选中 Actor 的遮罩 | `UAvaMaskEditorSubsystem` |
| `ToggleEnableMask` | 切换是否启用选中 Actor 的遮罩 | `UAvaMaskEditorSubsystem` |

### 使用流程

1. 在编辑器菜单栏中启用 "Motion Design Masking" 编辑器模式
2. 在场景中选中一个 Actor
3. 该 Actor 上的 `UAvaMask2DBaseModifier` 组件会在预览窗口中显示
4. 使用快捷键或菜单切换显示/隔离/启用状态

## C++ 用法

### 头文件引入

```cpp
#include "IAvaMaskEditor.h"
```

### 编辑器模式名称

```cpp
// 获取 Motion Design 遮罩编辑器模式的名称标识
FName MaskEditorModeName = UE::AvaMaskEditor::MotionDesignMaskEditorModeName;
// 等价于 FName("EditMode.MotionDesignMask")
```

来源: `Public/IAvaMaskEditor.h`

### 自定义细节面板

```cpp
#include "Details/AvaMask2DModifierDetails.h"

// 在模块启动时注册自定义细节面板
FPropertyEditorModule& PropertyModule = 
    FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");

PropertyModule.RegisterCustomClassLayout(
    UAvaMask2DBaseModifier::StaticClass()->GetFName(),
    FOnGetDetailCustomizationInstance::CreateStatic(
        &FAvaMask2DModifierDetails::MakeInstance)
);
```

来源: `Private/Details/AvaMask2DModifierDetails.h`

## Demo 示例

### 遮罩编辑器模式使用

```cpp
// MyActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyActor.generated.h"

/**
 * 演示如何通过 C++ 切换遮罩编辑器模式
 */
UCLASS()
class AMyMaskEditorActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMaskEditorActor();

    /** 编程式地进入遮罩编辑器模式 */
    UFUNCTION(BlueprintCallable, Category = "Motion Design|Mask")
    static void EnterMaskEditorMode();

    /** 编程式地退出遮罩编辑器模式 */
    UFUNCTION(BlueprintCallable, Category = "Motion Design|Mask")
    static void ExitMaskEditorMode();
};
```

```cpp
// MyActor.cpp
#include "MyActor.h"
#include "IAvaMaskEditor.h"
#include "EditorModeManager.h"

AMyMaskEditorActor::AMyMaskEditorActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMaskEditorActor::EnterMaskEditorMode()
{
    if (GLevelEditorModeTools().IsModeActive(
        UE::AvaMaskEditor::MotionDesignMaskEditorModeName))
    {
        return; // 已在该模式中
    }
    GLevelEditorModeTools().ActivateMode(
        UE::AvaMaskEditor::MotionDesignMaskEditorModeName);
}

void AMyMaskEditorActor::ExitMaskEditorMode()
{
    GLevelEditorModeTools().DeactivateMode(
        UE::AvaMaskEditor::MotionDesignMaskEditorModeName);
}
```

## 模块依赖

从模块信息和源码分析，AvalancheMaskEditor 依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `GeometryMask` | 几何遮罩核心功能（Canvas、Mask 实现） |
| `AvalancheMask` | Motion Design 遮罩运行时模块 |
| `AvalancheModifiers` | Motion Design 修饰器系统 |
| `AvalancheEditorCore` | Motion Design 编辑器核心工具 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将 Motion Design 标签页（场景设置、大纲）移至独立分组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 使用 Rundown 页面设置时增加 MRQ 分析功能 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 为节目控制工具栏添加页面加载选项（全部、下一个、选中） |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加项目设置以强制禁用 Text3D 和形状的碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口：重构客户端关联/解除关联通知逻辑 |

### 维护评价

- **活跃维护**: 最近一周内有多个功能性更新，开发非常活跃
- 插件于 2025 年 5 月从 Experimental 迁移至 VirtualProduction，表明 Epic 认为其已达到生产就绪状态
- 作为 Virtual Production 领域的核心工具，持续获得 Epic 工程团队的支持
- 2060 个源文件、42+ 模块的规模说明这是一个大型、成熟的插件系统
- **推荐使用**: 适合虚拟制片和动态图形工作流

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [AvalancheMaskEditor 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheMaskEditor)