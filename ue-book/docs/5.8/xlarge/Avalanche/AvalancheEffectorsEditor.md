# Motion Design — AvalancheEffectorsEditor 模块

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计效果器编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无（纯编辑器逻辑模块） |
| 模块 | `AvalancheEffectorsEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheEffectorsEditor) | |

---

## 用途

AvalancheEffectorsEditor 是 Motion Design（原 Avalanche）插件中负责 **Cloner（克隆器）和 Effector（效果器）编辑器交互** 的模块。

Motion Design 是 UE5 的虚拟制作动态设计工具集，用于广播级合成、设计和播出。其中 Cloner 和 Effector 是核心组件系统：
- **Cloner（克隆器）**：在场景中按规则（网格、线性、径向、环形等布局）克隆子物体，是粒子/阵列式排版的基础
- **Effector（效果器）**：通过权重区域（球形、盒形、环形等）影响克隆器中子物体的属性（位移、旋转、缩放等），类似 C4D 的效应器概念

本模块提供这两个组件在编辑器中的：
1. **Viewport 可视化绘制**：在 3D 视口中绘制效果器的权重区域、克隆器的间距控制手柄
2. **交互式操纵**：通过拖拽手柄调整效果器的内外半径/范围、克隆器的轴向间距
3. **交互式放置工具**：通过工具栏按钮在场景中点击放置新的 Cloner/Effector Actor
4. **大纲菜单扩展**：在 Motion Design Outliner 中添加 Cloner/Effector 的右键上下文菜单

## 使用场景

- 你在用 Motion Design 制作广播级动态图形，需要可视化调整克隆器的间距 → Cloner 可视化器
- 你需要精确控制效果器的影响范围（内外球半径、盒形范围等）→ Effector 可视化器
- 你需要通过工具栏一键放置克隆器或效果器到场景中 → 交互式放置工具
- 你在 Motion Design Outliner 中管理 Cloner/Effector 的层级关系 → 大纲上下文菜单

## 蓝图用法

本模块主要提供编辑器扩展逻辑（组件可视化器、工具注册），不直接暴露 BlueprintCallable API。Cloner/Effector 的运行时蓝图 API 位于 `AvalancheEffectors` 运行时模块中，由 `UCEEffectorComponent` 和 `UCEClonerComponent` 提供。

本模块的使用主要通过编辑器 UI 自动触发，无需手动蓝图连接。

## C++ 用法

### 模块结构

```
AvalancheEffectorsEditor/
├── Private/
│   ├── AvalancheEffectorsEditorModule.h   // 模块入口
│   ├── AvaEffectorsEditorCommands.h       // 编辑器命令定义
│   ├── AvaEffectorsEditorStyle.h          // 编辑器样式
│   ├── Effector/
│   │   ├── AvaEffectorActorVis.h          // 效果器组件可视化器
│   │   ├── AvaEffectorActorTool.h         // 效果器放置工具
│   │   └── AvaEffectorEditorOutlinerContextMenu.h  // 效果器大纲菜单
│   └── Cloner/
│       ├── AvaClonerActorVis.h            // 克隆器组件可视化器
│       ├── AvaClonerActorTool.h           // 克隆器放置工具
│       └── AvaClonerEditorOutlinerContextMenu.h    // 克隆器大纲菜单
```

### 头文件引入

```cpp
// 效果器可视化器
#include "Effector/AvaEffectorActorVis.h"

// 克隆器可视化器
#include "Cloner/AvaClonerActorVis.h"
```

### 组件可视化器继承体系

可视化器基于 `FAvaVisualizerBase`（来自 AvalancheComponentVisualizers 模块）扩展，提供统一的编辑器内组件绘制和交互框架：

```cpp
// FAvaVisualizerBase 是 Motion Design 所有组件可视化器的基类
// FAvaEffectorActorVisualizer 专门处理效果器的权重区域绘制和手柄交互
// FAvaClonerActorVisualizer 专门处理克隆器的间距控制绘制和手柄交互

// 效果器可视化器重写了以下核心方法：
virtual bool VisProxyHandleClick(...) override;           // 点击选择手柄
virtual bool GetWidgetLocation(...) override;             // 变换控件位置
virtual bool HandleInputDeltaInternal(...) override;      // 处理拖拽输入
virtual void DrawVisualizationEditing(...) override;      // 编辑状态绘制
virtual void DrawVisualizationNotEditing(...) override;   // 非编辑状态绘制
```

### 效果器权重区域编辑

`FAvaEffectorActorVisualizer` 支持以下效果器参数的手柄交互编辑：

| 手柄类型 | 常量 | 可编辑属性 |
|---|---|---|
| 内区域 | `HandleTypeInnerZone = 0` | `InnerRadiusProperty`, `InnerExtentProperty` |
| 外区域 | `HandleTypeOuterZone = 1` | `OuterRadiusProperty`, `OuterExtentProperty` |
| 半径 | `HandleTypeRadius = 2` | `RadialMinRadiusProperty`, `RadialMaxRadiusProperty`, `TorusRadiusProperty` |
| 角度 | `HandleTypeAngle = 3` | `RadialAngleProperty`, `TorusInnerRadiusProperty`, `TorusOuterRadiusProperty` |

### 克隆器间距编辑

`FAvaClonerActorVisualizer` 支持按轴向编辑克隆器间距：

```cpp
// 通过 ECEClonerAxis 枚举区分 X/Y/Z 轴间距
struct HAvaClonerActorSpacingHitProxy : HAvaHitProxy
{
    ECEClonerAxis Axis = ECEClonerAxis::Custom;  // 轴向标识
};
```

### 交互式放置工具

Cloner 和 Effector 的放置工具均继承自 `UAvaInteractiveToolsActorPointToolBase`（来自 AvalancheInteractiveTools 模块）：

```cpp
// UAvaClonerActorTool - 在场景中点击放置克隆器 Actor
// UAvaEffectorActorTool - 在场景中点击放置效果器 Actor
// 两者通过 OnRegisterTool() 注册到 IAvalancheInteractiveToolsModule
```

### 编辑器命令注册

```cpp
// FAvaEffectorsEditorCommands 管理所有 Cloner/Effector 相关的编辑器命令
class FAvaEffectorsEditorCommands : public TCommands<FAvaEffectorsEditorCommands>
{
    TMap<FName, TSharedPtr<FUICommandInfo>> Tool_Actor_Cloners;   // 克隆器工具命令
    TMap<FName, TSharedPtr<FUICommandInfo>> Tool_Actor_Effectors; // 效果器工具命令
};
```

## Demo 示例

本模块是纯编辑器基础设施模块，不直接提供运行时 API。以下是模块启动时的注册流程示意：

```cpp
// AvalancheEffectorsEditorModule.cpp 中的核心逻辑
void FAvalancheEffectorsEditorModule::StartupModule()
{
    // 1. 注册组件可视化器（使 Cloner/Effector 组件在视口中可交互）
    RegisterComponentVisualizers();
    
    // 2. 注册大纲上下文菜单扩展
    RegisterOutlinerItems();
}

void FAvalancheEffectorsEditorModule::RegisterComponentVisualizers()
{
    // 为 UCEEffectorComponent 注册 FAvaEffectorActorVisualizer
    // 为 UCEClonerComponent 注册 FAvaClonerActorVisualizer
    // 注册后，视口中选中对应的组件会自动显示权重区域/间距控制手柄
}

void FAvalancheEffectorsEditorModule::ShutdownModule()
{
    // 注销大纲菜单委托
    UnregisterOutlinerItems();
    // 组件可视化器随引擎生命周期自动清理
}
```

## 模块依赖

AvalancheEffectorsEditor 是编辑器模块，依赖以下 Motion Design 子模块：

| 模块 | 用途 |
|---|---|
| `AvalancheEffectors` | Cloner/Effector 运行时组件定义（UCEEffectorComponent、UCEClonerComponent） |
| `AvalancheComponentVisualizers` | 可视化器基类 FAvaVisualizerBase |
| `AvalancheInteractiveTools` | 交互式工具基类 UAvaInteractiveToolsActorPointToolBase |
| `AvalancheOutliner` | Motion Design Outliner 集成 |
| `AvalancheEditorCore` | 编辑器核心工具和通用功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将 Motion Design 的场景设置和大纲标签页移至独立分组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 添加 MRQ 分析功能，跟踪 Rundown 页面设置的使用情况 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在播出控制工具栏添加页面加载选项（全部/下一个/选中） |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加项目设置，支持强制禁用 Text3D 和形状的碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联/断开通知机制 |

### 维护评价

**🟢 活跃维护**

Motion Design（原 Avalanche）是 Epic 官方重点维护的 Virtual Production 工具集：
- **创建时间**：2025-05-09，从 Experimental 迁移至正式的 VirtualProduction 目录
- **更新频率**：非常活跃，近期 commit 密集（一周内多次功能性更新）
- **代码规模**：2060 个源文件、43 个子模块，是 UE5 中规模最大的插件之一
- **开发团队**：Epic Games 官方团队维护，有明确的 Jira 任务跟踪（UE-207892）
- **成熟度**：虽然从 Experimental 迁出不到一年，但代码组织成熟，模块划分清晰

**建议**：Motion Design 是广播级动态图形和虚拟制作的核心工具，AvalancheEffectorsEditor 作为其编辑器交互层的关键模块，推荐在使用 Cloner/Effector 系统时了解其工作方式。

## 相关链接

- [Motion Design 插件根目录](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [AvalancheEffectorsEditor 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheEffectorsEditor)
- [AvalancheEffectors 运行时模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheEffectors)
- [AvalancheComponentVisualizers 基类模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheComponentVisualizers)
- [AvalancheInteractiveTools 工具模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheInteractiveTools)