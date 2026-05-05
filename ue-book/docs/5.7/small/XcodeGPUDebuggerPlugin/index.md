# Xcode GPU Debugger Plugin

> Xcode GPU debugger integration.

| 属性 | 值 |
|---|---|
| 分类 | Rendering |
| 默认启用 | ❌ 需手动启用 |
| 包含内容 | 否 |
| 模块 | XcodeGPUDebuggerPlugin (DeveloperTool, PostConfigInit) |
| 限定平台 | Mac |
| 创建时间 | 2021-07-12 |
| 年龄标签 | 🆕 (~4.8年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/XcodeGPUDebuggerPlugin) | |

## 用途

这个 Plugin 是 Apple 为 UE5 开发的 **Metal GPU 帧捕获工具**。它在 UE5 编辑器中集成了一键式 GPU 帧捕获功能，能够将当前帧的 Metal 渲染指令录制为 `.gputrace` 文件，并自动在 Xcode 中打开，供开发者使用 Xcode 的 GPU Debugger 进行逐 Draw Call 分析。

核心工作原理：
1. 启用 Metal Capture Layer（设置 `METAL_CAPTURE_ENABLED=1`）
2. 通过 Metal API 的 `MTL::CaptureManager` 开始/停止帧捕获
3. 将捕获数据写入 `Saved/XcodeGPUTraceCaptures/` 目录
4. 调用 NSWorkspace 自动用 Xcode 打开 `.gputrace` 文件

## 使用场景

- 你在 macOS 上开发 UE5 项目，需要分析 Metal 渲染管线的性能瓶颈
- 你需要逐帧查看 GPU 指令执行顺序、资源绑定状态、Shader 参数
- 你要调试某个特定 Draw Call 的渲染结果不符合预期的问题
- 你在优化 Metal 渲染后端，需要对比优化前后的 GPU trace

⚠️ **仅限 macOS 平台**。在 iOS/tvOS 上会将目标设为 DeveloperTools（需要 Xcode 已连接设备），在其他平台完全不可用。

## 蓝图用法

此 Plugin 不暴露任何 BlueprintCallable 函数，无蓝图节点可用。

## C++ 用法

### 通过控制台命令

Plugin 注册了控制台命令 `Xcode.CaptureFrame`，可在任意控制台窗口中使用：

```
Xcode.CaptureFrame
```

执行后会捕获下一帧的渲染指令并在 Xcode 中打开。

### 快捷键

Plugin 自动注入了 `Shift+E` 快捷键（通过 `PlayerInput.DebugExecBindings`），在编辑器和游戏中均可直接按 `Shift+E` 触发帧捕获。

### 通过 IRenderCaptureProvider API

Plugin 实现了 `IRenderCaptureProvider` 接口，其他模块可通过 Modular Features 系统调用：

```cpp
#include "IRenderCaptureProvider.h"

// 获取已注册的 capture provider
TArray<IRenderCaptureProvider*> Providers;
IModularFeatures::Get().GetModularFeatureImplementations<IRenderCaptureProvider>(
    IRenderCaptureProvider::GetModularFeatureName(), Providers);

if (Providers.Num() > 0)
{
    // CaptureFrame: 捕获指定 viewport 的下一帧
    // Flags: ECaptureFlags_Launch = 捕获后自动启动 debugger
    Providers[0]->CaptureFrame(nullptr, IRenderCaptureProvider::ECaptureFlags_Launch, TEXT("MyCapture"));
}
```

### 通过 BeginCapture/EndCapture 精确控制捕获范围

```cpp
#include "IRenderCaptureProvider.h"

TArray<IRenderCaptureProvider*> Providers;
IModularFeatures::Get().GetModularFeatureImplementations<IRenderCaptureProvider>(
    IRenderCaptureProvider::GetModularFeatureName(), Providers);

if (Providers.Num() > 0)
{
    IRenderCaptureProvider* Provider = Providers[0];
    FRHICommandListImmediate& RHICmdList = GRHICommandList.GetImmediateCommandList();
    
    // 开始捕获
    Provider->BeginCapture(&RHICmdList, IRenderCaptureProvider::ECaptureFlags_Launch, TEXT("TargetedCapture"));
    
    // ... 在这里执行你想要捕获的渲染指令 ...
    
    // 结束捕获并打开 Xcode
    Provider->EndCapture(&RHICmdList);
}
```

### 捕获文件路径

默认保存路径为：`{ProjectSavedDir}/XcodeGPUTraceCaptures/{FileName}.gputrace`

- 如果未指定文件名，自动使用当前日期时间
- 支持绝对路径和相对路径
- 文件扩展名自动设为 `.gputrace`

## Demo 示例

### 最小集成示例：自定义帧捕获按钮

```cpp
// MyFrameCaptureHelper.h
#pragma once

#include "CoreMinimal.h"
#include "IRenderCaptureProvider.h"

class FMyFrameCaptureHelper
{
public:
    static bool CaptureCurrentFrame(const FString& FileName)
    {
        TArray<IRenderCaptureProvider*> Providers;
        IModularFeatures::Get().GetModularFeatureImplementations<IRenderCaptureProvider>(
            IRenderCaptureProvider::GetModularFeatureName(), Providers);
        
        if (Providers.Num() == 0)
        {
            UE_LOG(LogTemp, Warning, TEXT("No render capture provider available. "
                   "Enable XcodeGPUDebuggerPlugin in Plugins settings."));
            return false;
        }
        
        Providers[0]->CaptureFrame(nullptr, IRenderCaptureProvider::ECaptureFlags_Launch, FileName);
        return true;
    }
};
```

**Build.cs 依赖：**
```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "RenderCore",
    "RHI"
});
```

## 模块依赖

从 `XcodeGPUDebuggerPlugin.Build.cs` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | 基础引擎功能 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `InputCore` | 输入系统核心 |
| `DesktopPlatform` | 桌面平台抽象（获取 Xcode 路径） |
| `Projects` | Plugin 管理 |
| `RenderCore` | 渲染核心 |
| `InputDevice` | 输入设备接口（用于注入 dummy input device 获取 Tick） |
| `RHI` | 渲染硬件接口 |
| `DeveloperSettings` | 开发者设置 |
| `MetalRHI` | Metal 渲染后端 |
| **编辑器额外依赖** | |
| `Slate` / `SlateCore` | UI 框架 |
| `UnrealEd` | 编辑器核心 |
| `MainFrame` | 主窗口 |
| `GameProjectGeneration` | 项目生成 |
| `ToolMenus` | 工具栏菜单扩展 |

第三方依赖：`MetalCPP`（Apple Metal C++ 头文件），弱链接 `Metal.framework`。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-05-27 | `6246f23` | Fix an issue submitted in 43006398 | Bug 修复（UE 内部 issue tracker 编号） |
| 2025-05-27 | `2bef474` | Update the various GPU debugger extensions to only support the new toolbar | 适配 UE5 新版 Viewport Toolbar |
| 2025-05-09 | `4e69b0b` | Convert the PixWIN and XcodeGPUDebugger buttons to the new viewport toolbar | 迁移到新 toolbar 架构（与 PixWIN 插件同步更新） |

### 维护评价

- **创建时间**：2021-07-12，约 4.8 年前
- **最近更新**：2025 年 5 月，有活跃的维护更新
- **维护状态**：✅ **活跃维护** — 2025 年 5 月有多次功能性更新，适配新版编辑器 UI
- **维护方**：由 Apple, Inc. 直接维护（而非 Epic Games），体现了 Apple 对 Metal 生态的投入
- **已知限制**：
  - 仅支持 macOS 平台
  - Shipping 构建中完全禁用（`#if !UE_BUILD_SHIPPING`）
  - 不支持 headless（Null RHI）模式
  - PIE-Eject 模式下从编辑器按钮捕获可能不正常，需要使用控制台命令
- **推荐使用**：如果你在 macOS 上做 Metal 渲染相关的调试/优化工作，这是必备工具。直接一键从 UE5 编辑器跳转到 Xcode GPU Debugger，比手动配置 Metal Capture 高效得多。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/XcodeGPUDebuggerPlugin)
- [官方文档]()（无）
