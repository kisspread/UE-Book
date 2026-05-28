# Niagara Simulation Caching

> Adds support for recording and playing back Niagara simulations in sequencer via take recorder

| 属性 | 值 |
|---|---|
| 中文名 | Niagara 模拟缓存 |
| 分类 | FX |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `NiagaraSimCaching` (Runtime), `NiagaraSimCachingEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-09-12 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/NiagaraSimCaching) | |

## 用途

该插件为 Niagara 粒子系统提供了模拟状态录制与回放功能。它解决了在 Sequencer 中精确录制复杂、非确定性的 Niagara 模拟（如流体、布料）并进行回放的需求，使得这些效果可以完美同步到过场动画或预渲染的时间线上。通过集成 Take Recorder，它使流程自动化、标准化。

## 使用场景

- **游戏过场动画制作**：需要将复杂的 Niagara 粒子效果（如爆炸、魔法效果）与镜头运动和角色动画精确同步。
- **高质量预渲染/宣传片**：录制高计算成本的模拟并多次回放，以获得稳定、高质量的渲染结果，无需每次都实时计算。
- **快速迭代预览**：在编辑器内录制一次模拟，之后反复回放以快速调整灯光、后期等其他元素，无需等待模拟重新运行。

## 模块列表

| 模块 | 功能概述 |
|---|---|
| **NiagaraSimCaching** (Runtime) | 核心运行时逻辑，提供管理模拟缓存资产、控制缓存数据生命周期的基础类与接口。 |
| **NiagaraSimCachingEditor** (Editor) | 编辑器扩展，集成 Sequencer 与 Take Recorder，提供 UI 控件以启动录制、选择缓存资产等。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/NiagaraSimCaching)
- [官方教程](https://dev.epicgames.com/community/learning/tutorials/Rk9v/unreal-engine-niagara-simulation-caching-in-sequencer)