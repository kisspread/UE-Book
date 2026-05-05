# Level Sequence Editor

> Content Editor for LevelSequence Assets.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（SVG 图标） |
| 模块 | `LevelSequenceEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2015-09-29 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/LevelSequenceEditor) | |

## 用途

Level Sequence Editor 是 Unreal Engine 的核心 Sequencer 编辑器 UI 插件，为 `ULevelSequence` 资产提供完整的可视化编辑界面。它是连接底层 `MovieScene` / `SequencerCore` 运行时和用户之间的桥梁，负责：

- **资产编辑器 UI**：双击 `.uasset` 中的 Level Sequence 时打开的 Sequencer 窗口，包括时间轴、曲线编辑器、轨道大纲等全部 UI
- **Cinematic Viewport**：专用的电影级视口，提供 Letterbox、安全框、网格辅助线、十字准星等专业摄影辅助功能
- **蓝图脚本接口**：通过 `ULevelSequenceEditorBlueprintLibrary` 和 `ULevelSequenceEditorSubsystem` 暴露大量编辑器操作给蓝图和 Python 脚本
- **绑定管理**：管理 Sequencer 中 Actor/Camera 等对象的 Possessable/Spawnable 绑定关系
- **FBX 导入/导出**：支持动画数据的 FBX 格式导入导出
- **Placement Mode 集成**：在编辑器的放置面板注册 Cinematic 分类（CineCamera、CameraRig、LevelSequenceActor 等）
- **Film Overlay 系统**：可扩展的电影叠加层框架，支持 Letterbox、安全区域等自定义覆盖层

简而言之：**MovieScene 定义数据格式，SequencerCore 提供核心引擎，LevelSequenceEditor 把它们变成你看到的编辑器窗口**。

## 使用场景

- 你在制作过场动画、CG 镜头或电影级内容 → 打开 Level Sequence 编辑器
- 你需要通过蓝图/Python 脚本自动化 Sequencer 工作流（如批量打开、设置播放头、选择轨道）
- 你需要在编辑器中预览 Camera Cut 并直接在 Cinematic Viewport 中看到结果
- 你需要将 Actor 绑定到 Sequencer 并管理 Spawnable/Possessable 关系
- 你需要从 FBX 导入关键帧动画数据到 Sequencer

## 模块结构

本插件包含一个 Editor 模块，内部按功能区域组织：

```
LevelSequenceEditor/
├── Public/
│   ├── LevelSequenceEditorModule.h          # 模块接口
│   ├── LevelSequenceEditorSubsystem.h       # 编辑器子系统（蓝图可调用）
│   ├── LevelSequenceEditorBlueprintLibrary.h # 蓝图函数库（静态函数）
│   ├── ILevelSequenceEditorToolkit.h         # Toolkit 接口
│   ├── FilmOverlayToolkit.h                  # Film Overlay 管理
│   ├── IFilmOverlay.h                        # Film Overlay 抽象接口
│   ├── AssetTools/
│   │   └── AssetDefinition_LevelSequence.h   # 资产定义（Content Browser 集成）
│   ├── Misc/
│   │   ├── LevelSequenceEditorSettings.h     # 编辑器设置
│   │   ├── LevelSequencePlaybackContext.h    # 播放上下文管理
│   │   └── LevelSequenceEditorSpawnRegister.h # Spawn Register（编辑器版）
│   └── Widgets/
│       └── SLevelSequenceFavoriteRating.h    # 评分 Widget
├── Private/
│   ├── LevelSequenceEditorToolkit.h/.cpp     # 编辑器 Toolkit 实现
│   ├── LevelSequenceEditorModule.cpp         # 模块注册逻辑
│   ├── LevelSequenceEditorCommands.h/.cpp    # UI 命令定义
│   ├── LevelSequenceEditorSubsystem.cpp
│   ├── LevelSequenceEditorBlueprintLibrary.cpp
│   ├── CinematicViewport/
│   │   ├── SCinematicLevelViewport.h/.cpp    # 电影级视口
│   │   ├── CinematicViewportCommands.h/.cpp   # 视口命令
│   │   ├── CinematicViewportLayoutEntity.h   # 视口布局
│   │   ├── FilmOverlays.h/.cpp               # Film Overlay 实现
│   │   └── SCinematicTransportRange.h/.cpp   # 传输范围控件
│   ├── Factories/
│   │   └── LevelSequenceFactoryNew.h/.cpp    # 资产创建工厂
│   ├── Misc/
│   │   ├── LevelSequenceCustomization.h/.cpp # Sequencer 自定义
│   │   ├── MovieSceneSequenceEditor_LevelSequence.h # Director Blueprint 支持
│   │   ├── LevelSequenceEditorActorBinding.h/.cpp   # Actor 绑定
│   │   ├── LevelSequenceEditorActorSpawner.h/.cpp   # Actor Spawner
│   │   ├── LevelSequenceEditorHelpers.h/.cpp        # 工具函数
│   │   ├── LevelSequenceEditorMenuContext.h         # 菜单上下文
│   │   └── LevelSequencePlaybackContext.cpp
│   ├── Styles/
│   │   └── LevelSequenceEditorStyle.h        # 编辑器样式
│   └── Widgets/
│       ├── SScoreRating.h/.cpp               # 评分控件
│       └── SScoreRatingElement.h/.cpp        # 评分元素
└── Content/
    ├── Flag.svg                              # 旗帜图标
    └── ThumbsDown.svg                        # 差评图标
```

## 蓝图用法

### 核心节点 — 序列操作 (`ULevelSequenceEditorBlueprintLibrary`)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OpenLevelSequence` | 在 Sequencer 编辑器中打开指定 Level Sequence | `ULevelSequenceEditorBlueprintLibrary` |
| `CloseLevelSequence` | 关闭当前打开的 Level Sequence | `ULevelSequenceEditorBlueprintLibrary` |
| `GetCurrentLevelSequence` | 获取当前打开的根级 Level Sequence | `ULevelSequenceEditorBlueprintLibrary` |
| `GetFocusedLevelSequence` | 获取当前聚焦的子序列（在序列层级中） | `ULevelSequenceEditorBlueprintLibrary` |
| `FocusLevelSequence` | 聚焦到指定 Sub Section 对应的子序列 | `ULevelSequenceEditorBlueprintLibrary` |
| `FocusParentSequence` | 返回上层父序列 | `ULevelSequenceEditorBlueprintLibrary` |
| `GetSubSequenceHierarchy` | 获取从根到当前聚焦序列的 Sub Section 路径 | `ULevelSequenceEditorBlueprintLibrary` |
| `RefreshCurrentLevelSequence` | 刷新 Sequencer UI（下一帧生效） | `ULevelSequenceEditorBlueprintLibrary` |
| `ForceUpdate` | 强制立即评估并更新 UI | `ULevelSequenceEditorBlueprintLibrary` |

### 核心节点 — 播放控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play` | 播放当前序列 | `ULevelSequenceEditorBlueprintLibrary` |
| `Pause` | 暂停播放 | `ULevelSequenceEditorBlueprintLibrary` |
| `PlayTo` | 从当前位置播放到指定帧 | `ULevelSequenceEditorBlueprintLibrary` |
| `Set Current Time` (`SetGlobalPosition`) | 设置全局播放头位置 | `ULevelSequenceEditorBlueprintLibrary` |
| `Get Current Time` (`GetGlobalPosition`) | 获取全局播放头位置 | `ULevelSequenceEditorBlueprintLibrary` |
| `Set Current Local Time` (`SetLocalPosition`) | 设置本地播放头位置（子序列中） | `ULevelSequenceEditorBlueprintLibrary` |
| `Get Current Local Time` (`GetLocalPosition`) | 获取本地播放头位置 | `ULevelSequenceEditorBlueprintLibrary` |
| `SetPlaybackSpeed` | 设置播放速度 | `ULevelSequenceEditorBlueprintLibrary` |
| `GetPlaybackSpeed` | 获取播放速度 | `ULevelSequenceEditorBlueprintLibrary` |
| `SetLoopMode` / `GetLoopMode` | 设置/获取循环模式 | `ULevelSequenceEditorBlueprintLibrary` |
| `GetPlaybackStartPosition` | 获取播放范围起始位置 | `ULevelSequenceEditorBlueprintLibrary` |
| `GetPlaybackEndPosition` | 获取播放范围结束位置 | `ULevelSequenceEditorBlueprintLibrary` |
| `IsPlaying` | 检查是否正在播放 | `ULevelSequenceEditorBlueprintLibrary` |

### 核心节点 — 选择操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSelectedTracks` | 获取当前选中的轨道 | `ULevelSequenceEditorBlueprintLibrary` |
| `GetSelectedSections` | 获取当前选中的 Section | `ULevelSequenceEditorBlueprintLibrary` |
| `GetSelectedChannels` | 获取当前选中的通道 | `ULevelSequenceEditorBlueprintLibrary` |
| `GetChannelsWithSelectedKeys` | 获取包含选中关键帧的通道 | `ULevelSequenceEditorBlueprintLibrary` |
| `GetSelectedKeys` | 获取指定通道中选中的关键帧索引 | `ULevelSequenceEditorBlueprintLibrary` |
| `GetSelectedFolders` | 获取选中的文件夹 | `ULevelSequenceEditorBlueprintLibrary` |
| `GetSelectedBindings` | 获取选中的对象绑定 | `ULevelSequenceEditorBlueprintLibrary` |
| `SelectTracks` | 选择指定轨道 | `ULevelSequenceEditorBlueprintLibrary` |
| `SelectSections` | 选择指定 Section | `ULevelSequenceEditorBlueprintLibrary` |
| `SelectKeys` | 选择指定关键帧 | `ULevelSequenceEditorBlueprintLibrary` |
| `SelectFolders` | 选择指定文件夹 | `ULevelSequenceEditorBlueprintLibrary` |
| `SelectBindings` / `DeselectBindings` | 选择/取消选择绑定 | `ULevelSequenceEditorBlueprintLibrary` |
| `EmptySelection` | 清空选择 | `ULevelSequenceEditorBlueprintLibrary` |
| `SetSelectionRangeStart` / `End` | 设置选择范围起止帧 | `ULevelSequenceEditorBlueprintLibrary` |

### 核心节点 — 绑定管理 (`ULevelSequenceEditorSubsystem`)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddActors` | 将已有 Actor 添加到 Sequencer（自动创建默认轨道） | `ULevelSequenceEditorSubsystem` |
| `AddSpawnableFromInstance` | 从实例创建 Spawnable 绑定 | `ULevelSequenceEditorSubsystem` |
| `AddSpawnableFromClass` | 从类创建 Spawnable 绑定 | `ULevelSequenceEditorSubsystem` |
| `CreateCamera` | 创建 CineCamera 并添加到 Sequencer | `ULevelSequenceEditorSubsystem` |
| `ConvertToSpawnable` | 将 Possessable 转换为 Spawnable | `ULevelSequenceEditorSubsystem` |
| `ConvertToPossessable` | 将 Spawnable 转换为 Possessable | `ULevelSequenceEditorSubsystem` |
| `ConvertToCustomBinding` | 转换为自定义绑定类型 | `ULevelSequenceEditorSubsystem` |
| `AddActorsToBinding` | 将 Actor 分配到指定绑定 | `ULevelSequenceEditorSubsystem` |
| `ReplaceBindingWithActors` | 用新 Actor 替换绑定中的对象 | `ULevelSequenceEditorSubsystem` |
| `RemoveActorsFromBinding` | 从绑定中移除 Actor | `ULevelSequenceEditorSubsystem` |
| `RemoveAllBindings` | 移除绑定中的所有对象 | `ULevelSequenceEditorSubsystem` |
| `RemoveInvalidBindings` | 移除无效绑定引用 | `ULevelSequenceEditorSubsystem` |
| `FixActorReferences` | 自动修复断开的 Actor 引用 | `ULevelSequenceEditorSubsystem` |
| `RebindComponent` | 重新绑定组件 | `ULevelSequenceEditorSubsystem` |
| `ChangeActorTemplateClass` | 更改 Spawnable 的 Actor 模板类 | `ULevelSequenceEditorSubsystem` |
| `SaveDefaultSpawnableState` | 保存 Spawnable 的默认状态 | `ULevelSequenceEditorSubsystem` |

### 核心节点 — 剪贴板操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CopyFolders` / `PasteFolders` | 复制/粘贴文件夹 | `ULevelSequenceEditorSubsystem` |
| `CopySections` / `PasteSections` | 复制/粘贴 Section | `ULevelSequenceEditorSubsystem` |
| `CopyTracks` / `PasteTracks` | 复制/粘贴轨道 | `ULevelSequenceEditorSubsystem` |
| `CopyBindings` / `PasteBindings` | 复制/粘贴绑定 | `ULevelSequenceEditorSubsystem` |

### 核心节点 — 其他

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsLevelSequenceLocked` / `SetLockLevelSequence` | 检查/设置序列锁定状态 | `ULevelSequenceEditorBlueprintLibrary` |
| `IsCameraCutLockedToViewport` / `SetLockCameraCutToViewport` | 检查/设置 Camera Cut 与视口的锁定 | `ULevelSequenceEditorBlueprintLibrary` |
| `GetBoundObjects` | 获取绑定 ID 对应的对象 | `ULevelSequenceEditorBlueprintLibrary` |
| `IsTrackFilterActive` / `SetTrackFilterActive` | 查询/设置轨道过滤器 | `ULevelSequenceEditorBlueprintLibrary` |
| `GetTrackFilterNames` | 获取所有可用轨道过滤器名称 | `ULevelSequenceEditorBlueprintLibrary` |
| `SnapSectionsToTimelineUsingSourceTimecode` | 使用源 Timecode 对齐 Section | `ULevelSequenceEditorSubsystem` |
| `SyncSectionsUsingSourceTimecode` | 使用源 Timecode 同步 Section | `ULevelSequenceEditorSubsystem` |
| `BakeTransformWithSettings` | 烘焙变换动画（带设置） | `ULevelSequenceEditorSubsystem` |
| `GetScriptingLayer` | 获取 Sequencer 脚本层 | `ULevelSequenceEditorSubsystem` |
| `GetCurveEditor` | 获取曲线编辑器对象 | `ULevelSequenceEditorSubsystem` |

### 使用示例（蓝图描述）

**打开并播放一个 Level Sequence：**
1. 获取 Level Sequence 资产引用（例如通过 `Get Asset` 节点）
2. 调用 `Open Level Sequence`（位于 `ULevelSequenceEditorBlueprintLibrary`），输入资产引用
3. 调用 `Play` 开始播放
4. 通过 `Is Playing` 查询播放状态

**批量添加 Actor 到 Sequencer：**
1. 使用 `Get Actors Of Class` 获取场景中所有目标 Actor
2. 构造 Actor 数组
3. 调用 `Add Actors`（位于 `ULevelSequenceEditorSubsystem`），返回 `FMovieSceneBindingProxy` 数组

**程序化创建 Camera Cut：**
1. 调用 `Create Camera`（Spawnable=true），获取 `FMovieSceneBindingProxy` 和 `ACineCameraActor` 输出
2. 设置 Camera 的位置和 FOV
3. 调用 `Force Update` 刷新

## C++ 用法

### 头文件引入

```cpp
#include "LevelSequenceEditorSubsystem.h"
#include "LevelSequenceEditorBlueprintLibrary.h"
#include "LevelSequenceEditorModule.h"
```

### 基本用法 — 获取 Subsystem

`ULevelSequenceEditorSubsystem` 是一个 `UEditorSubsystem`，通过标准方式获取：

```cpp
// 获取 Level Sequence Editor 子系统
ULevelSequenceEditorSubsystem* Subsystem = GEditor->GetEditorSubsystem<ULevelSequenceEditorSubsystem>();

// 添加 Actor 到 Sequencer
TArray<AActor*> Actors;
Actors.Add(MyActor);
TArray<FMovieSceneBindingProxy> Bindings = Subsystem->AddActors(Actors);
```

（来源：`Source/LevelSequenceEditor/Public/LevelSequenceEditorSubsystem.h`）

### 基本用法 — 蓝图库静态函数

`ULevelSequenceEditorBlueprintLibrary` 提供全静态函数，可直接调用：

```cpp
#include "LevelSequenceEditorBlueprintLibrary.h"

// 打开 Level Sequence
ULevelSequence* MySequence = LoadObject<ULevelSequence>(nullptr, TEXT("/Game/Cinematics/MyLevelSequence"));
ULevelSequenceEditorBlueprintLibrary::OpenLevelSequence(MySequence);

// 设置播放头到第 30 帧
FMovieSceneSequencePlaybackParams Params;
Params.Frame = 30;
ULevelSequenceEditorBlueprintLibrary::SetGlobalPosition(Params, EMovieSceneTimeUnit::DisplayRate);

// 播放
ULevelSequenceEditorBlueprintLibrary::Play();
```

（来源：`Source/LevelSequenceEditor/Public/LevelSequenceEditorBlueprintLibrary.h`）

### 进阶用法 — 绑定类型转换

```cpp
// 将 Possessable 转换为 Spawnable
FMovieSceneBindingProxy Binding = /* ... */;
TArray<FMovieSceneBindingProxy> SpawnableBindings = Subsystem->ConvertToSpawnable(Binding);

// 转换为自定义绑定类型
FMovieSceneBindingProxy CustomBinding = Subsystem->ConvertToCustomBinding(Binding, UMyCustomBinding::StaticClass());

// 获取自定义绑定对象以访问属性
TArray<UMovieSceneCustomBinding*> CustomBindingObjects = Subsystem->GetCustomBindingObjects(Binding);
for (UMovieSceneCustomBinding* Obj : CustomBindingObjects)
{
    // 访问自定义绑定属性
}
```

（来源：`Source/LevelSequenceEditor/Public/LevelSequenceEditorSubsystem.h`）

### 进阶用法 — 模块接口扩展

通过 `ILevelSequenceEditorModule` 注册自定义 Sequencer 集成：

```cpp
#include "LevelSequenceEditorModule.h"

ILevelSequenceEditorModule& LSEModule = FModuleManager::LoadModuleChecked<ILevelSequenceEditorModule>("LevelSequenceEditor");

// 注册自定义 Sequencer 自定义
FGuid Handle = LSEModule.RegisterAdditionalLevelSequenceEditorCustomization(
    FOnGetSequencerCustomizationInstance::CreateLambda([]()
    {
        return MakeUnique<FMyCustomSequencerCustomization>();
    })
);

// 监听带 Shots 的序列创建
LSEModule.OnLevelSequenceWithShotsCreated().AddLambda([](UObject* Asset)
{
    // 处理新创建的序列
});

// 注销
LSEModule.UnregisterAdditionalLevelSequenceEditorCustomization(Handle);
```

（来源：`Source/LevelSequenceEditor/Public/LevelSequenceEditorModule.h`）

### 进阶用法 — Film Overlay 系统

```cpp
#include "FilmOverlayToolkit.h"
#include "IFilmOverlay.h"

// 自定义 Film Overlay
struct FMyFilmOverlay : IFilmOverlay
{
    virtual FText GetDisplayName() const override { return NSLOCTEXT("My", "Overlay", "My Overlay"); }
    virtual const FSlateBrush* GetThumbnail() const override { return FAppStyle::GetBrush("Icons.Info"); }
    virtual void Paint(const FGeometry& AllottedGeometry, const FSlateRect& CullingRect,
                       FSlateWindowElementList& OutDrawElements, int32 LayerId) const override
    {
        // 自定义绘制逻辑
    }
};

// 注册为 Primary Overlay（同时只能激活一个）
UFilmOverlayToolkit::RegisterPrimaryFilmOverlay("MyOverlay", MakeShared<FMyFilmOverlay>());

// 或注册为 Toggleable Overlay（可同时激活多个）
UFilmOverlayToolkit::RegisterToggleableFilmOverlay("MyOverlay", MakeShared<FMyFilmOverlay>());
```

（来源：`Source/LevelSequenceEditor/Public/FilmOverlayToolkit.h`, `Source/LevelSequenceEditor/Public/IFilmOverlay.h`）

## Demo 示例

### 最小编辑器扩展示例

```cpp
// MySequenceAutomation.Build.cs
public class MySequenceAutomation : ModuleRules
{
    public MySequenceAutomation(ReadOnlyTargetRules Target) : base(Target)
    {
        PublicDependencyModuleNames.AddRange(new string[] {
            "Core",
            "CoreUObject",
            "Engine",
            "LevelSequence",
            "MovieScene",
            "LevelSequenceEditor"  // 依赖 LevelSequenceEditor 模块
        });
    }
}
```

```cpp
// MySequenceAutomation.h
#pragma once
#include "Modules/ModuleManager.h"

class FMySequenceAutomationModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// MySequenceAutomation.cpp
#include "MySequenceAutomation.h"
#include "LevelSequenceEditorSubsystem.h"
#include "LevelSequenceEditorBlueprintLibrary.h"
#include "LevelSequence.h"

IMPLEMENT_MODULE(FMySequenceAutomationModule, MySequenceAutomation)

void FMySequenceAutomationModule::StartupModule()
{
    // 模块启动时的示例：订阅序列打开事件
}

void FMySequenceAutomationModule::ShutdownModule()
{
}

// 示例函数：批量操作 Sequencer
void BatchSetupSequence(ULevelSequence* Sequence)
{
    // 1. 在编辑器中打开
    ULevelSequenceEditorBlueprintLibrary::OpenLevelSequence(Sequence);

    // 2. 获取 Subsystem
    ULevelSequenceEditorSubsystem* Subsystem =
        GEditor->GetEditorSubsystem<ULevelSequenceEditorSubsystem>();

    // 3. 添加 Camera
    ACineCameraActor* Camera = nullptr;
    FMovieSceneBindingProxy CameraBinding = Subsystem->CreateCamera(true, Camera);

    // 4. 设置播放范围
    FMovieSceneSequencePlaybackParams StartParams;
    StartParams.Frame = 0;
    ULevelSequenceEditorBlueprintLibrary::SetGlobalPosition(StartParams);

    // 5. 刷新
    ULevelSequenceEditorBlueprintLibrary::ForceUpdate();
}
```

## 模块依赖

### Public 依赖（你的模块需要引用）

| 模块 | 用途 |
|---|---|
| `SequencerScripting` | Sequencer 蓝图脚本运行时 |
| `SequencerScriptingEditor` | Sequencer 蓝图脚本编辑器扩展 |

### Private 依赖（插件内部使用）

| 模块 | 用途 |
|---|---|
| `LevelSequence` | Level Sequence 核心运行时 |
| `MovieScene` | Movie Scene 底层框架 |
| `SequencerCore` | Sequencer 核心引擎 |
| `Sequencer` | Sequencer 编辑器核心 |
| `MovieSceneTools` | Movie Scene 编辑器工具 |
| `MovieSceneTracks` | Movie Scene 轨道类型 |
| `CinematicCamera` | CineCamera Actor 支持 |
| `CurveEditor` | 曲线编辑器 |
| `LevelEditor` | 关卡编辑器集成 |
| `UnrealEd` | 编辑器框架 |
| `VREditor` | VR 编辑器模式支持 |
| `ToolMenus` | 工具菜单系统 |
| `PropertyEditor` | 属性编辑器 |
| `ContentBrowser` | 内容浏览器集成 |
| `SceneOutliner` | 场景大纲 |
| `AssetDefinition` | 资产定义系统 |
| `UniversalObjectLocator` | 通用对象定位器 |
| `Constraints` | 约束系统 |
| `TimeManagement` | 时间管理 |
| `FBX` (ThirdParty) | FBX 导入导出 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-09-23 | `a33e983` | Film Overlays: 修复 tint 值每次打开配置菜单时被重置的问题 |
| 2025-09-10 | `cb5faa0` | VR Editor: 废弃 VR Editor 模式及相关类 |
| 2025-09-10 | `0dae3bc` | Sequencer: 修复 `GetBoundObjects` 使其接受 sequence ID 而非 sequence 对象 |
| 2025-09-05 | `6a9721d` | ShotManagement: 修复 CineAssembly tooltip 不更新 Favorite Rating 的问题 |

### 维护评价

- **创建时间**: 2015 年 9 月，UE4 时代就存在的核心插件
- **更新频率**: 非常活跃，2025 年 9 月仍在持续更新
- **维护状态**: ✅ **活跃维护** — 作为 Unreal Engine Sequencer 的核心编辑器 UI，由 Epic Games 官方持续维护
- **重要性**: 极高 — 这是所有 Sequencer 编辑操作的基础，几乎所有使用 Level Sequence 的项目都依赖此插件
- **推荐**: ✅ **强烈推荐使用** — 默认启用，无需手动操作

**注意事项**:
- 该插件仅在 Editor 中加载（`Type: Editor`），不会被打包到最终游戏中
- 同时支持 LiveLinkHub 程序（`SupportedPrograms: ["LiveLinkHub"]`）
- 依赖 `SequencerScripting` 插件
- 5.4/5.5 版本中一些旧 API 被标记为 `UE_DEPRECATED`（如 `SetCurrentTime(int32)` → `SetGlobalPosition(FMovieSceneSequencePlaybackParams)`），建议使用新 API

## 架构概览

### 关键类关系

```
ILevelSequenceEditorModule (模块接口)
  └── FLevelSequenceEditorModule (模块实现)
        ├── 注册 Editor Object Binding (FLevelSequenceEditorActorBinding)
        ├── 注册 Actor Spawner (FLevelSequenceEditorActorSpawner)
        ├── 注册 Sequence Editor (FMovieSceneSequenceEditor_LevelSequence)
        ├── 注册 Sequencer Customization (FLevelSequenceCustomization)
        ├── 注册 Cinematic Viewport 类型
        ├── 注册 Placement Mode 分类
        └── 注册 Settings

FLevelSequenceEditorToolkit (编辑器 Toolkit)
  ├── 拥有 ISequencer 实例
  ├── 拥有 FLevelSequencePlaybackContext
  └── 管理 Sequencer UI Tab

ULevelSequenceEditorSubsystem (EditorSubsystem)
  ├── 管理活跃的 Sequencer 实例列表
  ├── 提供蓝图可调用的编辑操作
  └── 管理 Curve Editor 对象映射

ULevelSequenceEditorBlueprintLibrary (蓝图函数库)
  └── 静态代理到当前活跃的 ISequencer

FLevelSequencePlaybackContext (播放上下文)
  └── 管理 World Context（自动绑定 PIE/Simulate/Editor 世界）

FLevelSequenceEditorSpawnRegister (Spawn Register)
  └── 编辑器特有的 Spawn 管理（保持选择状态、投影默认状态）
```

### 播放上下文自动绑定

`FLevelSequencePlaybackContext` 负责决定 Sequencer 在哪个 World 中评估：

1. 如果启用了 `bAutoBindToPIE` 且正在 PIE → 使用 PIE World
2. 如果启用了 `bAutoBindToSimulate` 且正在 Simulate → 使用 Simulate World
3. 否则 → 使用 Editor World
4. 用户可通过 `OverrideWith()` 手动指定 World

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/LevelSequenceEditor)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/sequencer-in-unreal-engine/)（Sequencer 总览）
- 测试用例：本插件无独立测试文件
