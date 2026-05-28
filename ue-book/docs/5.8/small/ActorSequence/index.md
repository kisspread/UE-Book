# Actor Sequence (Experimental)

> Runtime for embedded actor sequences（照抄）

| 属性 | 值 |
|---|---|
| 中文名 | Actor 内嵌序列 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ActorSequence` (Runtime), `ActorSequenceEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2017-09-07 |
| 年龄标签 | 🏛️ 文物（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/ActorSequence) | |

## 用途

ActorSequence 插件提供了一种将 Sequencer 序列**直接嵌入到 Actor 内部**的能力，而非依赖独立的 Level Sequence 资产。

核心机制是 `UActorSequenceComponent`——一个可添加到任意 Actor 上的组件，它内部持有一个 `UActorSequence` 对象。这个内嵌序列可以驱动该 Actor 自身及子 Actor 的属性动画，相当于将 Sequencer 的功能微型化并绑定到单个 Actor 上。

与独立 Level Sequence 的区别：
- **无需外部资产**：序列数据直接存储在 Actor 内部（通过 `UActorSequenceComponent`）
- **作用域限定**：自动绑定拥有者 Actor 及其子层级
- **轻量级**：适合单个 Actor 的自包含动画，不需要 Sequencer 全局编排

Runtime 模块提供播放引擎，Editor 模块提供序列编辑 UI（通过 `UActorSequence` 继承自 `UMovieSceneSequence`，可复用 Sequencer 编辑器）。

> ⚠️ 该插件标记为 `IsBetaVersion=true`，已保持"实验性"状态长达 9 年。虽然仍在维护，但 Epic 未正式宣布其为稳定功能。

## 使用场景

- 你需要给门、按钮、宝箱等 Actor 添加开合动画，且不想创建独立的 Level Sequence 资产
- 你需要一个自包含的 Actor 级别动画，只驱动自身和子 Actor 的属性
- 你在做 UI Widget 动画（UMG Widget 内嵌序列）
- 你需要在多人游戏中让 Actor 携带动画数据，由 `UActorSequenceComponent` 自动处理复制

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `ActorSequence` | Runtime | 核心运行时：`UActorSequenceComponent`、`UActorSequence`、绑定/播放逻辑 |
| `ActorSequenceEditor` | Editor | 编辑器扩展：在 Sequencer 编辑器中集成内嵌序列的编辑 UI |

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play` | 正向播放内嵌序列 | `UActorSequenceComponent` |
| `PlayReverse` | 反向播放内嵌序列 | `UActorSequenceComponent` |
| `Stop` | 停止播放 | `UActorSequenceComponent` |
| `Pause` | 暂停播放 | `UActorSequenceComponent` |
| `IsPlaying` | 查询是否正在播放 | `UActorSequenceComponent` |

### 使用示例

1. 在 Actor 上添加 `ActorSequenceComponent`
2. 在编辑器中选中该组件，使用 Sequencer 面板编辑内嵌序列
3. 通过蓝图调用 `Play` / `PlayReverse` 触发动画

## C++ 用法

### 头文件引入

```cpp
#include "ActorSequenceComponent.h"
#include "ActorSequence.h"
```

### 基本用法

```cpp
// 获取 Actor 上的 Sequence Component 并播放
UActorSequenceComponent* SeqComp = MyActor->FindComponentByClass<UActorSequenceComponent>();
if (SeqComp)
{
    SeqComp->Play();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer 核心框架（UMovieSceneSequence 基类） |
| `MovieSceneTracks` | Sequencer 轨道类型 |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-10 | `c03b3afd` | PR #14610: Rep layout mismatch in level sequence player due to with editoronly data property | 修复序列播放器中仅编辑器数据属性导致的复制布局不匹配 |
| 2026-03-20 | `992fad6c` | Gameplay systems deprecation removal pass for 5.4 and earlier | 清理 5.4 及更早版本的废弃代码 |
| 2025-09-25 | `f04d06c7` | Sequencer: Limit Viewport Selection UX Tweaks | Sequencer 视口选择 UX 调整 |
| 2025-09-10 | `bb165be8` | UMG: Disable Dynamic Possession menu if it's not supported | UMG 动态占有菜单在不支持时禁用 |
| 2025-07-14 | `b010bdd4` | PR #13519: [Sequences] Add PlayReverse function to actor sequence components | 新增反向播放功能 |

### 维护评价

该插件自 2017 年创建以来持续有更新，最近一次改动在 2026 年 4 月，属于**活跃维护**状态。但需注意：它始终保持 `IsBetaVersion=true`，长达 9 年未"毕业"为正式功能。新增的 `PlayReverse` 功能（2025-07）说明 Epic 仍在积极增强其能力。

**推荐使用**：适合需要轻量级 Actor 内嵌动画的场景，但要做好"实验性功能可能变更 API"的心理准备。对于复杂的、多 Actor 协同的序列编排，仍建议使用独立的 Level Sequence 资产。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/ActorSequence)
- [ActorSequence 运行时模块](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/MovieScene/ActorSequence/Source/ActorSequence/ActorSequence.Build.cs)
- [ActorSequenceEditor 编辑器模块](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/MovieScene/ActorSequence/Source/ActorSequenceEditor/ActorSequenceEditor.Build.cs)