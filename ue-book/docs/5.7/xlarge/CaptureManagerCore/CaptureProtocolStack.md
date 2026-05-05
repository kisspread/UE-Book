# Capture Manager Core

> The Capture Manager Core plugin contains utility modules that are shared between Capture Manager App plugin and Capture Manager Editor plugin.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（样式资产） |
| 模块 | `CaptureManagerStyle` (Runtime), `CaptureManagerTakeMetadata` (Runtime), `CaptureProtocolStack` (Runtime), `CaptureUtils` (Runtime), `DataIngestCore` (Runtime), `LiveLinkHubCaptureMessaging` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore) | |

## 用途

Capture Manager Core 是 Unreal 虚拟制片（Virtual Production）中 **Capture Manager** 系统的底层网络通信核心。它解决的核心问题是：**Unreal Engine 如何发现、控制和从捕获设备（如运行 Live Link Face 等应用的 iPhone）下载数据**。

该插件实现了三层网络协议栈：

1. **发现协议（Discovery Protocol）**：基于 UDP 多播，在局域网中自动发现捕获设备，获取设备 ID、名称和控制端口等信息，并监听设备上下线通知。

2. **控制协议（Control Protocol）**：基于 TCP 的 JSON-RPC 风格协议，用于管理捕获会话的完整生命周期——建立会话、开始/停止/中止录制、获取 Take 列表和元数据、订阅实时状态更新（录制状态、Take 变更、iOS 设备状态如电量/温度/磁盘容量等），并内置心跳保活机制。

3. **导出协议（Export Protocol）**：基于 TCP 的二进制协议，用于从捕获设备下载已录制的数据（Take 文件、视频帧、摄像头画面），支持事务 ID 追踪、文件偏移续传和 MD5 哈希校验，采用多线程工作队列实现高效并发导出。

该插件本身不直接面向最终用户，而是作为 Capture Manager App（连接 iOS 设备）和 Capture Manager Editor（编辑器内管理工具）两个上层插件的共享基础设施。

## 使用场景

- 你在做虚拟制片，需要用 iPhone 上的 Live Link Face 等应用捕获面部动画 → Capture Manager Core 提供发现和控制这些设备的协议
- 你需要在编辑器中管理多个捕获设备的录制会话、查看 Take 列表 → 控制协议提供完整的会话和 Take 管理 API
- 你需要从捕获设备批量下载录制好的视频和元数据 → 导出协议支持多文件并发下载和校验
- 你在开发自定义的捕获设备管理工具 → 可以直接使用底层的 DiscoveryMessenger、ControlMessenger、ExportClient

## 蓝图用法

该插件为纯 C++ 网络协议库，所有类均为原生 C++ 类（非 `UCLASS`），**不暴露任何蓝图节点**。如需在蓝图中使用捕获管理功能，请使用上层的 Capture Manager Editor 插件，该插件提供了蓝图友好的封装。

## C++ 用法

### 头文件引入

```cpp
// 发现协议
#include "Discovery/DiscoveryMessenger.h"

// 控制协议
#include "Control/ControlMessenger.h"
#include "Control/Messages/ControlRequest.h"
#include "Control/Messages/ControlResponse.h"
#include "Control/Messages/ControlUpdate.h"

// 导出协议
#include "ExportClient/ExportClient.h"
```

### 基本用法：设备发现

使用 `FDiscoveryMessenger` 在局域网中搜索捕获设备：

```cpp
using namespace UE::CaptureManager;

// 创建发现信使
FDiscoveryMessenger DiscoveryMessenger;

// 启动 UDP 监听
TProtocolResult<void> StartResult = DiscoveryMessenger.Start();
if (StartResult.HasError())
{
    UE_LOG(LogTemp, Error, TEXT("Failed to start discovery"));
    return;
}

// 设置响应处理器——当设备回复发现请求时触发
DiscoveryMessenger.SetResponseHandler(
    [](FString ServerIp, FDiscoveryResponse Response)
    {
        FString ServerName = Response.GetServerName();
        uint16 ControlPort = Response.GetControlPort();
        UE_LOG(LogTemp, Log, TEXT("Found device: %s at %s:%d"), *ServerName, *ServerIp, ControlPort);
    }
);

// 设置通知处理器——当设备状态变化时触发（上线/下线）
DiscoveryMessenger.SetNotifyHandler(
    [](FString ServerIp, FDiscoveryNotify Notify)
    {
        bool bOnline = Notify.GetConnectionState() == FDiscoveryNotify::EConnectionState::Online;
        UE_LOG(LogTemp, Log, TEXT("Device %s is now %s"), *Notify.GetServerName(), bOnline ? TEXT("Online") : TEXT("Offline"));
    }
);

// 发送多播发现请求
DiscoveryMessenger.SendRequest();

// ... 使用完毕后停止
DiscoveryMessenger.Stop();
```

### 基本用法：控制会话

使用 `FControlMessenger` 连接设备并管理录制会话：

```cpp
using namespace UE::CaptureManager;

FControlMessenger ControlMessenger;

// 注册断连处理器
ControlMessenger.RegisterDisconnectHandler(
    [](const FString& Cause)
    {
        UE_LOG(LogTemp, Warning, TEXT("Disconnected: %s"), *Cause);
    }
);

// 注册更新处理器——订阅录制状态变更
ControlMessenger.RegisterUpdateHandler(
    CPS::AddressPaths::GRecordingStatus,
    FControlUpdate::FOnUpdateMessage::CreateLambda(
        [](TSharedPtr<FControlUpdate> Update)
        {
            if (auto* RecordingUpdate = static_cast<FRecordingStatusUpdate*>(Update.Get()))
            {
                UE_LOG(LogTemp, Log, TEXT("Recording: %s"), RecordingUpdate->IsRecording() ? TEXT("Yes") : TEXT("No"));
            }
        }
    )
);

// 连接到设备
TProtocolResult<void> ConnectResult = ControlMessenger.Start(ServerIp, ControlPort);
if (ConnectResult.HasError())
{
    UE_LOG(LogTemp, Error, TEXT("Failed to connect"));
    return;
}

// 获取服务器信息
TProtocolResult<FGetServerInformationResponse> InfoResult = ControlMessenger.GetServerInformation();
if (!InfoResult.HasError())
{
    const auto& Info = InfoResult.GetValue();
    UE_LOG(LogTemp, Log, TEXT("Server: %s, Software: %s %s"),
        *Info.GetName(), *Info.GetSoftwareName(), *Info.GetSoftwareVersion());
}

// 开始会话
TProtocolResult<FStartSessionResponse> SessionResult = ControlMessenger.StartSession();
if (!SessionResult.HasError())
{
    FString SessionId = SessionResult.GetValue().GetSessionId();
    UE_LOG(LogTemp, Log, TEXT("Session started: %s"), *SessionId);
}

// 获取 Take 列表
TProtocolResult<FGetTakeListResponse> TakeListResult = ControlMessenger.GetTakeList();
if (!TakeListResult.HasError())
{
    // 处理 Take 列表
}

// 发送自定义请求（模板化 API）
FStartRecordingTakeRequest RecordRequest(TEXT("Slate01"), 1);
auto RecordResult = ControlMessenger.SendRequest(RecordRequest);
if (!RecordResult.HasError())
{
    UE_LOG(LogTemp, Log, TEXT("Recording started"));
}

// ... 使用完毕后停止
ControlMessenger.Stop();
```

### 基本用法：导出数据

使用 `FExportClient` 从设备下载录制数据：

```cpp
using namespace UE::CaptureManager;

// 创建导出客户端（需要设备的导出端口，从 GetServerInformation 获取）
FExportClient ExportClient(ServerIp, ExportPort);

// 准备要导出的文件列表
TArray<FTakeFile> TakeFiles;
FTakeFile File;
File.FileName = TEXT("video.mp4");
File.Length = 0;  // 由服务器决定
File.Offset = 0;
TakeFiles.Add(File);

// 创建输出流（写入本地文件）
TUniquePtr<FBaseStream> Stream = MakeUnique<FFileStream>(TEXT("/path/to/output/"));

// 提交导出任务
FExportClient::FTaskId TaskId = ExportClient.ExportTakeFiles(TEXT("TakeName"), MoveTemp(TakeFiles), MoveTemp(Stream));

// 如需取消
ExportClient.AbortExport(TaskId);
```

### 进阶用法：批量导出多个 Take

```cpp
using namespace UE::CaptureManager;

FExportClient ExportClient(ServerIp, ExportPort);

// 构建多 Take 导出映射
TMap<FString, TArray<FTakeFile>> TakesFilesMap;

TArray<FTakeFile> Files1;
Files1.Add({ TEXT("video.mp4"), 0, 0 });
Files1.Add({ TEXT("metadata.json"), 0, 0 });
TakesFilesMap.Add(TEXT("Take_Slate01_001"), MoveTemp(Files1));

TArray<FTakeFile> Files2;
Files2.Add({ TEXT("video.mp4"), 0, 0 });
TakesFilesMap.Add(TEXT("Take_Slate01_002"), MoveTemp(Files2));

// 批量导出
TUniquePtr<FBaseStream> Stream = MakeUnique<FFileStream>(TEXT("/path/to/output/"));
FExportClient::FTaskId TaskId = ExportClient.ExportFiles(MoveTemp(TakesFilesMap), MoveTemp(Stream));

// 取消所有导出
ExportClient.AbortAllExports();
```

### 进阶用法：自定义控制请求

利用模板化的 `SendRequest` 发送任意控制请求：

```cpp
using namespace UE::CaptureManager;

// 获取 Take 元数据
FGetTakeMetadataRequest MetadataRequest(TEXT("Take_Slate01_001"));
auto MetadataResult = ControlMessenger.SendRequest(MetadataRequest);

// 开始流式传输
FStartStreamingRequest StreamRequest(/* subject IDs */);
auto StreamResult = ControlMessenger.SendRequest(StreamRequest);

// 订阅设备事件
FSubscribeRequest SubscribeRequest;
auto SubscribeResult = ControlMessenger.SendRequest(SubscribeRequest);
```

## Demo 示例

以下是一个完整的最小示例，展示发现设备、建立控制会话并开始录制的流程：

```cpp
// CaptureManagerDemo.h
#pragma once

#include "CoreMinimal.h"

class FCaptureManagerDemo
{
public:
    void DiscoverDevices();
    void ConnectAndRecord(const FString& InServerIp, uint16 InControlPort);

private:
    void OnDeviceFound(FString ServerIp, class FDiscoveryResponse Response);
    void OnRecordingUpdate(TSharedPtr<class FControlUpdate> Update);

    TUniquePtr<class FDiscoveryMessenger> DiscoveryMessenger;
    TUniquePtr<class FControlMessenger> ControlMessenger;
};
```

```cpp
// CaptureManagerDemo.cpp
#include "CaptureManagerDemo.h"

#include "Discovery/DiscoveryMessenger.h"
#include "Control/ControlMessenger.h"
#include "Control/Messages/ControlRequest.h"
#include "Control/Messages/ControlUpdate.h"
#include "Control/Messages/Constants.h"

using namespace UE::CaptureManager;

void FCaptureManagerDemo::DiscoverDevices()
{
    DiscoveryMessenger = MakeUnique<FDiscoveryMessenger>();

    DiscoveryMessenger->SetResponseHandler(
        FDiscoveryMessenger::FOnResponseArrived::CreateRaw(this, &FCaptureManagerDemo::OnDeviceFound)
    );

    DiscoveryMessenger->Start();
    DiscoveryMessenger->SendRequest();
}

void FCaptureManagerDemo::OnDeviceFound(FString ServerIp, FDiscoveryResponse Response)
{
    UE_LOG(LogTemp, Log, TEXT("Found: %s (%s) on port %d"),
        *Response.GetServerName(), *ServerIp, Response.GetControlPort());

    // 发现设备后自动连接
    ConnectAndRecord(ServerIp, Response.GetControlPort());
}

void FCaptureManagerDemo::ConnectAndRecord(const FString& InServerIp, uint16 InControlPort)
{
    ControlMessenger = MakeUnique<FControlMessenger>();

    // 注册录制状态更新
    ControlMessenger->RegisterUpdateHandler(
        CPS::AddressPaths::GRecordingStatus,
        FControlUpdate::FOnUpdateMessage::CreateRaw(this, &FCaptureManagerDemo::OnRecordingUpdate)
    );

    // 连接
    if (ControlMessenger->Start(InServerIp, InControlPort).HasError())
    {
        UE_LOG(LogTemp, Error, TEXT("Connection failed"));
        return;
    }

    // 开始会话
    auto SessionResult = ControlMessenger->StartSession();
    if (SessionResult.HasError())
    {
        UE_LOG(LogTemp, Error, TEXT("Session start failed"));
        return;
    }

    // 开始录制
    FStartRecordingTakeRequest Request(TEXT("DemoSlate"), 1);
    auto RecordResult = ControlMessenger->SendRequest(Request);
    if (RecordResult.HasError())
    {
        UE_LOG(LogTemp, Error, TEXT("Recording start failed"));
    }
}

void FCaptureManagerDemo::OnRecordingUpdate(TSharedPtr<FControlUpdate> Update)
{
    if (auto* RecUpdate = static_cast<FRecordingStatusUpdate*>(Update.Get()))
    {
        UE_LOG(LogTemp, Log, TEXT("Recording status: %s"),
            RecUpdate->IsRecording() ? TEXT("ACTIVE") : TEXT("STOPPED"));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Json` | 控制协议的 JSON 序列化/反序列化 |
| `Sockets` | 底层 TCP/UDP 套接字操作（被插件内部 Network 层封装） |
| `Networking` | IP 地址类型（FIPv4Endpoint 等） |

无特殊依赖（仅标准 Core/Engine/Slate 等 + 上述网络/JSON 模块）。

## 维护状态

### 近期更新

```
- 8a5633e01da9 Handling GetTakeList response should check for take name uniqueness
  → 修复 GetTakeList 响应处理中 Take 名称唯一性校验的问题
- 2d11f4ac205b Invalid finalize at the hash error
  → 修复哈希校验出错时的无效 finalize 操作
- 2739c3d30ebc Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 4/n
  → 代码规范化：修正 DLL 导出标记（UE_API）的正确位置
```

### 维护评价

- **创建时间**：2025 年 2 月，是一个非常新的插件
- **维护状态**：活跃维护中。近期 commit 包含功能性 bug 修复和代码规范化，表明 Epic 正在积极开发
- **实验性标记**：`IsBetaVersion=true`，`EnabledByDefault=false`，说明该插件仍处于 Beta 阶段，API 可能发生变化
- **已知限制**：
  - 5.6 版本中废弃了 `SupportedVersions` 相关接口（`FDiscoveryResponse`、`FDiscoveryNotify` 中标记了 `UE_DEPRECATED(5.6, ...)`），说明协议仍在演进
  - 作为底层协议库，不提供蓝图接口，仅限 C++ 使用
- **推荐程度**：如果你在开发虚拟制片捕获工具，这是必经之路。但需注意 API 稳定性风险，建议锁定引擎版本使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore)
- 官方文档（无）
- 测试用例（未在插件目录内发现独立测试文件）