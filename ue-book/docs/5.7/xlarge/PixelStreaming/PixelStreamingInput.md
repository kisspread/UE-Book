# Pixel Streaming

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流送 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreaming` (Runtime), `PixelStreamingBlueprint` (Runtime), `PixelStreamingBlueprintEditor` (Runtime), `PixelStreamingEditor` (Runtime), `PixelStreamingHMD` (Runtime), `PixelStreamingInput` (Runtime), `PixelStreamingServers` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-08-29 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming) | |

## 用途

Pixel Streaming 插件将 Unreal Engine 的渲染画面和音频实时编码并通过 WebRTC 协议传输到浏览器等远端客户端。它允许任何支持 WebRTC 的设备（如手机、平板、PC 浏览器）以极低延迟的流式方式体验 UE 内容，无需在客户端安装 UE 或高配显卡。

该插件主要解决两个问题：
1. **跨平台分发**：将高性能的 UE 应用（如建筑可视化、数字孪生、游戏）通过浏览器直接运行，不受终端硬件限制。
2. **远程交互**：支持远端用户通过键盘、鼠标、触摸、游戏手柄甚至 XR 控制器与 UE 场景实时互动。

`PixelStreamingInput` 模块是输入处理的核心，负责接收来自 WebRTC 数据通道的输入事件（按键、鼠标、触摸、控制器等），将其转换为 UE 的输入系统可识别的消息，并路由到正确的窗口/视口。

## 使用场景

- **云游戏**：将 UE 游戏部署在服务器，玩家通过浏览器即可游玩，无需下载。
- **建筑与工业可视化**：设计师或客户通过 iPad 或笔记本远程查看并操控 3D 模型。
- **虚拟制片**：导播或导演在远端浏览器中控制虚幻引擎的虚拟摄像机。
- **远程培训**：学员在浏览器中操作复杂的 UE 模拟环境，无需高性能工作站。

## 蓝图用法

`PixelStreamingInput` 模块主要提供 C++ 接口，蓝图可直接使用的仅有 `UPixelStreamingSettings` 配置类。此外，可通过 `PixelStreamingBlueprint` 模块的蓝图节点（未在本次提供源码中体现）来启动/停止流或注册命令。

### 配置类节点

可在项目设置中直接修改以下属性（蓝图无法动态修改，需重启）:

| 属性 | 类型 | 说明 |
|---|---|---|
| `Default Cursor Class` | `FSoftClassPath` | 浏览器中显示默认鼠标的软引用 |
| `Text Edit Beam Cursor Class` | `FSoftClassPath` | 文本输入时光标的软引用 |
| `Hidden Cursor Class` | `FSoftClassPath` | 隐藏系统鼠标时使用的游标类 |
| `Mouse Always Attached` | `bool` | 强制 UE 认为鼠标始终连接（即使无物理鼠标） |

### 自定义消息处理（需 C++）

蓝图无法直接注册 `IPixelStreamingInputHandler` 的回调，需要通过 C++ 扩展或 Blueprint Function Library 封装。若需要使用蓝图接收自定义命令，可参考 `PixelStreamingBlueprint` 模块的节点。

## C++ 用法

### 头文件引入

```cpp
#include "IPixelStreamingInputModule.h"
#include "IPixelStreamingInputHandler.h"
#include "PixelStreamingInputProtocol.h"
#include "PixelStreamingInputMessage.h"
```

### 基本用法

#### 1. 获取输入处理器

在插件或模块启动时，通过输入模块创建处理器。

```cpp
// PixelStreamingInputTest.cpp (示例)
#include "IPixelStreamingInputModule.h"
#include "IPixelStreamingInputHandler.h"

void SetupInputHandler()
{
    IPixelStreamingInputModule& InputModule = IPixelStreamingInputModule::Get();
    TSharedPtr<IPixelStreamingInputHandler> InputHandler = InputModule.CreateInputHandler();

    // 设置目标窗口和视口（从您的游戏视图获取）
    TSharedPtr<SWindow> TargetWindow = ...;
    TSharedPtr<SViewport> TargetViewport = ...;
    InputHandler->SetTargetWindow(TargetWindow);
    InputHandler->SetTargetViewport(TargetViewport);
}
```

#### 2. 注册自定义命令处理器

当浏览器发送 JSON 命令时，通过 `SetCommandHandler` 进行响应。

```cpp
// 注册一个名为 "CustomAction" 的命令处理器
InputHandler->SetCommandHandler("CustomAction", [](FString SourceId, FString Descriptor, FString CommandString) {
    // Descriptor 包含完整的 JSON 对象字符串
    // CommandString 为命令参数（如果有）
    UE_LOG(LogTemp, Log, TEXT("Received CustomAction from %s: %s"), *SourceId, *CommandString);
});
```

#### 3. 注册自定义消息类型

Pixel Streaming 使用预定义的协议（`ToStreamerProtocol` / `FromStreamerProtocol`）进行消息路由。如需增加新的消息类型，可先向协议添加条目，然后注册处理器。

```cpp
// 在启动阶段添加新的消息类型（建议在模块 Startup 中调用）
FPixelStreamingInputProtocol::ToStreamerProtocol.Add("MyCustomMessage", FPixelStreamingInputMessage({
    EPixelStreamingMessageTypes::String,
    EPixelStreamingMessageTypes::Uint8
}));

// 然后在处理器中注册回调
InputHandler->RegisterMessageHandler("MyCustomMessage", [](FString SourceId, FMemoryReader Message) {
    FString PayloadString;
    uint8 PayloadByte;
    Message << PayloadString;
    Message << PayloadByte;
    UE_LOG(LogTemp, Log, TEXT("MyCustomMessage: %s, %d"), *PayloadString, PayloadByte);
});
```

#### 4. 直接处理原始数据通道消息

`OnMessage` 是核心入口，所有数据通道消息都会经过此接口。

```cpp
// 当收到远端消息时调用（通常由 PixelStreaming 内部触发）
InputHandler->OnMessage(SourceId, Buffer);
```

### 进阶用法

#### 接管窗口与视口

在 Editor 中可能打开多个视口，`IPixelStreamingInputHandler` 允许将输入只路由到特定窗口/视口，避免干扰其他内容。

```cpp
// 在 PIE 或独立应用启动时
void OnBeginPlay()
{
    // 假设已获取 UWorld 的 GameViewportClient
    UGameViewportClient* GameViewport = ...;
    TSharedPtr<SViewport> ViewportWidget = GameViewport->GetGameViewportWidget();
    InputHandler->SetTargetViewport(ViewportWidget);
    InputHandler->SetTargetWindow(FSlateApplication::Get().GetActiveTopLevelWindow());
}
```

#### 模拟触摸事件

当浏览器发送触摸消息时，处理器会设置 `bFakingTouchEvents` 为 true，并自动将鼠标事件转换为触摸事件，这对于移动端浏览器非常有用。

```cpp
bool bIsCurrentlyFaking = InputHandler->IsFakingTouchEvents(); // 返回当前状态
```

#### XR 输入适配

`FPixelStreamingInputHandler` 同时实现了 `FXRMotionControllerBase`，可以处理远端 XR 设备的姿势与按钮输入。

```cpp
// 获取 XR 控制器的位置与旋转
FRotator Orientation;
FVector Position;
bool bSuccess = InputHandler->GetControllerOrientationAndPosition(0, FName("AnySource"), Orientation, Position, 100.0f);
```

#### 消息转换表

`FPixelStreamingInputConverter` 提供了从 WebRTC 按键/编号到 UE `FKey` 的映射表，可自行扩展或查询。

```cpp
// 示例：根据 XR 系统、手、按钮编号查找 FKey
TTuple<EPixelStreamingXRSystem, EControllerHand, uint8, EPixelStreamingInputAction> KeyTuple = ...;
FKey* FoundKey = FPixelStreamingInputConverter::XRInputToFKey.Find(KeyTuple);
if (FoundKey)
{
    // 使用 FoundKey 发送按键事件
}
```

## Demo 示例

以下为一个完整的、可编译的最小示例，展示如何在自定义模块中创建输入处理器并注册命令。

### DemoPSInput.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FDemoPSInputModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    TSharedPtr<IPixelStreamingInputHandler> InputHandler;
    void OnCustomCommand(FString SourceId, FString Descriptor, FString CommandString);
};
```

### DemoPSInput.cpp

```cpp
#include "DemoPSInput.h"
#include "IPixelStreamingInputModule.h"
#include "IPixelStreamingInputHandler.h"

IMPLEMENT_MODULE(FDemoPSInputModule, DemoPSInput)

void FDemoPSInputModule::StartupModule()
{
    // 获取输入模块并创建处理器
    IPixelStreamingInputModule& InputModule = IPixelStreamingInputModule::Get();
    InputHandler = InputModule.CreateInputHandler();

    // 注册一个自定义命令 "SetColor"，浏览器可发送：{ "type": "Command", "SetColor": "Red" }
    InputHandler->SetCommandHandler("SetColor", [this](FString SourceId, FString Descriptor, FString CommandString) {
        OnCustomCommand(SourceId, Descriptor, CommandString);
    });

    // 可选：设置目标窗口（若已知）
    if (GWorld && GWorld->GetGameViewport())
    {
        TSharedPtr<SViewport> Viewport = GWorld->GetGameViewport()->GetGameViewportWidget();
        InputHandler->SetTargetViewport(Viewport);
    }
}

void FDemoPSInputModule::ShutdownModule()
{
    InputHandler.Reset();
}

void FDemoPSInputModule::OnCustomCommand(FString SourceId, FString Descriptor, FString CommandString)
{
    UE_LOG(LogTemp, Log, TEXT("SetColor command received from %s: %s"), *SourceId, *CommandString);
    // 根据 CommandString 执行逻辑，例如设置颜色
}
```

## 模块依赖

以下为使用 `PixelStreamingInput` 模块时，您的模块需要添加的独特依赖（标准依赖省略）。

| 模块 | 用途 |
|---|---|
| `PixelStreamingHMD` | 提供 XR/头显相关枚举和转换（如 `EPixelStreamingXRSystem`, `EPixelStreamingHMDEnums`） |
| `Slate` | 窗口、视口、鼠标光标支持（虽然常见，但因涉及输入路由需显式依赖） |

其他依赖（如 `Core`, `Engine`, `InputCore`, `ApplicationCore`, `WebRTC` 通过 `PixelStreaming` 主模块传递，无需直接添加。

## 维护状态

### 近期更新

- 2025-09-30 `4bfe7f55` 更新基础设施脚本指向新发布分支
- 2025-09-25 `1fdac7d5` [PixelCapture, PS, PS2] 修复 MediaCapture 因使用队列导致的异常状态
- 2025-09-23 `30db91bd` [PS1, PS2] 修复内部信令服务器在创建时因 FTickableGameObject 触发的 ensure
- 2025-09-23 `cc062cea` [PS1, PS2] 修复在编辑器通过命令行设置 streamID 时的崩溃
- 2025-08-29 `32884de4` 将 RHICreateTexture 替换为 RHICmdList.CreateTexture

### 维护评价

Pixel Streaming 插件及其 `PixelStreamingInput` 模块处于**活跃维护**状态。从近期的提交记录看，修复频繁，涉及多个子模块的稳定性改进和 API 调整。该插件跟随 UE 主版本迭代持续更新，且官方提供了完善文档与示例。其架构设计较为成熟，但仍存在一些已知的边缘崩溃问题（已解决）。对于希望实现实时云渲染或远程交互的项目，强烈推荐使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming/Source/PixelStreamingInput/Private) （模块内 Private 目录包含单元测试与调试代码）