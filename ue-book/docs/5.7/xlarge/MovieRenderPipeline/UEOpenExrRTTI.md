# Movie Render Pipeline (UEOpenExrRTTI 模块)

> Advanced movie rendering pipeline for use in creating rendered cinematics or other multi-media creation.

| 属性 | 值 |
|---|---|
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置文件） |
| 模块 | `MovieRenderPipelineCore` (Runtime), `MovieRenderPipelineEditor` (Runtime), `MovieRenderPipelineMP4Encoder` (Runtime), `MovieRenderPipelineRenderPasses` (Runtime), `MovieRenderPipelineSettings` (Runtime), `UEOpenExrRTTI` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-30 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/MovieRenderPipeline) | |

## 用途

本插件（`MovieRenderPipeline`）提供了一个高级的、可扩展的离线渲染管线，专门用于生成高质量的视频序列，例如游戏内的过场动画、宣传片或电影级渲染。它解决了传统 `Sequencer` 渲染器在功能、灵活性和输出质量上的限制，支持多通道渲染、高分辨率时间采样、自定义渲染通道、复杂的输出格式（如 EXR）以及队列化批量处理。

**当前模块 `UEOpenExrRTTI`** 是该管线的一个底层支持模块，其唯一职责是为 OpenEXR 文件格式提供运行时类型信息（RTTI）支持。它定义了一个接口 `IOpenExrRTTIModule`，允许其他模块（主要是 `MovieRenderPipelineRenderPasses` 中的 EXR 输出器）将自定义的元数据（Metadata）键值对写入到 OpenEXR 文件头中。这使得渲染输出的 EXR 文件能够携带场景、镜头、渲染设置等丰富的上下文信息，便于后期合成软件（如 Nuke、DaVinci Resolve）进行自动化处理。

## 使用场景

- **制作游戏宣传片或过场动画**：需要电影级的抗锯齿、运动模糊和高动态范围（HDR）输出。
- **渲染多通道（AOVs）**：将漫反射、高光、法线、深度等通道分别输出为独立的图像序列，用于后期精细合成。
- **需要精确时间采样**：对于包含快速运动或粒子效果的场景，使用高时间采样率（Temporal Samples）来获得平滑的运动模糊。
- **批量渲染任务**：使用“渲染队列”功能，将多个序列或关卡的渲染任务排队，无人值守地完成大量渲染工作。
- **自定义渲染流程**：通过编写自定义的 `UMoviePipelineSetting` 或 `UMoviePipelineRenderPass`，集成特殊的渲染步骤或输出格式。
- **需要向 EXR 文件写入自定义元数据**：当默认的 EXR 输出无法满足后期流程的元数据需求时，通过 `UEOpenExrRTTI` 模块进行扩展。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Pipeline` | 启动一个已配置的电影管线实例进行渲染。 | `UMoviePipeline` |
| `Set Initialization Time` | 设置管线初始化时使用的 `UWorld` 和时间点。 | `UMoviePipeline` |
| `Get Configuration` | 获取管线当前的配置资产 (`UMoviePipelinePrimaryConfig`)。 | `UMoviePipeline` |
| `Set Configuration` | 为管线设置一个配置资产。 | `UMoviePipeline` |
| `Add Job` | 向渲染队列 (`UMoviePipelineQueue`) 添加一个新的渲染作业。 | `UMoviePipelineQueue` |
| `Set Map` | 为渲染作业指定要渲染的地图/关卡。 | `UMoviePipelineExecutorJob` |
| `Set Sequence` | 为渲染作业指定要渲染的 `ULevelSequence` 资产。 | `UMoviePipelineExecutorJob` |
| `Get Settings` | 获取作业配置中所有设置的数组。 | `UMoviePipelinePrimaryConfig` |
| `Find Setting by Class` | 根据类类型查找特定的设置对象。 | `UMoviePipelinePrimaryConfig` |

### 使用示例（蓝图描述）

1.  **启动简单渲染**：
    *   创建一个 `UMoviePipeline` 对象。
    *   使用 `Set Sequence` 节点为其指定一个 `ULevelSequence`。
    *   使用 `Set Initialization Time` 节点，传入当前 `World` 和 `Sequence` 的起始时间。
    *   调用 `Start Pipeline` 节点开始渲染。

2.  **配置并使用渲染队列**：
    *   获取游戏实例中的 `UMoviePipelineQueue` 子系统。
    *   使用 `Add Job` 节点创建一个新作业。
    *   为作业设置 `Map` 和 `Sequence`。
    *   通过 `Get Configuration` 获取作业的配置，并使用 `Find Setting by Class` 节点查找并修改 `UMoviePipelineOutputSetting` 来设置输出路径和格式。
    *   最终，通过队列子系统启动执行器来处理所有排队作业。

## C++ 用法

### 头文件引入

```cpp
// 核心管线功能
#include "MoviePipeline.h"
#include "MoviePipelineQueue.h"
#include "MoviePipelinePrimaryConfig.h"
#include "MoviePipelineOutputSetting.h"

// EXR 元数据支持 (UEOpenExrRTTI 模块)
#include "IOpenExrRTTIModule.h"
```

### 基本用法

以下代码演示了如何以编程方式创建并启动一个简单的电影管线渲染任务。
（来源：引擎测试用例及 `MoviePipeline.cpp` 中的典型用法）

```cpp
// 假设在某个 Actor 或 Subsystem 中
void AMyActor::StartMovieRender()
{
    // 1. 创建管线实例
    UMoviePipeline* Pipeline = NewObject<UMoviePipeline>();

    // 2. 设置初始化上下文 (需要有效的 World 和时间)
    FMoviePipelineInitParams InitParams;
    InitParams.World = GetWorld();
    // 通常从 LevelSequence 的播放时间获取
    InitParams.TimeRange = TRange<FMovieSceneSequenceTime>(FMovieSceneSequenceTime(0), FMovieSceneSequenceTime(1000));
    Pipeline->SetInitializationTime(InitParams);

    // 3. 加载或创建配置
    UMoviePipelinePrimaryConfig* Config = LoadObject<UMoviePipelinePrimaryConfig>(nullptr, TEXT("/Game/MoviePipeline/MyConfig.MyConfig"));
    if (!Config)
    {
        Config = NewObject<UMoviePipelinePrimaryConfig>();
        // 配置输出设置
        UMoviePipelineOutputSetting* OutputSetting = Config->FindOrAddSettingByClass<UMoviePipelineOutputSetting>();
        OutputSetting->OutputDirectory.Path = FPaths::ProjectSavedDir() / TEXT("MovieRenders");
        OutputSetting->FileNameFormat = TEXT("{sequence_name}.{frame_number}");
    }
    Pipeline->SetConfiguration(Config);

    // 4. 指定要渲染的序列
    ULevelSequence* Sequence = LoadObject<ULevelSequence>(nullptr, TEXT("/Game/Cinematics/MySequence.MySequence"));
    // 管线内部通过 Job 管理序列，这里简化操作
    Pipeline->GetJob()->SetSequence(Sequence);

    // 5. 启动渲染
    Pipeline->StartPipeline();
}
```

### 进阶用法

**实现自定义的 `IOpenExrRTTIModule` 以添加 EXR 元数据**：
（来源：`MovieRenderPipelineRenderPasses` 模块中 `UMoviePipelineImageSequenceOutput_EXR` 的实现逻辑）

```cpp
// 在你的模块实现文件中 (例如 MyExrModule.cpp)
#include "IOpenExrRTTIModule.h"
#include "Modules/ModuleManager.h"

class FMyExrRTTIModule : public IOpenExrRTTIModule
{
public:
    virtual void AddFileMetadata(const TMap<FString, FStringFormatArg>& InMetadata, Imf::Header& InHeader) override
    {
        // 遍历传入的元数据键值对
        for (const auto& Pair : InMetadata)
        {
            // 将 Unreal 字符串转换为 OpenEXR 能识别的类型并插入到 Header 中
            // 例如，添加一个自定义的 “camera” 元数据
            if (Pair.Key == TEXT("camera"))
            {
                InHeader.insert("camera", Imf::StringAttribute(Pair.Value.ToString()));
            }
            // ... 处理其他自定义键
        }
    }
};

// 注册模块
IMPLEMENT_MODULE(FMyExrRTTIModule, MyExrRTTI);
```

## Demo 示例

一个最小的示例，展示如何实现 `IOpenExrRTTIModule` 接口并注册模块，以便 `MovieRenderPipeline` 在输出 EXR 时调用你的逻辑。

**MyExrRTTIModule.h**
```cpp
// MyExrRTTIModule.h
#pragma once
#include "IOpenExrRTTIModule.h"

class FMyExrRTTIModule : public IOpenExrRTTIModule
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
    virtual void AddFileMetadata(const TMap<FString, FStringFormatArg>& InMetadata, Imf::Header& InHeader) override;
};
```

**MyExrRTTIModule.cpp**
```cpp
// MyExrRTTIModule.cpp
#include "MyExrRTTIModule.h"
#include "Modules/ModuleManager.h"

void FMyExrRTTIModule::StartupModule()
{
    // 模块启动时的初始化代码（如果需要）
}

void FMyExrRTTIModule::ShutdownModule()
{
    // 模块关闭时的清理代码
}

void FMyExrRTTIModule::AddFileMetadata(const TMap<FString, FStringFormatArg>& InMetadata, Imf::Header& InHeader)
{
    // 示例：将所有传入的元数据以 “unreal_” 为前缀写入 EXR 头
    for (const auto& Pair : InMetadata)
    {
        FString Key = FString::Printf(TEXT("unreal_%s"), *Pair.Key);
        InHeader.insert(TCHAR_TO_ANSI(*Key), Imf::StringAttribute(Pair.Value.ToString()));
    }
}

// 注册模块。模块名 “MyExrRTTI” 需要与 .uplugin 或 .uproject 中的模块名一致。
IMPLEMENT_MODULE(FMyExrRTTIModule, MyExrRTTI);
```

## 模块依赖

`UEOpenExrRTTI` 模块本身依赖简单，但作为 `MovieRenderPipeline` 的一部分，使用整个管线时需要关注以下依赖：

| 模块 | 用途 |
|---|---|
| `OpenEXR` | 第三方库，提供读写 OpenEXR 图像格式的核心功能。`UEOpenExrRTTI` 直接依赖其头文件。 |
| `MovieScene` | 提供 `ULevelSequence`、`FMovieSceneSequenceTime` 等 Sequencer 核心类型。 |
| `LevelSequence` | 提供关卡序列资产和播放功能。 |
| `MediaUtils` | 用于处理媒体纹理和捕获，可能用于预览或某些输出格式。 |
| `ImageWriteQueue` | 异步图像写入队列，用于高效地将渲染帧写入磁盘。 |
| `ConsoleVariablesEditor` | `MovieRenderPipelineSettings` 模块的依赖，用于在渲染时管理控制台变量。 |

## 维护状态

### 近期更新

```
- 2025-10-03 52e3dac151e1 Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 3/n
- 2025-09-15 14f1b91176fc [AutoRTFM] Disable AutoRTFM instrumentation on some targets that enable exceptions
- 2025-08-20 94591bb9fcc9 ANSICHAR, WIDECHAR, UCS2CHAR and UTF8CHAR support for FStringFormatter
```

### 维护评价

`MovieRenderPipeline` 是一个成熟且核心的插件，自 2019 年创建以来一直是 UE 高质量离线渲染的基石。从近期的 git 历史看，更新主要集中在**底层代码维护和兼容性修复**（如 DLL 导出规范、AutoRTFM 适配、字符类型支持），而非重大新功能开发。这表明该插件已进入**稳定维护期**。

- **优点**：功能强大且稳定，是官方推荐的电影渲染解决方案，拥有完善的文档和社区支持。
- **注意**：由于其复杂性，学习曲线较陡峭。`EnabledByDefault=false` 意味着新项目需要手动启用。
- **推荐**：**强烈推荐**用于任何需要高质量离线渲染的项目。尽管近期无重大功能更新，但其稳定性和必要性无可替代。对于 `UEOpenExrRTTI` 这类底层模块，除非需要深度定制 EXR 元数据，否则一般用户无需直接接触。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/MovieRenderPipeline)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/rendering-high-quality-frames-with-movie-render-queue-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/MovieRenderPipeline/Tests)