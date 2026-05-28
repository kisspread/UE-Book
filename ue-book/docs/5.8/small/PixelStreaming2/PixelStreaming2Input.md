# Pixel Streaming 2

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流媒体2 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreaming2` (Runtime), `PixelStreaming2Core` (Runtime), `PixelStreaming2Editor` (Runtime), `PixelStreaming2HMD` (Runtime), `PixelStreaming2Input` (Runtime), `PixelStreaming2RTC` (Runtime), `PixelStreaming2Servers` (Runtime), `PixelStreaming2Settings` (Runtime), `EpicRtc` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2) | |

## 用途

Pixel Streaming 2 插件旨在通过 WebRTC 协议将 Unreal Engine 的实时音频和渲染画面流式传输到兼容的 Web 浏览器等媒体播放器。它本质上是 UE 云渲染解决方案的核心，允许用户通过浏览器远程体验 UE 应用或游戏。

本文档聚焦于其输入子模块 **PixelStreaming2Input**。该模块专门负责处理从 Web 客户端（浏览器）发送过来的各类输入事件（如键盘、鼠标、触摸、游戏手柄、XR 控制器），并将其转换、路由到 Unreal Engine 的原生输入系统中，从而实现浏览器对 UE 应用程序的远程控制。

## 使用场景

- **云游戏/云应用**：玩家通过手机、平板或低端电脑的浏览器，远程游玩在高性能服务器上运行的 UE 游戏，输入指令通过该模块传回游戏。
- **远程演示与协作**：设计师或演示者在一台机器上运行 UE 应用，多人通过浏览器同时查看并交互。
- **跨平台输入整合**：将来自 Web 端的复杂输入（如多点触控、自定义手柄映射）统一处理并注入 UE 的输入管线。

## 蓝图用法

Pixel Streaming 2 的输入模块主要通过 C++ 进行深度集成和定制。蓝图层面，其核心接口 `IPixelStreaming2InputHandler` 提供的主要是运行时状态查询和配置功能，而非直接的事件蓝图节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetInputType` | 设置输入路由模式：路由到窗口（`RouteToWindow`）或路由到特定控件（`RouteToWidget`）。 | `IPixelStreaming2InputHandler` |
| `IsFakingTouchEvents` | 查询输入处理器当前是否在模拟触摸事件（例如用鼠标模拟触摸）。 | `IPixelStreaming2InputHandler` |

**注意**：输入事件的处理（`OnMouseDown`, `OnKeyDown` 等）和自定义消息处理器的注册（`RegisterMessageHandler`, `SetCommandHandler`）均为 C++ 虚函数接口，无法在蓝图中直接覆盖或调用。蓝图主要用于查询状态或在 C++ 层面进行初始配置。

## C++ 用法

### 头文件引入

```cpp
#include "PixelStreaming2Input/Public/IPixelStreaming2InputHandler.h"
#include "PixelStreaming2Input/Public/IPixelStreaming2InputModule.h"
#include "PixelStreaming2Input/Public/PixelStreaming2InputEnums.h"
```

### 基本用法

Pixel Streaming 2 的输入系统通常由其流媒体模块自动创建和管理。开发者更常见的需求是**扩展或监听**输入行为，而不是从头创建。

**示例：监听并处理来自浏览器的自定义“命令”消息**
```cpp
// 假设你已经获取了一个 IPixelStreaming2InputHandler 实例的引用，例如通过流媒体子系统
TSharedPtr<IPixelStreaming2InputHandler> InputHandler = ...;

// 1. 注册一个自定义命令处理器，用于处理来自浏览器的特定JSON命令
// 例如，浏览器发送：{ "type": "Command", "MyCustomSetting": 75 }
InputHandler->SetCommandHandler(TEXT("MyCustomSetting"), 
    [](FString SourceId, FString Descriptor, FString CommandString)
    {
        // SourceId: 发送命令的浏览器用户标识
        // Descriptor: 完整的JSON命令字符串，例如上面的例子
        // CommandString: 提取出来的命令值，例如 "75"
        UE_LOG(LogTemp, Log, TEXT("收到用户 %s 的自定义设置: %s"), *SourceId, *CommandString);
        
        // 在这里处理你的游戏逻辑...
    });

// 2. 你也可以注册一个通用的消息处理器来处理原始二进制消息
InputHandler->RegisterMessageHandler(TEXT("MyCustomMessage"),
    [](FString SourceId, FMemoryReader Message)
    {
        // 从 Message FMemoryReader 中按协议读取数据
        float Value;
        Message << Value;
        UE_LOG(LogTemp, Log, TEXT("收到自定义消息，值: %f"), Value);
    });
```

### 进阶用法：扩展输入协议

你可以向 Pixel Streaming 的默认数据协议中添加自定义的消息类型，用于收发自定义数据。

```cpp
// 获取当前的“发送到流媒体端”协议
TSharedPtr<IPixelStreaming2DataProtocol> ToStreamerProtocol = InputHandler->GetToStreamerProtocol();

// 添加一个自定义的、带结构定义的消息
// 定义：消息ID为200，包含两个float数据
TArray<EPixelStreaming2MessageTypes> Structure = { EPixelStreaming2MessageTypes::Float, EPixelStreaming2MessageTypes::Float };
TSharedPtr<IPixelStreaming2InputMessage> MyMessage = ToStreamerProtocol->Add(TEXT("MyCustomData"), Structure);

if (MyMessage)
{
    UE_LOG(LogTemp, Log, TEXT("自定义消息已注册，ID: %d"), MyMessage->GetID());
}

// 监听协议更新事件，当协议变化时（例如其他模块也添加了消息），你可以同步更新客户端
ToStreamerProtocol->OnProtocolUpdated().AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("数据协议已更新，需要通知前端重新获取协议。"));
    // 通常由流媒体模块自动处理重新同步
});
```

## Demo 示例

一个最小化的示例，展示如何获取输入处理器并注册一个简单的命令处理器。

```cpp
// MyInputHandlerExtension.h
#pragma once

#include "CoreMinimal.h"

class FMyInputHandlerExtension
{
public:
    FMyInputHandlerExtension();
    ~FMyInputHandlerExtension();

private:
    void OnHelloCommand(FString SourceId, FString Descriptor, FString CommandString);
};
```

```cpp
// MyInputHandlerExtension.cpp
#include "MyInputHandlerExtension.h"
#include "PixelStreaming2Input/Public/IPixelStreaming2InputHandler.h"
#include "PixelStreaming2Input/Public/IPixelStreaming2InputModule.h"

FMyInputHandlerExtension::FMyInputHandlerExtension()
{
    // 检查模块是否可用
    if (IPixelStreaming2InputModule::IsAvailable())
    {
        // 通过模块接口创建一个新的输入处理器实例（通常由流媒体模块内部完成，此为演示）
        TSharedPtr<IPixelStreaming2InputHandler> Handler = IPixelStreaming2InputModule::Get().CreateInputHandler();
        if (Handler.IsValid())
        {
            // 注册一个名为“Hello”的命令处理器
            Handler->SetCommandHandler(TEXT("Hello"), 
                FMyInputHandlerExtension::OnHelloCommand);
        }
    }
}

FMyInputHandlerExtension::~FMyInputHandlerExtension()
{
    // 清理工作...
}

void FMyInputHandlerExtension::OnHelloCommand(FString SourceId, FString Descriptor, FString CommandString)
{
    UE_LOG(LogTemp, Warning, TEXT("Hello命令来自 %s！消息内容: %s"), *SourceId, *Descriptor);
}
```

## 模块依赖

从 `PixelStreaming2Input.Build.cs` 分析，使用者主要需要依赖标准模块。其**独特依赖**如下：

| 模块 | 用途 |
|---|---|
| `VulkanRHI` | 提供 Vulkan 图形 API 支持，用于图形渲染和可能的纹理流送。 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `c1dab3e1` | [PixelStreaming2] Fix: Input handler obtaining default target window from wrong method | 修复了输入处理器从错误的方法获取默认目标窗口的问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量被截断为浮点数产生警告的代码 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制作：将不同的VP资产移动到其他资产分类，并迁移它们（标题不完整） |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构了FJsonObject以同时支持FString和UE::FSharedString |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了在格式化函数中使用的域作用域枚举可能导致输出乱码的问题 |

### 维护评价

- **活跃维护**：插件创建于 2024 年 9 月，非常新。近期（2026 年 5 月）仍有针对功能性和代码质量的实质性提交，表明处于**活跃维护**状态。
- **实验性**：虽然 `.uplugin` 中未标记为实验性，但默认是**禁用**的（`EnabledByDefault: false`），这表明它可能是一个较新或需要用户主动启用的功能。
- **推荐使用**：对于需要实现 UE 应用云化、远程访问和跨平台输入整合的新项目，**推荐使用**此插件及其输入模块。由于其较新，建议密切关注官方更新和社区反馈。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2/Tests)