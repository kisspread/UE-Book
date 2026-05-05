# Capture Manager Application

> The Capture Manager allows control and monitoring of the capture device, obtains and transcodes the data from the devices and upload the data for import to the UE

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例设备、设置资产） |
| 模块 | `CaptureDataConverter` (Runtime), `CaptureManagerEditor` (Runtime), `CaptureManagerMediaRW` (Runtime), `CaptureManagerPipeline` (Runtime), `CaptureManagerSettings` (Runtime), `CaptureManagerUnrealEndpoint` (Runtime), `ExampleLiveLinkDevices` (Runtime), `IngestLiveLinkDevice` (Runtime), `LiveLinkCapabilities` (Runtime), `LiveLinkFaceMetadata` (Runtime), `StereoCameraMetadata` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp) | |

---

## 用途

Capture Manager 是一个面向虚拟制片（Virtual Production）的**端到端捕获数据管理工具**。它解决的核心问题是：在使用 iPhone（LiveLink Face App）等设备进行面部/身体动作捕捉时，如何高效地发现设备、获取捕获数据、转码处理、并将数据上传到 Unreal Engine 实例中进行导入。

整个插件由 11 个模块组成，覆盖了从设备发现到数据导入的完整管线：

| 模块 | 职责 |
|---|---|
| **CaptureManagerUnrealEndpoint** | 发现并管理网络上的 UE/UEFN 实例（作为数据导入端点） |
| **CaptureManagerPipeline** | 数据处理管线，协调捕获、转码、上传流程 |
| **CaptureDataConverter** | 将捕获的原始数据转换为 UE 可用格式 |
| **CaptureManagerMediaRW** | 媒体数据的读写操作 |
| **CaptureManagerSettings** | 插件配置与设置 |
| **CaptureManagerEditor** | 编辑器 UI 集成（尽管标记为 Runtime） |
| **IngestLiveLinkDevice** | 用于数据导入的 LiveLink 设备实现 |
| **LiveLinkCapabilities** | LiveLink 能力定义 |
| **LiveLinkFaceMetadata** | LiveLink Face 捕获的元数据解析 |
| **StereoCameraMetadata** | 立体相机捕获的元数据解析 |
| **ExampleLiveLinkDevices** | 示例 LiveLink 设备实现，供开发者参考 |

## 使用场景

- 你在使用 iPhone + LiveLink Face App 进行面部动作捕捉 → 用 Capture Manager 管理整个数据采集和导入流程
- 你需要将捕获的 Take 数据批量上传到多个 UE 实例 → 用 CaptureManagerUnrealEndpoint 发现并连接端点
- 你在搭建虚拟制片管线，需要自动化捕获数据的转码和导入 → 用 CaptureManagerPipeline 协调流程
- 你需要解析 LiveLink Face 导出的元数据文件 → 用 LiveLinkFaceMetadata 模块

---

## 子模块文档

> 本文档为汇总页。由于插件规模较大（xlarge，258 个源文件），以下按模块分别说明。当前仅提供 `CaptureManagerUnrealEndpoint` 模块的详细文档，其余模块待补充。

---

## CaptureManagerUnrealEndpoint 模块

### 模块概述

`CaptureManagerUnrealEndpoint` 负责**发现和管理网络上的 Unreal Engine 实例**（称为"端点"），这些端点作为捕获数据的导入目标。它使用消息总线（Message Bus）进行端点发现和通信。

### 核心类

| 类 | 说明 |
|---|---|
| `FCaptureManagerUnrealEndpointModule` | 模块入口，提供 `GetEndpointManager()` 访问端点管理器 |
| `FUnrealEndpointManager` | 端点发现与管理器，负责扫描网络上的 UE 实例 |
| `FUnrealEndpoint` | 单个 UE 端点的抽象，管理连接和数据上传 |
| `FTakeUploadTask` | 上传任务容器，携带进度和完成回调 |
| `FUnrealEndpointInfo` | 端点信息结构体（ID、地址、主机名、端口等） |

### 关键工作流

```
获取模块 → 获取 EndpointManager → 启动发现 → 查找端点 → 建立连接 → 上传 Take 数据 → 监听进度/完成
```

---

## 蓝图用法

本插件的核心类均标记为 `UE_INTERNAL`，**不直接暴露给蓝图**。Capture Manager 的用户交互主要通过编辑器 UI（CaptureManagerEditor 模块）完成，而非蓝图节点。

如需在蓝图中使用捕获数据，建议通过 LiveLink 接口间接访问。

---

## C++ 用法

### 头文件引入

```cpp
#include "CaptureManagerUnrealEndpointModule.h"
#include "CaptureManagerUnrealEndpoint.h"
#include "CaptureManagerUnrealEndpointManager.h"
```

### 基本用法：发现并连接端点

```cpp
// 获取端点管理器
FCaptureManagerUnrealEndpointModule& EndpointModule = 
    FModuleManager::Get().LoadModuleChecked<FCaptureManagerUnrealEndpointModule>("CaptureManagerUnrealEndpoint");

TSharedRef<UE::CaptureManager::FUnrealEndpointManager> EndpointManager = 
    EndpointModule.GetEndpointManager();

// 启动端点发现
EndpointManager->Start();

// 监听端点变化
EndpointManager->EndpointsChanged().AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("Endpoints changed!"));
});

// 等待特定端点出现（阻塞，带超时）
TOptional<TWeakPtr<UE::CaptureManager::FUnrealEndpoint>> Endpoint = 
    EndpointManager->WaitForEndpoint(
        [](const UE::CaptureManager::FUnrealEndpoint& InEndpoint)
        {
            // 自定义匹配条件
            return true;
        },
        5000  // 5 秒超时
    );

if (Endpoint.IsSet())
{
    TSharedPtr<UE::CaptureManager::FUnrealEndpoint> PinnedEndpoint = Endpoint.GetValue().Pin();
    if (PinnedEndpoint.IsValid())
    {
        // 建立连接
        PinnedEndpoint->StartConnection();
        
        // 等待连接建立
        PinnedEndpoint->WaitForConnectionState(
            UE::CaptureManager::FUnrealEndpoint::EConnectionState::Connected,
            5000
        );
    }
}
```

### 进阶用法：上传 Take 数据并监听进度

```cpp
// 构造上传任务
FGuid TaskID = FGuid::NewGuid();
FGuid CaptureSourceID = FGuid::NewGuid();
FString DataDirectory = TEXT("/path/to/captured/data");
FTakeMetadata Metadata;  // 从 LiveLinkFaceMetadata 或 StereoCameraMetadata 解析

TSharedRef<UE::CaptureManager::FTakeUploadTask> UploadTask = 
    MakeShared<UE::CaptureManager::FTakeUploadTask>(
        TaskID,
        CaptureSourceID,
        TEXT("MyCaptureDevice"),
        DataDirectory,
        Metadata
    );

// 监听上传进度
UploadTask->Progressed().BindLambda([](double InProgress)
{
    UE_LOG(LogTemp, Log, TEXT("Upload progress: %.1f%%"), InProgress * 100.0);
});

// 监听上传完成
UploadTask->Complete().BindLambda(
    [](const FString& InMessage, int32 InStatusCode)
    {
        if (InStatusCode == 200)
        {
            UE_LOG(LogTemp, Log, TEXT("Upload complete: %s"), *InMessage);
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("Upload failed (%d): %s"), InStatusCode, *InMessage);
        }
    }
);

// 执行上传（通过端点）
PinnedEndpoint->UploadTake(UploadTask);
```

### 进阶用法：按条件查找多个端点

```cpp
// 查找所有可用端点
TArray<TWeakPtr<UE::CaptureManager::FUnrealEndpoint>> AllEndpoints = 
    EndpointManager->GetEndpoints();

UE_LOG(LogTemp, Log, TEXT("Discovered %d endpoints"), EndpointManager->GetNumEndpoints());

// 按条件过滤
TArray<TWeakPtr<UE::CaptureManager::FUnrealEndpoint>> MatchingEndpoints = 
    EndpointManager->FindEndpointsByPredicate(
        [](const UE::CaptureManager::FUnrealEndpoint& InEndpoint)
        {
            const UE::CaptureManager::FUnrealEndpointInfo& Info = InEndpoint.GetEndpointInfo();
            return Info.HostName.Contains(TEXT("RenderNode"));
        }
    );
```

---

## Demo 示例

### 端点发现与上传的最小完整示例

```cpp
// MyCaptureUploader.h
#pragma once

#include "CoreMinimal.h"
#include "CaptureManagerUnrealEndpointManager.h"
#include "CaptureManagerUnrealEndpoint.h"

class FMyCaptureUploader
{
public:
    void Initialize();
    void Shutdown();
    void UploadTakeToFirstEndpoint(const FString& InDataDirectory, const FTakeMetadata& InMetadata);

private:
    TSharedPtr<UE::CaptureManager::FUnrealEndpointManager> EndpointManager;
    TWeakPtr<UE::CaptureManager::FUnrealEndpoint> ActiveEndpoint;
};
```

```cpp
// MyCaptureUploader.cpp
#include "MyCaptureUploader.h"
#include "CaptureManagerUnrealEndpointModule.h"

void FMyCaptureUploader::Initialize()
{
    FCaptureManagerUnrealEndpointModule& Module = 
        FModuleManager::Get().LoadModuleChecked<FCaptureManagerUnrealEndpointModule>(
            TEXT("CaptureManagerUnrealEndpoint")
        );
    
    EndpointManager = Module.GetEndpointManager();
    EndpointManager->Start();
}

void FMyCaptureUploader::Shutdown()
{
    if (EndpointManager.IsValid())
    {
        EndpointManager->Stop();
    }
}

void FMyCaptureUploader::UploadTakeToFirstEndpoint(
    const FString& InDataDirectory, 
    const FTakeMetadata& InMetadata)
{
    // 等待第一个端点出现
    auto EndpointOpt = EndpointManager->WaitForEndpoint(
        [](const UE::CaptureManager::FUnrealEndpoint&) { return true; },
        10000
    );

    if (!EndpointOpt.IsSet())
    {
        UE_LOG(LogTemp, Warning, TEXT("No endpoint found within timeout"));
        return;
    }

    TSharedPtr<UE::CaptureManager::FUnrealEndpoint> Endpoint = EndpointOpt.GetValue().Pin();
    if (!Endpoint.IsValid())
    {
        UE_LOG(LogTemp, Warning, Endpoint disappeared);
        return;
    }

    // 连接
    Endpoint->StartConnection();
    Endpoint->WaitForConnectionState(
        UE::CaptureManager::FUnrealEndpoint::EConnectionState::Connected, 
        5000
    );

    // 创建并执行上传
    auto Task = MakeShared<UE::CaptureManager::FTakeUploadTask>(
        FGuid::NewGuid(),
        FGuid::NewGuid(),
        TEXT("MyUploader"),
        InDataDirectory,
        InMetadata
    );

    Task->Progressed().BindLambda([](double Progress)
    {
        UE_LOG(LogTemp, Log, TEXT("Progress: %.0f%%"), Progress * 100.0);
    });

    Task->Complete().BindLambda([](const FString& Msg, int32 Code)
    {
        UE_LOG(LogTemp, Log, TEXT("Done (%d): %s"), Code, *Msg);
    });

    Endpoint->UploadTake(Task);
    ActiveEndpoint = Endpoint;
}
```

---

## 模块依赖

从各模块的头文件和命名空间推断的依赖关系：

| 模块 | 用途 |
|---|---|
| `CaptureManagerTakeMetadata` | Take 元数据结构体（FTakeMetadata），被多个模块引用 |
| `Messaging` | 消息总线通信（FMessageAddress, IMessageContext），用于端点发现 |
| `LiveLinkInterface` | LiveLink 接口，用于设备集成 |

> 无特殊依赖（仅标准 Core/Engine/Slate 等 + 上述模块）

---

## 维护状态

### 近期更新

```
- fdaf85b60939 [Capture Manager] Fixed several crashes while aborting take upload.
  → 修复了中止上传时的多个崩溃问题，说明上传流程仍在积极打磨
- 8f3b6b801a63 [Capture Manager] Use weak ptrs on endpoint manager interface.
  → 将端点管理器接口改为使用弱指针，提升内存安全性
- 3cb1199596ff Fixing Python issues:
  → 修复 Python 脚本相关问题，可能涉及自动化管线
```

### 维护评价

- **创建时间**：2025-02-04，非常新的插件（约 6 个月）
- **更新频率**：近期有实质性 bug 修复和接口改进，处于**活跃开发期**
- **已知问题**：上传中止流程存在崩溃风险（已在最新提交中修复）
- **接口稳定性**：接口仍在调整中（如弱指针迁移），API 可能随版本变化
- **推荐度**：✅ 推荐用于虚拟制片管线，但需注意 API 可能不稳定，建议锁定引擎版本使用

⚠️ **注意**：这是一个较新的插件，API 尚未完全稳定。在生产环境中使用时，建议密切关注引擎更新日志中的 Breaking Changes。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp)
- [官方文档]()（暂无）
- [CaptureManagerUnrealEndpoint 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp/Source/CaptureManagerUnrealEndpoint)