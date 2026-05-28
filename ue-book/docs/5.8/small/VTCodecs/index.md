# VTCodecs

> Adds codecs from the Apple Video Toolbox Framework to AVCodecs

| 属性 | 值 |
|---|---|
| 中文名 | 视频工具箱编解码器 |
| 分类 | Codecs |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `VTCodecs` (Runtime), `VTCodecsRHI` (Runtime) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2023-11-14 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/VTCodecs) | |

## 用途

VTCodecs 插件为 Unreal Engine 的音视频编解码框架（`AVCodecs`）增加了对 Apple 原生 `Video Toolbox` 框架的支持。它主要解决了在 iOS、macOS 等 Apple 平台上，使用硬件加速进行视频编码（如 H.264/H.265）和解码的需求。通过集成 Video Toolbox，插件允许开发者在 Apple 设备上获得原生的、高性能的视频处理能力。

## 模块列表

*   **`VTCodecs`**: 核心运行时模块，实现与 Apple Video Toolbox 框架交互的编解码器工厂和具体编解码器逻辑。
*   **`VTCodecsRHI`**: 硬件接口（RHI）模块，提供与渲染硬件接口（如 Metal）相关的视频帧和纹理转换支持，确保编解码数据能在 GPU 和游戏引擎间高效流转。

## 使用场景

*   开发面向 iOS 或 macOS 平台的音视频应用，需要利用设备硬件加速进行高效视频编码或解码。
*   在 Apple 平台上进行视频录制、流媒体处理或视频编辑功能开发，追求最佳性能和电池效率。
*   需要在 UE5 中直接处理来自 Apple 设备摄像头或媒体文件的 H.264/H.265 视频流。

## 相关链接

*   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/VTCodecs)
*   [关联基础插件: AVCodecs]()

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了作用域枚举在格式化函数中可能导致输出乱码的错误 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 继续修复因错误的全局替换导致的问题 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 撤销了之前的某个提交（CL51314860） |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复初始化委托注册问题，迁移到新API以避免注册失败 |
| 2026-01-24 | `e793e61e` | Fixed more compile errors when using portable toolchain | 修复了使用便携式工具链时出现的更多编译错误 |

### 维护评价

VTCodecs 是一个于 2023 年创建的实验性插件，主要面向 Apple 平台。从 Git 历史看，截至 2026 年初仍有持续的代码维护和修复，表明它处于 **活跃维护** 状态。近期更新集中在编译问题、平台兼容性和初始化流程的修复上，属于稳定性改进。

*   **年龄**: 🆕（约 3 年）
*   **维护状态**: 活跃维护（最近一次更新在 2026 年 4 月）
*   **建议**: 该插件仍在开发中，但因为标记为 **实验性** 且 **默认未启用**，建议仅在目标平台为 Apple (iOS/macOS) 且明确需要硬件加速视频编解码功能的项目中谨慎试用。请注意其 API 可能会发生变化。