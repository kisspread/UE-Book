# MetaHuman Live Link

> Live Link sources and associated utilities for streaming real time MetaHuman animation data.

| 属性 | 值 |
|---|---|
| 中文名 | 元人实时链接 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具） |
| 模块 | `LiveLinkFaceDiscovery` (Runtime), `LiveLinkFaceSource` (Runtime), `LiveLinkFaceSourceEditor` (Runtime), `MetaHumanLiveLinkSource` (Runtime), `MetaHumanLiveLinkSourceEditor` (Runtime), `MetaHumanLocalLiveLinkSource` (Runtime), `MetaHumanLocalLiveLinkSourceEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanLiveLink) | |

## 用途

MetaHuman Live Link 插件为 Unreal Engine 提供了通过 Live Link 协议实时驱动 MetaHuman 角色面部动画的能力。它解决的核心问题是：如何将外部设备（如网络摄像头、麦克风、专业面部捕捉设备）捕获的实时面部表情和音频数据，无缝地流式传输到 UE5 中的 MetaHuman 角色上，实现低延迟的实时动画驱动。

该插件包含多个子模块，主要功能包括：
1.  **设备发现与接入**：`LiveLinkFaceDiscovery` 和 `LiveLinkFaceSource` 模块负责发现并连接 MetaHuman 应用程序或兼容的捕捉设备。
2.  **本地实时处理**：`MetaHumanLocalLiveLinkSource` 是核心模块，它接收来自摄像头或麦克风的音视频流，运行 MetaHuman 的实时动画解算管线（Hyprsense， Speech-to-Anim），并生成 Live Link 面部动画数据。
3.  **编辑器集成与设置**：配套的 `*Editor` 模块提供了在 Unreal Editor 中创建、管理和监控 Live Link 源和主题的 UI 工具。

## 使用场景

*   你需要在虚幻引擎中实时驱动一个 MetaHuman 角色的面部表情，数据来源是普通网络摄像头 → 使用 `MetaHumanLocalLiveLinkSource` 的 **视频** 功能。
*   你希望仅通过麦克风输入，实时驱动 MetaHuman 角色的口型和面部表情（语音驱动动画） → 使用 `MetaHumanLocalLiveLinkSource` 的 **音频** 功能。
*   你正在使用 MetaHuman 的 iOS 应用程序进行面部捕捉，并想将数据实时传输到 UE5 中 → 使用 `LiveLinkFaceSource`。
*   你需要为虚拟主播、实时表演捕捉或需要实时反馈的影视预览制作搭建系统 → 本插件是关键的基础组件。

## 蓝图用法

主要蓝图功能集中在 `UMetaHumanLocalLiveLinkSourceBlueprint` 中，它是一个静态函数库，提供了设备发现、格式查询和主题创建的完整工作流。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Video Devices` | 获取所有可用的视频捕获设备列表。 | `UMetaHumanLocalLiveLinkSourceBlueprint` |
| `Get Audio Devices` | 获取所有可用的音频捕获设备列表。 | `UMetaHumanLocalLiveLinkSourceBlueprint` |
| `Get Video Tracks` | 获取指定视频设备的所有可用视频轨道。 | `UMetaHumanLocalLiveLinkSourceBlueprint` |
| `Get Video Formats` | 获取指定视频轨道的所有可用分辨率/帧率格式。 | `UMetaHumanLocalLiveLinkSourceBlueprint` |
| `Create Video Source` | 创建一个 MetaHuman 视频类型的 Live Link 源。 | `UMetaHumanLocalLiveLinkSourceBlueprint` |
| `Create Video Subject` | 在源上创建一个视频主题，并开始处理指定格式的视频流。 | `UMetaHumanLocalLiveLinkSourceBlueprint` |
| `Get Subject Settings` | 获取某个 Live Link 主题关联的设置对象（用于调整参数）。 | `UMetaHumanLocalLiveLinkSourceBlueprint` |
| `Set Head Orientation` | 启用或禁用头部朝向输出（在主题设置中）。 | `UMetaHumanVideoBaseLiveLinkSubjectSettings` |
| `Set Head Translation` | 启用或禁用头部位移输出（在主题设置中）。 | `UMetaHumanVideoBaseLiveLinkSubjectSettings` |
| `Set Monitor Image` | 设置用于调试的监控图像类型（无、原始图像、跟踪标记图像）。 | `UMetaHumanVideoBaseLiveLinkSubjectSettings` |

### 使用示例（蓝图描述）

一个典型的蓝图工作流如下：
1.  调用 `Get Video Devices` 获取摄像头列表。
2.  对于选中的设备，调用 `Get Video Tracks` 获取其轨道（通常只有一个）。
3.  对于该轨道，调用 `Get Video Formats` 获取支持的分辨率列表（如 1920x1080 @ 30fps）。
4.  调用 `Create Video Source` 创建一个 Live Link 源。
5.  使用上一步获取的源句柄和选中的视频格式，调用 `Create Video Subject` 并指定一个主题名称（如 `MyWebCam`）。
6.  （可选）通过 `Get Subject Settings` 获取设置对象，然后使用 `Set Head Orientation`、`Set Monitor Image` 等节点调整动画解算参数。
7.  将创建的 `FLiveLinkSubjectKey` 连接到 MetaHuman 角色上的 `Live Link Transform` 或 `Control Rig` 节点，即可实现实时驱动。

## C++ 用法

### 头文件引入

```cpp
#include “MetaHumanLocalLiveLinkSourceBlueprint.h”
#include “MetaHumanVideoBaseLiveLinkSubjectSettings.h”
#include “MetaHumanLocalLiveLinkSubjectSettings.h”
```

### 基本用法

以下代码演示了如何在 C++ 中发现设备并创建一个视频主题。这是基于 `UMetaHumanLocalLiveLinkSourceBlueprint` 中函数的封装。

```cpp
// 来源：基于 MetaHumanLocalLiveLinkSourceBlueprint.h 中的静态函数 API
#include “MetaHumanLocalLiveLinkSourceBlueprint.h”

void CreateMyMetaHumanLiveLink()
{
    // 1. 发现视频设备
    TArray<FMetaHumanLiveLinkVideoDevice> VideoDevices;
    UMetaHumanLocalLiveLinkSourceBlueprint::GetVideoDevices(VideoDevices, true);

    if (VideoDevices.Num() == 0)
    {
        UE_LOG(LogTemp, Warning, TEXT(“No video devices found.”));
        return;
    }

    // 2. 获取第一个设备的轨道
    const FMetaHumanLiveLinkVideoDevice& SelectedDevice = VideoDevices[0];
    TArray<FMetaHumanLiveLinkVideoTrack> VideoTracks;
    bool bTimedOut = false;
    UMetaHumanLocalLiveLinkSourceBlueprint::GetVideoTracks(SelectedDevice, VideoTracks, bTimedOut, 5.0f);

    if (VideoTracks.Num() == 0 || bTimedOut)
    {
        UE_LOG(LogTemp, Warning, TEXT(“No video tracks found for device %s.”), *SelectedDevice.Name);
        return;
    }

    // 3. 获取第一个轨道的格式
    const FMetaHumanLiveLinkVideoTrack& SelectedTrack = VideoTracks[0];
    TArray<FMetaHumanLiveLinkVideoFormat> VideoFormats;
    UMetaHumanLocalLiveLinkSourceBlueprint::GetVideoFormats(SelectedTrack, VideoFormats, bTimedOut, true, 5.0f);

    if (VideoFormats.Num() == 0 || bTimedOut)
    {
        UE_LOG(LogTemp, Warning, TEXT(“No video formats found for track %s.”), *SelectedTrack.Name);
        return;
    }

    // 4. 创建源和主题
    FLiveLinkSourceHandle SourceHandle;
    UMetaHumanLocalLiveLinkSourceBlueprint::CreateVideoSource(SourceHandle, bTimedOut);
    if (!bTimedOut)
    {
        FLiveLinkSubjectKey SubjectKey;
        UMetaHumanLocalLiveLinkSourceBlueprint::CreateVideoSubject(
            SourceHandle,
            VideoFormats[0], // 选择第一个格式
            “MyCppWebCam”,
            SubjectKey,
            bTimedOut,
            5.0f, // StartTimeout
            0.1f, // FormatWaitTime
            5.0f  // SampleTimeout
        );
        if (!bTimedOut)
        {
            UE_LOG(LogTemp, Log, TEXT(“Successfully created Live Link subject: %s”), *SubjectKey.SubjectName.ToString());
        }
    }
}
```

### 进阶用法

创建主题后，获取并修改其设置参数。

```cpp
// 来源：基于 MetaHumanVideoBaseLiveLinkSubjectSettings.h 中的 UPROPERTY 和 UFUNCTION
#include “MetaHumanVideoBaseLiveLinkSubjectSettings.h”
#include “MetaHumanLocalLiveLinkSourceBlueprint.h”

void ConfigureMetaHumanLiveLinkSubject(const FLiveLinkSubjectKey& SubjectKey)
{
    UObject* SettingsObject = nullptr;
    UMetaHumanLocalLiveLinkSourceBlueprint::GetSubjectSettings(SubjectKey, SettingsObject);

    if (UMetaHumanVideoBaseLiveLinkSubjectSettings* VideoSettings = Cast<UMetaHumanVideoBaseLiveLinkSubjectSettings>(SettingsObject))
    {
        // 禁用头部位移输出，仅使用面部动画
        VideoSettings->SetHeadTranslation(false);

        // 启用带有跟踪标记的监控视图用于调试
        VideoSettings->SetMonitorImage(EHyprsenseRealtimeNodeDebugImage::Trackers);

        // 根据摄像头安装方向调整图像旋转
        VideoSettings->SetRotation(EMetaHumanVideoRotation::Ninety);
    }
}
```

## Demo 示例

一个最小化的 C++ 类，用于启动时自动创建 MetaHuman 视频 Live Link 主题。

```cpp
// MetaHumanLiveLinkDemo.h
#pragma once

#include “CoreMinimal.h”
#include “Subsystems/GameInstanceSubsystem.h”
#include “MetaHumanLiveLinkDemo.generated.h”

UCLASS()
class UMetaHumanLiveLinkDemoSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

private:
    FLiveLinkSourceHandle VideoSourceHandle;
    FLiveLinkSubjectKey VideoSubjectKey;
};
```

```cpp
// MetaHumanLiveLinkDemo.cpp
#include “MetaHumanLiveLinkDemo.h”
#include “MetaHumanLocalLiveLinkSourceBlueprint.h”

void UMetaHumanLiveLinkDemoSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    // 创建视频源和主题
    bool bSuccess = false;
    UMetaHumanLocalLiveLinkSourceBlueprint::CreateVideoSource(VideoSourceHandle, bSuccess);

    if (bSuccess)
    {
        // 使用默认/第一个找到的视频格式
        TArray<FMetaHumanLiveLinkVideoDevice> Devices;
        UMetaHumanLocalLiveLinkSourceBlueprint::GetVideoDevices(Devices, true);

        if (Devices.Num() > 0)
        {
            TArray<FMetaHumanLiveLinkVideoTrack> Tracks;
            bool bTimedOut;
            UMetaHumanLocalLiveLinkSourceBlueprint::GetVideoTracks(Devices[0], Tracks, bTimedOut);

            if (Tracks.Num() > 0 && !bTimedOut)
            {
                TArray<FMetaHumanLiveLinkVideoFormat> Formats;
                UMetaHumanLocalLiveLinkSourceBlueprint::GetVideoFormats(Tracks[0], Formats, bTimedOut);

                if (Formats.Num() > 0 && !bTimedOut)
                {
                    UMetaHumanLocalLiveLinkSourceBlueprint::CreateVideoSubject(
                        VideoSourceHandle,
                        Formats[0],
                        “AutoDemoSubject”,
                        VideoSubjectKey,
                        bSuccess
                    );
                }
            }
        }
    }

    if (!bSuccess)
    {
        UE_LOG(LogTemp, Error, TEXT(“Failed to initialize MetaHuman Live Link Demo.”));
    }
}

void UMetaHumanLiveLinkDemoSubsystem::Deinitialize()
{
    // 清理（在实际项目中，可能需要更优雅地关闭源和主题）
    VideoSourceHandle = FLiveLinkSourceHandle();
    VideoSubjectKey = FLiveLinkSubjectKey();
    Super::Deinitialize();
}
```

## 模块依赖

`MetaHumanLocalLiveLinkSource` 模块除了标准依赖外，还依赖以下模块以支持其编辑器功能：

| 模块 | 用途 |
|---|---|
| `EditorWidgets` | 提供编辑器内的复合控件（SCompoundWidget）支持。 |
| `UnrealEd` | 提供编辑器核心功能，如属性编辑（PostEditChangeProperty）。 |
| `PropertyEditor` | 用于自定义属性的编辑器 UI 逻辑。 |

其他模块（如 `LiveLinkFaceDiscovery`, `LiveLinkFaceSource`）的依赖通常也是 Live Link、Media 框架相关的标准模块，无特殊依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `9bee2cb0` | [MHA] Expose detection thresholds for body | 暴露身体检测阈值参数，增强身体动画控制。 |
| 2026-05-14 | `988b3911` | [MHA] Face animation sequence export changes for combined solve | 为组合解算优化面动画序列导出功能。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下 double 常量截断为 float 产生警告的代码。 |
| 2026-05-12 | `8bf9ba92` | [MetaHumanLiveLink] Use AvfMedia for FileMediaSource bundles on Apple platforms | 在 Apple 平台上为文件媒体源包启用 AvfMedia 后端，改善兼容性。 |
| 2026-05-12 | `fa06fada` | New ADA model | 集成新的 ADA 模型，可能提升动画质量或性能。 |

### 维护评价

**活跃维护**。插件创建于 2025 年 2 月，至今约一年半，属于较新的插件。从近期提交记录（截至 2026 年 5 月）可以看出，该插件仍在被 Epic Games 积极开发和维护，更新频率高，内容涉及功能增强（暴露新参数、集成新模型）、平台兼容性改进（Apple 平台媒体支持）以及代码质量修复。

插件是 MetaHuman 工作流的关键组件，对于需要实时驱动 MetaHuman 的项目是**强烈推荐使用**的官方解决方案。由于其更新活跃且属于 Epic 核心功能，可以预期它会随着 MetaHuman 技术栈一同演进。主要限制可能与特定平台的媒体后端支持或硬件兼容性有关。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanLiveLink)
- [官方文档](https://docs.unrealengine.com/)（插件描述中的 DocsURL 为空，请查阅 Unreal Engine 官方 MetaHuman 文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanLiveLink/Tests)（如果存在）