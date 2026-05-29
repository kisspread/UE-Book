# Cinematic Prestreaming

> Adds a way to record certain types of streaming data requests in cinematic cutscenes. The requests can then be played back in advance on the Sequencer timeline to pre-stream data during normal gameplay/rendering.

| 属性 | 值 |
|---|---|
| 中文名 | 影视预流送 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CinematicPrestreaming` (Runtime), `CinematicPrestreamingEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-19 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/CinematicPrestreaming) | |

## 用途

解决影视过场动画播放时数据流送（Streaming）延迟导致的画面卡顿或资产突然弹出问题。

在 Sequencer 播放影视序列时，纹理、网格体等流送资产可能因为未及时加载而出现明显的 Pop-in 或卡顿。本插件提供了一套**录制-回放**机制：

1. **录制阶段**：在编辑器中预演（Preview）Sequencer 轨道时，插件记录所有流送数据请求的时间戳和资源位置，生成预流送资产（Prestreaming Asset）
2. **回放阶段**：正式游戏运行时，Sequencer 在过场动画播放前，根据录制的时间线提前触发流送请求，使资产在真正需要前就已加载完毕

本质上是一个**流送数据的时间线录制器+预加载调度器**，让过场动画的资源加载变得可预测、可控制。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `CinematicPrestreaming` | Runtime | 核心运行时模块：预流送资产定义、Sequencer 轨道/节、录制回放逻辑、蓝图节点 |
| `CinematicPrestreamingEditor` | UncookedOnly | 编辑器模块：预流送资产编辑器、录制工作流 UI、Graph 节点、资产类型注册 |

## 使用场景

- 你正在制作大型开放世界游戏 → 过场动画中远景资产突然弹出 → 用本插件预录流送请求并提前加载
- 你需要确保影视级过场动画流畅无卡顿 → 录制流送时间线，让引擎提前 1-2 秒加载所需资源
- 你在 Sequencer 中制作复杂的镜头切换序列 → 不同镜头需要不同区域的资产 → 用预流送轨道统一管理加载时机

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/CinematicPrestreaming)
- [CinematicPrestreaming 模块文档](CinematicPrestreaming.md)
- [CinematicPrestreamingEditor 模块文档](CinematicPrestreamingEditor.md)