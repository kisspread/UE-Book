# Capture Manager Editor

> The Capture Manager Editor plugin is used for importing the Capture archive data into UE/UEFN to create necessary assets

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器设置、UI 自定义） |
| 模块 | `CaptureManagerEditorSettings` (Editor), `LiveLinkHubWorkerManager` (Editor), `LiveLinkHubExportServer` (Editor), `DataIngestCoreEditor` (Editor), `LiveLinkHubDiscoveryEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor) | |

## 用途

Capture Manager Editor 是 Unreal Engine 虚拟制作管线中负责**数据导入（Ingest）**的编辑器端组件。它解决的核心问题是：将 Live Link Hub 采集到的面部/身体捕捉数据（视频序列、音频、深度图、相机标定数据）从远端设备传输到 UE 编辑器内，并自动创建对应的资产（`UFootageCaptureData`、`UImgMediaSource`、`USoundWave`、`UCameraCalibration` 等）。

整个数据流为：**Live Link Hub（采集端）→ TCP 网络传输 → Capture Manager Editor（编辑器端接收/解析/创建资产）**。

该插件是 Capture Manager 大型插件包中的**编辑器子插件**，仅在编辑器环境下加载。它依赖 `CaptureManagerCore`（运行时协议栈）和 `LiveLinkHub`（消息通信框架），是连接远端采集设备与编辑器资产系统的桥梁。

## 使用场景

- 你在使用 Live Link Hub 进行 MetaHuman 面部捕捉，需要将采集的视频/音频自动导入 UE 并创建 CaptureData 资产 → 启用本插件
- 你需要从远端设备接收相机标定数据并自动创建 LensFile 和 CameraCalibration 资产 → 本插件处理完整的标定数据导入流程
- 你需要自定义导入资产的命名规则（如按 slate、take number、设备名等模板化命名）→ 使用 `UCaptureManagerEditorSettings` 的 Naming Tokens 系统
- 你运行 UEFN（Unreal Editor for Fortnite）环境，需要将捕捉数据导入到 Fortnite 项目 → 本插件同时支持 UE 和 UEFN 路径

## 蓝图用法

本插件没有暴露 `BlueprintCallable` 函数——它是纯编辑器内部的导入管线，通过 Live Link Hub 的消息系统自动触发。用户通过 **Editor Preferences → Capture Manager** 设置面板配置导入行为，无需手动蓝图调用。

### 核心设置面板

在 Editor Preferences 中找到 **Capture Manager** 分类，可配置：

| 设置项 | 说明 |
|---|---|
| `MediaDirectory` | 从远端下载的媒体文件存储路径（支持命名 Token 模板） |
| `ImportDirectory` | Content Browser 中资产创建的目标路径 |
| `bAutoSaveAssets` | 导入完成后是否自动保存资产（默认 true） |
| `CaptureDataAssetName` | CaptureData 资产的命名模板 |
| `ImageSequenceAssetName` | 图像序列资产命名模板 |
| `DepthSequenceAssetName` | 深度序列资产命名模板 |
| `SoundwaveAssetName` | 音频资产命名模板 |
| `CalibrationAssetName` | 标定数据资产命名模板 |
| `LensFileAssetName` | Lens File 资产命名模板 |
| `bLaunchIngestServerOnLiveLinkHubConnection` | 连接 Live Link Hub 时自动启动 Ingest Server |
| `IngestServerPort` | Ingest Server 监听端口（0 = 自动选择） |

### 命名 Token 系统

插件通过 `NamingTokens` 框架支持模板化命名，可用 Token 包括：

| Token 类别 | 可用 Token | 说明 |
|---|---|---|
| General | `{id}`, `{device}`, `{slate}`, `{take}` | 上传 ID、设备名、场次号、条次号 |
| Video | `{name}`, `{frameRate}` | 视频名称、帧率 |
| Audio | `{name}` | 音频名称 |
| Calibration | `{name}` | 标定名称 |
| LensFile | `{cameraName}` | 相机名称 |

## C++ 用法

### 头文件引入

```cpp
#include "Settings/CaptureManagerEditorSettings.h"
#include "IngestAssetCreator.h"
#include "LiveLinkHubExportServer.h"
#include "LiveLinkHubWorkerManager.h"
```

### 基本用法：读取编辑器设置

```cpp
// 获取 Capture Manager 编辑器设置（单例）
const UCaptureManagerEditorSettings* Settings = GetDefault<UCaptureManagerEditorSettings>();

// 获取各类型的命名 Token
TObjectPtr<const UCaptureManagerIngestNamingTokens> GeneralTokens = Settings->GetGeneralNamingTokens();
TObjectPtr<const UCaptureManagerVideoNamingTokens> VideoTokens = Settings->GetVideoNamingTokens();
TObjectPtr<const UCaptureManagerAudioNamingTokens> AudioTokens = Settings->GetAudioNamingTokens();

// 获取导入目录
FString ImportDir = Settings->GetVerifiedImportDirectory();

// 检查是否自动保存
bool bAutoSave = Settings->bAutoSaveAssets;
```

**来源**: `CaptureManagerEditorSettings/Public/Settings/CaptureManagerEditorSettings.h`

### 进阶用法：手动创建捕获资产

```cpp
using namespace UE::CaptureManager;

// 准备资产创建数据
FCreateAssetsData AssetData;
AssetData.CaptureDataAssetName = TEXT("MyCapture");
AssetData.TakeId = 0;
AssetData.PackagePath = TEXT("/Game/Captures/MyTake");

// 添加图像序列
FCreateAssetsData::FImageSequenceData ImageSeq;
ImageSeq.AssetName = TEXT("Video_01");
ImageSeq.Name = TEXT("main");
ImageSeq.SequenceDirectory = TEXT("/path/to/image/sequence");
ImageSeq.FrameRate = FFrameRate(30, 1);
ImageSeq.bTimecodePresent = true;
ImageSeq.Timecode = FTimecode(1, 0, 0, 0, false);
ImageSeq.TimecodeRate = FFrameRate(30, 1);
AssetData.ImageSequences.Add(ImageSeq);

// 添加音频
FCreateAssetsData::FAudioData AudioData;
AudioData.AssetName = TEXT("Audio_01");
AudioData.Name = TEXT("mic");
AudioData.WAVFile = TEXT("/path/to/audio.wav");
AssetData.AudioClips.Add(AudioData);

// 在 Game Thread 上创建资产
TArray<FCreateAssetsData> AssetDataList;
AssetDataList.Add(AssetData);

FIngestAssetCreator::FPerTakeCallback Callback;
// ... 设置回调 ...

TArray<FCaptureDataAssetInfo> Results = 
    FIngestAssetCreator::CreateAssets_GameThread(AssetDataList, Callback);

// 获取创建的资产
for (const FCaptureDataAssetInfo& Info : Results)
{
    for (const FCaptureDataAssetInfo::FImageSequence& Seq : Info.ImageSequences)
    {
        UImgMediaSource* Asset = Seq.Asset;
        // 使用资产...
    }
}
```

**来源**: `DataIngestCoreEditor/Public/IngestAssetCreator.h`

### 进阶用法：启动 Export Server

```cpp
// 获取 Export Server 模块
FLiveLinkHubExportServerModule& Module = 
    FModuleManager::LoadModuleChecked<FLiveLinkHubExportServerModule>("LiveLinkHubExportServer");

// 启动服务器（自动分配端口）
Module.StartExportServer(0);

// 获取服务器信息
auto ServerInfo = Module.GetExportServerInfo();
if (ServerInfo.HasValue())
{
    FString IP = ServerInfo.GetValue().IPAddress;
    uint16 Port = ServerInfo.GetValue().Port;
}

// 注册文件下载处理器
Module.RegisterExportServerHandler(
    ClientId.ToString(),
    FLiveLinkHubExportServer::FFileDataHandler::CreateLambda(
        [](FUploadDataHeader Header, TSharedPtr<FTcpClientHandler> Client) -> bool
        {
            // 处理接收到的文件数据
            return true;
        })
);
```

**来源**: `LiveLinkHubExportServer/Public/LiveLinkHubExportServerModule.h`

## Demo 示例

### 最小集成：监听 Live Link Hub 连接并自动导入

```cpp
// MyIngestHandler.h
#pragma once

#include "CoreMinimal.h"
#include "LiveLinkHubWorkerManagerModule.h"

class FMyIngestHandler
{
public:
    void Init()
    {
        // WorkerManager 在模块启动时自动创建
        // 它会自动处理来自 Live Link Hub 的连接请求
        // 并在接收到数据时自动调用 IngestCaptureDataProcess
        // 创建资产并可选地自动保存
    }
};
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "CaptureUtils"
});

PrivateDependencyModuleNames.AddRange(new string[]
{
    "CaptureManagerEditorSettings",
    "DataIngestCoreEditor",
    "LiveLinkHubExportServer",
    "LiveLinkHubWorkerManager"
});
```

注意：由于所有模块都是 Editor 类型，你的模块也必须是 Editor 类型才能依赖它们。

## 模块依赖

以下是使用者需要依赖的公共模块（从各 Build.cs 的 `PublicDependencyModuleNames` 提取）：

| 模块 | 用途 |
|---|---|
| `CaptureUtils` | 捕获工具函数（所有子模块都依赖） |
| `CaptureDataCore` | CaptureData 资产类型定义 |
| `CaptureDataEditor` | CaptureData 编辑器集成 |
| `CaptureDataUtils` | CaptureData 工具函数 |
| `DataIngestCore` | 数据导入核心（运行时部分） |
| `LiveLinkHubCaptureMessaging` | Live Link Hub 消息协议定义 |
| `LiveLinkHubMessaging` | Live Link Hub 消息框架 |
| `NamingTokens` | 命名 Token 模板系统 |
| `CaptureManagerEditorSettings` | 编辑器设置（单例访问） |
| `CameraCalibrationCore` | 相机标定数据类型 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-10-03 | `747b2230a6fa` | Capture Manager - Remove unsafe access to "this" ptr when modules are unloading | 安全修复：修复模块卸载时的悬空 this 指针问题 |
| 2025-10-03 | `a7fe5bca1c4b` | [CaptureManager] Add camera id to ingested asset metadata | 功能更新：在导入的资产元数据中添加相机 ID |
| 2025-09-23 | `f207c623330f` | [MetaHuman] Fixed a couple of garbage collection issues during ingest | Bug 修复：修复导入过程中的垃圾回收问题 |

### 维护评价

- **创建时间**: 2025 年 2 月，约 1 年历史，是较新的插件
- **更新频率**: 2025 年 9-10 月有密集更新，包括功能添加和稳定性修复
- **维护状态**: **活跃维护** — 作为 Virtual Production 管线的核心组件，Epic 持续投入
- **已知限制**:
  - `EnabledByDefault=false`，需要手动在插件列表中启用
  - 所有模块均为 Editor 类型，不可在打包版本中使用
  - 依赖 `LiveLinkHub` 插件，需要 Live Link Hub 应用配合使用
- **推荐使用**: 如果你在做 MetaHuman 捕捉工作流，这是必须启用的插件。它是 Live Link Hub 与 UE 编辑器之间的标准数据导入通道。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor)
- [Capture Manager Core（运行时依赖）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore)
- [Capture Manager App（应用层模块）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp)
- [Capture Manager Devices（设备模块）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerDevices)
