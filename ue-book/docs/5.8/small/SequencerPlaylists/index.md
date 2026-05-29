# Playlists

> Sequencer Playlists allow users to prepare, queue, and trigger level sequences on the fly during a virtual production session, providing increased flexibility and agility when interacting with animation on set.

| 属性 | 值 |
|---|---|
| 中文名 | 播放列表 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SequencerPlaylists` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-11-08 |
| 年龄标签 | 👴 老古董（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SequencerPlaylists) | |

## 用途

本插件扩展了 Sequencer（序列器）的功能，专门面向**虚拟制作 (Virtual Production)** 场景。它提供了一个“播放列表”系统，允许用户在虚拟拍摄现场实时地**准备、排队和触发**多个关卡序列（Level Sequences）。

传统方式下，如果需要按特定顺序播放一系列动画（如预滚动、动画表演、后滚动），用户通常需要编辑一个包含所有内容的长序列，或者在拍摄时手动切换。本插件通过引入 `USequencerPlaylist`（播放列表）和 `USequencerPlaylistPlayer`（播放器）对象，将这些序列组织成一个可动态调整的队列，并提供了方便的播放控制界面，极大提升了现场导演和技术美术与动画交互的**灵活性和敏捷性**。它还集成了多用户同步（Concert）和拍摄录制（Takes）功能，确保在协作环境中也能可靠工作。

## 使用场景

-   **虚拟拍摄现场**：导演希望在实时预览中，按特定顺序依次播放角色的“待机”、“行走”、“表演”和“退场”动画序列，而无需将它们全部剪辑到一个长序列中。
-   **动态动画编排**：技术美术需要快速测试不同动画片段（例如不同的台词表演）的组合与播放顺序，以找到最佳方案。
-   **预览与排练**：在正式录制Take前，使用播放列表来预演和确认一系列复杂的镜头动画。
-   **多用户协作环境**：在多人联机编辑会话中，确保所有客户端的序列预加载状态同步，避免播放时出现资源缺失。

## 蓝图用法

插件的核心蓝图功能集中在 `USequencerPlaylistPlayer` 类上，它代表一个播放列表的控制器。以下节点可用于在蓝图中动态操控播放列表。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Playlist` | 为播放器设置一个要控制的播放列表资产。 | `USequencerPlaylistPlayer` |
| `Get Playlist` | 获取当前播放器控制的播放列表资产。 | `USequencerPlaylistPlayer` |
| `Play Item` | 播放播放列表中的指定项（序列）。可指定播放方向（正向/反向）。 | `USequencerPlaylistPlayer` |
| `Pause Item` | 暂停/恢复播放指定项。 | `USequencerPlaylistPlayer` |
| `Stop Item` | 停止指定项的播放。 | `USequencerPlaylistPlayer` |
| `Reset Item` | 重置指定项（相当于停止并回到起始帧待命）。 | `USequencerPlaylistPlayer` |
| `Get Playback State` | 查询指定项的播放状态（是否正在播放、是否暂停、播放方向）。 | `USequencerPlaylistPlayer` |
| `Play All` | 播放播放列表中的所有项。 | `USequencerPlaylistPlayer` |
| `Stop All` | 停止播放列表中的所有项。 | `USequencerPlaylistPlayer` |
| `On Playlist Set` | 当播放器设置了一个新的播放列表时触发的委托。 | `USequencerPlaylistPlayer` |

### 使用示例（蓝图描述）

1.  **基础播放控制**：
    -   创建一个 `USequencerPlaylist` 资产，添加几个 `ULevelSequence` 资产作为播放项。
    -   在蓝图中，使用 `Create Object` 节点创建一个 `USequencerPlaylistPlayer` 的实例。
    -   调用 `Set Playlist` 节点，将创建好的播放列表资产连接到此播放器。
    -   之后，可以通过调用 `Play Item`（传入播放列表中的某个项）或 `Play All` 来开始播放。
    -   使用 `Get Playback State` 可以在 Tick 或事件中检查播放项是否完成。

2.  **响应状态变化**：
    -   绑定 `On Playlist Set` 委托，当播放列表被更换时，可以触发自定义逻辑（如更新UI）。
    -   结合 `Get Playback State` 节点，可以实现更复杂的逻辑，例如在某个序列播放完毕后自动播放下一个。

## C++ 用法

本插件的C++ API主要涉及创建播放器、管理播放列表以及注册自定义的播放项类型。

### 头文件引入

```cpp
#include "ISequencerPlaylistsModule.h"
#include "SequencerPlaylistPlayer.h"
#include "SequencerPlaylist.h"
```

### 基本用法

以下代码展示了如何在C++中获取模块接口并创建一个播放器来控制播放列表。

```cpp
// 获取播放列表模块的单例
ISequencerPlaylistsModule& PlaylistsModule = ISequencerPlaylistsModule::Get();

// 在编辑器工具或子系统中，通常可以获取一个 ISequencer 实例
// TSharedRef<ISequencer> Sequencer = ...;

// 通过模块接口为特定的ISequencer实例创建一个播放器
// 注意：在实际的编辑器面板(SSequencerPlaylistPanel)中，播放器是由子系统管理的
// 这里演示的是API概念
// USequencerPlaylistPlayer* NewPlayer = NewObject<USequencerPlaylistPlayer>();
// NewPlayer->SetPlaylist(MyPlaylistAsset);

// 控制播放
// if (USequencerPlaylistItem* FirstItem = MyPlaylistAsset->Items[0])
// {
//     NewPlayer->PlayItem(FirstItem);
// }
```
（来源：`ISequencerPlaylistsModule.h`, `SequencerPlaylistPlayer.h`）

### 进阶用法

插件采用**工厂模式**支持扩展。你可以注册自定义的播放项类型和对应的播放器实现，从而让播放列表支持播放除关卡序列之外的其它内容（如音频、蓝图事件等）。

1.  **定义自定义播放项和播放器**：
    ```cpp
    // MyCustomPlaylistItem.h
    UCLASS(BlueprintType)
    class UMyCustomPlaylistItem : public USequencerPlaylistItem
    {
        GENERATED_BODY()
    public:
        virtual FText GetDisplayName() override { return NSLOCTEXT("MyPlugin", "CustomItem", "Custom Item"); }
        // 自定义属性...
        UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Custom")
        int32 CustomParameter;
    };

    // MyCustomItemPlayer.h (实现 ISequencerPlaylistItemPlayer 接口)
    class FMyCustomItemPlayer : public ISequencerPlaylistItemPlayer
    {
    public:
        FMyCustomItemPlayer(TSharedRef<ISequencer> InSequencer) : WeakSequencer(InSequencer) {}

        virtual bool Play(USequencerPlaylistItem* Item, ESequencerPlaylistPlaybackDirection Direction) override
        {
            UMyCustomPlaylistItem* CustomItem = Cast<UMyCustomPlaylistItem>(Item);
            if (CustomItem)
            {
                // 实现播放逻辑，例如触发一段自定义代码或音频
                UE_LOG(LogTemp, Log, TEXT("Playing custom item with param: %d"), CustomItem->CustomParameter);
                return true; // 表示已处理
            }
            return false;
        }
        // ... 实现 TogglePause, Stop, AddHold, Reset, GetPlaybackState
    private:
        TWeakPtr<ISequencer> WeakSequencer;
    };
    ```

2.  **在模块启动时注册**：
    ```cpp
    // 在你的编辑器模块 StartupModule() 中
    #include "ISequencerPlaylistsModule.h"

    void FMyEditorModule::StartupModule()
    {
        ISequencerPlaylistsModule& PlaylistsModule = ISequencerPlaylistsModule::Get();
        PlaylistsModule.RegisterItemPlayer(
            UMyCustomPlaylistItem::StaticClass(),
            [](TSharedRef<ISequencer> Sequencer) -> TSharedPtr<ISequencerPlaylistItemPlayer>
            {
                return MakeShared<FMyCustomItemPlayer>(Sequencer);
            }
        );
    }
    ```
    （来源：`ISequencerPlaylistsModule.h` 中的 `RegisterItemPlayer` 接口）

## Demo 示例

一个最小的编辑器工具，创建一个播放列表并播放其中的序列。

```cpp
// MyPlaylistDemo.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "SequencerPlaylistPlayer.h"
#include "SequencerPlaylist.h"
#include "SequencerPlaylistItem_Sequence.h"

class UMyPlaylistDemo : public UObject
{
    GENERATED_BODY()

public:
    UPROPERTY(Transient)
    TObjectPtr<USequencerPlaylist> DemoPlaylist;

    UPROPERTY(Transient)
    TObjectPtr<USequencerPlaylistPlayer> DemoPlayer;

    UFUNCTION(BlueprintCallable, Category="Demo")
    void CreateAndPlayDemoPlaylist(ULevelSequence* SequenceA, ULevelSequence* SequenceB);
};
```

```cpp
// MyPlaylistDemo.cpp
#include "MyPlaylistDemo.h"
#include "ISequencerPlaylistsModule.h"

void UMyPlaylistDemo::CreateAndPlayDemoPlaylist(ULevelSequence* SequenceA, ULevelSequence* SequenceB)
{
    // 1. 创建临时播放列表
    DemoPlaylist = NewObject<USequencerPlaylist>(GetTransientPackage());
    DemoPlaylist->Description = FText::FromString(TEXT("Demo Playlist"));

    // 2. 添加两个序列项
    if (SequenceA)
    {
        USequencerPlaylistItem_Sequence* ItemA = NewObject<USequencerPlaylistItem_Sequence>(DemoPlaylist);
        ItemA->SetSequence(SequenceA);
        ItemA->PlaybackSpeed = 1.0f;
        DemoPlaylist->Items.Add(ItemA);
    }
    if (SequenceB)
    {
        USequencerPlaylistItem_Sequence* ItemB = NewObject<USequencerPlaylistItem_Sequence>(DemoPlaylist);
        ItemB->SetSequence(SequenceB);
        ItemB->PlaybackSpeed = 1.5f;
        ItemB->NumLoops = 1; // 循环1次，即播放2遍
        DemoPlaylist->Items.Add(ItemB);
    }

    // 3. 创建播放器并设置播放列表
    // 注意：在实际插件中，播放器通常由编辑器子系统管理，并关联到具体的Sequencer实例。
    // 这里仅为演示核心API。
    DemoPlayer = NewObject<USequencerPlaylistPlayer>(GetTransientPackage());
    DemoPlayer->SetPlaylist(DemoPlaylist);

    // 4. 播放所有项
    if (DemoPlaylist->Items.Num() > 0)
    {
        // 播放第一项
        DemoPlayer->PlayItem(DemoPlaylist->Items[0]);
        // 或者直接播放全部: DemoPlayer->PlayAll();
    }
}
```

## 模块依赖

从插件的 `.uplugin` 元数据可以看出，本插件依赖于以下核心虚拟制作和协作插件。

| 模块 | 用途 |
|---|---|
| `ConcertSyncClient` | 多用户协作同步客户端，用于在多机联机会话中同步播放列表状态和序列预加载信息。 |
| `ConcertSyncCore` | 多用户协作同步核心，提供基础的会话和事件处理机制。 |
| `Takes` | 集成拍摄录制系统，确保播放列表的播放能与Take录制流程协同工作（如进入/退出录制状态）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `05be130a` | Playing a playlist item in reverse with NumLoops > 0 hit EXCEPTION_INT_DIVIDE_BY_ZERO inside FMovieS... | 修复了反向播放循环次数大于0的播放项时发生的整数除零崩溃。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的UE_LOG宏迁移到新的UE_LOGF宏，是引擎日志系统的统一更新。 |
| 2024-07-15 | `927c5d41` | Sequencer: Added time-warp capabilities to sequences, sub-sections and skeletal animation sections | 引擎级功能更新：为序列、子片段和骨骼动画片段添加了时间扭曲能力。 |
| 2023-08-08 | `c40d2094` | Fix display of preload column when Multi-user session is not active | 修复了在未激活多用户会话时，预加载状态列显示不正确的问题。 |
| 2023-07-20 | `a28f239e` | Use the transient package for playlists | 改为使用临时包来存储播放列表数据，避免污染资产包。 |

### 维护评价

- **年龄**：插件创建于2021年底，至今约有4年半历史，属于“老古董”级别。
- **近期活跃度**：最近一次实质性功能更新（时间扭曲）在2024年7月。2026年的提交主要是bug修复和日志迁移。维护频率**不频繁**。
- **状态**：插件仍在维护中，没有被标记为废弃。但作为 `IsBetaVersion=true` 的**实验性功能**，其API和功能可能发生变化。
- **已知限制**：从历史commit看，曾存在反向循环播放的崩溃问题，已在最新修复中解决。与多用户同步的集成较为紧密，单独使用时部分列（如预加载状态）可能显示异常。
- **推荐度**：适用于正在开展虚拟制作项目，并且需要灵活编排实时动画的团队。由于是实验性功能，建议在项目中谨慎引入，并做好应对API变更的准备。对于不需要虚拟制作功能的普通项目，无需启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SequencerPlaylists)
- [测试用例]（注：在提供的源码信息中未发现专门的测试用例文件路径，可能测试集成在更大的模块测试中）