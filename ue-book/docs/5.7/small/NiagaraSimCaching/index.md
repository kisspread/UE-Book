# NiagaraSimCaching

> Adds support for recording and playing back Niagara simulations in sequencer via take recorder

| 属性 | 值 |
|---|---|
| 中文名 | Niagara模拟缓存 |
| 分类 | FX |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（模拟缓存资产） |
| 模块 | `NiagaraSimCaching` (Runtime), `NiagaraSimCachingEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-03-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/NiagaraSimCaching) | |

## 总体用途

该类缓存插件允许用户通过 Sequencer 和 Take Recorder 录制 Niagara 粒子系统的模拟过程，并将其保存为可重复使用的缓存资产。录制完成后，可以在序列编辑器中精确回放粒子动画，无需实时模拟，适用于电影级品质的过场动画、预渲染镜头或需要确定性回放的场景。

## 模块列表

| 模块名 | 类型 | 一句话总结 |
|---|---|---|
| [NiagaraSimCaching](NiagaraSimCaching.md) | Runtime | 提供运行时录制、缓存管理、回放的核心逻辑与数据结构 |
| [NiagaraSimCachingEditor](NiagaraSimCachingEditor.md) | Editor | 为 Sequencer 和 Take Recorder 提供编辑器集成，包括UI、录制设置和轨道支持 |

## 使用场景

- **过场动画制作**：在 Sequencer 中编排包含 Niagara 特效的镜头时，将粒子模拟录制为缓存，确保每次回放一致且性能优异。
- **性能优化**：对于计算量巨大的粒子系统，提前录制模拟缓存，运行时仅播放缓存的帧，避免实时计算开销。
- **协作与迭代**：艺术家可录制满意的粒子效果，程序员直接使用缓存，无需依赖实时模拟的随机性。
- **Take Recorder 工作流**：在游戏内录制实机演出时，同时捕捉 Niagara 模拟数据，便于后期调整。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/NiagaraSimCaching)
- [官方文档](https://dev.epicgames.com/community/learning/tutorials/Rk9v/unreal-engine-niagara-simulation-caching-in-sequencer)