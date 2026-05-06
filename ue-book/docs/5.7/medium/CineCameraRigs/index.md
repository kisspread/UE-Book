# CineCameraRigs

> Extended camera rigs for cinematic workflow

| 属性 | 值 |
|---|---|
| 中文名 | 电影摄像机装备 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、关卡序列绑定资源） |
| 模块 | `CineCameraRigs` (Runtime), `CineCameraRigsEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-16 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CineCameraRigs) | |

## 总体用途

CineCameraRigs 是面向虚拟制片（Virtual Production）的扩展摄像机装备插件。它提供了一套可编程的摄像机绑定与运动控制组件，允许用户模拟真实世界的摇臂、轨道、无人机等复杂运镜。插件深度集成 Sequencer、Level Sequence 以及多用户协同编辑（Concert），通过 Blueprint 和 Sequencer Scripting 实现高度灵活的电影级相机控制。

## 模块列表

| 模块 | 类型 | 一句话说明 | 详细文档 |
|---|---|---|---|
| `CineCameraRigs` | Runtime | 核心摄像机装备组件，提供绑定逻辑、运动轨迹计算和运行时数据同步 | [CineCameraRigs.md](./CineCameraRigs.md) |
| `CineCameraRigsEditor` | Editor | 编辑器扩展，包含资产创建/编辑支持、自定义细节面板、Sequencer 轨道集成以及多用户会话配置 | [CineCameraRigsEditor.md](./CineCameraRigsEditor.md) |

## 使用场景

- 为 CineCamera（或任意摄像机）附加摇臂、滑轨、云台等真实装备，获得自然的电影运镜效果。
- 在 Sequencer 中通过关键帧动画或表达式驱动装备参数，制作无人机航拍、穿梭镜头等复杂运动。
- 配合 Multi-User Editing（Concert）让多个团队成员同时调整同一台摄影机的装备位置。
- 使用 Sequencer Scripting 在运行时或编辑器脚本中动态配置摄像机装备，实现程序化镜头。

## 依赖项（使用者所需）

| 模块 | 用途 |
|---|---|
| `EditorScriptingUtilities` | 编辑器脚本工具，用于自动化创建/修改资产 |
| `ConcertSyncCore` | 多用户同步核心，支持装备状态的协同编辑 |
| `SequencerScripting` | Sequencer 脚本接口，用于编程控制装备时序 |
| `LevelSequenceEditor` | Level Sequence 编辑器扩展，提供 UI 和命令支持 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CineCameraRigs)
- [CineCameraRigs 模块文档](./CineCameraRigs.md)
- [CineCameraRigsEditor 模块文档](./CineCameraRigsEditor.md)