# Capture Manager Editor

> The Capture Manager Editor plugin is used for importing the Capture archive data into UE/UEFN to create necessary assets

| 属性 | 值 |
|---|---|
| 中文名 | 捕获管理器编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（设备蓝图、设置资产、摄取蓝图资产、编辑器功能、LiveLink Hub相关模块） |
| 模块 | `CaptureManagerDeviceBlueprint` (Runtime), `CaptureManagerEditorSettings` (Runtime), `CaptureManagerIngestBlueprint` (Runtime), `DataIngestCoreEditor` (Runtime), `LiveLinkHubDiscoveryEditor` (Runtime), `LiveLinkHubExportServer` (Runtime), `LiveLinkHubWorkerManager` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager) | |

## 用途

CaptureManagerEditor 是虚幻引擎虚拟制作流水线中的一个核心插件，旨在自动化从外部捕获设备（如 LiveLink Hub）获取数据并在引擎内创建可直接使用的资产。它解决的问题是将现实世界捕获的媒体数据（视频、音频、深度信息等）高效、可靠地转化为UE内的资产（如纹理、序列、网格体），用于可视化预览、实时合成或资产创建。其核心价值在于提供一套完整的数据摄取、传输和处理框架，特别是通过其 `LiveLinkHubExportServer` 模块，建立了一个基于TCP的服务器，允许捕获设备实时或批量地将数据推送到引擎中进行处理。

## 使用场景

- **使用多设备（如相机阵列）进行同步捕获**：在拍摄现场，多个捕获设备通过 LiveLink Hub 同步。CaptureManager 自动将这些设备生成的归档数据包传输到 UE 中。
- **创建用于虚拟制作或后期制作的资产**：从现场捕获的素材（视频、深度图等）需要快速导入UE，用于场景合成、光照匹配或虚拟摄像机预览。
- **构建自定义数据摄取管线**：开发者可以利用 `LiveLinkHubExportServer` 提供的网络API，集成自定义的捕获设备或数据处理流程。

## 蓝图用法

`LiveLinkHubExportServer` 模块的核心功能通过 `FLiveLinkHubExportServerModule` 模块接口暴露给蓝图。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Export Server` | 在指定端口启动导出服务器，开始监听来自捕获设备的数据连接。 | `FLiveLinkHubExportServerModule` |
| `Stop Export Server` | 停止导出服务器，关闭所有连接。 | `FLiveLinkHubExportServerModule` |
| `Is Export Server Running` | 查询导出服务器当前是否正在运行。 | `FLiveLinkHubExportServerModule` |
| `Get Export Server Info` | 获取服务器的IP地址和端口信息，供捕获设备连接使用。 | `FLiveLinkHubExportServerModule` |
| `Register Export Server Handler` | 为特定客户端（设备）注册一个处理传入文件数据的委托。 | `FLiveLinkHubExportServerModule` |
| `Unregister Export Server Handler` | 取消注册某个客户端的处理器。 | `FLiveLinkHubExportServerModule` |

### 使用示例（蓝图描述）

1.  在游戏启动或蓝图初始化时，调用 `Start Export Server` 节点，传入一个未被占用的端口（如 `8080`）。
2.  使用 `Get Export Server Info` 获取服务器地址（如 `192.168.1.100:8080`），将此地址配置到你的 LiveLink Hub 或捕获设备上。
3.  为预期的客户端（例如一个特定设备的ID）调用 `Register Export Server Handler`，并绑定一个自定义事件或函数作为 `FFileDataHandler` 委托。
4.  在该委托中，你将收到 `FUploadDataHeader`（包含文件元数据）和一个 `FTcpClientHandler` 指针，你可以通过该指针接收实际的文件数据流并进行处理（如创建纹理、保存文件等）。

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkHubExportServerModule.h"
// 用于直接操作服务器实例和类型定义
#include "LiveLinkHubExportServer.h"
```

### 基本用法

通过模块单例管理导出服务器的生命周期。
（来源：`Public/LiveLinkHubExportServerModule.h`）

```cpp
#include "LiveLinkHubExportServerModule.h"

// 获取模块实例
FLiveLinkHubExportServerModule& ExportModule = FModuleManager::Get().LoadModuleChecked<FLiveLinkHubExportServerModule>(TEXT("LiveLinkHubExportServer"));

// 启动服务器
uint16 DesiredPort = 9090;
if (ExportModule.StartExportServer(DesiredPort))
{
    UE_LOG(LogTemp, Log, TEXT("Export Server started on port %d"), DesiredPort);
    
    // 获取并打印服务器信息
    auto InfoOrError = ExportModule.GetExportServerInfo();
    if (InfoOrError.HasValue())
    {
        FLiveLinkHubExportServer::FServerInfo Info = InfoOrError.GetValue();
        UE_LOG(LogTemp, Log, TEXT("Server info - IP: %s, Port: %d"), *Info.IPAddress, Info.Port);
    }
}

// 在模块关闭或不需要时停止服务器
ExportModule.StopExportServer();
```

### 进阶用法

注册一个文件处理器来接收并处理捕获设备推送的数据。
（来源：`Public/LiveLinkHubExportServer.h`, `Public/LiveLinkHubExportServerModule.h`）

```cpp
#include "LiveLinkHubExportServerModule.h"
#include "LiveLinkHubExportServer.h"

// 定义一个文件数据处理委托
FLiveLinkHubExportServer::FFileDataHandler FileDataHandler;
FileDataHandler.BindLambda([](FUploadDataHeader Header, TSharedPtr<UE::CaptureManager::FTcpClientHandler> ClientHandler) -> bool
{
    UE_LOG(LogTemp, Log, TEXT("Received file: %s, Size: %lld"), *Header.FileName, Header.FileSize);
    
    // 此处应实现从 ClientHandler 读取数据的逻辑，例如：
    // TArray<uint8> FileData;
    // int64 BytesRead = ClientHandler->Receive(FileData, Header.FileSize);
    // if (BytesRead == Header.FileSize)
    // {
    //     // 处理文件数据，例如创建纹理、保存到磁盘等
    //     SaveFileToProject(Header.FileName, FileData);
    //     return true; // 表示处理成功
    // }
    
    return false; // 表示处理失败
});

// 注册处理器
FString MyDeviceId = TEXT("MyCaptureDevice_001");
ExportModule.RegisterExportServerHandler(MyDeviceId, FileDataHandler);

// ... 在某个时刻，例如设备断开连接时，取消注册
ExportModule.UnregisterExportServerHandler(MyDeviceId);
```

## Demo 示例

一个最小化的服务器端监听和处理示例。

**LiveLinkExportServerDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "LiveLinkHubExportServerModule.h"
#include "LiveLinkHubExportServer.h"

class ULiveLinkExportServerDemo : public UObject
{
public:
    void Initialize();
    void Shutdown();

private:
    FFileDataHandler OnFileReceived;
    void HandleReceivedFile(FUploadDataHeader Header, TSharedPtr<UE::CaptureManager::FTcpClientHandler> Client);
};
```

**LiveLinkExportServerDemo.cpp**
```cpp
#include "LiveLinkExportServerDemo.h"

void ULiveLinkExportServerDemo::Initialize()
{
    // 绑定处理函数
    OnFileReceived.BindUObject(this, &ULiveLinkExportServerDemo::HandleReceivedFile);

    FLiveLinkHubExportServerModule& Module = FModuleManager::Get().LoadModuleChecked<FLiveLinkHubExportServerModule>(TEXT("LiveLinkHubExportServer"));
    if (Module.StartExportServer(8888))
    {
        Module.RegisterExportServerHandler(TEXT("DemoClient"), OnFileReceived);
        UE_LOG(LogTemp, Log, TEXT("LiveLink Export Server Demo initialized on port 8888."));
    }
}

void ULiveLinkExportServerDemo::Shutdown()
{
    FLiveLinkHubExportServerModule& Module = FModuleManager::Get().LoadModuleChecked<FLiveLinkHubExportServerModule>(TEXT("LiveLinkHubExportServer"));
    Module.UnregisterExportServerHandler(TEXT("DemoClient"));
    Module.StopExportServer();
}

void ULiveLinkExportServerDemo::HandleReceivedFile(FUploadDataHeader Header, TSharedPtr<UE::CaptureManager::FTcpClientHandler> Client)
{
    UE_LOG(LogTemp, Log, TEXT("Demo: Processing file '%s'"), *Header.FileName);
    // 在此处添加实际的文件接收和处理逻辑
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TCP` | 提供底层的TCP服务器（`FTcpServer`）和客户端处理（`FTcpClientHandler`）能力，是 `LiveLinkHubExportServer` 的网络通信核心。 |
| `LiveLinkHubWorkerManager` | 协调和管理来自 LiveLink Hub 的摄取任务工作线程，`LiveLinkHubExportServer` 可能依赖它来分发接收到的数据。 |
| `LiveLink` | LiveLink 系统核心框架，用于发现和管理 LiveLink Hub 设备。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `175468f6` | [CaptureManager] Generalize device terminology in DeviceBlueprint | 将设备蓝图中的术语泛化，提升通用性。 |
| 2026-04-30 | `63a844fc` | [CaptureManager] Move blocking ingest Blueprint APIs to a Blocking subcategory. | 将阻塞式摄取蓝图API移至独立子类别，改善蓝图组织。 |
| 2026-04-30 | `d6f72591` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 新增CaptureManagerDeviceBlueprint模块，用于设备蓝图功能。 |
| 2026-04-29 | `5a664506` | [Backout] - CL53274396 | 回滚了之前的某个改动。 |
| 2026-04-29 | `1c481042` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 首次尝试添加CaptureManagerDeviceBlueprint模块（后被回滚）。 |

### 维护评价

该插件处于**活跃维护**状态。
- **创建时间**：约1年前，属于较新的插件。
- **更新频率**：最近一次更新在2026年4月底，有连续的功能性提交，主要围绕新增 `CaptureManagerDeviceBlueprint` 模块和改进现有API的组织结构。
- **状态**：插件仍在开发中，功能持续迭代和完善。`EnabledByDefault=false` 表明它可能尚未被视为最终稳定版本，但功能已经可用。
- **推荐使用**：**推荐**用于虚拟制作流水线中需要自动化数据导入的场景。由于其活跃的开发状态，建议关注后续版本更新，API可能会有变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager)
- [官方文档]() (暂无)
- [测试用例]() (未在当前插件目录中发现标准测试文件)