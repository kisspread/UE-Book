# Sequencer Scripting

> Python and editor utility scripting extensions for sequencer and movie scenes

| 属性 | 值 |
|---|---|
| 中文名 | 序列器脚本 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SequencerScripting` (Runtime), `SequencerScriptingEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-05-09 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting) | |

## 用途

Sequencer Scripting 插件的核心是为 Unreal Engine 的**序列器（Sequencer）** 系统提供强大的**Python 和蓝图脚本接口**。它解决的核心问题是：将 Sequencer 复杂的 C++ 原生 API 封装成易于在 Python 和蓝图中使用的函数库，从而实现序列编辑的自动化。

具体而言，它允许开发者通过脚本：
1.  **程序化创建和编辑序列**：动态创建轨道、片段、关键帧，而不仅仅是手动在编辑器中操作。
2.  **批量处理与管线集成**：在制作管线中批量处理多个序列，例如导出数据、应用更改、链接资产等。
3.  **扩展编辑器功能**：通过编写 Python 脚本或蓝图工具，为 Sequencer 添加自定义功能，如批量绑定对象、FBX 导入/导出、与动画序列链接等。

它本质上是 Sequencer 编辑器功能的“遥控器”和“自动化工具箱”。

## 使用场景

-   **影视与动画制作管线**：你需要用 Python 脚本批量从外部 DCC 软件（如 Maya）导入 FBX 动画数据到 Sequencer 的绑定上。
-   **动画工作流优化**：你需要从 Sequencer 中将动画数据导出为 `UAnimSequence` 资产，并建立双向链接以便后续更新。
-   **程序化内容生成**：你在生成关卡或动画时，需要动态创建包含摄像机运动、物体变换的 Sequencer 序列。
-   **自定义编辑器工具**：你希望为 Sequencer 的曲线编辑器编写自定义的过滤器或快捷操作。
-   **事件序列控制**：你需要在序列的特定时间点触发蓝图事件，并希望通过脚本快速设置这些事件端点。

## 蓝图用法

该插件的功能主要通过两个核心蓝图函数库类暴露。

### 核心节点

**来自 `USequencerToolsFunctionLibrary` (Sequencer Tools):**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ExportLevelSequenceFBX` | 将指定的绑定和轨道导出为 FBX 文件。 | `USequencerToolsFunctionLibrary` |
| `ImportLevelSequenceFBX` | 从 FBX 文件导入动画数据到序列的指定绑定上。 | `USequencerToolsFunctionLibrary` |
| `ExportAnimSequence` | 将序列中指定的骨骼网格体绑定导出为 `UAnimSequence`。 | `USequencerToolsFunctionLibrary` |
| `LinkAnimSequence` | 在关卡序列的骨骼网格体绑定与现有的动画序列资产之间建立链接。 | `USequencerToolsFunctionLibrary` |
| `ImportFBXToControlRig` | 将 FBX 文件导入到序列中指定的 Control Rig 轨道上。 | `USequencerToolsFunctionLibrary` |
| `CreateQuickBinding` | 为序列中的事件轨道创建一个快速绑定到对象函数的端点。 | `USequencerToolsFunctionLibrary` |
| `CreateEvent` | 根据一个有效的端点和载荷数据创建一个电影场景事件。 | `USequencerToolsFunctionLibrary` |

**来自 `USequencerCurveEditorObject` (Sequencer Curve Editor):**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OpenCurveEditor` / `CloseCurveEditor` | 打开或关闭序列器的曲线编辑器。 | `USequencerCurveEditorObject` |
| `GetChannelsWithSelectedKeys` | 获取当前在曲线编辑器中有关键帧被选中的通道代理。 | `USequencerCurveEditorObject` |
| `GetSelectedKeys` | 获取指定通道代理中被选中的关键帧索引。 | `USequencerCurveEditorObject` |
| `SelectKeys` | 在曲线编辑器中选中指定通道代理上的关键帧。 | `USequencerCurveEditorObject` |
| `ApplyFilter` | 对曲线编辑器中的曲线应用一个滤镜。 | `USequencerCurveEditorObject` |
| `SetCustomColorForChannel` | 为曲线编辑器中的特定通道设置自定义颜色（存储在编辑器用户偏好中）。 | `USequencerCurveEditorObject` |

### 使用示例（蓝图描述）

1.  **导出动画序列**：
    *   获取一个 `ULevelSequence` 引用。
    *   使用 `GetBindings` (来自其他序列API) 或一个 `FMovieSceneBindingProxy` 指定目标骨骼网格体演员绑定。
    *   创建一个 `UAnimSequence` 资产和一个 `UAnimSeqExportOption` 对象。
    *   将以上对象连接到 `ExportAnimSequence` 节点的对应输入引脚。执行该节点即可将动画烘焙到 `UAnimSequence` 中。

2.  **为曲线通道设置自定义颜色**：
    *   获取 `USequencerCurveEditorObject` 实例（通常通过 `ULevelSequenceBlueprintLibrary` 获得）。
    *   准备通道的 `UClass` (例如 `UFloatProperty` 的 `StaticClass()`) 和一个标识字符串（如通道名称）。
    *   调用 `SetCustomColorForChannel`，传入 `Class`、`Identifier` 和一个 `FLinearColor`。该颜色偏好将被保存。

## C++ 用法

该插件的 C++ API 同样强大，适用于需要深度集成或更高性能的场景。

### 头文件引入

```cpp
// 包含核心工具函数库
#include "SequencerTools.h"

// 包含曲线编辑器操作对象
#include "SequencerCurveEditorObject.h"

// 通常也需要包含序列器相关的核心头文件
#include "LevelSequence.h"
#include "MovieSceneBindingProxy.h"
```

### 基本用法

以下示例展示了如何使用 C++ 导出一个关卡序列中特定绑定的动画。

```cpp
// 文件路径: Engine/Plugins/MovieScene/SequencerScripting/Source/SequencerScriptingEditor/Public/SequencerTools.h (API 定义)
// 假设在某个编辑器工具函数中

void ExportAnimFromSequence(ULevelSequence* Sequence, AActor* TargetActor)
{
    if (!Sequence || !TargetActor)
    {
        return;
    }

    // 1. 找到目标Actor在序列中的绑定
    UMovieSceneSequence* MovieSceneSequence = Sequence;
    TArrayView<TWeakObjectPtr<>> BoundObjects = MovieSceneSequence->GetBoundObjects(FMovieSceneObjectBindingID());
    // ... (此处省略了通过 BoundObjects 数组找到与 TargetActor 匹配的 FMovieSceneBindingProxy 的逻辑)
    FMovieSceneBindingProxy TargetBindingProxy;

    // 2. 准备导出选项
    UAnimSeqExportOption* ExportOptions = NewObject<UAnimSeqExportOption>();
    ExportOptions->bExportMorphTargets = true;
    // ... 设置其他选项

    // 3. 创建或找到目标动画序列资产
    UAnimSequence* AnimSequence = ...; // 通过 LoadObject 或 FindObject 获取

    // 4. 调用静态函数进行导出
    bool bSuccess = USequencerToolsFunctionLibrary::ExportAnimSequence(
        GetWorld(),
        Sequence,
        AnimSequence,
        ExportOptions,
        TargetBindingProxy,
        true // bCreateLink
    );

    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("动画导出并链接成功。"));
    }
}
```

### 进阶用法

结合 `USequencerCurveEditorObject` 和序列数据，可以编写更复杂的编辑工具。

```cpp
// 文件路径: Engine/Plugins/MovieScene/SequencerScripting/Source/SequencerScriptingEditor/Public/SequencerCurveEditorObject.h (API 定义)

void HighlightSelectedKeys()
{
    // 获取当前编辑器的序列器实例
    TSharedPtr<ISequencer> Sequencer = ...; // 通过 FLevelSequenceEditorModule 获取

    // 创建曲线编辑器对象并关联序列器
    USequencerCurveEditorObject* CurveEditorObject = NewObject<USequencerCurveEditorObject>();
    CurveEditorObject->SetSequencer(Sequencer);

    // 获取有选中关键帧的通道
    TArray<FSequencerChannelProxy> ChannelsWithSelectedKeys = CurveEditorObject->GetChannelsWithSelectedKeys();

    for (const FSequencerChannelProxy& ChannelProxy : ChannelsWithSelectedKeys)
    {
        // 获取该通道上选中的关键帧索引
        TArray<int32> SelectedKeys = CurveEditorObject->GetSelectedKeys(ChannelProxy);

        // 在这里，你可以对选中的关键帧进行自定义操作，例如：
        // - 修改它们的值
        // - 改变它们的插值模式
        // - 将它们的信息记录到日志
        // 由于修改关键帧数据通常需要通过 ISequencer 或直接操作 Section，这里仅作演示获取。
        UE_LOG(LogTemp, Log, TEXT("在通道 [%s] 的 Section [%s] 中选中了 %d 个关键帧。"),
            *ChannelProxy.ChannelName.ToString(),
            *ChannelProxy.Section->GetName(),
            SelectedKeys.Num());
    }
}
```

## Demo 示例

一个最小的 C++ 示例，演示如何初始化并使用 `USequencerToolsFunctionLibrary` 的功能。

**文件: MySequencerTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "MySequencerTool.generated.h"

class ULevelSequence;
class AActor;

UCLASS()
class UMySequencerToolLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    /** 演示：将指定演员的动画从序列中导出到 AnimSequence */
    UFUNCTION(BlueprintCallable, Category = "My Tools|Sequencer")
    static bool ExportActorAnimationFromSequence(ULevelSequence* Sequence, AActor* ActorToExport);
};
```

**文件: MySequencerTool.cpp**
```cpp
#include "MySequencerTool.h"
#include "SequencerTools.h"
#include "LevelSequence.h"
#include "MovieSceneBindingProxy.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimSeqExportOption.h"

bool UMySequencerToolLibrary::ExportActorAnimationFromSequence(ULevelSequence* Sequence, AActor* ActorToExport)
{
    if (!Sequence || !ActorToExport)
    {
        UE_LOG(LogTemp, Warning, TEXT("无效的序列或演员输入。"));
        return false;
    }

    // 步骤1: 通过演员查找其在序列中的绑定代理。
    // 注意: 实际项目中，更可靠的方法是使用 ISequencer 的 GetBoundObjects 或遍历绑定。
    TArray<FMovieSceneBindingProxy> AllBindings = Sequence->GetMovieScene()->GetBindings();
    FMovieSceneBindingProxy FoundBinding;

    for (const FMovieSceneBindingProxy& Binding : AllBindings)
    {
        // 简化查找：实际应用可能需要更复杂的匹配逻辑。
        TArray<UObject*> BoundObjects = Sequence->GetBoundObjects(Binding);
        if (BoundObjects.Contains(ActorToExport))
        {
            FoundBinding = Binding;
            break;
        }
    }

    if (!FoundBinding.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("在序列中未找到演员 %s 的绑定。"), *ActorToExport->GetName());
        return false;
    }

    // 步骤2: 创建一个默认的 AnimSequence 资产和导出选项
    // 这里假设我们创建一个临时的包和资产用于演示
    UPackage* Pkg = CreatePackage(nullptr, *FString::Printf(TEXT("/Game/Temp/%s_Anim"), *ActorToExport->GetName()));
    UAnimSequence* AnimSequence = NewObject<UAnimSequence>(Pkg, *FString::Printf(TEXT("%s_Anim"), *ActorToExport->GetName()), RF_Public | RF_Standalone);
    UAnimSeqExportOption* ExportOptions = NewObject<UAnimSeqExportOption>();

    // 步骤3: 调用 SequencerTools 的静态导出函数
    bool bSuccess = USequencerToolsFunctionLibrary::ExportAnimSequence(
        ActorToExport->GetWorld(),
        Sequence,
        AnimSequence,
        ExportOptions,
        FoundBinding,
        true // bCreateLink
    );

    if (bSuccess)
    {
        // 标记资产为已修改并保存（可选）
        AnimSequence->MarkPackageDirty();
        UE_LOG(LogTemp, Log, TEXT("成功将 %s 的动画导出到 %s。"), *ActorToExport->GetName(), *AnimSequence->GetPathName());
    }

    return bSuccess;
}
```

## 模块依赖

从 `SequencerScriptingEditor` 模块的 `Build.cs` 分析，该插件除了通用依赖外，还需要以下特定模块：

| 模块 | 用途 |
|---|---|
| `ControlRig` | 支持将动画导入/导出到 Control Rig 轨道。 |
| `Animation` | 处理 `UAnimSequence` 资产的创建和链接。 |
| `FBX` | 提供 FBX 文件导入和导出的底层支持。 |
| `EditorScriptingUtilities` | 提供通用的编辑器脚本工具函数。 |
| `MovieSceneTools` | 提供序列器编辑器相关的工具函数。 |
| `LevelSequenceEditor` | 获取当前在编辑器中打开的 Sequencer 实例。 |
| `ToolMenus` | 用于扩展编辑器菜单，可能用于添加 Sequencer 相关的上下文操作。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b209798d` | Anim In Engine: Add bRemoveExcludedCurves option to animation recording so we can remove curves already | 动画录制中增加移除排除曲线的选项，用于提前清理已有曲线。 |
| 2026-04-24 | `8b8110b4` | [EDA] Add Sequencer tool wrappers + fix sequencer toolset tests | 添加序列器工具封装函数，并修复序列器工具集的相关测试。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将通用的 UE_LOG 日志输出迁移到更结构化的 UE_LOGF 宏。 |
| 2026-04-10 | `77af3950` | [EDA] Add SequencerTools toolset with Anim Mixer split into separate plugin | 添加 SequencerTools 工具集，并将动画混合器拆分为独立插件。 |
| 2026-04-10 | `8bd8f719` | [Backout] - CL52569948 | 回滚一个提交 (CL52569948)。 |

### 维护评价

-   **活跃维护**：从最近的提交记录来看，该插件仍在被积极维护和更新。最近的提交都发生在 2026 年 4 月和 5 月，主要集中在功能增强（添加新的动画录制选项、扩展工具集）和代码改进（日志迁移、测试修复）。
-   **功能状态**：插件标记为实验性 (`IsBetaVersion=true`) 且默认未启用 (`Installed: false`)，表明其 API 可能还不完全稳定，未来版本可能会有变动。许多功能（如 `RenderMovie`）已被标记为废弃，推荐使用更新的 `Movie Render Queue` 系统。
-   **推荐使用**：对于需要深度自动化 Sequencer 工作流、特别是涉及动画数据导出/导入和 FBX 交换的**高级用户和管线开发者**，该插件是必不可少的工具。普通蓝图用户可能更倾向于使用官方更新、更稳定的 `ULevelSequenceEditorBlueprintLibrary` 等接口。建议在项目中使用时，密切关注 API 的废弃警告并做好向后兼容的准备。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting)
-   官方文档：暂无专门链接。
-   测试用例：路径未在提供的信息中明确，但可能位于 `Engine/Plugins/MovieScene/SequencerScripting/Tests` 或 `Engine/Tests` 下。