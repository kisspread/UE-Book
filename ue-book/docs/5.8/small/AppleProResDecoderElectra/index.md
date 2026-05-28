# Apple ProRes Decoder for Electra

> Implements video playback of Apple ProRes encoded videos. Apple ProRes is a high quality, lossy video compression format.

| 属性 | 值 |
|---|---|
| 中文名 | ProRes 解码器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AppleProResDecoderElectra` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-04-03 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AppleProResDecoderElectra) | |

## 用途

本插件为 Unreal Engine 的 **Electra 媒体播放器框架**提供针对 **Apple ProRes** 视频编解码器的解码支持。ProRes 是一种广泛应用于专业影视后期制作的高质量、低压缩损失的视频格式。该插件的存在使得在使用 Electra 播放器播放 `.mov` 等包含 ProRes 编码视频流的媒体文件时，能够进行硬件加速或软件解码。

它并非一个通用的媒体播放器，而是 Electra 框架中的一个**解码器模块**。其核心功能是将 ProRes 编码的视频比特流解码为引擎可使用的像素数据。

## 使用场景

- 你在 Unreal Engine 中需要播放使用 **Apple ProRes 422, 4444** 等编码的高质量视频素材（常见于从 Final Cut Pro、DaVinci Resolve 等专业软件导出的文件）。
- 你的目标平台是 **Windows 64位（非ARM64）** 或 **Mac**，并希望通过 Electra 播放器进行低延迟、高画质的视频回放。

## 蓝图用法

根据提供的源码分析，该插件是一个底层的解码器实现模块，**不直接暴露任何蓝图可调用的函数或属性**。所有功能均通过 Electra 媒体播放器框架在后台调用。

### 核心节点

无。要使用此解码器播放 ProRes 视频，您应使用标准的 **Media Framework** 蓝图节点，如 `Create Media Player`，`Open Source` 等，并确保该插件已启用。Electra 播放器会自动检测并使用可用的 ProRes 解码器。

### 使用示例（蓝图描述）

1.  在插件列表中启用 “**Apple ProRes Decoder for Electra**” 插件。
2.  使用标准的 Media Player 蓝图工作流，创建 Media Player 资产并选择使用 **Electra** 播放器。
3.  在 Open Source 节点中，提供一个包含 ProRes 视频流的媒体源（如 `.mov` 文件路径）。
4.  如果文件有效且解码器正常工作，视频将被解码并显示在 Media Texture 或 Media Player 组件上。

## C++ 用法

### 头文件引入

该插件是作为 Electra 框架的解码器注册的，不直接为上层游戏逻辑提供头文件。其内部结构遵循 Electra 的解码器模块接口。

### 基本用法

从模块注册代码推断，解码器通过静态方法在模块启动时注册到 Electra 框架中。

```cpp
// 模块启动时会调用此函数，将 ProRes 解码器注册到 Electra 框架。
// 文件: Source/AppleProResDecoderElectra/Private/ProResDecoder/ElectraMediaProResDecoder.cpp
void FElectraMediaProResDecoder::Startup()
{
    // 向 Electra 注册 ProRes 解码器工厂的代码
}

// 模块卸载时注销解码器。
void FElectraMediaProResDecoder::Shutdown()
{
    // 从 Electra 注销 ProRes 解码器工厂的代码
}
```

### 进阶用法

对于绝大多数用户，无需直接操作此解码器的 C++ 代码。解码器的行为通过 Electra 播放器配置或控制台变量进行调优（如果插件提供了相关的 `ConsoleVariable`）。开发者主要的工作是**集成**而非**调用**。

## Demo 示例

此插件不包含独立的示例或可演示的资产。它是一个运行时依赖项。一个最小使用场景是创建一个简单的测试关卡，其中包含一个 Media Player 蓝图，用于打开并播放一个 ProRes 编码的视频文件，以验证解码器是否工作。

## 模块依赖

从 `Build.cs` 分析，该插件依赖以下模块：

| 模块 | 用途 |
|---|---|
| `DirectX` | 用于可能的硬件加速解码支持（特别是 Windows 平台）。 |

此外，它作为插件依赖 `ElectraCodecs`，这是其正常工作的**必要前提**。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-20 | `3ed2062b` | ElectraDecoders: modernized the decoder factory to be more usable for other clients | 现代化解码器工厂接口，便于其他客户端集成 |
| 2026-01-28 | `5f766aee` | Fixed modules that does not support portable toolchain | 修复了不支持可移植工具链的模块 |
| 2026-01-12 | `611dda1f` | Electra: Moved mp4 related utilities into dedicated plugin | 将MP4相关工具移至独立插件，进行代码拆分 |
| 2025-11-19 | `514ccff4` | ElectraCodecs: Add information about the decoder implementation being used for decoding. | 为解码器添加实现信息日志，便于调试 |
| 2025-09-23 | `a0779f41` | ElectraDecoders: Added missing explicit ESPMode on shared pointers of D3D helper for consistency | 为D3D帮助类的共享指针补充显式ESPMode，保持代码一致性 |

### 维护评价

- **创建时间**: 2023 年 4 月创建，至今约 2 年半。
- **更新频率**: 从 git 记录看，每隔数月会有维护性或改进性更新，最近一次在 2026 年 4 月。
- **活跃度**: **维护中**。该插件作为 Electra 播放器生态的一部分，仍在接收 bug 修复、接口优化和代码整理。
- **已知限制**:
    - 仅支持 **Win64** 和 **Mac** 平台。
    - 不支持 **Win64:arm64**（Windows ARM 设备）。
    - 不支持服务器目标（`Server` TargetDenyList）。
    - 默认不启用，需要用户手动在插件列表中启用。
- **推荐使用**: 如果你的项目需要在上述支持平台上播放 ProRes 视频，**推荐启用**此插件。它是官方提供的解码器实现，稳定且与 Electra 框架深度集成。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AppleProResDecoderElectra)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/media-framework/)（Electra 媒体框架通用文档）