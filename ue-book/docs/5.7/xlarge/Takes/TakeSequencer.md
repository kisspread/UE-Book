# Take Recorder

> A suite of tools and interfaces designed for recording, reviewing and playing back takes in a virtual production environment.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `CacheTrackRecorder` (Runtime), `TakeMovieScene` (Runtime), `TakeRecorder` (Runtime), `TakeRecorderNamingTokens` (Runtime), `TakeRecorderSources` (Runtime), `TakesCore` (Runtime), `TakeSequencer` (Runtime), `TakeTrackRecorders` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Takes) | |

## 用途

Takes 插件是 Unreal Engine 虚拟制作工作流的核心组件，它提供了一套完整的工具链，用于在虚拟环境中录制、管理和回放“Take”（拍摄条）。其核心功能是将实时运行的 Actor、动画、摄像机运动、音频等数据，以时间轴的形式录制下来，并保存为可编辑、可回放的资产。`TakeSequencer` 模块作为该插件的关键部分，负责将录制的 Take 数据与 Sequencer（序列器）深度集成，使得录制的 Take 能够像普通的 Sequencer 轨道一样被编辑、混合和播放。

## 使用场景

- **虚拟制片 (Virtual Production)**：在 LED 墙或绿幕前进行实时拍摄时，导演需要即时回放刚刚录制的镜头，以检查表演、灯光和合成效果。Takes 插件允许快速录制并回放整个场景状态。
- **动作捕捉 (Motion Capture)**：录制演员的动作捕捉数据，并将其直接映射到虚拟角色上，然后通过 Sequencer 进行精细调整和后期处理。
- **多机位录制与回放**：同时录制多个虚拟摄像机的视角，并在 Sequencer 中像切换真实摄像机机位一样进行剪辑。
- **迭代式拍摄**：在同一个场景设置下，快速录制多个版本的表演（Take），并在 Sequencer 中进行对比和选择最佳版本。

## 蓝图用法

`TakeSequencer` 模块主要提供 C++ 层面的集成，其公共接口（如 `FTakeSequencerModule`）主要用于模块生命周期管理和内部系统注册，并未直接暴露大量面向蓝图的 `BlueprintCallable` 函数。蓝图用户通常通过 `TakeRecorder` 模块提供的 UI 和功能来操作录制和回放，而 `TakeSequencer` 在底层确保录制的数据能正确地在 Sequencer 中呈现。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无直接蓝图节点） | 该模块主要作为 Sequencer 与 Take 录制系统之间的桥梁，其功能通过 Sequencer 的 Take 轨道和 Take Recorder 的 UI 间接体现。 | `FTakeSequencerModule` |

### 使用示例（蓝图描述）

在蓝图中，你通常不会直接调用 `TakeSequencer` 模块。相反，你会：
1.  使用 `Take Recorder` 面板（一个编辑器 UI）来配置和启动录制。
2.  录制完成后，生成的 Take 资产会自动出现在 Content Browser 中。
3.  将该 Take 资产拖拽到 Sequencer 编辑器中，它会自动创建对应的轨道，这些轨道的创建和编辑能力由 `TakeSequencer` 模块在幕后支持。

## C++ 用法

`TakeSequencer` 模块的核心是向 Sequencer 注册自定义的轨道编辑器（Track Editor），以便 Sequencer 能够识别和编辑由 Take Recorder 生成的特殊轨道类型。

### 头文件引入

```cpp
#include "TakeSequencerModule.h"
```

### 基本用法

获取模块实例并检查其可用性，通常在需要与 Take 录制系统交互的模块启动时进行。

```cpp
// 来源：Engine/Plugins/VirtualProduction/Takes/Source/TakeSequencer/Public/TakeSequencerModule.h
if (FTakeSequencerModule::IsAvailable())
{
    FTakeSequencerModule& TakeSequencerModule = FTakeSequencerModule::Get();
    // 模块已加载，可以安全使用其提供的功能（如果有的话）
}
```

### 进阶用法

该模块的主要工作在 `StartupModule` 和 `ShutdownModule` 中完成。它通过 Sequencer 的扩展点注册自定义的 Track Editor。以下是其内部工作原理的简化示意（非直接可调用代码）：

```cpp
// 概念性代码，展示模块如何集成
void FTakeSequencerModule::StartupModule()
{
    // 获取 Sequencer 的扩展管理器
    ISequencerModule& SequencerModule = FModuleManager::Get().LoadModuleChecked<ISequencerModule>("Sequencer");
    
    // 注册一个用于编辑 Take 相关轨道的编辑器
    TakeTrackEditorHandle = SequencerModule.RegisterTrackEditor(FOnCreateTrackEditor::CreateStatic(&FMyTakeTrackEditor::CreateTrackEditor));
}

void FTakeSequencerModule::ShutdownModule()
{
    if (ISequencerModule* SequencerModule = FModuleManager::Get().GetModulePtr<ISequencerModule>("Sequencer"))
    {
        // 注销之前注册的轨道编辑器
        SequencerModule->UnRegisterTrackEditor(TakeTrackEditorHandle);
    }
}
```

## Demo 示例

一个最小的示例，展示如何在你的游戏模块中检查并引用 `TakeSequencer` 模块。

```cpp
// MyGameModule.h
#pragma once
#include "Modules/ModuleManager.h"

class FMyGameModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// MyGameModule.cpp
#include "MyGameModule.h"
#include "TakeSequencerModule.h"

void FMyGameModule::StartupModule()
{
    // 检查 TakeSequencer 模块是否可用
    if (FTakeSequencerModule::IsAvailable())
    {
        UE_LOG(LogTemp, Log, TEXT("TakeSequencer module is loaded and available."));
        // 在这里可以安全地使用 TakeSequencer 模块提供的功能
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("TakeSequencer module is not available."));
    }
}

void FMyGameModule::ShutdownModule()
{
    // 清理工作
}

IMPLEMENT_PRIMARY_GAME_MODULE(FMyGameModule, MyGame, "MyGame");
```

## 模块依赖

`TakeSequencer` 模块的依赖关系未在提供的 Build.cs 中明确列出。根据其功能（集成 Sequencer 和 Take 系统）推断，它很可能依赖以下模块：

| 模块 | 用途 |
|---|---|
| `TakesCore` | Takes 插件的核心数据类型和接口 |
| `TakeMovieScene` | 处理 Take 数据与 MovieScene（Sequencer 的底层数据结构）之间的转换 |
| `Sequencer` | Unreal Engine 的序列器核心模块 |

## 维护状态

### 近期更新

```
- ef0d3477c053 [Sequencer] Update Tracks Names and Reorganize Tracks Order #jira UE-221625 #rb Max.Chen
- fa1c08d366b8 [Backout] - CL39424548 [FYI] brad.monahan #rnx Original CL Desc ----------------------------------------------------------------- [Sequencer] Update Tracks Names and Reorganize Tracks Order #jira UE-221625 #rb Max.Chen
- c2e4648ff435 [Sequencer] Update Tracks Names and Reorganize Tracks Order #jira UE-221625 #rb Max.Chen
```

### 维护评价

- **创建时间**：2019年，是虚拟制作工具链的早期组件之一。
- **近期活动**：最近的提交（2025年）集中在 Sequencer 轨道的命名和组织优化上，表明 Epic 仍在积极维护和改进此模块，以提升用户体验。
- **维护状态**：**维护中**。作为虚拟制作的核心模块，它随着引擎版本持续更新。
- **推荐使用**：**强烈推荐**。对于任何涉及虚拟制片、实时录制和回放的项目，Takes 插件（包括 TakeSequencer）是标准且必要的工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Takes)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/take-recorder-in-unreal-engine/) （Takes 插件整体文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Takes/Tests) （如果存在）