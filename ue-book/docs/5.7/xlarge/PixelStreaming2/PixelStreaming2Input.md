# PixelStreaming2Input

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流输入模块 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreaming2Input` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-10-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming2/Source/PixelStreaming2Input) | |

## 用途

`PixelStreaming2Input` 是 Pixel Streaming 2 插件中的输入处理模块，负责接收来自远程浏览器（WebRTC 对等端）的所有输入事件，并将其转换为 Unreal Engine 的本地输入事件。主要职责包括：

- 解析来自数据通道的标准输入消息（鼠标、键盘、触摸、游戏手柄）。
- 支持 XR 输入（HMD、控制器变换、按钮、触控等）。
- 提供一个可扩展的数据协议接口，允许用户自定义消息类型和处理器。
- 通过 `FPixelStreaming2ApplicationWrapper` 覆盖默认的 `GenericApplication`，实现对输入的路由和修饰键状态管理。
- 支持多流输入（多个浏览器连接到同一个 UE 实例时，每个流有独立的 `InputHandler`）。

该模块解决了远程渲染场景下的输入重定向难题，使得浏览器端的交互能够无缝映射到 UE 应用中。

## 使用场景

- 你搭建了一个 Pixel Streaming 服务器，希望用户在浏览器中通过鼠标、键盘、手柄操作 UE 应用。
- 你需要对输入进行自定义处理（例如，拦截特定命令、添加自定义数据通道消息）。
- 你正在开发一个 XR 远程演示应用，需要将头盔和控制器姿态从浏览器传递给 UE。
- 你的 UE 应用包含多个可切换的目标窗口或视口，需要精确地将输入路由到正确的控件。

## 蓝图用法

该模块不提供任何公开的蓝图可调用函数或属性。所有功能仅在 C++ 端可用。输入处理完全通过 C++ 接口完成。

## C++ 用法

### 头文件引入

```cpp
#include "IPixelStreaming2InputModule.h"
#include "IPixelStreaming2InputHandler.h"
#include "IPixelStreaming2DataProtocol.h"
#include "IPixelStreaming2InputMessage.h"
```

### 基本用法

创建一个输入处理器（`InputHandler`）并将其绑定到目标视口。

```cpp
// 获取 PixelStreaming2Input 模块
IPixelStreaming2InputModule& InputModule = IPixelStreaming2InputModule::Get();

// 创建输入处理器（每个流对应一个）
TSharedPtr<IPixelStreaming2InputHandler> InputHandler = InputModule.CreateInputHandler();

// 设置目标视口（例如从现有视口获取）
TSharedPtr<SViewport> Viewport = ...;
InputHandler->SetTargetViewport(Viewport);

// 设置目标窗口（可选，用于窗口级路由）
TSharedPtr<SWindow> Window = ...;
InputHandler->SetTargetWindow(Window);

// 注册一个自定义消息处理器
InputHandler->RegisterMessageHandler(TEXT("my_custom_event"),
    [](FString SourceId, FMemoryReader Message) {
        // 处理自定义数据
    });

// 注册一个自定义命令处理器
InputHandler->SetCommandHandler(TEXT("my_command"),
    [](FString SourceId, FString Descriptor, FString CommandString) {
        // 处理命令
    });
```

### 进阶用法

#### 扩展数据协议

```cpp
// 获取 ToStreamer 协议（从浏览器到 UE）
TSharedPtr<IPixelStreaming2DataProtocol> ToStreamerProtocol = InputHandler->GetToStreamerProtocol();

// 添加一个自定义消息类型，带结构体
TArray<EPixelStreaming2MessageTypes> Structure = { 
    EPixelStreaming2MessageTypes::Uint16, 
    EPixelStreaming2MessageTypes::Float 
};
TSharedPtr<IPixelStreaming2InputMessage> CustomMsg = ToStreamerProtocol->Add(TEXT("my_message"), Structure);

// 注册针对该消息的处理函数
InputHandler->RegisterMessageHandler(TEXT("my_message"),
    [](FString SourceId, FMemoryReader Message) {
        uint16 Value1;
        float Value2;
        Message << Value1;
        Message << Value2;
        UE_LOG(LogTemp, Log, TEXT("Received my_message: Value1=%d, Value2=%f"), Value1, Value2);
    });
```

#### 手动模拟输入

```cpp
// 直接触发键盘事件
InputHandler->OnKeyDown(EKeys::A, false);
InputHandler->OnKeyUp(EKeys::A);

// 模拟鼠标移动（需要先设置目标视口）
InputHandler->OnMouseMove(FIntPoint(100, 200), FIntPoint(0, 0));

// 模拟游戏手柄连接
uint8 ControllerId = InputHandler->OnControllerConnected();
InputHandler->OnControllerButtonPressed(ControllerId, EKeys::Gamepad_FaceButton_Bottom, false);
```

## Demo 示例

一个完整的、可编译的最小示例如下。假设已创建一个空的 UE 插件项目，并添加了对 `PixelStreaming2Input` 的依赖。

### PixelStreaming2InputDemo.h

```cpp
#pragma once

#include "IPixelStreaming2InputModule.h"
#include "IPixelStreaming2InputHandler.h"
#include "Widgets/SWindow.h"
#include "Widgets/SViewport.h"

class FPixelStreaming2InputDemo
{
public:
    void Startup();
    void Shutdown();

private:
    TSharedPtr<IPixelStreaming2InputHandler> InputHandler;
};
```

### PixelStreaming2InputDemo.cpp

```cpp
#include "PixelStreaming2InputDemo.h"
#include "Framework/Application/SlateApplication.h"
#include "Widgets/SViewport.h"

void FPixelStreaming2InputDemo::Startup()
{
    // 获取输入模块
    IPixelStreaming2InputModule& InputModule = IPixelStreaming2InputModule::Get();
    
    // 创建输入处理器
    InputHandler = InputModule.CreateInputHandler();
    
    // 获取当前活跃的视口（假设有一个）
    if (TSharedPtr<SViewport> ActiveViewport = FSlateApplication::Get().GetGameViewport())
    {
        InputHandler->SetTargetViewport(ActiveViewport);
    }
    
    // 也可以设置目标窗口
    if (TSharedPtr<SWindow> ActiveWindow = FSlateApplication::Get().GetActiveTopLevelWindow())
    {
        InputHandler->SetTargetWindow(ActiveWindow);
    }
    
    // 注册一个调试命令
    InputHandler->SetCommandHandler(TEXT("demo.hello"), 
        [this](FString SourceId, FString Descriptor, FString CommandString)
        {
            UE_LOG(LogTemp, Log, TEXT("PixelStreaming2 Demo: Hello from browser!"));
        });
    
    // 注册自定义消息
    TSharedPtr<IPixelStreaming2DataProtocol> ToStreamer = InputHandler->GetToStreamerProtocol();
    TArray<EPixelStreaming2MessageTypes> Structure = { EPixelStreaming2MessageTypes::String };
    ToStreamer->Add(TEXT("demo.echo"), Structure);
    
    InputHandler->RegisterMessageHandler(TEXT("demo.echo"),
        [this](FString SourceId, FMemoryReader Message)
        {
            FString EchoText;
            Message << EchoText;
            UE_LOG(LogTemp, Log, TEXT("Echo from browser: %s"), *EchoText);
        });
}

void FPixelStreaming2InputDemo::Shutdown()
{
    InputHandler.Reset();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PixelStreaming2HMD` | 提供 XR 输入相关的枚举（`EPixelStreaming2XRSystem`, `EControllerHand` 等） |
| `PixelStreaming2Core` | 提供核心日志宏和共享指针支持 |
| `PixelStreaming2RTC` | 数据通道底层通信模块（运行时依赖，非直接头文件引用） |

其他常见依赖（`Core`, `Engine`, `Slate`, `InputCore` 等）已省略。

## 维护状态

### 近期更新

- 2026-01-23 `a9928676` — [NVCodecs, PixelStreaming2] Fixes:
- 2025-11-18 `d7a4d160` — [AVCodecs, PixelStreaming2] Fixes:
- 2025-10-28 `b1db9444` — [PixelStreaming2] Fix: Deadlocks in PixelStreaming2Thread
- 2025-10-17 `5c2f039d` — [PS2] Fix: Non-functional public API
- 2025-10-13 `0de4d465` — [PS2] Bug Fixes for 5.7

### 维护评价

该插件模块创建于 2025 年 10 月，属于较新的功能。近期更新包含性能修复、死锁处理及 API 修复，更新频率较高，开发活跃。目前没有已知的废弃或严重限制，推荐在需要远程输入的应用中使用。但注意 `IsExperimentalVersion` 未标记为实验性（.uplugin 中未设置），但 `EnabledByDefault=false`，用户需手动在项目设置中启用。

## 相关链接

- [源码（Plugin 根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming2)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [输入模块头文件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming2/Source/PixelStreaming2Input/Public)