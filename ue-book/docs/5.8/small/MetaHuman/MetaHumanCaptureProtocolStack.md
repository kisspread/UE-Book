# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 数字人动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（配置资产、编辑器工具） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-04-01 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## ⚠️ 重要废弃警告

**`MetaHumanCaptureProtocolStack` 模块已在 UE 5.7 中被标记为废弃（Deprecated）。** 所有公共 API 均附带 `UE_DEPRECATED(5.7, ...)` 警告。功能已迁移至新模块 `CaptureManagerCore/CaptureProtocolStack`。新项目应使用新模块。

## 用途

`MetaHumanCaptureProtocolStack`（简称 CPS）是 MetaHuman Animator 插件的核心通信模块，实现了 **Capture Protocol Stack** 协议——一套用于 Unreal Engine 与外部面部/身体捕捉设备（如 iPhone 上的 Live Link Face 应用）之间进行实时通信的网络协议栈。

该模块解决的核心问题：
- **设备发现**：通过 UDP 多播在网络上自动发现运行捕捉应用的设备
- **控制会话管理**：通过 TCP 建立与设备的控制连接，管理会话生命周期（开始/停止会话、心跳保活）
- **录制控制**：远程控制设备上的 Take 录制（开始/停止/中止录制，获取 Take 列表和元数据）
- **数据导出**：将设备上录制的 Take 数据（视频、音频、深度数据等）通过专用 TCP 通道导出到引擎

这套协议栈是 MetaHuman Animator 工作流的基础设施——没有它，引擎就无法与捕捉设备通信，也就无法获取面部表演数据来驱动 MetaHuman 角色。

## 使用场景

- 你在用 MetaHuman Animator 做面部动作捕捉 → 通过 CPS 与 iPhone/设备上的 Live Link Face 应用通信
- 你需要自动化管理多个捕捉设备的录制流程 → 用 CPS 的控制协议批量管理设备
- 你在开发自定义的捕捉应用 → 使用 CPS 协议规范实现与 Unreal Engine 的兼容通信
- 你需要将设备上的 Take 数据导入引擎进行处理 → 使用 CPS 的导出协议

## 蓝图用法

该模块不暴露 BlueprintCallable 节点。所有 API 均为 C++ 层面的网络协议实现，不面向蓝图用户。实际的蓝图交互发生在上层模块（如 `MetaHumanPerformance`、`MetaHumanFaceAnimationSolver`）中。

## C++ 用法

### 头文件引入

```cpp
#include "ControlMessenger.h"       // 核心控制信使
#include "DiscoveryMessenger.h"     // 设备发现
#include "ExportClient.h"           // 数据导出
#include "ControlRequest.h"         // 请求消息
#include "ControlResponse.h"        // 响应消息
#include "ControlUpdate.h"          // 更新通知
#include "Constants.h"              // 协议常量
#include "Definitions.h"            // 日志分类
```

### 基本用法：发现设备

```cpp
// 创建发现信使并启动监听
FDiscoveryMessenger DiscoveryMessenger;

DiscoveryMessenger.SetResponseHandler(FDiscoveryMessenger::FOnResponseArrived::CreateLambda(
    [](FDiscoveryResponse InResponse)
    {
        UE_LOG(LogCPSDiscoveryMessenger, Log, TEXT("发现设备，ServerId: %s, ControlPort: %d"),
            *BytesToHex(InResponse.GetServerId().GetData(), InResponse.GetServerId().Num()),
            InResponse.GetControlPort());
    }));

DiscoveryMessenger.SetNotifyHandler(FDiscoveryMessenger::FOnNotifyArrived::CreateLambda(
    [](FDiscoveryNotify InNotify)
    {
        if (InNotify.GetConnectionState() == FDiscoveryNotify::EConnectionState::Online)
        {
            UE_LOG(LogCPSDiscoveryMessenger, Log, TEXT("设备上线"));
        }
    }));

TProtocolResult<void> StartResult = DiscoveryMessenger.Start();
if (StartResult.IsError())
{
    UE_LOG(LogCPSDiscoveryMessenger, Error, TEXT("启动发现失败: %s"), *StartResult.ClaimError().GetMessage());
    return;
}

// 发送多播请求以发现网络上的设备
TProtocolResult<void> Result = DiscoveryMessenger.SendMulticastRequest();
```

### 基本用法：建立控制会话

```cpp
// 创建控制信使
FControlMessenger ControlMessenger;

// 注册断开连接回调
ControlMessenger.RegisterDisconnectHandler(FControlMessenger::FOnDisconnect::CreateLambda(
    [](const FString& InCause)
    {
        UE_LOG(LogCPSControlMessenger, Warning, TEXT("连接断开: %s"), *InCause);
    }));

// 连接到设备（IP 和端口从发现结果获取）
TProtocolResult<void> ConnectResult = ControlMessenger.Start(TEXT("192.168.1.100"), 14560);
if (ConnectResult.IsError())
{
    UE_LOG(LogCPSControlMessenger, Error, TEXT("连接失败: %s"), *ConnectResult.ClaimError().GetMessage());
    return;
}

// 获取服务器信息
TProtocolResult<FGetServerInformationResponse> ServerInfoResult = ControlMessenger.GetServerInformation();
if (ServerInfoResult.IsValid())
{
    const FGetServerInformationResponse& Info = ServerInfoResult.GetResult();
    UE_LOG(LogCPSControlMessenger, Log, TEXT("设备: %s %s, 平台: %s %s"),
        *Info.GetSoftwareName(), *Info.GetSoftwareVersion(),
        *Info.GetPlatformName(), *Info.GetPlatformVersion());
}

// 发送请求获取设备状态
TProtocolResult<FGetStateResponse> StateResult = ControlMessenger.SendRequest(FGetStateRequest());
if (StateResult.IsValid())
{
    UE_LOG(LogCPSControlMessenger, Log, TEXT("设备录制状态: %s"),
        StateResult.GetResult().IsRecording() ? TEXT("录制中") : TEXT("空闲"));
}
```

### 进阶用法：录制控制

```cpp
// 开始录制 Take
TProtocolResult<FStartRecordingTakeResponse> RecordResult = ControlMessenger.SendRequest(
    FStartRecordingTakeRequest(
        TEXT("MySlate"),        // Slate 名称
        1,                      // Take 编号
        TEXT("Subject"),        // 可选：主题
        TEXT("Scenario"),       // 可选：场景
        TArray<FString>({ TEXT("tag1"), TEXT("tag2") })  // 可选：标签
    ));

if (RecordResult.IsValid())
{
    UE_LOG(LogCPSControlMessenger, Log, TEXT("录制已开始"));
}

// ... 录制一段时间后 ...

// 停止录制
TProtocolResult<FStopRecordingTakeResponse> StopResult = ControlMessenger.SendRequest(FStopRecordingTakeRequest());
if (StopResult.IsValid())
{
    UE_LOG(LogCPSControlMessenger, Log, TEXT("录制已停止，Take 名称: %s"), *StopResult.GetResult().GetTakeName());
}

// 获取 Take 列表
TProtocolResult<FGetTakeListResponse> TakeListResult = ControlMessenger.SendRequest(FGetTakeListRequest());
if (TakeListResult.IsValid())
{
    for (const FString& TakeName : TakeListResult.GetResult().GetNames())
    {
        UE_LOG(LogCPSControlMessenger, Log, TEXT("Take: %s"), *TakeName);
    }
}

// 获取 Take 元数据（视频、音频、文件信息）
TArray<FString> TakeNames = { TEXT("MySlate_001") };
TProtocolResult<FGetTakeMetadataResponse> MetadataResult = ControlMessenger.SendRequest(FGetTakeMetadataRequest(TakeNames));
if (MetadataResult.IsValid())
{
    for (const FGetTakeMetadataResponse::FTakeObject& Take : MetadataResult.GetResult().GetTakes())
    {
        UE_LOG(LogCPSControlMessenger, Log, TEXT("Take: %s, 视频: %dx%d@%dfps"),
            *Take.Name, Take.Video.Width, Take.Video.Height, Take.Video.FrameRate);
    }
}
```

### 进阶用法：导出 Take 数据

```cpp
// 创建导出客户端（IP 和导出端口从 GetServerInformation 获取）
FExportClient ExportClient(TEXT("192.168.1.100"), 14561);

// 定义自定义流处理器来接收导出数据
class FMyExportStream : public FBaseStream
{
public:
    virtual bool StartFile(const FString& InTakeName, const FString& InFileName) override
    {
        UE_LOG(LogCPSExportHandler, Log, TEXT("开始接收文件: %s/%s"), *InTakeName, *InFileName);
        return true;
    }

    virtual bool ProcessData(const FString& InTakeName, const FString& InFileName,
                             const TConstArrayView<uint8>& InData) override
    {
        // 处理接收到的数据块
        UE_LOG(LogCPSExportHandler, Verbose, TEXT("接收数据: %d 字节"), InData.Num());
        return true;
    }

    virtual bool FinishFile(const FString& InTakeName, const FString& InFileName,
                            const TStaticArray<uint8, 16>& InHash) override
    {
        UE_LOG(LogCPSExportHandler, Log, TEXT("文件接收完成: %s/%s"), *InTakeName, *InFileName);
        return true;
    }

    virtual void Done(TProtocolResult<void> InResult) override
    {
        if (InResult.IsError())
        {
            UE_LOG(LogCPSExportHandler, Error, TEXT("导出失败: %s"), *InResult.ClaimError().GetMessage());
        }
        else
        {
            UE_LOG(LogCPSExportHandler, Log, TEXT("导出完成"));
        }
    }
};

// 构建导出任务
TArray<FTakeFile> Files;
Files.Add({ TEXT("video.mp4"), 1024 * 1024 * 100, 0 });  // 文件名、长度、偏移

FExportClient::FTaskId TaskId = ExportClient.ExportTakeFiles(
    TEXT("MySlate_001"),
    Files,
    MakeUnique<FMyExportStream>()
);

// 需要时中止导出
// ExportClient.AbortExport(TaskId);
```

## 模块依赖

该模块自身依赖关系紧凑，主要依赖标准引擎模块：

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | 网络通信基于 FSocket、FTcpListener 等标准引擎类 |

> 注：使用该模块的上层模块（如 `MetaHumanIdentity`）会依赖更多模块，但 `MetaHumanCaptureProtocolStack` 本身是自包含的协议实现。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 身体追踪启用时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 渲染伪影 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为已有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

**MetaHuman Animator 整体**处于活跃维护状态，最近更新频繁（2026 年 5 月仍有多次提交），功能持续迭代。

**但 `MetaHumanCaptureProtocolStack` 模块本身已被废弃**：
- 所有公共 API 均标记 `UE_DEPRECATED(5.7, ...)`
- 功能已迁移至 `CaptureManagerCore/CaptureProtocolStack` 新模块
- 该模块仍保留在源码中以保持向后兼容，但不建议新项目使用

**建议**：新项目应直接使用 `CaptureManagerCore/CaptureProtocolStack` 模块。现有项目在升级到 UE 5.7+ 时应规划迁移计划。

## 协议架构概览

CPS 协议栈采用三层架构：

```
┌─────────────────────────────────────────────┐
│              Discovery Layer                │  UDP 多播发现
│         FDiscoveryMessenger                 │
├─────────────────────────────────────────────┤
│              Control Layer                  │  TCP 控制通道
│          FControlMessenger                  │
│  ┌──────────┬──────────┬──────────────┐     │
│  │ Requests │ Responses│   Updates    │     │
│  └──────────┴──────────┴──────────────┘     │
├─────────────────────────────────────────────┤
│              Export Layer                   │  TCP 数据导出
│            FExportClient                    │
│         FExportWorker (线程)                │
└─────────────────────────────────────────────┘
```

| 层 | 传输方式 | 用途 |
|---|---|---|
| Discovery | UDP 多播 | 在局域网内自动发现捕捉设备 |
| Control | TCP | 发送控制指令（录制、查询状态等），接收设备更新 |
| Export | TCP | 将设备上的 Take 数据（视频、音频文件）下载到引擎 |

## 核心类说明

| 类 | 说明 |
|---|---|
| `FDiscoveryMessenger` | 设备发现：通过 UDP 多播发现网络上的捕捉设备 |
| `FControlMessenger` | 控制信使：管理与设备的 TCP 控制会话，发送请求/接收响应 |
| `FExportClient` | 导出客户端：将设备上的 Take 文件数据通过 TCP 导出到本地 |
| `FControlMessage` | 控制消息：封装协议消息的序列化/反序列化 |
| `FTcpServer` / `FTcpClient` | TCP 网络层：底层 TCP 连接管理 |
| `FUdpClient` | UDP 网络层：用于发现层的 UDP 多播通信 |
| `TQueueRunner<T>` | 通用线程安全队列：用于异步消息处理的基础设施 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCaptureProtocolStack)
- [MetaHuman Animator 官方文档](https://docs.unrealengine.com/en-US/metahuman-animator/)
- [后继模块: CaptureManagerCore/CaptureProtocolStack](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/CaptureManagerCore/Source/CaptureProtocolStack)