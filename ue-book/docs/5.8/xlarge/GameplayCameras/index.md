# Gameplay Cameras

> A modular and data-driven camera system for Unreal

| 属性 | 值 |
|---|---|
| 中文名 | 游戏相机系统 |
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产，示例内容） |
| 模块 | `GameplayCameras` (Runtime), `GameplayCamerasEditor` (Runtime), `GameplayCamerasUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-03 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras) | |

## 用途

GameplayCameras 插件的核心是提供一个 **基于节点的相机行为图 (Camera Behavior Graph) 系统**。它并非一个简单的相机切换或混合器，而是一个用于构建复杂的、数据驱动的相机逻辑的底层框架。

这个系统存在的根本原因是**解决传统相机管理方式中代码冗余、逻辑分散、难以维护和调试的问题**。通过将相机行为抽象为可在编辑器中可视化编辑的节点图，开发者可以将原本需要大量 C++ 或蓝图代码才能实现的复杂镜头逻辑（如根据游戏状态动态调整视角、平滑过渡、应用特殊效果等）转化为可组合、可重用的数据资产，从而提高开发效率和可维护性。

## 使用场景

- **复杂镜头动画序列**：当游戏需要一系列根据玩家输入、游戏事件或过场动画触发的复杂镜头运动和视角切换时。
- **多摄像机视角管理**：需要在一个或多个 `UCineCameraComponent` 之间根据规则（如角色状态、距离、方向）动态切换或混合输出视角。
- **数据驱动的相机行为**：希望将相机行为（如灵敏度、跟随参数、后处理效果）的参数化配置放在数据资产中，而非硬编码，以便策划调整。
- **模块化相机逻辑**：需要将不同的相机功能（如基础跟随、瞄准缩放、震动、特殊演出效果）封装成独立的节点或子图，以便在不同场景下复用。
- **替代传统 `CameraModifier` 和 `CameraShake`**：当默认的 `CameraModifier` 机制不足以处理复杂的、基于状态的组合逻辑时。

## 蓝图用法

该插件的蓝图 API 主要围绕 **“相机行为资产”（Camera Behavior Asset）** 和 **“节点”（Node）** 展开。详细的类和函数列表请参考 [GameplayCameras 模块文档](GameplayCameras.md)。

### 核心概念

- **`UCameraBehaviorAsset`**：相机行为资产是节点图的容器，可在内容浏览器中创建和编辑。
- **`UCameraNode`**：所有节点的基类，代表图中的一个计算步骤（如获取数据、计算目标、应用效果）。
- **`UCameraComponent`**（游戏侧）：负责拥有和驱动一个相机行为资产实例，将其逻辑输出到场景中的相机组件。

### 使用示例（蓝图描述）

1.  **创建资产**：在内容浏览器中右键，选择 `Cameras` -> `Camera Behavior Asset`。
2.  **编辑逻辑**：双击资产打开专用的图形编辑器，从节点面板拖拽各种功能节点（如 `Follow Target`, `Look At`, `Apply Camera Shake`），连接它们以构建逻辑流。
3.  **应用到角色**：在角色蓝图中添加一个 `GameplayCameras` -> `CameraComponent`。
4.  **指定资产**：在 `CameraComponent` 的详情面板中，将上一步创建的 `Camera Behavior Asset` 赋值给 `BehaviorAsset` 属性。
5.  **运行时控制**：运行游戏后，`CameraComponent` 会自动评估其关联的节点图，并将计算结果应用到场景中的相机。

## C++ 用法

C++ 层面提供了扩展节点系统和直接驱动相机行为的能力。详细的头文件、类继承关系和代码示例请参考 [GameplayCameras 模块文档](GameplayCameras.md)。

### 核心用法

- **创建自定义节点**：继承 `UCameraNode` 或其子类，重写 `Evaluate` 函数来实现自定义的相机计算逻辑。
- **在代码中驱动相机**：通过获取角色的 `UCameraComponent` 实例，可以在 C++ 中动态地切换资产 (`SetBehaviorAsset`) 或访问节点图中的特定参数。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| [`GameplayCameras`](GameplayCameras.md) | Runtime | **核心运行时模块**。包含所有相机节点定义、行为图评估引擎、以及游戏端用于驱动相机的组件。 |
| [`GameplayCamerasEditor`](GameplayCamerasEditor.md) | Runtime | **编辑器工具模块**。提供创建、编辑和预览 `CameraBehaviorAsset` 的专用图形编辑器、细节面板自定义和资产工厂。 |
| [`GameplayCamerasUncookedOnly`](GameplayCamerasUncookedOnly.md) | Runtime | **仅编辑器/未打包构建模块**。包含编辑器专用的工具类、辅助函数和测试用例，确保在打包时不会包含这些代码。 |

## 维护状态

### 近期更新

```
- 2026-04-14 35e60df1 Migrate UE_LOG to UE_LOGF.
- 2026-04-13 6f1ea925 State Tree: Updated state tree reference struct details to show the display name of the struct rather than the type.
- 2026-04-08 81eea83d [ContentBrowser] New Add Menu Gameplay Menu
```

### 维护评价

**活跃维护，但处于实验阶段**。
- **创建时间**：该插件于 **2026年3月** 创建，非常新。
- **更新频率**：最近一个月（2026年4月）有持续的代码提交，表明正在积极开发和集成。
- **当前状态**：尽管功能在持续迭代，但 `.uplugin` 文件中明确标记为 **`IsExperimentalVersion: true`**。这意味着其 API 和功能可能随时发生破坏性变更，不建议在需要高度稳定性的正式项目中依赖它。
- **推荐使用**：适合用于**技术原型验证**和**学习先进的相机系统架构**。在生产环境中使用需承担实验性 API 带来的风险，并密切关注引擎版本更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras)
- [官方文档]() (无)