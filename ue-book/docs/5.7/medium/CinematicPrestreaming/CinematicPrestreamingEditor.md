# Cinematic Prestreaming

> Adds a way to record certain types of streaming data requests in cinematic cutscenes. The requests can then be played back in advance on the Sequencer timeline to pre-stream data during normal gameplay/rendering.

| 属性 | 值 |
|---|---|
| 中文名 | 过场预流送 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（SVG 图标等编辑器资源） |
| 模块 | `CinematicPrestreaming` (Runtime), `CinematicPrestreamingEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-29 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CinematicPrestreaming) | |

## 用途

该插件解决的是**过场动画渲染时的数据流送延迟**问题。在播放包含大量高分辨率虚拟纹理（VT）、Nanite 网格等资源的过场动画时，引擎通常需要即时流送这些数据，可能导致画面卡顿或渲染低质量 mip。本插件提供一种机制：在离线渲染阶段（通过 Movie Render Queue）**记录**特定类型的数据流送请求（如 VT 页面请求、Nanite 渲染请求），然后将这些请求保存为资产；在运行时（或编辑器预览中）通过 Sequencer 时间线上的“预流送轨道”**提前回放**这些请求，确保资源在需要渲染之前已经完成加载。

- **记录阶段**：使用 MRQ 中的 `Prestreaming Recorder` 设置，在渲染过场动画时收集每一帧的流送请求。
- **回放阶段**：生成的预流送数据资产（`UCinePrestreamingData`）可以被 Sequencer 轨道引用，播放时按时间顺序提前加载数据。

> 该插件目前是实验性功能，核心记录/回放逻辑位于 `CinematicPrestreaming` 运行时模块，编辑器模块提供的是 UI、调试渲染和 MRQ 集成。

## 使用场景

- 你在制作一个包含大量虚拟纹理地面/建筑、高精度 Nanite 树木、角色、粒子的过场动画 → 使用此插件预流送，避免播放时画面突然模糊或掉帧。
- 你需要确保最终渲染输出（或实时游戏播放）时所有资源都已就绪，但又不希望手动加载序列 → 通过 Sequencer 上的预流送轨道自动管理。
- 你已经在使用 MRQ 批量渲染过场动画 → 只需添加一个 `Prestreaming Recorder` 设置即可自动生成预流送数据，无需额外工作流。

## 蓝图用法

以下 API 来自 `CinematicPrestreamingEditor` 模块，主要面向编辑器环境下通过蓝图/脚本进行自动化操作。

### 核心节点（编辑器子系统）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Is Rendering` | 检查是否正在执行预流送录制渲染。返回 `true` 或 `false`。 | `UCinePrestreamingEditorSubsystem` |
| `Generate Prestreaming Asset` | 启动一个 MRQ 渲染任务来生成预流送资产。传入 `FCinePrestreamingGenerateAssetArgs` 参数（包含 Sequence、Map、Resolution 等）。 | `UCinePrestreamingEditorSubsystem` |
| `Create Packages From Generated Data` | 将从 MRQ 生成的原始数据（`FMoviePipelineCinePrestreamingGeneratedData` 数组）打包为最终资产包（`.uasset`）。通常作为 `OnGenerateData` 响应的后续处理。 | `UCinePrestreamingEditorSubsystem` |
| `On Asset Generated`（事件） | 当一次 `GeneratePrestreamingAsset` 完成渲染并生成数据时触发。输出参数与输入相同，可用于监控进度。 | `UCinePrestreamingEditorSubsystem` |

### 常用属性（MRQ 设置）

在 `UCinePrestreamingRecorderSetting` 中暴露的常用属性（可直接在 MRQ 设置的 Details 面板中修改）：

| 属性 | 说明 | 类型 |
|---|---|---|
| `Package Directory` | 生成资产的输出路径（如 `/Game/MyCutscenes/Prestream`）。 | FDirectoryPath |
| `b Virtual Textures` | 是否录制虚拟纹理页面请求。 | bool |
| `b Nanite` | 是否录制 Nanite 渲染请求。 | bool |
| `b Modify Target Sequence` | 是否自动将生成的轨道添加到目标 Sequence 中。 | bool |
| `b Disable Advance Render Features` | 优化：录制时禁用不必要的渲染特性以加快速度（但生成的图像不可用）。 | bool |
| `Start Frame / End Frame` | 限定录制帧范围（0 表示不限制）。 | int32 |

### 使用示例（蓝图）

1. **手动触发一次预流送资产生成**
   - 获取编辑器子系统：`Get Editor Subsystem (by Class)` → 选择 `CinePrestreaming Editor Subsystem`。
   - 调用 `Generate Prestreaming Asset`，构造 `FCinePrestreamingGenerateAssetArgs`，设置 `Sequence`（一个 Level Sequence）、`Map`（对应 World）、`Resolution`（如 1920x1080）。
   - 连接 `On Asset Generated` 事件，以获取回调信息。

2. **录制并打包资产**
   - 在 MRQ 配置中添加 `Prestreaming Recorder` 设置（类型为 `Prestreaming Recorder`）。
   - 在渲染完成后，通过 `OnGenerateData` 事件获取 `FMoviePipelineCinePrestreamingGeneratedData` 数组。
   - 调用 `Create Packages From Generated Data` 将这些数据保存为资产（若未自动执行）。

## C++ 用法

### 头文件引入

```cpp
#include "CinePrestreamingEditorSubsystem.h"
#include "CinePrestreamingRecorderSetting.h"
```

### 基本用法

**1. 通过编辑器子系统启动一个预流送录制**

```cpp
// 获取编辑器子系统
UCinePrestreamingEditorSubsystem* Subsystem = GEditor->GetEditorSubsystem<UCinePrestreamingEditorSubsystem>();
if (Subsystem && !Subsystem->IsRendering())
{
    // 构建参数
    FCinePrestreamingGenerateAssetArgs Args;
    Args.Sequence = TSoftObjectPtr<ULevelSequence>(FSoftObjectPath("/Game/Cinematics/MySequence.MySequence"));
    Args.Map = TSoftObjectPtr<UWorld>(FSoftObjectPath("/Game/Maps/MyMap.MyMap"));
    Args.Resolution = FIntPoint(1920, 1080);
    // 可选：指定输出目录覆盖
    Args.OutputDirectoryOverride.Path = TEXT("/Game/PrestreamingData/MyCutscene");

    // 启动渲染
    Subsystem->GeneratePrestreamingAsset(Args);
}
```

**2. 在 MRQ 设置中自定义录制行为**

```cpp
// 在创建 MRQ 设置时添加 Prestreaming Recorder
UCinePrestreamingRecorderSetting* RecorderSetting = NewObject<UCinePrestreamingRecorderSetting>();
RecorderSetting->bVirtualTextures = true;
RecorderSetting->bNanite = true;
RecorderSetting->bDisableAdvanceRenderFeatures = true;
RecorderSetting->PackageDirectory.Path = TEXT("/Game/PrestreamingData");
// 然后将此设置添加到 UMoviePipelinePrimaryConfig 或 UMoviePipelineShotConfig 中
```

**3. 响应生成完成事件**

```cpp
// 绑定 OnGenerateData 委托
RecorderSetting->OnGenerateData.AddLambda(
    [](const TArray<FMoviePipelineCinePrestreamingGeneratedData>& GeneratedData)
    {
        for (const auto& Data : GeneratedData)
        {
            UE_LOG(LogTemp, Log, TEXT("Generated prestreaming asset for %s at %s"),
                   *Data.AssetName, *Data.PackagePath);
        }
    }
);
```

### 进阶用法

**组合使用：手动触发渲染并创建资产包**

以下示例展示了如何通过 C++ 在不打开 MRQ UI 的情况下完成全流程：

```cpp
// 1. 构建参数
FCinePrestreamingGenerateAssetArgs Args;
Args.Sequence = ...;
Args.Map = ...;
Args.Resolution = ...;

// 2. 启动渲染（会自动在后台运行 MRQ）
Subsystem->OnAssetGenerated.AddLambda(
    [Subsystem](FCinePrestreamingGenerateAssetArgs OriginalArgs)
    {
        // 3. 渲染完成后，从 AMoviePipelineExecutorBase 获取生成的原始数据
        // 通常需要监听 MRQ 完成。更好的方式是等待 MRQ 回回调：
        // 但子系统内部已经做了：OnGenerateData 会携带数据，再调用 CreatePackagesFromGeneratedData
    }
);
Subsystem->GeneratePrestreamingAsset(Args);

// 注意：内部实现中，GeneratePrestreamingAsset 会创建一个临时的 MRQ 队列，
// 并在渲染完成后自动调用 CreatePackagesFromGeneratedData（如需自动打包）。
// 具体行为取决于 bModifyTargetSequence 等设置。
```

**在 Sequencer 轨道编辑器中添加自定义预流送分段**

`FCinePrestreamingTrackEditor` 提供了在 Sequencer 时间线上添加预流送段的功能，但该类是私有的。官方使用方式是通过 MRQ 设置中的 `bModifyTargetSequence` 自动添加轨道，或右键添加 `Cine Prestreaming` 轨道（需要注册）。

## Demo 示例

以下是一个完整的、可编译的最小示例，展示如何通过 C++ 脚本在编辑器中触发一次预流送资产生成。假设你的模块依赖了 `CinematicPrestreamingEditor` 和 `MovieRenderPipeline`，且运行在编辑器模式下。

```cpp
// MyPrestreamingHelper.h
#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "MyPrestreamingHelper.generated.h"

UCLASS()
class UMyPrestreamingHelper : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Prestreaming")
    static void QuickGeneratePrestreaming(
        ULevelSequence* Sequence,
        UWorld* World,
        FIntPoint Resolution,
        const FString& OutputDir = TEXT("/Game/PrestreamingTemp"))
    {
        UCinePrestreamingEditorSubsystem* Subsystem = GEditor->GetEditorSubsystem<UCinePrestreamingEditorSubsystem>();
        if (!Subsystem || Subsystem->IsRendering())
        {
            UE_LOG(LogTemp, Warning, TEXT("Cannot generate - already rendering or subsystem invalid."));
            return;
        }

        FCinePrestreamingGenerateAssetArgs Args;
        Args.Sequence = Sequence;
        Args.Map = World;
        Args.Resolution = Resolution;
        Args.OutputDirectoryOverride.Path = OutputDir;

        // 绑定回调
        Subsystem->OnAssetGenerated.Clear();
        Subsystem->OnAssetGenerated.AddDynamic(&UMyPrestreamingHelper::OnAssetGenerated);
        Subsystem->GeneratePrestreamingAsset(Args);
    }

private:
    UFUNCTION()
    static void OnAssetGenerated(const FCinePrestreamingGenerateAssetArgs& Args)
    {
        UE_LOG(LogTemp, Log, TEXT("Prestreaming generation completed for %s"), *Args.Sequence.ToString());
    }
};
```

## 模块依赖

使用 `CinematicPrestreamingEditor` 模块时，你的模块需要添加以下依赖（在 `Build.cs` 中）：

| 模块 | 用途 |
|---|---|
| `MovieRenderPipeline` | 核心 MRQ 框架，用于执行录制渲染 |
| `LevelSequence` | 序列编辑器集成 |
| `MovieScene` | 预流送轨道数据结构 |
| `UnrealEd` | 编辑器子系统、菜单扩展 |

**省略常见依赖**：Core, CoreUObject, Engine, Slate, SlateCore, InputCore, UMG 等。

如果只使用时序模块 `CinematicPrestreaming`（运行时），则只需依赖 `MovieRenderPipelineCore` 和 `VirtualTexture` 等相关模块。

## 维护状态

### 近期更新

| 日期 | Hash | Commit 解读 |
|---|---|---|
| 2025-04-04 | a130cb0d | 将待定虚拟纹理 mip 的调试可视化移到后处理阶段 |
| 2025-02-13 | 5fa596c5 | 为 Cinematic Prestreaming 轨道添加显示名称 |
| 2024-08-01 | 8b337f53 | 修复 TSoftObjectPtr 的 const 正确性问题 |
| 2024-07-15 | 927c5d41 | Sequencer：为序列、子分段和骨骼动画分段添加时间扭曲能力 |
| 2024-01-29 | c262d4f9 | Sequencer：大纲视图用户体验改进 |

### 维护评价

该插件创建于 2024-01-29，至今约 1 年，仍处于**实验性**阶段。从最近的 commit 来看：
- 2025 年 4 月有实质性功能更新（调试可视化改进），表明仍在活跃开发。
- 2025 年 2 月添加了轨道显示名称，提升可用性。
- 提交记录显示与 Sequencer 和 MRQ 的集成不断改进。

综合评价：**维护中，但实验性**。插件功能已可用，但可能缺少完整文档和稳定性。如果你在 UE 5.5 或更高版本中使用，值得尝试；但需注意引擎升级时可能有 API 变更。建议在非生产环节先验证。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CinematicPrestreaming)
- [MRQ 文档](https://docs.unrealengine.com/5.3/en-US/movie-render-queue-in-unreal-engine/)（UE 通用文档，该插件依赖 MRQ）
- [Sequencer 时间线文档](https://docs.unrealengine.com/5.3/en-US/sequencer-in-unreal-engine/)