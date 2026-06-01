# Avalanche Effectors Editor

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 特效编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AvalancheEffectorsEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheEffectorsEditor) | |

## 用途

AvalancheEffectorsEditor 是 Motion Design（Avalanche）插件中负责**克隆器（Cloner）和特效器（Effector）编辑器功能**的模块。它为这两种虚拟制片核心组件提供：

1. **可视化器（Component Visualizer）**：在视口中直接操控 Cloner 的间距（Spacing）和 Effector 的影响区域（Zone），支持拖拽句柄进行实时调整
2. **交互式创建工具**：通过工具栏按钮在场景中放置 Cloner 和 Effector Actor
3. **大纲栏上下文菜单**：在 Motion Design 大纲栏中为 Cloner/Effector 提供右键操作菜单
4. **编辑器命令与样式**：注册工具栏命令和 Slate 样式资源

此模块是 Motion Design 工作流中创建和编辑动态图形效果的核心编辑器支撑。

## 使用场景

- 你在 Motion Design 中使用克隆器批量复制物体，需要在视口中直观调整间距 → Cloner 可视化器
- 你需要放置一个特效器来影响克隆器阵列中的物体（如缩放、旋转、颜色变化）→ Effector 可视化器与交互工具
- 你想在大纲栏中对 Cloner/Effector 进行批量操作 → 右键上下文菜单扩展
- 你想通过工具栏按钮快速在场景中创建 Cloner/Effector → 交互式工具

## 蓝图用法

本模块主要为编辑器扩展模块，不暴露蓝图 API。核心功能通过编辑器 UI 交互访问：

### 核心可视化器

| 组件 | 可视化器 | 说明 |
|---|---|---|
| `UCEClonerComponent` | `FAvaClonerActorVisualizer` | 视口中显示间距句柄，拖拽可调整各轴间距 |
| `UCEEffectorComponent` | `FAvaEffectorActorVisualizer` | 视口中显示影响区域句柄，支持内/外半径、范围、角度等 |

### Effector 区域句柄类型

| 句柄类型 | 常量 | 说明 |
|---|---|---|
| 内区域 | `HandleTypeInnerZone` (0) | 调整 Effector 内部影响半径 |
| 外区域 | `HandleTypeOuterZone` (1) | 调整 Effector 外部影响半径/范围 |
| 半径 | `HandleTypeRadius` (2) | 调整环形/径向半径参数 |
| 角度 | `HandleTypeAngle` (3) | 调整径向角度参数 |

### 使用示例（编辑器操作）

1. 通过 Motion Design 工具栏选择 **Cloner** 工具 → 在视口中点击放置 Cloner Actor
2. 通过 Motion Design 工具栏选择 **Effector** 工具 → 在视口中点击放置 Effector Actor
3. 选中 Cloner → 视口中出现间距句柄（X/Y/Z 轴）→ 拖拽调整实例间距
4. 选中 Effector → 视口中出现区域句柄 → 拖拽调整影响范围

## C++ 用法

### 头文件引入

```cpp
#include "AvaEffectorsEditorCommands.h"
#include "AvaEffectorsEditorStyle.h"
```

### 基本用法 — 注册编辑器命令

来自 `AvaEffectorsEditorCommands.h`：

```cpp
// 获取已注册的 Cloner/Effector 工具命令
FAvaEffectorsEditorCommands& Commands = FAvaEffectorsEditorCommands::Get();

// 通过工具名称获取特定命令
TSharedPtr<FUICommandInfo> ClonerCommand = Commands.Tool_Actor_Cloners[ToolName];
TSharedPtr<FUICommandInfo> EffectorCommand = Commands.Tool_Actor_Effectors[ToolName];
```

### 基本用法 — 获取编辑器样式

来自 `AvaEffectorsEditorStyle.h`：

```cpp
// 获取 Motion Design 特效编辑器样式集
FSlateStyleSet& StyleSet = FAvaEffectorsEditorStyle::Get();

// 使用样式中的 Brush/Font 等资源
const FSlateBrush* Brush = StyleSet.GetBrush("BrushName");
```

### 进阶用法 — 自定义组件可视化器

来自 `Effector/AvaEffectorActorVis.h`，展示如何扩展可视化器：

```cpp
// 继承 FAvaVisualizerBase 创建自定义可视化器
class FMyCustomVisualizer : public FAvaVisualizerBase
{
public:
    // 重写关键虚函数
    virtual UActorComponent* GetEditedComponent() const override;
    virtual bool VisProxyHandleClick(FEditorViewportClient* InViewportClient,
        HComponentVisProxy* InVisProxy, const FViewportClick& InClick) override;
    virtual bool GetWidgetLocation(const FEditorViewportClient* InViewportClient,
        FVector& OutLocation) const override;
    virtual bool HandleInputDeltaInternal(FEditorViewportClient* InViewportClient,
        FViewport* InViewport,
        const FVector& InAccumulatedTranslation,
        const FRotator& InAccumulatedRotation,
        const FVector& InAccumulatedScale) override;
    virtual void DrawVisualizationEditing(const UActorComponent* InComponent,
        const FSceneView* InView, FPrimitiveDrawInterface* InPDI,
        int32& InOutIconIndex) override;
};
```

## Demo 示例

```cpp
// MyEffectorTool.h
#pragma once

#include "CoreMinimal.h"
#include "AvalancheInteractiveTools/Tools/AvaInteractiveToolsActorPointToolBase.h"
#include "MyEffectorTool.generated.h"

UCLASS()
class UMyEffectorTool : public UAvaInteractiveToolsActorPointToolBase
{
    GENERATED_BODY()

public:
    UMyEffectorTool();

    virtual void OnRegisterTool(IAvalancheInteractiveToolsModule* InAITModule) override;
};
```

```cpp
// MyEffectorTool.cpp
#include "MyEffectorTool.h"

UMyEffectorTool::UMyEffectorTool()
{
    // 配置工具参数
}

void UMyEffectorTool::OnRegisterTool(IAvalancheInteractiveToolsModule* InAITModule)
{
    // 注册到交互式工具系统
    Super::OnRegisterTool(InAITModule);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AvalancheOutliner` | 大纲栏系统，提供上下文菜单扩展点 |
| `AvalancheInteractiveTools` | 交互式工具框架，基类 UAvaInteractiveToolsActorPointToolBase |
| `AvalancheEffectors` | Cloner/Effector 运行时组件（UCEClonerComponent、UCEEffectorComponent） |
| `ClonerEffector` | 底层克隆器/特效器运行时模块 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-05-09 | `d53ec51` | Motion Design: moved the following plugins from /Plugins/Experimental to /Plugins/VirtualProduction | 将 Motion Design 相关插件从实验性目录迁移至虚拟制片目录 |

### 维护评价

该模块于 2025 年 5 月从实验性（Experimental）迁移至正式的 VirtualProduction 目录，标志着 Motion Design 工具链进入生产就绪状态。作为 Motion Design 插件的编辑器子模块，它随着主插件一同维护。模块架构清晰，遵循运行时/编辑器分离的 UE 模块设计模式。由于迁移时间较短，尚需观察后续独立维护频率。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheEffectorsEditor)
- [插件根目录](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [运行时模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheEffectors)