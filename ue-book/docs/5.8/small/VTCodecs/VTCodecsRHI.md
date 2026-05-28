# VTCodecs

> Adds codecs from the Apple Video Toolbox Framework to AVCodecs

| 属性 | 值 |
|---|---|
| 中文名 | VT 编解码器 |
| 分类 | Codecs |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `VTCodecs` (Runtime), `VTCodecsRHI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-14 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/VTCodecs) | |

## 用途

VTCodecs 为 UE5 的 AVCodecs（音视频编解码器）插件体系集成了 Apple 的 Video Toolbox 框架。它提供了基于 macOS/iOS 原生硬件加速能力的 H.264/H.265 视频编码器和解码器实现。

该插件解决的问题是：在 Apple 平台上，UE5 需要一个利用系统级硬件编解码能力的高性能视频处理方案。Video Toolbox 是 Apple 提供的低级别视频编解码 API，可以直接访问硬件编码器/解码器（如 Apple Silicon 的媒体引擎），相比纯软件编解码有显著的性能优势。

插件包含两个模块：
- **VTCodecs**：核心编解码器逻辑，实现 Video Toolbox 的编码器和解码器抽象
- **VTCodecsRHI**：将 VT 编解码器与 UE5 的 RHI（渲染硬件接口）层桥接，支持 GPU 纹理的直接编解码

> ⚠️ 此插件默认禁用且处于实验性阶段，仅适用于 macOS/iOS 平台。

## 使用场景

- 你在 macOS/iOS 上进行视频录制或流媒体推流，需要硬件加速的 H.264/H.265 编码
- 你需要在 Apple 平台上解码来自网络或文件的视频流，利用硬件解码降低 CPU 占用
- 你在构建 AVCodecs 自定义编解码管线，需要注册 Video Toolbox 后端作为编解码方案

## 蓝图用法

该插件作为底层编解码器后端，通常不直接暴露蓝图节点。其 API 主要通过 AVCodecs 的上层接口使用。

## C++ 用法

### 头文件引入

```cpp
#include "VTCodecsModule.h"
```

### 基本用法

该插件作为 AVCodecs 的编解码器后端注册，使用时需通过 AVCodecs 的统一接口：

```cpp
// Video Toolbox 编解码器通过 AVCodecs 的模块系统自动注册
// 无需手动实例化，启用插件后即可通过以下方式使用：

#include "AVCodecs/Public/VideoEncoder.h"
#include "AVCodecs/Public/VideoDecoder.h"

// 编码器会自动检测并使用 Video Toolbox 后端（macOS/iOS 平台）
```

## Demo 示例

作为底层编解码器后端，此插件不包含独立的 Demo。使用时参考 AVCodecs 主插件的示例，将编解码器后端切换为 Video Toolbox 即可。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AVCodecs` | AVCodecs 编解码器框架基座 |
| `AVRHI` | 音视频 RHI 桥接层 |

> Apple Video Toolbox 框架通过平台 SDK 自动链接，无需额外配置。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复作用域枚举在格式化函数中导致的输出错误 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修正前次错误的查找替换操作 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退之前的提交 CL51314860 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing registry | 迁移核心委托 API 修复注册遗漏问题 |
| 2026-01-24 | `e793e61e` | Fixed more compile errors when using portable toolchain | 修复可移植工具链下的更多编译错误 |

### 维护评价

该插件创建于 2023 年 11 月，至今约 2 年。从最近的提交记录来看，2026 年仍有活跃更新，但主要是编译修复和 API 适配性的改动（如核心委托 API 迁移、作用域枚举修复），而非功能性开发。插件一直处于实验性状态且默认禁用，尚未进入正式发布流程。

- **优点**：仍在跟随引擎主线进行兼容性维护
- **不足**：长期停留在实验阶段，无实质性功能迭代
- **建议**：仅在 macOS/iOS 平台的开发/测试环境中使用，不建议用于生产项目

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/VTCodecs)
- [AVCodecs 父插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs)