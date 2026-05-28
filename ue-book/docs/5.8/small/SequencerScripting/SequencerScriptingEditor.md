# Sequencer Scripting

> Python and editor utility scripting extensions for sequencer and movie scenes

| 属性 | 值 |
|---|---|
| 中文名 | Sequencer 脚本扩展 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、Python 脚本示例） |
| 模块 | `SequencerScripting` (Runtime), `SequencerScriptingEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-05-09 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting) | |

## 用途

这个插件为 Unreal Engine 的 Sequencer（过场动画编辑器）提供完整的脚本化接口。它解决的核心问题是：**Sequencer 底层 API 过于复杂，无法直接暴露给蓝图和 Python**，因此该插件通过一系列 UObject 包装器，将 Sequencer 的核心功能（绑定管理、轨道操作、曲线编辑、FBX 导入导出、动画序列关联等）封装为易于使用的脚本 API。

插件分为两层：
- **SequencerScripting**（运行时）：对 LevelSequence 的基础脚本操作（添加绑定、管理轨道/区段、设置范围等）
- **SequencerScriptingEditor**（编辑器扩展）：面向编辑器的高级工具（FBX 导入导出、动画序列关联、曲线编辑器操作、事件绑定等）

该插件是 Epic 推动"全流程 Python 自动化"战略的关键组件，使得影视制作管线和大型项目可以通过 Python 脚本批量操作 Sequencer，实现自动化过场动画制作。

## 使用场景

- 你有一百个过场动画需要批量修改相机轨道参数 → 用 Python 脚本遍历所有 LevelSequence 自动化修改
- 你需要将 Sequencer 中的骨骼动画导出为 FBX 或 AnimSequence → 用 `ExportLevelSequenceFBX` / `ExportAnimSequence`
- 你需要从外部 DCC 工具（如 Maya）导入 FBX 动画到 Sequencer 绑定 → 用 `ImportLevelSequenceFBX`
- 你需要在蓝图中操作 Sequencer 曲线编辑器（选择关键帧、调整曲线颜色等） → 用 `SequencerCurveEditorObject`
- 你需要为 Sequencer 事件轨道创建快速绑定 → 用 `CreateQuickBinding` / `CreateEvent`
- 你需要在 ControlRig 轨道上导入/导出 FBX → 用 `ImportFBXToControlRig` / `ExportFBXFromControlRig`

## 蓝图用法

### FBX 导入导出

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ExportLevelSequenceFBX` | 将指定绑定和轨道导出为 FBX 文件 | `USequencerToolsFunctionLibrary` |
| `ImportLevelSequenceFBX` | 从 FBX 文件导入动画到指定绑定 | `USequencerToolsFunctionLibrary` |
| `ExportFBXFromControlRig` | 从 ControlRig 轨道区段导出 FBX | `USequencerToolsFunctionLibrary` |
| `ImportFBXToControlRig` | 将 FBX 导入到 ControlRig 轨道 | `USequencerToolsFunctionLibrary` |

### 动画序列关联

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ExportAnimSequence` | 将绑定的骨骼动画导出为 AnimSequence | `USequencerToolsFunctionLibrary` |
| `ExportAnimSequenceWaitForDelegate` | 导出动画序列，等待委托确认后再执行 | `USequencerToolsFunctionLibrary` |
| `LinkAnimSequence` | 关联 LevelSequence 的骨骼绑定到已有 AnimSequence | `USequencerToolsFunctionLibrary` |
| `ClearLinkedAnimSequences` | 清除 LevelSequence 上所有动画关联 | `USequencerToolsFunctionLibrary` |
| `GetAnimSequenceLinkFromLevelSequence` | 获取 LevelSequence 的动画链接对象 | `USequencerToolsFunctionLibrary` |
| `GetLevelSequenceLinkFromAnimSequence` | 获取 AnimSequence 的关卡序列链接对象 | `USequencerToolsFunctionLibrary` |

### 事件快速绑定

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateQuickBinding` | 创建到 Actor 方法的快速事件绑定 | `USequencerToolsFunctionLibrary` |
| `CreateEvent` | 从已创建的端点和负载创建事件 | `USequencerToolsFunctionLibrary` |
| `IsEventEndpointValid` | 检查事件端点是否有效 | `USequencerToolsFunctionLibrary` |

### 曲线编辑器

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OpenCurveEditor` | 打开曲线编辑器 | `USequencerCurveEditorObject` |
| `CloseCurveEditor` | 关闭曲线编辑器 | `USequencerCurveEditorObject` |
| `IsCurveEditorOpen` | 曲线编辑器是否已打开 | `USequencerCurveEditorObject` |
| `ApplyFilter` | 对曲线编辑器应用过滤器 | `USequencerCurveEditorObject` |
| `GetChannelsWithSelectedKeys` | 获取包含已选关键帧的通道列表 | `USequencerCurveEditorObject` |
| `GetSelectedKeys` | 获取指定通道中已选关键帧的索引 | `USequencerCurveEditorObject` |
| `SelectKeys` | 选择指定通道中的关键帧 | `USequencerCurveEditorObject` |
| `EmptySelection` | 清空当前选择 | `USequencerCurveEditorObject` |
| `ShowCurve` | 显示/隐藏指定通道的曲线 | `USequencerCurveEditorObject` |
| `IsCurveShown` | 指定通道的曲线是否正在显示 | `USequencerCurveEditorObject` |

### 曲线颜色管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `HasCustomColorForChannel` | 检查通道是否有自定义颜色 | `USequencerCurveEditorObject` |
| `GetCustomColorForChannel` | 获取通道自定义颜色 | `USequencerCurveEditorObject` |
| `SetCustomColorForChannel` | 设置通道自定义颜色 | `USequencerCurveEditorObject` |
| `SetCustomColorForChannels` | 批量设置通道自定义颜色 | `USequencerCurveEditorObject` |
| `SetRandomColorForChannels` | 为通道设置随机颜色 | `USequencerCurveEditorObject` |
| `DeleteColorForChannels` | 删除通道的自定义颜色 | `USequencerCurveEditorObject` |

### 使用示例（蓝图描述）

**示例 1：导出 LevelSequence 为 FBX**

1. 创建 `FSequencerExportFBXParams` 结构体，设置 World、Sequence、Bindings、Tracks 和 FBXFileName
2. 调用 `ExportLevelSequenceFBX`，传入该参数结构体
3. 返回 `true` 表示导出成功

**示例 2：管理曲线编辑器颜色**

1. 调用 `SetRandomColorForChannels` 为目标通道设置随机颜色，传入通道的 Class 和 Identifier 数组
2. 使用 `HasCustomColorForChannel` 检查是否已存在自定义颜色
3. 调用 `GetCustomColorForChannel` 读取颜色值

**示例 3：创建事件快速绑定**

1. 调用 `CreateQuickBinding`，传入 Sequence、目标 Object、函数名和是否在编辑器中调用
2. 使用 `IsEventEndpointValid` 验证返回的 `FSequencerQuickBindingResult`
3. 调用 `CreateEvent` 创建最终的事件，传入 Endpoint 和 Payload 字符串数组

## C++ 用法

### 头文件引入

```cpp
#include "SequencerTools.h"
#include "SequencerCurveEditorObject.h"
```

### 基本用法 — FBX 导出

```cpp
// 来源: Public/SequencerTools.h
#include "SequencerTools.h"
#include "LevelSequence.h"

void ExportSequenceToFBX(UWorld* World, ULevelSequence* Sequence)
{
    // 构建导出参数
    FSequencerExportFBXParams Params;
    Params.World = World;
    Params.Sequence = Sequence;
    Params.RootSequence = Sequence;
    Params.Bindings = { FMovieSceneBindingProxy(FGuid(), Sequence) }; // 按需填充绑定
    Params.Tracks = {}; // 按需填充轨道
    Params.OverrideOptions = nullptr; // 使用默认 FBX 导出选项
    Params.FBXFileName = TEXT("C:/Export/output.fbx");

    bool bSuccess = USequencerToolsFunctionLibrary::ExportLevelSequenceFBX(Params);
    UE_LOG(LogTemp, Log, TEXT("FBX Export %s"), bSuccess ? TEXT("succeeded") : TEXT("failed"));
}
```

### 基本用法 — 动画序列关联

```cpp
// 来源: Public/SequencerTools.h
#include "SequencerTools.h"

void LinkAndExportAnimSequence(UWorld* World, ULevelSequence* Sequence,
    UAnimSequence* AnimSeq, UAnimSeqExportOption* ExportOptions,
    const FMovieSceneBindingProxy& Binding)
{
    // 导出动画序列并创建双向链接
    bool bExported = USequencerToolsFunctionLibrary::ExportAnimSequence(
        World, Sequence, AnimSeq, ExportOptions, Binding, /*bCreateLink=*/true);

    // 之后可以通过以下方式查询链接关系
    UAnimSequenceLevelSequenceLink* Link =
        USequencerToolsFunctionLibrary::GetLevelSequenceLinkFromAnimSequence(AnimSeq);

    // 获取 LevelSequence 的所有动画链接
    ULevelSequenceAnimSequenceLink* SeqLinks =
        USequencerToolsFunctionLibrary::GetAnimSequenceLinkFromLevelSequence(Sequence);
}
```

### 进阶用法 — 事件快速绑定

```cpp
// 来源: Public/SequencerTools.h
#include "SequencerTools.h"
#include "MovieSceneEventSection.h"

void CreateSequencerEvent(UMovieSceneSequence* Sequence, UObject* TargetObject,
    UMovieSceneEventSectionBase* EventSection)
{
    // 创建快速绑定到目标对象的函数
    FSequencerQuickBindingResult Endpoint = USequencerToolsFunctionLibrary::CreateQuickBinding(
        Sequence, TargetObject, TEXT("Set Actor Scale 3D"), /*bCallInEditor=*/false);

    // 验证端点有效性
    if (!USequencerToolsFunctionLibrary::IsEventEndpointValid(Endpoint))
    {
        UE_LOG(LogTemp, Warning, TEXT("Invalid event endpoint"));
        return;
    }

    // 创建事件并添加到区段
    TArray<FString> Payload = { TEXT("1.0, 1.0, 1.0") }; // 负载参数
    FMovieSceneEvent Event = USequencerToolsFunctionLibrary::CreateEvent(
        Sequence, EventSection, Endpoint, Payload);
}
```

### 进阶用法 — 曲线编辑器操作

```cpp
// 来源: Public/SequencerCurveEditorObject.h
#include "SequencerCurveEditorObject.h"

void ManipulateCurves(USequencerCurveEditorObject* CurveEditor)
{
    // 打开曲线编辑器
    CurveEditor->OpenCurveEditor();

    // 获取包含已选关键帧的通道
    TArray<FSequencerChannelProxy> Channels = CurveEditor->GetChannelsWithSelectedKeys();

    for (const FSequencerChannelProxy& Channel : Channels)
    {
        // 获取该通道的已选关键帧索引
        TArray<int32> SelectedIndices = CurveEditor->GetSelectedKeys(Channel);

        // 设置自定义颜色
        CurveEditor->SetCustomColorForChannel(
            Channel.Section->GetClass(),
            Channel.ChannelName.ToString(),
            FLinearColor::Red);

        // 显示曲线
        CurveEditor->ShowCurve(Channel, true);
    }
}
```

## Demo 示例

### 最小完整示例 — 通过蓝图函数库操作 Sequencer

```cpp
// MySequencerAutomation.h
#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "LevelSequence.h"
#include "MovieSceneBindingProxy.h"
#include "SequencerTools.h"
#include "MySequencerAutomation.generated.h"

UCLASS()
class UMySequencerAutomation : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    /**
     * 批量导出指定 LevelSequence 中所有绑定的动画为 AnimSequence。
     * 适用于需要从过场动画中批量提取骨骼动画的管线场景。
     */
    UFUNCTION(BlueprintCallable, Category = "My Tools | Sequencer")
    static bool BatchExportAnimSequences(
        UWorld* World,
        ULevelSequence* Sequence,
        UAnimSeqExportOption* ExportOptions,
        const TArray<FMovieSceneBindingProxy>& Bindings,
        const FString& OutputDirectory);
};
```

```cpp
// MySequencerAutomation.cpp
#include "MySequencerAutomation.h"
#include "AnimSequence.h"
#include "MovieScene.h"

bool UMySequencerAutomation::BatchExportAnimSequences(
    UWorld* World,
    ULevelSequence* Sequence,
    UAnimSeqExportOption* ExportOptions,
    const TArray<FMovieSceneBindingProxy>& Bindings,
    const FString& OutputDirectory)
{
    if (!World || !Sequence || Bindings.Num() == 0)
    {
        return false;
    }

    int32 SuccessCount = 0;

    for (int32 i = 0; i < Bindings.Num(); ++i)
    {
        const FMovieSceneBindingProxy& Binding = Bindings[i];

        // 为每个绑定创建新的 AnimSequence 资产
        FString AssetName = FString::Printf(TEXT("AnimSeq_%s_%d"),
            *Sequence->GetName(), i);
        FString PackagePath = FPaths::Combine(OutputDirectory, AssetName);
        UPackage* Package = CreatePackage(*PackagePath);
        UAnimSequence* AnimSeq = NewObject<UAnimSequence>(Package, *AssetName, RF_Public | RF_Standalone);

        // 使用 SequencerTools 导出并创建双向链接
        bool bExported = USequencerToolsFunctionLibrary::ExportAnimSequence(
            World, Sequence, AnimSeq, ExportOptions, Binding, /*bCreateLink=*/true);

        if (bExported)
        {
            // 保存资产
            FAssetRegistryModule::AssetCreated(AnimSeq);
            Package->MarkPackageDirty();
            UPackage::SavePackage(Package, AnimSeq,
                EObjectFlags::RF_Standalone, *FPackageName::LongPackageNameToFilename(PackagePath, FPackageName::GetAssetPackageExtension()));
            ++SuccessCount;
        }
    }

    UE_LOG(LogTemp, Log, TEXT("Batch export: %d/%d succeeded"),
        SuccessCount, Bindings.Num());
    return SuccessCount > 0;
}
```

## 模块依赖

从 Build.cs 分析，该插件依赖以下非通用模块：

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer 核心数据模型（MovieSceneSection、MovieSceneTrack 等） |
| `LevelSequenceEditor` | 编辑器中的 LevelSequence 操作（打开/关闭序列编辑器） |
| `LevelSequence` | LevelSequence 资产类型和评估器 |
| `ControlRig` | ControlRig 轨道的 FBX 导入导出支持 |
| `FbxExport` / `FbxImport` | FBX 文件格式的读写 |
| `AnimGraph` | 动画图表相关功能 |
| `UnrealEd` | 编辑器功能（序列录制、FBX 对话框等） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b209798d` | Anim In Engine: Add bRemoveExcludedCurves option to animation recording so we can remove curves alre | 添加动画录制中移除排除曲线的选项 |
| 2026-04-24 | `8b8110b4` | [EDA] Add Sequencer tool wrappers + fix sequencer toolset tests | 添加 Sequencer 工具包装器并修复工具集测试 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到 UE_LOGF 新格式 |
| 2026-04-10 | `77af3950` | [EDA] Add SequencerTools toolset with Anim Mixer split into separate plugin | 添加 SequencerTools 工具集，动画混合器拆分为独立插件 |
| 2026-04-10 | `8bd8f719` | [Backout] - CL52569948 | 回退之前的提交 |

### 维护评价

该插件处于**活跃维护**状态：

- **年龄**：2018 年创建，已有约 8 年历史
- **实验性标记**：尽管已存在 8 年，`.uplugin` 中 `IsBetaVersion` 仍为 `true`，表明 Epic 将其视为仍在演进中的 API
- **近期活跃度**：2026 年 4-5 月有多次功能性更新（EDA 工具集、动画录制增强），维护非常活跃
- **API 演进**：许多早期函数（`RenderMovie`、`IsRenderingMovie`、`GetBoundObjects`、`GetObjectBindings`）已在 5.3 标记为废弃，建议迁移到 Movie Render Queue 和 `ULevelSequenceEditorBlueprintLibrary`
- **架构方向**：正在向更模块化的 EDA（Editor Development Architecture）方向重构，动画混合器等组件被拆分为独立插件

**推荐使用**：✅ 推荐。该插件是 Sequencer 自动化的核心接口，虽然标记为 Beta，但 API 已经相当稳定且持续得到维护。注意关注废弃函数的迁移路径，优先使用新推荐的 API（如 Movie Render Queue 替代 `RenderMovie`）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting)
- 官方文档（无公开链接）