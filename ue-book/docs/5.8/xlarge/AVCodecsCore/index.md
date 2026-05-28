# AVCodecs Core

> Core Plugin for various Audio/Video codecs（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 音视频编解码核心 |
| 分类 | Codecs |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AVCodecsCore` (Runtime), `AVCodecsCoreRHI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-25 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/AVCodecsCore) | |

## 用途

AVCodecsCore 是 Unreal Engine 5 中用于处理音频和视频编解码的核心框架插件。它旨在提供一个统一的抽象层，用于管理和调度各种软件及硬件编解码器。该插件解决了在 UE5 中进行音视频处理时，需要直接面对各种平台特定、格式特定编解码 API 的复杂性问题，为开发者提供了一套标准化的接口来实现编解码功能。

插件的主要价值在于：
1. **解耦**：将上层应用逻辑与具体的编解码实现分离。
2. **跨平台**：支持在 Windows、Linux、Mac、Android 和 iOS 上运行。
3. **扩展性**：允许通过添加新的插件模块（如特定格式的编解码器）来扩展功能，而无需修改核心框架。

## 使用场景

- **视频播放与编辑**：在编辑器或运行时播放、编辑视频文件。
- **实时通信与直播推流**：实现实时视频通话、游戏直播推流等需要低延迟编解码的场景。
- **媒体资产处理**：批量转码、压缩或处理项目中的媒体资产。
- **游戏内视频播放**：在游戏中播放过场动画、背景视频等。
- **AR/VR 应用**：处理来自摄像头或传感器的实时视频流。

## 模块列表

| 模块 | 类型 | 用途 |
|---|---|---|
| [AVCodecsCore](./AVCodecsCore.md) | Runtime | 提供音视频编解码的核心抽象、枚举定义、工具函数和基础结构。 |
| [AVCodecsCoreRHI](./AVCodecsCoreRHI.md) | Runtime | 提供与渲染硬件接口 (RHI) 集成的编解码支持，例如硬件加速纹理和 GPU 相关的编解码操作。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量被截断为浮点数的警告代码。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器之间可移植。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了用于格式化函数的强类型枚举可能导致输出乱码的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了 64 位参数使用 32 位格式说明符，以及反之亦然的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志输出宏 UE_LOG 迁移至 UE_LOGF。 |

### 维护评价

该插件处于 **实验性** 状态，创建于约 3 年前（2023 年）。从最近的 Git 历史来看，维护活动集中在 **2026 年 4 月至 5 月**，主要进行了编译器警告修复和跨平台兼容性改进。这表明插件仍在被关注和维护，以应对引擎基础构建的迭代，但 **近期没有新的功能开发**。

由于是实验性插件且默认未启用，不建议在生产环境中未经充分测试就直接使用。它更适合作为**研究、原型开发或学习音视频编解码框架结构**的起点。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/AVCodecsCore)
- [AVCodecsCore 模块文档](./AVCodecsCore.md)
- [AVCodecsCoreRHI 模块文档](./AVCodecsCoreRHI.md)