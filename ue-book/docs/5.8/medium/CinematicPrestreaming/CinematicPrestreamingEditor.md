# Cinematic Prestreaming

> Adds a way to record certain types of streaming data requests in cinematic cutscenes. The requests can then be played back in advance on the Sequencer timeline to pre-stream data during normal gameplay/rendering.

| 属性 | 值 |
|---|---|
| 中文名 | 影视预流送 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CinematicPrestreaming` (Runtime), `CinematicPrestreamingEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-19 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/CinematicPrestreaming) | |

## 用途

这个插件解决了 **影视过场动画中的流式加载卡顿问题**。当在游戏中播放过场动画序列时，新的虚拟纹理页面和 Nanite 几何体需要被流式加载进来，导致画面突然出现（pop-in）或明显卡顿。

Cinematic Prestreaming 的核心思路是 **先录制、后回放**：

1. **录制阶段**：在预渲染过场动画时，捕获所有虚拟纹理页面请求（Virtual Texture page requests）和 Nanite 几何体请求（Nanite geometry requests）
2. **保存阶段**：将捕获的请求数据保存为 `UCinePrestreamingData` 资产
3. **预流送阶段**：在 Sequencer 时间线上回放这些请求，使内容在实际需要之前就已经流式加载完成

插件支持两条录制管线：
- **Movie Render Queue**（传统管线）：通过 `UCinePrestreamingRecorderSetting` 设置项
- **Movie Render Graph**（新管线）：通过 `UCinePrestreamingGraphNode` 图节点

## 使用场景

- 你有一个包含大量 Nanite 建筑和虚拟纹理地形的开放世界游戏，过场动画播放时出现纹理弹出 → 用此插件录制并预流送
- 你的过场动画使用 Movie Render Pipeline 导出，需要确保最终渲染无 pop-in → 配合 MRQ 录制流送数据
- 你已迁移到 Movie Render Graph 管线，需要在新管线中实现预流送 → 使用 Graph 节点集成
- 你需要调试虚拟纹理流送行为 → 使用 `UCinePrestreamingDebugRender` 可视化调试通道

> **注意**：此插件当前为 **Beta 状态**（`IsBetaVersion=true`），需要在项目设置中手动启用。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreatePackagesFromGeneratedData` | 从录制数据创建资产包 | `UCinePrestreamingEditorSubsystem` |

### 录制设置属性（Movie Render Queue）

以下属性暴露为 BlueprintReadWrite，可在蓝图中配置 `UCinePrestreamingRecorderSetting`：

| 属性 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `PackageDirectory` | FDirectoryPath | — | 生成资产的输出目录，支持 `{shot_name}` 等格式标记 |
| `bVirtualTextures` | bool | true | 录制虚拟纹理页面请求 |
| `bNanite` | bool | true | 录制 Nanite 几何体请求 |
| `bModifyTargetSequence` | bool | true | 自动将生成的预流送轨道添加到目标序列 |
| `bMergeFrames` | bool | false | 合并相邻帧数据以减小资产体积 |
| `FrameCountMergeThreshold` | int32 | 6 | 最大合并帧数 |
| `bDisableAdvanceRenderFeatures` | bool | true | 禁用光照/后处理等，加速录制但输出图像不可用 |
| `StartFrame` | int32 | 0 | 录制起始帧 |
| `EndFrame` | int32 | 0 | 录制结束帧（0=全部） |

### Movie Render Graph 节点属性

`UCinePrestreamingGraphNode` 提供与 Recorder Setting 相同的配置属性，额外差异：

| 属性 | 说明 |
|---|---|
| `bDisableAdvanceRenderFeatures` | Graph 节点默认为 `false`（与 Recorder Setting 相反） |
| `OnGenerateData` | 资产生成完成后的委托回调 |

### 生成数据结构

```cpp
FMoviePipelineCinePrestreamingGeneratedData
├── StreamingData    (UCinePrestreamingData*)  — 录制的流送请求数据
├── MovieScene       (UMovieScene*)            — 关联的 MovieScene
├── PackagePath      (FString)                 — 包路径
└── AssetName        (FString)                 — 资产名称
```

### 蓝图使用示例

**在 Movie Render Queue 中启用录制**：

1. 打开 Movie Render Queue 配置
2. 添加 `Cine Prestreaming Recorder` 设置项（即 `UCinePrestreamingRecorderSetting`）
3. 设置 `Package Directory` 指向你的资产目录（如 `/Game/Cinematics/Prestreaming`）
4. 勾选需要捕获的类型（`bVirtualTextures` / `bNanite`）
5. 运行渲染，生成的 `UCinePrestreamingData` 资产会自动保存
6. 若勾选了 `bModifyTargetSequence`，预流送轨道会自动添加到目标 Sequencer 序列

**在 Movie Render Graph 中使用**：

1. 在 Graph 编辑器中添加 `Cine Prestreaming` 输出节点（即 `UCinePrestreamingGraphNode`）
2. 将节点连接到渲染管线
3. 配置录制参数
4. 运行渲染作业

## C++ 用法

### 头文件引入

```cpp
// 录制设置（Movie Render Queue 集成）
#include "CinePrestreamingRecorderSetting.h"

// Graph 节点（Movie Render Graph 集成）
#include "CinePrestreamingGraphNode.h"

// 编辑器子系统
#include "CinePrestreamingEditorSubsystem.h"
```

### 基本用法：监听生成数据

通过 `OnGenerateData` 委托接收录制完成后的数据：

```cpp
// 来源: Public/CinePrestreamingRecorderSetting.h
// 来源: Public/CinePrestreamingGraphNode.h

// 假设你有一个 UCinePrestreamingRecorderSetting 的实例
UCinePrestreamingRecorderSetting* RecorderSetting = /* 获取或创建 */;

// 绑定生成数据委托
RecorderSetting->OnGenerateData.AddLambda(
    [](TArray<FMoviePipelineCinePrestreamingGeneratedData> GeneratedData)
    {
        for (const FMoviePipelineCinePrestreamingGeneratedData& Data : GeneratedData)
        {
            if (Data.StreamingData)
            {
                UE_LOG(LogTemp, Log, TEXT("Generated prestreaming asset: %s/%s"),
                    *Data.PackagePath, *Data.AssetName);
            }
            if (Data.MovieScene)
            {
                UE_LOG(LogTemp, Log, TEXT("Target MovieScene: %s"),
                    *Data.MovieScene->GetPathName());
            }
        }
    }
);
```

### 进阶用法：通过编辑器子系统手动创建资产

```cpp
// 来源: Public/CinePrestreamingEditorSubsystem.h

#include "CinePrestreamingEditorSubsystem.h"

void CreatePrestreamingAssets(TArray<FMoviePipelineCinePrestreamingGeneratedData>& InData)
{
    // 获取编辑器子系统
    UCinePrestreamingEditorSubsystem* EditorSubsystem = 
        GEditor->GetEditorSubsystem<UCinePrestreamingEditorSubsystem>();
    
    if (EditorSubsystem)
    {
        // 从生成数据创建包（资产文件）
        EditorSubsystem->CreatePackagesFromGeneratedData(InData);
    }
}
```

### 进阶用法：配置录制参数

```cpp
// 来源: Public/CinePrestreamingRecorderSetting.h

void ConfigurePrestreamingRecorder(UCinePrestreamingRecorderSetting* Setting)
{
    // 设置输出目录（支持 MRQ 格式标记）
    Setting->PackageDirectory.Path = TEXT("/Game/Cinematics/Prestreaming/{shot_name}");
    
    // 启用虚拟纹理和 Nanite 捕获
    Setting->bVirtualTextures = true;
    Setting->bNanite = true;
    
    // 启用帧合并以减小文件大小
    Setting->bMergeFrames = true;
    Setting->FrameCountMergeThreshold = 10;
    Setting->VirtualTextureRequestMergeThreshold = 3000;
    Setting->NaniteRequestMergeThreshold = 800;
    
    // 禁用高级渲染特性以加速录制（仅用于专用录制图）
    Setting->bDisableAdvanceRenderFeatures = true;
    
    // 设置录制帧范围
    Setting->StartFrame = 0;
    Setting->EndFrame = 0; // 录制所有帧
    
    // 自动将预流送轨道添加到目标序列
    Setting->bModifyTargetSequence = true;
}
```

### 调试用法：虚拟纹理可视化

```cpp
// 来源: Private/CinePrestreamingDebugRender.h

// UCinePrestreamingDebugRender 是一个延迟渲染通道，用于可视化虚拟纹理状态
// 在 Movie Render Queue 设置中添加此通道，可使用 VirtualTextureDebugMode
// 指定可视化模式（EVirtualTextureVisualizationMode）
```

## Demo 示例

以下示例展示如何在 C++ 中以编程方式设置 Movie Render Queue 录制预流送数据：

```cpp
// PrestreamingRecorderExample.h
#pragma once

#include "CoreMinimal.h"

class UMoviePipelineQueue;
class UMoviePipelineExecutorJob;

class FPrestreamingRecorderExample
{
public:
    /** 配置一个 MRQ 作业以录制预流送数据 */
    static void ConfigureJobForPrestreaming(UMoviePipelineExecutorJob* Job);
};
```

```cpp
// PrestreamingRecorderExample.cpp
#include "PrestreamingRecorderExample.h"
#include "CinePrestreamingRecorderSetting.h"
#include "MoviePipelineQueue.h"
#include "MoviePipelineExecutorJob.h"
#include "MoviePipelineOutputBase.h"

void FPrestreamingRecorderExample::ConfigureJobForPrestreaming(UMoviePipelineExecutorJob* Job)
{
    if (!Job)
    {
        return;
    }

    // 获取作业的配置
    UMoviePipelinePrimaryConfig* Config = Job->GetConfiguration();
    if (!Config)
    {
        return;
    }

    // 查找或创建预流送录制设置
    UCinePrestreamingRecorderSetting* PrestreamingSetting = nullptr;
    for (UMoviePipelineSetting* Setting : Config->GetAllSettings())
    {
        PrestreamingSetting = Cast<UCinePrestreamingRecorderSetting>(Setting);
        if (PrestreamingSetting)
        {
            break;
        }
    }

    if (!PrestreamingSetting)
    {
        PrestreamingSetting = NewObject<UCinePrestreamingRecorderSetting>(Config);
        Config->AddSetting(PrestreamingSetting);
    }

    // 配置参数
    PrestreamingSetting->PackageDirectory.Path = TEXT("/Game/Cinematics/Prestreaming");
    PrestreamingSetting->bVirtualTextures = true;
    PrestreamingSetting->bNanite = true;
    PrestreamingSetting->bDisableAdvanceRenderFeatures = true;
    PrestreamingSetting->bModifyTargetSequence = true;

    // 绑定完成回调
    PrestreamingSetting->OnGenerateData.AddLambda(
        [](TArray<FMoviePipelineCinePrestreamingGeneratedData> GeneratedData)
        {
            UE_LOG(LogTemp, Display,
                TEXT("Prestreaming recording complete: %d assets generated"),
                GeneratedData.Num());
        }
    );
}
```

## 模块依赖

插件显式依赖 `MovieRenderPipeline` 插件。

| 模块 | 用途 |
|---|---|
| `MovieRenderPipeline` / `MovieRenderPipelineCore` | Movie Render Queue 和 Movie Render Graph 管线集成 |
| `MovieScene` / `MovieSceneTools` | Sequencer 轨道编辑器、序列段（Section）支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-19 | `5057560f` | CinematicPrestreaming: Move plugin out of Experimental and promote to beta. Move plugin from Engine/Plugins/Experimental to Engine/Plugins/MovieScene. Remove IsExperimentalVersion, add IsBetaVersion. Remove incomplete GeneratePrestreamingAsset from UCinePrestreamingEditorSubsystem. Move SVG icons from Content/ to Resources/. Delete unused Python script. Remove CanContainContent (no content remaining). Fix EditCondition referencing bCompactFrames (should be bMergeFrames). Clean up DataLayer copy-paste residue in track editor. Remove dead commented-out code. Add cinematic prestreaming graph nodes. | 从 Experimental 提升为 Beta 版本，迁移目录结构，清理残留代码，新增 Movie Render Graph 节点支持 |

### 维护评价

**🆕 刚刚发布 — Beta 阶段**

- **创建时间**：2026-04-19，刚刚从 `Engine/Plugins/Experimental` 迁移到 `Engine/Plugins/MovieScene` 并升级为 Beta
- **当前状态**：`IsBetaVersion=true`，`Installed=false`，需要手动启用
- **代码成熟度**：虽然只有一个 commit 记录在当前路径，但插件已在 Experimental 中经过开发迭代。此次迁移进行了全面的代码清理（移除未完成功能、修复 copy-paste 错误、清理死代码）
- **功能完整性**：已支持 Movie Render Queue 和 Movie Render Graph 两条管线，覆盖虚拟纹理和 Nanite 两大流送类型
- **已知限制**：Graph 节点的说明文档指出第一帧的流送请求不会被捕获（因为委托是懒注册的），但 warmup 帧可以弥补此问题

⚠️ **Beta 警告**：此插件处于 Beta 状态，API 可能在后续版本中发生变化。建议在生产环境中谨慎使用，并关注后续更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/CinematicPrestreaming)
- 官方文档：暂无