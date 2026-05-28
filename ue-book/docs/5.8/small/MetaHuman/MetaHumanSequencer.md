# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置、模板） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 未知 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 MetaHuman 在 Unreal Engine 中的核心工具包，专注于将现实世界中的面部表演数据（如视频、音频）转化为可用于 MetaHuman 角色驱动的动画数据。其工作流程覆盖了从捕获、追踪、求解到在 Sequencer 中编辑与播放的全过程。它解决的核心问题是提供了一个完整、高度集成的管线，用于创建逼真的 MetaHuman 面部动画，无需依赖第三方昂贵的动捕设备或复杂的外部软件。

## 使用场景

- 你拍摄了一段演员的面部表演视频，想要快速驱动一个 MetaHuman 角色复现这段表演。
- 你有一个音频文件，希望生成与之口型同步的 MetaHuman 面部动画。
- 你需要在 Unreal 的 Sequencer 时间线上精确编辑由 MetaHuman Animator 生成的动画性能数据，调整节奏、排除无效帧或进行后期混合。
- 你正在开发一个大规模生产流程，需要批量处理多个 MetaHuman 角色的动画数据。

## 蓝图用法

`MetaHumanSequencer` 模块主要作为 Sequencer 的编辑器扩展，提供对 MetaHuman 专属媒体和音频轨道的自定义支持、渲染和编辑功能。其核心功能集成在 Sequencer 的编辑器界面中，而非通过蓝图节点暴露。

### 核心节点

该模块不提供 `UFUNCTION(BlueprintCallable)` 接口。其功能通过以下方式在编辑器中体现：

1.  **自定义 Sequencer 轨道**：在 Sequencer 中为 `MetaHumanPerformance` 资产创建带有专用编辑界面的媒体和音频轨道。
2.  **可视化通道**：在媒体轨道区段上直接绘制用于标记有效/无效动画帧的布尔通道（`FMetaHumanMovieSceneChannel`）。
3.  **增强的区段编辑**：支持媒体轨道区段的调整大小、缩略图显示，并能根据配置排除特定帧范围的渲染。

## C++ 用法

`MetaHumanSequencer` 模块的 C++ API 主要面向 Sequencer 扩展的开发者，提供了用于管理自定义数据通道、轨道编辑器和序列资产的类。

### 头文件引入

```cpp
#include "MetaHumanSequencerModule.h"
#include "MetaHumanMovieSceneChannel.h"
#include "MetaHumanSequence.h"
#include "MetaHumanMovieSceneMediaTrack.h"
#include "MetaHumanMovieSceneMediaSection.h"
```

### 基本用法：操作自定义数据通道

`FMetaHumanMovieSceneChannel` 是模块的核心数据结构，用于存储一系列与时间关联的布尔值（关键帧），常用于标记动画中的有效/无效区间。
*来源: Public/MetaHumanMovieSceneChannel.h*

```cpp
// 创建一个数据通道实例
FMetaHumanMovieSceneChannel MyChannel;

// 添加关键帧：在时间10处设置为 true，在时间20处设置为 false
MyChannel.GetData().AddKey(FFrameNumber(10), true);
MyChannel.GetData().AddKey(FFrameNumber(20), false);

// 查询特定时间的值
bool bValue;
if (MyChannel.Evaluate(FFrameTime(15), bValue))
{
    // bValue 应为 true (在10和20之间插值)
    UE_LOG(LogTemp, Log, TEXT("Value at frame 15: %s"), bValue ? TEXT("True") : TEXT("False"));
}

// 设置默认值（当没有关键帧时使用）
MyChannel.SetDefault(true);
TOptional<bool> DefaultValue = MyChannel.GetDefault(); // 获取 default true
```

### 进阶用法：自定义序列与轨道

该模块定义了 `UMetaHumanSceneSequence`，这是一个为 MetaHuman 系统定制的 `UMovieSceneSequence` 子类。
*来源: Public/MetaHumanSequence.h, Public/MetaHumanMovieSceneMediaTrack.h*

```cpp
// 通常，这些类由编辑器内部创建和使用。
// 开发者可以通过注册新类型来扩展 Sequencer，例如创建自定义轨道编辑器：
// (简化示意，实际注册发生在模块 StartupModule)
ISequencerModule& SequencerModule = FModuleManager::Get().LoadModuleChecked<ISequencerModule>(“Sequencer”);
SequencerModule.RegisterPropertyTrackEditor(
    FOnCreateTrackEditor::CreateStatic(&FMetaHumanMediaTrackEditor::CreateTrackEditor)
);
```

## Demo 示例

以下示例展示了如何在 C++ 中注册一个自定义的 Sequencer 轨道编辑器（类似于 `MetaHumanSequencer` 模块所做的）。

**MyCustomSequencerModule.h**
```cpp
#pragma once

#include “Modules/ModuleManager.h”

class FMyCustomSequencerModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MyCustomSequencerModule.cpp**
```cpp
#include “MyCustomSequencerModule.h”
#include “ISequencerModule.h”
#include “Sequencer/MyCustomTrackEditor.h” // 假设这是你的自定义轨道编辑器头文件

#define LOCTEXT_NAMESPACE “FMyCustomSequencerModule”

void FMyCustomSequencerModule::StartupModule()
{
    ISequencerModule& SequencerModule = FModuleManager::Get().LoadModuleChecked<ISequencerModule>(TEXT(“Sequencer”));

    // 注册你的自定义轨道编辑器
    SequencerModule.RegisterPropertyTrackEditor(
        FOnCreateTrackEditor::CreateStatic(&FMyCustomTrackEditor::CreateTrackEditor)
    );

    UE_LOG(LogTemp, Log, TEXT(“Custom Sequencer Track Editor Registered.”));
}

void FMyCustomSequencerModule::ShutdownModule()
{
    // 通常编辑器模块的反注册在 Sequencer 模块卸载时自动处理
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyCustomSequencerModule, MyCustomSequencer)
```

## 模块依赖

要使用 `MetaHumanSequencer` 模块的功能（通常是通过其他 MetaHuman 模块间接使用），你的模块需要链接它。具体的依赖关系需查看 `MetaHumanSequencer.Build.cs`。根据常见的 MetaHuman 依赖推断，可能需要链接：

| 模块 | 用途 |
|---|---|
| `MetaHumanPerformance` | 处理捕获的面部表演数据 |
| `MovieScene` | Unreal Sequencer 的核心数据结构 |
| `MediaAssets` | 处理媒体（视频）资产和轨道 |

*注意：上表为基于上下文的合理推测，实际依赖请以 `MetaHumanSequencer.Build.cs` 文件为准。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 身体上的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤掉可视化调试对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MetaHuman Animator] 为现有网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题。 |

### 维护评价

**活跃维护**。`MetaHumanSequencer` 作为 MetaHuman 工具链的关键组件，近期的更新非常频繁（2026年5月有多次提交），且改动内容涉及功能修复、优化和新特性，表明该模块在积极开发和维护中。由于它是 MetaHuman 官方插件的一部分，其稳定性和兼容性得到 Epic 的直接支持，推荐在 MetaHuman 工作流中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanSequencer)
- [官方文档](https://docs.unrealengine.com/en-US/InteractiveExperiences/Sequencer/)（关于通用 Sequencer 的文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Tests) （插件根目录下的测试文件夹，可能包含相关测试）