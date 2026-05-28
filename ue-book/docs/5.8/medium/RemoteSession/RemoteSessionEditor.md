# RemoteSession

> A plugin for Unreal that allows one instance to act as a thin-client (rendering and input) to a second instance

| 属性 | 值 |
|---|---|
| 中文名 | 远程会话 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例应用） |
| 模块 | `RemoteSession` (Runtime), `RemoteSessionEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-03-07 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RemoteSession) | |

## 用途

RemoteSession 插件的核心功能是实现 **远程瘦客户端连接**。它允许一个 Unreal 引擎实例（“主机”）将渲染画面和输入事件实时流式传输到另一个实例（“客户端”），使客户端成为一个只负责显示和输入的轻量级终端。

该插件解决的核心问题是 **跨设备/跨机器的实时协作与远程控制**。通过它，开发者可以在一台设备上运行复杂的逻辑和渲染，而在另一台设备（如平板、手机或另一台电脑）上进行查看和操作，非常适合用于：
- 远程预览与调试
- 多设备协作开发
- 移动设备作为 PC 游戏的第二屏幕或控制器
- 创建类似云游戏的瘦客户端应用

## 使用场景

- 你在 PC 上开发一个移动 VR 应用 → 用 RemoteSession 将 PC 端的运行画面实时推送到移动设备上预览。
- 你需要让设计师在移动设备上实时调整游戏内材质参数 → 用 RemoteSession 连接移动设备和编辑器，实时修改并查看效果。
- 你想在一台高性能机器上运行游戏逻辑，而在另一台低配设备上查看和操作 → 用 RemoteSession 将后者变为前者的瘦客户端。
- 你需要为 Unreal 项目创建一个轻量级的远程控制应用（如 RemoteSessionApp 示例所示）。

## 蓝图用法

RemoteSession 主要通过编辑器面板和 C++ API 提供功能，直接暴露的蓝图节点较少。其核心交互主要在编辑器中完成。

### 核心功能点

| 功能 | 说明 | 所在类/组件 |
|---|---|---|
| 远程会话流面板 | 在编辑器中显示远程客户端传来的画面流 | `SRemoteSessionStream` |
| 流设置 | 配置流显示方向、缩放等 | `URemoteSessionStreamSettings` |
| 用户控件数据资产 | 将自定义 UMG 控件流式传输到远程客户端 | `URemoteSessionStreamWidgetUserData` |

### 使用示例（蓝图描述）

1.  **在编辑器中查看远程流**：
    *   打开编辑器，在“窗口” > “开发者工具” 中找到 “Remote Session” 面板。
    *   启用“启用流式传输”开关，该面板将开始尝试连接并显示远程客户端（或另一个引擎实例）传来的画面。
    *   通过“设置”菜单可以调整分屏方向、是否棋盘格显示以及缩放方式。

2.  **流式传输自定义控件**：
    *   创建一个继承自 `UUserWidget` 的蓝图控件。
    *   创建一个 `URemoteSessionStreamWidgetUserData` 资产，并为其指定你创建的蓝图控件类。
    *   将此资产附加到你想要流式传输的 Actor 或组件上。当远程会话建立时，该控件将被序列化并发送到客户端进行渲染。

## C++ 用法

### 头文件引入

要使用 RemoteSession 的核心功能，通常需要包含：
```cpp
#include "IRemoteSessionRole.h"
#include "IRemoteSessionChannel.h"
```
对于编辑器面板功能：
```cpp
#include "Widgets/SRemoteSessionStream.h"
```

### 基本用法

该插件更侧重于提供基础设施和编辑器集成，其使用通常涉及处理远程会话的连接和通道事件。

**处理远程会话通道变化（源自 `SRemoteSessionStream` 的实现逻辑）**:
```cpp
// 假设你已经有一个 IRemoteSessionRole* 的指针 (如 RemoteSessionHost)
void OnRemoteSessionChannelChange(IRemoteSessionRole* Role, TWeakPtr<IRemoteSessionChannel> Channel, ERemoteSessionChannelChange Change)
{
    if (Change == ERemoteSessionChannelChange::Added)
    {
        // 当一个新通道（如图像通道、输入通道）被添加时触发
        if (Channel.IsValid())
        {
            // 根据通道类型进行不同处理
            // 例如，当图像通道建立时，可以设置 MediaCapture 来捕获画面
            // OnImageChannelCreated(Channel);
            // 当输入通道建立时，可以设置转发输入事件
            // OnInputChannelCreated(Channel);
        }
    }
    else if (Change == ERemoteSessionChannelChange::Removed)
    {
        // 通道被移除时的清理工作
    }
}
```

### 进阶用法

结合 `URemoteSessionMediaOutput` 和 `URemoteSessionMediaCapture` 可以实现更精细的画面流控制。

**将编辑器视图捕获并流式传输（概念代码，源自 `SRemoteSessionStream` 的部分实现）**:
```cpp
// 1. 创建媒体输出和捕获对象
URemoteSessionMediaOutput* MediaOutput = NewObject<URemoteSessionMediaOutput>();
URemoteSessionMediaCapture* MediaCapture = NewObject<URemoteSessionMediaCapture>();

// 2. 设置捕获源为场景视口或渲染目标
MediaCapture->SetCaptureSource(ERemoteSessionMediaCaptureSource::Viewport);

// 3. 将捕获关联到输出
MediaCapture->SetMediaOutput(MediaOutput);
MediaCapture->UpdateRenderTarget(nullptr); // 可选参数，指定特定的渲染目标

// 4. 开始捕获（这通常在远程连接建立后触发）
MediaCapture->CaptureScene();

// 5. 停止捕获
MediaCapture->StopCapture();
```
*注：此代码为逻辑示例，实际使用需处理对象生命周期和线程安全。*

## Demo 示例

RemoteSession 插件本身包含一个示例项目 **RemoteSessionApp**，它演示了如何构建一个独立的瘦客户端应用。其核心代码结构如下，展示了一个简化版的应用初始化：

**RemoteSessionApp.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FRemoteSessionAppModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**RemoteSessionApp.cpp**
```cpp
#include "RemoteSessionApp.h"
#include "RemoteSession.h" // 核心插件模块
#include "RemoteSessionEditor.h" // 编辑器模块（用于连接等功能）

void FRemoteSessionAppModule::StartupModule()
{
    // 作为客户端，需要连接到远程主机
    // 这通常涉及配置主机IP、端口等
    // 具体实现需参考 RemoteSessionApp 项目源码
    // 以及 RemoteSession 模块提供的连接 API
}

void FRemoteSessionAppModule::ShutdownModule()
{
    // 断开连接，清理资源
}
```

## 模块依赖

从 `RemoteSession` 和 `RemoteSessionEditor` 模块的 `Build.cs` 分析，其主要依赖如下：

| 模块 | 用途 |
|---|---|
| `MediaUtils` | 用于处理媒体捕获和输出，是流式传输画面的基础。 |
| `Media` | 提供媒体框架的核心抽象。 |
| `UMG` | 用于流式传输和渲染自定义的 UMG 控件。 |
| `Slate`, `SlateCore` | 用于构建编辑器中的远程会话流预览面板。 |
| `PropertyEditor` | 用于在细节面板中显示和编辑 `URemoteSessionStreamWidgetUserData` 等资产属性。 |
| `WorkspaceMenuStructure` | 用于将远程会话面板注册到编辑器的工作区菜单结构中。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `92167537` | Support other analytics providers for RemoteSession | 为RemoteSession支持更多第三方分析提供商 |
| 2026-05-12 | `1af5af49` | RemoteSession analytics | 为RemoteSession添加内置分析功能 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将传统日志宏迁移至新的UE_LOGF格式 |
| 2026-04-13 | `fb2897b0` | IPv6 support for RemoteSession client and server | 为RemoteSession的客户端和服务器添加IPv6网络协议支持 |
| 2026-04-13 | `015f61a1` | Fixed a bunch of unreachable code warnings causing errors on some targets | 修复大量在部分平台上导致编译错误的“不可达代码”警告 |

### 维护评价

RemoteSession 插件是一个 **实验性** 功能，但维护状态较为活跃。从创建至今已有约7年，属于“老古董”级别，但近期（2026年）仍有明确的功能性更新，如添加IPv6支持和新的分析系统，表明它仍在被开发或维护。

**注意事项**：
1.  该插件默认未启用（`EnabledByDefault: false`），且标记为实验性，意味着 Epic 官方可能认为其接口和功能尚不稳定，不建议用于核心生产环境。
2.  其主要价值在于提供了一种特定的远程协作架构，适合有明确远程瘦客户端需求的项目进行探索和使用。
3.  对于常规的多人游戏或网络功能，请使用标准的 Replication 或专用服务器方案。

**推荐**：如果你的项目需要非标准的远程显示与控制能力，并且能够接受实验性 API 可能发生的变化，可以尝试使用。否则，建议关注其技术实现思路，或将需求转化为其他更成熟的网络方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RemoteSession)
- [官方文档] 无
- [测试用例] 无公开路径