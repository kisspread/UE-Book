# OpenImageDenoise

> Denoising engine for the Unreal Path Tracer based on Intel's OpenImageDenoise library.

| 属性 | 值 |
|---|---|
| 中文名 | 路径追踪降噪 |
| 分类 | Denoising |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OpenImageDenoise` (ClientOnly) |
| 实验性 | 否 |
| 创建时间 | 2021-05-27 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/OpenImageDenoise) | |

## 用途

此插件为 Unreal Engine 的路径追踪器 (`r.PathTracing`) 提供了基于 Intel OpenImageDenoise (OIDN) 库的降噪功能。路径追踪器通过光线模拟生成真实感图像，但会产生大量噪点，需要极长的渲染时间才能收敛。此插件利用 AI 降噪技术，在渲染初期（少量样本）对图像进行智能去噪，从而大幅缩短获得高质量图像的等待时间，提升工作流效率。

## 使用场景

-   你在进行建筑可视化或产品设计，需要实时预览或快速迭代路径追踪渲染结果。
-   你为影视或动画项目创建路径追踪序列，希望减少最终帧的渲染时间。
-   你希望使用 Intel GPU 或 CPU 加速的降噪方案来优化路径追踪工作流。

## 蓝图用法

此插件主要通过控制台变量（CVar）进行控制，没有暴露用于蓝图的 `BlueprintCallable` 函数。其行为通过引擎的路径追踪器模块调用内部接口实现。

### 核心控制方式

| 控制台变量 (CVar) | 说明 |
|---|---|
| `r.PathTracing.Denoiser` | 启用/禁用降噪器。设置为 `1` 启用。 |
| `r.PathTracing.Denoiser.Type` | 指定降噪器类型。当加载了此插件后，可以设置为 `Oidn` 以使用 Intel OpenImageDenoise。 |

### 使用示例（蓝图描述）

在蓝图中，可以通过 `Execute Console Command` 节点来动态设置降噪器。

1.  添加一个 `Execute Console Command` 节点。
2.  在 `Command` 输入框输入 `r.PathTracing.Denoiser 1`。
3.  添加另一个 `Execute Console Command` 节点。
4.  在 `Command` 输入框输入 `r.PathTracing.Denoiser.Type Oidn`。
5.  确保已启用路径追踪（`r.PathTracing 1`）。

## C++ 用法

此插件主要服务于引擎内部的路径追踪器模块，没有公开的、面向使用者的 C++ API。其核心逻辑由引擎的路径追踪器在适当的时候调用。

### 基本用法

此插件的功能主要通过控制台变量激活，无需在 C++ 代码中直接调用。要启用它，需要：
1.  确保插件已启用（在 `.uproject` 文件或编辑器插件列表中）。
2.  通过控制台命令启用降噪器并指定类型。

```cpp
// 通常在控制台或配置文件中设置，代码中可如下操作（非必需）
#include "HAL/IConsoleManager.h"

// 启用路径追踪降噪
IConsoleManager::Get().FindConsoleVariable(TEXT("r.PathTracing.Denoiser"))->Set(1);
// 设置降噪器类型为 OIDN
IConsoleManager::Get().FindConsoleVariable(TEXT("r.PathTracing.Denoiser.Type"))->Set(TEXT("Oidn"));
```
*（此代码仅为演示控制台变量操作，并非插件直接 API）*

### 进阶用法

对于需要自定义降噪行为的开发者，可能需要深入研究 `OpenImageDenoise` 模块的源码，并理解 `FPathTracingDenoiser` 接口是如何被 `OIDN` 实现和注册的。这通常涉及修改引擎代码或插件本身，不推荐常规使用。

## Demo 示例

由于此插件没有公开的 API，最小示例是确保它在环境中正常工作并产生降噪效果。

**前提条件**：你的硬件和驱动支持 Intel Open Image Denoise（通常需要支持 Intel® oneAPI 的 CPU 或 Intel Arc GPU）。

**步骤**：
1.  确保你的项目启用了 `OpenImageDenoise` 插件。
2.  打开一个包含简单场景的关卡。
3.  在控制台中依次输入：
    ```
    r.PathTracing 1
    r.PathTracing.Denoiser 1
    r.PathTracing.Denoiser.Type Oidn
    r.PathTracing.SamplesPerPixel 1
    ```
4.  观察视口。在只有 1 个样本的极高噪点情况下，降噪器会介入，输出一个相对清晰但可能有细节模糊的预览图像。随着样本数增加，降噪效果会与路径追踪收敛结果融合。

## 模块依赖

从 `OpenImageDenoise.Build.cs` 分析：

| 模块 | 用途 |
|---|---|
| `MessageLog` | 用于输出与降噪器相关的日志或错误消息。 |

无其他特殊依赖（仅标准 Core/Engine 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 更新了 GPU 同步 API 调用，采用更统一的接口。 |
| 2026-03-04 | `ac7c846a` | Path Tracer: Refactor UE_LOG calls to UE_LOGF and remove unused deprecated plugin interface | 清理代码，重构日志宏，并移除了废弃的接口。 |
| 2025-06-03 | `0a44e4b8` | Plugin modules can be included & excluded on a per-architecture basis. | 插件现在支持按 CPU 架构进行包含/排除，本次更新应用了此规则（明确排除了 Win64 的 ARM 架构）。 |
| 2025-01-15 | `d190c59c` | Miscellaneous fixes for Windows Arm64 | 修复了一些在 Windows ARM64 平台上的编译或兼容性问题。 |
| 2024-12-06 | `d439e46e` | OpenImageDenoise: Fix alpha channel denoising | 修复了对图像 Alpha 通道的降噪处理问题。 |

### 维护评价

此插件**仍在积极维护**。从 2021 年创建至今，一直有持续的更新，最近一次功能性更新（GPU API 调整）发生在 2026 年 4 月。更新内容包括平台兼容性修复、代码清理和 Bug 修复，表明 Epic Games 将其作为路径追踪器的一个重要可选组件进行维护。作为一个依赖第三方库的集成插件，其更新频率与上游 Intel OIDN 库的发布以及引擎路径追踪器的开发进度相关。**推荐使用**，它是获得快速路径追踪预览的有效工具，尤其适合 Windows x64 平台。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/OpenImageDenoise)
- [Intel Open Image Denoise 官网](https://www.openimagedenoise.org/) (上游库文档)
- [官方文档]() (无专属文档，请参考路径追踪器文档)