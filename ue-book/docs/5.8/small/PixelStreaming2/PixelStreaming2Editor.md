# Pixel Streaming 2

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流2 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreaming2` (Runtime), `PixelStreaming2Core` (Runtime), `PixelStreaming2Editor` (Runtime), `PixelStreaming2HMD` (Runtime), `PixelStreaming2Input` (Runtime), `PixelStreaming2RTC` (Runtime), `PixelStreaming2Servers` (Runtime), `PixelStreaming2Settings` (Runtime), `EpicRtc` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-04 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2) | |

## 用途

Pixel Streaming 2 插件为虚幻编辑器（Unreal Editor）提供了核心的实时音视频流媒体传输功能。它基于 WebRTC 技术，能够将编辑器内的完整画面、场景视口或指定渲染目标，连同音频一起，实时编码并流式传输到任何兼容 WebRTC 的播放器（主要是网页浏览器）。与旧版像素流插件相比，它提供了更模块化、更易扩展的架构，并内置了编辑器专用的流媒体、输入处理和信号服务器管理功能。

**解决的核心问题：** 让身处不同地理位置的团队成员或用户，无需在本地运行完整的虚幻编辑器或项目，即可通过浏览器实时查看、审阅甚至远程操控正在运行的编辑器内容。这极大地促进了远程协作、设计评审、技术演示和云渲染应用。

## 使用场景

- **远程设计评审：** 艺术家或设计师在编辑器中修改场景，其他团队成员通过浏览器实时观看修改过程，无需共享屏幕。
- **实时技术演示：** 将编辑器中的交互式原型（例如关卡设计、蓝图逻辑演示）流式传输给客户或利益相关者进行体验。
- **云渲染/远程工作站：** 将运行在云端高性能服务器上的虚幻编辑器画面，低延迟地传输到低配置的终端设备（如笔记本、平板）。
- **远程教育与培训：** 讲师在虚幻编辑器中进行操作演示，学员通过浏览器同步观看学习。
- **虚拟制片（Virtual Production）协作：** 导演在控制室通过浏览器监看片场LED墙上由虚幻编辑器驱动的实时画面。

## 蓝图用法

当前模块 (`PixelStreaming2Editor`) 的主要功能通过 `IPixelStreaming2EditorModule` 接口暴露。该接口主要面向 C++ 代码，但蓝图可以通过获取模块实例来间接调用。请注意，这通常需要在编辑器工具（Editor Utility Widget）或编辑器脚本中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get PixelStreaming2Editor Module` | 获取 `PixelStreaming2Editor` 模块的单例实例。 | `IPixelStreaming2EditorModule` |
| `Start Streaming (Editor)` | 启动编辑器特定的像素流发送器。 | `IPixelStreaming2EditorModule` |
| `Stop Streaming` | 停止编辑器特定的像素流发送器。 | `IPixelStreaming2EditorModule` |
| `Start Signalling` | 启动内置的 C++ 信令服务器。 | `IPixelStreaming2EditorModule` |
| `Stop Signalling` | 停止内置的 C++ 信令服务器。 | `IPixelStreaming2EditorModule` |

### 使用示例（蓝图描述）

在一个 **Editor Utility Blueprint** 或 **Editor Utility Widget** 中：
1.  使用 `Get PixelStreaming2Editor Module` 节点获取模块引用。
2.  检查 `Is Available` 返回是否为 `True`。
3.  调用 `Start Streaming (Editor)`，并指定流类型（如 `Level Editor` 或 `Full Editor`）。
4.  （可选）使用 `Start Signalling` 节点启动内置信令服务器，以便浏览器可以直接连接。
5.  在不需要时，调用 `Stop Streaming` 和 `Stop Signalling`。

## C++ 用法

### 头文件引入

```cpp
#include "IPixelStreaming2EditorModule.h"
```

### 基本用法

获取模块单例并启动编辑器流。

```cpp
// 检查模块是否可用
if (IPixelStreaming2EditorModule::IsAvailable())
{
    // 获取模块实例
    IPixelStreaming2EditorModule& EditorStreamingModule = IPixelStreaming2EditorModule::Get();

    // 启动整个编辑器窗口的流式传输
    EditorStreamingModule.StartStreaming(EPixelStreaming2EditorStreamTypes::FullEditor);
    
    // 启动内置信令服务器
    EditorStreamingModule.StartSignalling();
    
    // 打印信令服务器地址供浏览器连接
    UE_LOG(LogTemp, Log, TEXT("Pixel Streaming 2 viewer available at: %s"), *EditorStreamingModule.GetSignallingDomain());
}
```

**停止流式传输**

```cpp
if (IPixelStreaming2EditorModule::IsAvailable())
{
    IPixelStreaming2EditorModule& EditorStreamingModule = IPixelStreaming2EditorModule::Get();
    
    // 停止流式传输
    EditorStreamingModule.StopStreaming();
    
    // 停止信令服务器（即使有连接的客户端也强制停止）
    EditorStreamingModule.StopSignalling(true);
}
```

### 进阶用法

自定义信令服务器配置，例如更改端口和启用 HTTPS。

```cpp
if (IPixelStreaming2EditorModule::IsAvailable())
{
    IPixelStreaming2EditorModule& EditorStreamingModule = IPixelStreaming2EditorModule::Get();
    
    // 设置自定义端口（避免与系统端口冲突）
    EditorStreamingModule.SetStreamerPort(8888);
    EditorStreamingModule.SetViewerPort(8080);
    
    // 设置信令服务器域名
    EditorStreamingModule.SetSignallingDomain(TEXT("ws://my-streaming-server.com"));
    
    // 启用HTTPS（需要提供证书和私钥路径）
    EditorStreamingModule.SetServeHttps(true);
    EditorStreamingModule.SetSSLCertificatePath(TEXT("/path/to/your/cert.pem"));
    EditorStreamingModule.SetSSLPrivateKeyPath(TEXT("/path/to/your/private.key"));
    
    // 启动自定义配置的服务
    EditorStreamingModule.StartSignalling();
    EditorStreamingModule.StartStreaming(EPixelStreaming2EditorStreamTypes::LevelEditor);
}
```

## Demo 示例

以下是一个简单的 C++ 示例，演示如何在编辑器菜单扩展中启动和停止流式传输。

```cpp
// MyStreamingManager.h
#pragma once

#include "CoreMinimal.h"

class FMyStreamingManager
{
public:
    static void StartEditorStream();
    static void StopEditorStream();
};
```

```cpp
// MyStreamingManager.cpp
#include "MyStreamingManager.h"
#include "IPixelStreaming2EditorModule.h"

void FMyStreamingManager::StartEditorStream()
{
    if (IPixelStreaming2EditorModule::IsAvailable())
    {
        IPixelStreaming2EditorModule& PS2Module = IPixelStreaming2EditorModule::Get();
        
        // 启动对关卡编辑器视口的流式传输
        PS2Module.StartStreaming(EPixelStreaming2EditorStreamTypes::LevelEditor);
        PS2Module.StartSignalling();
        
        UE_LOG(LogTemp, Display, TEXT("Pixel Streaming 2 Started. Connect via: %s"), *PS2Module.GetSignallingDomain());
    }
}

void FMyStreamingManager::StopEditorStream()
{
    if (IPixelStreaming2EditorModule::IsAvailable())
    {
        IPixelStreaming2EditorModule& PS2Module = IPixelStreaming2EditorModule::Get();
        
        PS2Module.StopStreaming();
        PS2Module.StopSignalling(true);
        
        UE_LOG(LogTemp, Display, TEXT("Pixel Streaming 2 Stopped."));
    }
}
```

## 模块依赖

要使用 `PixelStreaming2Editor` 模块，你的项目模块需要在 `Build.cs` 中添加对其的依赖。

| 模块 | 用途 |
|---|---|
| `PixelStreaming2Editor` | 编辑器内像素流的核心功能，包含流启动/停止、信令服务器管理、工具栏集成等。 |
| `PixelStreaming2Core` | 像素流的核心运行时功能，被 `PixelStreaming2Editor` 依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `c1dab3e1` | [PixelStreaming2] Fix: Input handler obtaining default target window from wrong method | 修复了输入处理器从错误方法获取默认目标窗口的问题。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量截断为浮点数时产生警告的代码。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制片相关资产的分类调整和迁移。 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构了 FJsonObject 以支持 FString 和 UE::FSharedString。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了在格式化函数中使用的范围枚举可能导致输出乱码的问题。 |

### 维护评价

- **活跃维护**：从提交历史看，插件自2024年9月创建以来持续更新，最近一次更新在2026年5月。
- **更新内容**：近期更新主要集中在 **Bug 修复、性能优化和代码质量改进**（如严格浮点模式警告、输入处理修复），以及**资产组织结构的调整**，而非重大新功能。这表明插件核心功能已趋于稳定。
- **成熟度**：作为 Epic Games 官方维护的插件，其代码质量和稳定性有保障。`EnabledByDefault: false` 表明它被设计为可选功能，需要用户主动启用。
- **推荐度**：**推荐使用**。它是实现虚幻编辑器实时远程查看和协作的官方解决方案，尤其适合需要跨地域协作或进行云端渲染的团队。请确保你的使用场景符合 WebRTC 的网络要求。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)