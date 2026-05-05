# Playlists (Sequencer Playlists)

> Sequencer Playlists allow users to prepare, queue, and trigger level sequences on the fly during a virtual production session, providing increased flexibility and agility when interacting with animation on set.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | 否（需手动启用） |
| 包含内容 | 否 |
| 模块 | SequencerPlaylists (Editor) |
| 创建时间 | 2021-11-07 |
| 年龄标签 | 🆕（约4.5年） |
| Beta 版本 | 是 (IsBetaVersion=true) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SequencerPlaylists) | |

## 用途

Sequencer Playlists 是一个**编辑器专用**插件，解决的是虚拟制片（Virtual Production）场景下的一个核心痛点：在片场需要快速、灵活地按需触发和编排多个 Level Sequence 动画。

传统的 Sequencer 工作流是打开一个 Level Sequence、点击播放。但在 VP 现场，导演可能需要：
- 按顺序触发一系列动画（比如：先播进场动画，再播表情，再播退场）
- 随时暂停某个动画并保持在当前帧
- 反向播放某个动画
- 循环播放某段动画 N 次
- 多个动画可以排队播放或同时播放

Playlists 插件将这些能力封装为一个 **Playlist 资产**，每个 Playlist 包含多个 Item，每个 Item 引用一个 Level Sequence，并可配置播放速度、循环次数、起止帧偏移等参数。它与 **Take Recorder** 深度集成——录制时会将 Playlist 中的序列作为 Sub-Section 注入到当前 Sequencer 的根序列中。

## 使用场景

- **虚拟制片现场**：你有一组预定义的动画序列，需要在拍摄时按需触发 → 用 Sequencer Playlists
- **Take Recorder 配合**：你在用 Take Recorder 录制表演，需要同时触发多个 Level Sequence 作为动画层 → 用 Sequencer Playlists
- **动画预览/排练**：你需要快速切换、排队播放不同动画组合来预览效果 → 用 Sequencer Playlists
- **多用户协作**：你在 Multi-User Session 中工作，需要确保所有客户端都预加载了正确的序列 → Playlists 内建了 Concert/Multi-User 预加载同步机制

## 编辑器用法

Sequencer Playlists 主要通过编辑器 UI 操作，而非蓝图节点。它提供一个专用的 **Playlist 面板**（类似 Sequencer Editor 的 Tab）。

### 打开 Playlist 面板

1. 启用插件后，在编辑器菜单中找到 Sequencer Playlists 入口
2. 打开后会出现一个停靠面板，包含：
   - **工具栏**：新建、打开、保存 Playlist
   - **Item 列表**：显示当前 Playlist 中的所有 Item
   - **传输控制**：Play All / Pause All / Stop All / Reset All

### 添加 Item

- 在面板中点击 **Add Sequence** 按钮
- 或从 Content Browser 拖拽 Level Sequence 资产到面板中

### 每个 Item 的属性

| 属性 | 说明 |
|---|---|
| Sequence | 引用的 Level Sequence 资产 |
| StartFrameOffset | 裁剪序列起始帧（向内偏移） |
| EndFrameOffset | 裁剪序列结束帧（向内偏移） |
| NumLoops | 循环次数（0=单次播放，1=播放两次，以此类推） |
| PlaybackSpeed | 播放速度倍率（1.0=原速） |
| bMute | 静音/禁用此 Item |

### Item 播放控制

每个 Item 有独立的播放按钮：
- **▶ Play**：正向播放
- **◀ Play Reverse**：反向播放
- **⏸ Pause**：暂停（再次点击恢复）
- **⏹ Stop**：停止
- **↻ Reset**：重置到初始状态（若启用了 Hold At First Frame，会停在第一帧）

### 全局控制

面板顶部的传输控制按钮：
- **Play All** / **Play All Reverse**：同时播放所有 Item
- **Pause All**：暂停所有 Item
- **Stop All**：停止所有 Item
- **Reset All**：重置所有 Item

### Playlist 资产管理

- **New Playlist**：创建新的空 Playlist（瞬态，需手动保存）
- **Open Playlist**：从 Content Browser 打开已保存的 Playlist 资产
- **Save / Save As**：将当前 Playlist 保存为资产

## C++ 用法

### 头文件引入

```cpp
#include "SequencerPlaylist.h"
#include "SequencerPlaylistPlayer.h"
#include "SequencerPlaylistItem_Sequence.h"
#include "ISequencerPlaylistsModule.h"
```

### 核心类结构

```
USequencerPlaylist          — Playlist 资产，包含 Items 数组
├── USequencerPlaylistItem  — 抽象基类，表示一个播放项
│   └── USequencerPlaylistItem_Sequence  — 引用 Level Sequence 的具体 Item
└── USequencerPlaylistPlayer — 播放控制器，负责实际播放逻辑
```

### 通过 Player 控制播放

`USequencerPlaylistPlayer` 是核心播放控制器，提供以下 BlueprintCallable 方法：

```cpp
// 设置 Playlist
void SetPlaylist(USequencerPlaylist* InPlaylist);

// 单个 Item 控制
bool PlayItem(USequencerPlaylistItem* Item, ESequencerPlaylistPlaybackDirection Direction = Forward);
bool PauseItem(USequencerPlaylistItem* Item);
bool StopItem(USequencerPlaylistItem* Item);
bool ResetItem(USequencerPlaylistItem* Item);
FSequencerPlaylistPlaybackState GetPlaybackState(USequencerPlaylistItem* Item);

// 全局控制
bool PlayAll(ESequencerPlaylistPlaybackDirection Direction = Forward);
bool PauseAll();
bool StopAll();
bool ResetAll();
```

### 播放方向

```cpp
UENUM(BlueprintType)
enum class ESequencerPlaylistPlaybackDirection : uint8
{
    Forward,
    Reverse,
};
```

### 查询播放状态

```cpp
USTRUCT(BlueprintType)
struct FSequencerPlaylistPlaybackState
{
    uint8 bIsPlaying : 1;
    uint8 bIsPaused : 1;
    ESequencerPlaylistPlaybackDirection PlaybackDirection;
};
```

### 工作原理

播放一个 Item 时，Player 实际上是在当前 Sequencer 的**根序列**中创建一个 `UMovieSceneSubSection`（子序列段），将目标 Level Sequence 作为子序列插入。这使得 Take Recorder 可以录制这些子序列的输出。

具体流程：
1. `PlayItem()` → 在根序列的 Sub Track 上添加一个 Sub Section
2. Sub Section 的起止帧由当前时间 + Item 的偏移量决定
3. 播放速度通过 `TimeScale` 参数控制
4. 循环通过 `bCanLoop` + 计算总持续时间实现
5. 反向播放通过负 `TimeScale` 实现
6. 暂停通过插入一个 `TimeScale=0` 的 Hold Section 实现

## Demo 示例

### 最小使用示例（C++）

```cpp
// MyPlaylistActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyPlaylistActor.generated.h"

class USequencerPlaylist;
class USequencerPlaylistPlayer;
class USequencerPlaylistItem_Sequence;

UCLASS()
class AMyPlaylistActor : public AActor
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category="Playlist")
    TObjectPtr<USequencerPlaylist> MyPlaylist;

    UFUNCTION(BlueprintCallable, Category="Playlist")
    void PlayFirstItem();

    UFUNCTION(BlueprintCallable, Category="Playlist")
    void PlayAllItems();

private:
    UPROPERTY(Transient)
    TObjectPtr<USequencerPlaylistPlayer> Player;
};
```

```cpp
// MyPlaylistActor.cpp
#include "MyPlaylistActor.h"
#include "SequencerPlaylist.h"
#include "SequencerPlaylistPlayer.h"
#include "SequencerPlaylistItem_Sequence.h"

void AMyPlaylistActor::PlayFirstItem()
{
    if (!MyPlaylist || MyPlaylist->Items.Num() == 0)
    {
        return;
    }

    if (!Player)
    {
        Player = NewObject<USequencerPlaylistPlayer>();
        Player->SetPlaylist(MyPlaylist);
    }

    Player->PlayItem(MyPlaylist->Items[0], ESequencerPlaylistPlaybackDirection::Forward);
}

void AMyPlaylistActor::PlayAllItems()
{
    if (!Player)
    {
        Player = NewObject<USequencerPlaylistPlayer>();
        Player->SetPlaylist(MyPlaylist);
    }

    Player->PlayAll(ESequencerPlaylistPlaybackDirection::Forward);
}
```

### Build.cs 依赖

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "SequencerPlaylists",
});
```

> **注意**：SequencerPlaylists 是 Editor 模块，只能在编辑器环境下使用，不能在打包后的运行时使用。

## 模块依赖

以下是 SequencerPlaylists 模块的依赖列表：

| 模块 | 用途 |
|---|---|
| `Core` | 引擎核心（公开依赖） |
| `LevelSequence` | Level Sequence 资产支持 |
| `MovieScene` | Sequencer 底层框架 |
| `LevelSequenceEditor` | Sequencer 编辑器集成 |
| `TakeRecorder` | 录制集成 |
| `TakesCore` | Takes 系统核心 |
| `MovieSceneTools` | Sequencer 工具集 |
| `UnrealEd` | 编辑器框架 |
| `Slate` / `SlateCore` | UI 框架 |
| `PropertyEditor` | 属性面板 |
| `ToolMenus` | 菜单系统 |
| `ConcertClient` / `ConcertSyncClient` / `ConcertSyncCore` | Multi-User Session 集成 |
| `EditorSubsystem` | 编辑器子系统基类 |

### 插件依赖

| 插件 | 用途 |
|---|---|
| `ConcertSyncClient` | Multi-User 同步客户端 |
| `ConcertSyncCore` | Multi-User 同步核心 |
| `Takes` | Takes 系统 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2024-07-15 | `927c5d41` | Sequencer: Added time-warp capabilities to sequences, sub-sections and skeletal animation sections — 为 Sequencer 添加了时间扭曲功能，影响子序列段 |
| 2023-08-08 | `c40d2094` | Fix display of preload column when Multi-user session is not active — 修复预加载列在非多用户会话时的显示问题 |
| 2023-07-20 | `a28f239e` | Use the transient package for playlists — 改用瞬态包来存储 Playlist |

### 维护评价

- **创建时间**：2021 年 11 月，约 4 年前
- **Beta 状态**：`IsBetaVersion=true`，表明 Epic 仍视其为 Beta 功能
- **最近更新**：最后一次实质性更新在 2024 年 7 月（距今不到 2 年），但该更新是 Sequencer 整体的功能增强而非 Playlists 专属
- **Playlists 专属更新**：2023 年 8 月之后未见 Playlists 专属的 bug 修复或功能增强
- **测试用例**：在插件目录和 Engine/Tests 中均未发现自动化测试用例
- **维护评价**：**维护不活跃**。插件功能基本完整，但处于 Beta 状态且近两年无专属更新。作为 VP 现场工具仍有使用价值，但需注意其 Beta 标签意味着 API 可能变动。

**推荐使用**：如果你的项目是虚拟制片场景，且需要在片场灵活编排动画，这个插件是可用的。但不建议在非 VP 项目中依赖它，且需要注意它只在编辑器中可用（Editor 模块），无法打包到运行时。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SequencerPlaylists)
- [官方文档]()（无，.uplugin 中 DocsURL 为空）
