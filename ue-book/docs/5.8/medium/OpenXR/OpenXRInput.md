# OpenXR

> OpenXR is an open VR/AR standard

| 属性 | 值 |
|---|---|
| 中文名 | 开放XR |
| 分类 | Virtual Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置数据） |
| 模块 | `OpenXRHMD` (Runtime), `OpenXRInput` (Runtime), `OpenXRAR` (Runtime), `OpenXREditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-04-16 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OpenXR) | |

## 用途

OpenXR 是一个开放标准，旨在统一 VR 和 AR 应用的开发。该插件是 Unreal Engine 5 对 OpenXR 标准的官方实现。它解决了 VR/AR 设备碎片化的问题，允许开发者使用一套标准的 API 来支持多种头显（如 Meta Quest、Windows Mixed Reality、HTC Vive 等），而无需为每个设备单独编写代码。该插件主要提供：
- **头显显示 (HMD)**：管理 XR 会话、渲染帧的合成。
- **输入处理**：将 OpenXR 的动作系统映射到 UE 的输入系统（包括传统输入和增强输入）。
- **增强现实 (AR)**：支持基于摄像头和空间追踪的 AR 功能。
- **编辑器支持**：在编辑器中预览和调试 XR 体验。

## 使用场景

- 你正在开发一个需要兼容多种 VR 头显的游戏或应用，希望使用统一的 API。
- 你需要利用 OpenXR 的输入动作系统来设计可移植的控制器交互。
- 你的项目需要支持增强现实（AR）功能，例如基于平面的检测和图像追踪。
- 你需要在 Unreal Editor 中测试和调试 XR 应用，而无需每次都部署到设备。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Begin XR Session` | 使用提供的输入映射上下文启动一个 XR 会话。这将使跟踪系统了解用于 XR 动作控制器的动作和绑定。 | `UOpenXRInputFunctionLibrary` |
| `End XR Session` | 终止当前的 XR 会话。 | `UOpenXRInputFunctionLibrary` |

### 使用示例（蓝图描述）

1.  **启动 XR 会话**：在游戏开始时（例如在 `BeginPlay` 事件中），调用 `Begin XR Session` 节点。你需要将一个包含所有用于 XR 控制器交互的 `UInputMappingContext` 资产的集合（Set）作为输入参数传递给它。该节点返回一个布尔值，指示会话是否成功开始。
2.  **结束 XR 会话**：在游戏结束时或需要退出 XR 体验时，调用 `End XR Session` 节点来清理和关闭会话。

## C++ 用法

### 头文件引入

```cpp
#include "IOpenXRInputPlugin.h"
#include "OpenXRInput.h"
#include "OpenXRInputFunctionLibrary.h"
```

### 基本用法

获取 OpenXR 输入模块实例，并检查其可用性。这是与 OpenXR 输入系统交互的入口点。

```cpp
// 检查 OpenXR 输入模块是否已加载
if (IOpenXRInputPlugin::IsAvailable())
{
    // 获取模块单例
    IOpenXRInputPlugin& OpenXRInputPlugin = IOpenXRInputPlugin::Get();
    // ... 进一步使用
}
```

### 进阶用法

通过 OpenXR 输入插件创建自定义输入设备。以下代码展示了如何创建一个基于 `FOpenXRInput` 的自定义输入设备，并将其注册到引擎中。

```cpp
// 在你的输入设备模块中
#include "IInputDeviceModule.h"
#include "OpenXRInput.h" // 假设你想继承或组合 OpenXR 的功能

class FMyCustomInputDevice : public IInputDevice
{
public:
    FMyCustomInputDevice(const TSharedRef<FGenericApplicationMessageHandler>& InMessageHandler)
        : MessageHandler(InMessageHandler)
    {
        // 如果需要，可以访问 OpenXR 的底层功能
        // 例如，通过 FOpenXRInputPlugin 获取 OpenXRHMD
    }

    // IInputDevice 接口实现
    virtual void Tick(float DeltaTime) override { /* ... */ }
    virtual void SendControllerEvents() override { /* ... */ }
    // ... 其他必要的接口实现

private:
    TSharedRef<FGenericApplicationMessageHandler> MessageHandler;
};

// 在你的输入设备模块中创建设备
TSharedPtr<IInputDevice> FMyInputModule::CreateInputDevice(const TSharedRef<FGenericApplicationMessageHandler>& InMessageHandler)
{
    return MakeShareable(new FMyCustomInputDevice(InMessageHandler));
}
```

## Demo 示例

以下示例展示了一个最简化的输入设备模块结构，它依赖于 OpenXR 输入模块，并注册一个自定义输入设备。

```cpp
// MyXRExampleModule.h
#pragma once

#include "Modules/ModuleManager.h"
#include "IInputDeviceModule.h"

class FMyXRExampleModule : public IInputDeviceModule
{
public:
    // IModuleInterface
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    // IInputDeviceModule
    virtual TSharedPtr<IInputDevice> CreateInputDevice(const TSharedRef<FGenericApplicationMessageHandler>& InMessageHandler) override;
};
```

```cpp
// MyXRExampleModule.cpp
#include "MyXRExampleModule.h"
#include "IOpenXRInputPlugin.h"

#define LOCTEXT_NAMESPACE "FMyXRExampleModule"

void FMyXRExampleModule::StartupModule()
{
    // 模块启动时，可以检查 OpenXR 是否可用
    IOpenXRInputPlugin::IsAvailable();
}

void FMyXRExampleModule::ShutdownModule()
{
    // 清理
}

TSharedPtr<IInputDevice> FMyXRExampleModule::CreateInputDevice(const TSharedRef<FGenericApplicationMessageHandler>& InMessageHandler)
{
    // 创建一个简单的输入设备，实际项目中应实现 IInputDevice 接口
    // 这里为了演示，返回 nullptr。你需要实现一个真正的设备。
    return nullptr;
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyXRExampleModule, MyXRExampleModule)
```

## 模块依赖

要使用 OpenXR 插件的模块，你的 `Build.cs` 需要包含以下特殊依赖。常见依赖（如 Core, Engine, InputCore）已省略。

| 模块 | 用途 |
|---|---|
| `OpenXRInput` | 如果你的模块需要与 OpenXR 的输入系统交互或扩展。 |
| `EnhancedInput` | `OpenXRInput` 模块本身依赖于它，用于将 OpenXR 动作映射到增强输入系统。 |
| `InputEditor` | `OpenXRInput` 模块本身依赖于它，可能用于输入相关的编辑器功能。 |
| `OpenXRHMD` | 如果你的模块需要直接访问头显（HMD）的渲染或追踪功能。 |
| `OpenXRAR` | 如果你的模块需要使用增强现实（AR）功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `0421053e` | [OpenXR][Vulkan] Request TRANSFER_DST_BIT for XR render target swapchains | 为 XR 渲染目标交换链请求 TRANSFER_DST_BIT 位标志，以修复 Vulkan 下的潜在问题。 |
| 2026-05-14 | `a57c6062` | Stereolayers with Supports Depth wobble: prevent dangling next-chain pointers in CompositionDepthTest | 修复支持深度抖动的立体层在组合深度测试时可能出现的悬垂指针问题。 |
| 2026-04-30 | `da4fc827` | PR #14037: Fix no audio when xrGetAudioOutputDeviceGuidOculus returns failure | 修复当 Oculus 的 `xrGetAudioOutputDeviceGuidOculus` 返回失败时，导致无音频输出的问题。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复在格式化函数中使用作用域枚举可能导致垃圾输出的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复格式说明符与参数位宽不匹配的问题，确保 32 位和 64 位参数使用正确的格式符。 |

### 维护评价

OpenXR 插件自 2019 年创建以来，一直是 Unreal Engine 官方支持的 XR 核心组件。尽管它默认未启用，但随着 XR 行业向 OpenXR 标准迁移，其重要性日益增加。

- **活跃维护**：从 Git 日志可以看到，插件在 2026 年 5 月仍有密集的提交，主要集中在 Vulkan 后端、立体渲染层和 Oculus 平台特定的音频修复上。这表明 Epic Games 的团队仍在积极维护和优化此插件。
- **稳定性**：修复内容多为底层渲染和 API 交互的 bug，表明插件已进入成熟期，工作重心转向稳定性和平台兼容性。
- **推荐使用**：**强烈推荐**。对于任何计划支持 OpenXR 标准的 VR/AR 项目，这是唯一且官方的引擎级解决方案。它封装了复杂的底层 API，并提供了与 Unreal 已有输入和渲染系统的集成。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OpenXR)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/openxr-in-unreal-engine/) (通用指南，非插件专属)