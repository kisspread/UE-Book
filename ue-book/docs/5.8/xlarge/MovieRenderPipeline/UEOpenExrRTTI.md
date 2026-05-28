# Movie Render Queue

> Advanced movie rendering pipeline for use in creating rendered cinematics or other multi-media creation.

| 属性 | 值 |
|---|---|
| 中文名 | 影片渲染队列 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置预设） |
| 模块 | `MovieRenderPipelineCore` (Runtime), `MovieRenderPipelineEditor` (Runtime), `MovieRenderPipelineMP4Encoder` (Runtime), `MovieRenderPipelineRenderPasses` (Runtime), `MovieRenderPipelineSettings` (Runtime), `UEOpenExrRTTI` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-30 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/MovieRenderPipeline) | |

## 用途

Movie Render Pipeline（MRQ）是 UE5 的专业级离线渲染管线，用于将 Sequencer 中的过场动画序列渲染为高品质视频或图像序列。它解决了传统实时截图/录像质量不足的问题，提供了一套**完全可脚本化、可扩展**的渲染架构。

核心解决的问题：
- **高品质抗锯齿**：支持空间/时间超采样（Temporal/Spatial Super Sampling），产出无锯齿的离线渲染画面
- **多通道输出**：支持将深度、法线、对象 ID、自定义 Pass 等分别输出为 EXR 多层文件
- **批量渲染**：提供队列系统（Render Queue），可一次性排队渲染多个序列/组合
- **编码支持**：内建 MP4 编码器（H.264），无需外部工具即可输出视频文件
- **EXR 元数据**：通过 UEOpenExrRTTI 模块将自定义元数据嵌入 OpenEXR 文件头
- **nDisplay 集成**：支持多机分布式渲染和 EXR 多层输出

与旧的 Movie Scene Capture 相比，MRQ 采用了全新的 Job → Pipeline → Renderer 架构，每个环节都可蓝图/C++ 自定义扩展。

## 使用场景

- 你在用 Sequencer 制作高品质过场动画 → 用 MRQ 离线渲染
- 你需要输出带深度/法线通道的 EXR 序列用于后期合成 → 用 MRQ 的多通道渲染
- 你需要批量渲染多个镜头的多种质量预设 → 用 MRQ Render Queue
- 你在做虚拟制片/LED 墙拍摄 → 用 MRQ + nDisplay 支持
- 你需要把渲染结果直接输出为 MP4 视频 → 用 MRQ + MP4 编码模块
- 你希望在 CI/CD 流水线中自动化渲染 → 用 MRQ 的命令行和脚本接口

> ⚠️ **注意**：此插件默认未启用（`EnabledByDefault: false`），需要在 Edit → Plugins 中手动启用。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindOrAddJobForShot` | 为指定 Shot 在队列中查找或创建渲染 Job | `UMoviePipelineQueue` |
| `SetConfiguration` | 为 Job 指定渲染配置（.uasset） | `UMoviePipelineExecutorJob` |
| `SetSequence` | 设置 Job 要渲染的 Level Sequence 资产 | `UMoviePipelineExecutorJob` |
| `SetMap` | 设置 Job 使用的地图 | `UMoviePipelineExecutorJob` |
| `StartRendering` | 启动当前队列的渲染执行 | `UMoviePipelineQueueSubsystem` |
| `SetInitializationTime` | 设置初始化阶段时长（用于材质/LOD 预热） | `UMoviePipeline` |
| `SetViewportBackgroundColor` | 设置渲染时的视口背景颜色 | `UMoviePipeline` |
| `SetViewportTexture` | 设置渲染时的视口背景纹理 | `UMoviePipeline` |
| `GetEstimatedTimeRemaining` | 获取预估剩余渲染时间 | `UMoviePipeline` |
| `GetCurrentJob` | 获取当前正在渲染的 Job | `UMoviePipeline` |

### 使用示例（蓝图描述）

**基础用法：通过蓝图启动渲染**

1. 使用 `Get Game Instance` → `Get Subsystem (MoviePipelineQueueSubsystem)` 获取队列子系统
2. 调用 `Load Queue` 加载一个 `.uasset` 渲染队列（或用 `Create Queue` 新建）
3. 在队列上 `Add Job`，获得 `UMoviePipelineExecutorJob`
4. 对 Job 调用 `Set Sequence` 指定 Level Sequence 资产
5. 对 Job 调用 `Set Map` 指定要渲染的地图
6. 对 Job 调用 `Set Configuration` 指定渲染配置（分辨率、输出格式、通道等）
7. 最后调用队列子系统的 `Render Queue` 开始渲染

**命令行渲染（无需编辑器 UI）**

```
UnrealEditor-Cmd.exe MyProject.uproject /Game/Maps/MyMap -game -MoviePipelineConfig=/Game/Cinematics/MyRenderConfig -MoviePipelineLocalExecutorClass=/Script/MovieRenderPipelineCore.MoviePipelineLocalExecutor -NoLoadingScreen -NoSound -NoTextureStreaming -windowed -ResX=1920 -ResY=1080
```

## C++ 用法

### 头文件引入

```cpp
#include "MoviePipeline.h"
#include "MoviePipelineQueue.h"
#include "MoviePipelineExecutor.h"
#include "MoviePipelineOutputBase.h"
#include "MoviePipelineRenderPass.h"
#include "MovieRenderPipelineCoreModule.h"
```

### 基本用法：创建并配置渲染 Job

```cpp
#include "MoviePipelineQueue.h"
#include "MoviePipeline.h"
#include "MoviePipelinePrimaryConfig.h"
#include "MoviePipelineOutputSetting.h"
#include "LevelSequence.h"

// 创建渲染队列
UMoviePipelineQueue* Queue = NewObject<UMoviePipelineQueue>();

// 添加一个 Job
UMoviePipelineExecutorJob* Job = Queue->AllocateNewJob(UMoviePipelineExecutorJob::StaticClass());
Job->SetSequence(SequenceAsset);   // ULevelSequence*
Job->SetMap(MapAsset);             // UWorld*
Job->JobName = TEXT("MyRenderJob");

// 配置输出
UMoviePipelinePrimaryConfig* Config = NewObject<UMoviePipelinePrimaryConfig>();
UMoviePipelineOutputSetting* OutputSetting = Config->FindOrAddSettingByClass(UMoviePipelineOutputSetting::StaticClass());
OutputSetting->OutputDirectory.Path = FPaths::ProjectSavedDir() / TEXT("MovieRenders");
OutputSetting->FileNameFormat = TEXT("{sequence_name}/{sequence_name}_{frame_number}");
OutputSetting->OutputResolution = FIntPoint(1920, 1080);

Job->SetConfiguration(Config);
```

> 来源：基于 MovieRenderPipelineCore 模块公共 API 提取

### 进阶用法：自定义渲染通道

```cpp
#include "MoviePipelineRenderPass.h"
#include "MoviePipelineDeferredPasses.h"

// 添加自定义渲染通道到配置
UMoviePipelinePrimaryConfig* Config = Job->GetConfiguration();

// 添加延迟渲染基础通道
UMoviePipelineDeferredPassBase* DeferredPass = Cast<UMoviePipelineDeferredPassBase>(
    Config->FindOrAddSettingByClass(UMoviePipelineDeferredPassBase::StaticClass()));

// 添加图像输出通道
UMoviePipelineOutputSetting* OutputSetting = Config->FindOrAddSettingByClass(
    UMoviePipelineOutputSetting::StaticClass());
OutputSetting->bUseCustomFrameRate = true;
OutputSetting->OutputFrameRate = FFrameRate(24, 1); // 24fps cinematic
```

### EXR 元数据写入（UEOpenExrRTTI 模块）

```cpp
#include "IOpenExrRTTIModule.h"
#include "Modules/ModuleManager.h"

// 获取 OpenEXR RTTI 模块实例
IOpenExrRTTIModule* OpenExrModule = FModuleManager::GetModulePtr<IOpenExrRTTIModule>(TEXT("UEOpenExrRTTI"));
if (OpenExrModule)
{
    // 构造元数据键值对
    TMap<FString, FStringFormatArg> Metadata;
    Metadata.Add(TEXT("shot"), FStringFormatArg(TEXT("shot_010")));
    Metadata.Add(TEXT("artist"), FStringFormatArg(TEXT("John Doe")));
    Metadata.Add(TEXT("frame_range"), FStringFormatArg(TEXT("1-120")));

    // 写入 OpenEXR 文件头
    Imf::Header ExrHeader;
    OpenExrModule->AddFileMetadata(Metadata, ExrHeader);
}
```

> 来源：Source/openexrRTTI/UEOpenExrRTTI.Build.cs + Public/IOpenExrRTTIModule.h

## 模块架构

```
MovieRenderPipeline/
├── MovieRenderPipelineCore          ← 核心管线框架（Job、Pipeline、Executor）
├── MovieRenderPipelineEditor        ← 编辑器 UI（Render Queue 窗口、设置面板）
├── MovieRenderPipelineRenderPasses  ← 内建渲染通道（Deferred、Path Tracing 等）
├── MovieRenderPipelineMP4Encoder    ← H.264/MP4 视频编码器
├── MovieRenderPipelineSettings      ← 默认配置和设置资产
└── UEOpenExrRTTI                    ← OpenEXR 文件头元数据读写
```

| 模块 | 职责 |
|---|---|
| `MovieRenderPipelineCore` | Job 管理、Pipeline 执行流程、Executor 框架、输出基类 |
| `MovieRenderPipelineEditor` | Render Queue 窗口、Job 配置 UI、序列选择器 |
| `MovieRenderPipelineRenderPasses` | 延迟渲染 Pass、路径追踪 Pass、对象 ID Pass 等 |
| `MovieRenderPipelineMP4Encoder` | 视频编码器，支持 H.264 输出 MP4 |
| `MovieRenderPipelineSettings` | 默认渲染配置预设、Console Variables 集成 |
| `UEOpenExrRTTI` | OpenEXR 文件头自定义属性写入（单头文件模块） |

## 模块依赖

从各模块 Build.cs 提取的独特依赖（排除 Core/CoreUObject/Engine/Slate 等常见模块）：

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer 核心，Level Sequence 时间轴基础 |
| `MovieSceneTracks` | Sequencer 轨道系统，用于读取动画/摄像机数据 |
| `LevelSequence` | Level Sequence 资产类型和播放逻辑 |
| `RenderCore` | 渲染核心，RHI 命令提交和渲染资源管理 |
| `Renderer` | 延迟渲染器管线，用于访问 GBuffer 和渲染通道 |
| `ImageWriteQueue` | 异步图像写入队列，用于多线程保存 EXR/PNG 序列 |
| `OpenEXR` (ThirdParty) | OpenEXR 库，EXR 文件编解码 |
| `ConsoleVariablesEditor` | 控制台变量编辑器集成（MovieRenderPipelineSettings 依赖） |
| `Json` | 配置序列化 |
| `MediaAssets` | 媒体资产支持（MP4 编码器依赖） |
| `MediaUtils` | 媒体工具函数 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | nDisplay 支持 EXR 多层输出 |
| 2026-05-26 | `353f4079` | MoviePipeline: Fixed an issue with layer warm-ups in the graph that could cause some skeletal meshes | 修复图模式下层预热导致骨骼网格体异常的问题 |
| 2026-05-26 | `5b4aedd1` | MoviePipeline: Reverting a change made to letterboxing, which was meant to correct it when it's comb | 回退了信箱化功能的改动，恢复原始行为 |
| 2026-05-21 | `a1446fbd` | MoviePipeline: Added an "Anti Aliasing Method" property to the Basic configuration type for the Defe | 在基础配置中添加了抗锯齿方法属性 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 为运动设计的 Rundown 页面添加了 MRQ 分析事件 |

### 维护评价

- **活跃度**：🟢 **高度活跃** — 2026 年 5 月仍有密集的功能更新和 Bug 修复
- **创建时间**：2019 年 10 月，已有约 6 年历史，从实验性项目成长为 UE5 标准渲染管线
- **维护质量**：由 Epic Games 官方团队维护，更新频率极高，既有新功能（EXR 多层、新抗锯齿方法）也有稳定性修复
- **已知限制**：默认未启用，需手动激活；路径追踪模式依赖 DXR/MetalRT 硬件支持；命令行渲染需要完整的 Editor-Cmd 可执行文件
- **推荐程度**：⭐⭐⭐⭐⭐ **强烈推荐** — 这是 UE5 中渲染高品质过场动画的官方标准方案，任何需要离线渲染输出的项目都应该使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/MovieRenderPipeline)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/movie-render-pipeline-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/MovieRenderPipeline/Tests)