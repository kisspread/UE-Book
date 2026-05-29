# VirtualCamera

> Content for VirtualCameraCore which adds actors, components, and utilities for controlling and viewing cameras via physical devices.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟相机 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质） |
| 模块 | `VCamExtensions` (Runtime), `VCamExtensionsEditor` (Runtime), `VirtualCamera` (Runtime), `VirtualCameraEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-18 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualCamera) | |

## 用途

VirtualCamera 插件是 Epic Games 虚拟制片（Virtual Production）工具集的核心组成部分。它并非独立的相机控制器，而是作为 `VirtualCameraCore` 插件的内容层，提供了一套蓝图可用的工具集、Actor 和组件，旨在解决通过物理设备（如 iPad 或 iPhone 上的虚拟相机应用）在编辑器内远程控制和预览场景的问题。其核心目标是为影视和广播行业的虚拟制片流程提供流畅的相机操控、拍摄录制（Take Recorder）和序列管理体验。

## 使用场景

-   **影视预览与排演**：你在使用 LED 墙（如 Unreal 的 In-Camera VFX）进行拍摄时，需要导演或摄影师通过 iPad 等设备实时控制虚拟场景中的相机角度、焦距和运动，以预览最终镜头效果。
-   **快速镜头迭代**：你需要快速录制多个相机运动版本（Take），并方便地对它们进行管理、筛选（标记为“好”、“收藏”等）和回放，以便选择最佳版本。
-   **编辑器内游戏视角**：你需要在编辑器视口中快速切换到“游戏视图”，以检查相机在最终游戏中的渲染效果，同时又能方便地切换回编辑视图进行调整。
-   **多人协作拍摄**：在多人编辑会话（Multi-User Editing）中，你需要协调不同客户端的 Take Recorder 录制状态。

## 蓝图用法

本插件的功能主要通过一系列蓝图函数库暴露给蓝图使用，不直接提供新的、可在场景中拖放的 Actor 或组件（这些由底层的 `VirtualCameraCore` 提供）。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsGameRunning` | 检查游戏是否正在运行（PIE或模拟）。 | `UVCamBlueprintFunctionLibrary` |
| `OpenLevelSequence` | 打开一个关卡序列资产。 | `UVCamBlueprintFunctionLibrary` |
| `PlayCurrentLevelSequence` | 播放当前打开的关卡序列。 | `UVCamBlueprintFunctionLibrary` |
| `SetCurrentLevelSequenceCurrentFrame` | 设置当前关卡序列的播放位置（帧）。 | `UVCamBlueprintFunctionLibrary` |
| `ImportSnapshotTexture` | 将图像文件作为纹理资产导入。 | `UVCamBlueprintFunctionLibrary` |
| `EditorSaveAsset` | 通过路径保存资产。 | `UVCamBlueprintFunctionLibrary` |
| `EditorLoadAsset` | 通过路径加载资产。 | `UVCamBlueprintFunctionLibrary` |
| `ModifyObjectMetadataTags` | 修改UObject的元数据标签。 | `UVCamBlueprintFunctionLibrary` |
| `SortAssetsByTimecodeAssetData` | 按时间码对资产数据数组进行排序。 | `UVCamBlueprintFunctionLibrary` |
| `PilotActor` | 使用编辑器脚本“驾驶”一个Actor（通常是相机）。 | `UVCamBlueprintFunctionLibrary` |
| `UpdatePostProcessSettingsForCapture` | 更新场景捕获组件的后处理设置。 | `UVCamBlueprintFunctionLibrary` |
| `CalculateAutoFocusDistance` | 计算自动对焦距离。 | `UVCamBlueprintFunctionLibrary` |
| `DeprojectScreenToWorld` | 将2D屏幕位置转换为世界空间3D位置和方向。 | `UVCamBlueprintFunctionLibrary` |
| `MultiTraceHitProxyOnViewport` | 在视口中进行多重命中代理追踪，用于确定像素对应的Actor。 | `UVCamBlueprintFunctionLibrary` |
| `SetCameraOverscan` | 为相机设置非对称过扫描。 | `UVCamBlueprintFunctionLibrary` |
| `ToggleGameView` | 切换指定视口的游戏视图模式。 | `UGameViewFunctionLibrary` |
| `SetGameViewEnabled` | 设置指定视口的游戏视图启用状态。 | `UGameViewFunctionLibrary` |
| `HasAnyCameraCutsInLevelSequence` | 检查序列中是否有任何镜头切换设置。 | `ULevelSequenceVCamLibrary` |
| `FindPilotableCamerasInActiveLevelSequence` | 在活动的关卡序列中查找所有可驾驶的相机。 | `ULevelSequenceVCamLibrary` |
| `GetTakeMetaDataTag_Slate` | 获取拍摄元数据的“场记板”标签名。 | `UTakeMetaDataTagsFunctionLibrary` |
| `GetIsNoGood (Migration)` | （迁移辅助）获取拍摄是否被标记为“不好”。 | `UVCamTakesMetaDataMigration` |
| `SetFavoriteLevel (Migration)` | （迁移辅助）设置拍摄的收藏等级。 | `UVCamTakesMetaDataMigration` |
| `GetRecordOnClientLocal` | 获取本地客户端的“在客户端录制”开关状态。 | `UMultiUserTakesVCamFunctionLibrary` |
| `SetSynchronizeTakeRecorderTransactionsLocal` | 设置本地客户端的“同步Take Recorder事务”开关。 | `UMultiUserTakesVCamFunctionLibrary` |

### 使用示例（蓝图描述）

假设你有一个蓝图，需要在编辑器内播放一个序列并导出一帧截图：
1.  使用 `OpenLevelSequence` 节点打开你的序列资产。
2.  连接 `PlayCurrentLevelSequence` 节点开始播放。
3.  使用 `SetCurrentLevelSequenceCurrentFrame` 节点将播放头移动到目标帧。
4.  调用 `ImportSnapshotTexture` 节点，传入帧缓冲区图像的路径和参数，将其保存为 UTexture 资产。
5.  （可选）使用 `ModifyObjectMetadataTags` 为这个新生成的纹理资产添加自定义的元数据标签，如“ScreenshotFrame”:”100”。

## C++ 用法

虽然主要面向蓝图，但核心功能也可以通过 C++ 调用。关键类是 `UVCamBlueprintFunctionLibrary` 和相关的函数库。

### 头文件引入

```cpp
#include “FunctionLibraries/VCamBlueprintFunctionLibrary.h”
#include “FunctionLibraries/GameViewFunctionLibrary.h”
#include “LevelSequence/VirtualCameraClipsMetaData.h” // 注意：此类已部分废弃
```

### 基本用法

以下示例展示了如何在 C++ 中使用 VCam 函数库来控制序列播放和获取元数据标签。

```cpp
// (来自 Public/FunctionLibraries/VCamBlueprintFunctionLibrary.h)
// 检查编辑器是否在游戏模式下运行
bool bIsRunning = UVCamBlueprintFunctionLibrary::IsGameRunning();

// 获取当前打开的关卡序列
ULevelSequence* CurrentSequence = UVCamBlueprintFunctionLibrary::GetCurrentLevelSequence();

// 打开一个特定的关卡序列资产（假设 MySequence 是 ULevelSequence* 指针）
bool bSuccess = UVCamBlueprintFunctionLibrary::OpenLevelSequence(MySequence);

// 获取 “拍摄时间码” 这个元数据标签的名称
FName TimecodeTag = UTakeMetaDataTagsFunctionLibrary::GetTakeMetaDataTag_TimecodeIn();

// 为一个关卡序列资产数据添加元数据
FAssetData AssetData; // 假设已正确初始化
UVCamBlueprintFunctionLibrary::ModifyObjectMetadataTags(AssetData.GetAsset(), TEXT(“CustomTag”), TEXT(“Value”));
```

### 进阶用法

结合多个函数库功能，可以实现更复杂的编辑器自动化脚本。

```cpp
// (综合来自多个头文件的功能)
// 1. 进入游戏视图模式
UGameViewFunctionLibrary::SetGameViewEnabled(EVCamTargetViewportID::PIE, true);

// 2. 获取当前序列并检查其镜头切换
if (ULevelSequence* Sequence = UVCamBlueprintFunctionLibrary::GetCurrentLevelSequence())
{
    if (ULevelSequenceVCamLibrary::HasAnyCameraCutsInLevelSequence(Sequence))
    {
        // 3. 如果存在镜头切换，则查找序列中的相机
        TArray<FPilotableSequenceCameraInfo> Cameras = ULevelSequenceVCamLibrary::FindPilotableCamerasInActiveLevelSequence();
        if (Cameras.Num() > 0)
        {
            // 4. “驾驶”找到的第一个相机
            UVCamBlueprintFunctionLibrary::PilotActor(Cameras[0].Camera->GetOwner());
        }
    }
    // 5. (迁移辅助) 检查并迁移旧版元数据
    if (UVCamTakesMetaDataMigration::NeedsToMigrateVCamMetaData(Sequence))
    {
        UVCamTakesMetaDataMigration::MigrateVCamTakesMetaData(Sequence);
    }
}

// 6. 退出游戏视图模式
UGameViewFunctionLibrary::SetGameViewEnabled(EVCamTargetViewportID::PIE, false);
```

**注意**：`UVirtualCameraClipsMetaData` 中的许多属性和方法已在 UE 5.6 中被标记为废弃。对于新的开发，应使用 `UVCamTakesMetaDataMigration` 作为过渡，并最终转向引擎提供的 `UMovieSceneShotMetaData` 和 `ULevelSequenceShotMetaDataLibrary`。

## Demo 示例

此插件作为工具集，没有独立的可运行Demo Actor。其使用体现在虚拟制片的工作流中（如配合 `Take Recorder` 和 `Level Sequence` 编辑器）。一个最小的 C++ 示例可能是在自定义编辑器工具中批量为序列资产添加元数据标签。

```cpp
// MyEditorToolkit.h
#pragma once
#include “CoreMinimal.h”
#include “UObject/NoExportTypes.h”

class ULevelSequence;
class UMyEditorToolkit : public UObject
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category = “Editor Tools”)
    static void BatchTagLevelSequences(const TArray<FAssetData>& LevelSequenceAssets, FName Tag, const FString& Value);
};

// MyEditorToolkit.cpp
#include “MyEditorToolkit.h”
#include “FunctionLibraries/VCamBlueprintFunctionLibrary.h”

void UMyEditorToolkit::BatchTagLevelSequences(const TArray<FAssetData>& LevelSequenceAssets, FName Tag, const FString& Value)
{
    for (const FAssetData& AssetData : LevelSequenceAssets)
    {
        if (ULevelSequence* LevelSequence = Cast<ULevelSequence>(AssetData.GetAsset()))
        {
            // 使用 VCam 函数库为其添加统一的元数据标签
            UVCamBlueprintFunctionLibrary::ModifyObjectMetadataTags(LevelSequence, Tag, Value);
        }
    }
}
```

## 模块依赖

从 `VirtualCamera.Build.cs` 分析，本插件依赖了大量虚拟制片和电影相关的模块。

| 模块 | 用途 |
|---|---|
| `LevelSequenceEditor` | 提供与关卡序列编辑器交互的蓝图接口。 |
| `TakeRecorder` | 集成“拍摄录制器”功能。 |
| `MovieScene` | 底层电影场景框架。 |
| `LevelSequence` | 关卡序列资产和运行时。 |
| `SequencerCore` | Sequencer的核心功能。 |
| `ViewportInteraction` | 提供视口交互功能。 |
| `MultiUserClient` | 支持多用户编辑会话。 |
| `ContentBrowserAssetData` | 与内容浏览器资产数据交互。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the ... | 将多个虚拟制片资产移动到新的资产分类中，并进行迁移。 |
| 2026-04-20 | `9de9532f` | VCam: update transform track mask based on constraint filter | 根据约束过滤器更新VCam的变换轨迹掩码。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从UE_LOG迁移至UE_LOGF。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 在修复了错误的查找替换操作后进行的第二次提交。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 撤销了变更列表 CL51314860 的改动。 |

### 维护评价

-   **状态**：**实验性（Beta）且活跃维护中**。插件仍处于 Beta 状态（`IsBetaVersion=true`），且需要手动启用（`EnabledByDefault=false`）。
-   **活跃度**：非常活跃。从 Git 历史看，最近一个月内仍有持续的功能更新和代码优化，表明 Epic Games 内部团队正在积极开发和完善此工具集。
-   **代码健康**：代码库正在经历重构和迁移。多个旧版类和函数（如 `UVirtualCameraClipsMetaData` 的大部分属性、`UDEPRECATED_AssetFilteringAndSortingFunctionLibrary`）已被标记为废弃，并引导用户使用新的、更通用的引擎接口（如 `UEditorAssetSubsystem`、`UMovieSceneShotMetaData`）。这是一个积极的信号，表明代码正在向更稳定、更通用的方向发展。
-   **推荐**：**对于正在使用或计划使用 Unreal 进行虚拟制片（ICVFX）的项目，强烈推荐关注和试用此插件**。它是 Epic 官方提供的核心虚拟相机工作流解决方案，尽管是 Beta 版，但功能完整且持续更新。对于不涉及虚拟制片的普通游戏开发项目，则无需使用。
-   **注意事项**：由于是 Beta 版，API 可能发生变化（如所示的废弃标记）。在项目中使用时需做好版本适配准备。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualCamera)
-   [官方文档]() (DocsURL 字段为空)
-   [测试用例]() (未在提供的源码路径中发现专用测试用例，可能集成在更上层的虚拟制片测试中)