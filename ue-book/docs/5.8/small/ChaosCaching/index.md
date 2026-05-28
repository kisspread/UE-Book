# ChaosCaching

> Chaos Cache asset support for recording and playing back physics simulations

| 属性 | 值 |
|---|---|
| 中文名 | 物理缓存 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（缓存资产） |
| 模块 | `ChaosCaching` (Runtime), `ChaosCachingEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-09-01 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCaching) | |

## 用途

ChaosCaching 是基于 Chaos 物理系统的缓存框架，用于**录制物理模拟结果并回放**。它解决的核心问题是：物理模拟具有随机性和不可复现性，而影视、过场动画等场景需要物理效果完全一致可复现。

该插件允许你：
- 在编辑器或运行时录制 Chaos 物理系统的模拟数据（刚体、几何体碎片、粒子等）
- 将模拟结果保存为 Cache 资产
- 回放时跳过物理计算，直接使用缓存数据驱动物体动画，保证帧一致

该插件默认关闭（`EnabledByDefault: false`）且标记为实验性，需要手动在插件设置中启用。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [`ChaosCaching`](ChaosCaching.md) | Runtime | 核心缓存运行时：Cache 资产、适配器、序列化、回放逻辑 |
| [`ChaosCachingEditor`](ChaosCachingEditor.md) | Editor | 编辑器扩展：资产编辑器 UI、Cache 采集器面板、内容浏览器集成 |

## 使用场景

- 你在做影视级过场动画，需要爆炸、坍塌等物理效果每次播放完全一致 → 用 ChaosCaching 录制并回放
- 你需要在 Sequencer 时间线上精确控制物理碎裂的时间点 → Cache 资产可与 Sequencer 集成
- 你希望在关卡中放置预计算的物理破坏效果，避免运行时物理计算开销 → 用缓存回放替代实时模拟
- 你需要在多台机器上播放相同的物理效果（如多人游戏中的同步破坏） → 缓存回放保证确定性

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosCaching)
- [ChaosCaching 模块文档](ChaosCaching.md)
- [ChaosCachingEditor 模块文档](ChaosCachingEditor.md)