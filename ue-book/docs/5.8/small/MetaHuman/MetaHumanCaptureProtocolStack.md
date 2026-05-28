# MetaHuman Capture Protocol Stack

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman捕获协议栈 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（代码库、测试资源） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🏛️ 文物（约 N 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHumanCaptureProtocolStack 是 MetaHuman Animator 插件中的一个模块，**该模块已被官方废弃**。它实现了一套用于 Unreal Engine 与外部捕获设备（如运行 Live Link Face 应用的 iOS 设备）通信的协议栈。

从源码分析，该模块的核心功能是实现一个基于 JSON-RPC 的客户端/服务器通信协议，用于：
1.  **设备发现**：通过 UDP 多播在网络上发现可用的捕获设备。
2.  **会话控制**：与捕获设备建立 TCP 连接，管理捕获会话的生命周期（开始、停止、保活）。
3.  **数据管理**：控制录制、获取 Take 列表和元数据。
4.  **数据导出**：通过独立的 TCP 通道从设备导出录制好的视频和音频数据。

**重要提示**：所有公共 API 都标记为 `UE_DEPRECATED(5.7, "...")`，表明此功能已被迁移到新的 `CaptureManagerCore/CaptureProtocolStack` 模块。新项目应避免使用此模块。

## 使用场景

-   你需要开发一个自定义工具，与运行 Live Link Face 的 iOS 设备进行底层协议通信（但请注意该模块已废弃，应使用新模块）。
-   你正在维护一个旧版本的 MetaHuman Animator 工作流，且未升级到包含新模块的引擎版本。
-   你想了解 MetaHuman 捕获协议的底层实现细节作为学习参考。

## 蓝图用法

在提供的源码中，`MetaHumanCaptureProtocolStack` 模块的头文件（`.h`）主要定义了底层的 C++ 通信类（如 `FControlMessenger`, `FDiscoveryMessenger`, `FExportClient`），**没有发现任何 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 标记**。

这表明该模块是一个纯 C++ 的协议实现库，**不直接提供蓝图可调用的节点**。所有交互都需要在 C++ 层面完成。更高层的 MetaHuman Animator 蓝图功能可能由插件中的其他模块（如 `MetaHumanPipeline`, `MetaHumanToolkit`）提供，但这些不在本次文档范围内。

## C++ 用法

### 头文件引入

根据要使用的功能，引入对应的头文件：
```cpp
// 控制协议（会话管理、录制控制）
#include "Control/ControlMessenger.h"
#include "Control/Messages/ControlRequest.h"
#include "Control/Messages/ControlResponse.h"

// 设备发现
#include "Discovery/DiscoveryMessenger.h"
#include "Discovery/Messages/DiscoveryNotify.h"
#include "Discovery/Messages/DiscoveryResponse.h"

// 数据导出
#include "ExportClient/ExportClient.h"
```

### 基本用法 (设备发现与控制)

以下是一个简化的示例，展示如何发现设备并获取服务器信息。**此模块已废弃，代码仅作参考**。

```cpp
// 来源: 模块接口设计分析
#include "Discovery/DiscoveryMessenger.h"
#include "Control/ControlMessenger.h"

// 1. 发现设备
FDiscoveryMessenger DiscoveryMessenger;
DiscoveryMessenger.SetResponseHandler(
    FDiscoveryMessenger::FOnResponseArrived::CreateLambda(
        [](const FDiscoveryResponse& InResponse)
        {
            UE_LOG(LogTemp, Log, TEXT("Found device at control port: %u"), InResponse.GetControlPort());
            // 使用 InResponse.GetServerId() 和 InResponse.GetControlPort() 建立控制连接
        }
    )
);

if (TProtocolResult<void> Result = DiscoveryMessenger.Start(); Result.IsError())
{
    UE_LOG(LogTemp, Error, TEXT("Failed to start discovery: %s"), *Result.ClaimError().GetMessage());
    return;
}

DiscoveryMessenger.SendMulticastRequest(); // 发送多播请求

// 2. 建立控制连接 (假设已知服务器IP和端口)
FControlMessenger ControlMessenger;
if (TProtocolResult<void> Result = ControlMessenger.Start(TEXT("192.168.1.100"), 14221); Result.IsError())
{
    UE_LOG(LogTemp, Error, TEXT("Failed to connect: %s"), *Result.ClaimError().GetMessage());
    return;
}

// 3. 开始会话并查询信息
if (TProtocolResult<void> Result = ControlMessenger.StartSession(); Result.IsError())
{
    UE_LOG(LogTemp, Error, TEXT("Failed to start session: %s"), *Result.ClaimError().GetMessage());
    return;
}

TProtocolResult<FGetServerInformationResponse> InfoResult = ControlMessenger.GetServerInformation();
if (InfoResult.IsValid())
{
    const FGetServerInformationResponse& ServerInfo = InfoResult.GetResult();
    UE_LOG(LogTemp, Log, TEXT("Server: %s, Software: %s %s"),
        *ServerInfo.GetName(), *ServerInfo.GetSoftwareName(), *ServerInfo.GetSoftwareVersion());
}

// 注意：实际使用中需要正确处理异步回调和生命周期管理。
```

### 进阶用法 (异步请求与数据导出)

`FControlMessenger` 支持异步请求。`FExportClient` 用于从设备导出数据文件。

```cpp
// 来源: 模块接口设计分析
// 异步获取 Take 列表
FControlMessenger ControlMessenger; // 假设已连接并开始会话
ControlMessenger.SendAsyncRequest<FGetTakeListRequest>(
    FGetTakeListRequest(),
    FControlMessenger::FOnControlResponse<FGetTakeListRequest>::CreateLambda(
        [](TProtocolResult<FGetTakeListResponse> InResult)
        {
            if (InResult.IsValid())
            {
                const TArray<FString>& TakeNames = InResult.GetResult().GetNames();
                for (const FString& Name : TakeNames)
                {
                    UE_LOG(LogTemp, Log, TEXT("Take: %s"), *Name);
                }
            }
        }
    )
);

// 导出一个 Take 的视频文件
// 1. 先获取 Take 的元数据，得到文件信息
// 2. 创建导出客户端并开始导出
FExportClient ExportClient(TEXT("192.168.1.100"), ServerInfo.GetExportPort());
TArray<FTakeFile> FilesToExport;
// ... 根据元数据填充 FilesToExport ...

// 使用自定义的流处理器接收数据
class FMyStreamProcessor : public FBaseStream
{
    virtual bool StartFile(const FString& InTakeName, const FString& InFileName) override { /*...*/ return true; }
    virtual bool ProcessData(const FString& InTakeName, const FString& InFileName, const TConstArrayView<uint8>& InData) override { /*...*/ return true; }
    virtual bool FinishFile(const FString& InTakeName, const FString& InFileName, const TStaticArray<uint8, 16>& InHash) override { /*...*/ return true; }
    virtual void Done(TProtocolResult<void> InResult) override { /*...*/ }
};

ExportClient.ExportTakeFiles(
    TEXT("Take_001"),
    FilesToExport,
    MakeUnique<FMyStreamProcessor>()
);
```

## Demo 示例

一个最小的、编译可能通过但需要连接真实设备的示例框架。

```cpp
// MyCaptureProtocolDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyCaptureProtocolDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    // 持有协议栈实例的指针（示例中未实际使用，需根据生命周期管理）
};
```

```cpp
// MyCaptureProtocolDemo.cpp
#include "MyCaptureProtocolDemo.h"

// 引入所需的协议栈头文件
#include "Discovery/DiscoveryMessenger.h"
#include "Control/ControlMessenger.h"

#define LOCTEXT_NAMESPACE "FMyCaptureProtocolDemoModule"

void FMyCaptureProtocolDemoModule::StartupModule()
{
    // 在此可以初始化协议栈组件
    UE_LOG(LogTemp, Log, TEXT("MyCaptureProtocolDemo Module Started"));
}

void FMyCaptureProtocolDemoModule::ShutdownModule()
{
    // 在此清理资源
    UE_LOG(LogTemp, Log, TEXT("MyCaptureProtocolDemo Module Shutdown"));
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyCaptureProtocolDemoModule, MyCaptureProtocolDemo)
```

## 模块依赖

根据 `MetaHumanCaptureProtocolStack.Build.cs` 及相关模块分析，该模块**没有特殊依赖**，主要依赖 Unreal Engine 核心模块。

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | 基础引擎功能、网络、JSON 解析、线程管理等 |

**注意**：使用整个 MetaHuman Animator 插件中的其他模块（如 `MetaHumanIdentity`）会有额外的依赖要求。

## 维护状态

### 近期更新

以下 git 记录针对整个 `Engine/Plugins/MetaHuman/MetaHumanAnimator/` 目录。

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

-   **创建时间**：未知，但模块功能明确。
-   **最近更新频率**：近期（2026年5月）有活跃提交，但主要针对 MetaHuman Animator 的其他功能（如身体追踪、Sequencer、渲染），**并非针对 `MetaHumanCaptureProtocolStack` 模块本身**。
-   **活跃维护状态**：**该模块已正式废弃**。所有核心 API 都标记为 `UE_DEPRECATED(5.7)`，并指向新的 `CaptureManagerCore/CaptureProtocolStack` 模块。虽然整个 MetaHuman Animator 插件仍在维护，但此特定模块已被新实现替代。
-   **已知问题或限制**：不兼容 UE 5.7+ 的新捕获管理器工作流。使用此模块将导致编译警告，并可能在未来引擎版本中被移除。
-   **使用建议**：**不推荐新项目使用**。对于需要捕获协议功能的新开发，应使用 `CaptureManagerCore` 插件。仅在维护需要兼容旧版 MetaHuman Animator 工作流的遗留项目时，才可能需要接触此模块。

## 相关链接

-   [源码 (Tree)](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCaptureProtocolStack)
-   [官方文档]() (.uplugin 中 DocsURL 为空)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCaptureProtocolStack/Tests) (Private/Tests 目录下)