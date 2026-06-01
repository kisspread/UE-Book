# RivermaxCore

> Base plugin exposing rivermax to engine（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Rivermax 核心 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RivermaxCore` (Runtime), `RivermaxEditor` (Editor), `RivermaxRendering` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-30 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Rivermax/RivermaxCore) | |

## 用途

此插件为 Unreal Engine 提供了与 **Rivermax** 库集成的底层核心功能。Rivermax 是 NVIDIA 提供的用于高速网络传输（特别是符合 SMPTE ST 2110 标准）的库。`RivermaxCore` 插件的主要目的是**管理通过 IP 网络（如 25/100GbE）发送和接收未压缩视频流的会话**。它是所有基于 Rivermax 的媒体输入/输出功能（如 `MediaOutput`、`MediaCapture`、`MediaSource`）的基础运行时模块。

## 使用场景

-   你需要在 **虚拟摄影棚** 中，通过 25/100GbE IP 网络实时接收来自摄像机的未压缩视频流，用于 LED 墙或虚拟背景渲染。
-   你需要将引擎渲染的帧**以未压缩格式、低延迟地发送**到外部硬件（如监视器、后期系统或其他渲染节点），作为现场制作流程的一部分。
-   你的项目需要实现 **SMPTE ST 2110** 标准下的视频传输工作流。

## 模块概述

-   **RivermaxCore**：运行时核心模块。提供与 Rivermax SDK 交互的底层 API，管理输入和输出媒体流的会话生命周期、缓冲区调度以及设备发现。
-   **RivermaxEditor**：编辑器模块。提供在编辑器中配置 Rivermax 设备、媒体配置和流属性的资产编辑器界面。
-   **RivermaxRendering**：渲染集成模块。负责将 Rivermax 流与 Unreal Engine 的渲染管线集成，处理视频帧的捕获（输入）和提交（输出）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下常量截断产生的编译器警告。 |
| 2026-04-29 | `bef86caa` | Whitespace: followup to migrate UE_LOG to UE_LOGF: Restore newlines in multi-line format strings tha | 格式化修正：补充从 UE_LOG 迁移到 UE_LOGF 后对多行格式字符串中换行符的恢复。 |
| 2026-04-28 | `3348026a` | Rivermax: ANC timecode input, input stream base class refactor, and pixel format unification | 新增 ANC 时间码输入支持，重构输入流基类，并统一像素格式处理。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复作用域枚举在格式化函数中使用可能导致输出错误的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复格式说明符与参数位宽不匹配（32位对64位）的问题。 |

### 维护评价

该插件自创建以来（约 4 年）持续有功能更新和错误修复，**维护活跃**。最近的提交（2026年4-5月）显示其仍在积极开发，包括新功能（时间码输入）、架构重构（流基类）和广泛的编译兼容性修复（格式说明符、浮点模式）。尽管在 `.uplugin` 中标记为 `IsBetaVersion` 和 `Hidden`，且默认不启用，但它是一个针对专业虚拟制作领域的功能性模块，推荐有相应硬件和网络环境的项目使用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Rivermax/RivermaxCore)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Rivermax/RivermaxCore/Tests)