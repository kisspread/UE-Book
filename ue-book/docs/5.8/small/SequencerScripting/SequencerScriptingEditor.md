# Sequencer Scripting

> Python and editor utility scripting extensions for sequencer and movie scenes

| 属性 | 值 |
|---|---|
| 中文名 | Sequencer 脚本扩展 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SequencerScripting` (Runtime), `SequencerScriptingEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-05-09 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting) | |

## 用途

SequencerScripting 是 Sequencer 与 Python 脚本之间的桥梁插件。Sequencer 自身的 C++ API 体系庞大且复杂，不适合直接暴露给 Python 或蓝图编辑器工具脚本。本插件通过包装层（Wrapper UObjects）将 Sequencer 核心功能简化为易于使用的蓝图/Python API。

该插件解决的核心问题：
- **Python 自动化 Sequencer 工作流**：用 Python 脚本批量创建、修改、导出关卡序列（Level Sequence），替代手动操作
- **FBX 导入/导出管线集成**：在 Python 脚本或蓝图中实现 FBX 动画数据与 Sequencer 的双向转换
- **动画序列链接管理**：管理 Level Sequence 与 AnimSequence 之间的绑定关系，支持烘焙和链接
- **曲线编辑器脚本化控制**：通过 Python/蓝图操作 Sequencer 曲线编辑器的选择、颜色、显示状态等
- **事件轨道快速绑定**：脚本化创建 Sequencer 事件轨道的事件端点和 payload

## 使用场景

- 你的动画管线需要批量将多个 Level Sequence 导出为 FBX 文件 → 使用 `ExportLevelSequenceFBX`
- 你需要将 Sequencer 中的动画烘焙到 AnimSequence 并建立关联 → 使用 `ExportAnimSequence` + `LinkAnimSequence`
- 你想用 Python 脚本遍历 Sequencer 中所有绑定的对象 → 使用 `GetBoundObjects`
- 你需要通过脚本向 Control Rig 轨道导入 FBX 动画数据 → 使用 `ImportFBXToControlRig`
- 你想编程方式操作 Sequencer 曲线编辑器（选键、改颜色、筛选曲线）→ 使用 `USequencerCurveEditorObject`
- 你需要脚本化创建 Sequencer 事件轨道上的事件和快速绑定 → 使用 `CreateEvent` + `CreateQuickBinding`

## 蓝图用法

本插件的核心 API 分布在两个主要类中：`USequencerToolsFunctionLibrary`（全局工具函数）和 `USequencerCurveEditorObject`（曲线编辑器操作）。

### 核心节点 — Sequencer 工具

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Export Level Sequence FBX` | 将指定绑定和轨道导出为 FBX 文件 | `USequencerToolsFunctionLibrary` |
| `Import Level Sequence FBX` | 从 FBX 文件导入动画数据到指定绑定 | `USequencerToolsFunctionLibrary` |
| `Import FBX To Control Rig` | 向 Control Rig 轨道导入 FBX 数据 | `USequencerToolsFunctionLibrary` |
| `Export FBX From Control Rig` | 从 Control Rig 轨道导出 FBX | `USequencerToolsFunctionLibrary` |
| `Export Anim Sequence` | 将 Sequencer 动画烘焙导出为 AnimSequence | `USequencerToolsFunctionLibrary` |
| `Export Anim Sequence Wait For Delegate` | 等待委托返回后再导出动画序列（支持动态 Spawnable） | `USequencerToolsFunctionLibrary` |
| `Link Anim Sequence` | 建立 Level Sequence 与 AnimSequence 的链接 | `USequencerToolsFunctionLibrary` |
| `Clear Linked Anim Sequences` | 清除 Level Sequence 的所有动画序列链接 | `USequencerToolsFunctionLibrary` |
| `Get Level Sequence Link From Anim Sequence` | 从 AnimSequence 获取关联的 Level Sequence 链接 | `USequencerToolsFunctionLibrary` |
| `Get Anim Sequence Link From Level Sequence` | 从 Level Sequence 获取关联的 AnimSequence 链接 | `USequencerToolsFunctionLibrary` |
| `Create Quick Binding` | 创建事件轨道的快速绑定（Actor 方法绑定） | `USequencerToolsFunctionLibrary` |
| `Create Event` | 从端点和 payload 创建电影场景事件 | `USequencerToolsFunctionLibrary` |
| `Is Event Endpoint Valid` | 检查事件端点是否有效 | `USequencerToolsFunctionLibrary` |

### 核心节点 — 曲线编辑器

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Curve Editor` | 打开曲线编辑器窗口 | `USequencerCurveEditorObject` |
| `Close Curve Editor` | 关闭曲线编辑器窗口 | `USequencerCurveEditorObject` |
| `Is Curve Editor Open` | 检查曲线编辑器是否已打开 | `USequencerCurveEditorObject` |
| `Apply Filter` | 对曲线编辑器应用筛选器 | `USequencerCurveEditorObject` |
| `Get Channels With Selected Keys` | 获取当前有选中关键帧的通道 | `USequencerCurveEditorObject` |
| `Get Selected Keys` | 获取指定通道中的选中关键帧索引 | `USequencerCurveEditorObject` |
| `Select Keys` | 选择指定通道的指定关键帧 | `USequencerCurveEditorObject` |
| `Empty Selection` | 清空当前所有选择 | `USequencerCurveEditorObject` |
| `Show Curve` | 显示或隐藏指定曲线 | `USequencerCurveEditorObject` |
| `Is Curve Shown` | 检查指定曲线是否可见 | `USequencerCurveEditorObject` |
| `Set Custom Color For Channel` | 为指定通道设置自定义颜色 | `USequencerCurveEditorObject` |
| `Set Random Color For Channels` | 为多个通道设置随机颜色 | `USequencerCurveEditorObject` |

### 蓝图使用示例 — FBX 导出

1. 获取目标 `ULevelSequence` 引用
2. 创建 `FSequencerExportFBXParams` 结构体
3. 设置 `World`、`Sequence`、`Bindings`（通过 `FMovieSceneBindingProxy` 指定绑定）、`Tracks`、`FBXFileName`
4. 调用 `Export Level Sequence FBX` 节点
5. 检查返回的布尔值确认导出是否成功

### 蓝图使用示例 — 曲线编辑器

1. 从 `ULevelSequenceBlueprintLibrary` 获取曲线编辑器对象
2. 调用 `Open Curve Editor` 打开
3. 使用 `Get Channels With Selected Keys` 获取当前选中通道
4. 使用 `Get Selected Keys` 获取具体选中的关键帧索引
5. 通过 `Set Custom Color For Channel` 自定义曲线颜色

## C++ 用法

### 头文件引入

```cpp
#include "SequencerTools.h"
#include "SequencerCurveEditorObject.h"
```

### 基本用法 — FBX 导出

从 `SequencerTools.h` 中的 API 使用：

```cpp
// 来源: Public/SequencerTools.h - ExportLevelSequenceFBX
#include "SequencerTools.h"
#include "LevelSequence.h"
#include "MovieSceneBindingProxy.h"

// 构造导出参数
FSequencerExportFBXParams ExportParams;
ExportParams.World = GetWorld();
ExportParams.Sequence = MyLevelSequence;
ExportParams.Bindings = TargetBindings;  // TArray<FMovieSceneBindingProxy>
ExportParams.FBXFileName = TEXT("/Game/ExportedAnimation.fbx");

// 执行导出
bool bSuccess = USequencerToolsFunctionLibrary::ExportLevelSequenceFBX(ExportParams);
```

### 基本用法 — 动画序列导出与链接

```cpp
// 来源: Public/SequencerTools.h - ExportAnimSequence + LinkAnimSequence
#include "SequencerTools.h"

// 导出动画序列
bool bExported = USequencerToolsFunctionLibrary::ExportAnimSequence(
    GetWorld(),
    MyLevelSequence,
    MyAnimSequence,
    ExportOptions,
    BindingProxy,
    true  // bCreateLink - 建立 LevelSequence 与 AnimSequence 的关联
);

// 单独建立链接
bool bLinked = USequencerToolsFunctionLibrary::LinkAnimSequence(
    MyLevelSequence,
    MyAnimSequence,
    ExportOptions,
    BindingProxy
);

// 获取关联信息
UAnimSequenceLevelSequenceLink* Link = 
    USequencerToolsFunctionLibrary::GetLevelSequenceLinkFromAnimSequence(MyAnimSequence);
```

### 基本用法 — 曲线编辑器

```cpp
// 来源: Public/SequencerCurveEditorObject.h
#include "SequencerCurveEditorObject.h"

// 创建曲线编辑器对象
USequencerCurveEditorObject* CurveEditorObj = NewObject<USequencerCurveEditorObject>();
CurveEditorObj->SetSequencer(SequencerPtr);

// 打开曲线编辑器
CurveEditorObj->OpenCurveEditor();

// 获取有选中关键帧的通道
TArray<FSequencerChannelProxy> SelectedChannels = CurveEditorObj->GetChannelsWithSelectedKeys();

for (const FSequencerChannelProxy& Channel : SelectedChannels)
{
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

### 进阶用法 — 事件轨道快速绑定

```cpp
// 来源: Public/SequencerTools.h - CreateQuickBinding + CreateEvent
#include "SequencerTools.h"

// 1. 创建快速绑定（绑定到 Actor 的方法）
FSequencerQuickBindingResult QuickBinding = USequencerToolsFunctionLibrary::CreateQuickBinding(
    MySequence,       // UMovieSceneSequence*
    TargetActor,      // UObject* - 绑定目标
    TEXT("Set Actor Scale 3D"),  // 函数名（蓝图编辑器中显示的名称）
    false             // bCallInEditor
);

// 2. 验证端点
if (USequencerToolsFunctionLibrary::IsEventEndpointValid(QuickBinding))
{
    // 3. 构造 payload
    TArray<FString> Payload = { TEXT("(X=2.0,Y=2.0,Z=2.0)") };
    
    // 4. 创建事件并添加到 section
    FMovieSceneEvent NewEvent = USequencerToolsFunctionLibrary::CreateEvent(
        MySequence,
        EventSection,
        QuickBinding,
        Payload
    );
}
```

### 进阶用法 — Control Rig FBX 导入导出

```cpp
// 来源: Public/SequencerTools.h - ImportFBXToControlRig + ExportFBXFromControlRig
#include "SequencerTools.h"

// 向 Control Rig 导入 FBX
TArray<FString> SelectedControls = { TEXT("LeftArm"), TEXT("RightArm") };
bool bImported = USequencerToolsFunctionLibrary::ImportFBXToControlRig(
    GetWorld(),
    MyLevelSequence,
    TEXT("MyActorWithControlRig"),
    SelectedControls,
    ImportSettings,  // UMovieSceneUserImportFBXControlRigSettings*
    TEXT("/Game/Animation.fbx")
);

// 从 Control Rig 导出 FBX
bool bExported = USequencerToolsFunctionLibrary::ExportFBXFromControlRig(
    MyLevelSequence,
    TEXT("MyActorWithControlRig"),
    ExportSettings   // UMovieSceneUserExportFBXControlRigSettings*
);
```

## Demo 示例

```cpp
// MySequencerAutomation.h
#pragma once

#include "CoreMinimal.h"

class FMySequencerAutomation
{
public:
    /** 遍历 Level Sequence 中的所有绑定并打印信息 */
    static void DumpSequenceBindings(ULevelSequence* Sequence, UWorld* World);
    
    /** 批量导出序列到 FBX */
    static bool BatchExportToFBX(ULevelSequence* Sequence, const FString& OutputPath);
};
```

```cpp
// MySequencerAutomation.cpp
#include "MySequencerAutomation.h"
#include "SequencerTools.h"
#include "LevelSequence.h"
#include "MovieScene.h"
#include "MovieSceneBindingProxy.h"

void FMySequencerAutomation::DumpSequenceBindings(ULevelSequence* Sequence, UWorld* World)
{
    if (!Sequence || !World) return;
    
    UMovieScene* MovieScene = Sequence->GetMovieScene();
    if (!MovieScene) return;
    
    // 获取所有拥有绑定的对象
    TArray<FMovieSceneBinding> Bindings = MovieScene->GetBindings();
    
    // 使用 SequencerTools 获取绑定的对象实例
    TArray<FMovieSceneBindingProxy> BindingProxies;
    for (const auto& Binding : Bindings)
    {
        BindingProxies.Add(FMovieSceneBindingProxy(Binding.GetObjectGuid(), Sequence));
    }
    
    FSequencerScriptingRange Range;
    Range.Value = MovieScene->GetPlaybackRange().GetLowerBoundValue();
    
    TArray<FSequencerBoundObjects> BoundObjects = 
        USequencerToolsFunctionLibrary::GetBoundObjects(World, Sequence, BindingProxies, Range);
    
    for (const auto& Entry : BoundObjects)
    {
        UE_LOG(LogTemp, Log, TEXT("Binding: %s"), *Entry.BindingProxy.GetGuid().ToString());
        for (const auto& Obj : Entry.BoundObjects)
        {
            if (Obj)
            {
                UE_LOG(LogTemp, Log, TEXT("  -> Object: %s"), *Obj->GetName());
            }
        }
    }
}

bool FMySequencerAutomation::BatchExportToFBX(ULevelSequence* Sequence, const FString& OutputPath)
{
    if (!Sequence) return false;
    
    UMovieScene* MovieScene = Sequence->GetMovieScene();
    if (!MovieScene) return false;
    
    // 收集所有绑定
    TArray<FMovieSceneBindingProxy> AllBindings;
    for (const auto& Binding : MovieScene->GetBindings())
    {
        AllBindings.Add(FMovieSceneBindingProxy(Binding.GetObjectGuid(), Sequence));
    }
    
    // 收集所有轨道
    TArray<UMovieSceneTrack*> AllTracks;
    for (const auto& Binding : MovieScene->GetBindings())
    {
        for (UMovieSceneTrack* Track : Binding.GetTracks())
        {
            AllTracks.Add(Track);
        }
    }
    
    FSequencerExportFBXParams Params;
    Params.Sequence = Sequence;
    Params.Bindings = AllBindings;
    Params.Tracks = AllTracks;
    Params.FBXFileName = OutputPath;
    
    return USequencerToolsFunctionLibrary::ExportLevelSequenceFBX(Params);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LevelSequence` | Level Sequence 资产类型和核心数据结构 |
| `MovieScene` | 电影场景基础框架，提供绑定、轨道、通道等核心类型 |
| `MovieSceneTools` | 电影场景编辑器工具支持 |
| `ControlRig` | Control Rig 集成（FBX 导入导出到 Control Rig） |
| `FbxExport` / `FbxImport` | FBX 文件读写支持 |
| `SequencerCore` | Sequencer 核心接口（ISequencer 等） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b209798d` | Anim In Engine: Add bRemoveExcludedCurves option to animation recording so we can remove curves alre | 为动画录制添加移除排除曲线选项 |
| 2026-04-24 | `8b8110b4` | [EDA] Add Sequencer tool wrappers + fix sequencer toolset tests | 添加 Sequencer 工具封装并修复工具集测试 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新格式 UE_LOGF |
| 2026-04-10 | `77af3950` | [EDA] Add SequencerTools toolset with Anim Mixer split into separate plugin | 添加 SequencerTools 工具集，Anim Mixer 拆分为独立插件 |
| 2026-04-10 | `8bd8f719` | [Backout] - CL52569948 | 回退一次变更提交 |

### 维护评价

- **创建时间**：2018 年 5 月，已持续维护约 8 年
- **近期活跃度**：非常活跃，2026 年 4-5 月有多次功能性和工具集重构提交
- **维护状态**：**活跃维护中** — Epic 持续在更新 Sequencer 工具封装和测试
- **已知限制**：
  - `.uplugin` 标记为 `IsBetaVersion: true`，API 可能有变化
  - 多个旧 API 已标记为 `Deprecated`（如 `RenderMovie`、`GetBoundObjects`、`GetObjectBindings`），官方建议迁移到 Movie Render Queue 和 `ULevelSequenceEditorBlueprintLibrary`
  - 需要手动启用插件
- **推荐使用**：✅ 推荐 — 作为 Sequencer Python/蓝图自动化的核心插件，是目前唯一的选择，Epic 持续投入维护。注意避开已废弃的 API。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequencerScripting)
- [官方文档]() （暂无链接）