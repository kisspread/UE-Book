# Cinematic Prestreaming

> Adds a way to record certain types of streaming data requests in cinematic cutscenes. The requests can then be played back in advance on the Sequencer timeline to pre-stream data during normal gameplay/rendering.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 过场动画预流送 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（数据资产） |
| 模块 | `CinematicPrestreaming` (Runtime), `CinematicPrestreamingEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-19 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/CinematicPrestreaming) | |

## 用途

该插件用于解决在播放过场动画（尤其是电影级画质的过场动画）时，**虚拟纹理（Virtual Texture）和 Nanite** 等流式渲染系统的数据按需加载可能导致的画面卡顿、弹出或质量降低的问题。

**核心问题**：虚拟纹理和 Nanite 的默认流送策略是基于屏幕可见性（视图），即只有当画面中需要显示某块纹理或网格时，系统才会开始加载对应的数据。在复杂的过场动画中，摄像机运动快速，视角切换频繁，这种“按需加载”模式容易导致数据来不及加载完成，造成视觉瑕疵。

**解决方案**：此插件允许开发者在 Sequencer 时间线中录制一段过场动画运行时实际发生的虚拟纹理和 Nanite 流式传输请求。这些请求被保存到一个专用的数据资产（`UCinePrestreamingData`）中。然后，在 Sequencer 时间线上放置一个代表此数据资产的 Section，并配置一个“提前量”（Start FrameOffset）。这样，在游戏正常运行并预演到该过场动画之前，系统就会提前播放这些录制的流送请求，从而确保所需的数据在画面实际需要前已经被加载到内存中，实现平滑的画质呈现。

## 使用场景

- 你正在制作一款拥有电影级过场动画的游戏，并且使用了 **虚拟纹理** 或 **Nanite** 技术。
- 在过场动画中，摄像机快速移动，穿过了广阔的虚拟纹理地形或由 Nanite 构成的复杂建筑群落。
- 你发现在过场动画播放时，远处的地形或细节会突然出现弹出（Pop-in）或分辨率降低（模糊），这是由于流送数据加载不及时导致的。
- **解决方案**：使用 Cinematic Prestreaming 插件。你可以在编辑器中录制一次该过场动画的流送请求，并将录制好的数据资产放置到时间线上。之后每次播放前，游戏都会提前加载这些数据，彻底解决弹出问题。

## 蓝图用法

蓝图 API 主要围绕数据资产和 Sequencer Section 的配置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Prestreaming Asset` | 获取当前 Section 关联的预流送数据资产 | `UMovieSceneCinePrestreamingSection` |
| `Set Prestreaming Asset` | 为当前 Section 设置一个预流送数据资产 | `UMovieSceneCinePrestreamingSection` |
| `Get Quality Level` | 获取此 Section 生效的最低质量等级。当运行时设置的 `MovieScene.PreStream.QualityLevel` 小于此值时，此 Section 将被忽略 | `UMovieSceneCinePrestreamingSection` |
| `Set Quality Level` | 设置此 Section 的最低质量等级阈值 | `UMovieSceneCinePrestreamingSection` |
| `Set Start Frame Offset` | 设置开始帧偏移量（以帧为单位）。值越大，预流送越早开始。这是确保数据提前加载的关键参数 | `UMovieSceneCinePrestreamingSection` |

### 使用示例（蓝图描述）

在 Sequencer 中操作：
1.  打开包含过场动画的 **Level Sequence**。
2.  在轨道列表中，点击 `+` 按钮，找到并添加 `Cinematic Prestreaming` 轨道。
3.  在新轨道上创建一个 Section，覆盖你需要预流送的过场动画时间范围。
4.  选中该 Section，在细节面板中，找到 `Prestreaming` 分类。
5.  将你预先录制好的 `UCinePrestreamingData` 资产（通常位于 Content Browser）拖拽到 `Prestreaming Asset` 属性上。
6.  调整 `Start Frame Offset` 的值。例如，设置为 `30` 意味着系统将在 Sequencer 评估到该 Section 前 30 帧就开始预流送数据。你需要根据场景复杂度和硬件加载速度进行测试调整。

## C++ 用法

该插件主要为 Sequencer 集成，C++ 用法通常在自定义电影流程或需要精细控制流送行为的系统中。

### 头文件引入

```cpp
#include "CinePrestreamingData.h"
#include "Tracks/MovieSceneCinePrestreamingTrack.h"
#include "Sections/MovieSceneCinePrestreamingSection.h"
```

### 基本用法

`UCinePrestreamingData` 是核心数据资产，其内部存储了压缩的虚拟纹理和 Nanite 请求流。
```cpp
// 假设你已经通过插件的编辑器功能（或自定义录制流程）生成了一个 UCinePrestreamingData 资产。
// 在代码中，你通常只需引用它，而不需要手动构造其内部数据。
// 以下为概念性代码，展示其数据结构。
UCinePrestreamingData* PrestreamingData = LoadObject<UCinePrestreamingData>(nullptr, TEXT("/Game/Cinematics/MyShot_PrestreamingAsset"));
if (PrestreamingData)
{
    // Times 数组包含了请求对应的时间点（帧号）
    const TArray<FFrameNumber>& RequestTimes = PrestreamingData->Times;
    
    // 虚拟纹理请求数据，按时间点组织
    const TArray<FCinePrestreamingVTData>& VTData = PrestreamingData->VirtualTextureDatas;
    
    // Nanite 请求数据，按时间点组织
    const TArray<FCinePrestreamingNaniteData>& NaniteData = PrestreamingData->NaniteDatas;
}
```

### 进阶用法

在自定义的电影播放器或需要直接操控 Sequencer 轨道的系统中，可以程序化地创建和配置预流送 Section。
```cpp
// 获取或创建预流送轨道
UMovieSceneCinePrestreamingTrack* PrestreamingTrack = MySequence->FindTrack<UMovieSceneCinePrestreamingTrack>();
if (!PrestreamingTrack)
{
    PrestreamingTrack = MySequence->AddTrack<UMovieSceneCinePrestreamingTrack>();
}

// 创建一个 Section
UMovieSceneCinePrestreamingSection* NewSection = Cast<UMovieSceneCinePrestreamingSection>(PrestreamingTrack->CreateNewSection());
if (NewSection)
{
    // 设置 Section 的时间范围
    FFrameNumber StartFrame = 1000; // 过场动画开始的帧
    FFrameNumber EndFrame = 3000;   // 过场动画结束的帧
    NewSection->SetRange(TRange<FFrameNumber>(StartFrame, EndFrame));
    
    // 关联预流送数据资产
    UCinePrestreamingData* MyData = /* ... */;
    NewSection->SetPrestreamingAsset(MyData);
    
    // 设置提前量，例如提前 50 帧开始加载
    NewSection->SetStartFrameOffset(50);
    
    // 设置质量等级要求，仅在史诗(Epic)画质或以上生效
    NewSection->SetQualityLevel(3); // 假设3代表史诗画质
    
    // 将 Section 添加到轨道
    PrestreamingTrack->AddSection(*NewSection);
}
```

## Demo 示例

一个可编译的最小示例，演示如何在 C++ 中引用和使用预流送数据。

**文件：PrestreamingDemoActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "PrestreamingDemoActor.generated.h"

class UCinePrestreamingData;

UCLASS()
class APrestreamingDemoActor : public AActor
{
    GENERATED_BODY()
    
public:
    APrestreamingDemoActor();

    /** 在编辑器中或代码里指定一个预流送数据资产 */
    UPROPERTY(EditAnywhere, Category = "Prestreaming")
    TObjectPtr<UCinePrestreamingData> PrestreamingDataAsset;

    /** 在 BeginPlay 时打印资产信息，用于验证加载 */
    virtual void BeginPlay() override;
};
```

**文件：PrestreamingDemoActor.cpp**
```cpp
#include "PrestreamingDemoActor.h"
#include "CinePrestreamingData.h"

APrestreamingDemoActor::APrestreamingDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void APrestreamingDemoActor::BeginPlay()
{
    Super::BeginPlay();

    if (PrestreamingDataAsset)
    {
        UE_LOG(LogTemp, Log, TEXT("Loaded Prestreaming Asset: %s"), *PrestreamingDataAsset->GetName());
        UE_LOG(LogTemp, Log, TEXT("  Recorded at Resolution: %s"), *PrestreamingDataAsset->RecordedResolution.ToString());
        UE_LOG(LogTemp, Log, TEXT("  Total Request Frames: %d"), PrestreamingDataAsset->Times.Num());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("No Prestreaming Data Asset assigned to %s."), *GetName());
    }
}
```

## 模块依赖

此插件需要依赖以下引擎模块，这些模块在标准的 Sequencer 或渲染插件中很常见，因此你的项目模块通常已隐含依赖它们。

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer 核心模块，提供 Section、Track 等基础类 |
| `MovieSceneTracks` | Sequencer 基础轨道模块 |
| `LevelSequence` | 处理关卡序列资产 |
| `MovieRenderPipeline` | 电影渲染管线（插件依赖项，用于高质量渲染和流送录制） |

对于直接使用此插件功能的游戏模块，在 `Build.cs` 中添加对 `CinematicPrestreaming` 模块的依赖即可。对于需要修改编辑器功能（如自定义录制器）的编辑器模块，则需要依赖 `CinematicPrestreamingEditor`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-19 | `5057560f` | CinematicPrestreaming: Move plugin out of Experimental and promote to beta. - Move plugin from Engine/Plugins/Experimental to Engine/Plugins/MovieScene - Remove IsExperimentalVersion, add IsBetaVersion - Remove incomplete GeneratePrestreamingAsset from UCinePrestreamingEditorSubsystem - Move SVG icons from Content/ to Resources/ - Delete unused Python script - Remove CanContainContent (no content remaining) - Fix EditCondition referencing bCompactFrames (should be bMergeFrames) - Clean up DataLayer copy-paste residue in track editor - Remove dead commented-out code - Add cinematic prestreaming graph nodes | 将插件从实验目录移至MovieScene目录并升级为Beta版。进行了大量代码清理、修正了错误属性引用、添加了图表节点功能。 |

### 维护评价

- **状态**: **实验性/Beta 版**。该插件刚刚（根据提供的时间）从 `Experimental` 文件夹移出，并标记为 `IsBetaVersion`。
- **活跃度**: **初次提交**。目前仅有一次提交记录，是迁移和整理代码，尚未观察到后续的功能迭代或修复。
- **已知限制**:
    1.  **Beta 状态**：API 和功能可能在未来版本中发生变化。
    2.  **依赖特定渲染功能**：其核心价值依赖于虚拟纹理和 Nanite 这两个特定的渲染技术。
    3.  **录制流程未完全公开**：如何生成 `UCinePrestreamingData` 资产的完整编辑器工作流（`UCinePrestreamingEditorSubsystem` 的 `GeneratePrestreamingAsset` 已被移除）在提供的信息中不明确。
- **推荐使用**：
    - **推荐**：如果你正在开发一个对过场动画质量要求极高，并且确实遇到了虚拟纹理/Nanite 流送弹出问题的项目，可以评估和使用此插件。它的设计目标非常明确。
    - **注意事项**：鉴于其 Beta 状态和缺乏活跃的更新记录，建议在项目中谨慎引入，并做好未来可能需要适配 API 变更的准备。建议密切关注官方源码库的后续更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/CinematicPrestreaming)
- [官方文档](暂无)
- [测试用例](暂无)