# MovieSceneTextTrack

> Deprecated plugin. Text support moved to Movie Scene Tracks (built-in).

| 属性 | 值 |
|---|---|
| 分类 | Text |
| 默认启用 | false（`"Installed": false`） |
| 包含内容 | false |
| 模块 | MovieSceneTextTrack (Runtime), MovieSceneTextTrackEditor (Editor) |
| 创建时间 | 2023-06-09 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/MovieSceneTextTrack) | |

## 用途

**⚠️ 此插件已废弃（Deprecated）。**

MovieSceneTextTrack 原本为 Sequencer 提供 Text（文本）属性轨道支持，允许在 Sequencer 时间轴上对 `FText` 类型的属性做关键帧动画。在 UE 5.7 中，所有功能已迁移至引擎内置的 `MovieSceneTracks` 模块，此插件仅保留为兼容性重定向头文件（deprecated header redirects）。

如果你在旧代码中引用了此插件的头文件，编译器会发出 `UE_DEPRECATED(5.7, ...)` 警告，并自动重定向到新路径。**不应在新项目中启用此插件。**

## 使用场景

此插件已废弃，不再需要主动使用。以下信息仅供维护旧代码参考：

- 你在 Sequencer 中需要对 Text 属性做关键帧动画 → 使用内置的 MovieSceneTracks 即可，无需此插件
- 你的旧项目引用了 `MovieSceneTextTrack` 模块 → 编译仍可通过（有重定向），但应尽快迁移

## 蓝图用法

无。此插件不暴露任何 BlueprintCallable 函数或 BlueprintReadWrite 属性。

## C++ 用法

### ⚠️ 迁移指南

所有头文件已废弃，以下映射关系告诉你应该改用哪个新头文件：

| 旧路径（此插件） | 新路径（MovieSceneTracks 模块） |
|---|---|
| `MovieSceneTextTrack/MovieSceneTextTrack.h` | `Tracks/MovieSceneTextTrack.h` |
| `MovieSceneTextTrack/MovieSceneTextSection.h` | `Sections/MovieSceneTextSection.h` |
| `MovieSceneTextTrack/MovieSceneTextChannel.h` | `Channels/MovieSceneTextChannel.h` |
| `MovieSceneTextTrack/MovieSceneTextPropertySystem.h` | `Systems/MovieSceneTextPropertySystem.h` |
| `MovieSceneTextTrack/TextChannelEvaluatorSystem.h` | `Systems/TextChannelEvaluatorSystem.h` |

### FTextComponentTypes（已废弃）

`FTextComponentTypes` 是一个单例，提供 Sequencer ECS 所需的 Text 相关组件类型 ID：

```cpp
// 已废弃 —— 使用 FBuiltInComponentTypes 和 FMovieSceneTracksComponentTypes 代替
namespace UE::MovieScene
{
    struct UE_DEPRECATED(5.7, "Use FBuiltInComponentTypes and FMovieSceneTracksComponentTypes instead") FTextComponentTypes
    {
        static FTextComponentTypes* Get();
        static void Destroy();

        TComponentTypeID<FSourceTextChannel> TextChannel;   // 源文本通道
        TComponentTypeID<FText>              TextResult;     // 通道求值结果
        TPropertyComponents<FTextPropertyTraits> Text;       // Text 属性组件
    };
}
```

新代码应直接使用：
```cpp
#include "EntitySystem/BuiltInComponentTypes.h"
#include "MovieSceneTracksComponentTypes.h"
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `MovieScene` | Sequencer 核心框架 |
| `MovieSceneTracks` | **实际功能所在模块**（所有代码已迁移到此处） |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-08-07 | `b074e3451cb0` | Movie Scene: migrate text track to movie scene tracks | **关键变更**：将 Text Track 从独立插件迁移到 MovieSceneTracks 内置模块，原插件变为废弃重定向壳 |
| 2025-06-13 | `b3edcb219713` | Replace some usages of FORCEINLINE with inline in MovieScene modules | 代码规范化，将 `FORCEINLINE` 替换为 `inline` |
| 2024-12-02 | `027924bd09a3` | Sequencer: Added missing CurveValueType typedefs, SupportsDefaults, and EvaluateChannel | Sequencer 功能增强，为曲线值类型添加缺失的 typedef |

### 维护评价

- **状态：已废弃（Deprecated）**
- 创建于 2023-06-09，最初作为实验性插件（`IsExperimentalVersion: true`）
- 2025-08-07 最后一次实质性更新：将所有代码迁移到 MovieSceneTracks 模块
- 插件本身现在只剩空壳模块和重定向头文件，不再有独立功能
- **不推荐使用**：新项目应直接依赖 `MovieSceneTracks` 模块；旧项目应尽快迁移头文件引用
- 此插件可能在 UE 5.8 或之后的版本中被完全移除

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/MovieSceneTextTrack)
- 官方文档：无（`.uplugin` 中 DocsURL 为空）
