# Capture Manager Editor

> The Capture Manager Editor plugin is used for importing the Capture archive data into UE/UEFN to create necessary assets

| 属性 | 值 |
|---|---|
| 中文名 | 捕获管理器编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（设置资产、命名令牌） |
| 模块 | `CaptureManagerDeviceBlueprint` (Runtime), `CaptureManagerEditorSettings` (Runtime), `CaptureManagerIngestBlueprint` (Runtime), `DataIngestCoreEditor` (Runtime), `LiveLinkHubDiscoveryEditor` (Runtime), `LiveLinkHubExportServer` (Runtime), `LiveLinkHubWorkerManager` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor) | |

## 用途

Capture Manager Editor 是虚拟制作流程中的**采集数据导入管线**，负责将外部设备拍摄的 Capture 档案（视频序列、音频、标定数据、镜头文件）导入到 UE 或 UEFN（Unreal Editor for Fortnite）中，生成引擎可直接使用的资产（ImageMediaSource、SoundWave、CameraCalibration、LensFile 等）。

核心解决的问题：
- **资产命名标准化**：通过命名令牌（Naming Tokens）系统，为导入的每类资产提供可配置的命名模板
- **导入路径管理**：区分原始媒体存储路径（MediaDirectory）和引擎资产输出路径（ImportDirectory），并确保 ImportDirectory 位于合法的 Content 子目录
- **并发导入控制**：限制同时运行的 Ingest 任务数量（默认 2，最大 8），平衡 I/O 吞吐和系统压力
- **第三方编码器集成**：可选启用外部编码器替代引擎内置的媒体读写器，支持自定义命令行参数
- **Live Link Hub 联动**：在检测到 Live Link Hub 连接时自动启动 Ingest Server，实现远程采集设备到引擎的自动化数据流

## 使用场景

- 你有一套基于 Live Link Hub 的多机位虚拟拍摄系统 → 用此插件管理拍摄数据的自动导入和资产生成
- 你需要将 MetaHuman 或体积视频拍摄的标定数据导入引擎 → 配置 MediaDirectory 和 ImportDirectory，利用命名令牌模板控制资产命名
- 你的录制环境使用 FFmpeg 等外部编码器 → 启用第三方编码器路径和自定义命令行参数
- 你希望在 UEFN 中使用 Capture 数据 → ImportDirectory 支持 `/VerseDevices` 等 UEFN 内容根路径

## 蓝图用法

以下节点来自 `UCaptureManagerEditorSettings` 类，在 `Capture Manager|Settings` 分类下可用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetCaptureManagerEditorSettings` | 获取 Capture Manager Editor 设置单例（BlueprintPure） | `UCaptureManagerEditorSettings` |
| `SetMediaDirectory` | 设置原始媒体数据的存储目录 | `UCaptureManagerEditorSettings` |
| `SetImportDirectory` | 设置导入资产的目标 Content 目录（必须是有效的 UE 包路径） | `UCaptureManagerEditorSettings` |

### 关键配置属性

| 属性 | 类型 | 分类 | 说明 |
|---|---|---|---|
| `MediaDirectory` | `FDirectoryPath` | Import | 原始采集媒体的存储位置 |
| `ImportDirectory` | `FDirectoryPath` | Import | 导入资产在 Content Browser 中的目标位置 |
| `bAutoSaveAssets` | `bool` | Import | Ingest 完成后是否自动保存资产（默认 true） |
| `CaptureDataAssetName` | `FString` | Import | Capture Data 资产的命名模板 |
| `ImageSequenceAssetName` | `FString` | Import\Video | 图像序列资产命名模板 |
| `DepthSequenceAssetName` | `FString` | Import\Video | 深度序列资产命名模板 |
| `SoundwaveAssetName` | `FString` | Import\Audio | SoundWave 资产命名模板 |
| `CalibrationAssetName` | `FString` | Import\Calibration | 相机标定资产命名模板 |
| `LensFileAssetName` | `FString` | Import\Calibration | 镜头文件资产命名模板 |
| `MaxConcurrentIngests` | `int32` | Conversion | 最大并发 Ingest 任务数（1-8，默认 2） |
| `bEnableThirdPartyEncoder` | `bool` | Conversion | 是否启用第三方编码器 |
| `ThirdPartyEncoder` | `FFilePath` | Conversion | 第三方编码器可执行文件路径 |
| `CustomVideoCommandArguments` | `FString` | Conversion | 自定义视频编码命令行参数 |
| `CustomAudioCommandArguments` | `FString` | Conversion | 自定义音频编码命令行参数 |
| `bLaunchIngestServerOnLiveLinkHubConnection` | `bool` | Ingest Server | LLH 连接时自动启动 Ingest Server（默认 true） |
| `IngestServerPort` | `uint16` | Ingest Server | Ingest Server 监听端口（0 = 自动选择） |

### 命名令牌（Naming Tokens）

资产命名模板支持以下令牌类别，每类有独立的令牌上下文：

| 令牌类 | 对应属性 | 说明 |
|---|---|---|
| `UCaptureManagerIngestNamingTokens` | Import 属性 | 通用导入令牌 |
| `UCaptureManagerVideoNamingTokens` | Video 属性 | 视频相关令牌 |
| `UCaptureManagerAudioNamingTokens` | Audio 属性 | 音频相关令牌 |
| `UCaptureManagerCalibrationNamingTokens` | Calibration 属性 | 标定相关令牌 |
| `UCaptureManagerLensFileNamingTokens` | LensFile 属性 | 镜头文件相关令牌 |
| `UCaptureManagerVideoEncoderTokens` | 视频编码器参数 | 视频编码器令牌 |
| `UCaptureManagerAudioEncoderTokens` | 音频编码器参数 | 音频编码器令牌 |

### 使用示例（蓝图描述）

**获取设置并修改导入目录**：

1. 调用 `GetCaptureManagerEditorSettings` 获取设置对象
2. 拖出返回值引脚，调用 `SetMediaDirectory`，传入 `FDirectoryPath`（例如 `D:/CaptureData/Raw`）
3. 调用 `SetImportDirectory`，传入 Content Browser 路径（例如 `/Game/CaptureManager/Imports`）

**配置第三方编码器**：

在设置对象的属性面板中，勾选 `bEnableThirdPartyEncoder`，设置 `ThirdPartyEncoder` 指向 FFmpeg 等可执行文件路径，可选填自定义视频/音频命令行参数。

**监听设置变更**：

绑定 `OnCaptureManagerEditorSettingsChanged` 多播委托，在设置被修改时执行自定义逻辑（如刷新 UI）。

## C++ 用法

### 头文件引入

```cpp
#include "Settings/CaptureManagerEditorSettings.h"
```

### 基本用法

获取设置实例并读取配置项：

```cpp
// 获取 Capture Manager Editor 设置单例
UCaptureManagerEditorSettings* Settings = UCaptureManagerEditorSettings::GetCaptureManagerEditorSettings();
if (Settings)
{
    // 获取验证后的导入目录（自动修正不合法路径）
    FString ImportDir = Settings->GetVerifiedImportDirectory();
    
    // 获取媒体目录
    FString MediaDir = Settings->MediaDirectory.Path;
    
    // 读取最大并发 Ingest 数
    int32 MaxConcurrent = Settings->MaxConcurrentIngests;
    
    // 是否启用第三方编码器
    bool bUseExternalEncoder = Settings->bEnableThirdPartyEncoder;
}
```

*来源：Public/Settings/CaptureManagerEditorSettings.h*

### 进阶用法

**通过命名令牌获取资产名称**：

```cpp
UCaptureManagerEditorSettings* Settings = UCaptureManagerEditorSettings::GetCaptureManagerEditorSettings();
if (Settings)
{
    // 获取通用命名令牌实例
    TObjectPtr<const UCaptureManagerIngestNamingTokens> GeneralTokens = Settings->GetGeneralNamingTokens();
    
    // 获取视频命名令牌实例
    TObjectPtr<const UCaptureManagerVideoNamingTokens> VideoTokens = Settings->GetVideoNamingTokens();
    
    // 获取音频命名令牌实例
    TObjectPtr<const UCaptureManagerAudioNamingTokens> AudioTokens = Settings->GetAudioNamingTokens();
    
    // 获取标定命名令牌
    TObjectPtr<const UCaptureManagerCalibrationNamingTokens> CalibTokens = Settings->GetCalibrationNamingTokens();
    
    // 获取镜头文件命名令牌
    TObjectPtr<const UCaptureManagerLensFileNamingTokens> LensTokens = Settings->GetLensFileNamingTokens();
    
    // 获取编码器令牌
    TObjectPtr<const UCaptureManagerVideoEncoderTokens> VideoEncTokens = Settings->GetVideoEncoderNamingTokens();
    TObjectPtr<const UCaptureManagerAudioEncoderTokens> AudioEncTokens = Settings->GetAudioEncoderNamingTokens();
}
```

*来源：Public/Settings/CaptureManagerEditorSettings.h*

**监听设置变更**：

```cpp
#if WITH_EDITOR
UCaptureManagerEditorSettings* Settings = UCaptureManagerEditorSettings::GetCaptureManagerEditorSettings();
if (Settings)
{
    // 绑定设置变更委托
    Settings->OnCaptureManagerEditorSettingsChanged.AddDynamic(this, &UMyClass::OnSettingsChanged);
}
#endif
```

*来源：Public/Settings/CaptureManagerEditorSettings.h*

**在编辑器中设置导入目录**：

```cpp
#if WITH_EDITOR
UCaptureManagerEditorSettings* Settings = UCaptureManagerEditorSettings::GetCaptureManagerEditorSettings();
if (Settings)
{
    FDirectoryPath NewImportDir;
    NewImportDir.Path = TEXT("/Game/CaptureManager/Imports");
    Settings->SetImportDirectory(NewImportDir);
    
    FDirectoryPath NewMediaDir;
    NewMediaDir.Path = TEXT("D:/CaptureData");
    Settings->SetMediaDirectory(NewMediaDir);
}
#endif
```

*来源：Public/Settings/CaptureManagerEditorSettings.h*

## Demo 示例

以下演示如何注册一个监听 Capture Manager 设置变更的 Actor 组件，并在设置修改时刷新缓存的路径信息。

### MyCaptureDataComponent.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MyCaptureDataComponent.generated.h"

class UCaptureManagerEditorSettings;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyCaptureDataComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UFUNCTION()
    void OnSettingsChanged();

    void RefreshCachedPaths();

    FString CachedImportDirectory;
    FString CachedMediaDirectory;
};
```

### MyCaptureDataComponent.cpp

```cpp
#include "MyCaptureDataComponent.h"
#include "Settings/CaptureManagerEditorSettings.h"

void UMyCaptureDataComponent::BeginPlay()
{
    Super::BeginPlay();

#if WITH_EDITOR
    UCaptureManagerEditorSettings* Settings = UCaptureManagerEditorSettings::GetCaptureManagerEditorSettings();
    if (Settings)
    {
        Settings->OnCaptureManagerEditorSettingsChanged.AddDynamic(this, &UMyCaptureDataComponent::OnSettingsChanged);
        RefreshCachedPaths();
    }
#endif
}

void UMyCaptureDataComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
#if WITH_EDITOR
    UCaptureManagerEditorSettings* Settings = UCaptureManagerEditorSettings::GetCaptureManagerEditorSettings();
    if (Settings)
    {
        Settings->OnCaptureManagerEditorSettingsChanged.RemoveDynamic(this, &UMyCaptureDataComponent::OnSettingsChanged);
    }
#endif
    Super::EndPlay(EndPlayReason);
}

void UMyCaptureDataComponent::OnSettingsChanged()
{
    RefreshCachedPaths();
    UE_LOG(LogTemp, Log, TEXT("Capture Manager settings changed. Import: %s, Media: %s"),
        *CachedImportDirectory, *CachedMediaDirectory);
}

void UMyCaptureDataComponent::RefreshCachedPaths()
{
    UCaptureManagerEditorSettings* Settings = UCaptureManagerEditorSettings::GetCaptureManagerEditorSettings();
    if (Settings)
    {
        CachedImportDirectory = Settings->GetVerifiedImportDirectory();
        CachedMediaDirectory = Settings->MediaDirectory.Path;
    }
}
```

## 模块依赖

基于模块名称推断的依赖关系（Build.cs 内容未完整提供）：

| 模块 | 用途 |
|---|---|
| `NamingTokens` | 命名令牌系统基类（UNamingTokens） |
| `LiveLinkHubMessaging` | Live Link Hub 消息通信接口（ILiveLinkHubMessagingModule） |
| `LiveLink` | Live Link 客户端接口（ILiveLinkClient） |

其他标准依赖（无需额外声明）：Core, CoreUObject, Engine, Slate, SlateCore, UnrealEd 等。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `175468f6` | [CaptureManager] Generalize device terminology in DeviceBlueprint | 将 DeviceBlueprint 中的设备术语通用化 |
| 2026-04-30 | `63a844fc` | [CaptureManager] Move blocking ingest Blueprint APIs to a Blocking subcategory. | 将阻塞式 Ingest 蓝图 API 移至 Blocking 子分类 |
| 2026-04-30 | `d6f72591` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 新增 CaptureManagerDeviceBlueprint 模块 |
| 2026-04-29 | `5a664506` | [Backout] - CL53274396 | 回退一个变更 |
| 2026-04-29 | `1c481042` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 新增 CaptureManagerDeviceBlueprint 模块（首次尝试后回退） |

### 维护评价

- **创建时间**：2025-02-04，约 1 年前
- **活跃度**：2026 年 4 月底有集中更新（DeviceBlueprint 模块、API 分类优化），说明插件仍处于**活跃开发阶段**
- **成熟度**：非 Beta、非实验性，但 `EnabledByDefault=false` 表明 Epic 将其定位为**可选的虚拟制作工具**，尚不作为默认启用的核心功能
- **注意**：近期提交主要涉及 CaptureManagerDeviceBlueprint 子模块，CaptureManagerEditorSettings 模块相对稳定
- **推荐**：适用于虚拟制作团队，特别是需要从外部设备导入 Capture 数据的工作流。建议在正式项目中关注命名令牌模板的配置是否满足资产组织需求

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor)
- 官方文档：暂无
- 测试用例：未在插件目录内发现测试文件