# Sequencer Scripting

> Python and editor utility scripting extensions for sequencer and movie scenes

| 属性 | 值 |
|---|---|
| 中文名 | 序列器脚本 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `SequencerScripting` (Runtime), `SequencerScriptingEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-05-09 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting) | |

## 用途

SequencerScripting 是 Sequencer（关卡序列器）与 Python/蓝图脚本之间的桥梁。Sequencer 自身的 C++ API 暴露复杂、面向内部设计，不适合直接脚本化操作。此插件通过封装层（UObject 包装器）将 Sequencer 的核心能力暴露为易用的蓝图节点和 Python 函数。

**解决的核心问题**：允许开发者通过 Python 脚本或蓝图自动化 Sequencer 工作流——包括导入/导出 FBX 动画数据、管理 Sequencer 曲线编辑器、创建事件绑定、关联 AnimSequence 与 LevelSequence 等。

插件分为两个模块：
- **SequencerScripting**（Runtime）：核心序列器脚本功能，包括 UMG 动画轨道支持
- **SequencerScriptingEditor**（Runtime）：编辑器工具集，包括 FBX 导入导出、曲线编辑器操作、动画序列链接等

## 使用场景

- 你需要通过 Python 脚本批量导出 Sequencer 中的动画数据到 FBX 文件 → 使用 `ExportLevelSequenceFBX`
- 你需要在自动化流程中将 LevelSequence 的骨骼动画烘焙为 AnimSequence → 使用 `ExportAnimSequence`
- 你需要通过蓝图控制 Sequencer 曲线编辑器（选择关键帧、自定义颜色等） → 使用 `USequencerCurveEditorObject`
- 你需要在 Sequencer 事件轨道中通过脚本快速创建蓝图事件绑定 → 使用 `CreateQuickBinding` + `CreateEvent`
- 你需要将 FBX 文件批量导入到 ControlRig 轨道 → 使用 `ImportFBXToControlRig`
- 你需要在 Python 中将 LevelSequence 与 AnimSequence 建立双向链接 → 使用 `LinkAnimSequence` / `GetLevelSequenceLinkFromAnimSequence`

## 蓝图用法

### FBX 导入导出

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Export Level Sequence FBX` | 将指定绑定和轨道导出为 FBX 文件 | `USequencerToolsFunctionLibrary` |
| `Import Level Sequence FBX` | 从 FBX 文件导入动画数据到指定绑定 | `USequencerToolsFunctionLibrary` |
| `Import FBX To Control Rig` | 将 FBX 导入到 ControlRig 轨道 | `USequencerToolsFunctionLibrary` |
| `Export FBX From Control Rig` | 从 ControlRig 轨道导出 FBX | `USequencerToolsFunctionLibrary` |

### 动画序列链接

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Export Anim Sequence` | 将绑定中的骨骼动画烘焙为 AnimSequence | `USequencerToolsFunctionLibrary` |
| `Export Anim Sequence Wait For Delegate` | 等待委托返回 true 后再导出（用于异步场景） | `USequencerToolsFunctionLibrary` |
| `Link Anim Sequence` | 将 LevelSequence 的骨骼绑定链接到已有 AnimSequence | `USequencerToolsFunctionLibrary` |
| `Clear Linked Anim Sequences` | 清除 LevelSequence 的所有 AnimSequence 链接 | `USequencerToolsFunctionLibrary` |
| `Get Level Sequence Link From Anim Sequence` | 从 AnimSequence 获取关联的 LevelSequence 链接 | `USequencerToolsFunctionLibrary` |
| `Get Anim Sequence Link From Level Sequence` | 从 LevelSequence 获取关联的 AnimSequence 链接 | `USequencerToolsFunctionLibrary` |

### 事件快速绑定

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Quick Binding` | 为 Actor 成员方法创建事件快速绑定端点 | `USequencerToolsFunctionLibrary` |
| `Create Event` | 从端点和负载创建 MovieSceneEvent | `USequencerToolsFunctionLibrary` |
| `Is Event Endpoint Valid` | 检查端点是否有效 | `USequencerToolsFunctionLibrary` |

### 曲线编辑器

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Curve Editor` | 打开 Sequencer 曲线编辑器 | `USequencerCurveEditorObject` |
| `Close Curve Editor` | 关闭 Sequencer 曲线编辑器 | `USequencerCurveEditorObject` |
| `Is Curve Editor Open` | 曲线编辑器是否已打开 | `USequencerCurveEditorObject` |
| `Apply Filter` | 对曲线编辑器应用滤镜 | `USequencerCurveEditorObject` |
| `Get Channels With Selected Keys` | 获取包含选中关键帧的通道列表 | `USequencerCurveEditorObject` |
| `Get Selected Keys` | 获取指定通道中的选中关键帧索引 | `USequencerCurveEditorObject` |
| `Select Keys` | 选择指定通道中的关键帧 | `USequencerCurveEditorObject` |
| `Empty Selection` | 清空当前选择 | `USequencerCurveEditorObject` |
| `Show Curve` | 显示/隐藏指定曲线 | `USequencerCurveEditorObject` |
| `Is Curve Shown` | 曲线是否正在显示 | `USequencerCurveEditorObject` |

### 曲线颜色管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Has Custom Color For Channel` | 指定通道是否有自定义颜色 | `USequencerCurveEditorObject` |
| `Get Custom Color For Channel` | 获取通道自定义颜色（无则返回白色） | `USequencerCurveEditorObject` |
| `Set Custom Color For Channel` | 设置通道自定义颜色（存储在编辑器用户偏好中） | `USequencerCurveEditorObject` |
| `Set Random Color For Channels` | 为多个通道设置随机颜色 | `USequencerCurveEditorObject` |
| `Delete Color For Channels` | 删除通道自定义颜色 | `USequencerCurveEditorObject` |

### 使用示例（蓝图描述）

**导出 FBX 动画**：
1. 创建 `FSequencerExportFBXParams` 结构体，填入 World、Sequence、Bindings、Tracks、FBX 文件路径
2. 调用 `Export Level Sequence FBX` 节点，传入参数结构体
3. 检查返回值判断是否导出成功

**曲线编辑器操作流程**：
1. 获取 `USequencerCurveEditorObject` 实例
2. 调用 `Open Curve Editor` 打开编辑器
3. 调用 `Get Channels With Selected Keys` 获取已选中关键帧的通道
4. 对选中通道调用 `Set Custom Color For Channel` 设置高亮颜色

**创建事件快速绑定**：
1. 调用 `Create Quick Binding`，传入 Sequence、目标 Object、函数名（如 `"Set Actor Scale 3D"`）
2. 获取返回的 `FSequencerQuickBindingResult`
3. 调用 `Create Event` 将端点和负载字符串组合为 `FMovieSceneEvent`
4. 将事件添加到 Sequencer 事件轨道的通道中

## C++ 用法

### 头文件引入

```cpp
#include "SequencerTools.h"              // USequencerToolsFunctionLibrary
#include "SequencerCurveEditorObject.h"  // USequencerCurveEditorObject
```

### 基本用法 — FBX 导出

```cpp
// 来源: Public/SequencerTools.h
#include "SequencerTools.h"
#include "LevelSequence.h"

// 构建 FBX 导出参数
FSequencerExportFBXParams ExportParams;
ExportParams.World = GetWorld();
ExportParams.Sequence = MyLevelSequence;
ExportParams.RootSequence = MyLevelSequence;
ExportParams.Bindings = MyBindings;  // TArray<FMovieSceneBindingProxy>
ExportParams.Tracks = MyTracks;      // TArray<UMovieSceneTrack*>
ExportParams.FBXFileName = TEXT("/Game/ExportedAnim.fbx");

// 执行导出
bool bSuccess = USequencerToolsFunctionLibrary::ExportLevelSequenceFBX(ExportParams);
```

### 基本用法 — 事件快速绑定

```cpp
// 来源: Public/SequencerTools.h
#include "SequencerTools.h"

// 为 Actor 的成员函数创建快速绑定
FSequencerQuickBindingResult Result = USequencerToolsFunctionLibrary::CreateQuickBinding(
    MySequence,         // UMovieSceneSequence*
    MyActor,            // UObject*
    TEXT("Set Actor Scale 3D"),
    false               // bCallInEditor
);

if (USequencerToolsFunctionLibrary::IsEventEndpointValid(Result))
{
    // 创建事件，传入负载参数
    TArray<FString> Payload = { TEXT("1.0,1.0,1.0") };
    FMovieSceneEvent Event = USequencerToolsFunctionLibrary::CreateEvent(
        MySequence, MyEventSection, Result, Payload
    );
}
```

### 进阶用法 — 曲线编辑器操作

```cpp
// 来源: Public/SequencerCurveEditorObject.h
#include "SequencerCurveEditorObject.h"

// 创建曲线编辑器对象并关联 Sequencer
USequencerCurveEditorObject* CurveEditorObj = NewObject<USequencerCurveEditorObject>();
CurveEditorObj->SetSequencer(MySequencer);

// 打开曲线编辑器
CurveEditorObj->OpenCurveEditor();

// 获取包含选中关键帧的通道
TArray<FSequencerChannelProxy> Channels = CurveEditorObj->GetChannelsWithSelectedKeys();

for (const FSequencerChannelProxy& Channel : Channels)
{
    // 显示该通道的曲线
    CurveEditorObj->ShowCurve(Channel, true);
    
    // 获取选中的关键帧索引
    TArray<int32> SelectedKeys = CurveEditorObj->GetSelectedKeys(Channel);
    
    // 设置自定义颜色
    CurveEditorObj->SetCustomColorForChannel(
        Channel.Section->GetClass(),
        Channel.ChannelName.ToString(),
        FLinearColor::Red
    );
}
```

### 进阶用法 — AnimSequence 链接管理

```cpp
// 来源: Public/SequencerTools.h
#include "SequencerTools.h"

// 将 LevelSequence 的骨骼动画烘焙到 AnimSequence 并建立链接
bool bExported = USequencerToolsFunctionLibrary::ExportAnimSequence(
    GetWorld(),
    MyLevelSequence,
    MyAnimSequence,      // UAnimSequence*
    ExportOptions,        // UAnimSeqExportOption*
    BindingProxy,         // FMovieSceneBindingProxy
    true                  // bCreateLink
);

// 查询链接关系
UAnimSequenceLevelSequenceLink* AnimLink = 
    USequencerToolsFunctionLibrary::GetLevelSequenceLinkFromAnimSequence(MyAnimSequence);

ULevelSequenceAnimSequenceLink* SeqLink = 
    USequencerToolsFunctionLibrary::GetAnimSequenceLinkFromLevelSequence(MyLevelSequence);
```

## Demo 示例

### 完整的 FBX 导出与曲线编辑器示例

```cpp
// SequencerScriptingDemo.h
#pragma once

#include "CoreMinimal.h"
#include "SequencerTools.h"
#include "SequencerCurveEditorObject.h"
#include "LevelSequence.h"

class FSequencerScriptingDemo
{
public:
    /** 导出 LevelSequence 中指定绑定的动画到 FBX */
    static bool ExportSequenceToFBX(UWorld* World, ULevelSequence* Sequence, 
                                     const FString& OutputPath);

    /** 为 LevelSequence 创建动画事件快速绑定 */
    static FSequencerQuickBindingResult CreateAnimEventBinding(
        UMovieSceneSequence* Sequence, UObject* TargetActor, const FString& FunctionName);

    /** 打开曲线编辑器并为选中通道设置高亮颜色 */
    static void HighlightSelectedCurves(USequencerCurveEditorObject* CurveEditorObj, 
                                         const FLinearColor& Color);
};
```

```cpp
// SequencerScriptingDemo.cpp
#include "SequencerScriptingDemo.h"

bool FSequencerScriptingDemo::ExportSequenceToFBX(
    UWorld* World, ULevelSequence* Sequence, const FString& OutputPath)
{
    if (!World || !Sequence)
    {
        return false;
    }

    // 构建导出参数
    FSequencerExportFBXParams Params;
    Params.World = World;
    Params.Sequence = Sequence;
    Params.RootSequence = Sequence;
    Params.FBXFileName = OutputPath;

    // 获取序列中所有绑定
    UMovieScene* MovieScene = Sequence->GetMovieScene();
    if (MovieScene)
    {
        for (const FMovieSceneBinding& Binding : MovieScene->GetBindings())
        {
            Params.Bindings.Add(FMovieSceneBindingProxy(Binding.GetGuid(), Sequence));
        }
    }

    return USequencerToolsFunctionLibrary::ExportLevelSequenceFBX(Params);
}

FSequencerQuickBindingResult FSequencerScriptingDemo::CreateAnimEventBinding(
    UMovieSceneSequence* Sequence, UObject* TargetActor, const FString& FunctionName)
{
    return USequencerToolsFunctionLibrary::CreateQuickBinding(
        Sequence, TargetActor, FunctionName, false);
}

void FSequencerScriptingDemo::HighlightSelectedCurves(
    USequencerCurveEditorObject* CurveEditorObj, const FLinearColor& Color)
{
    if (!CurveEditorObj || !CurveEditorObj->IsCurveEditorOpen())
    {
        return;
    }

    TArray<FSequencerChannelProxy> Channels = CurveEditorObj->GetChannelsWithSelectedKeys();

    for (const FSequencerChannelProxy& Channel : Channels)
    {
        CurveEditorObj->SetCustomColorForChannel(
            Channel.Section->GetClass(),
            Channel.ChannelName.ToString(),
            Color
        );
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer 核心电影场景系统 |
| `LevelSequence` | 关卡序列资产和播放 |
| `MovieSceneTools` | Sequencer 编辑器工具集 |
| `MovieSceneCapture` | 影片渲染捕获（已废弃，迁移至 Movie Render Queue） |
| `ControlRig` | ControlRig 动画系统集成 |
| `FBX` | FBX 文件格式导入导出 |
| `AnimGraph` | 动画图表相关功能 |
| `BlueprintGraph` | 蓝图图表节点（用于事件快速绑定的 K2Node） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b209798d` | Anim In Engine: Add bRemoveExcludedCurves option to animation recording so we can remove curves alre | 动画录制新增排除曲线选项 |
| 2026-04-24 | `8b8110b4` | [EDA] Add Sequencer tool wrappers + fix sequencer toolset tests | 新增 Sequencer 工具包装器并修复测试 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至 UE_LOGF |
| 2026-04-10 | `77af3950` | [EDA] Add SequencerTools toolset with Anim Mixer split into separate plugin | 新增 SequencerTools 工具集，动画混合器拆分为独立插件 |
| 2026-04-10 | `8bd8f719` | [Backout] - CL52569948 | 回退变更 CL52569948 |

### 维护评价

- **活跃维护中**：最近一次更新距今约 5 个月（2026-05），且 2026 年 4 月有密集的功能性更新
- 虽然 `.uplugin` 标记为 `IsBetaVersion: true`，但该插件自 2018 年创建至今持续更新超过 8 年，功能已相当成熟
- 近期更新集中在 Sequencer 工具集扩展（EDA 项目）、动画录制增强、以及代码现代化
- ⚠️ 注意：部分旧 API（`RenderMovie`、`IsRenderingMovie`、`CancelMovieRender`、`GetBoundObjects`、`GetObjectBindings`）已在 UE 5.3 中标记为废弃，建议使用 Movie Render Queue 和 `ULevelSequenceEditorBlueprintLibrary` 替代
- **推荐使用**：对于需要脚本化 Sequencer 工作流（特别是 FBX 导入导出、动画序列链接、事件绑定）的项目，此插件是官方推荐方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting/Tests)