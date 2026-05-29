# Live Link Hub Export Server

> The Capture Manager Editor plugin is used for importing the Capture archive data into UE/UEFN to create necessary assets

| 属性 | 值 |
|---|---|
| 中文名 | Live Link Hub 导出服务器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `CaptureManagerDeviceBlueprint` (Runtime), `CaptureManagerEditorSettings` (Runtime), `CaptureManagerIngestBlueprint` (Runtime), `DataIngestCoreEditor` (Runtime), `LiveLinkHubDiscoveryEditor` (Runtime), `LiveLinkHubExportServer` (Runtime), `LiveLinkHubWorkerManager` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor) | |

> **注意**：本文档聚焦于 `LiveLinkHubExportServer` 模块。该插件共包含 7 个子模块，本模块负责 TCP 文件导出服务器功能。

## 用途

LiveLinkHubExportServer 模块提供一个 TCP 文件传输服务器，用于在 Live Link Hub 设备（如 iPhone 捕获设备）与 Unreal Engine 之间建立安全的文件传输通道。它的核心功能是：

- **接收捕获设备上传的文件数据**：设备通过 TCP 连接将捕获的媒体文件（视频、深度数据等）推送到引擎
- **按客户端注册处理器**：支持多设备并发，每个设备通过唯一标识注册自己的文件处理回调
- **作为 CaptureManager 捕获流水线的传输层**：连接捕获硬件与引擎内的资产导入管线

该模块是 CaptureManagerEditor 插件"从捕获设备导入数据到引擎"这一核心流程中的关键基础设施。

## 使用场景

- 你在使用 iPhone + Live Link Hub 进行面部/身体捕捉 → 此模块提供引擎端的 TCP 服务器接收设备推流的文件
- 你需要多台设备同时向引擎推送捕获数据 → 每台设备注册独立的文件处理器，互不干扰
- 你在 Virtual Production 现场需要实时接收捕获设备的文件 → 使用此模块在指定端口启动导出服务器

## 蓝图用法

本模块主要面向 C++ 层，蓝图 API 封装在 `CaptureManagerIngestBlueprint` 等其他模块中。LiveLinkHubExportServer 自身的公开接口为纯 C++ API。

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkHubExportServerModule.h"
#include "LiveLinkHubExportServer.h"
```

### 基本用法

获取模块单例，启动和停止导出服务器：

```cpp
// 获取模块实例
FLiveLinkHubExportServerModule& ExportModule = FModuleManager::GetModuleChecked<FLiveLinkHubExportServerModule>("LiveLinkHubExportServer");

// 在指定端口启动服务器
bool bStarted = ExportModule.StartExportServer(12345);
if (bStarted)
{
    UE_LOG(LogTemp, Log, TEXT("Export server started"));
}

// 检查服务器是否正在运行
bool bRunning = ExportModule.IsExportServerRunning();

// 获取服务器信息（IP 地址和端口）
auto ServerInfoResult = ExportModule.GetExportServerInfo();
if (ServerInfoResult.HasValue())
{
    auto Info = ServerInfoResult.GetValue();
    UE_LOG(LogTemp, Log, TEXT("Server at %s:%d"), *Info.IPAddress, Info.Port);
}

// 停止服务器
ExportModule.StopExportServer();
```

### 进阶用法

为特定客户端设备注册文件数据处理器，处理上传的捕获数据：

```cpp
// 注册文件数据处理器
// InClientId: 设备的唯一标识（通常是字符串化的 FGuid）
// FFileDataHandler: 接收文件头和 TCP 客户端处理器的委托
ExportModule.RegisterExportServerHandler(TEXT("Device-ABC-123"),
    FLiveLinkHubExportServer::FFileDataHandler::CreateLambda(
        [](FUploadDataHeader InHeader, TSharedPtr<UE::CaptureManager::FTcpClientHandler> InClient) -> bool
        {
            // 处理上传的文件数据
            // InHeader 包含文件元信息（文件名、大小等）
            // InClient 提供对 TCP 连接的控制（读取数据、断开等）
            
            UE_LOG(LogTemp, Log, TEXT("Received file: %s"), *InHeader.FileName);
            
            // 返回 true 表示成功处理
            return true;
        }
    )
);

// 取消注册（设备断开或不再需要时）
ExportModule.UnregisterExportServerHandler(TEXT("Device-ABC-123"));
```

使用 `FLiveLinkHubExportServer` 类直接操作（无需通过模块单例）：

```cpp
// 直接创建服务器实例
TSharedPtr<FLiveLinkHubExportServer> Server = MakeShared<FLiveLinkHubExportServer>();

// 在默认端口启动
Server->Start();

// 或指定端口
Server->Start(8080);

// 注册处理器
Server->RegisterFileDownloadHandler(TEXT("Client-001"),
    FLiveLinkHubExportServer::FFileDataHandler::CreateRaw(this, &FMyClass::HandleFileData));

// 销毁时自动停止
Server.Reset();
```

## Demo 示例

一个完整的最小示例，展示如何创建导出服务器并处理上传的文件：

```cpp
// MyExportServerManager.h
#pragma once

#include "CoreMinimal.h"
#include "LiveLinkHubExportServer.h"

class FMyExportServerManager
{
public:
    void Initialize(uint16 InPort);
    void Shutdown();

private:
    bool HandleIncomingFile(FUploadDataHeader InHeader, 
                            TSharedPtr<UE::CaptureManager::FTcpClientHandler> InClient);

    TSharedPtr<FLiveLinkHubExportServer> ExportServer;
};
```

```cpp
// MyExportServerManager.cpp
#include "MyExportServerManager.h"

void FMyExportServerManager::Initialize(uint16 InPort)
{
    ExportServer = MakeShared<FLiveLinkHubExportServer>();

    // 注册文件处理器
    ExportServer->RegisterFileDownloadHandler(TEXT("DefaultHandler"),
        FLiveLinkHubExportServer::FFileDataHandler::CreateRaw(
            this, &FMyExportServerManager::HandleIncomingFile));

    // 启动服务器
    if (ExportServer->Start(InPort))
    {
        auto Info = ExportServer->GetServerInfo();
        if (Info.HasValue())
        {
            UE_LOG(LogTemp, Log, TEXT("Export server running at %s:%d"),
                *Info.GetValue().IPAddress, Info.GetValue().Port);
        }
    }
}

void FMyExportServerManager::Shutdown()
{
    if (ExportServer)
    {
        ExportServer->UnregisterFileDownloadHandler(TEXT("DefaultHandler"));
        ExportServer->Stop();
        ExportServer.Reset();
    }
}

bool FMyExportServerManager::HandleIncomingFile(
    FUploadDataHeader InHeader,
    TSharedPtr<UE::CaptureManager::FTcpClientHandler> InClient)
{
    // 处理从捕获设备接收到的文件
    UE_LOG(LogTemp, Log, TEXT("Received file from capture device: %s (%lld bytes)"),
        *InHeader.FileName, InHeader.FileSize);
    
    // ... 保存文件或触发资产导入流程
    
    return true;
}
```

## 模块依赖

本模块依赖较为精简，使用标准网络基础设施：

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | — |

> TCP 服务器实现在 `UE::CaptureManager::FTcpServer` 中，该类可能位于其他 CaptureManager 模块中，通过 `CaptureManager` 内部链接提供。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `175468f6` | [CaptureManager] Generalize device terminology in DeviceBlueprint | 统一设备蓝图中的设备术语命名 |
| 2026-04-30 | `63a844fc` | [CaptureManager] Move blocking ingest Blueprint APIs to a Blocking subcategory. | 将阻塞式摄入蓝图 API 移到独立子分类 |
| 2026-04-30 | `d6f72591` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 新增设备蓝图模块 |
| 2026-04-29 | `5a664506` | [Backout] - CL53274396 | 回退一个变更 |
| 2026-04-29 | `1c481042` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 首次添加设备蓝图模块（后被回退再重提） |

### 维护评价

- **状态**：🟢 **活跃开发中**
- 插件于 2025 年 2 月创建，至今约 1 年
- 最近更新集中在 2026 年 4 月底，持续有功能迭代和模块扩展
- 虽然 `EnabledByDefault=false`，但这属于 Virtual Production 专业场景的常见设置，用户按需启用
- 插件由 Epic Games 官方维护，属于 CaptureManager 虚拟制片管线的核心组件
- **推荐使用**：如果你在做虚拟制片/动作捕捉相关工作，这是官方推荐的数据导入传输层

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor)
- [LiveLinkHubExportServer 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor/Source/LiveLinkHubExportServer)