# Geometry Cache

> Support for distilled Geometry animations（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GeometryCache` (Runtime), `GeometryCacheEd` (Runtime), `GeometryCacheSequencer` (Runtime), `GeometryCacheStreamer` (Runtime), `GeometryCacheTracks` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-04-12 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryCache) | |

## 用途

GeometryCache 插件用于支持“蒸馏”后的几何体动画。它允许将预计算的顶点动画（例如从 Alembic (.abc) 文件导入的流体模拟、布料模拟、角色变形动画等）作为资产在引擎中播放。与骨骼动画不同，它直接存储和回放网格体顶点在每一帧的位置，适用于无法用骨骼驱动的复杂形变效果。

`GeometryCacheSequencer` 模块是此插件与 **Sequencer**（虚幻引擎的非线性动画编辑器）的集成部分。它使得 Geometry Cache 动画资产能够作为 Sequencer 中的一个轨道，从而实现：
- 在过场动画或电影序列中精确控制几何缓存动画的播放时间、速度和范围。
- 将几何缓存动画与其他动画、音频、摄像机运动等事件进行同步。
- 在 Sequencer 时间线上对几何缓存动画进行剪辑、滑移、缩放等编辑操作。

## 使用场景

- 你在制作一个角色面部表情或身体变形的过场动画，该动画由外部 DCC 工具（如 Maya, Houdini）通过顶点动画模拟生成 → 使用 GeometryCache 在 Sequencer 中播放和控制。
- 你需要一个物体破碎或聚合的精确动画，并希望将其与游戏内事件或电影序列中的其他元素精确同步 → 将破碎动画导入为 GeometryCache，并在 Sequencer 中编排。
- 你正在制作一个影视级项目，需要将复杂的流体、烟雾或布料模拟无缝集成到镜头中，并需要非破坏性地调整其时序 → 使用 GeometryCache 轨道在 Sequencer 中进行迭代。

## 蓝图用法

`GeometryCacheSequencer` 模块主要通过 Sequencer 编辑器界面进行操作，其核心功能是注册一个 `TrackEditor`，并未直接暴露大量新的蓝图节点。用户通过 Sequencer UI 与几何缓存轨道交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 无直接蓝图节点 | 该模块的功能通过 Sequencer 编辑器界面提供，而非蓝图节点。 | - |

### 使用示例（蓝图描述）

1.  **在 Sequencer 中添加轨道**：
    *   在 Sequencer 编辑器中，为拥有 `GeometryCacheComponent` 的 Actor 添加一个轨道。
    *   在轨道菜单中，找到并选择 “Geometry Cache” 轨道类型。
    *   将你的 `GeometryCache` 资产拖拽到该轨道上，即可创建动画片段。

2.  **编辑动画片段**：
    *   你可以像编辑其他 Sequencer 片段一样，拖动片段的起始和结束点来调整其在时间线上的位置和持续时间。
    *   右键点击片段可以访问更多选项，如设置播放速率、循环模式等。

## C++ 用法

### 头文件引入

```cpp
#include "GeometryCacheSequencerModule.h"
```

### 基本用法

该模块的核心是向 Sequencer 注册一个自定义的轨道编辑器。以下代码展示了模块的启动和关闭逻辑，这是理解其工作原理的基础。

```cpp
// 来源: Engine/Plugins/Runtime/GeometryCache/Source/GeometryCacheSequencer/Public/GeometryCacheSequencerModule.h
// 在模块启动时，向 Sequencer 注册 GeometryCache 的轨道编辑器。
virtual void StartupModule() override
{
    LLM_SCOPE_BYTAG(GeometryCache);

    ISequencerModule& SequencerModule = FModuleManager::Get().LoadModuleChecked<ISequencerModule>("Sequencer");
    // 将 FGeometryCacheTrackEditor 的工厂方法绑定到 Sequencer 模块。
    TrackEditorBindingHandle = SequencerModule.RegisterTrackEditor(FOnCreateTrackEditor::CreateStatic(&FGeometryCacheTrackEditor::CreateTrackEditor));
}

// 在模块关闭时，从 Sequencer 注销轨道编辑器。
virtual void ShutdownModule() override
{
    ISequencerModule* SequencerModulePtr = FModuleManager::Get().GetModulePtr<ISequencerModule>("Sequencer");
    if (SequencerModulePtr)
    {
        SequencerModulePtr->UnRegisterTrackEditor(TrackEditorBindingHandle);
    }
}
```

### 进阶用法

`FGeometryCacheTrackEditor` 类是 Sequencer 与 GeometryCache 交互的核心。它负责创建轨道、生成 UI 区块（Section）以及处理关键帧逻辑。你可以通过继承或参考此类来理解如何为自定义资产类型创建 Sequencer 集成。

```cpp
// 来源: Engine/Plugins/Runtime/GeometryCache/Source/GeometryCacheSequencer/Classes/GeometryCacheTrackEditor.h
// 轨道编辑器类，负责管理 GeometryCache 轨道在 Sequencer 中的行为。
class FGeometryCacheTrackEditor : public FMovieSceneTrackEditor
{
public:
    // ... 构造函数和静态工厂方法 ...

    // 返回在 Sequencer UI 中显示的轨道名称。
    virtual FText GetDisplayName() const override;

    // 当用户尝试为绑定的对象添加轨道时，构建菜单项。
    virtual void BuildObjectBindingTrackMenu(FMenuBuilder& MenuBuilder, const TArray<FGuid>& ObjectBindings, const UClass* ObjectClass) override;

    // 为给定的轨道和对象绑定创建具体的 Sequencer 区块（Section）UI。
    virtual TSharedRef<ISequencerSection> MakeSectionInterface(UMovieSceneSection& SectionObject, UMovieSceneTrack& Track, FGuid ObjectBinding) override;

    // 判断此轨道编辑器是否支持给定的序列类型（例如，仅支持关卡序列）。
    virtual bool SupportsSequence(UMovieSceneSequence* InSequence) const override;

    // 判断此轨道编辑器是否支持给定的轨道类型（UMovieSceneGeometryCacheTrack）。
    virtual bool SupportsType(TSubclassOf<UMovieSceneTrack> Type) const override;

    // ... 其他用于构建 UI 和处理关键帧的方法 ...
};

// 区块（Section）类，代表 Sequencer 时间线上的一个几何缓存动画片段。
class FGeometryCacheSection : public ISequencerSection, public TSharedFromThis<FGeometryCacheSection>
{
public:
    // ... 构造函数 ...

    // 获取此区块对应的 UMovieSceneSection 对象。
    virtual UMovieSceneSection* GetSectionObject() override;

    // 获取在 Sequencer 时间线上显示的区块标题（通常是资产名称）。
    virtual FText GetSectionTitle() const override;

    // 处理区块的绘制，例如在时间线上显示动画预览。
    virtual int32 OnPaintSection(FSequencerSectionPainter& Painter) const override;

    // 处理区块的调整大小、滑移和缩放操作，以更新内部的动画时间映射。
    virtual void ResizeSection(ESequencerSectionResizeMode ResizeMode, FFrameNumber ResizeTime) override;
    virtual void SlipSection(FFrameNumber SlipTime) override;
    virtual void DilateSection(const TRange<FFrameNumber>& NewRange, float DilationFactor) override;

private:
    // 对所属 Sequencer 区块的引用。
    UMovieSceneGeometryCacheSection& Section;
    // 弱引用到 Sequencer 实例，用于获取时间信息。
    TWeakPtr<ISequencer> Sequencer;
};
```

## Demo 示例

以下是一个最小化的示例，展示如何在 C++ 中获取并操作 Sequencer 中的 GeometryCache 轨道。此代码通常用于编辑器工具或自动化脚本中。

```cpp
// MyGeometryCacheSequencerTool.h
#pragma once
#include "CoreMinimal.h"

class ULevelSequence;
class UGeometryCacheComponent;

class FMyGeometryCacheSequencerTool
{
public:
    /** 为指定的关卡序列和几何缓存组件添加一个 GeometryCache 轨道和片段。 */
    static bool AddGeometryCacheTrackToSequence(ULevelSequence* Sequence, UGeometryCacheComponent* Component, UGeometryCache* CacheAsset);
};
```

```cpp
// MyGeometryCacheSequencerTool.cpp
#include "MyGeometryCacheSequencerTool.h"
#include "GeometryCache.h"
#include "GeometryCacheComponent.h"
#include "LevelSequence.h"
#include "MovieScene.h"
#include "MovieSceneGeometryCacheTrack.h"
#include "MovieSceneGeometryCacheSection.h"
#include "Sections/MovieSceneGeometryCacheSection.h" // 用于访问具体 Section 类型

bool FMyGeometryCacheSequencerTool::AddGeometryCacheTrackToSequence(ULevelSequence* Sequence, UGeometryCacheComponent* Component, UGeometryCache* CacheAsset)
{
    if (!Sequence || !Component || !CacheAsset)
    {
        return false;
    }

    UMovieScene* MovieScene = Sequence->GetMovieScene();
    if (!MovieScene)
    {
        return false;
    }

    // 1. 查找或创建对象绑定（Object Binding）
    FGuid ObjectBindingID;
    // 此处省略了查找或创建绑定到 Component 的逻辑，通常通过 MovieScene->FindSpawnable 或 AddSpawnable 等方法。
    // 假设我们已经有一个有效的 ObjectBindingID。

    // 2. 为该绑定添加一个 GeometryCache 轨道
    UMovieSceneGeometryCacheTrack* NewTrack = Cast<UMovieSceneGeometryCacheTrack>(
        MovieScene->AddTrack(UMovieSceneGeometryCacheTrack::StaticClass(), ObjectBindingID)
    );
    if (!NewTrack)
    {
        return false;
    }

    // 3. 在轨道上创建一个新的片段（Section）
    UMovieSceneGeometryCacheSection* NewSection = Cast<UMovieSceneGeometryCacheSection>(NewTrack->CreateNewSection());
    if (!NewSection)
    {
        MovieScene->RemoveTrack(*NewTrack);
        return false;
    }

    // 4. 配置片段：设置资产和时间范围
    NewSection->SetGeometryCache(CacheAsset);
    TRange<FFrameNumber> SectionRange = MovieScene->GetPlaybackRange(); // 使用序列的播放范围
    NewSection->SetRange(SectionRange);

    // 5. 将片段添加到轨道
    NewTrack->AddSection(*NewSection);

    // 6. 标记序列已修改
    Sequence->Modify();

    return true;
}
```

**Build.cs 依赖说明**：
```csharp
// 在你的模块的 .Build.cs 文件中添加以下依赖
PublicDependencyModuleNames.AddRange(new string[] {
    "GeometryCache",
    "GeometryCacheSequencer",
    "LevelSequence",
    "MovieScene"
});
```

## 模块依赖

从 `GeometryCacheSequencer` 模块的 `Build.cs` 及其功能推断，使用此模块需要以下独特依赖：

| 模块 | 用途 |
|---|---|
| `Sequencer` | 核心依赖，提供 Sequencer 框架和 `ISequencerModule` 接口。 |
| `GeometryCacheEd` | 提供编辑器支持，可能包含资产工厂和导入器。 |
| `GeometryCacheTracks` | 提供 `UMovieSceneGeometryCacheTrack` 和 `UMovieSceneGeometryCacheSection` 等 Sequencer 轨道和片段类。 |

## 维护状态

### 近期更新

1.  **2739c3d30ebc** (2024-07-18): `Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 4/n`
    *   **解读**：代码维护性更新，修正了头文件中的 DLL 导出/导入宏（`UE_API`）的使用方式，确保其应用于函数和静态变量而非类型。这是 Epic 代码库的全局性清理工作的一部分，不影响功能。
2.  **ef0d3477c053** (2024-07-16): `[Sequencer] Update Tracks Names and Reorganize Tracks Order #jira UE-221625 #rb Max.Chen`
    *   **解读**：功能更新。更新了 Sequencer 中轨道的显示名称，并重新组织了轨道的默认顺序。这改善了 Sequencer 的用户体验和可读性。
3.  **fa1c08d366b8** (2024-07-16): `[Backout] - CL39424548 [FYI] brad.monahan #rnx ...`
    *   **解读**：这是一个回滚操作，撤销了之前的提交 `ef0d3477c053`。这表明 `ef0d3477c053` 的更改可能引入了问题或需要进一步调整，随后被回滚。紧接着的 `ef0d3477c053` 可能是重新提交的修正版本。

### 维护评价

- **创建时间**：2018 年，是一个相对成熟的插件。
- **最近更新**：最近的提交集中在 2024 年 7 月，主要是代码风格维护和 Sequencer UI 的微调。没有重大的功能添加或架构变更。
- **活跃度**：处于**维护中**状态。核心功能稳定，更新主要是为了跟随引擎代码规范和小幅改进。
- **已知问题/限制**：作为“蒸馏”动画的播放器，其性能和内存占用与导入的几何缓存资产大小直接相关。非常大的缓存文件可能导致加载时间长和内存压力。
- **推荐使用**：**推荐**。对于需要精确控制顶点动画播放的影视、过场动画或特定游戏玩法场景，这是一个官方且稳定的解决方案。由于其长期存在和持续维护，兼容性有保障。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryCache)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/#importasgeometrycache)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryCache/Tests) (如果存在)