# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画器 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | unknown |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一套用于在 Unreal Engine 中创建、编辑和驱动 MetaHuman 数字角色的完整工具链。它解决了从原始视频/音频数据到高质量、可实时驱动的 MetaHuman 面部动画的全流程问题。其核心价值在于提供了一个端到端的解决方案，允许用户：
1.  **从捕获设备（如 iPhone）接收并处理面部表演数据**（通过 `MetaHumanCaptureProtocolStack` 等模块与移动端 App 通信）。
2.  **管理和关联 MetaHuman 角色的身份资产**（如面部网格、DNA），这些资产是驱动动画的基础（通过 `MetaHumanIdentity` 模块）。
3.  **应用和优化面部动画求解**，包括从视频追踪关键点、生成动画、以及从音频驱动面部动画（`Speech2Face`）。
4.  **与 Sequencer 深度集成**，以便在时间轴上编辑和控制 MetaHuman 动画。

它不仅仅是一个单一功能插件，而是一个庞大的生态系统，包含了数据捕获、处理、求解和编辑的所有必要组件。

## 使用场景

-   **数字人虚拟主播/实时交互**：你需要一个能实时响应用户语音和输入的 MetaHuman 角色，使用 `MetaHumanSpeech2Face` 模块将语音实时转换为面部动画。
-   **影视预演/动画制作**：演员在动捕棚中表演，你需要使用 iPhone 应用（如 Live Link Face）捕获其面部表演，然后通过 `MetaHumanCaptureProtocolStack` 和 `MetaHumanCaptureSource` 将数据导入引擎，并应用 `MetaHumanFaceFittingSolver` 生成高质量的面部动画。
-   **批量生产流程**：你有大量的面部表演视频片段需要处理成 MetaHuman 动画资产，可以使用 `MetaHumanBatchProcessor` 来自动化这一流程。
-   **定制化角色开发**：你需要为特定的 MetaHuman 角色（`MetaHumanIdentity`）创建专属的动画控制器或微调面部动画效果。

## 蓝图用法

### 核心节点

该插件的功能主要通过 C++ 类和编辑器工具暴露，直接的蓝图节点较少。以下是一些关键的可蓝图访问的类和功能：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SendRequest` (模板) | 向连接的移动设备（如运行 Live Link Face 的 iPhone）发送协议请求（如获取服务器信息、开始/停止录制）。这是一个模板函数，具体请求类型如 `FGetServerInformationRequest`。 | `FControlMessenger` |
| `ExportTakeFiles` | 发起从移动设备导出特定 Take 的文件（如视频、音频）的任务。 | `FExportClient` |
| `StartSession` / `StopSession` | 建立或断开与移动设备的控制会话。 | `FControlMessenger` |
| `RegisterUpdateHandler` | 注册一个回调来处理来自设备的实时更新消息（如录制状态变化、Take 增删）。 | `FControlMessenger` |

### 使用示例（蓝图描述）

典型的蓝图工作流可能如下：
1.  创建一个 `FControlMessenger` 对象，调用 `Start` 连接到移动设备的 IP 和端口。
2.  调用 `StartSession` 初始化会话。
3.  通过 `SendRequest` 并传入 `FGetServerInformationRequest` 来验证连接并获取设备信息。
4.  调用 `RegisterUpdateHandler` 并绑定到 `GRecordingStatus` 地址路径，以便在演员开始或停止表演时收到通知。
5.  当收到 `FStartRecordingTakeRequest` 的更新或通过 UI 触发时，构造一个 `FStartRecordingTakeRequest`（包含 Slate 名称和 Take 编号）并通过 `SendRequest` 发送。
6.  使用 `FExportClient` 的 `ExportTakeFiles` 方法将录制的文件从设备导出到本地磁盘。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanCaptureProtocolStack/Control/Messages/Constants.h"
#include "MetaHumanCaptureProtocolStack/Control/ControlMessenger.h"
#include "MetaHumanCaptureProtocolStack/ExportClient/ExportClient.h"
```

### 基本用法

以下代码展示了如何使用 `FControlMessenger` 与移动设备建立连接并获取服务器信息。这是整个动画捕获流程的第一步。
*（来源：基于 `ControlMessenger.h` 和 `Constants.h` 的 API 推断）*

```cpp
using namespace UE::CPS;

// 创建 Messenger 实例
FControlMessenger Messenger;

// 注册断开连接的处理器
Messenger.RegisterDisconnectHandler(FControlMessenger::FOnDisconnect::CreateLambda([](const FString& Cause) {
    UE_LOG(LogTemp, Warning, TEXT("Disconnected: %s"), *Cause);
}));

// 启动连接（阻塞直到连接建立或失败）
// IP 和端口通常从移动设备的发现协议或用户输入获得
TProtocolResult<void> StartResult = Messenger.Start(TEXT("192.168.1.100"), 14785);
if (StartResult.IsError()) {
    UE_LOG(LogTemp, Error, TEXT("Failed to start connection: %s"), *StartResult.ClaimError().GetMessage());
    return;
}

// 开始一个控制会话
TProtocolResult<void> SessionResult = Messenger.StartSession();
if (SessionResult.IsError()) {
    UE_LOG(LogTemp, Error, TEXT("Failed to start session: %s"), *SessionResult.ClaimError().GetMessage());
    return;
}

// 发送一个同步请求获取服务器信息
FGetServerInformationRequest InfoRequest;
TProtocolResult<FGetServerInformationResponse> InfoResult = Messenger.SendRequest(InfoRequest);

if (InfoResult.IsValid()) {
    const FGetServerInformationResponse& Info = InfoResult.GetResult();
    UE_LOG(LogTemp, Log, TEXT("Connected to: %s, Model: %s, Platform: %s %s"),
        *Info.GetName(), *Info.GetModel(), *Info.GetPlatformName(), *Info.GetPlatformVersion());
} else {
    UE_LOG(LogTemp, Error, TEXT("GetServerInformation failed: %s"), *InfoResult.ClaimError().GetMessage());
}
```

### 进阶用法

结合 `FControlMessenger` 和 `FExportClient`，实现一个自动录制并导出 Take 的流程。这需要处理异步请求和更新。
*（来源：基于 `ControlMessenger.h`、`ControlRequest.h`、`ExportClient.h` 的 API 推断）*

```cpp
// ... 假设 Messenger 已经连接并开始会话 ...

// 注册更新处理器来监听 Take 列表的变化
Messenger.RegisterUpdateHandler(GTakeAdded, FControlUpdate::FOnUpdateMessage::CreateLambda([](TSharedPtr<FControlUpdate> Update) {
    if (TSharedPtr<FTakeAddedUpdate> TakeUpdate = StaticCastSharedPtr<FTakeAddedUpdate>(Update)) {
        UE_LOG(LogTemp, Log, TEXT("New Take added: %s"), *TakeUpdate->GetTakeName());
    }
}));

// 开始录制一个 Take
FStartRecordingTakeRequest RecordRequest(TEXT("MySlate"), 1, TEXT("Actor"), TEXT("Happy"));
TProtocolResult<FStartRecordingTakeResponse> RecordResult = Messenger.SendRequest(RecordRequest);

if (RecordResult.IsError()) {
    UE_LOG(LogTemp, Error, TEXT("Failed to start recording: %s"), *RecordResult.ClaimError().GetMessage());
    return;
}

// 模拟录制 5 秒
FPlatformProcess::Sleep(5.0f);

// 停止录制
FStopRecordingTakeRequest StopRequest;
TProtocolResult<FStopRecordingTakeResponse> StopResult = Messenger.SendRequest(StopRequest);

if (StopResult.IsValid()) {
    const FString& TakeName = StopResult.GetResult().GetTakeName();
    UE_LOG(LogTemp, Log, TEXT("Recording stopped. Take: %s"), *TakeName);

    // 创建导出客户端并导出刚录制的 Take
    // 假设 ExportPort 来自 GetServerInformationResponse
    uint16 ExportPort = 14786; // 示例端口
    FExportClient ExportClient(TEXT("192.168.1.100"), ExportPort);

    // 构造要导出的文件列表（需要从 GetTakeMetadata 获得具体文件信息）
    TArray<FTakeFile> TakeFiles;
    TakeFiles.Add({TEXT("video.mp4"), 1024000, 0}); // 示例文件
    TakeFiles.Add({TEXT("audio.wav"), 512000, 0});

    // 创建一个简单的流式写入器（实际项目中需实现 FBaseStream 以保存到磁盘）
    // 此处仅为演示调用接口
    // TUniquePtr<FBaseStream> Stream = MakeUnique<FMyDiskSaveStream>(SavePath);
    // ExportClient.ExportTakeFiles(TakeName, MoveTemp(TakeFiles), MoveTemp(Stream));
}
```

## Demo 示例

一个最小的可编译示例，演示如何初始化 `MetaHumanCaptureProtocolStack` 模块并使用其日志类别。
*（来源：`MetaHumanCaptureProtocolStack.h` 和 `Definitions.h`）*

**MyMetaHumanDemoModule.h**
```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FMyMetaHumanDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MyMetaHumanDemoModule.cpp**
```cpp
#include "MyMetaHumanDemoModule.h"
#include "MetaHumanCaptureProtocolStack/MetaHumanCaptureProtocolStack.h"
#include "MetaHumanCaptureProtocolStack/Utility/Definitions.h"

#define LOCTEXT_NAMESPACE "FMyMetaHumanDemoModule"

void FMyMetaHumanDemoModule::StartupModule()
{
    // 确保 MetaHumanCaptureProtocolStack 模块已加载
    FModuleManager::Get().LoadModuleChecked(TEXT("MetaHumanCaptureProtocolStack"));

    // 现在可以安全地使用该模块提供的日志类别
    UE_LOG(LogCPSControlMessenger, Log, TEXT("MetaHuman Capture Protocol Stack is loaded and ready."));

    // 在此处添加您的初始化逻辑，例如创建 FControlMessenger 实例。
}

void FMyMetaHumanDemoModule::ShutdownModule()
{
    // 清理资源
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyMetaHumanDemoModule, MyMetaHumanDemoModule)
```

## 模块依赖

要使用 `MetaHumanCaptureProtocolStack` 模块或整个 `MetaHumanAnimator` 插件的功能，你的项目模块需要依赖以下 **独特** 的模块：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 底层核心算法和技术库，提供面部追踪、求解等基础计算功能。 |
| `MetaHumanSDKEditor` | MetaHuman 的编辑器扩展 SDK，提供资产导入、管理等编辑器功能。 |
| `ControlRigDeveloper` | 用于与 Control Rig 系统集成，驱动 MetaHuman 的骨骼和控制器。 |
| `SkeletalMeshUtilitiesCommon` | 提供骨骼网格体相关的通用工具函数。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 修复当启用身体追踪时关卡序列导出的功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色身上的渲染伪影问题 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 优化身体追踪时的可视化对象过滤 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 实现为已存在的网格体导出动画序列的功能 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存导致的问题 |

### 维护评价

**评价：活跃维护，但存在重大未来变更风险。**

-   **活跃维护**：从 Git 历史看，该插件在最近一周内（2026年5月）有多个功能更新和 Bug 修复，表明 Epic Games 团队仍在积极维护和迭代 MetaHuman Animator。
-   **重大警告**：源码中 **大量** 类和函数（尤其是 `MetaHumanCaptureProtocolStack` 模块中的）都标注了 `UE_DEPRECATED(5.7, "MetaHumanAnimator/MetaHumanCaptureProtocolStack is deprecated. This functionality is now available in the CaptureManagerCore/CaptureProtocolStack module")`。这意味着 **整个捕获协议栈功能将在未来版本（很可能是 UE 5.8 或 5.9）中被迁移到新的 `CaptureManagerCore/CaptureProtocolStack` 模块中，并在 `MetaHumanAnimator` 插件内废弃**。
-   **建议**：虽然当前（UE 5.7/5.8）可以使用该插件，但开发者应密切关注版本更新日志，并为未来迁移到 `CaptureManagerCore` 做好准备。新的项目或功能开发应优先考虑使用未来的新模块路径。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCaptureProtocolStack/Private/Tests) （位于 `Private/Tests` 目录下）
- （官方文档链接未在 .uplugin 中提供）