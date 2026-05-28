# Pixel Streaming 2

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流送 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreaming2` (Runtime), `PixelStreaming2Core` (Runtime), `PixelStreaming2Editor` (Runtime), `PixelStreaming2HMD` (Runtime), `PixelStreaming2Input` (Runtime), `PixelStreaming2RTC` (Runtime), `PixelStreaming2Servers` (Runtime), `PixelStreaming2Settings` (Runtime), `EpicRtc` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-04 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2) | |

---

## 用途

Pixel Streaming 2 是 UE5 新一代像素流送系统，用于将 Unreal Engine 的音视频渲染通过 WebRTC 协议实时传输到浏览器等兼容媒体播放器。用户无需在本地安装客户端，只需通过浏览器即可远程访问和交互 UE5 应用程序。

**本文档聚焦于 `PixelStreaming2Input` 子模块**，该模块负责将浏览器端的输入事件（鼠标、键盘、触摸、手柄、XR 控制器）转换为 Unreal Engine 可识别的原生输入事件，是实现远程交互的核心组件。

与第一代 Pixel Streaming 插件相比，Pixel Streaming 2 采用了全新的模块化架构，将核心逻辑、输入处理、WebRTC 通信、设置管理等拆分为独立模块，并使用 Epic 自研的 `EpicRtc` 替代了原有的 libwebrtc 依赖。

## 使用场景

- 你需要将 UE5 应用通过浏览器远程访问，且需要完整的鼠标/键盘/触摸/手柄输入支持 → 使用 Pixel Streaming 2 的 Input 模块
- 你需要为 Pixel Streaming 自定义数据通道消息协议，添加自定义输入消息类型 → 使用 `IPixelStreaming2DataProtocol` 扩展
- 你需要支持 WebXR 设备（如 Meta Quest）通过浏览器流送 → 使用 XR 输入处理器
- 你需要将输入路由到特定 Widget 而非整个窗口 → 设置 `InputType` 为 `RouteToWidget`

## 蓝图用法

`PixelStreaming2Input` 是一个 Runtime 模块，主要通过 C++ 接口使用，不直接暴露蓝图节点。输入事件的接收和处理发生在引擎内部的 `IInputDevice` 层级。

如需在蓝图中与 Pixel Streaming 交互，应使用 `PixelStreaming2Settings` 或 `PixelStreaming2Core` 模块中提供的蓝图暴露接口。

## C++ 用法

### 头文件引入

```cpp
#include "IPixelStreaming2InputHandler.h"
#include "IPixelStreaming2InputModule.h"
#include "IPixelStreaming2DataProtocol.h"
#include "PixelStreaming2DefaultDataProtocol.h"
#include "PixelStreaming2InputEnums.h"
```

### 基本用法 — 创建 Input Handler

通过模块接口创建输入处理器实例。每个 Streamer 对应一个 Input Handler。

```cpp
#include "IPixelStreaming2InputModule.h"

// 获取模块接口
IPixelStreaming2InputModule& InputModule = IPixelStreaming2InputModule::Get();

// 创建输入处理器
TSharedPtr<IPixelStreaming2InputHandler> InputHandler = InputModule.CreateInputHandler();

// 设置目标窗口（输入事件将路由到此窗口）
InputHandler->SetTargetWindow(MyWindow);

// 设置目标视口（输入事件将路由到此视口）
InputHandler->SetTargetViewport(MyViewport);
```

### 基本用法 — 设置输入路由模式

```cpp
#include "PixelStreaming2InputEnums.h"

// 将输入路由到整个窗口（默认模式）
InputHandler->SetInputType(EPixelStreaming2InputType::RouteToWindow);

// 将输入路由到特定 Widget（适合多实例场景）
InputHandler->SetInputType(EPixelStreaming2InputType::RouteToWidget);
```

### 基本用法 — 注册自定义命令处理器

```cpp
// 注册一个自定义命令处理器，处理来自浏览器的 JSON 命令
// 浏览器发送: { "type": "Command", "MyCustomCommand": "value" }
InputHandler->SetCommandHandler("MyCustomCommand",
    [](FString SourceId, FString Descriptor, FString CommandString)
    {
        UE_LOG(LogTemp, Log, TEXT("收到命令 [%s] 来自用户 [%s]: %s"),
            *Descriptor, *SourceId, *CommandString);
    });

// 覆盖默认命令处理器（如 Stat.FPS）
InputHandler->SetCommandHandler("Stat.FPS",
    [](FString SourceId, FString Descriptor, FString CommandString)
    {
        // 自定义处理逻辑
    });
```

### 基本用法 — 注册自定义消息处理器

```cpp
// 注册自定义消息处理器
InputHandler->RegisterMessageHandler("MyCustomMessage",
    [](FString SourceId, FMemoryReader Message)
    {
        // 解析自定义二进制消息
        int32 CustomValue;
        Message << CustomValue;
        
        UE_LOG(LogTemp, Log, TEXT("收到自定义消息: %d 来自 %s"), CustomValue, *SourceId);
    });
```

### 基本用法 — 权限提升检查

```cpp
// 设置权限检查函数，用于限制特定操作仅允许"提升权限"的用户执行
InputHandler->SetElevatedCheck([](FString SourceId) -> bool
{
    // 根据 SourceId 判断用户是否具有提升权限
    return SourceId == "admin";
});

// 后续可通过以下方式检查
bool bIsElevated = InputHandler->IsElevated("some-user-id");
```

### 进阶用法 — 扩展数据通道协议

```cpp
#include "IPixelStreaming2DataProtocol.h"
#include "PixelStreaming2InputEnums.h"

// 获取默认的 "ToStreamer" 协议
TSharedPtr<IPixelStreaming2DataProtocol> ToStreamerProtocol = InputHandler->GetToStreamerProtocol();

// 添加无消息体的自定义消息类型
TSharedPtr<IPixelStreaming2InputMessage> SimpleMsg = ToStreamerProtocol->Add("MySimpleMessage");

// 添加带结构定义的自定义消息类型
// 定义消息结构：一个 Float + 一个 String
TArray<EPixelStreaming2MessageTypes> Structure = {
    EPixelStreaming2MessageTypes::Float,
    EPixelStreaming2MessageTypes::String
};
TSharedPtr<IPixelStreaming2InputMessage> ComplexMsg = ToStreamerProtocol->Add("MyComplexMessage", Structure);

// 监听协议更新（当协议发生变化时自动触发）
ToStreamerProtocol->OnProtocolUpdated().AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("ToStreamer 协议已更新"));
});

// 查找消息类型
TSharedPtr<IPixelStreaming2InputMessage> FoundMsg = ToStreamerProtocol->Find("MySimpleMessage");
if (FoundMsg.IsValid())
{
    uint8 MsgId = FoundMsg->GetID();
    TArray<EPixelStreaming2MessageTypes> MsgStructure = FoundMsg->GetStructure();
}
```

### 进阶用法 — 获取默认协议

```cpp
#include "PixelStreaming2DefaultDataProtocol.h"

// 获取默认的 ToStreamer 协议（用于浏览器→UE 方向）
TSharedPtr<IPixelStreaming2DataProtocol> DefaultToStreamer = 
    UE::PixelStreaming2Input::GetDefaultToStreamerProtocol();

// 获取默认的 FromStreamer 协议（用于 UE→浏览器方向）
TSharedPtr<IPixelStreaming2DataProtocol> DefaultFromStreamer = 
    UE::PixelStreaming2Input::GetDefaultFromStreamerProtocol();

// 将协议导出为 JSON Schema
TSharedPtr<FJsonObject> SchemaJson = DefaultToStreamer->ToJson();
```

### 进阶用法 — 处理 WebRTC 数据通道消息

```cpp
// 当 WebRTC 数据通道收到消息时，将原始缓冲区传递给 Input Handler
void OnDataChannelMessage(FString SourceId, TArray<uint8> Buffer)
{
    InputHandler->OnMessage(SourceId, Buffer);
}
```

### 进阶用法 — 模拟输入事件

以下方法通常由内部的 WebRTC 消息解析器调用，但也可手动调用来模拟浏览器输入：

```cpp
// 模拟鼠标按下
InputHandler->OnMouseDown(EMouseButtons::Left, FIntPoint(100, 200));

// 模拟鼠标移动
InputHandler->OnMouseMove(FIntPoint(150, 250), FIntPoint(50, 50));

// 模拟鼠标释放
InputHandler->OnMouseUp(EMouseButtons::Left);

// 模拟键盘按下
InputHandler->OnKeyDown(EKeys::W, false);

// 模拟键盘释放
InputHandler->OnKeyUp(EKeys::W);

// 模拟触摸开始
InputHandler->OnTouchStarted(FIntPoint(200, 300), /*TouchIndex=*/0, /*Force=*/0.5f);

// 模拟触摸移动
InputHandler->OnTouchMoved(FIntPoint(250, 350), /*TouchIndex=*/0, /*Force=*/0.7f);

// 模拟触摸结束
InputHandler->OnTouchEnded(FIntPoint(250, 350), /*TouchIndex=*/0);

// 模拟手柄连接
uint8 ControllerId = InputHandler->OnControllerConnected();

// 模拟手柄摇杆输入（范围 -1 到 1）
InputHandler->OnControllerAnalog(ControllerId, EKeys::Gamepad_LeftX, 0.75);

// 模拟手柄按键按下
InputHandler->OnControllerButtonPressed(ControllerId, EKeys::Gamepad_FaceButton_Bottom, false);

// 模拟手柄按键释放
InputHandler->OnControllerButtonReleased(ControllerId, EKeys::Gamepad_FaceButton_Bottom);

// 模拟手柄断开
InputHandler->OnControllerDisconnected(ControllerId);
```

## Demo 示例

### 自定义命令处理器 + 数据协议扩展

```cpp
// MyPixelStreamingInputComponent.h
#pragma once

#include "Components/ActorComponent.h"
#include "IPixelStreaming2InputHandler.h"
#include "MyPixelStreamingInputComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyPixelStreamingInputComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UFUNCTION(BlueprintCallable)
    void RegisterCustomInputHandlers();

private:
    TSharedPtr<IPixelStreaming2InputHandler> InputHandler;

    void OnChatCommand(FString SourceId, FString Descriptor, FString CommandString);
    void OnCustomBinaryMessage(FString SourceId, FMemoryReader Message);
};
```

```cpp
// MyPixelStreamingInputComponent.cpp
#include "MyPixelStreamingInputComponent.h"
#include "IPixelStreaming2InputModule.h"
#include "IPixelStreaming2DataProtocol.h"
#include "PixelStreaming2DefaultDataProtocol.h"
#include "PixelStreaming2InputEnums.h"

void UMyPixelStreamingInputComponent::BeginPlay()
{
    Super::BeginPlay();

    if (IPixelStreaming2InputModule::IsAvailable())
    {
        InputHandler = IPixelStreaming2InputModule::Get().CreateInputHandler();
        if (InputHandler.IsValid())
        {
            RegisterCustomInputHandlers();
        }
    }
}

void UMyPixelStreamingInputComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    InputHandler.Reset();
    Super::EndPlay(EndPlayReason);
}

void UMyPixelStreamingInputComponent::RegisterCustomInputHandlers()
{
    if (!InputHandler.IsValid())
    {
        return;
    }

    // 1. 注册自定义命令处理器
    InputHandler->SetCommandHandler("Chat.Send",
        [this](FString SourceId, FString Descriptor, FString CommandString)
        {
            OnChatCommand(SourceId, Descriptor, CommandString);
        });

    // 2. 注册权限检查
    InputHandler->SetElevatedCheck([](FString SourceId) -> bool
    {
        return SourceId.StartsWith(TEXT("admin_"));
    });

    // 3. 扩展 ToStreamer 协议，添加自定义消息类型
    TSharedPtr<IPixelStreaming2DataProtocol> ToStreamerProtocol = InputHandler->GetToStreamerProtocol();
    if (ToStreamerProtocol.IsValid())
    {
        // 添加一个带 2 个 Float 字段的自定义消息
        TArray<EPixelStreaming2MessageTypes> Structure = {
            EPixelStreaming2MessageTypes::Float,
            EPixelStreaming2MessageTypes::Float
        };
        ToStreamerProtocol->Add("Custom.Analog2D", Structure);

        // 注册对应的二进制消息处理器
        InputHandler->RegisterMessageHandler("Custom.Analog2D",
            [this](FString SourceId, FMemoryReader Message)
            {
                OnCustomBinaryMessage(SourceId, Message);
            });
    }

    // 4. 设置输入路由模式
    InputHandler->SetInputType(EPixelStreaming2InputType::RouteToWindow);
}

void UMyPixelStreamingInputComponent::OnChatCommand(FString SourceId, FString Descriptor, FString CommandString)
{
    UE_LOG(LogTemp, Log, TEXT("[Chat] 来自 [%s]: %s"), *SourceId, *CommandString);
    // 在此处处理聊天消息，例如广播到所有连接的客户端
}

void UMyPixelStreamingInputComponent::OnCustomBinaryMessage(FString SourceId, FMemoryReader Message)
{
    float X, Y;
    Message << X;
    Message << Y;
    UE_LOG(LogTemp, Log, TEXT("自定义摇杆输入 (%f, %f) 来自 %s"), X, Y, *SourceId);
}
```

## 模块依赖

PixelStreaming2Input 模块依赖如下：

| 模块 | 用途 |
|---|---|
| `PixelStreaming2Core` | Pixel Streaming 核心基础设施 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

> **注意**：完整使用 Pixel Streaming 2 功能还需要启用主插件中的其他模块（`PixelStreaming2`, `PixelStreaming2RTC`, `EpicRtc` 等），其中 `PixelStreaming2` 模块依赖 `VulkanRHI`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `c1dab3e1` | [PixelStreaming2] Fix: Input handler obtaining default target window from wrong method | 修复 Input Handler 从错误方法获取默认目标窗口的问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制作资产分类迁移，涉及多个 VP 相关模块的重组 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以支持 FString 和 UE::FSharedString 两种字符串类型 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中作用域枚举导致的乱码输出问题 |

### 维护评价

**活跃维护**。

- **创建时间**：2024-09-04，约 2 年前，属于较新的插件
- **更新频率**：最近 1 个月内有多次提交，包含 Bug 修复和代码重构，说明处于活跃开发阶段
- **维护状态**：由 Epic Games 官方维护，作为 Unreal Engine 核心功能的一部分持续迭代
- **已知注意点**：该插件默认未启用（`EnabledByDefault: false`），需要在项目设置中手动启用
- **推荐使用**：✅ 推荐。这是 Epic 官方的下一代 Pixel Streaming 解决方案，架构更模块化，维护活跃，适合新的 Pixel Streaming 项目。对于已有项目，需评估从第一代 Pixel Streaming 迁移的成本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2/Tests)