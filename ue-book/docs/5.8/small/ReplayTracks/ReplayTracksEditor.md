# Replay Tracks (Experimental)

> Sequence tracks for playing recorded gameplay（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 回放轨道 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ReplayTracks` (Runtime), `ReplayTracksEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-04-08 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/ReplayTracks) | |

## 用途

这个插件将 **游戏回放录制** 功能与 **Sequencer 序列编辑器** 集成，允许您在 Sequencer 时间轴上精确控制和编辑预先录制的游戏过程。它的核心价值在于：将回放数据作为序列轨道进行处理，可以像编辑动画或摄像机轨道一样，对游戏回放进行时间同步、剪辑和混合，从而为游戏预告片、电影式过场动画或回放分析工具提供强大的支持。

## 使用场景

- 您制作了一个游戏关卡的演示回放，希望将其与其它的摄像机、音效、字幕等序列轨道精确对齐，制作成一段完整的过场动画。
- 您需要将多局玩家的游戏回放剪辑、合并，并叠加后期特效，以制作游戏宣传视频。
- 您在开发回放分析工具，希望将回放的关键帧数据输出到 Sequencer 中进行逐帧检视和数据可视化。

## 蓝图用法

此插件主要在 Sequencer 编辑器界面中提供新的轨道类型和编辑器控件，不直接暴露蓝图节点。

### 核心节点（编辑器操作）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddReplayTrack` (菜单项) | 在 Sequencer 菜单中添加一个 “Replay Track”。 | `FReplayTrackEditor` |
| `ToggleReplay` (按钮) | 控制 Sequencer 中回放轨道的播放/暂停/跳转。 | `FReplayTrackEditor` |

### 使用示例（蓝图描述）

1.  在 Sequencer 编辑器中，右键点击轨道区域，选择 **“添加轨道” -> “Replay Track”**。
2.  在轨道上创建区段（Section），该区段将关联一个已录制的回放数据。
3.  使用轨道上的 **“ToggleReplay”** 按钮，可以像控制普通动画一样，播放、暂停或拖拽时间滑块来预览回放。
4.  通过拖拽区段，可以调整回放在整个序列中的播放时机和时长。

## C++ 用法

该插件的 C++ 接口主要面向 Sequencer 的编辑器扩展开发。

### 头文件引入

```cpp
#include "ReplayTracksEditorModule.h" // 用于设置锁定的观察Actor
```

### 基本用法

从 `ReplayTracksEditorModule.h` 中获取的模块接口，用于在回放播放时控制视角。

```cpp
// 获取回放轨道编辑器模块
IReplayTracksEditorModule& ReplayTracksModule = FModuleManager::GetModuleChecked<IReplayTracksEditorModule>("ReplayTracksEditor");

// 设置在回放期间，摄像机要锁定到的目标Actor
// 通常在回放开始前调用，用于实现摄像机跟踪特定角色
ReplayTracksModule.SetLockedActor(MyWorld, MyCharacterToFollow);
```

### 进阶用法

结合 `FReplayTrackEditor` 类，可以创建自定义的 Sequencer 轨道编辑器。

```cpp
// 在自定义的Sequencer编辑器初始化时，注册自定义的ReplayTrack编辑器
void UMyCustomSequencerModule::StartupModule()
{
    // 获取Sequencer实例
    TSharedRef<ISequencer> Sequencer = GetMySequencer();
    
    // 创建一个FReplayTrackEditor实例，它会自动处理ReplayTrack的UI和交互
    TSharedRef<FReplayTrackEditor> ReplayEditor = MakeShareable(new FReplayTrackEditor(Sequencer));
    
    // 将编辑器注册到Sequencer中
    // (通常在Sequencer创建时由系统自动完成，此处仅为演示逻辑)
}
```

## Demo 示例

以下是一个最小化的编辑器模块，演示如何注册和使用 `ReplayTracksEditorModule` 的接口。

**MyReplayIntegration.h**
```cpp
// MyReplayIntegration.h
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyReplayIntegrationModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    /** 一个示例函数，用于演示如何调用ReplayTracks模块 */
    void FocusReplayOnActor(UWorld* World, AActor* TargetActor);
};
```

**MyReplayIntegration.cpp**
```cpp
// MyReplayIntegration.cpp
#include "MyReplayIntegration.h"
#include "ReplayTracksEditorModule.h"

#define LOCTEXT_NAMESPACE "FMyReplayIntegrationModule"

void FMyReplayIntegrationModule::StartupModule()
{
    // 模块启动时的初始化逻辑
}

void FMyReplayIntegrationModule::ShutdownModule()
{
    // 模块关闭时的清理逻辑
}

void FMyReplayIntegrationModule::FocusReplayOnActor(UWorld* World, AActor* TargetActor)
{
    if (World && TargetActor)
    {
        // 检查ReplayTracksEditor模块是否加载
        if (FModuleManager::Get().IsModuleLoaded("ReplayTracksEditor"))
        {
            IReplayTracksEditorModule& ReplayModule = FModuleManager::GetModuleChecked<IReplayTracksEditorModule>("ReplayTracksEditor");
            
            // 通知ReplayTracks模块，在播放回放时将摄像机锁定到指定的Actor
            ReplayModule.SetLockedActor(World, TargetActor);
            
            UE_LOG(LogTemp, Log, TEXT("已设置回放摄像机锁定目标为: %s"), *TargetActor->GetName());
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("ReplayTracksEditor模块未加载，无法设置锁定Actor。请确保已启用插件。"));
        }
    }
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyReplayIntegrationModule, MyReplayIntegration)
```

## 模块依赖

从 `Build.cs` 文件中提取，以下是该插件**独特**的、不常见的依赖。常见依赖（Core, CoreUObject, Engine, Slate 等）已省略。

| 模块 | 用途 |
|---|---|
| `MovieScene` | 提供 Sequencer 序列场景和轨道的核心框架。 |
| `Sequencer` | Sequencer 编辑器核心逻辑。 |
| `LevelSequence` | 关卡序列资产相关功能。 |
| `Replay` | 底层的回放系统接口。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-06-05 | `28030cd1` | Sequencer: remove uses of IMovieScenePlayer | 移除了对旧接口 `IMovieScenePlayer` 的使用，进行接口现代化重构。 |
| 2024-02-21 | `33c4fac2` | [Backout] - CL31676435 and 31676432, which restores 31652683 and 31660265 | 回退了之前的一次重构，恢复了更早的两个改动（31652683 和 31660265）。 |
| 2024-02-21 | `22575fdd` | [Backout] - CL31652683 | 回退了一次链接器/运行器重构（CL31652683）。 |
| 2024-02-20 | `4aa3f9f3` | Sequencer: linker/runner refactor | Sequencer 进行了一次链接器/运行器（linker/runner）的重构。 |
| 2023-11-03 | `bb5b082f` | Sequencer: move evaluation information onto FSharedPlaybackState | 将评估信息迁移到 `FSharedPlaybackState` 上，属于 Sequencer 架构调整。 |

### 维护评价

该插件自2021年创建以来，一直处于**实验性**状态（`IsBetaVersion=true` 且 `EnabledByDefault=false`）。从提交历史看，近期（2024年）仍有多次更新，但主要集中在 Sequencer 核心框架的重构和适配上（如移除旧接口、修改评估架构），并非为该插件自身增加新功能。

**总结**：
- **年龄**：约4年，属于较新的插件。
- **状态**：**实验性，维护不活跃**。虽然近期有提交，但主要是被动适配 Sequencer 的底层变更，而非主动开发。
- **风险**：接口和功能可能不稳定，存在未来被移除或大改的风险。
- **推荐**：**不推荐用于生产环境**。可作为技术预研或内部工具开发的参考。如果计划在项目中使用回放序列功能，需要评估其稳定性和长期维护性，并准备好进行自行维护和扩展。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/ReplayTracks)
- [官方文档]()（无）
- [测试用例]()（未在已知路径发现专门的测试用例）