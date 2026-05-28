# Level Sequence Editor

> Content Editor for LevelSequence Assets.

| 属性 | 值 |
|---|---|
| 中文名 | 关卡序列编辑器 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `LevelSequenceEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2015-09-29 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/LevelSequenceEditor) | |

## 用途

LevelSequenceEditor 是 UE5 Sequencer 编辑器的核心实现插件，为关卡序列（Level Sequence）资产提供完整的编辑器界面和交互功能。它解决了以下问题：

- **序列资产编辑界面**：提供 Sequencer 面板，用于在编辑器中可视化编辑关卡序列（动画、过场、摄像机等）
- **播放控制**：在编辑器内对序列进行播放、暂停、跳转、变速等操作
- **对象绑定管理**：管理序列与场景中 Actor 的 Possessable/Spawnable 绑定关系
- **选择与编辑操作**：支持对轨道、片段、通道、关键帧、文件夹、绑定的选择、复制、粘贴
- **影视视口**：提供带胶片叠加层（安全框、十字线等）的专用影视视口
- **绑定类型转换**：在 Possessable、Spawnable 和自定义绑定之间转换
- **烘焙与时间码同步**：变换烘焙、基于源时间码对齐片段

简单来说，如果没有这个插件，你将无法在编辑器中打开和编辑任何 Level Sequence 资产。它是 Sequencer 面板、影视视口、以及蓝图控制序列编辑器的底层实现。

## 使用场景

- 你在制作过场动画或电影 → 打开 Level Sequence 资产，使用 Sequencer 面板编辑
- 你需要在蓝图中控制 Sequencer 的播放、跳帧 → 使用 `ULevelSequenceEditorBlueprintLibrary`
- 你需要批量管理序列中的 Actor 绑定（添加/替换/移除） → 使用 `ULevelSequenceEditorSubsystem`
- 你需要在影视视口中添加安全框、三分线等构图辅助 → 使用 Film Overlay 系统
- 你需要自定义序列编辑器的 UI 行为 → 实现 `ISequencerCustomization` 并通过模块接口注册

## 蓝图用法

此插件提供两个主要的蓝图功能库：`ULevelSequenceEditorBlueprintLibrary`（静态函数库）和 `ULevelSequenceEditorSubsystem`（编辑器子系统）。

### 核心节点 — 播放控制（LevelSequenceEditorBlueprintLibrary）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OpenLevelSequence` | 打开一个关卡序列资产进行编辑 | `ULevelSequenceEditorBlueprintLibrary` |
| `CloseLevelSequence` | 关闭当前打开的关卡序列 | `ULevelSequenceEditorBlueprintLibrary` |
| `GetCurrentLevelSequence` | 获取当前打开的根序列 | `ULevelSequenceEditorBlueprintLibrary` |
| `GetFocusedLevelSequence` | 获取当前聚焦的序列（子序列层级中） | `ULevelSequenceEditorBlueprintLibrary` |
| `FocusLevelSequence` | 聚焦到指定子序列片段 | `ULevelSequenceEditorBlueprintLibrary` |
| `FocusParentSequence` | 返回上一级父序列 | `ULevelSequenceEditorBlueprintLibrary` |
| `Play` | 播放当前序列 | `ULevelSequenceEditorBlueprintLibrary` |
| `Pause` | 暂停当前序列 | `ULevelSequenceEditorBlueprintLibrary` |
| `PlayTo` | 从当前位置播放到指定时间 | `ULevelSequenceEditorBlueprintLibrary` |
| `SetCurrentTime` | 设置全局播放头位置（支持帧/秒） | `ULevelSequenceEditorBlueprintLibrary` |
| `GetCurrentTime` | 获取全局播放头位置 | `ULevelSequenceEditorBlueprintLibrary` |
| `SetCurrentLocalTime` | 设置本地播放头位置（子序列内） | `ULevelSequenceEditorBlueprintLibrary` |
| `GetCurrentLocalTime` | 获取本地播放头位置 | `ULevelSequenceEditorBlueprintLibrary` |
| `SetPlaybackSpeed` | 设置播放速度 | `ULevelSequenceEditorBlueprintLibrary` |
| `GetPlaybackSpeed` | 获取播放速度 | `ULevelSequenceEditorBlueprintLibrary` |
| `SetLoopMode` | 设置循环模式 | `ULevelSequenceEditorBlueprintLibrary` |
| `IsPlaying` | 检查是否正在播放 | `ULevelSequenceEditorBlueprintLibrary` |

### 核心节点 — 选择操作（LevelSequenceEditorBlueprintLibrary）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSelectedTracks` | 获取当前选中的轨道 | `ULevelSequenceEditorBlueprintLibrary` |
| `GetSelectedSections` | 获取当前选中的片段 | `ULevelSequenceEditorBlueprintLibrary` |
| `GetSelectedChannels` | 获取当前选中的通道 | `ULevelSequenceEditorBlueprintLibrary` |
| `GetSelectedKeys` | 获取指定通道中选中的关键帧索引 | `ULevelSequenceEditorBlueprintLibrary` |
| `GetSelectedFolders` | 获取当前选中的文件夹 | `ULevelSequenceEditorBlueprintLibrary` |
| `GetSelectedBindings` | 获取当前选中的绑定 | `ULevelSequenceEditorBlueprintLibrary` |
| `SelectTracks` | 选中指定轨道 | `ULevelSequenceEditorBlueprintLibrary` |
| `SelectSections` | 选中指定片段 | `ULevelSequenceEditorBlueprintLibrary` |
| `SelectChannels` | 选中指定通道 | `ULevelSequenceEditorBlueprintLibrary` |
| `SelectKeys` | 选中指定关键帧 | `ULevelSequenceEditorBlueprintLibrary` |
| `SelectFolders` | 选中指定文件夹 | `ULevelSequenceEditorBlueprintLibrary` |
| `SelectBindings` | 选中指定绑定 | `ULevelSequenceEditorBlueprintLibrary` |
| `EmptySelection` | 清空选择 | `ULevelSequenceEditorBlueprintLibrary` |

### 核心节点 — 绑定与 Actor 管理（LevelSequenceEditorSubsystem）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddActors` | 将 Actor 添加到 Sequencer（自动创建轨道） | `ULevelSequenceEditorSubsystem` |
| `AddSpawnableFromInstance` | 基于实例添加 Spawnable 绑定 | `ULevelSequenceEditorSubsystem` |
| `AddSpawnableFromClass` | 基于类添加 Spawnable 绑定 | `ULevelSequenceEditorSubsystem` |
| `CreateCamera` | 创建 Cine Camera 并添加到 Sequencer | `ULevelSequenceEditorSubsystem` |
| `ConvertToSpawnable` | 将 Possessable 转换为 Spawnable | `ULevelSequenceEditorSubsystem` |
| `ConvertToPossessable` | 将 Spawnable 转换为 Possessable | `ULevelSequenceEditorSubsystem` |
| `ConvertToCustomBinding` | 转换为自定义绑定类型 | `ULevelSequenceEditorSubsystem` |
| `AddActorsToBinding` | 将 Actor 分配到已有绑定 | `ULevelSequenceEditorSubsystem` |
| `ReplaceBindingWithActors` | 用新 Actor 替换绑定 | `ULevelSequenceEditorSubsystem` |
| `RemoveActorsFromBinding` | 从绑定中移除 Actor | `ULevelSequenceEditorSubsystem` |
| `RemoveAllBindings` | 移除绑定中的所有对象 | `ULevelSequenceEditorSubsystem` |

### 核心节点 — 复制粘贴与工具（LevelSequenceEditorSubsystem）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CopyFolders` | 复制文件夹（含内部对象和轨道） | `ULevelSequenceEditorSubsystem` |
| `PasteFolders` | 粘贴文件夹 | `ULevelSequenceEditorSubsystem` |
| `CopySections` | 复制片段 | `ULevelSequenceEditorSubsystem` |
| `PasteSections` | 粘贴片段 | `ULevelSequenceEditorSubsystem` |
| `CopyTracks` | 复制轨道 | `ULevelSequenceEditorSubsystem` |
| `PasteTracks` | 粘贴轨道 | `ULevelSequenceEditorSubsystem` |
| `CopyBindings` | 复制绑定 | `ULevelSequenceEditorSubsystem` |
| `PasteBindings` | 粘贴绑定 | `ULevelSequenceEditorSubsystem` |
| `BakeTransformWithSettings` | 烘焙变换 | `ULevelSequenceEditorSubsystem` |
| `FixActorReferences` | 自动修复断开的 Actor 引用 | `ULevelSequenceEditorSubsystem` |
| `SnapSectionsToTimelineUsingSourceTimecode` | 基于源时间码对齐片段到时间线 | `ULevelSequenceEditorSubsystem` |

### 核心节点 — 事件委托（LevelSequenceEditorSubsystem）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OnGlobalTimeChanged` | 全局时间变化时触发 | `ULevelSequenceEditorSubsystem` |
| `OnPlayEvent` | 开始播放时触发 | `ULevelSequenceEditorSubsystem` |
| `OnStopEvent` | 停止播放时触发 | `ULevelSequenceEditorSubsystem` |
| `OnRecordEvent` | 切换录制状态时触发 | `ULevelSequenceEditorSubsystem` |
| `OnBeginScrubbingEvent` | 开始拖拽时间线时触发 | `ULevelSequenceEditorSubsystem` |
| `OnEndScrubbingEvent` | 结束拖拽时间线时触发 | `ULevelSequenceEditorSubsystem` |

### 使用示例（蓝图描述）

**示例 1：打开序列并跳转到指定帧**

1. 从 `ULevelSequence` 资产引用节点出发，调用 `OpenLevelSequence` 打开序列
2. 创建 `FMovieSceneSequencePlaybackParams` 结构体，设置帧号
3. 调用 `SetCurrentTime`（`SetGlobalPosition`）跳转到目标帧
4. 调用 `Play` 开始播放

**示例 2：批量添加 Actor 到序列**

1. 获取 `ULevelSequenceEditorSubsystem`（通过 `GetEditorSubsystem` 节点）
2. 创建一个 Actor 数组，包含需要添加的 Actor
3. 调用 `AddActors`，返回绑定代理数组
4. 可选：调用 `ConvertToSpawnable` 将绑定转换为 Spawnable 类型

**示例 3：监听序列播放事件**

1. 获取 `ULevelSequenceEditorSubsystem` 子系统实例
2. 绑定 `OnPlayEvent` 和 `OnStopEvent` 委托到自定义事件
3. 在事件回调中执行所需逻辑（如 UI 更新、日志记录等）

## C++ 用法

### 头文件引入

```cpp
#include "LevelSequenceEditorBlueprintLibrary.h"
#include "LevelSequenceEditorSubsystem.h"
#include "LevelSequenceEditorModule.h"
```

### 基本用法 — 通过蓝图库控制序列

```cpp
#include "LevelSequenceEditorBlueprintLibrary.h"
#include "LevelSequence/LevelSequence.h"

// 打开一个关卡序列
ULevelSequence* MySequence = LoadObject<ULevelSequence>(nullptr, TEXT("/Game/MySequence"));
if (ULevelSequenceEditorBlueprintLibrary::OpenLevelSequence(MySequence))
{
    // 跳转到第 30 帧
    FMovieSceneSequencePlaybackParams Params;
    Params.Frame = FFrameTime(30);
    ULevelSequenceEditorBlueprintLibrary::SetGlobalPosition(Params);
    
    // 开始播放
    ULevelSequenceEditorBlueprintLibrary::Play();
}
```

### 基本用法 — 通过子系统管理绑定

```cpp
#include "LevelSequenceEditorSubsystem.h"

// 获取子系统
ULevelSequenceEditorSubsystem* Subsystem = GEditor->GetEditorSubsystem<ULevelSequenceEditorSubsystem>();
if (Subsystem)
{
    // 添加 Actor 到当前序列
    TArray<AActor*> Actors = { MyActor1, MyActor2 };
    TArray<FMovieSceneBindingProxy> Bindings = Subsystem->AddActors(Actors);
    
    // 将绑定转换为 Spawnable
    for (const FMovieSceneBindingProxy& Binding : Bindings)
    {
        Subsystem->ConvertToSpawnable(Binding);
    }
}
```

### 进阶用法 — 注册自定义 Sequencer 扩展

```cpp
#include "LevelSequenceEditorModule.h"

// 在模块 StartupModule 中注册自定义 Sequencer 扩展
void FMyModule::StartupModule()
{
    ILevelSequenceEditorModule& EditorModule = 
        FModuleManager::LoadModuleChecked<ILevelSequenceEditorModule>("LevelSequenceEditor");
    
    // 注册自定义 customization
    FGuid Handle = EditorModule.RegisterAdditionalLevelSequenceEditorCustomization(
        FOnGetSequencerCustomizationInstance::CreateLambda([]() -> TUniquePtr<ISequencerCustomization>
        {
            return MakeUnique<FMyCustomSequencerCustomization>();
        })
    );
    
    // 保存 Handle 以便在 ShutdownModule 中注销
    CustomizationHandle = Handle;
}

void FMyModule::ShutdownModule()
{
    ILevelSequenceEditorModule& EditorModule = 
        FModuleManager::GetModuleChecked<ILevelSequenceEditorModule>("LevelSequenceEditor");
    EditorModule.UnregisterAdditionalLevelSequenceEditorCustomization(CustomizationHandle);
}
```

### 进阶用法 — 监听播放事件

```cpp
#include "LevelSequenceEditorSubsystem.h"

void FMyClass::BindToSequencerEvents()
{
    ULevelSequenceEditorSubsystem* Subsystem = 
        GEditor->GetEditorSubsystem<ULevelSequenceEditorSubsystem>();
    
    if (Subsystem)
    {
        Subsystem->OnPlayEvent.AddDynamic(this, &FMyClass::OnSequencerPlay);
        Subsystem->OnStopEvent.AddDynamic(this, &FMyClass::OnSequencerStop);
        Subsystem->OnGlobalTimeChanged.AddDynamic(this, &FMyClass::OnTimeChanged);
    }
}

void FMyClass::OnSequencerPlay()
{
    UE_LOG(LogTemp, Log, TEXT("Sequencer started playing"));
}

void FMyClass::OnSequencerStop()
{
    UE_LOG(LogTemp, Log, TEXT("Sequencer stopped"));
}

void FMyClass::OnTimeChanged()
{
    // 可以在此处获取当前时间
    FMovieSceneSequencePlaybackParams Params = 
        ULevelSequenceEditorBlueprintLibrary::GetGlobalPosition();
}
```

## Demo 示例

以下示例展示如何通过 C++ 在编辑器中打开序列、添加 Actor、并监听事件：

**MySequenceManager.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MySequenceManager.generated.h"

class ULevelSequence;
class AActor;

UCLASS(BlueprintType)
class UMySequenceManager : public UObject
{
    GENERATED_BODY()

public:
    /** 打开指定序列并添加 Actor */
    UFUNCTION(BlueprintCallable, Category = "MySequenceManager")
    bool OpenAndPopulateSequence(ULevelSequence* Sequence, const TArray<AActor*>& Actors);

    /** 关闭当前序列 */
    UFUNCTION(BlueprintCallable, Category = "MySequenceManager")
    void CloseSequence();

private:
    UPROPERTY()
    TArray<FDelegateHandle> EventHandles;
};
```

**MySequenceManager.cpp**

```cpp
#include "MySequenceManager.h"
#include "LevelSequenceEditorBlueprintLibrary.h"
#include "LevelSequenceEditorSubsystem.h"
#include "LevelSequence/LevelSequence.h"
#include "Editor.h"

bool UMySequenceManager::OpenAndPopulateSequence(
    ULevelSequence* Sequence, const TArray<AActor*>& Actors)
{
    if (!Sequence)
    {
        return false;
    }

    // 打开序列
    if (!ULevelSequenceEditorBlueprintLibrary::OpenLevelSequence(Sequence))
    {
        return false;
    }

    // 通过子系统添加 Actor
    ULevelSequenceEditorSubsystem* Subsystem = 
        GEditor->GetEditorSubsystem<ULevelSequenceEditorSubsystem>();
    if (Subsystem && !Actors.IsEmpty())
    {
        TArray<FMovieSceneBindingProxy> Bindings = Subsystem->AddActors(Actors);
        UE_LOG(LogTemp, Log, TEXT("Added %d actors with %d bindings"), 
            Actors.Num(), Bindings.Num());
    }

    // 跳转到起始位置并播放
    FMovieSceneSequencePlaybackParams Params;
    Params.Frame = FFrameTime(0);
    ULevelSequenceEditorBlueprintLibrary::SetGlobalPosition(Params);
    ULevelSequenceEditorBlueprintLibrary::Play();

    return true;
}

void UMySequenceManager::CloseSequence()
{
    ULevelSequenceEditorBlueprintLibrary::CloseLevelSequence();
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

插件依赖了 `SequencerScripting` 插件（在 `.uplugin` 中声明），这是提供 `USequencerModuleScriptingLayer` 和 `USequencerCurveEditorObject` 等脚本功能的基础插件。使用者通常不需要额外手动声明依赖，因为该插件作为编辑器插件在加载时自动解析依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `750bdbb6` | Sequencer: Fix captures when opening bindings menus | 修复打开绑定菜单时的变量捕获问题 |
| 2026-05-20 | `4eb0dfb2` | Sequencer: Fix captures when opening bindings menus | 修复绑定菜单中的变量捕获问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的编译警告 |
| 2026-05-12 | `68c46438` | Sequencer: Move AddDefaultTracksForActor to a public method on ULevelSequenceEditorSubsystem so that | 将 AddDefaultTracksForActor 移至子系统公开方法，供外部调用 |
| 2026-04-14 | `79d7a59b` | TLazyObjectPtr Deprecation: | 废弃 TLazyObjectPtr，迁移至新的引用类型 |

### 维护评价

- **年龄**：该插件创建于 2015 年 9 月，是 UE4 Sequencer 系统早期的核心组件，历史超过 10 年
- **活跃度**：近期（2026 年 5 月）仍有持续的功能更新和 bug 修复，属于**活跃维护**状态
- **稳定性**：作为 Epic 官方维护的编辑器核心功能，具有极高的稳定性保障
- **已知注意事项**：
  - 有多个函数在 UE 5.4/5.5 标记为 `Deprecated`（如旧版 `SetCurrentTime(int32)`、`IsTrackFilterEnabled` 等），新代码应使用替换 API
  - `GetPlaybackClient()` 在 UE 5.8 已废弃，应使用 `GetPlaybackClientAsUObject()`
  - 模块类型为 Editor，不可在运行时使用
  - 依赖 `SequencerScripting` 插件
- **推荐使用**：✅ 强烈推荐。这是 Sequencer 的官方编辑器实现，所有需要在蓝图或 C++ 中控制 Sequencer 编辑器状态的场景都应使用此插件提供的 API

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/LevelSequenceEditor)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/LevelSequenceEditor)（无独立测试目录，测试可能位于 Engine/Tests/ 下的 Sequencer 相关测试中）