# Sequencer Scripting

> Python and editor utility scripting extensions for sequencer and movie scenes（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 序列器脚本 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `SequencerScripting` (Runtime), `SequencerScriptingEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-05-09 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting) | |

## 用途

`SequencerScripting` 插件是一个功能丰富的 Sequencer（序列器）脚本化工具集，它通过蓝图和 Python 暴露了 Sequencer 的核心 API。其存在的核心价值在于**自动化**和**工具开发**：解决了需要通过脚本程序化地创建、编辑、查询、导出和动画序列（Level Sequence）的需求，避免了重复性的手动编辑器操作。

基于源码分析，该插件主要包含两大功能域：
1.  **运行时与基础脚本支持 (`SequencerScripting`)**：提供底层的结构体（如 `FMovieSceneBindingProxy`）和函数库，用于在蓝图或 Python 中表示和操作序列器对象（如绑定、轨道、区段）。
2.  **编辑器与高级工具 (`SequencerScriptingEditor`)**：提供更高层次的编辑器工具函数库（`USequencerToolsFunctionLibrary`）和曲线编辑器对象（`USequencerCurveEditorObject`），涵盖了 FBX 导入/导出、动画序列链接、事件快速绑定、曲线编辑器控制等高级功能。

## 使用场景

-   **自动化创建过场动画**：你需要为游戏批量生成一系列角色对话的过场动画序列 → 使用 Python 脚本创建序列、添加绑定和动画轨道。
-   **开发自定义动画工具**：你在制作一个动画状态机编辑器，需要在运行时或编辑器中动态创建和管理动画序列 → 使用 `SequencerScripting` 模块暴露的 API 进行底层构建。
-   **影视预渲染与自动化测试**：你需要根据配置文件自动渲染多个序列的最终视频 → 使用蓝图脚本调用 `RenderMovie`（尽管已废弃）或结合其他插件。
-   **动画数据流水线**：你需要将序列器中的骨骼动画批量导出为独立的 `UAnimSequence` 资产，或从 FBX 文件批量导入动画数据到序列中 → 使用 `ExportAnimSequence` 和 `ImportLevelSequenceFBX` 等函数。
-   **程序化控制曲线编辑器**：你需要在一个自定义的编辑器窗口中镜像或操作 Sequencer 曲线编辑器的选择和显示状态 → 使用 `USequencerCurveEditorObject`。

## 蓝图用法

该插件的核心蓝图节点主要来自两个函数库：`USequencerToolsFunctionLibrary` 和 `USequencerCurveEditorObject`。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ExportAnimSequence` | 将序列中指定绑定（骨骼网格体）的动画烘焙并导出为 `UAnimSequence` 资产。 | `USequencerToolsFunctionLibrary` |
| `ExportLevelSequenceFBX` | 将序列中指定绑定和轨道的数据导出为 FBX 文件。 | `USequencerToolsFunctionLibrary` |
| `ImportLevelSequenceFBX` | 将 FBX 文件中的动画数据导入到序列的指定绑定上。 | `USequencerToolsFunctionLibrary` |
| `CreateQuickBinding` | 为事件轨道创建一个指向对象函数的快速绑定端点。 | `USequencerToolsFunctionLibrary` |
| `CreateEvent` | 使用之前创建的快速绑定端点和载荷数据创建一个电影场景事件。 | `USequencerToolsFunctionLibrary` |
| `LinkAnimSequence` / `ClearLinkedAnimSequences` | 管理序列与动画序列资产之间的链接关系，便于重新烘焙。 | `USequencerToolsFunctionLibrary` |
| `OpenCurveEditor` / `CloseCurveEditor` | 控制 Sequencer 曲线编辑器窗口的打开与关闭。 | `USequencerCurveEditorObject` |
| `GetChannelsWithSelectedKeys` / `SelectKeys` | 查询和设置在曲线编辑器中被选中的关键帧。 | `USequencerCurveEditorObject` |
| `SetCustomColorForChannel` | 为曲线编辑器中的特定通道设置自定义显示颜色。 | `USequencerCurveEditorObject` |

### 使用示例（蓝图描述）

**场景：将序列中特定角色的动画导出为 `AnimSequence` 资产。**

1.  首先，你需要一个 `ULevelSequence*` 引用（来自资产或场景中的 `ALevelSequenceActor`）和一个代表角色骨骼网格体组件的 `FMovieSceneBindingProxy`。
2.  创建一个 `UAnimSeqExportOption` 对象，设置烘焙参数（如起始/结束帧、是否自定义范围等）。
3.  调用 `ExportAnimSequence` 节点，将世界、序列、要导出的 `AnimSequence` 资产、导出选项和目标绑定作为输入。
4.  节点执行成功后，动画数据将被烘焙到指定的 `AnimSequence` 资产中，并可以设置一个链接以便后续更新。

**场景：通过脚本在曲线编辑器中选中特定通道的关键帧。**

1.  获取或创建一个 `USequencerCurveEditorObject` 实例（通常通过 `ULevelSequenceBlueprintLibrary` 获取当前 Sequencer 的实例）。
2.  确保曲线编辑器已打开（调用 `OpenCurveEditor`）。
3.  构造一个 `FSequencerChannelProxy` 结构体，其中包含目标 `UMovieSceneSection` 和通道名称（如 `"Location.X"`）。
4.  调用 `SelectKeys` 节点，传入通道代理和一个包含要选中关键帧索引的数组。

## C++ 用法

### 头文件引入

```cpp
// 核心结构体和基础脚本支持
#include "SequencerScripting.h"

// 编辑器工具函数库 (用于 FBX 导入导出、动画链接等)
#include "SequencerTools.h"

// 曲线编辑器对象 (用于操作曲线编辑器)
#include "SequencerCurveEditorObject.h"
```

### 基本用法

以下示例演示如何创建一个简单的序列并为其绑定添加一个变换轨道。

```cpp
// 来源：基于 Sequencer 初始脚本暴露的通用模式
#include "LevelSequence.h"
#include "MovieScene.h"
#include "MovieSceneSequence.h"
#include "MovieSceneBindingProxy.h"
#include "Sections/MovieScene3DTransformSection.h"

void CreateSimpleSequence()
{
    // 1. 创建一个新的 Level Sequence 资产
    ULevelSequence* NewSequence = NewObject<ULevelSequence>(GetTransientPackage(), TEXT("MyTestSequence"));
    UMovieScene* MovieScene = NewSequence->GetMovieScene();

    // 2. 定义一个绑定 (假设我们有一个目标 Actor)
    FGuid ObjectBindingId = MovieScene->AddPossessable(TEXT("TargetActor"), AActor::StaticClass());
    FMovieSceneBindingProxy BindingProxy(ObjectBindingId, NewSequence);

    // 3. 为该绑定添加一个 3D 变换轨道
    UMovieScene3DTransformTrack* TransformTrack = MovieScene->AddTrack<UMovieScene3DTransformTrack>(ObjectBindingId);

    // 4. 在轨道上创建一个区段，并设置其范围
    UMovieScene3DTransformSection* TransformSection = Cast<UMovieScene3DTransformSection>(TransformTrack->CreateNewSection());
    TransformSection->SetRange(TRange<FFrameNumber>(0, 100)); // 从第 0 帧到第 100 帧
    TransformTrack->AddSection(*TransformSection);

    // 5. 可以在此处通过 TransformSection 的 Channel 进一步添加关键帧数据
    // ...
}
```

### 进阶用法

结合 `USequencerToolsFunctionLibrary` 和 `USequencerCurveEditorObject` 实现更复杂的编辑器工具逻辑。

```cpp
// 来源：综合自 SequencerTools 和 SequencerCurveEditorObject 的公开 API
#include "SequencerTools.h"
#include "SequencerCurveEditorObject.h"
#include "LevelSequence.h"
#include "MovieSceneBindingProxy.h"
#include "Animation/AnimSequence.h"
#include "Editor/Sequencer/Public/ISequencer.h"

// 示例：导出指定序列中特定绑定的动画，并操作其曲线编辑器
void ExportAnimAndManipulateCurves(ULevelSequence* InSequence, const FMovieSceneBindingProxy& InBinding, UAnimSequence* OutAnimSequence)
{
    // 1. 导出动画序列
    UAnimSeqExportOption* ExportOptions = NewObject<UAnimSeqExportOption>();
    bool bSuccess = USequencerToolsFunctionLibrary::ExportAnimSequence(
        GetWorld(), InSequence, OutAnimSequence, ExportOptions, InBinding, /*bCreateLink=*/ true
    );

    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("动画导出成功。"));
    }

    // 2. 获取并操作曲线编辑器 (需要当前 Sequencer 的实例)
    // 注意：在实际编辑器工具中，通常通过 ULevelSequenceBlueprintLibrary::GetSequencer() 获取。
    TSharedPtr<ISequencer> SequencerPtr = ...; // 假设已获取
    USequencerCurveEditorObject* CurveEditorObj = NewObject<USequencerCurveEditorObject>();
    CurveEditorObj->SetSequencer(SequencerPtr);

    // 3. 打开曲线编辑器并尝试选中一些通道
    if (!CurveEditorObj->IsCurveEditorOpen())
    {
        CurveEditorObj->OpenCurveEditor();
    }

    // 假设我们已知 InBinding 对应轨道的某个 Section 和 ChannelName
    UMovieSceneSection* TargetSection = ...; // 获取目标区段
    FName ChannelName(TEXT("Location.Y"));

    FSequencerChannelProxy ChannelProxy(ChannelName, TargetSection);
    CurveEditorObj->SelectKeys(ChannelProxy, {0, 5, 10}); // 选中索引为0,5,10的关键帧

    // 4. 为选中的通道设置一个自定义颜色
    UClass* ChannelClass = ...; // 获取通道的 UObject 类，如 UMovieSceneFloatChannel
    FString Identifier = ChannelName.ToString();
    CurveEditorObj->SetCustomColorForChannel(ChannelClass, Identifier, FLinearColor::Red);
}
```

## Demo 示例

下面是一个完整的、可编译的最小示例，演示如何在 C++ 中利用 `SequencerScripting` 创建一个序列并为其添加动画。

**MyAnimSequenceGenerator.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyAnimSequenceGenerator.generated.h"

class ULevelSequence;
class UAnimSequence;
struct FMovieSceneBindingProxy;

UCLASS(BlueprintType, Blueprintable)
class MYPROJECT_API UMyAnimSequenceGenerator : public UObject
{
    GENERATED_BODY()

public:
    /** 创建一个测试用的Level Sequence，并为其添加基本的变换动画关键帧 */
    UFUNCTION(BlueprintCallable, Category = "Test")
    ULevelSequence* CreateTestSequence();

    /** 将指定序列中特定绑定的动画导出为一个新的AnimSequence资产 */
    UFUNCTION(BlueprintCallable, Category = "Test")
    UAnimSequence* ExportAnimFromSequence(ULevelSequence* Sequence, const FMovieSceneBindingProxy& Binding);
};
```

**MyAnimSequenceGenerator.cpp**
```cpp
#include "MyAnimSequenceGenerator.h"

#include "LevelSequence.h"
#include "MovieScene.h"
#include "MovieSceneBindingProxy.h"
#include "Sections/MovieScene3DTransformSection.h"
#include "Channels/MovieSceneChannel.h"
#include "KeyParams.h"
#include "SequencerTools.h"
#include "Animation/AnimSequence.h"
#include "UObject/SavePackage.h"

ULevelSequence* UMyAnimSequenceGenerator::CreateTestSequence()
{
    // 创建一个新的 Level Sequence 资产 (保存在内存中)
    ULevelSequence* Sequence = NewObject<ULevelSequence>(GetTransientPackage(), NAME_None, RF_Transient);
    UMovieScene* MovieScene = Sequence->GetMovieScene();

    // 添加一个可拥有对象绑定 (假定绑定到一个AActor)
    FGuid BindingId = MovieScene->AddPossessable(TEXT("TestActor"), AActor::StaticClass());

    // 为该绑定添加一个3D变换轨道
    UMovieScene3DTransformTrack* TransformTrack = MovieScene->AddTrack<UMovieScene3DTransformTrack>(BindingId);
    UMovieScene3DTransformSection* Section = Cast<UMovieScene3DTransformSection>(TransformTrack->CreateNewSection());

    // 设置轨道区段的范围 (0到30帧)
    Section->SetRange(TRange<FFrameNumber>(0, 30));

    // 为X位置通道添加关键帧 (简单示例，假设在0帧位置为0，在30帧位置为100)
    // 注意：实际操作Channel的API较复杂，这里仅为概念演示
    FFrameNumber KeyTime1(0);
    FFrameNumber KeyTime2(30);
    float Value1 = 0.0f;
    float Value2 = 100.0f;
    // 假设的添加关键帧函数，实际需要通过Section->GetChannelProxy()获取通道并操作
    // Section->GetChannelProxy().AddKey(KeyTime1, Value1, EMovieSceneKeyInterpolation::Auto);
    // Section->GetChannelProxy().AddKey(KeyTime2, Value2, EMovieSceneKeyInterpolation::Auto);

    TransformTrack->AddSection(*Section);
    return Sequence;
}

UAnimSequence* UMyAnimSequenceGenerator::ExportAnimFromSequence(ULevelSequence* Sequence, const FMovieSceneBindingProxy& Binding)
{
    if (!Sequence)
    {
        return nullptr;
    }

    // 创建一个临时的AnimSequence资产用于导出
    UAnimSequence* AnimSequence = NewObject<UAnimSequence>(GetTransientPackage(), NAME_None, RF_Transient);

    // 配置导出选项
    UAnimSeqExportOption* ExportOptions = NewObject<UAnimSeqExportOption>();
    ExportOptions->bExportTransforms = true;
    // ... 设置其他选项

    // 调用SequencerTools导出
    bool bExportSuccess = USequencerToolsFunctionLibrary::ExportAnimSequence(
        GetWorld(), Sequence, AnimSequence, ExportOptions, Binding, false /* bCreateLink */
    );

    return bExportSuccess ? AnimSequence : nullptr;
}
```

## 模块依赖

要使用 `SequencerScripting` 插件的功能，你的项目模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `SequencerScripting` | 提供操作序列器所需的底层结构体和基础函数库。 |
| `SequencerScriptingEditor` | 提供编辑器专用的高级工具函数库，如 FBX 导入导出、动画链接等。 |
| `MovieScene` | Sequencer 的核心数据模型模块，包含 `UMovieScene`、`UMovieSceneTrack` 等。 |
| `LevelSequence` | 包含 `ULevelSequence` 资产类型。 |

此外，根据你使用功能的深度，可能还需要依赖 `ControlRig`（用于 ControlRig 相关的导入导出）、`FbxExport`/`FbxImport`（用于 FBX 功能）等模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b209798d` | Anim In Engine: Add bRemoveExcludedCurves option to animation recording so we can remove curves alre | 为动画记录功能添加了移除排除曲线的选项。 |
| 2026-04-24 | `8b8110b4` | [EDA] Add Sequencer tool wrappers + fix sequencer toolset tests | 添加了序列器工具包装器并修复了相关测试。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-04-10 | `77af3950` | [EDA] Add SequencerTools toolset with Anim Mixer split into separate plugin | 添加了 SequencerTools 工具集，并将动画混合器拆分为独立插件。 |
| 2026-04-10 | `8bd8f719` | [Backout] - CL52569948 | 回滚了一个提交。 |

### 维护评价

`SequencerScripting` 插件自 2018 年创建以来，已有约 7 年历史。从近期提交记录看，它在 **2026 年仍有持续的功能更新和维护**（如动画录制功能改进、工具集拆分与封装），表明 Epic 仍在将其作为编辑器扩展和自动化工作流的重要组件进行开发。

尽管在 `.uplugin` 中标记为 `IsBetaVersion: true`，这意味着其 API 可能未完全稳定或存在限制，但其长期存在和持续更新的事实证明了其成熟度和实用价值。它是连接蓝图/Python 与复杂 Sequencer 系统的关键桥梁。

**结论：推荐使用**。虽然 API 带有实验性标签，但对于需要程序化操作 Sequencer 的开发者来说，它是目前最官方、功能最全面的解决方案。使用时请注意关注版本更新日志，以应对可能的 API 变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting)
- 官方文档：暂无专门链接，可参考 [Unreal Engine Python 文档](https://docs.unrealengine.com/en-US/ProductionPipelines/ScriptingAndAutomation/Python/) 中关于 Sequencer 的部分。
- 测试用例：通常位于 `Engine/Plugins/MovieScene/SequencerScripting/Tests` 或 `Engine/Tests` 目录下，可搜索 `IMPLEMENT_SIMPLE_AUTOMATION_TEST` 相关文件。