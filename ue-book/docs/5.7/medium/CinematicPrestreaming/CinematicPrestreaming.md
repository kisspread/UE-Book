# Cinematic Prestreaming

> Adds a way to record certain types of streaming data requests in cinematic cutscenes. The requests can then be played back in advance on the Sequencer timeline to pre-stream data during normal gameplay/rendering.

| 属性 | 值 |
|---|---|
| 中文名 | 过场动画预流送 |
| 分类 | Rendering |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（数据资产、Sequence Track/Section 模板） |
| 模块 | `CinematicPrestreaming` (Runtime), `CinematicPrestreamingEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-29 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CinematicPrestreaming) | |

## 用途

在 UE5 中，虚拟纹理（Virtual Texture）和 Nanite 等系统的流送决策通常基于当前屏幕上可见的内容。当高画质的过场动画（Cinematic Cutscenes）需要快速切换镜头或展示远处细节时，默认的按需流送可能来不及加载所需数据，导致卡顿或画面降级。

**Cinematic Prestreaming** 插件提供了一种**记录 - 回放**机制：

1. **记录阶段**：在 Sequencer 中录制过场动画期间，捕捉每一帧所需的虚拟纹理页面、Nanite 请求等流送数据。
2. **回放阶段**：将记录的请求提前注入到 Sequencer 时间线上（通过 `UMovieSceneCinePrestreamingTrack`），在正式渲染**之前**触发数据的预流送，确保数据在需要的时刻已经就绪。

该插件与 **Movie Render Pipeline** 深度集成，常用于电影级渲染管道。

## 使用场景

- **制作电影级过场动画**：当你需要确保在镜头切换或大场景移动时，虚拟纹理和 Nanite 数据能平滑加载，避免画面闪烁或模糊。
- **高分辨率截图/渲染**：在 `Movie Render Pipeline` 输出高质量帧时，提前预加载所有必要数据，减少渲染帧的等待时间。
- **性能监控与优化**：对于复杂的持续世界流送，该插件可以辅助分析哪些数据需要提前加载，从而通过配置 `QualityLevel` 实现分级预流送。

## 蓝图用法

插件暴露的蓝图节点均位于 `UMovieSceneCinePrestreamingSection` 类，用于在 Sequencer 蓝图中控制预流送行为。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetPrestreamingAsset` | 获取该 Section 关联的预流送数据资产（软引用） | `UMovieSceneCinePrestreamingSection` |
| `SetPrestreamingAsset` | 设置该 Section 使用的预流送数据资产 | `UMovieSceneCinePrestreamingSection` |
| `GetQualityLevel` | 获取该 Section 的质量等级（整型）。系统运行时通过 `MovieScene.PreStream.QualityLevel` 设置阈值，低于此阈值的 Section 将被忽略 | `UMovieSceneCinePrestreamingSection` |
| `SetQualityLevel` | 设置质量等级 | `UMovieSceneCinePrestreamingSection` |
| `SetStartFrameOffset` | 设置预流送相对于 Section 起始帧的偏移（帧数）。正值使预流送**提前**发生，负值延迟 | `UMovieSceneCinePrestreamingSection` |

### 使用示例（蓝图描述）

1. **在 Sequencer 中添加预流送轨道**  
   - 将 `CinePrestreamingTrack` 拖拽到 Sequence 中（类似于添加 Cinematic Shot 轨道）。
   - 在轨道上创建 Section，并打开 Section 的细节面板。
2. **关联预流送数据资产**  
   - 通过蓝图调用 `SetPrestreamingAsset`，传入一个已录制好的 `CinePrestreamingData` 数据资产（软引用）。
3. **调整预流送时机**  
   - 调用 `SetStartFrameOffset` 设置提前加载的帧数（例如 `60` 帧表示在 Section 开始前 60 帧就开始加载）。
4. **按质量分级**  
   - 如果项目中有多个质量层次的预流送资产，可通过 `SetQualityLevel` 区分。运行时通过控制台变量 `MovieScene.PreStream.QualityLevel` 全局设定当前设备的等级，低等级设备的 Section 将被自动忽略。

## C++ 用法

### 头文件引入

```cpp
#include "Sections/MovieSceneCinePrestreamingSection.h"
#include "Tracks/MovieSceneCinePrestreamingTrack.h"
#include "CinePrestreamingData.h"
```

### 基本用法

**创建并配置 PrestreamingData 资产**

```cpp
// 创建数据资产对象（通常在编辑器工具模块中由记录过程生成）
UCinePrestreamingData* PrestreamData = NewObject<UCinePrestreamingData>(GetTransientPackage());
PrestreamData->Times = {FFrameNumber(0), FFrameNumber(100)};
PrestreamData->VirtualTextureDatas.Add({ /* PageIds */ });
PrestreamData->NaniteDatas.Add({ /* RequestData */ });
PrestreamData->RecordedTime = FDateTime::UtcNow();
PrestreamData->RecordedResolution = FIntPoint(1920, 1080);

// 保存为资产（略，通常由编辑器录制过程自动完成）
```

**在运行时获取预流送资产并设置到 Section**

```cpp
// 假设已经在你的 C++ Actor 或 Manager 中持有 Section 指针
UMovieSceneCinePrestreamingSection* Section = ...;
TSoftObjectPtr<UCinePrestreamingData> Asset = Section->GetPrestreamingAsset();

// 异步加载资产（如果尚未加载）
if (Asset.IsPending())
{
    FSoftObjectPath AssetPath = Asset.ToSoftObjectPath();
    TSharedPtr<FStreamableHandle> Handle = UAssetManager::GetStreamableManager().RequestAsyncLoad(
        AssetPath,
        FStreamableDelegate::CreateLambda([Section, AssetPath]()
        {
            UCinePrestreamingData* LoadedData = Cast<UCinePrestreamingData>(AssetPath.ResolveObject());
            if (LoadedData)
            {
                // 数据已就绪，系统会自动在动画时使用
                UE_LOG(LogCinePrestreaming, Log, TEXT("Prestream data loaded."));
            }
        })
    );
}
```

**设置 Section 参数**

```cpp
Section->SetPrestreamingAsset(MyData);
Section->SetStartFrameOffset(60);    // 提前 60 帧开始预流送
Section->SetQualityLevel(2);         // 质量等级 2（阈值由控制台变量决定）
```

### 进阶用法

**使用 Track 实例进行手动预流送**

`UMovieSceneCinePrestreamingTrackInstance` 内部管理了 `UCinePrestreamingData` 的加载和卸载。当 Section 进入范围时，`OnInputAdded` 自动开始异步加载；退出范围时 `OnInputRemoved` 取消加载。你不需要直接操作 `LoadHandleMap`，但可以通过重写 Track Instance 来自定义行为。

```cpp
// 继承 UMovieSceneCinePrestreamingTrackInstance 并覆写 OnAnimate()
void UMyCustomPrestreamingTrackInstance::OnAnimate()
{
    // 获取当前输入的 PrestreamingData
    for (auto& Pair : PrestreamingAssetMap)
    {
        UCinePrestreamingData* Data = Pair.Value;
        if (Data)
        {
            // 在此处将预加载的请求提交给渲染系统
            // 例如，批量提交 VirtualTexture 页面请求
        }
    }
}
```

## Demo 示例

以下是一个最小示例，展示如何在蓝图中记录并回放预流送数据。由于实际录制过程依赖编辑器扩展，这里只给出运行时回放的 C++ 代码片段。

**MyPrestreamingPlayer.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CinePrestreamingData.h"
#include "Sections/MovieSceneCinePrestreamingSection.h"
#include "MyPrestreamingPlayer.generated.h"

UCLASS()
class CINEMATICPRESTREAMING_API AMyPrestreamingPlayer : public AActor
{
    GENERATED_BODY()

public:
    // 设置要回放的 PrestreamingData 资产（通过蓝图或世界设置）
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Prestreaming")
    TSoftObjectPtr<UCinePrestreamingData> PrestreamDataAsset;

    // 预流送提前帧数
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Prestreaming")
    int32 StartFrameOffset = 60;

    // 质量等级（根据 MovieScene.PreStream.QualityLevel 全局变量）
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Prestreaming")
    int32 QualityLevel = 1;

    UFUNCTION(BlueprintCallable, CallInEditor, Category = "Prestreaming")
    void StartPrestreaming();

    UFUNCTION(BlueprintCallable, CallInEditor, Category = "Prestreaming")
    void StopPrestreaming();
};
```

**MyPrestreamingPlayer.cpp**

```cpp
#include "MyPrestreamingPlayer.h"
#include "CinePrestreamingData.h"
#include "EntitySystem/MovieSceneInstanceRegistry.h"
#include "EntitySystem/MovieSceneEntitySystemLinker.h"
#include "Tracks/MovieSceneCinePrestreamingTrack.h"
#include "Sections/MovieSceneCinePrestreamingSection.h"
#include "UObject/SoftObjectPath.h"

void AMyPrestreamingPlayer::StartPrestreaming()
{
    if (!PrestreamDataAsset.IsNull())
    {
        // 模拟手动创建一个 Section 并设置参数（实际项目中由 Sequencer 管理）
        UMovieSceneCinePrestreamingSection* Section = NewObject<UMovieSceneCinePrestreamingSection>(this);
        Section->SetPrestreamingAsset(PrestreamDataAsset.Get());
        Section->SetStartFrameOffset(StartFrameOffset);
        Section->SetQualityLevel(QualityLevel);

        // 异步加载数据
        FSoftObjectPath AssetPath = PrestreamDataAsset.ToSoftObjectPath();
        TSharedPtr<FStreamableHandle> Handle = UAssetManager::GetStreamableManager().RequestAsyncLoad(
            AssetPath,
            FStreamableDelegate::CreateLambda([Section, AssetPath]()
            {
                UCinePrestreamingData* LoadedData = Cast<UCinePrestreamingData>(AssetPath.ResolveObject());
                if (LoadedData)
                {
                    UE_LOG(LogTemp, Log, TEXT("Prestreaming data loaded successfully."));
                    // 数据已就绪，系统会通过 TrackInstance 使用
                }
            })
        );
    }
}

void AMyPrestreamingPlayer::StopPrestreaming()
{
    // 清理工作（可在此处取消加载）
    UAssetManager::GetStreamableManager().Unload(PrestreamDataAsset.ToSoftObjectPath());
}
```

## 模块依赖

**运行时模块（`CinematicPrestreaming`）**

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer 核心模块，提供 Entity System、Track、Section 等基础 |
| `MovieSceneTracks` | 用于 Track Instance 注册和动画 |
| `VirtualTexture` | 记录和回放虚拟纹理页面请求 |
| `Nanite` | 记录和回放 Nanite 流送请求 |

**编辑器模块（`CinematicPrestreamingEditor`）**

| 模块 | 用途 |
|---|---|
| (上述运行时模块) | 继承运行时功能 |
| `UnrealEd` | 编辑器界面、录制工具 |
| `MovieRenderPipeline` | 与 MRQ 集成，提供录制功能 |

> *注意：以上依赖基于源码中的头文件引用和常规 UE5 插件体系推断。实际 Build.cs 中可能还包括 `CoreUObject`、`Engine` 等标准模块，此处仅列出特殊的。*

## 维护状态

### 近期更新

- 2025-04-04 `a130cb0d` — 将待处理虚拟纹理 mip 的调试可视化移至后期处理
- 2025-02-13 `5fa596c5` — 为轨道添加显示名称
- 2024-08-01 `8b337f53` — 修复 `TSoftObjectPtr` 的 constness 问题
- 2024-07-15 `927c5d41` — Sequencer：为序列、子片段和蒙皮动画片段添加时间扭曲功能
- 2024-01-29 `c262d4f9` — Sequencer：大纲视图 UX 改进（初始版本）

### 维护评价

- **创建时间**：2024-01-29，至今约1年2个月。
- **更新频率**：近半年内有两次实质性更新（2024-08、2025-02、2025-04），且涉及功能增强和 Bug 修复，表明项目仍在活跃开发中。
- **实验性状态**：`IsExperimentalVersion=true`，API 可能在未来版本中发生不兼容变化。
- **整体评价**：该插件专为高画质过场动画的高效流送设计，对于使用虚拟纹理和 Nanite 的项目非常有用。如果项目中需要集成 Sequencer 并处理性能敏感的渲染数据预加载，**推荐使用**。注意需要搭配 `MovieRenderPipeline` 录制数据资产。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CinematicPrestreaming)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CinematicPrestreaming/Tests)（若有）