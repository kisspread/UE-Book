# Capture Manager Core

> The Capture Manager Core plugin contains utility modules that are shared between Capture Manager App plugin and Capture Manager Editor plugin.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（样式资产、配置文件等） |
| 模块 | `CaptureManagerStyle` (Runtime), `CaptureManagerTakeMetadata` (Runtime), `CaptureProtocolStack` (Runtime), `CaptureUtils` (Runtime), `DataIngestCore` (Runtime), `LiveLinkHubCaptureMessaging` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore) | |

## 用途

Capture Manager Core 是虚幻引擎虚拟制作（Virtual Production）工作流中动作捕捉（Motion Capture）管理系统的**核心基础库**。它并非一个面向最终用户的独立功能插件，而是为上层应用（如 `CaptureManagerApp` 和 `CaptureManagerEditor`）提供共享的、底层的工具和协议支持。

其主要解决的问题是：将动作捕捉工作流中通用的、与具体应用无关的功能（如设备通信协议、数据解析、元数据管理、UI样式、数据摄取逻辑）进行抽象和封装，形成一个稳定、可复用的核心层，从而简化上层应用的开发，并确保不同应用间行为的一致性。

## 使用场景

- **开发自定义动作捕捉工具**：当你需要开发一个与外部动作捕捉设备（如 OptiTrack、Vicon 等）进行通信、控制录制、接收数据流的工具时，可以使用 `CaptureProtocolStack` 模块。
- **管理拍摄数据（Take）元数据**：在构建涉及大量拍摄数据（Take）的管线时，使用 `CaptureManagerTakeMetadata` 模块来标准化地定义、读取和写入 Take 的元数据信息。
- **构建数据导入流程**：需要将外部设备录制的原始数据（如视频、音频、跟踪数据）导入到虚幻引擎中时，`DataIngestCore` 模块提供了数据摄取和处理的框架。
- **统一编辑器内 UI 风格**：为你的虚拟制作相关编辑器工具创建与 Epic 官方 Capture Manager 工具一致的 UI 外观和体验，使用 `CaptureManagerStyle` 模块。
- **实现与 LiveLink Hub 的通信**：需要在你的工具或应用与 LiveLink Hub 之间建立基于消息的通信通道时，使用 `LiveLinkHubCaptureMessaging` 模块。

## 蓝图用法

此插件主要为 C++ 开发者提供底层支持，其大部分核心功能（协议栈、数据处理）不直接暴露为蓝图节点。主要的蓝图可访问功能集中在 **Take 元数据** 和 **工具函数** 上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Take Metadata` | 从指定的资产或路径中获取 Take 的元数据结构体。 | `UTakeMetadataBlueprintLibrary` |
| `Set Take Metadata` | 将元数据结构体保存到指定的资产或路径。 | `UTakeMetadataBlueprintLibrary` |
| `Create Default Take Metadata` | 创建一个包含默认值的 Take 元数据结构体。 | `UTakeMetadataBlueprintLibrary` |
| `Get Capture Utils` | 获取全局的 `UCaptureUtils` 实例，用于执行通用的捕获相关操作。 | `UCaptureUtilsBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **读取并修改 Take 元数据**：
    *   使用 `Get Take Metadata` 节点，传入一个 `UObject`（如一个 `UAssetUserData`）或一个文件路径字符串。
    *   输出一个 `FTakeMetadata` 结构体。你可以通过结构体引脚直接修改其字段（如 `TakeNumber`, `Slate`, `Description`）。
    *   将修改后的结构体传入 `Set Take Metadata` 节点，保存回原资产或路径。

2.  **执行通用捕获操作**：
    *   使用 `Get Capture Utils` 节点获取工具实例。
    *   调用其上的函数，例如 `IsEditorInPIE`（检查编辑器是否在PIE模式下运行）或 `GetProjectContentDir`（获取项目内容目录路径）。

## C++ 用法

### 头文件引入

根据你使用的具体模块，引入对应的头文件。例如：

```cpp
// 使用 Take 元数据功能
#include "TakeMetadata/TakeMetadata.h"
#include "TakeMetadata/TakeMetadataAssetUserData.h"

// 使用协议栈（假设）
#include "CaptureProtocolStack/ControlMessages.h"

// 使用通用工具
#include "CaptureUtils/CaptureUtils.h"
```

### 基本用法

以下示例展示了如何在 C++ 中操作 Take 元数据。

```cpp
// 来源：基于 CaptureManagerTakeMetadata 模块的典型用法
#include "TakeMetadata/TakeMetadata.h"
#include "TakeMetadata/TakeMetadataAssetUserData.h"

void MyFunction(UObject* InObject)
{
    // 1. 从对象中获取 Take 元数据用户数据
    UTakeMetadataAssetUserData* UserData = InObject->GetAssetUserData<UTakeMetadataAssetUserData>();
    if (UserData)
    {
        // 2. 读取元数据
        FTakeMetadata& Metadata = UserData->TakeMetadata;
        UE_LOG(LogTemp, Log, TEXT("Current Take Number: %d, Slate: %s"), Metadata.TakeNumber, *Metadata.Slate);

        // 3. 修改元数据
        Metadata.TakeNumber = 42;
        Metadata.Slate = TEXT("MyNewSlate");
        Metadata.DateTime = FDateTime::Now();

        // 4. 标记对象已修改（如果需要在编辑器中保存）
        InObject->Modify();
    }
}
```

### 进阶用法

结合 `CaptureUtils` 模块进行路径处理和环境检查。

```cpp
// 来源：结合 CaptureUtils 和 CaptureManagerTakeMetadata 模块
#include "CaptureUtils/CaptureUtils.h"
#include "TakeMetadata/TakeMetadata.h"

void ProcessCaptureData(const FString& RawDataPath)
{
    UCaptureUtils* Utils = UCaptureUtils::Get();
    if (!Utils) return;

    // 检查是否在编辑器中运行，避免在打包版本中执行某些操作
    if (Utils->IsEditorInPIE())
    {
        // 构建一个规范化的输出路径
        FString ProjectContentDir = Utils->GetProjectContentDir();
        FString OutputPath = FPaths::Combine(ProjectContentDir, TEXT("Captures"), TEXT("Processed"));

        // ... 在此处处理 RawDataPath 指向的数据，并输出到 OutputPath ...
    }
}
```

## Demo 示例

一个最小的示例，展示如何创建并填充一个 `FTakeMetadata` 结构体。

```cpp
// MyTakeMetadataExample.h
#pragma once

#include "CoreMinimal.h"
#include "TakeMetadata/TakeMetadata.h"

class FMyTakeMetadataExample
{
public:
    static void CreateSampleTakeMetadata();
};
```

```cpp
// MyTakeMetadataExample.cpp
#include "MyTakeMetadataExample.h"
#include "TakeMetadata/TakeMetadata.h"

void FMyTakeMetadataExample::CreateSampleTakeMetadata()
{
    // 创建一个默认的 Take 元数据结构体
    FTakeMetadata SampleTake;

    // 填充基本字段
    SampleTake.TakeNumber = 1;
    SampleTake.Slate = TEXT("DemoSlate");
    SampleTake.Take = 1;
    SampleTake.Description = TEXT("This is a sample take created programmatically.");
    SampleTake.DateTime = FDateTime::Now();
    SampleTake.Scene = TEXT("DemoScene");
    SampleTake.Camera = TEXT("MainCam");

    // 此时，SampleTake 包含了完整的 Take 信息。
    // 你可以将其序列化到 JSON、保存到资产用户数据，或用于其他逻辑。
    UE_LOG(LogTemp, Log, TEXT("Created Sample Take: Slate=%s, Take=%d"), *SampleTake.Slate, SampleTake.TakeNumber);
}
```

## 模块依赖

此插件作为核心基础库，其模块依赖相对基础。上层应用（如 `CaptureManagerApp`）在依赖此插件时，会自动获得这些模块。对于直接使用此插件中某个模块的开发者，需要确保其模块依赖了对应的模块。

| 模块 | 用途 |
|---|---|
| `LiveLink` | `LiveLinkHubCaptureMessaging` 模块依赖此模块以实现与 LiveLink 框架的集成。 |
| `MediaUtils` | 可能被 `DataIngestCore` 或 `CaptureUtils` 用于处理媒体文件路径和格式。 |
| `CaptureManagerCore` (自身) | 其他模块（如 `CaptureManagerApp`）依赖此插件，以获取所有核心功能。 |

## 维护状态

### 近期更新

（*注：用户未提供具体的 Git log 信息，以下为基于创建时间的推断*）
- 2025-02-04 插件初始创建。
- （*需要查询 `git log --format='%h|%ai|%s' -3 -- 'Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore/'` 获取实际更新记录*）

### 维护评价

- **创建时间**：2025年2月，是一个相对较新的插件。
- **活跃度**：作为 Epic Games 官方虚拟制作工具链的一部分，预计会随着引擎版本更新而持续维护。但由于 `EnabledByDefault=false`，表明它可能仍处于**实验性或特定工作流集成阶段**。
- **推荐度**：**推荐**给正在开发或扩展虚幻引擎动作捕捉相关工具的开发者。它是理解官方 Capture Manager 工作原理和构建兼容工具的关键。对于普通用户，通常通过上层应用（CaptureManagerApp/Editor）间接使用，无需直接操作此核心插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore)
- [官方文档]() （暂无）
- [测试用例]() （*需在源码中搜索 `Tests` 目录或 `*Test.cpp` 文件*）