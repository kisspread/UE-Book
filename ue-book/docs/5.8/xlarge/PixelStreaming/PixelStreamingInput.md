# Pixel Streaming

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流输入 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreaming` (Runtime), `PixelStreamingBlueprint` (Runtime), `PixelStreamingBlueprintEditor` (Runtime), `PixelStreamingEditor` (Runtime), `PixelStreamingHMD` (Runtime), `PixelStreamingInput` (Runtime), `PixelStreamingServers` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-31 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming) | |

## 用途

Pixel Streaming 解决的核心问题是**将 Unreal Engine 应用的实时渲染画面和音频流式传输到浏览器**，并在浏览器中接收用户输入（键盘、鼠标、触摸、手柄、XR 控制器等）返回给引擎，实现**云端渲染、客户端交互**的模式。

它主要用于：
- **无需客户端安装**：用户只需一个支持 WebRTC 的浏览器即可使用完整的 UE 应用（如高质量图形演示、交互式体验）。
- **云游戏/云应用**：将计算密集的渲染工作放在服务器，降低用户端硬件要求。
- **远程协作与审查**：多人通过浏览器实时查看和交互同一个 UE 应用场景。
- **部署灵活性**：适合需要跨平台、快速部署的场景。

## 使用场景

- 你需要将一个高保真度的 UE 项目（如建筑可视化、产品配置器）分享给客户，而不想让他们下载庞大的可执行文件。
- 你在开发云游戏服务，希望玩家通过浏览器即可游玩。
- 你需要在远程设备（如平板、手机）上流畅体验 UE 应用，且设备性能有限。
- 你想实现在网页中嵌入实时 3D 内容，并支持完整交互。

## 蓝图用法

Pixel Streaming 的输入模块主要通过 C++ 接口进行控制，蓝图层面主要涉及配置和状态查询。核心的配置节点来自 `UPixelStreamingSettings` 开发者设置类，可在编辑器中配置。

### 核心设置（编辑器）

在 **项目设置** → **PixelStreaming** 分类中可以找到以下配置项：

| 设置项 | 说明 |
|---|---|
| `EnablePixelStreamingToolbar` | 是否在主视口工具栏添加 Pixel Streaming 控制按钮 |
| `DefaultCursorClassName` | 默认光标样式类 |
| `TextEditBeamCursorClassName` | 文本编辑光束光标样式类 |
| `HiddenCursorClassName` | 隐藏光标样式类（用于客户端光标模式） |
| `bMouseAlwaysAttached` | 是否强制假定鼠标已连接（用于无物理鼠标的服务器） |

## C++ 用法

Pixel Streaming 的输入系统高度模块化，核心是 `IPixelStreamingInputHandler` 接口和 `IPixelStreamingInputModule` 模块接口。

### 头文件引入

```cpp
#include "IPixelStreamingInputHandler.h"
#include "IPixelStreamingInputModule.h"
```

### 基本用法：创建输入处理器并处理消息

以下代码演示如何通过模块创建输入处理器，并注册自定义消息处理函数。

```cpp
// 来自 Public/IPixelStreamingInputModule.h
// 1. 获取输入模块单例
IPixelStreamingInputModule& InputModule = IPixelStreamingInputModule::Get();

// 2. 创建一个输入处理器（通常每个流实例对应一个）
TSharedPtr<IPixelStreamingInputHandler> InputHandler = InputModule.CreateInputHandler();

// 3. 注册自定义消息处理函数
// 定义一个函数来处理来自浏览器的特定类型消息
auto MyCustomHandler = [](FString SourceId, FMemoryReader Message) {
    // 解析 Message 中的数据
    // 例如，读取一个浮点数
    float Value;
    Message << Value;
    UE_LOG(LogTemp, Log, TEXT("Received custom value from %s: %f"), *SourceId, Value);
};

// 将处理器与消息类型字符串绑定
InputHandler->RegisterMessageHandler(TEXT("MyCustomMessage"), MyCustomHandler);

// 4. 设置目标窗口（用于路由输入）
// 假设你有一个有效的 TWeakPtr<SWindow> MyWindow
InputHandler->SetTargetWindow(MyWindow);
```

### 进阶用法：处理命令和权限控制

以下代码展示如何注册命令处理器和实现权限检查。

```cpp
// 来自 Public/IPixelStreamingInputHandler.h

// 注册一个命令处理器，用于处理浏览器发送的 JSON 命令
// 命令格式: { "type": "Command", "MyCommand": "value" }
InputHandler->SetCommandHandler(TEXT("MyCommand"), 
    [](FString SourceId, FString Descriptor, FString CommandString) {
        UE_LOG(LogTemp, Log, TEXT("User %s executed command: %s with value: %s"), 
            *SourceId, *Descriptor, *CommandString);
        // 根据 CommandString 执行相应逻辑
    }
);

// 设置权限检查函数，用于判断用户是否有权限执行某些操作（如发送命令）
InputHandler->SetElevatedCheck([](FString SourceId) {
    // 这里可以连接到你的用户验证系统
    // 例如，检查 SourceId 是否在管理员列表中
    return SourceId == TEXT("AdminUser");
});

// 后续可以通过 InputHandler->IsElevated(SourceId) 进行检查
```

### 输入路由控制

```cpp
// 来自 Public/PixelStreamingInputEnums.h
// 设置输入类型：路由到窗口（整个应用）还是路由到特定控件
InputHandler->SetInputType(EPixelStreamingInputType::RouteToWindow); // 或 RouteToWidget
```

## Demo 示例

以下是一个完整的、最小化的示例，展示如何在自定义模块中使用 Pixel Streaming 输入系统。

**MyPixelStreamingHandler.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "IPixelStreamingInputHandler.h"

class FMyPixelStreamingHandler
{
public:
    void Initialize(TWeakPtr<SWindow> TargetWindow);
    void Shutdown();

private:
    TSharedPtr<IPixelStreamingInputHandler> InputHandler;

    void OnMyCustomMessage(FString SourceId, FMemoryReader Message);
    void OnMyCommand(FString SourceId, FString Descriptor, FString CommandString);
};
```

**MyPixelStreamingHandler.cpp**
```cpp
#include "MyPixelStreamingHandler.h"
#include "IPixelStreamingInputModule.h"

void FMyPixelStreamingHandler::Initialize(TWeakPtr<SWindow> TargetWindow)
{
    // 1. 获取输入模块并创建处理器
    IPixelStreamingInputModule& InputModule = IPixelStreamingInputModule::Get();
    InputHandler = InputModule.CreateInputHandler();

    if (!InputHandler.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create Pixel Streaming Input Handler"));
        return;
    }

    // 2. 设置目标窗口
    InputHandler->SetTargetWindow(TargetWindow);

    // 3. 注册消息处理
    InputHandler->RegisterMessageHandler(TEXT("PlayerChat"), 
        [this](FString SourceId, FMemoryReader Msg) { OnMyCustomMessage(SourceId, Msg); });

    // 4. 注册命令处理
    InputHandler->SetCommandHandler(TEXT("RestartLevel"), 
        [this](FString SourceId, FString Desc, FString Cmd) { OnMyCommand(SourceId, Desc, Cmd); });

    UE_LOG(LogTemp, Log, TEXT("Pixel Streaming Input Handler initialized"));
}

void FMyPixelStreamingHandler::Shutdown()
{
    InputHandler.Reset();
}

void FMyPixelStreamingHandler::OnMyCustomMessage(FString SourceId, FMemoryReader Message)
{
    // 假设消息体是长度前缀的字符串
    FString ChatMessage;
    Message << ChatMessage;
    UE_LOG(LogTemp, Log, TEXT("Player %s says: %s"), *SourceId, *ChatMessage);
}

void FMyPixelStreamingHandler::OnMyCommand(FString SourceId, FString Descriptor, FString CommandString)
{
    UE_LOG(LogTemp, Log, TEXT("Command received from %s: %s (value: %s)"), 
        *SourceId, *Descriptor, *CommandString);
    
    if (CommandString == TEXT("1"))
    {
        // 执行重启关卡逻辑
        UGameplayStatics::OpenLevel(GetWorld(), FName(*GetWorld()->GetName()));
    }
}
```

## 模块依赖

从源码分析，Pixel Streaming Input 模块依赖于 Unreal Engine 的核心输入系统和 WebRTC 相关模块。使用该模块时，你的 Build.cs 需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `WebRTC` | WebRTC 协议实现，是像素流传输的基础 |
| `PixelStreamingServers` | 像素流服务器，处理信令和流媒体 |
| `Renderer` | 处理视频编码和渲染相关功能 |
| `ApplicationCore` | 应用程序框架，包括窗口管理 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `c1dab3e1` | [PixelStreaming2] Fix: Input handler obtaining default target window from wrong method | 修复输入处理器从错误方法获取默认目标窗口的问题 |
| 2026-05-14 | `876d5541` | Fix the crash with PIE/Simulate | 修复编辑器内预览/模拟运行时的崩溃问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的警告 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制作：将虚拟制作资产移动到不同类别并迁移 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以同时支持 FString 和 UE::FSharedString |

### 维护评价

**活跃维护**。Pixel Streaming 是 Unreal Engine 的核心功能之一，持续得到 Epic Games 的官方维护和更新。
- **更新频率**：最近几个月有多次实质性更新，包括 bug 修复、性能优化和架构改进。
- **功能成熟度**：从 2019 年发展至今，功能稳定，是生产环境中广泛使用的方案。
- **技术栈**：基于 WebRTC 标准，兼容性良好。
- **推荐使用**：强烈推荐用于需要流式传输和远程交互的项目。注意，该插件默认未启用（`EnabledByDefault: false`），需要在项目设置中手动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)