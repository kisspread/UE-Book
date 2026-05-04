# Capture Manager Application

> The Capture Manager allows control and monitoring of the capture device, obtains and transcodes the data from the devices and upload the data for import to the UE

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `CaptureDataConverter` (Runtime), `CaptureManagerEditor` (Runtime), `CaptureManagerMediaRW` (Runtime), `CaptureManagerPipeline` (Runtime), `CaptureManagerSettings` (Runtime), `CaptureManagerUnrealEndpoint` (Runtime), `ExampleLiveLinkDevices` (Runtime), `IngestLiveLinkDevice` (Runtime), `LiveLinkCapabilities` (Runtime), `LiveLinkFaceMetadata` (Runtime), `StereoCameraMetadata` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp) | |

---

## 用途

Capture Manager Application 是虚幻引擎虚拟制片流程中的**数据采集与管理中枢**。它解决的核心问题是：如何将来自各种捕获设备（如 Live Link Face、立体相机阵列等）的原始数据，经过转码、转换后，高效地上传并导入到 UE 中。

具体来说，这个插件提供了一套完整的数据流水线：

1. **设备控制与监控**：连接并管理捕获设备，实时监控设备状态
2. **数据获取**：从设备下载拍摄的 Take 数据（视频、音频、元数据）
3. **数据转码**：将原始捕获数据转换为 UE 可用的格式，支持内置引擎媒体读写器或第三方编码器（如 FFmpeg）
4. **数据上传**：将转换后的数据上传到 Unreal 客户端进行导入

该插件是 Epic 为虚拟制片工作流（Virtual Production）设计的企业级工具，特别适用于需要批量处理大量捕获数据的影视制作场景。

## 使用场景

- 你正在使用 Live Link Face 等设备进行面部动捕，需要批量下载、转码并导入 Take 数据 → 用 Capture Manager
- 你有一个立体相机阵列拍摄的多机位素材，需要统一管理并转换为 UE 可用格式 → 用 Capture Manager
- 你的团队需要一个集中化的捕获数据管理界面，支持并行处理多个 Ingest 任务 → 用 Capture Manager
- 你需要使用第三方编码器（如 FFmpeg）进行自定义视频/音频转码 → 在 Capture Manager Settings 中配置

## 模块架构

作为 xlarge 级别插件（258 个源文件），CaptureManagerApp 由 11 个模块组成：

| 模块 | 类型 | 职责 |
|---|---|---|
| `CaptureManagerSettings` | Runtime | 全局设置与命名令牌配置 |
| `CaptureManagerPipeline` | Runtime | 数据处理流水线核心逻辑 |
| `CaptureDataConverter` | Runtime | 捕获数据格式转换 |
| `CaptureManagerMediaRW` | Runtime | 媒体读写操作 |
| `CaptureManagerUnrealEndpoint` | Runtime | 与 Unreal 客户端的通信端点 |
| `CaptureManagerEditor` | Runtime | 编辑器集成与 UI |
| `IngestLiveLinkDevice` | Runtime | Live Link 设备数据摄取 |
| `LiveLinkCapabilities` | Runtime | Live Link 能力定义 |
| `LiveLinkFaceMetadata` | Runtime | Live Link Face 元数据解析 |
| `StereoCameraMetadata` | Runtime | 立体相机元数据解析 |
| `ExampleLiveLinkDevices` | Runtime | 示例 Live Link 设备实现 |

---

# CaptureManagerSettings 模块

## 用途

`CaptureManagerSettings` 是 Capture Manager 的**配置中心**，负责管理所有全局设置和命名令牌（Naming Tokens）。它定义了：

- **工作目录配置**：转换数据的临时存储位置、下载目录
- **第三方编码器集成**：可选的外部编码器（如 FFmpeg）路径和命令行参数
- **命名令牌系统**：用于动态生成文件名和路径的模板变量（如 `{id}`、`{device}`、`{slate}`、`{take}`）
- **上传配置**：默认上传目标主机名
- **并行处理**：Ingest 任务的并行执行数量

## 蓝图用法

该模块的类标记为 `NotBlueprintable`，不直接暴露蓝图接口。配置通过编辑器的 **Project Settings → Capture Manager** 面板进行。

### 核心配置项

| 配置项 | 类型 | 说明 |
|---|---|---|
| `DefaultWorkingDirectory` | FDirectoryPath | 转换后数据的默认存储位置 |
| `bShouldCleanWorkingDirectory` | bool | Ingest 完成后是否清理工作目录 |
| `DownloadDirectory` | FDirectoryPath | 从设备下载 Take 数据的存储位置 |
| `bEnableThirdPartyEncoder` | bool | 是否启用第三方编码器 |
| `ThirdPartyEncoder` | FFilePath | 第三方编码器可执行文件路径 |
| `CustomVideoCommandArguments` | FString | 自定义视频编码命令参数 |
| `CustomAudioCommandArguments` | FString | 自定义音频编码命令参数 |
| `DefaultUploadHostName` | FString | 上传目标主机名（留空则使用本机） |
| `NumIngestExecutors` | int32 | 并行 Ingest 任务数（1-8） |

### 命名令牌

命名令牌用于在路径和文件名中插入动态值：

**通用令牌（General Tokens）**：
| 令牌 | 说明 |
|---|---|
| `{id}` | 唯一标识符 |
| `{device}` | 设备名称 |
| `{slate}` | Slate 编号 |
| `{take}` | Take 编号 |

**视频编码器令牌（Video Encoder Tokens）**：
| 令牌 | 说明 |
|---|---|
| `{input}` | 输入文件路径 |
| `{output}` | 输出文件路径 |
| `{params}` | 编码参数 |

**音频编码器令牌（Audio Encoder Tokens）**：
| 令牌 | 说明 |
|---|---|
| `{input}` | 输入文件路径 |
| `{output}` | 输出文件路径 |

## C++ 用法

### 头文件引入

```cpp
#include "Settings/CaptureManagerSettings.h"
#include "Settings/CaptureManagerTemplateTokens.h"
```

### 基本用法

访问 Capture Manager 全局设置：

```cpp
#include "Settings/CaptureManagerSettings.h"

// 获取全局设置对象
UCaptureManagerSettings* Settings = GetMutableDefault<UCaptureManagerSettings>();

// 读取配置
FString WorkingDir = Settings->DefaultWorkingDirectory.Path;
bool bCleanAfterIngest = Settings->bShouldCleanWorkingDirectory;
int32 ParallelJobs = Settings->NumIngestExecutors;

// 检查是否启用第三方编码器
if (Settings->bEnableThirdPartyEncoder)
{
    FString EncoderPath = Settings->ThirdPartyEncoder.FilePath;
    // 使用第三方编码器...
}
```

### 命名令牌使用

```cpp
#include "Settings/CaptureManagerTemplateTokens.h"

// 获取通用命名令牌
UCaptureManagerSettings* Settings = GetMutableDefault<UCaptureManagerSettings>();
TObjectPtr<UCaptureManagerGeneralTokens> GeneralTokens = Settings->GetGeneralNamingTokens();

// 查询特定令牌的描述信息
UE::CaptureManager::FArchiveToken DeviceToken = GeneralTokens->GetToken(
    FString(UE::CaptureManager::GeneralTokens::DeviceKey)
);
FString TokenName = DeviceToken.Name;
FText TokenDescription = DeviceToken.Description;

// 获取视频编码器令牌
TObjectPtr<UCaptureManagerVideoEncoderTokens> VideoTokens = Settings->GetVideoEncoderNamingTokens();
UE::CaptureManager::FArchiveToken InputToken = VideoTokens->GetToken(
    FString(UE::CaptureManager::VideoEncoderTokens::InputKey)
);
```

## Demo 示例

### 自定义 Ingest 配置管理器

```cpp
// MyIngestConfigManager.h
#pragma once

#include "CoreMinimal.h"

class FMyIngestConfigManager
{
public:
    /** 初始化配置管理器，读取 Capture Manager 设置 */
    void Initialize();

    /** 获取格式化后的工作目录路径 */
    FString GetFormattedWorkingDirectory(const FString& InDeviceName, 
                                          const FString& InSlate, 
                                          const FString& InTake) const;

    /** 检查是否应使用第三方编码器 */
    bool ShouldUseThirdPartyEncoder() const;

    /** 获取第三方编码器命令行 */
    FString BuildEncoderCommand(const FString& InInputPath, 
                                 const FString& InOutputPath) const;

private:
    FString WorkingDirectoryTemplate;
    bool bUseThirdPartyEncoder = false;
    FString EncoderPath;
    FString VideoCommandArgs;
};
```

```cpp
// MyIngestConfigManager.cpp
#include "MyIngestConfigManager.h"
#include "Settings/CaptureManagerSettings.h"
#include "Settings/CaptureManagerTemplateTokens.h"

void FMyIngestConfigManager::Initialize()
{
    UCaptureManagerSettings* Settings = GetMutableDefault<UCaptureManagerSettings>();
    
    WorkingDirectoryTemplate = Settings->DefaultWorkingDirectory.Path;
    bUseThirdPartyEncoder = Settings->bEnableThirdPartyEncoder;
    
    if (bUseThirdPartyEncoder)
    {
        EncoderPath = Settings->ThirdPartyEncoder.FilePath;
        VideoCommandArgs = Settings->CustomVideoCommandArguments;
    }
}

FString FMyIngestConfigManager::GetFormattedWorkingDirectory(
    const FString& InDeviceName, 
    const FString& InSlate, 
    const FString& InTake) const
{
    // 使用命名令牌替换生成最终路径
    FString Result = WorkingDirectoryTemplate;
    
    UCaptureManagerSettings* Settings = GetMutableDefault<UCaptureManagerSettings>();
    TObjectPtr<UCaptureManagerGeneralTokens> Tokens = Settings->GetGeneralNamingTokens();
    
    // 替换令牌占位符
    Result.ReplaceInline(TEXT("{device}"), *InDeviceName);
    Result.ReplaceInline(TEXT("{slate}"), *InSlate);
    Result.ReplaceInline(TEXT("{take}"), *InTake);
    
    return Result;
}

bool FMyIngestConfigManager::ShouldUseThirdPartyEncoder() const
{
    return bUseThirdPartyEncoder;
}

FString FMyIngestConfigManager::BuildEncoderCommand(
    const FString& InInputPath, 
    const FString& InOutputPath) const
{
    if (!bUseThirdPartyEncoder)
    {
        return FString();
    }
    
    FString Command = VideoCommandArgs;
    
    // 替换视频编码器令牌
    Command.ReplaceInline(TEXT("{input}"), *InInputPath);
    Command.ReplaceInline(TEXT("{output}"), *InOutputPath);
    
    return FString::Printf(TEXT("\"%s\" %s"), *EncoderPath, *Command);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NamingTokens` | 命名令牌框架，用于模板变量系统 |

无其他特殊依赖（仅标准 Core/CoreUObject/Engine 等）。

## 维护状态

### 近期更新

```
- 484f0378a0f8 [CaptureManager] Add device token to default working directory and download directory
- 044cc37ca528 Fixing crash when disconnect happens
- 28ddf7856b12 [CaptureManager] Default ingest locations to UserDir
```

- 最新提交添加了 `{device}` 令牌到默认工作目录和下载目录模板中，增强了路径的动态生成能力
- 修复了设备断开连接时的崩溃问题
- 将默认 Ingest 存储位置改为用户目录

### 维护评价

- **状态**：🆕 活跃维护中
- **创建时间**：2025-02-04，非常新的插件
- **更新频率**：近期有持续的功能增强和 bug 修复
- **推荐程度**：✅ 强烈推荐用于虚拟制片工作流

该插件是 Epic 官方维护的虚拟制片核心工具之一，处于积极开发阶段。作为 2025 年新推出的插件，它代表了 UE5 在虚拟制片领域的最新工具链投入。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp)
- [CaptureManagerSettings 源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp/Source/CaptureManagerSettings)