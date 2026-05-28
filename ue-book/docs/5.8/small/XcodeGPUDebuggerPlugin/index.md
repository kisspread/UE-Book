# Xcode GPU Debugger Plugin

> Xcode GPU debugger integration.

| 属性 | 值 |
|---|---|
| 中文名 | Xcode GPU 调试器 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `XcodeGPUDebuggerPlugin` (DeveloperTool) |
| 实验性 | 否 |
| 创建时间 | 2021-07-12 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/XcodeGPUDebuggerPlugin) | |

## 用途

此插件将 Unreal Engine 与 Apple Xcode 的 GPU 调试器集成，主要解决在 macOS 平台上进行底层渲染调试和性能分析的问题。它类似于 Windows 平台的 RenderDoc 插件，但专为 Apple 生态和 Xcode 设计。启用后，开发者可以一键捕获当前游戏或编辑器视口的 GPU 帧数据，并自动在 Xcode 中打开该捕获文件，从而利用 Xcode 强大的图形调试工具进行单步调试、资源检查和性能分析。

## 使用场景

- 你正在为 Mac 或 iOS（通过 Metal）开发游戏，需要分析特定帧的渲染管线状态和性能瓶颈。
- 你的团队主要使用 Xcode 作为开发和调试环境，希望有一个流畅的集成工作流来调试 GPU 指令。
- 你需要捕获并检查特定 Draw Call 的着色器、纹理、缓冲区等内容。
- 你想通过 `FRenderCaptureProvider` 接口，为你的自定义渲染工具或插件集成 Xcode 的捕获功能。

## 蓝图用法

该插件主要通过编辑器命令和快捷键触发，不提供蓝图可调用的函数节点。

### 核心节点

无蓝图可调用节点。

### 使用示例（蓝图描述）

此插件不直接在蓝图中使用。其核心功能通过以下方式触发：
1.  **编辑器工具栏**：在编辑器顶部工具栏中，找到 “Xcode GPU Debugger” 区域，点击捕获按钮。
2.  **热键**：在游戏或编辑器视口获得焦点时，按下 **Shift + E** 组合键即可触发帧捕获。

捕获完成后，生成的 `.gputrace` 文件会自动在 Xcode 中打开。

## C++ 用法

### 头文件引入

```cpp
#include "IXcodeGPUDebuggerPlugin.h"
```

### 基本用法

通过插件接口触发一次当前视口的帧捕获。

```cpp
// 来源：Engine/Plugins/Developer/XcodeGPUDebuggerPlugin/Source/XcodeGPUDebuggerPlugin/Private/XcodeGPUDebuggerPluginModule.cpp
if (IXcodeGPUDebuggerPlugin::IsAvailable())
{
    IXcodeGPUDebuggerPlugin& Plugin = IXcodeGPUDebuggerPlugin::Get();
    // 通过热键映射的逻辑，最终会调用 CaptureFrame 方法
    // CaptureFrame 内部会查找主视口并调用带默认参数的帧捕获
    // FViewport* Viewport = GEditor->GetActiveViewport();
    // if (Viewport)
    // {
    //     Plugin.CaptureFrame(Viewport, 0, TEXT("")); // Flags=0, 自动生成文件名
    // }
}
```

### 进阶用法

直接调用 `CaptureFrame` 方法，并指定自定义的捕获标志和输出文件路径。这允许进行更精细的捕获控制。

```cpp
// 来源：综合自 XcodeGPUDebuggerPluginModule 的接口实现
void CaptureSpecificViewportWithFlags(FViewport* TargetViewport)
{
    if (IXcodeGPUDebuggerPlugin::IsAvailable() && TargetViewport)
    {
        IXcodeGPUDebuggerPlugin& Plugin = IXcodeGPUDebuggerPlugin::Get();
        uint32 CaptureFlags = 0; // 可自定义标志，例如是否包含深度缓冲等，具体需查阅Metal/Xcode文档
        FString SavePath = FPaths::ProjectSavedDir() / TEXT("GPUTraces/CustomCapture.gputrace");
        Plugin.CaptureFrame(TargetViewport, CaptureFlags, SavePath);
    }
}
```

你也可以在渲染线程中，通过 `FRenderCaptureProvider` 接口嵌入你自己的捕获逻辑。

```cpp
// 来源：XcodeGPUDebuggerPluginModule.h 中的接口实现
// 在你的渲染代码中，可以像这样集成：
void MyRenderFunction(FRHICommandListImmediate& RHICmdList)
{
    // ... 前期渲染代码 ...

    if (ShouldCaptureThisFrame())
    {
        // 通知 Xcode GPU Debugger 插件开始捕获
        if (IXcodeGPUDebuggerPlugin::IsAvailable())
        {
            IXcodeGPUDebuggerPlugin::Get().BeginCapture(&RHICmdList, MyCaptureFlags, MyCapturePath);
        }
    }

    // ... 具体的渲染指令 ...

    if (ShouldCaptureThisFrame())
    {
        // 结束捕获
        if (IXcodeGPUDebuggerPlugin::IsAvailable())
        {
            IXcodeGPUDebuggerPlugin::Get().EndCapture(&RHICmdList);
        }
    }
}
```

## Demo 示例

一个最小化的示例，展示如何在你的模块中调用 Xcode GPU Debugger 进行帧捕获。

**MyFrameCapture.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FMyFrameCapture
{
public:
    static void CaptureCurrentViewport();
};
```

**MyFrameCapture.cpp**
```cpp
#include "MyFrameCapture.h"
#include "IXcodeGPUDebuggerPlugin.h"
#include "Engine/GameEngine.h"
#include "Engine/Engine.h"

void FMyFrameCapture::CaptureCurrentViewport()
{
    // 仅在插件可用且平台为 Mac 时尝试
    if (!IXcodeGPUDebuggerPlugin::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("Xcode GPU Debugger Plugin is not available."));
        return;
    }

    // 获取当前活动视口
    FViewport* Viewport = GEngine && GEngine->GameViewport
        ? GEngine->GameViewport->GetViewport()
        : nullptr;

    // 如果是编辑器环境，可以尝试获取编辑器视口
    if (!Viewport && GEditor)
    {
        Viewport = GEditor->GetActiveViewport();
    }

    if (Viewport)
    {
        UE_LOG(LogTemp, Log, TEXT("Triggering Xcode GPU Frame Capture..."));
        IXcodeGPUDebuggerPlugin::Get().CaptureFrame(Viewport, 0, TEXT(""));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("No active viewport found for frame capture."));
    }
}
```

## 模块依赖

你的模块若想使用此插件的功能，需要在 `Build.cs` 文件中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `XcodeGPUDebuggerPlugin` | 直接依赖本插件模块，以使用 `IXcodeGPUDebuggerPlugin` 接口。 |
| `InputDevice` | 插件实现了 `IInputDeviceModule` 接口以注册快捷键。 |
| `Renderer` | 插件需要与渲染命令列表交互以执行捕获。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 重构了 GPU 同步调用，用新函数替换旧接口，确保命令提交与空闲等待的原子性。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移到新的 `UE_LOGF` 格式。 |
| 2026-03-16 | `a8820581` | [CaptureFrame] Give the RenderDoc, PixWin, and Xcode "CaptureFrame" toolbar entries each their own u... | 为不同图形调试器的捕获按钮分配了独立的工具栏标识，改善了并存时的用户体验。 |
| 2026-02-19 | `3e97632c` | Refactored FSceneViewport / FViewport to remove the ViewportRHI field | 跟随引擎重构，移除了视口中已废弃的 `ViewportRHI` 字段引用。 |
| 2026-01-28 | `5f766aee` | Fixed modules that does not support portable toolchain | 修复了在不支持可移植工具链的构建配置下的编译问题。 |

### 维护评价

该插件由 Apple 官方提供和维护，以确保在 UE 中使用 Metal 和 Xcode 工具链的开发者拥有最佳的调试体验。从提交历史看，插件一直在跟随引擎的主线进行更新和适配（如 API 变更、日志系统升级），**维护状态活跃**。最新的提交（2026年4月）表明它仍在持续改进。对于在 macOS/iOS 平台进行深度渲染开发的团队，这是一个**强烈推荐启用**的工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/XcodeGPUDebuggerPlugin)
- [测试用例]（未在提供信息中发现独立测试文件，功能测试可能集成在引擎整体的渲染测试中。）