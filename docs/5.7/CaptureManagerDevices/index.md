# Capture Manager Devices

> The Capture Manager Devices contains devices that can be used from the Capture Manager layout of the LiveLink Hub

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（UI 自定义、编辑器资产） |
| 模块 | `MonoVideoIngestDevice` (Editor), `CPSLiveLinkDevice` (Editor), `TakeArchiveIngestDevice` (Editor), `StereoVideoIngestDevice` (Editor), `VideoLiveLinkDeviceCommon` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-02-14 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerDevices) | |

## 用途

Capture Manager Devices 是 Capture Manager 生态系统的设备层插件，为 LiveLink Hub 的 Capture Manager 布局提供各种数据采集（Ingest）设备。它解决的核心问题是：**如何从不同来源（iOS Live Link Face 应用、本地视频文件、Take 归档文件）将拍摄数据统一导入到 Unreal Engine 中**。

该插件本身是一个纯设备注册插件，不包含运行时逻辑。所有模块均为 Editor 类型，仅在编辑器环境中加载。插件被标记为 `Hidden: true`、`EnabledByDefault: false`，意味着它作为 CaptureManagerApp 的子插件被自动拉取，而非用户手动启用。

插件提供四种设备类型：

1. **Live Link Face Device** — 通过 CPS（Capture Protocol Stack）协议连接 iOS Live Link Face 应用，支持远程录制控制、Take 列表获取、数据导出与下载
2. **Mono Video Ingest Device** — 从本地目录导入单目视频文件，通过文件名模式解析 Slate/Take/Name 等元数据
3. **Stereo Video Ingest Device** — 从本地目录导入立体视频对（含音频），支持视频、图像序列和音频三种组件类型
4. **Take Archive Ingest Device** — 导入 `.cptake` 格式的 Take 归档文件和旧版 Capture Manager Take 数据

## 使用场景

- 你使用 iOS 上的 **Live Link Face** 应用进行面部捕捉，需要将录制数据导入 UE → 用 **Live Link Face Device**，它会自动连接设备、获取 Take 列表并支持远程录制控制
- 你有一批已拍摄的**单目视频文件**（如 `.mov` 文件），需要批量导入为 Take → 用 **Mono Video Ingest Device**，配置目录路径和文件名模式即可
- 你使用**立体相机**拍摄了左右眼视频对，需要作为立体 Take 导入 → 用 **Stereo Video Ingest Device**，支持视频、图像序列和音频的自动分组
- 你有 `.cptake` 格式的 **Take 归档**或旧版 Capture Manager 数据 → 用 **Take Archive Ingest Device**

## 蓝图用法

所有设备类均标记为 `BlueprintType`，可在蓝图中使用。但由于插件为 Editor-only，这些节点仅在编辑器蓝图中可用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSettings` | 获取设备设置（IP 地址、端口、目录路径等） | `ULiveLinkFaceDevice` / `UMonoVideoIngestDevice` / `UStereoVideoIngestDevice` / `UTakeArchiveIngestDevice` |
| `GetDisplayName` | 获取设备显示名称 | 各设备基类 |
| `GetDeviceHealth` | 获取设备健康状态 | 各设备基类 |

### 设备设置属性

**Live Link Face Device** (`ULiveLinkFaceDeviceSettings`)：
- `DisplayName` — 设备显示名称，默认 "Live Link Face"
- `IpAddress` — 设备 IP 地址
- `Port` — 控制端口，默认 14785
- `ConnectAction` — 连接操作（UI 按钮绑定）

**Mono Video Ingest Device** (`UMonoVideoIngestDeviceSettings`)：
- `DisplayName` — 设备显示名称，默认 "Mono Video Ingest"
- `TakeDirectory` — Take 数据目录路径
- `VideoDiscoveryExpression` — 文件名解析模式，默认 `<Auto>`

**Stereo Video Ingest Device** (`UStereoVideoIngestDeviceSettings`)：
- `DisplayName` — 设备显示名称，默认 "Stereo Video Ingest"
- `TakeDirectory` — Take 数据目录路径
- `VideoDiscoveryExpression` — 视频文件名解析模式，默认 `<Auto>`
- `AudioDiscoveryExpression` — 音频文件名解析模式，默认 `<Auto>`

**Take Archive Ingest Device** (`UTakeArchiveIngestDeviceSettings`)：
- `DisplayName` — 设备显示名称，默认 "Take Archive Ingest"
- `TakeDirectory` — Take 数据目录路径

### 文件名解析表达式

Mono/Stereo Video 设备支持自定义文件名模式来解析 Take 元数据：

| 表达式 | 说明 |
|---|---|
| `<Slate>` | Slate 名称 |
| `<Name>` | 相机标识符 |
| `<Take>` | Take 编号 |
| `<Any>` | 匹配任意字符串（忽略） |
| `<Auto>` | 独占使用，自动根据目录结构推断 |

支持的分隔符：`_`、`-`、`.`（Stereo 设备额外支持 `\`）

示例：对于文件 `MySlate_MyName_SomeString-005.mov`：
- `<Auto>` → Slate="MySlate_MyName_SomeString_005"，Name="video"，Take=1
- `<Slate>_<Name>_<Any>-<Take>` → Slate="MySlate"，Name="MyName"，Take=5

注意：不使用 `<Auto>` 时，`<Slate>` 和 `<Name>` 必须同时出现在模式中。

## C++ 用法

### 头文件引入

```cpp
// Live Link Face 设备（网络设备）
#include "LiveLinkFaceDevice.h"

// Mono Video Ingest 设备
#include "MonoVideoIngestDevice.h"

// Stereo Video Ingest 设备
#include "StereoVideoIngestDevice.h"

// Take Archive Ingest 设备
#include "TakeArchiveIngestDevice.h"

// CPS 协议层（底层通信）
#include "Protocol/CPSDevice.h"

// 文件名解析器
#include "Utils/TakeDiscoveryExpressionParser.h"
```

### Live Link Face 设备连接与录制

Live Link Face 设备通过 CPS 协议与 iOS 应用通信。底层 `FCPSDevice` 类管理连接、录制和数据导出。

```cpp
// 创建 CPS 设备实例
using namespace UE::CaptureManager;
TSharedPtr<FCPSDevice> Device = FCPSDevice::MakeCPSDevice(TEXT("192.168.1.100"), 14785);

// 订阅连接状态事件
Device->SubscribeToEvent(FConnectionStateChangedEvent::Name,
    FCaptureEventHandler::Type::CreateLambda([](TSharedPtr<const FCaptureEvent> Event)
    {
        auto StateEvent = StaticCastSharedPtr<const FConnectionStateChangedEvent>(Event);
        // 处理连接状态变化：Connecting, Connected, Disconnected
    }));

// 发起连接
Device->InitiateConnect();

// 开始录制（需要 Slate 名称和 Take 编号）
TProtocolResult<void> Result = Device->StartRecording(
    TEXT("MySlate"),    // Slate 名称
    1,                  // Take 编号
    TEXT("Subject"),    // 可选：主体
    TEXT("Scenario"),   // 可选：场景
    TArray<FString>{}   // 可选：标签
);

// 停止录制
Device->StopRecording();

// 获取 Take 列表
TProtocolResult<TArray<FGetTakeMetadataResponse::FTakeObject>> Takes = Device->FetchTakeList();
```

### 文件名解析器使用

```cpp
#include "Utils/TakeDiscoveryExpressionParser.h"

// 定义分隔符
TArray<FString::ElementType> Delimiters = { '-', '_', '.', '/' };

// 创建解析器：格式 + 文件名 + 分隔符
FTakeDiscoveryExpressionParser Parser(
    TEXT("<Slate>_<Name>_<Any>-<Take>"),     // 格式模式
    TEXT("MySlate_MyName_SomeString-005"),   // 实际文件名
    Delimiters
);

if (Parser.Parse())
{
    FString SlateName = Parser.GetSlateName();  // "MySlate"
    FString Name = Parser.GetName();             // "MyName"
    int32 TakeNumber = Parser.GetTakeNumber();   // 5
}
```

### 数据导出流

CPS 协议使用 `FBaseStream` 抽象处理数据导出。有两种实现：

```cpp
// FCPSFileStream — 导出到磁盘文件
TUniquePtr<FCPSFileStream> FileStream = MakeUnique<FCPSFileStream>(
    TEXT("/path/to/download"),  // 下载目录
    TotalSize                   // 预期总大小
);
FileStream->SetProgressHandler(/* 进度回调 */);
FileStream->SetExportFinished(/* 完成回调 */);
Device->StartExport(TakeId, MoveTemp(FileStream));

// FCPSDataStream — 导出到内存
TUniquePtr<FCPSDataStream> DataStream = MakeUnique<FCPSDataStream>(
    /* 文件导出完成回调 */
);
```

## Demo 示例

以下展示如何在 C++ 中使用文件名解析器解析视频文件名：

```cpp
// Build.cs
PublicDependencyModuleNames.AddRange(new string[]
{
    "VideoLiveLinkDeviceCommon",
    "CaptureManagerTakeMetadata",
    "Core"
});
```

```cpp
// TakeNameParserExample.h
#pragma once

#include "CoreMinimal.h"

class FTakeNameParserExample
{
public:
    static void ParseVideoFileName()
    {
        // 定义支持的分隔符
        TArray<FString::ElementType> Delimiters = { '-', '_', '.', '/' };

        // 示例 1：标准格式
        FTakeDiscoveryExpressionParser Parser1(
            TEXT("<Slate>_<Name>_<Any>-<Take>"),
            TEXT("MySlate_MyCam_BTS-003"),
            Delimiters
        );

        if (Parser1.Parse())
        {
            // Slate = "MySlate", Name = "MyCam", Take = 3
            UE_LOG(LogTemp, Log, TEXT("Slate: %s, Name: %s, Take: %d"),
                *Parser1.GetSlateName(), *Parser1.GetName(), Parser1.GetTakeNumber());
        }

        // 示例 2：单 Token（只提取 Slate）
        FTakeDiscoveryExpressionParser Parser2(
            TEXT("<Slate>"),
            TEXT("JustASlate"),
            Delimiters
        );

        if (Parser2.Parse())
        {
            // Slate = "JustASlate", Take = INDEX_NONE, Name = ""
            UE_LOG(LogTemp, Log, TEXT("Slate: %s"), *Parser2.GetSlateName());
        }
    }
};
```

## 模块依赖

各设备模块的公共依赖（使用者需要引用的模块）：

| 模块 | 用途 |
|---|---|
| `CaptureUtils` | Capture Manager 通用工具库 |
| `CaptureProtocolStack` | CPS 协议栈（仅 CPSLiveLinkDevice） |
| `CaptureManagerTakeMetadata` | Take 元数据结构定义 |
| `ImageCore` | 图像处理核心（仅 VideoLiveLinkDeviceCommon） |
| `Core` | UE 核心库 |

关键私有依赖（设备内部使用，使用者无需直接依赖）：

| 模块 | 用途 |
|---|---|
| `IngestLiveLinkDevice` | Ingest 设备基类（`UBaseIngestLiveLinkDevice`） |
| `LiveLinkDevice` | LiveLink 设备框架 |
| `LiveLinkCapabilities` | 设备能力接口（Ingest、Connection、Recording） |
| `CaptureManagerMediaRW` | 媒体读写 |
| `LiveLinkHub` | LiveLink Hub 集成 |
| `LiveLinkFaceMetadata` | LiveLink Face 元数据解析 |
| `StereoCameraMetadata` | 立体相机元数据解析 |
| `DataIngestCore` | 数据采集核心（仅部分模块） |

## 维护状态

### 近期更新

- `363783e2` | 2025-10-07 | Put quotes around file paths passed to ffmpeg and ffprobe
  - 修复视频缩略图提取时文件路径未加引号导致的问题（影响含空格的路径）
- `9b414a8d` | 2025-10-02 | LiveLinkHub - Fix using wrong PropertyEditorModule method to unregister struct customizations
  - 修复编辑器中结构体自定义注销方法错误的问题
- `803b1082` | 2025-10-02 | Resolving a crash when user removes the device during ingest
  - 修复用户在数据采集过程中移除设备导致的崩溃

### 维护评价

- **创建时间**：2025-02-14，约 1 年前，属于较新的插件
- **更新频率**：最近一次更新在 2025-10-07，近期有活跃维护
- **维护状态**：**活跃维护中** — 作为 Capture Manager / LiveLink Hub 生态系统的核心设备层，属于 Epic 虚拟制作路线图的重点功能
- **已知限制**：
  - `Hidden: true` + `EnabledByDefault: false`，不作为独立插件暴露给用户
  - 全部为 Editor 模块，无运行时支持
  - Live Link Face 设备依赖 iOS Live Link Face 应用的 CPS 协议兼容性
- **推荐使用**：如果你在使用 Capture Manager / LiveLink Hub 工作流，这是必需的设备插件。它由 CaptureManagerApp 自动依赖启用，无需手动操作。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerDevices)
- [父插件 CaptureManagerApp](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerDevices/Source/VideoLiveLinkDeviceCommon/Private/Tests/TestVideoDeviceDiscoveryExpressionParser.cpp)
