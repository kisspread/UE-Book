# Cinematic Prestreaming

> Adds a way to record certain types of streaming data requests in cinematic cutscenes. The requests can then be played back in advance on the Sequencer timeline to pre-stream data during normal gameplay/rendering.

| 属性 | 值 |
|---|---|
| 中文名 | 过场动画预加载 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `CinematicPrestreaming` (Runtime), `CinematicPrestreamingEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-29 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CinematicPrestreaming) | |

---

## 总体用途

Cinematic Prestreaming 允许在过场动画（Sequencer 时间线）中**录制**各类流式数据请求（如虚拟纹理、网格体、纹理等），并在后续回放时**提前**播放这些请求，从而在进入过场动画之前完成数据预加载，避免播放过程中因流式加载导致的卡顿和性能开销。该插件特别适用于需要高画质、无缝过场动画的体验（如电影化叙事、实时渲染预告片）。

---

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| [CinematicPrestreaming](./CinematicPrestreaming.md) | Runtime | 提供预加载数据的录制、存储和运行时回放核心逻辑 |
| [CinematicPrestreamingEditor](./CinematicPrestreamingEditor.md) | UncookedOnly | 提供 Sequencer 轨道、编辑器 UI 以及录制/回放配置的用户界面支持 |

---

## 使用场景

- **电影化过场动画优化**：当你需要在高保真场景中播放一段长达数分钟的预渲染过场动画时，使用本插件提前加载所需纹理、网格体等资源，避免播放期间出现低分辨率或加载卡顿。
- **实时渲染影片制作**：结合 Movie Render Pipeline 输出高质量视频片段时，可预先确保每帧所需数据都已存在于显存或内存中，缩短渲染时间。
- **大型开放世界游戏过场**：角色从广阔世界瞬移至特定场景时，提前流送附近资源，保证玩家体验不被打断。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CinematicPrestreaming)
- [模块 - CinematicPrestreaming](./CinematicPrestreaming.md)
- [模块 - CinematicPrestreamingEditor](./CinematicPrestreamingEditor.md)