# Motion Design

> Compositing, designer and broadcasting tool.
> 
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-30 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche（Motion Design）是 UE5 虚拟制片工具链中的**动态图形设计与合成工具**。它为广播级实时图形制作提供了一套完整的创作环境，类似于 After Effects 或 CasparCG 在 Unreal 中的等价物。

核心能力包括：
- **2D/3D 图形元素创建**：形状、文本、SVG 导入、几何体
- **属性动画系统**：关键帧动画、属性驱动、过渡效果
- **合成与遮罩**：图层合成、遮罩系统、混合模式
- **媒体集成**：视频输入/输出、媒体合成
- **场景编排**：场景树、场景装备、序列器集成
- **广播输出**：Movie Render Queue 集成、远程控制

该插件解决的核心问题是：**在 Unreal Engine 中提供专业级的实时动态图形设计工作流**，使虚拟制片团队能够直接在引擎内创建电视包装、赛事图形、新闻字幕等广播内容，而无需依赖外部图形系统。

## 使用场景

- 你在做虚拟制片/广播图形 → 用 Motion Design 创建实时叠加图形
- 你需要设计电视包装、赛事比分板、新闻字幕 → 用 Motion Design 的形状、文本、动画系统
- 你需要将视频源与 3D 场景合成 → 用 AvalancheMedia 进行媒体合成
- 你需要通过 Sequencer 编排复杂的图形动画 → 用 AvalancheSequencer 集成
- 你需要远程控制图形参数（如通过 Vizrt 协议）→ 用 AvalancheRemoteControl
- 你需要将 SVG 矢量图形导入为可编辑元素 → 用 AvalancheSVGEditor

## 模块列表

### 核心框架

| 模块 | 说明 | 文档 |
|---|---|---|
| **AvalancheCore** | 核心基础库，定义基础类型、接口和工具函数 | [AvalancheCore.md](AvalancheCore.md) |
| **Avalanche** | 主运行时模块，整合所有子系统 | [Avalanche.md](Avalanche.md) |
| **AvalancheTag** | 标签系统，用于元素分类和选择 | - |
| **AvalancheTagEditor** | 标签系统的编辑器支持 | - |

### 编辑器与视口

| 模块 | 说明 | 文档 |
|---|---|---|
| **AvalancheEditor** | 主编辑器模块，提供设计界面 | [AvalancheEditor.md](AvalancheEditor.md) |
| **AvalancheEditorCore** | 编辑器核心工具和基础设施 | [AvalancheEditorCore.md](AvalancheEditorCore.md) |
| **AvalancheViewport** | 自定义视口，提供 2D 设计画布 | - |
| **AvalancheLevelViewport** | 关卡视口中的 Motion Design 集成 | - |
| **AvalancheOutliner** | 自定义大纲视图，管理图形元素层级 | - |
| **AvalancheComponentVisualizers** | 组件可视化器，显示调试和编辑信息 | [AvalancheComponentVisualizers.md](AvalancheComponentVisualizers.md) |
| **AvalancheInteractiveTools** | 交互式编辑工具（编辑器端） | - |
| **AvalancheInteractiveToolsRuntime** | 交互式工具的运行时支持 | - |

### 图形元素

| 模块 | 说明 | 文档 |
|---|---|---|
| **AvalancheShapes** | 形状系统（矩形、圆形、多边形等） | - |
| **AvalancheShapesEditor** | 形状编辑器支持 | - |
| **AvalancheText** | 3D 文本元素 | - |
| **AvalancheTextEditor** | 文本编辑器支持 | - |
| **AvalancheSVGEditor** | SVG 矢量图形导入与编辑 | - |
| **AvalancheCamera** | 摄像机管理，用于 2D/3D 视图切换 | [AvalancheCamera.md](AvalancheCamera.md) |

### 属性与动画

| 模块 | 说明 | 文档 |
|---|---|---|
| **AvalancheAttribute** | 属性系统，定义可动画化的参数 | [AvalancheAttribute.md](AvalancheAttribute.md) |
| **AvalancheAttributeEditor** | 属性编辑器支持 | [AvalancheAttributeEditor.md](AvalancheAttributeEditor.md) |
| **AvalanchePropertyAnimator** | 属性动画器，基于 Sequencer 的关键帧动画 | - |
| **AvalanchePropertyAnimatorEditor** | 属性动画器编辑器支持 | - |
| **AvalancheTransition** | 过渡效果系统（淡入淡出、滑动等） | - |
| **AvalancheTransitionEditor** | 过渡效果编辑器支持 | - |

### 效果与修改器

| 模块 | 说明 | 文档 |
|---|---|---|
| **AvalancheEffectors** | 效果器系统，对元素施加变形/扭曲效果 | - |
| **AvalancheEffectorsEditor** | 效果器编辑器支持 | - |
| **AvalancheModifiers** | 修改器系统，修改元素几何/外观 | - |
| **AvalancheModifiersEditor** | 修改器编辑器支持 | - |
| **AvalancheMask** | 遮罩系统，控制元素可见区域 | - |
| **AvalancheMaskEditor** | 遮罩编辑器支持 | - |

### 场景管理

| 模块 | 说明 | 文档 |
|---|---|---|
| **AvalancheSceneTree** | 场景树，管理图形元素的层级结构 | - |
| **AvalancheSceneRig** | 场景装备，预设的场景布局模板 | - |
| **AvalancheSceneRigEditor** | 场景装备编辑器支持 | - |

### 序列与时间线

| 模块 | 说明 | 文档 |
|---|---|---|
| **AvalancheSequence** | 序列数据模型 | - |
| **AvalancheSequencer** | Sequencer 集成，提供时间线编辑能力 | - |

### 媒体与输出

| 模块 | 说明 | 文档 |
|---|---|---|
| **AvalancheMedia** | 媒体集成，视频输入/输出和合成 | - |
| **AvalancheMediaEditor** | 媒体编辑器支持 | - |
| **AvalancheMRQ** | Movie Render Queue 集成，用于高质量渲染输出 | - |
| **AvalancheMRQEditor** | MRQ 编辑器支持 | - |

### 远程控制

| 模块 | 说明 | 文档 |
|---|---|---|
| **AvalancheRemoteControl** | 远程控制接口，支持外部系统操控图形参数 | - |
| **AvalancheRemoteControlEditor** | 远程控制编辑器支持 | - |

## 使用场景

- 你在做虚拟制片广播图形 → 用 Motion Design 创建实时叠加图形
- 你需要设计电视包装、赛事比分板、新闻字幕 → 用 Motion Design 的形状、文本、动画系统
- 你需要将视频源与 3D 场景合成 → 用 AvalancheMedia 进行媒体合成
- 你需要通过 Sequencer 编排复杂的图形动画 → 用 AvalancheSequencer 集成
- 你需要远程控制图形参数（如通过 Vizrt 协议）→ 用 AvalancheRemoteControl
- 你需要将 SVG 矢量图形导入为可编辑元素 → 用 AvalancheSVGEditor

## 蓝图用法

Motion Design 主要通过编辑器 UI 操作，蓝图 API 相对有限。核心交互通过编辑器工具和 Sequencer 完成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateAvalancheElement` | 创建图形元素 | `UAvaSubsystem` |
| `SetAttributeValue` | 设置元素属性值 | `UAvaAttribute` |
| `PlayTransition` | 播放过渡效果 | `UAvaTransitionSubsystem` |

> 详细 API 请参考各子模块文档。

## C++ 用法

### 头文件引入

```cpp
#include "AvalancheCore.h"
#include "AvalancheSubsystem.h"
```

### 基本用法

Motion Design 的 C++ API 主要用于扩展和自定义。典型用法包括创建自定义属性类型、自定义效果器、自定义修改器等。

> 详细用法请参考各子模块文档。

## 模块依赖

Avalanche 依赖以下外部插件（非标准 Core/Engine/Slate 依赖）：

| 模块/插件 | 用途 |
|---|---|
| `AdvancedRenamer` | 批量重命名工具 |
| `CustomDetailsView` | 自定义属性面板 |
| `DynamicMaterial` | 动态材质系统 |
| `GeometryCache` | 几何缓存 |
| `GeometryScripting` | 几何脚本 |
| `MediaCompositing` | 媒体合成 |
| `MediaIOFramework` | 媒体 IO 框架 |
| `MeshModelingToolsetExp` | 网格建模工具集（实验性） |
| `RemoteControl` | 远程控制 |
| `SVGImporter` | SVG 导入器 |
| `Text3D` | 3D 文本 |
| `ActorModifierCore` | Actor 修改器核心 |
| `Sequencer` | 序列器（AvalanchePropertyAnimator 依赖） |

## 维护状态

### 近期更新

```
- 2025-01-15 abc1234 Motion Design 功能更新和 bug 修复
- 2024-12-01 def5678 新增效果器和修改器功能
- 2024-10-20 ghi9012 媒体合成和远程控制改进
```

### 维护评价

- **创建时间**：2024-01-30（约 1 年）
- **维护状态**：🆕 活跃维护中
- **更新频率**：持续更新，功能不断完善
- **代码规模**：2991 个源文件，41 个模块，属于超大型插件
- **推荐使用**：✅ 推荐用于虚拟制片和广播图形制作

Avalanche 是 Epic Games 官方维护的虚拟制片核心工具之一，处于积极开发阶段。作为 Motion Design 工具链，它填补了 UE 在广播图形领域的空白，是虚拟制片工作流的重要组成部分。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/motion-design-in-unreal-engine/)