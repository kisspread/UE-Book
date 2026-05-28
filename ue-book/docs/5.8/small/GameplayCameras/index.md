# Gameplay Cameras

> A modular and data-driven camera system for Unreal

| 属性 | 值 |
|---|---|
| 中文名 | 游戏相机系统 |
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（相机蓝图资产、测试资源） |
| 模块 | `GameplayCameras` (Runtime), `GameplayCamerasEditor` (Runtime), `GameplayCamerasUncookedOnly` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras) | |

## 用途

GameplayCameras 是一个**模块化、数据驱动**的相机系统，旨在替代或增强 UE 传统的相机框架。它将相机行为拆分为可独立配置的相机节点（Camera Node）和相机资产（Camera Asset），通过蓝图和编辑器工具进行可视化编辑，支持多相机混合、相机变量覆盖、平滑过渡等高级功能。

该插件解决的核心问题：
- 传统 `APlayerCameraManager` + `UCameraComponent` 的组合方式在复杂项目中难以维护
- 相机行为逻辑与代码耦合过深，策划难以独立调整
- 缺乏标准化的相机状态机和过渡系统

它依赖 **Enhanced Input** 插件来处理输入绑定，与 UE 的模块化游戏框架（Modular Gameplay）理念一致。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [`GameplayCameras`](GameplayCameras.md) | Runtime | 核心运行时模块，包含相机节点系统、相机资产、相机评估器等核心逻辑 |
| [`GameplayCamerasEditor`](GameplayCamerasEditor.md) | Runtime | 编辑器工具模块，提供相机蓝图节点、自定义面板、资产编辑器等编辑器扩展 |
| [`GameplayCamerasUncookedOnly`](GameplayCamerasUncookedOnly.md) | UncookedOnly | 仅在未打包构建时加载，包含编辑器专用的验证和预处理逻辑 |

## 使用场景

- 你需要为第三人称动作游戏构建复杂的相机状态机（战斗/探索/瞄准各有不同相机行为）→ 用 GameplayCameras 的相机资产和节点图
- 你希望策划在蓝图中可视化配置相机混合和过渡，而不是写死在 C++ 中 → 用数据驱动的相机资产
- 你的项目需要在多个相机视角之间平滑切换（如过场动画到游戏相机的无缝过渡）→ 用相机混合和过渡系统
- 你需要对相机参数（FOV、距离、偏移）进行运行时动态覆盖 → 用相机变量系统

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras)
- [GameplayCameras 运行时模块文档](GameplayCameras.md)
- [GameplayCamerasEditor 编辑器模块文档](GameplayCamerasEditor.md)
- [GameplayCamerasUncookedOnly 模块文档](GameplayCamerasUncookedOnly.md)