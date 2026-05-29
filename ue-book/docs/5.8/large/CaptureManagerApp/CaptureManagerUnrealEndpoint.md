# Capture Manager Application

> The Capture Manager allows control and monitoring of the capture device, obtains and transcodes the data from the devices and upload the data for import to the UE

| 属性 | 值 |
|---|---|
| 中文名 | 采集管理器应用 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（LiveLink设备示例） |
| 模块 | `CaptureManagerEditor` (Runtime), `CaptureManagerSettings` (Runtime), `CaptureManagerUnrealEndpoint` (Runtime), `ExampleLiveLinkDevices` (Runtime), `IngestLiveLinkDevice` (Runtime), `LiveLinkCapabilities` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp) | |

## 用途

`CaptureManagerApp` 是一个虚拟制片（Virtual Production）插件，用于管理外部数据采集设备。其核心功能是建立与 Unreal Engine (UE) 或 Unreal Editor for Fortnite (UEFN) 实例的连接，从设备获取采集数据（如动作捕捉），进行转码处理，并将数据上传至 UE 实例以供导入使用。它解决了从采集设备到 UE 内容管线之间的数据桥接和工作流自动化问题。

`CaptureManagerUnrealEndpoint` 模块是该插件的关键部分，专门负责管理这些与 UE 实例的通信端点，实现端点的自动发现、连接状态管理以及高效的数据上传任务队列。

## 使用场景

- **动捕数据采集**：使用专业的动捕设备（如Xsens, OptiTrack）采集演员动作数据，并需要实时或批量地将数据发送到 UE 中的 Live Link 进行预览或录制。
- **大规模虚拟制片**：在需要将大量视频、图像或传感器数据从采集服务器上传到多个 UE 渲染节点的场景中。
- **自定义采集管线**：开发者需要构建一个自动化的数据采集和导入流程，其中采集管理器作为中央控制点。

## 蓝图用法

`UCaptureManagerUnrealEndpointManager` 类提供了蓝图友好的端点管理功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start` | 启动端点管理器，开始自动发现 UE/UEFN 实例。 | `UCaptureManagerUnrealEndpointManager` |
| `Stop` | 停止端点管理器。 | `UCaptureManagerUnrealEndpointManager` |
| `WaitForEndpointByHostName` | 阻塞等待，直到发现指定主机名的端点或超时。成功返回 `true`。 | `UCaptureManagerUnrealEndpointManager` |

### 使用示例（蓝图描述）

1.  **创建管理器实例**：在 Actor 或 Subsystem 中创建一个 `UCaptureManagerUnrealEndpointManager` 类型的变量。
2.  **启动发现**：在需要开始工作时（如 BeginPlay），调用 `Start` 节点。
3.  **等待并连接**：调用 `WaitForEndpointByHostName`，传入目标计算机的主机名（如“MyRenderPC”）和合理的超时时间（毫秒）。根据返回的布尔值判断连接是否成功建立。
4.  **停止**：在结束工作或卸载时调用 `Stop` 节点。

## C++ 用法

### 头文件引入

```cpp
#include “CaptureManagerUnrealEndpointModule.h” // 获取模块单例
#include “CaptureManagerUnrealEndpoint.h”       // FUnrealEndpoint, FTakeUploadTask
#include “CaptureManagerUnrealEndpointManager.h” // FUnrealEndpointManager
```

### 基本用法

**获取端点管理器**
通过模块单例获取全局的 `FUnrealEndpointManager`。

```cpp
// 获取模块实例
FCaptureManagerUnrealEndpointModule& Module = FModuleManager::Get().LoadModuleChecked<FCaptureManagerUnrealEndpointModule>(TEXT(“CaptureManagerUnrealEndpoint”));
TSharedRef<UE::CaptureManager::FUnrealEndpointManager> EndpointManager = Module.GetEndpointManager();

// 启动发现
EndpointManager->Start();
```
*来源：`Public/CaptureManagerUnrealEndpointModule.h`*

**等待特定端点**
阻塞等待直到发现特定条件的端点。

```cpp
// 等待主机名为 “RenderNode1” 的端点，超时 5000 毫秒
TOptional<TWeakPtr<UE::CaptureManager::FUnrealEndpoint>> EndpointOpt =
    EndpointManager->WaitForEndpoint(
        [](const UE::CaptureManager::FUnrealEndpoint& Endpoint) {
            return Endpoint.GetInfo().HostName == “RenderNode1”;
        },
        5000
    );

if (EndpointOpt.IsSet())
{
    TSharedPtr<UE::CaptureManager::FUnrealEndpoint> Endpoint = EndpointOpt->Pin();
    // 开始使用端点…
}
```
*来源：`Public/CaptureManagerUnrealEndpointManager.h`*

### 进阶用法

**向端点添加上传任务**
创建一个上传任务并将其添加到端点的队列中。

```cpp
// 假设已获取到 Endpoint (TSharedPtr<FUnrealEndpoint>)
FGuid TaskID = FGuid::NewGuid();
FGuid CaptureSourceID = FGuid::NewGuid();
FString TakeDirectory = FPaths::ProjectSavedDir() / TEXT(“CapturedTake”);
UE::CaptureManager::FTakeMetadata TakeMetadata; // 假设已填充元数据

TUniquePtr<UE::CaptureManager::FTakeUploadTask> UploadTask = MakeUnique<UE::CaptureManager::FTakeUploadTask>(
    TaskID,
    CaptureSourceID,
    TEXT(“MyCamera”),
    TakeDirectory,
    MoveTemp(TakeMetadata)
);

// 绑定进度和完成回调
UploadTask->Progressed().BindLambda([](double Progress) {
    UE_LOG(LogCaptureManagerUnrealEndpoint, Log, TEXT(“Upload Progress: %.2f%%”), Progress * 100.0);
});

UploadTask->Complete().BindLambda([](const FString& Message, int32 StatusCode) {
    if (StatusCode == 200) {
        UE_LOG(LogCaptureManagerUnrealEndpoint, Log, TEXT(“Upload Complete: %s”), *Message);
    } else {
        UE_LOG(LogCaptureManagerUnrealEndpoint, Error, TEXT(“Upload Failed (%d): %s”), StatusCode, *Message);
    }
});

// 添加到端点队列
if (!Endpoint->AddTakeUploadTask(MoveTemp(UploadTask)))
{
    UE_LOG(LogCaptureManagerUnrealEndpoint, Error, TEXT(“Failed to add upload task.”));
}
```
*来源：`Public/CaptureManagerUnrealEndpoint.h`*

## Demo 示例

一个最小的控制台应用示例，展示如何发现端点并触发一次数据上传。

**CaptureManagerDemo.h**
```cpp
#pragma once
#include “CoreMinimal.h”
#include “Modules/ModuleManager.h”

class FCaptureManagerDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
private:
    void RunDemo();
    TSharedPtr<UE::CaptureManager::FUnrealEndpointManager> EndpointManager;
};
```

**CaptureManagerDemo.cpp**
```cpp
#include “CaptureManagerDemo.h”
#include “CaptureManagerUnrealEndpointModule.h”
#include “CaptureManagerUnrealEndpointManager.h”
#include “CaptureManagerUnrealEndpoint.h”
#include “Misc/Paths.h”

#define LOCTEXT_NAMESPACE “FCaptureManagerDemoModule”

void FCaptureManagerDemoModule::StartupModule()
{
    // 获取端点管理器
    FCaptureManagerUnrealEndpointModule& CMModule = FModuleManager::Get().LoadModuleChecked<FCaptureManagerUnrealEndpointModule>(TEXT(“CaptureManagerUnrealEndpoint”));
    EndpointManager = CMModule.GetEndpointManager();
    
    // 启动发现并运行演示
    EndpointManager->Start();
    RunDemo();
}

void FCaptureManagerDemoModule::ShutdownModule()
{
    if (EndpointManager)
    {
        EndpointManager->Stop();
    }
}

void FCaptureManagerDemoModule::RunDemo()
{
    UE_LOG(LogTemp, Log, TEXT(“Waiting for a UE endpoint…”));
    TOptional<TWeakPtr<UE::CaptureManager::FUnrealEndpoint>> EndpointWeak = EndpointManager->WaitForEndpoint(
        [](const UE::CaptureManager::FUnrealEndpoint& Endpoint) { return true; }, // 匹配第一个发现的端点
        10000 // 10秒超时
    );

    if (EndpointWeak.IsSet())
    {
        TSharedPtr<UE::CaptureManager::FUnrealEndpoint> Endpoint = EndpointWeak->Pin();
        if (Endpoint)
        {
            // 启动与端点的连接
            Endpoint->StartConnection();
            if (Endpoint->WaitForConnectionState(UE::CaptureManager::FUnrealEndpoint::EConnectionState::Connected, 5000))
            {
                UE_LOG(LogTemp, Log, TEXT(“Connected to %s”), *Endpoint->GetInfo().HostName);

                // 创建并添加一个示例上传任务
                FString SampleDir = FPaths::ConvertRelativePathToFull(FPaths::ProjectContentDir() / TEXT(“SampleCapture”));
                UE::CaptureManager::FTakeMetadata SampleMetadata;
                // … 填充元数据 …
                TUniquePtr<UE::CaptureManager::FTakeUploadTask> Task = MakeUnique<UE::CaptureManager::FTakeUploadTask>(
                    FGuid::NewGuid(), FGuid::NewGuid(), TEXT(“DemoSource”), SampleDir, MoveTemp(SampleMetadata)
                );

                Endpoint->AddTakeUploadTask(MoveTemp(Task));
                UE_LOG(LogTemp, Log, TEXT(“Upload task added to queue.”));
            }
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT(“Timed out waiting for endpoint.”));
    }
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FCaptureManagerDemoModule, CaptureManagerDemo)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Discovery` | 用于网络服务发现（`FDiscoveryRequester`）。 |
| `LiveLinkInterface` | 处理 Live Link 相关数据结构和接口。 |

*（已省略 Core, CoreUObject, Engine, Messaging 等常见依赖）*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-29 | `7a2061c9` | [CaptureManager] Add CaptureManagerCPSClient module to CaptureManagerCore. | 添加CPS客户端模块以支持新的采集管线。 |
| 2026-04-28 | `6eba47f3` | [Capture Manager] Warn when Third Party Encoder is required for ingest | 当摄入需要第三方编码器时增加警告提示。 |
| 2026-04-20 | `a8e2df25` | [CaptureManager] Add auto-rotation mode to ECaptureManagerRotation | 为采集管理器的旋转枚举添加自动旋转模式。 |
| 2026-04-16 | `cf2dffa4` | [CaptureManager] Fix broken LLH encoder defaults. | 修复LiveLinkHub编码器默认设置损坏的问题。 |
| 2026-04-08 | `1b3e594c` | [CaptureManager] Improve error messages for ingest pipeline. | 改进摄入管线的错误信息，使其更清晰。 |

### 维护评价

该插件创建于 **2025年2月**，距今仅约一年，属于非常年轻的模块。从最近的 Git 提交记录来看，**维护非常活跃**（最近一次更新在2026年4月）。更新内容集中在功能增强（如新模式、新模块）、错误修复和用户体验优化上，表明 Epic Games 在其内部和对外发布的虚拟制片工具链中持续投入和开发。**强烈推荐**用于新的虚拟制片项目，因为它代表了 Epic 在此领域的最新实践和持续支持。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp/Source/CaptureManagerUnrealEndpoint/Tests)