# MetaHuman Capture Protocol Stack

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 捕获协议栈 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MetaHumanCaptureProtocolStack` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 N 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCaptureProtocolStack) | |

## 用途

该模块实现了 **Capture Protocol Stack (CPS)** 协议。这是一个网络通信协议栈，专门用于**发现、连接和控制**外部的捕获设备（例如运行在 iPhone 上的 Live Link Face 应用）。

它的核心职责是：
1.  **设备发现**：通过 UDP 多播在网络上发现可用的 CPS 服务器。
2.  **控制会话**：通过 TCP 建立稳定的控制连接，用于管理捕获会话（开始/停止会话、开始/停止/中止录制、查询录制状态、获取 Take 列表和元数据）。
3.  **数据导出**：通过另一个 TCP 连接，将设备上录制的 Take 数据（视频、音频等）安全地传输到 UE 编辑器中。

它是 **MetaHuman Animator** 工作流中，连接外部物理捕获设备与 Unreal Engine 的关键基础设施。

## 使用场景

-   你在使用 **MetaHuman Animator** 工作流，需要从 **iPhone** 上的 **Live Link Face** 应用实时获取面部动画捕获数据。
-   你需要**批量管理**多个捕获设备的录制会话，例如开始录制、查询设备状态、获取录制好的 Take 列表。
-   你需要将设备上录制的高质量视频和音频文件**自动化地导出**到 UE 项目中，用于后续的 MetaHuman 面部动画解算。
-   你正在开发一个**自定义的捕获设备应用**，并希望它能够与 Unreal Engine 的 MetaHuman 工具链无缝集成。

## 蓝图用法

**注意：** `MetaHumanCaptureProtocolStack` 主要是一个**运行时 C++ 模块**，为上层编辑器工具（如 `MetaHumanCaptureSource`、`MetaHumanCaptureDataEditor`）提供底层通信能力。它本身暴露给蓝图的 API 非常有限。

其核心功能（如 `FControlMessenger`、`FExportClient`）在 C++ 层面使用，用于构建上层编辑器 UI 和工作流。蓝图开发者通常通过 MetaHuman Animator 的编辑器窗口间接使用其功能，而非直接调用此模块的蓝图节点。

## C++ 用法

本模块提供了底层的 C++ 类来实现 CPS 协议。以下是基于源码的典型使用模式。

### 头文件引入

```cpp
#include "MetaHumanCaptureProtocolStack.h"
// 通常还需要包含具体的子模块头文件，例如：
#include "Control/Messages/Constants.h"
#include "Control/ControlMessenger.h"
#include "ExportClient/ExportClient.h"
```

### 基本用法

连接设备并查询服务器信息。

```cpp
// 1. 创建并初始化控制通信器 (FControlMessenger)
UE::CPS::FControlMessenger ControlMessenger;

// 2. 注册更新消息处理器（可选，用于接收设备状态变化通知）
ControlMessenger.RegisterUpdateHandler(UE::CPS::AddressPaths::GRecordingStatus,
    [](TSharedPtr<UE::CPS::FControlUpdate> InUpdate) {
        // 处理录制状态更新...
    });

// 3. 启动连接（IP和端口通常从设备发现阶段获得）
const FString ServerIP = TEXT("192.168.1.100");
const uint16 ControlPort = 14567;
auto Result = ControlMessenger.Start(ServerIP, ControlPort);
if (Result.IsError()) {
    UE_LOG(LogTemp, Error, TEXT("Failed to start control messenger: %s"), *Result.ClaimError().GetMessage());
    return;
}

// 4. 开始会话
auto SessionResult = ControlMessenger.StartSession();
if (SessionResult.IsError()) {
    // 处理错误
}

// 5. 发送请求并获取服务器信息
auto ServerInfoResult = ControlMessenger.GetServerInformation();
if (ServerInfoResult.IsValid()) {
    const auto& ServerInfo = ServerInfoResult.GetResult();
    UE_LOG(LogTemp, Log, TEXT("Connected to: %s (%s)"), *ServerInfo.GetName(), *ServerInfo.GetPlatformName());
}

// 6. 完成后停止
ControlMessenger.Stop();
```

### 进阶用法

异步发送控制请求并处理响应。

```cpp
// 创建一个录制 Take 的请求
UE::CPS::FStartRecordingTakeRequest RecordTakeRequest(
    TEXT("MySlate"),     // Slate名称
    1,                   // Take编号
    TEXT("MySubject"),   // 主体（可选）
    TEXT("MyScenario"),  // 场景（可选）
    TArray<FString>{TEXT("TestTag")} // 标签（可选）
);

// 异步发送请求，并在回调中处理结果
ControlMessenger.SendAsyncRequest(RecordTakeRequest,
    UE::CPS::FControlMessenger::FOnControlResponse<UE::CPS::FStartRecordingTakeRequest>::CreateLambda(
        [](TProtocolResult<UE::CPS::FStartRecordingTakeResponse> InResult) {
            if (InResult.IsValid()) {
                UE_LOG(LogTemp, Log, TEXT("Recording started successfully."));
            } else {
                UE_LOG(LogTemp, Error, TEXT("Failed to start recording: %s"), *InResult.ClaimError().GetMessage());
            }
        })
);
```

## Demo 示例

一个最小的示例，展示如何初始化捕获协议栈并进行设备发现。

```cpp
// MyCaptureDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Discovery/DiscoveryMessenger.h"

class FMyCaptureDemo
{
public:
    void StartDiscovery();
    void StopDiscovery();

private:
    void OnServerDiscovered(UE::CPS::FDiscoveryResponse InResponse);
    void OnServerNotify(UE::CPS::FDiscoveryNotify InNotify);

    TUniquePtr<UE::CPS::FDiscoveryMessenger> DiscoveryMessenger;
};
```

```cpp
// MyCaptureDemo.cpp
#include "MyCaptureDemo.h"
#include "Discovery/Messages/DiscoveryResponse.h"
#include "Discovery/Messages/DiscoveryNotify.h"

void FMyCaptureDemo::StartDiscovery()
{
    DiscoveryMessenger = MakeUnique<UE::CPS::FDiscoveryMessenger>();

    // 注册设备响应和通知处理器
    DiscoveryMessenger->SetResponseHandler(
        UE::CPS::FDiscoveryMessenger::FOnResponseArrived::CreateRaw(
            this, &FMyCaptureDemo::OnServerDiscovered));
    DiscoveryMessenger->SetNotifyHandler(
        UE::CPS::FDiscoveryMessenger::FOnNotifyArrived::CreateRaw(
            this, &FMyCaptureDemo::OnServerNotify));

    // 启动发现服务
    auto Result = DiscoveryMessenger->Start();
    if (Result.IsError()) {
        UE_LOG(LogTemp, Error, TEXT("Failed to start discovery: %s"), *Result.ClaimError().GetMessage());
        return;
    }

    // 发送多播请求
    Result = DiscoveryMessenger->SendMulticastRequest();
    if (Result.IsError()) {
        UE_LOG(LogTemp, Error, TEXT("Failed to send discovery request: %s"), *Result.ClaimError().GetMessage());
    }
}

void FMyCaptureDemo::StopDiscovery()
{
    if (DiscoveryMessenger.IsValid()) {
        DiscoveryMessenger->Stop();
        DiscoveryMessenger.Reset();
    }
}

void FMyCaptureDemo::OnServerDiscovered(UE::CPS::FDiscoveryResponse InResponse)
{
    // 收到服务器对发现请求的响应
    UE_LOG(LogTemp, Log, TEXT("Discovered server on port: %d"), InResponse.GetControlPort());
    // 通常在此处记录服务器的IP和ControlPort，用于后续的FControlMessenger连接
}

void FMyCaptureDemo::OnServerNotify(UE::CPS::FDiscoveryNotify InNotify)
{
    // 收到服务器的主动通知（例如上线/下线状态变更）
    if (InNotify.GetConnectionState() == UE::CPS::FDiscoveryNotify::EConnectionState::Online) {
        UE_LOG(LogTemp, Log, TEXT("Server came online."));
    } else {
        UE_LOG(LogTemp, Log, TEXT("Server went offline."));
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体跟踪时禁用关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体跟踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

-   **活跃维护**：最近（2026年5月）有连续的功能更新和 Bug 修复，表明该模块正处于**活跃开发和维护**阶段。
-   **功能演进**：更新内容涉及身体跟踪支持、数据导出优化和渲染修复，显示其功能在不断扩展和优化。
-   **重要性**：作为 MetaHuman Animator 工作流的核心通信层，它被 Epic Games 官方持续维护。
-   **已知限制**：所有公开 API 均标记为 `UE_DEPRECATED(5.7, ...)`，表明该模块的功能已被迁移到新的 `CaptureManagerCore/CaptureProtocolStack` 模块中。**在 UE 5.7 及以后版本中，应使用新模块**。当前版本（5.8）仍可使用，但属于维护状态。
-   **推荐**：对于 UE 5.6 及以下版本的项目，如果需要完整的 MetaHuman Animator 捕获工作流，**推荐使用**此模块。对于 UE 5.7+ 的新项目，建议查找并使用新的 `CaptureManagerCore/CaptureProtocolStack` 模块。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCaptureProtocolStack)
-   [官方文档]() (暂无)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCaptureProtocolStack/Private/Tests)