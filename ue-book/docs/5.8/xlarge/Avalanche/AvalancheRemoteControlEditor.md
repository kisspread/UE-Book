# Motion Design

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Motion Design 是一个面向虚拟制片的动态图形设计与播出工具，最初作为实验性插件开发，2025 年 5 月从 `/Plugins/Experimental` 正式迁移到 `/Plugins/VirtualProduction`。它提供了一套完整的动态内容制作流水线，涵盖：

- **合成与设计**：通过 SceneRig、SceneTree、Shapes、Text 等模块构建和编排动态场景元素
- **特效系统**：Effectors（克隆/阵列效果）、Modifiers（修改器栈）、Mask（遮罩系统）、Transition（转场效果）
- **属性动画**：PropertyAnimator 提供基于 Sequencer 的属性关键帧动画能力
- **材质编辑**：Material 模块提供动态材质编辑器
- **媒体播出**：Media 模块支持实时媒体输入输出和播放控制（Rundown Page）
- **远程控制**：RemoteControl 模块将场景元素暴露为可远程控制的参数
- **序列集成**：Sequencer/Sequence 模块与 UE Sequencer 深度集成
- **MRQ 渲染**：通过 Movie Render Queue 输出最终画面

该插件是为广播级实时图形（如体育赛事图形、新闻包装、演唱会视觉）和虚拟制片场景设计的，解决了 UE 中缺少专业动态图形设计工具链的问题。

## 使用场景

- 你需要为电视直播制作实时图形模板 → 用 Motion Design 的 SceneRig + Rundown Page
- 你需要在虚拟制片现场快速设计和切换动态背景 → 用 Shapes + Text + Transitions
- 你需要将场景参数暴露给外部控制系统（如 Vizrt、Ross）→ 用 RemoteControl 模块
- 你需要创建复杂的阵列/粒子式动画效果 → 用 Effectors + Cloner
- 你需要对物体属性做关键帧动画但不想写蓝图 → 用 PropertyAnimator + Sequencer

## 模块架构

Motion Design 由 43 个模块组成，采用 Runtime/Editor 模块对设计模式。以下按功能分组：

### 核心框架

| 模块 | 说明 |
|---|---|
| `Avalanche` | 主模块，插件入口 |
| `AvalancheCore` | 核心类型定义与基础工具 |
| `AvalancheEditor` | 编辑器入口与通用编辑器功能 |
| `AvalancheEditorCore` | 编辑器核心类型与工具 |

### 场景元素

| 模块 | 说明 |
|---|---|
| `AvalancheShapes` / `ShapesEditor` | 几何形状（矩形、圆形等） |
| `AvalancheText` / `TextEditor` | 3D 文字（依赖 Text3D 插件） |
| `AvalancheSVGEditor` | SVG 导入与编辑 |

### 动画与效果

| 模块 | 说明 |
|---|---|
| `AvalancheEffectors` / `EffectorsEditor` | 效果器（克隆/阵列） |
| `AvalancheModifiers` / `ModifiersEditor` | 修改器栈 |
| `AvalanchePropertyAnimator` / `PropertyAnimatorEditor` | 属性动画 |
| `AvalancheTransition` / `TransitionEditor` | 转场效果 |
| `AvalancheMask` / `MaskEditor` | 遮罩系统 |

### 组织与控制

| 模块 | 说明 |
|---|---|
| `AvalancheSceneRig` / `SceneRigEditor` | 场景装备 |
| `AvalancheSceneTree` | 场景树结构 |
| `AvalancheOutliner` | Motion Design 专用大纲视图 |
| `AvalancheTag` / `TagEditor` | 标签系统 |
| `AvalancheAttribute` / `AttributeEditor` | 属性系统 |

### 远程控制与媒体

| 模块 | 说明 |
|---|---|
| `AvalancheRemoteControl` / `RemoteControlEditor` | 远程控制集成 |
| `AvalancheMedia` / `MediaEditor` | 媒体输入输出与播出控制 |

### 编辑器集成

| 模块 | 说明 |
|---|---|
| `AvalancheViewport` | 视口扩展 |
| `AvalancheLevelViewport` | 关卡编辑器视口 |
| `AvalancheCamera` | 摄像机管理 |
| `AvalancheSequencer` / `AvalancheSequence` | Sequencer 集成 |
| `AvalancheMRQ` / `MRQEditor` | Movie Render Queue 集成 |
| `AvalancheMaterial` | 材质编辑器 |
| `AvalancheComponentVisualizers` | 组件可视化器 |
| `AvalancheInteractiveTools` / `InteractiveToolsRuntime` | 交互式编辑工具 |

### 其他

| 模块 | 说明 |
|---|---|
| `AvalancheFunctionalTest` | 功能测试 |

---

## 子模块文档：AvalancheRemoteControlEditor

本模块为 Motion Design 提供与 Unreal Remote Control 插件的编辑器集成，将远程控制功能无缝嵌入 Motion Design 的大纲视图和属性面板中。

### 用途

AvalancheRemoteControlEditor 解决的核心问题：在 Motion Design 的大纲视图（Outliner）中直接管理和可视化 Remote Control Tracker 组件，让用户无需切换到其他面板即可：

1. 查看哪些 Actor 挂载了 Remote Control Tracker 组件
2. 查看和切换 Remote Control 被追踪的属性可见性
3. 通过上下文菜单批量添加/移除 Tracker 组件
4. 通过自定义属性面板选择 Remote Control Controller

### 核心组件

#### 大纲视图集成

**FAvaOutlinerRCTrackerComponent** — Tracker 组件的大纲视图项

在 Motion Design 大纲视图中展示 `URemoteControlTrackerComponent`。继承自 `FAvaOutlinerObject`（而非 `FAvaOutlinerComponent`），因为 Tracker 是 `UActorComponent` 而非 `USceneComponent`。

核心功能：
- 自定义图标显示
- 可见性管理（切换属性的显示/隐藏状态）
- 选中行为

**FAvaOutlinerRCTrackerComponentProxy** — Tracker 组件代理

作为大纲视图中的代理项，负责：
- 响应 Actor 被追踪属性变化的委托
- 管理代理项的注册/注销生命周期
- 提供追踪项列表

**FAvaOutlinerRCComponentsContextMenu** — 大纲上下文菜单扩展

扩展 Motion Design 大纲的右键菜单，提供以下操作：

| 操作 | 说明 |
|---|---|
| 添加 Tracker | 为选中 Actor 添加 Remote Control Tracker 组件 |
| 移除 Tracker | 移除选中 Actor 的 Tracker 组件 |
| 取消暴露全部属性 | 批量取消所有已暴露的属性 |

#### 属性自定义

**FAvaRCControllerIdCustomization** — Controller ID 属性自定义

为 Remote Control Controller ID 字段提供自定义的属性面板控件。

**SAvaRCControllerPicker** — Controller 选择器控件

一个 Slate 下拉选择框，用于在属性面板中选择 Remote Control Controller：
- 自动列出当前 Level 中可用的 Controller
- 支持手动输入 Controller 名称
- 实时刷新可用选项列表

### 蓝图用法

本模块主要提供编辑器扩展功能，无直接的蓝图可调用节点。其功能通过以下方式在编辑器中使用：

1. **大纲视图**：选中挂载了 Remote Control Tracker 的 Actor 后，在 Motion Design 大纲视图中会自动显示 Tracker 组件节点
2. **右键菜单**：在大纲视图中右键 Actor 可看到 Remote Control 相关菜单项
3. **属性面板**：当存在 Controller ID 属性时，会显示自定义的选择器控件

### C++ 用法

#### 头文件引入

```cpp
#include "AvalancheRemoteControlEditorModule.h"
```

#### 注册自定义属性布局

模块在启动时自动注册属性自定义。如果需要在其他模块中手动注册类似自定义：

```cpp
// 引入自定义类型
#include "Customizations/AvaRCControllerIdCustomization.h"

// 注册属性类型自定义
FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
PropertyModule.RegisterCustomPropertyTypeLayout(
    "AvaRCControllerId",  // 属性类型名
    FOnGetPropertyTypeCustomizationInstance::CreateStatic(&FAvaRCControllerIdCustomization::MakeInstance)
);
```

#### 扩展大纲上下文菜单

```cpp
#include "Outliner/AvaOutlinerRCComponentsContextMenu.h"

// 上下文菜单通过 UToolMenu 扩展系统注册
// 调用静态方法来注册菜单扩展
UToolMenus::RegisterMenu("AvaOutliner.ContextMenu");
```

#### 创建大纲代理项

```cpp
#include "Outliner/AvaOutlinerRCTrackerComponentProxy.h"

// 创建 Tracker 组件代理项，附加到指定的父项
TSharedRef<FAvaOutlinerRCTrackerComponentProxy> Proxy = 
    MakeShared<FAvaOutlinerRCTrackerComponentProxy>(Outliner, ParentItem);

// 代理会自动绑定 Actor 的 TrackedActorsChanged 委托
```

### 模块依赖

| 模块 | 用途 |
|---|---|
| `AvalancheOutliner` | Motion Design 大纲视图框架 |
| `RemoteControl` | Unreal Remote Control 核心功能 |
| `RemoteControlAPI` | Remote Control API 接口 |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

### 维护状态

#### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own group | 将 Motion Design 面板移至独立分组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 使用 Rundown Page 时添加 MRQ 分析 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar | 工具栏新增页面加载选项 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes | 新增禁用碰撞的项目设置 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated with a viewport | 视口客户端关联通知重构 |

#### 维护评价

- **活跃维护**：最近提交频繁（2026 年 5 月有多次更新），且均为功能性改动而非单纯编译修复
- **成熟度**：插件刚从 Experimental 毕业至 VirtualProduction，正处于稳定化阶段
- **团队支持**：由 Epic Games 维护，有明确的 JIRA ticket 追踪（UE-207892）
- **风险提示**：作为新毕业的插件，API 可能在后续版本中仍有变动
- **推荐程度**：✅ 推荐使用，尤其适合虚拟制片和广播图形场景

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- 官方文档（暂无）
- [Remote Control 插件文档](https://docs.unrealengine.com/5.8/en-US/remote-control-in-unreal-engine/)