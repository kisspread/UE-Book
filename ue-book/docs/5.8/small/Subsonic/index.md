# Subsonic

> Subsonic is a high-level audio authoring and playback system. This plugin is experimental and as such there is no guarantee of backward compatibility.

| 属性 | 值 |
|---|---|
| 中文名 | 次声波 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具与核心资产） |
| 模块 | `SubsonicCore` (Runtime), `SubsonicEditor` (Runtime), `SubsonicEngine` (Runtime), `SubsonicEngineTest` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic) | |

## 用途
Subsonic 是一个实验性的高级音频系统，旨在提供比 UE 标准音频引擎（如 Audio Mixer）更强大、更直观的音频内容创作与回放功能。它通过一个分层架构，将核心运行时、编辑器工具、引擎集成和测试框架分离，专注于解决复杂音频体验（如交互式音乐、环境声景设计、多轨混音）的创建和管理难题。

## 使用场景
- 你需要为游戏创建一个动态、分支的音乐系统，音乐能够根据玩家行为和游戏状态无缝切换、混合。
- 你在设计一个 VR 或沉浸式应用，需要精确控制 3D 空间中的音频源、混响和声场。
- 你希望拥有一个比传统波形编辑更高级的编辑器内音频创作工具，用于可视化地编排音频事件和效果。
- 你正在尝试 UE 的下一代音频特性，并愿意接受其实验性状态和潜在的 API 变动。

## 蓝图用法
> 由于此插件处于实验初期，公开的蓝图 API 可能有限或不稳定。以下功能基于模块结构和音频系统共性推断。

### 核心节点
| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play` / `Stop` | 控制音频资产的播放与停止 | `USubsonicSource` (推测) |
| `SetVolume` / `SetPitch` | 动态调整音量与音高 | `USubsonicSource` (推测) |
| `TriggerCue` | 触发音频剪辑或音乐段落 | `USubsonicDirector` (推测) |

### 使用示例（蓝图描述）
在蓝图中，你可能会创建一个 `SubsonicDirector` 资产来管理音乐的各个部分。通过 `Get` 节点获取该 Director 的引用，然后调用其 `TransitionTo` 函数，传入代表不同游戏状态（如“探索”、“战斗”）的音频剪辑标签，即可实现平滑的音乐过渡。

## C++ 用法
> 注意：此插件为实验性内容，API 可能随时变更。以下为模块化使用的示例性指引。

### 头文件引入
根据你的需求，引入对应模块的头文件。
```cpp
// 核心功能
#include "SubsonicCore.h"

// 引擎集成与高级功能
#include "SubsonicEngine.h"

// 编辑器扩展（仅在编辑器模块使用）
#if WITH_EDITOR
#include "SubsonicEditor.h"
#endif
```

### 基本用法
假设使用核心模块来管理一个简单的音频源。
```cpp
// 创建一个 Subsonic 核心音频源对象
TObjectPtr<USubsonicSource> AudioSource = NewObject<USubsonicSource>();

// 加载或分配一个音频资产
AudioSource->SetSoundWave(MySoundWaveAsset);

// 在游戏逻辑中播放
if (AudioSource && MySoundWaveAsset)
{
    AudioSource->Play();
}
```

### 进阶用法
结合引擎模块，可能用于创建更复杂的音频交互逻辑。
```cpp
// 获取 Subsonic 引擎子系统（如果存在）
USubsonicEngineSubsystem* SubsonicSubsystem = GetGameInstance()->GetSubsystem<USubsonicEngineSubsystem>();

if (SubsonicSubsystem)
{
    // 请求播放一个标记为“环境”的音频场景，并淡入
    FSubsonicPlayRequest PlayRequest;
    PlayRequest.SceneTag = FName("AmbientForest");
    PlayRequest.FadeInDuration = 2.0f;
    SubsonicSubsystem->PlayScene(PlayRequest);
}
```
*(以上代码为根据模块功能的合理推测，实际接口请参考最新头文件。)*

## Demo 示例
> 由于插件实验性且 API 不稳定，暂无可直接编译的最小示例。一个典型的最小使用可能涉及：
> 1.  在你的模块 `Build.cs` 中添加对 `SubsonicCore` 和 `SubsonicEngine` 的依赖。
> 2.  在游戏模块初始化时，通过子系统或手动创建的方式实例化 `SubsonicCore` 中的管理类。
> 3.  加载一个音频资产（如 `USoundWave`），并通过 Subsonic 的接口进行播放和控制。
> 4.  在编辑器中，利用 `SubsonicEditor` 提供的工具进行音频场景的编辑和预览。

## 模块依赖
此插件自身高度模块化。要在你的项目中使用它，你的模块需要依赖以下独特的模块：

| 模块 | 用途 |
|---|---|
| `SubsonicCore` | 引入核心音频数据类型、管理类和基础播放功能。 |
| `SubsonicEngine` | 引入与 UE 引擎深度集成的音频子系统、场景管理和高级功能。 |
| `SubsonicEditor` | 引入编辑器内的专用工具、资产编辑器和自定义界面。 |

**构建依赖示例** (YourModule.Build.cs):
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "SubsonicCore",
    "SubsonicEngine"
});

if (Target.bBuildEditor)
{
    PrivateDependencyModuleNames.Add("SubsonicEditor");
}
```

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `0ad6a1ff` | [Audio, CIS] Fixup bad merge: Revert wholesale Subsonic Subscriber stomp; apply minimal non-deprecat | 修复一次糟糕的合并，回退了对 Subsonic 订阅者系统的错误覆盖，并应用了最小化的非废弃修复。 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决了与 `FSoundWaveData` API 废弃修复相关的合并冲突。 |
| 2026-04-23 | `129c3dc2` | Fix/silence PVS warnings | 修复或静默了 PVS（可能的并行验证系统）警告。 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 在内容浏览器的新建菜单中添加了音频（可能与 Subsonic 相关）子菜单。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移到 `UE_LOGF`（可能是一种新的日志格式化方式）。 |

### 维护评价
Subsonic 是一个非常新的插件（创建于 2026 年初），目前仍处于**实验性阶段**。从 Git 提交记录看，它在过去一个月内有持续的活动，包括合并修复、编译警告清理和编辑器功能集成，表明 Epic 内部仍在积极开发和集成此功能。

**主要特点与风险**：
1.  **高度实验性**：官方明确声明无向后兼容保证，API 和功能可能发生破坏性更改。
2.  **活跃开发中**：提交频率表明它并非弃用状态，而是正在成熟。
3.  **架构清晰**：Core/Engine/Editor/Test 的分层结构表明这是一个设计目标明确的系统。

**建议**：适合用于研究下一代 UE 音频技术方向，或在不介意 API 稳定性的原型项目中尝试。**不建议**在需要长期维护的正式生产项目中使用，除非你愿意并有能力跟进其频繁的 API 变更。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic/Source/SubsonicEngineTest)