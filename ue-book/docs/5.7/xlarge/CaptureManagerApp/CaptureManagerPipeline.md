# Capture Manager Application

> The Capture Manager allows control and monitoring of the capture device, obtains and transcodes the data from the devices and upload the data for import to the UE

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、LiveLink 设备示例） |
| 模块 | `CaptureDataConverter` (Runtime), `CaptureManagerEditor` (Runtime), `CaptureManagerMediaRW` (Runtime), `CaptureManagerPipeline` (Runtime), `CaptureManagerSettings` (Runtime), `CaptureManagerUnrealEndpoint` (Runtime), `ExampleLiveLinkDevices` (Runtime), `IngestLiveLinkDevice` (Runtime), `LiveLinkCapabilities` (Runtime), `LiveLinkFaceMetadata` (Runtime), `StereoCameraMetadata` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp) | |

## 用途

CaptureManagerApp 是 Epic 为虚拟制片（Virtual Production）工作流打造的**端到端数据采集管理工具**。它解决的核心问题是：如何将来自物理采集设备（如 Live Link Face、立体相机阵列等）的原始数据，经过格式转换、转码后，自动上传并导入到 Unreal Engine 中。

整个插件围绕一条**数据处理流水线（Pipeline）** 构建，涵盖以下阶段：

1. **设备发现与连接** — 通过 LiveLink 协议发现并连接采集设备
2. **数据采集监控** — 实时监控设备状态和采集进度
3. **数据转码（Transcode）** — 将原始视频、音频、深度图、标定数据转换为 UE 可用格式
4. **数据上传与导入（Ingest）** — 将转码后的数据上传至 UE 并自动导入

插件包含 11 个模块，按职责可分为：

| 模块组 | 模块 | 职责 |
|---|---|---|
| **核心流水线** | `CaptureManagerPipeline` | 数据处理流水线引擎，管理节点的串行/并行执行 |
| **数据转换** | `CaptureDataConverter` | 底层数据格式转换逻辑 |
| **媒体读写** | `CaptureManagerMediaRW` | 媒体文件的读写抽象层 |
| **编辑器集成** | `CaptureManagerEditor` | 编辑器 UI 和操作面板 |
| **配置管理** | `CaptureManagerSettings` | 插件运行时配置 |
| **端点通信** | `CaptureManagerUnrealEndpoint` | 与 UE 实例的通信端点 |
| **LiveLink 集成** | `LiveLinkCapabilities`, `LiveLinkFaceMetadata`, `IngestLiveLinkDevice`, `ExampleLiveLinkDevices` | LiveLink 设备能力描述、元数据解析、数据摄入 |
| **立体相机** | `StereoCameraMetadata` | 立体相机标定和元数据处理 |

## 使用场景

- 你在做**虚拟制片**，需要从 Live Link Face 等设备采集面部表演数据 → 用 CaptureManagerApp 管理整个采集→转码→导入流程
- 你有一个**立体相机阵列**用于体积视频采集 → 用 CaptureManagerApp 统一管理多路视频、深度、标定数据的处理
- 你需要将采集数据**批量转码**为 UE 可用格式（视频帧序列、音频文件等） → 用 CaptureManagerPipeline 构建自定义处理流水线
- 你需要将采集数据**自动上传**到远程 UE 实例进行导入 → 用 CaptureManagerUnrealEndpoint

---

# CaptureManagerPipeline 模块文档

## 模块概述

`CaptureManagerPipeline` 是整个插件的**数据处理流水线引擎**。它实现了一个基于节点（Node）的处理管线，支持串行和并行执行策略，用于将采集到的原始数据（视频、音频、深度图、标定数据）转换为 UE 可用的格式。

### 核心设计模式

该模块采用经典的**管线（Pipeline）+ 节点（Node）** 架构：

```
┌─────────────────────────────────────────────────┐
│              FCaptureManagerPipeline             │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ Convert  │  │ Convert  │  │ Convert  │      │
│  │ Video    │  │ Audio    │  │ Depth    │ ...  │
│  │ Node     │  │ Node     │  │ Node     │      │
│  └──────────┘  └──────────┘  └──────────┘      │
│       ▲              ▲             ▲             │
│       └──────────────┼─────────────┘             │
│                      │                           │
│         Prepare() → Run() → Validate()          │
└─────────────────────────────────────────────────┘
```

每个节点遵循 **Prepare → Run → Validate** 三阶段生命周期：
- **Prepare()** — 准备阶段：检查输入、创建输出目录等
- **Run()** — 执行阶段：实际的数据转换工作
- **Validate()** — 验证阶段：检查输出是否正确

## 蓝图用法

> ⚠️ 本模块为纯 C++ Runtime 模块，不暴露 BlueprintCallable 接口。所有 API 均通过 C++ 调用。

## C++ 用法

### 头文件引入

```cpp
#include "CaptureManagerPipeline.h"

// 单独引入特定节点
#include "Nodes/ConvertVideoNode.h"
#include "Nodes/ConvertAudioNode.h"
#include "Nodes/ConvertDepthNode.h"
#include "Nodes/ConvertCalibrationNode.h"
```

### 基本用法 — 创建并运行流水线

```cpp
// 来源: CaptureManagerPipeline/Public/CaptureManagerPipeline.h

#include "CaptureManagerPipeline.h"

// 1. 创建流水线（异步模式）
TSharedPtr<FCaptureManagerPipeline> Pipeline = 
    MakeShared<FCaptureManagerPipeline>(EPipelineExecutionPolicy::Asynchronous);

// 2. 添加视频转换节点
TSharedPtr<FConvertVideoNode> VideoNode = 
    MakeShared<FConvertVideoNode>(TakeMetadata.Video, OutputDirectory);
FGuid VideoNodeId = Pipeline->AddConvertVideoNode(VideoNode);

// 3. 添加音频转换节点
TSharedPtr<FConvertAudioNode> AudioNode = 
    MakeShared<FConvertAudioNode>(TakeMetadata.Audio, OutputDirectory);
FGuid AudioNodeId = Pipeline->AddConvertAudioNode(AudioNode);

// 4. 运行流水线（阻塞调用）
FCaptureManagerPipeline::FResult Results = Pipeline->Run();

// 5. 检查结果
for (const auto& [NodeId, Result] : Results)
{
    if (Result.HasError())
    {
        UE_LOG(LogTemp, Error, TEXT("Node failed: %s"), 
               *Result.GetError().GetMessage().ToString());
    }
}
```

### 进阶用法 — 自定义流水线节点

```cpp
// 来源: CaptureManagerPipeline/Public/CaptureManagerPipelineNode.h

// 自定义节点需要继承 FCaptureManagerPipelineNode 并实现三个虚函数
class FMyCustomNode : public FCaptureManagerPipelineNode
{
public:
    FMyCustomNode(const FString& InInputPath, const FString& InOutputPath)
        : FCaptureManagerPipelineNode(TEXT("MyCustomNode"))
        , InputPath(InInputPath)
        , OutputPath(InOutputPath)
    {
    }

protected:
    FString InputPath;
    FString OutputPath;

private:
    // 准备阶段：验证输入、创建目录
    virtual FResult Prepare() override
    {
        if (!FPaths::FileExists(InputPath))
        {
            return FResult(FCaptureManagerPipelineError(
                FText::FromString(TEXT("Input file not found"))));
        }
        
        IFileManager::Get().MakeDirectory(*FPaths::GetPath(OutputPath), true);
        return FResult::Success();
    }

    // 执行阶段：实际处理逻辑
    virtual FResult Run() override
    {
        // 执行数据转换...
        return FResult::Success();
    }

    // 验证阶段：检查输出
    virtual FResult Validate() override
    {
        if (!FPaths::FileExists(OutputPath))
        {
            return FResult(FCaptureManagerPipelineError(
                FText::FromString(TEXT("Output file not generated"))));
        }
        return FResult::Success();
    }
};

// 使用自定义节点
TSharedPtr<FCaptureManagerPipeline> Pipeline = 
    MakeShared<FCaptureManagerPipeline>(EPipelineExecutionPolicy::Synchronous);

TSharedPtr<FMyCustomNode> CustomNode = 
    MakeShared<FMyCustomNode>(InputPath, OutputPath);

// AddGenericNode 用于添加自定义节点
FGuid NodeId = Pipeline->AddGenericNode(CustomNode);

// AddSyncedNode 添加同步节点（保证按添加顺序执行）
FGuid SyncedNodeId = Pipeline->AddSyncedNode(CustomNode);

auto Results = Pipeline->Run();
```

### 错误处理

```cpp
// 来源: CaptureManagerPipeline/Public/CaptureManagerPipelineNode.h

// FCaptureManagerPipelineError 封装了错误信息和错误码
FCaptureManagerPipelineError Error(FText::FromString(TEXT("Something went wrong")), 42);
FText Message = Error.GetMessage();  // 获取错误消息
int32 Code = Error.GetCode();        // 获取错误码

// FResult 使用 TValueOrError<void, FCaptureManagerPipelineError> 模式
FCaptureManagerPipelineNode::FResult Result = SomeNode->Execute();
if (Result.HasValue())
{
    // 成功
}
else if (Result.HasError())
{
    FCaptureManagerPipelineError Err = Result.GetError();
    UE_LOG(LogTemp, Error, TEXT("Error %d: %s"), 
           Err.GetCode(), *Err.GetMessage().ToString());
}
```

### 取消流水线

```cpp
// 在另一个线程中取消正在运行的流水线
Pipeline->Cancel();
```

## Demo 示例

### 完整的 Take 数据处理示例

```cpp
// MyCaptureProcessor.h
#pragma once

#include "CaptureManagerPipeline.h"
#include "CaptureManagerTakeMetadata.h"

class FMyCaptureProcessor
{
public:
    void ProcessTake(const FTakeMetadata& InTakeMetadata, 
                     const FString& InOutputDirectory);

private:
    TSharedPtr<FCaptureManagerPipeline> Pipeline;
};
```

```cpp
// MyCaptureProcessor.cpp
#include "MyCaptureProcessor.h"

void FMyCaptureProcessor::ProcessTake(
    const FTakeMetadata& InTakeMetadata, 
    const FString& InOutputDirectory)
{
    // 创建异步流水线
    Pipeline = MakeShared<FCaptureManagerPipeline>(
        EPipelineExecutionPolicy::Asynchronous);

    // 添加视频转换节点
    if (InTakeMetadata.Video.IsValid())
    {
        auto VideoNode = MakeShared<FConvertVideoNode>(
            InTakeMetadata.Video, InOutputDirectory);
        Pipeline->AddConvertVideoNode(VideoNode);
    }

    // 添加音频转换节点
    if (InTakeMetadata.Audio.IsValid())
    {
        auto AudioNode = MakeShared<FConvertAudioNode>(
            InTakeMetadata.Audio, InOutputDirectory);
        Pipeline->AddConvertAudioNode(AudioNode);
    }

    // 添加深度图转换节点
    if (InTakeMetadata.Depth.IsValid())
    {
        auto DepthNode = MakeShared<FConvertDepthNode>(
            InTakeMetadata.Depth, InOutputDirectory);
        Pipeline->AddConvertDepthNode(DepthNode);
    }

    // 添加标定数据转换节点
    if (InTakeMetadata.Calibration.IsValid())
    {
        auto CalibNode = MakeShared<FConvertCalibrationNode>(
            InTakeMetadata.Calibration, InOutputDirectory);
        Pipeline->AddConvertCalibrationNode(CalibNode);
    }

    // 运行流水线并检查结果
    FCaptureManagerPipeline::FResult Results = Pipeline->Run();

    for (const auto& [NodeId, Result] : Results)
    {
        if (Result.HasError())
        {
            UE_LOG(LogTemp, Error, TEXT("Pipeline node failed: %s"),
                   *Result.GetError().GetMessage().ToString());
        }
    }
}
```

## 模块依赖

从 Build.cs 分析，`CaptureManagerPipeline` 模块的依赖如下：

| 模块 | 用途 |
|---|---|
| `CaptureManagerTakeMetadata` | Take 元数据结构定义（FTakeMetadata、FVideo、FAudio、FCalibration 等） |

无其他特殊依赖（仅标准 Core/CoreUObject 等）。

## 维护状态

### 近期更新

```
- 3ba85c4188cb Monitor class renamed and fixed an issue with TMap
  → TMonitor 类重命名并修复了 TMap 相关问题，说明并行执行机制仍在活跃优化
- f9645b949518 Control flow crash during ingest
  → 修复了数据摄入过程中的控制流崩溃，属于关键稳定性修复
- bc42b6fd1407 Changes to the WMF usage
  → 修改了 WMF（Windows Media Foundation）的使用方式，涉及底层媒体处理
```

### 维护评价

- **创建时间**：2025-02-04，非常新的插件
- **活跃度**：活跃维护中，近期有稳定性修复和功能优化
- **成熟度**：作为 Virtual Production 工具链的一部分，由 Epic 官方维护，质量有保障
- **已知限制**：纯 C++ 模块，无蓝图接口；需要配合其他 CaptureManagerApp 子模块使用
- **推荐度**：✅ 推荐用于虚拟制片数据采集工作流。如果你需要自定义数据处理管线，`CaptureManagerPipeline` 的节点架构设计清晰，易于扩展

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp)
- [CaptureManagerPipeline 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp/Source/CaptureManagerPipeline)