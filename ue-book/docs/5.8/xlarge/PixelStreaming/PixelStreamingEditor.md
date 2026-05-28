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
| 创建时间 | 2019-10-31 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming) | |

## 用途

Pixel Streaming 是 Unreal Engine 的远程渲染流送解决方案。它将引擎的音频和画面通过 WebRTC 协议实时编码并推送到浏览器，让用户无需安装游戏客户端、无需高性能本地显卡，仅通过网页即可体验完整的 3D 应用。

该插件的核心价值在于**零客户端分发**——任何拥有现代浏览器的设备（包括手机、平板、低配电脑）都能实时交互高质量的 UE 画面。相比传统的"下载-安装-运行"模式，Pixel Streaming 将渲染计算集中在服务器端，客户端仅负责解码和显示。

本模块（PixelStreamingEditor）负责将**编辑器本身**也纳入流送范围，让远程用户可以实时查看和操控 Unreal Editor，服务于远程协作、虚拟制片、云端编辑等场景。

## 使用场景

- 你需要在没有安装 UE 的设备上远程查看编辑器实时画面 → 用 PixelStreamingEditor 的 Editor 流送模式
- 你正在做虚拟制片（Virtual Production），需要让远程导演实时看到编辑器视口 → 用 LevelEditorViewport 流送模式
- 你在搭建云端 UE 开发环境，让团队通过浏览器协作编辑 → 用内置信号服务器 + Editor 流送
- 你需要在远程浏览器中实时操控编辑器视口的摄像机 → 配置内置信号服务器的 ViewerPort
- 你做建筑可视化，需要让客户通过浏览器直接查看 UE 场景 → 用 Pixel Streaming（非 Editor 模块）

## 蓝图用法

PixelStreamingEditor 模块的 API 完全面向 C++，**不提供蓝图节点**。蓝图层的流送控制由 `PixelStreamingBlueprint` 模块提供（不在本文档范围内）。

编辑器内的流送控制通过 **Editor Toolbar 菜单**操作，无需蓝图：
1. 在编辑器工具栏找到 Pixel Streaming 菜单
2. 选择流送类型（Level Editor Viewport / Editor）
3. 配置信号服务器（内置 / 外部）
4. 选择编解码器（VP8 / VP9 / H264 / AV1）
5. 启动流送

## C++ 用法

### 头文件引入

```cpp
#include "IPixelStreamingEditorModule.h"
```

### 基本用法：启动和停止流送

```cpp
// 确认模块可用
if (IPixelStreamingEditorModule::IsAvailable())
{
    auto& EditorStreaming = IPixelStreamingEditorModule::Get();

    // 启动内置信号服务器
    EditorStreaming.StartSignalling();

    // 流送整个编辑器窗口
    EditorStreaming.StartStreaming(UE::EditorPixelStreaming::EStreamTypes::Editor);

    // 或者只流送关卡编辑器视口
    // EditorStreaming.StartStreaming(UE::EditorPixelStreaming::EStreamTypes::LevelEditorViewport);
}
```

### 配置信号服务器

```cpp
auto& EditorStreaming = IPixelStreamingEditorModule::Get();

// 使用外部信号服务器（不使用内置的）
EditorStreaming.UseExternalSignallingServer(true);

// 或者配置内置信号服务器
EditorStreaming.UseExternalSignallingServer(false);
EditorStreaming.SetSignallingDomain(TEXT("ws://127.0.0.1"));
EditorStreaming.SetStreamerPort(8888);   // 流送端口
EditorStreaming.SetViewerPort(8080);     // 浏览器访问端口（Linux 默认 8080，Windows 默认 80）
```

### 停止流送和信号服务器

```cpp
auto& EditorStreaming = IPixelStreamingEditorModule::Get();

EditorStreaming.StopStreaming();
EditorStreaming.StopSignalling();
```

### 获取信号服务器实例

```cpp
auto& EditorStreaming = IPixelStreamingEditorModule::Get();
TSharedPtr<UE::PixelStreamingServers::IServer> Server = EditorStreaming.GetSignallingServer();

if (Server.IsValid())
{
    // 可以对信号服务器做进一步操作
}
```

### Console Variables

通过控制台变量可以在启动时自动配置流送行为：

```cpp
// 启动编辑器时自动开始流送
// EditorPixelStreaming.StartOnLaunch = true

// 使用远程信号服务器（而非内置）
// EditorPixelStreaming.UseRemoteSignallingServer = true

// 配置流送源
// EditorPixelStreaming.Source = "LevelEditorViewport"
```

### 进阶用法：自定义视频输入源

PixelStreamingEditor 提供了两种视频输入方式，可根据需求选择或扩展：

**组合式后缓冲输入**（`FPixelStreamingVideoInputBackBufferComposited`）：捕获编辑器的组合画面，包含所有重叠的窗口和面板，适合流送完整的编辑器体验。

**视口输入**（`FPixelStreamingVideoInputViewport`）：仅捕获特定视口的内容，适合只需要流送 3D 场景预览的场景，会自动过滤非目标窗口。

## Demo 示例

### EditorStreamingManager.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "IPixelStreamingEditorModule.h"

class FEditorStreamingManager
{
public:
    void Init();
    void Shutdown();
    void ToggleEditorStream();
    void ToggleViewportStream();

private:
    bool bIsStreaming = false;
    UE::EditorPixelStreaming::EStreamTypes CurrentStreamType = UE::EditorPixelStreaming::EStreamTypes::LevelEditorViewport;
};
```

### EditorStreamingManager.cpp

```cpp
#include "EditorStreamingManager.h"

void FEditorStreamingManager::Init()
{
    if (!IPixelStreamingEditorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("PixelStreamingEditor module is not available."));
        return;
    }

    auto& EditorStreaming = IPixelStreamingEditorModule::Get();

    // 配置内置信号服务器
    EditorStreaming.UseExternalSignallingServer(false);
    EditorStreaming.SetSignallingDomain(TEXT("ws://127.0.0.1"));
    EditorStreaming.SetStreamerPort(8888);
    EditorStreaming.SetViewerPort(8080);

    // 启动信号服务器
    EditorStreaming.StartSignalling();

    UE_LOG(LogTemp, Log, TEXT("Editor streaming initialized. Viewer port: %d"), EditorStreaming.GetViewerPort());
}

void FEditorStreamingManager::Shutdown()
{
    if (!IPixelStreamingEditorModule::IsAvailable())
    {
        return;
    }

    auto& EditorStreaming = IPixelStreamingEditorModule::Get();

    if (bIsStreaming)
    {
        EditorStreaming.StopStreaming();
        bIsStreaming = false;
    }

    EditorStreaming.StopSignalling();
}

void FEditorStreamingManager::ToggleEditorStream()
{
    if (!IPixelStreamingEditorModule::IsAvailable())
    {
        return;
    }

    auto& EditorStreaming = IPixelStreamingEditorModule::Get();

    if (bIsStreaming)
    {
        EditorStreaming.StopStreaming();
        bIsStreaming = false;
        UE_LOG(LogTemp, Log, TEXT("Editor streaming stopped."));
    }
    else
    {
        CurrentStreamType = UE::EditorPixelStreaming::EStreamTypes::Editor;
        EditorStreaming.StartStreaming(CurrentStreamType);
        bIsStreaming = true;
        UE_LOG(LogTemp, Log, TEXT("Editor streaming started (full editor window)."));
    }
}

void FEditorStreamingManager::ToggleViewportStream()
{
    if (!IPixelStreamingEditorModule::IsAvailable())
    {
        return;
    }

    auto& EditorStreaming = IPixelStreamingEditorModule::Get();

    if (bIsStreaming)
    {
        EditorStreaming.StopStreaming();
        bIsStreaming = false;
        UE_LOG(LogTemp, Log, TEXT("Editor streaming stopped."));
    }
    else
    {
        CurrentStreamType = UE::EditorPixelStreaming::EStreamTypes::LevelEditorViewport;
        EditorStreaming.StartStreaming(CurrentStreamType);
        bIsStreaming = true;
        UE_LOG(LogTemp, Log, TEXT("Editor streaming started (level editor viewport)."));
    }
}
```

## 模块依赖

`PixelStreamingEditor.Build.cs` 的依赖关系（基于接口头文件分析）：

| 模块 | 用途 |
|---|---|
| `PixelStreaming` | 核心流送模块，提供 `IPixelStreamingStreamer`、`IPixelStreamingAudioInput`、`FPixelStreamingVideoInputRHI` 等基础接口 |
| `PixelStreamingServers` | 内置信号服务器实现，提供 `UE::PixelStreamingServers::IServer` 接口 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `c1dab3e1` | [PixelStreaming2] Fix: Input handler obtaining default target window from wrong method | 修复输入处理器获取默认目标窗口的方法错误 |
| 2026-05-14 | `876d5541` | Fix the crash with PIE/Simulate | 修复在 PIE/模拟模式下的崩溃问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度截断为浮点的编译警告 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制片相关资产分类重组和迁移 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 支持 FString 和 FSharedString 双模式 |

### 维护评价

**活跃维护中**。PixelStreaming 是 Epic 重点投入的旗舰功能之一：

- **高频更新**：最近一个月内有多次提交，涵盖 bug 修复、兼容性改进和架构重构
- **持续演进**：从 commit 中可以看到 PixelStreaming2 的开发痕迹，表明 Epic 正在对该功能进行重大升级
- **基础设施完善**：包含内置信号服务器、多种视频输入源、音频捕获、编辑器 UI 集成等完整功能链
- **已知注意点**：该插件默认未启用（`EnabledByDefault=false`），需要手动在插件管理器中启用；Linux 上 ViewerPort 默认为 8080（因为 80 端口需要 root 权限）

**推荐使用**。PixelStreaming 是 Epic 官方支持的核心功能，长期维护有保障，适合生产环境使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)