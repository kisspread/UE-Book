# Movie Render Queue

> Advanced movie rendering pipeline for use in creating rendered cinematics or other multi-media creation.

| 属性 | 值 |
|---|---|
| 中文名 | 电影渲染队列 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例项目，测试资源） |
| 模块 | `MovieRenderPipelineCore` (Runtime), `MovieRenderPipelineEditor` (Runtime), `MovieRenderPipelineMP4Encoder` (Runtime), `MovieRenderPipelineRenderPasses` (Runtime), `MovieRenderPipelineSettings` (Runtime), `UEOpenExrRTTI` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-30 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/MovieRenderPipeline) | |

## 用途

Movie Render Pipeline (MRQ) 是一个**高质量、可配置的离线渲染系统**，用于在虚幻引擎中创建电影级或广播级质量的视频输出。它解决了引擎实时渲染在画质、分辨率、抗锯齿和色彩深度上的限制，允许用户通过队列化、多配置的方式批量渲染过场动画序列、游戏内回放或任何 Sequencer 资产。与简单的“截图”或“录制视频”功能不同，MRQ 提供了一个完整且可扩展的渲染管线，支持复杂的渲染通道、自定义后处理、多GPU渲染以及对输出格式（如EXR、MP4）的精细控制。

## 使用场景

- **影视级过场动画渲染**：为电影、广告或游戏内的电影序列渲染最终高质量的画面。
- **营销预告片与内容创作**：录制游戏玩法或预渲染片段，用于制作预告片、社交媒体内容。
- **建筑与产品可视化**：从虚幻引擎的实时场景中渲染高分辨率、带有多通道（如反射、深度）的静态帧或动画。
- **自动化测试与验证**：通过脚本化和队列功能，自动渲染不同配置或版本的游戏画面，用于视觉回归测试。
- **离线渲染复杂特效**：利用“无限”渲染时间，渲染实时模式下无法达到品质的复杂粒子、光影或后处理效果。

## 蓝图用法

MRQ 主要通过其编辑器集成（MovieRenderPipelineEditor）和核心运行时类提供蓝图接口。大部分高级功能通过编辑器中的“电影渲染队列”窗口配置，但关键节点和类也可以在蓝图中使用，主要用于启动和控制渲染过程。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateMoviePipelineExecutor` | 创建一个用于执行渲染队列的执行器实例。 | `UMoviePipelineExecutorBase` |
| `RenderJob (MoviePipeline)` | 为指定的配置资产启动一个渲染任务。 | `UMoviePipeline` |
| `GetPipelineConfig` | 获取当前渲染管线的配置对象，用于读取或修改设置。 | `UMoviePipeline` |
| `AddJob` | 向队列执行器中添加一个渲染作业。 | `UMoviePipelineQueue` |

> **注**：MRQ 的配置高度数据驱动，绝大多数设置（如分辨率、输出格式、渲染通道）通过 `UMoviePipelinePrimaryConfig` 和其子对象在编辑器UI中或通过蓝图编辑资产（`UAsset`）来完成。C++ 和蓝图主要用于启动、停止渲染和动态配置。

## C++ 用法

### 头文件引入

```cpp
#include "MoviePipeline.h"
#include "MoviePipelinePrimaryConfig.h"
#include "MoviePipelineOutputSetting.h"
#include "MoviePipelineQueue.h"
#include "MoviePipelineExecutor.h"
```

### 基本用法

```cpp
// 创建一个基本的 MoviePipeline 实例并启动一个简单的渲染作业
UMoviePipeline* Pipeline = NewObject<UMoviePipeline>();
UMoviePipelinePrimaryConfig* Config = NewObject<UMoviePipelinePrimaryConfig>();

// 设置输出分辨率
UMoviePipelineOutputSetting* OutputSetting = Config->FindOrAddSettingByClass<UMoviePipelineOutputSetting>();
OutputSetting->OutputResolution = FIntPoint(1920, 1080);
OutputSetting->FileNameFormat = TEXT("{sequence_name}.{frame_number}");

// 设置要渲染的 Level Sequence 资产
ULevelSequence* SequenceToRender = LoadObject<ULevelSequence>(nullptr, TEXT("/Game/Cinematics/MySequence"));

// 设置世界上下文和配置
Pipeline->Initialize(SequenceToRender, Config, GetWorld());

// 开始渲染（通常需要在游戏线程调用）
Pipeline->StartRender();

// （可选）监听渲染完成的委托
Pipeline->OnMoviePipelineFinished().AddLambda([](UMoviePipeline* FinishedPipeline, bool bSuccess) {
    UE_LOG(LogTemp, Log, TEXT("渲染完成: %s"), bSuccess ? TEXT("成功") : TEXT("失败"));
});
```
*（功能综合自 `MovieRenderPipelineCore` 模块的公开接口）*

### 进阶用法

更复杂的用法通常涉及操作 `UMoviePipelineQueue` 和自定义 `UMoviePipelineExecutor`，以实现作业队列管理和分发到多台机器或GPU。

```cpp
// 获取全局队列并添加作业
UMoviePipelineQueue* Queue = GetDefault<UMoviePipelineQueueSubsystem>()->GetQueue();
UMoviePipelineExecutorJob* Job = Queue->AllocateNewJob();

// 为作业配置序列和预设
Job->SetSequence(SequenceToRender);
Job->SetConfiguration(Config); // 或通过 Job->SetPreset(PresetAsset) 加载预设

// 创建一个控制台变量执行器来本地渲染
UMoviePipelineExecutorBase* Executor = NewObject<UMoviePipelineConsoleVariableExecutor>();
Executor->OnExecutorFinished().AddLambda([](UMoviePipelineExecutorBase* InExecutor, bool bSuccess, FText Status) {
    // 处理完成事件
});

// 开始执行队列
Executor->Execute(Queue);
```
*（进阶模式参考了编辑器模块和 `MoviePipelineSettings` 模块中队列与执行器的交互逻辑）*

## Demo 示例

详细的 Demo 示例和蓝图用法，请参见以下子模块文档：
- **MovieRenderPipelineCore.md**：核心运行时逻辑、管线初始化和渲染流程。
- **MovieRenderPipelineEditor.md**：编辑器集成、队列窗口操作和蓝图资产使用。
- **MovieRenderPipelineRenderPasses.md**：内置和自定义渲染通道的使用方法。

## 模块依赖

使用本插件（特别是扩展或自定义渲染通道时）可能需要依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `ConsoleVariablesEditor` | MovieRenderPipelineSettings 模块依赖，用于在运行时通过UI编辑控制台变量。 |
| `UEOpenExrRTTI` | 提供对 OpenEXR 图像格式的运行时类型信息（RTTI）支持，用于读写 EXR 文件。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为电影图与nDisplay添加了EXR多层支持。 |
| 2026-05-26 | `353f4079` | MoviePipeline: Fixed an issue with layer warm-ups in the graph that could cause some skeletal meshes | 修复了图中图层预热可能导致骨骼网格体异常的问题。 |
| 2026-05-26 | `5b4aedd1` | MoviePipeline: Reverting a change made to letterboxing, which was meant to correct it when it's comb | 回滚了一个旨在修正合成模式下黑边显示的改动。 |
| 2026-05-21 | `a1446fbd` | MoviePipeline: Added an "Anti Aliasing Method" property to the Basic configuration type for the Defe | 为Deferrred渲染的基础配置类型添加了“抗锯齿方法”属性。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 当使用Rundown页面设置时，为动态设计添加了MRQ分析事件。 |

### 维护评价

**活跃维护**。虽然该插件创建于约7年前，但**近期（2026年5月）仍有密集的功能性更新和bug修复**，这表明它仍然是 Epic Games 积极维护的核心功能之一。更新内容聚焦于功能增强（EXR多层支持、新抗锯齿选项）和稳定性修复。鉴于其作为专业渲染管线的关键角色以及持续的活跃开发，**强烈推荐**有高质量离线渲染需求的项目使用。需要注意的是，它默认未启用，需要在插件设置中手动开启。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/MovieRenderPipeline)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/FunctionalTests/MoviePipelineTest)