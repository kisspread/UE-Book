# Pixel Streaming 2

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流二代 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图/材质资产工厂、编辑器工具栏、信令服务器） |
| 模块 | `PixelStreaming2` (Runtime), `PixelStreaming2Core` (Runtime), `PixelStreaming2Editor` (Runtime), `PixelStreaming2HMD` (Runtime), `PixelStreaming2Input` (Runtime), `PixelStreaming2RTC` (Runtime), `PixelStreaming2Servers` (Runtime), `PixelStreaming2Settings` (Runtime), `EpicRtc` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-10-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming2) | |

## 用途

Pixel Streaming 2 是虚幻引擎的第二代像素流技术。它利用 WebRTC 协议将引擎的音频、视频渲染结果实时流式传输到任意兼容 WebRTC 的客户端（如网页浏览器），实现远程实时交互体验。  

该插件完全基于 Epic 自研的 `EpicRtc` 库构建，支持 VP8、VP9、H264、AV1 多种编解码器，内置高性能信令服务器，并提供灵活的**编辑器内流式传输**（`PixelStreaming2Editor` 模块）与**运行时流式传输**两种模式。  
`PixelStreaming2Editor` 模块专门用于在 Unreal Editor 环境中启动/停止流媒体、管理信令服务器、切换视频源（全编辑器合成画面或关卡视口），为开发调试、远程协作和虚拟制作提供即开即用的编辑器工具。

## 使用场景

- **远程开发与调试**：将编辑器画面流式传输到平板或另一台电脑，方便在复杂场景中实时调优。
- **云游戏 / 互动展示**：在 Web 页面中嵌入高保真实时渲染，用户无需安装引擎即可交互。
- **虚拟制作监视器**：将 UE 视口画面发送给导演监视器，支持多路流。
- **多人协作评审**：多地团队成员同时查看同一编辑器或运行时画面。

## 蓝图用法

该插件模块为编辑器专属，其公开 API 均为 C++ 接口，**不直接暴露为蓝图节点**。  
如需从蓝图控制像素流启动/停止，请参考运行时的 `PixelStreaming2` 核心模块（`Create/Start/Stop PixelStreaming2 Streamer` 等节点）。

## C++ 用法

`PixelStreaming2Editor` 模块的核心接口定义在 `IPixelStreaming2EditorModule` 中，可用于从其他编辑器模块或 C++ 脚本控制流媒体。

### 头文件引入

```cpp
#include "IPixelStreaming2EditorModule.h"
```

### 基本用法

```cpp
// 获取模块实例
IPixelStreaming2EditorModule& PS2EditorModule = IPixelStreaming2EditorModule::Get();

// 启动编辑器流（将全编辑器画面或当前关卡视口作为视频源）
PS2EditorModule.StartStreaming(EPixelStreaming2EditorStreamTypes::LevelEditorViewport);

// 停止流
PS2EditorModule.StopStreaming();

// 启动内建信令服务器（默认监听 8888/80 端口）
PS2EditorModule.StartSignalling();

// 停止信令服务器
PS2EditorModule.StopSignalling(true); // bForce = true

// 自定义信令服务器参数
PS2EditorModule.SetSignallingDomain(TEXT("ws://192.168.1.100"));
PS2EditorModule.SetStreamerPort(8888);
PS2EditorModule.SetViewerPort(8080);
```

> **来源文件**: `Engine/Plugins/Media/PixelStreaming2/Source/PixelStreaming2Editor/Public/IPixelStreaming2EditorModule.h`

### 进阶用法

#### 获取当前信令服务器实例以检查状态

```cpp
TSharedPtr<UE::PixelStreaming2Servers::IServer> SignallingServer = PS2EditorModule.GetSignallingServer();
if (SignallingServer)
{
    UE_LOG(LogTemp, Log, TEXT("Signalling server is running: %s"),
           SignallingServer->IsRunning() ? TEXT("True") : TEXT("False"));
}
```

#### 切换流视频源（全编辑器合成 / 关卡视口）

`PixelStreaming2Editor` 支持两种视频源：
- `LevelEditorViewport`：仅捕获主关卡视口
- `EditorComposited`：合成所有编辑器窗口（包含 UI、工具栏等）

```cpp
// 先停止当前流，再以不同源启动
PS2EditorModule.StopStreaming();
PS2EditorModule.StartStreaming(EPixelStreaming2EditorStreamTypes::EditorComposited);
```

## Demo 示例

以下是一个最小示例，展示如何在自定义编辑器模块中启动 PixelStreaming2 编辑器流媒体（需在 Editor 模块中编译）。

### MyEditorTool.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"
#include "Modules/ModuleManager.h"

class FMyEditorToolModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void StartPSEditorStream();
    void StopPSEditorStream();
};
```

### MyEditorTool.cpp

```cpp
#include "MyEditorTool.h"
#include "IPixelStreaming2EditorModule.h"
#include "PixelStreaming2Servers.h"

IMPLEMENT_MODULE(FMyEditorToolModule, MyEditorTool)

void FMyEditorToolModule::StartupModule()
{
    // 注册控制台命令或 UI 按钮等，此处在模块加载时直接启动流演示
    StartPSEditorStream();
}

void FMyEditorToolModule::ShutdownModule()
{
    StopPSEditorStream();
}

void FMyEditorToolModule::StartPSEditorStream()
{
    if (IPixelStreaming2EditorModule::IsAvailable())
    {
        IPixelStreaming2EditorModule& PS2Editor = IPixelStreaming2EditorModule::Get();
        // 启动流并将输出发送到浏览器（自动启动内建信令服务器）
        PS2Editor.StartStreaming(EPixelStreaming2EditorStreamTypes::EditorComposited);
        PS2Editor.StartSignalling();
        UE_LOG(LogTemp, Log, TEXT("Pixel Streaming 2 编辑器流已启动"));
    }
}

void FMyEditorToolModule::StopPSEditorStream()
{
    if (IPixelStreaming2EditorModule::IsAvailable())
    {
        IPixelStreaming2EditorModule& PS2Editor = IPixelStreaming2EditorModule::Get();
        PS2Editor.StopStreaming();
        PS2Editor.StopSignalling();
    }
}
```

## 模块依赖

`PixelStreaming2Editor` 模块的构建依赖项（`PublicDependencyModuleNames`）主要包括以下独特模块：

| 模块 | 用途 |
|---|---|
| `PixelStreaming2` | 核心流媒体运行时 |
| `PixelStreaming2Servers` | 内建信令服务器管理 |
| `PixelStreaming2RTC` | WebRTC 实时通信层 |
| `PixelStreaming2Settings` | 流媒体配置与设置 |
| `PixelStreaming2Core` | 核心类型与工具 |

> **注意**：标准编辑器模块依赖（`Core`, `CoreUObject`, `Engine`, `Slate`, `SlateCore`, `UnrealEd`, `InputCore`, `Projects` 等）已省略。

## 维护状态

### 近期更新

```text
- 2026-01-23 `a9928676` [NVCodecs, PixelStreaming2] Fixes:
- 2025-11-18 `d7a4d160` [AVCodecs, PixelStreaming2] Fixes:
- 2025-10-28 `b1db9444` [PixelStreaming2] Fix: Deadlocks in PixelStreaming2Thread
```

### 维护评价

- **创建时间**：2025-10-13（约 3 个月）
- **最近更新**：2026-01-23（非常频繁）
- **活跃度**：极高，仍在功能性修 bug 和适配新编解码器
- **已知问题**：曾出现过死锁，但已修复
- **推荐使用**：✅ **强烈推荐**。作为 UE5.5+ 官方新一代像素流方案，它取代了旧版 `PixelStreaming`，性能更优、架构更简洁，且处于活跃开发中。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming2)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelStreaming2/Source/PixelStreaming2/Private/Tests)（部分）