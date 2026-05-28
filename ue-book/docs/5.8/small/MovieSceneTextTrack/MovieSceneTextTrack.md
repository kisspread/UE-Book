# MovieSceneTextTrack

> Deprecated plugin. Text support moved to Movie Scene Tracks (built-in).

| 属性 | 值 |
|---|---|
| 中文名 | 场景文字轨道 |
| 分类 | Text |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MovieSceneTextTrack` (Runtime), `MovieSceneTextTrackEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-06-09 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/MovieSceneTextTrack) | |

## 用途

**⚠️ 此插件已废弃，不应在新项目中使用。**

此插件原本为 Sequencer（过场动画编辑器）提供 **Text 属性的帧轨道支持**，用于对 UMG Widget、3D Text 等包含 `FText` 类型属性的组件进行关键帧录制，同时支持本地化文本。

自 UE 5.7 起，该功能已完整迁移至引擎内置的 `MovieSceneTracks` 模块。本插件的所有公开头文件现均为弃用重定向，保留仅为向后兼容。

## 使用场景

~~你需要在 Sequencer 中对 `FText` 属性设置关键帧动画~~ → **请直接使用内置的 `MovieSceneTracks` 模块，无需额外插件。**

## 蓝图用法

本插件无可用蓝图节点。所有功能已迁移至 `MovieSceneTracks` 模块，相关节点请查阅该模块文档。

## C++ 用法

**⚠️ 以下 API 已全部废弃（UE 5.7+），仅作历史参考。新代码请使用 `MovieSceneTracks` 模块中的对应类。**

### 头文件引入

所有头文件均为弃用重定向，include 后实际指向 `MovieSceneTracks` 模块：

```cpp
// 全部已废弃 — 直接使用 MovieSceneTracks 模块的对应头文件
#include "MovieSceneTextTrack.h"          // → Tracks/MovieSceneTextTrack.h (MovieSceneTracks)
#include "MovieSceneTextSection.h"        // → Sections/MovieSceneTextSection.h (MovieSceneTracks)
#include "MovieSceneTextChannel.h"        // → Channels/MovieSceneTextChannel.h (MovieSceneTracks)
#include "TextChannelEvaluatorSystem.h"   // → Systems/TextChannelEvaluatorSystem.h (MovieSceneTracks)
#include "MovieSceneTextPropertySystem.h" // → Systems/MovieSceneTextPropertySystem.h (MovieSceneTracks)
#include "TextComponentTypes.h"           // 已废弃，使用 FBuiltInComponentTypes + FMovieSceneTracksComponentTypes
```

### 基本用法（已废弃）

历史代码中通过 `FTextComponentTypes` 访问 ECS 组件类型：

```cpp
// ⚠️ 已废弃，仅供理解旧代码
using namespace UE::MovieScene;

FTextComponentTypes* TextTypes = FTextComponentTypes::Get();

// 获取文本通道组件类型（FSourceTextChannel）
TComponentTypeID<FSourceTextChannel> Channel = TextTypes->TextChannel;

// 获取文本求值结果组件类型（FText）
TComponentTypeID<FText> Result = TextTypes->TextResult;

// 使用完毕后销毁
FTextComponentTypes::Destroy();
```

**迁移方案**：改用 `FBuiltInComponentTypes` 和 `FMovieSceneTracksComponentTypes` 中的对应字段。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer 核心模块 |
| `MovieSceneTracks` | 已迁移至该模块，替代本插件功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-08-07 | `b074e345` | Movie Scene: migrate text track to movie scene tracks | 将文字轨道功能迁移至内置 MovieSceneTracks 模块 |
| 2025-06-13 | `b3edcb21` | Replace some usages of FORCEINLINE with inline in MovieScene modules. | 批量替换 FORCEINLINE 为 inline（代码规范化） |
| 2024-12-02 | `027924bd` | Sequencer: Added missing CurveValueType typedefs, SupportsDefaults, and EvaluateChannel | 补充缺失的曲线类型定义和求值接口 |
| 2024-11-27 | `33517915` | Movied previously committed squencer changes for music mode into a new Musical Mode plugin | 将音乐模式相关改动迁移到独立插件 |
| 2024-10-23 | `6145872a` | MUSIC_IN_SEQUENCER [Initial Check-In] | Sequencer 音乐功能初始提交 |

### 维护评价

**⛔ 已废弃 — 不推荐使用。**

- 创建于 2023 年 6 月，最初作为实验性插件引入 Sequencer 的 Text 属性关键帧支持
- 2025 年 8 月最后一次实质性更新将全部功能迁移至内置 `MovieSceneTracks` 模块
- `.uplugin` 中 `Installed: false`，说明该插件默认不安装
- 所有公开头文件均为 `UE_DEPRECATED_HEADER` 重定向
- `FTextComponentTypes` 结构体标记为 `UE_DEPRECATED(5.7, ...)`
- 此插件保留仅为向后兼容旧代码中的 `#include`，新项目不应引入

**迁移指引**：将所有对本插件头文件的引用改为直接引用 `MovieSceneTracks` 模块的对应头文件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/MovieSceneTextTrack)
- [MovieSceneTracks 模块（替代品）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Source/Runtime/MovieSceneTracks)