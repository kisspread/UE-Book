# Motion Design

> Compositing, designer and broadcasting tool. Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态图形设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质、预设、工具） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche (Motion Design) 是一个大型的综合性虚拟制作插件，旨在提供完整的 2D/3D 动态图形设计、合成与广播能力。它解决的核心问题是：在 Unreal Engine 中为广播、现场活动、数字标牌等场景提供高效、实时的图形内容创作与播放工作流。

从代码结构和模块划分来看，它不仅仅是一个工具，而是一个集成了设计、动画、材质、场景管理、远程控制、渲染和输出功能的**完整生态系统**。它将许多原本独立的插件（如 Text3D、ClonerEffector、PropertyAnimator 等）统一整合到 Motion Design 的框架下，为用户提供了一个从设计到播出的端到端解决方案。

## 使用场景

- **直播与活动**：为体育赛事、演唱会、颁奖典礼等制作实时更新的比分板、标题条、下方三分之一、数据可视化等动态图形。
- **数字标牌与信息展示**：创建可远程控制的、基于数据的动态展板、菜单屏、指引系统。
- **虚拟制作与 XR 舞台**：设计和控制 LED 墙上显示的动态背景、虚拟道具以及与摄像机运动绑定的图形元素。
- **产品发布与演示**：为产品发布活动制作酷炫的 3D 动画序列、转场和数据演示。
- **快速原型制作**：利用其节点式设计和预设系统，快速搭建和迭代复杂的动态图形场景。

## 模块列表

该插件由 42 个模块构成，按功能可分为以下几类：

### 核心框架与系统
| 模块 | 说明 |
|---|---|
| `AvalancheCore` | 核心基础类和系统。 |
| `Avalanche` | 主插件模块，包含核心组件和功能。 |
| `AvalancheEditorCore` | 编辑器扩展的核心基础。 |
| `AvalancheSceneTree` | 场景树/大纲视图数据管理。 |
| `AvalancheOutliner` | 自定义的大纲视图实现。 |
| `AvalancheTag` | 标签系统，用于对象分组和查询。 |
| `AvalancheAttribute` | 属性系统，为对象添加可配置的参数。 |
| `AvalancheTransition` | 场景间或状态间的过渡管理。 |
| `AvalancheSequence` | 序列/时间线数据管理。 |
| `AvalancheSequencer` | 与 UE Sequencer 深度集成的编辑器。 |

### 设计与创建工具
| 模块 | 说明 |
|---|---|
| `AvalancheText` | 3D 文本创建与控制。 |
| `AvalancheShapes` | 基础几何形状（矩形、圆形、线条等）创建。 |
| `AvalancheMaterial` | 动态材质创建与管理工具。 |
| `AvalancheMask` | 遮罩系统，用于定义效果区域。 |
| `AvalancheSVGEditor` | SVG 文件导入与编辑。 |
| `AvalancheCamera` | 专用的摄像机设置与控制。 |

### 运动与动画
| 模块 | 说明 |
|---|---|
| `AvalancheEffectors` | 效果器系统，驱动克隆体等对象运动。 |
| `AvalancheModifiers` | 修改器，用于批量处理几何体变形等。 |
| `AvalanchePropertyAnimator` | 属性动画师，可动画化任何属性。 |
| `AvalancheSceneRig` | 场景装备，用于预设复杂的场景结构。 |

### 渲染与输出
| 模块 | 说明 |
|---|---|
| `AvalancheMRQ` | 与 Movie Render Queue 集成，用于高质量离线渲染。 |
| `AvalancheMedia` | 媒体输入输出，处理视频流等。 |
| `AvalancheViewport` | 自定义视口功能和渲染。 |
| `AvalancheLevelViewport` | 关卡视口中的自定义绘制和交互。 |
| `AvalancheComponentVisualizers` | 为组件提供编辑器内的可视化辅助。 |

### 编辑器扩展与工具
| 模块 | 说明 |
|---|---|
| `AvalancheEditor` | 主编辑器工具、面板和菜单。 |
| `AvalancheInteractiveTools` | 编辑器内交互式工具（如拖拽、变形）。 |
| `AvalancheInteractiveToolsRuntime` | 交互式工具的运行时部分。 |
| `AvalancheRemoteControl` | 远程控制接口，允许外部应用控制场景。 |
| `AvalancheFunctionalTest` | 功能性自动化测试。 |

*注：带有 `Editor` 后缀的模块通常包含其对应运行时模块的编辑器扩展功能。*

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)