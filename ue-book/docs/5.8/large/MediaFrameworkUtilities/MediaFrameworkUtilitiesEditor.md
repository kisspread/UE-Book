# Media Framework Utilities

> This plugin provides utility assets and actors designed to simplify the Media Framework setup. It includes access to the Media Profile editor.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体框架工具集 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具、资产、Actor） |
| 模块 | `MediaFrameworkUtilities` (Runtime), `MediaFrameworkUtilitiesEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaFrameworkUtilities) | |

## 用途

`MediaFrameworkUtilities` 插件的核心目的是为 Unreal Engine 的 Media Framework 提供一套 **集成化的编辑器工具集**，用于管理、预览和调试复杂的媒体输入/输出工作流。它不仅仅是简化设置，而是构建了一个 **媒体工作流的开发环境**。

该插件解决了以下核心问题：
1.  **集中化管理**：通过 `MediaProfile`（媒体配置文件）资产，将项目中的多个 `MediaSource`（媒体源）和 `MediaOutput`（媒体输出）组织在一起，形成一个可管理、可切换的配置集合。
2.  **所见即所得预览**：提供专用的 `Media Profile Editor` 编辑器窗口，允许用户在编辑器中同时实时预览多个视频输入或输出的画面，并进行布局、缩放、通道查看等操作。
3.  **高级捕获控制**：内置一个 `Media Capture` 面板，支持配置和启动从编辑器视口、特定摄像机或渲染目标到媒体输出的捕获流程，方便进行视频录制、串流输出等。
4.  **视频输入监控**：提供 `Video Input` 面板，用于监控 `MediaBundle` 或 `MediaSource` 的实时视频流状态，是调试外部视频输入设备（如采集卡、IP摄像头）的利器。
5.  **时间码与同步**：集成了时间码（Timecode）和基因锁（Genlock）的显示与配置工具，对于需要精确帧同步的专业媒体工作流至关重要。

简单来说，它是处理 **虚拟制作（Virtual Production）**、**广播（Broadcast）**、**实时视频合成（Real-time Compositing）** 和 **多机位监控（Multi-camera Monitoring）** 等专业场景的必备工具箱。

## 使用场景

-   你在进行一场 **多机位虚拟制作**：需要同时预览来自不同摄像机（作为 MediaSource）的输入，并将合成画面输出到物理设备（作为 MediaOutput）。 → 使用 **Media Profile Editor** 来管理和预览所有媒体流。
-   你需要将 Unreal Engine 的 **实时渲染画面推流到外部平台**（如 OBS、vMix）： → 在 **Media Capture** 面板中配置捕获当前编辑器视口或游戏视口，并将其连接到相应的 MediaOutput。
-   你正在调试一个 **连接了 Blackmagic 或 AJA 采集卡** 的工作站，但不确定视频信号是否正确输入： → 使用 **Video Input** 面板实时查看采集卡捕获到的画面。
-   你正在为一个 **现场直播项目** 配置设备，需要确保所有摄像机和输出设备的时间码严格同步： → 在 **Media Profile Editor** 中查看和配置时间码与基因锁状态。
-   你需要从一个 **渲染目标（RenderTarget）** 捕获内容（如UI界面或特定视角）并录制为视频文件： → 在 **Media Capture** 面板中添加一个渲染目标捕获项。

## 蓝图用法

该插件主要提供编辑器脚本功能，而非运行时蓝图节点。核心节点集中在 `UMediaFrameworkCapturePanel` 和 `UMediaFrameworkCapturePanelBlueprintLibrary` 类中。

### 核心节点（编辑器脚本）

这些节点位于 `Editor Scripting | Media Capture` 分类下，用于通过蓝图脚本控制媒体捕获流程。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Media Capture Panel` | 获取媒体捕获面板的单例实例 | `UMediaFrameworkCapturePanelBlueprintLibrary` |
| `Start Capture` | 根据面板当前配置启动所有捕获 | `UMediaFrameworkCapturePanel` |
| `Stop Capture` | 停止当前正在进行的所有捕获 | `UMediaFrameworkCapturePanel` |
| `Add Viewport Capture` | 添加一个基于特定摄像机 Actor 的视口捕获项 | `UMediaFrameworkCapturePanel` |
| `Add Render Target Capture` | 添加一个基于渲染目标的捕获项 | `UMediaFrameworkCapturePanel` |
| `Set Current Viewport Capture` | 配置对当前活动视口的捕获 | `UMediaFrameworkCapturePanel` |
| `Empty Viewport Capture` / `Empty Render Target Capture` | 清除所有视口或渲染目标捕获项 | `UMediaFrameworkCapturePanel` |

### 使用示例（蓝图描述）

1.  **获取捕获面板**：拖拽 `Get Media Capture Panel` 节点，将其输出连接到一个局部变量。
2.  **添加摄像机捕获**：使用 `Add Viewport Capture` 节点。将上一步的输出连接到 `Target` 引脚。在 `Media Output` 引脚指定一个 `MediaOutput` 资产（例如 NDI 输出）。在 `Camera` 引脚指定一个场景中的摄像机 Actor。`Capture Options` 可配置分辨率等参数。
3.  **配置视口捕获**：使用 `Set Current Viewport Capture` 节点，可以捕获编辑器当前活动的视口或游戏视口。
4.  **启动捕获**：调用 `Start Capture` 节点。此时，指定的 `MediaOutput` 将开始接收来自指定摄像机或视口的画面。
5.  **停止捕获**：在需要时调用 `Stop Capture` 节点。

## C++ 用法

插件的核心功能在编辑器模块 (`MediaFrameworkUtilitiesEditor`) 中实现，用于扩展编辑器界面。其底层数据和管理主要依赖 `MediaProfile` 和 `MediaFrameworkWorldSettingsAssetUserData` 类。

### 头文件引入

```cpp
#include "MediaProfile.h"
#include "MediaFrameworkWorldSettingsAssetUserData.h"
```

### 基本用法

以下代码展示了如何访问和遍历当前激活的媒体配置文件（MediaProfile）中的媒体源和输出。这在编写自定义工具或检查场景配置时很有用。

```cpp
// 假设 UMediaProfile* CurrentProfile 是一个有效的媒体配置文件指针

// 获取配置的媒体源数量
int32 NumSources = CurrentProfile->NumMediaSources();

// 遍历并打印每个媒体源的标签
for (int32 i = 0; i < NumSources; ++i)
{
    UMediaSource* Source = CurrentProfile->GetMediaSource(i);
    FString Label = CurrentProfile->GetLabelForMediaSource(i);
    UE_LOG(LogTemp, Log, TEXT("媒体源 %d: %s - %s"), i, *Label, Source ? *Source->GetName() : TEXT("无"));
}

// 类似地处理媒体输出
int32 NumOutputs = CurrentProfile->NumMediaOutputs();
for (int32 i = 0; i < NumOutputs; ++i)
{
    UMediaOutput* Output = CurrentProfile->GetMediaOutput(i);
    FString Label = CurrentProfile->GetLabelForMediaOutput(i);
    UE_LOG(LogTemp, Log, TEXT("媒体输出 %d: %s - %s"), i, *Label, Output ? *Output->GetName() : TEXT("无"));
}
```

### 进阶用法

插件使用 `UMediaFrameworkWorldSettingsAssetUserData`（附加在 `WorldSettings` Actor 上）来存储与关卡相关的捕获设置。你可以通过它编程控制渲染目标捕获。

```cpp
#include "MediaFrameworkWorldSettingsAssetUserData.h"

// 获取或创建当前关卡的媒体框架资产用户数据
UWorld* World = GEditor->GetEditorWorldContext().World();
AWorldSettings* WorldSettings = World->GetWorldSettings();
UMediaFrameworkWorldSettingsAssetUserData* UserData = WorldSettings->GetAssetUserData<UMediaFrameworkWorldSettingsAssetUserData>();

if (!UserData)
{
    UserData = NewObject<UMediaFrameworkWorldSettingsAssetUserData>(WorldSettings);
    WorldSettings->AddAssetUserData(UserData);
}

// 添加一个渲染目标捕获配置
FMediaFrameworkCaptureRenderTargetCameraOutputInfo CaptureInfo;
CaptureInfo.RenderTarget = MyRenderTarget2D; // 你的UTextureRenderTarget2D*
CaptureInfo.MediaOutput = MyMediaOutput; // 你的UMediaOutput*
CaptureInfo.CaptureOptions = FMediaCaptureOptions(); // 使用默认选项

UserData->RenderTargetCaptures.Add(CaptureInfo);

// 保存更改，以使捕获面板能读取到新配置
UserData->Modify();
```

## Demo 示例

一个最小化的示例，展示如何通过 C++ 代码在编辑器工具中与媒体捕获面板交互。

### MyMediaCaptureHelper.h
```cpp
#pragma once

#include "CoreMinimal.h"

class UMediaOutput;
class UTextureRenderTarget2D;

class FMyMediaCaptureHelper
{
public:
    /** 将一个渲染目标捕获项添加到编辑器的媒体捕获面板中 */
    static void AddRenderTargetToCapturePanel(UMediaOutput* InMediaOutput, UTextureRenderTarget2D* InRenderTarget);
};
```

### MyMediaCaptureHelper.cpp
```cpp
#include "MyMediaCaptureHelper.h"

#include "MediaFrameworkCapturePanelBlueprintLibrary.h"
#include "MediaOutput.h"
#include "Engine/TextureRenderTarget2D.h"

void FMyMediaCaptureHelper::AddRenderTargetToCapturePanel(UMediaOutput* InMediaOutput, UTextureRenderTarget2D* InRenderTarget)
{
    // 检查指针有效性
    if (!InMediaOutput || !InRenderTarget)
    {
        UE_LOG(LogTemp, Warning, TEXT("MyMediaCaptureHelper: MediaOutput 或 RenderTarget 无效。"));
        return;
    }

    // 获取媒体捕获面板单例
    UMediaFrameworkCapturePanel* CapturePanel = UMediaFrameworkCapturePanelBlueprintLibrary::GetMediaCapturePanel();
    if (CapturePanel)
    {
        // 清除现有的渲染目标捕获（可选）
        CapturePanel->EmptyRenderTargetCapture();

        // 添加新的捕获配置
        FMediaCaptureOptions Options;
        Options.bAutoRestartCaptureOnChange = true; // 配置更改时自动重启
        CapturePanel->AddRenderTargetCapture(InMediaOutput, InRenderTarget, Options);

        UE_LOG(LogTemp, Log, TEXT("MyMediaCaptureHelper: 已将渲染目标 '%s' 捕获添加到 MediaOutput '%s'。"),
            *InRenderTarget->GetName(), *InMediaOutput->GetName());
    }
}
```

## 模块依赖

使用此插件（特别是其编辑器功能）的模块通常不需要直接依赖它，因为其功能主要通过编辑器界面和蓝图脚本访问。但如果需要编写扩展或访问其底层类型，你可能会依赖以下模块：

| 模块 | 用途 |
|---|---|
| `MediaFrameworkUtilities` | 访问 `MediaProfile`, `MediaFrameworkWorldSettingsAssetUserData` 等核心数据类型。 |
| `MediaFrameworkUtilitiesEditor` | 访问编辑器面板、捕获逻辑和自定义资产编辑器，仅在编辑器模块中使用。 |

*注：大部分情况下，通过 `AddOnScreenDebugMessage` 或编辑器脚本使用插件功能时，无需在 Build.cs 中手动添加依赖。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `36c08694` | Media IO - Populate Media Configuration when using auto for Blackmagic and Aja cards | 媒体IO：为Blackmagic和AJA采集卡在使用自动配置时填充媒体设置。 |
| 2026-05-22 | `7d256b73` | [Media] Add shared Media category to the Level Editor Window menu | 媒体：在关卡编辑器窗口菜单中添加共享的“媒体”类别。 |
| 2026-05-21 | `ff9996e8` | Media Profile: Fixed issue where ElectraProtron issue would not play a new video after it had alread | 媒体配置文件：修复了ElectraProtron插件在已经播放后无法播放新视频的问题。 |
| 2026-05-20 | `54cbb9f8` | Ensure a transient MediaProfile always exists from startup | 确保在启动时始终存在一个临时的媒体配置文件。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口：通过在客户端关联或解除关联时进行通知，来整合必要的代码片段。 |

### 维护评价

该插件自 2018 年创建，是一个 **成熟的、处于活跃维护状态** 的插件。

-   **年龄**：已存在约 8 年，是一个经历了多个引擎版本迭代的 **老古董** 级别组件。
-   **近期活跃度**：在 2026 年 5 月有多次提交，内容包括功能增强（为特定硬件自动配置）、UI改进（菜单分类）、Bug修复（播放新视频的问题）和稳定性改进（确保临时配置文件存在）。这表明插件仍在被 Epic Games 主动维护和更新。
-   **功能状态**：功能非常完备且专业，主要面向媒体和广播领域。其 UI 和功能经过多次迭代，已经相当稳定。
-   **推荐使用**：如果你的项目涉及任何非平凡的媒体输入/输出、视频捕获、虚拟制作或广播集成，**强烈推荐启用此插件**。它是连接 Unreal Engine 内部渲染与外部媒体世界的桥梁，能极大提升工作流效率。对于纯游戏项目，如果不需要编辑器内的高级媒体管理，可以保持禁用状态。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaFrameworkUtilities)
-   [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/media-framework-in-unreal-engine)（UE 通用媒体框架文档，此插件是其重要组成部分）