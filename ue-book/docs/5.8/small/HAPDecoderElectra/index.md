# HAP Decoder for Electra

> Implements video playback of the HAP Codec. HAP is a high performance, high resolution codec that runs on the GPU.

| 属性 | 值 |
|---|---|
| 中文名 | HAP 解码器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `HAPDecoderElectra` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-04-03 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/HAPDecoderElectra) | |

## 用途

HAP 是一种专为实时、高性能视频回放设计的编解码器，其核心特点是**解码过程在 GPU 上完成**，非常适合高分辨率、低延迟的视频播放场景（如装置艺术、VJ 表演、沉浸式体验等）。

本插件为 UE5 的 Electra 媒体框架注册了 HAP 编解码器的解码实现。启用后，Electra Media Player 即可透明地播放 HAP 编码的视频文件，无需额外代码或蓝图配置。插件本身不暴露任何公共 API，作为编解码器插件完全在后台工作。

**注意**：此插件默认未启用（`EnabledByDefault: false`），需要手动在项目设置中启用。

## 使用场景

- 你需要播放 HAP 编码的高分辨率视频（如 4K/8K 实时视频素材）
- 你在做沉浸式装置、LED 墙或投影映射，需要 GPU 解码以降低 CPU 开销
- 你的项目使用 Electra 作为媒体播放后端，需要支持 HAP 容器格式
- 目标平台为 Win64 或 Mac（插件仅支持这两个平台）

## 蓝图用法

本插件不包含任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。它是 Electra 框架的底层解码器实现，注册过程在模块启动时自动完成。

**使用方式**：启用插件后，通过标准的 Electra Media Player 蓝图节点播放 HAP 编码的视频文件即可，无需任何特殊操作。

### 使用示例（蓝图描述）

1. 在项目设置中启用 **HAPDecoderElectra** 插件
2. 使用 **Media Player** 资产，选择 Electra 作为播放后端
3. 将 HAP 编码的视频文件（`.mov` 容器）添加到项目
4. 通过 `Open Source` 或 `Open URL` 节点播放视频
5. HAP 解码器会自动被 Electra 框架选中并使用

## C++ 用法

本插件不暴露公共 C++ API。解码器在模块启动时自动注册到 Electra 编解码器工厂，对使用者透明。

### 模块启停（内部机制）

解码器的生命周期由模块自动管理：

```cpp
// 来源: Source/HAPDecoderElectra/Private/HAPDecoder/ElectraMediaHAPDecoder.h

class FElectraMediaHAPDecoder
{
public:
    // 模块启动时注册 HAP 解码器到 Electra 框架
    static void Startup();
    // 模块关闭时注销 HAP 解码器
    static void Shutdown();
};
```

### 日志类别

```cpp
// 来源: Source/HAPDecoderElectra/Private/HAPDecoderElectraModule.h

// HAP 解码器专用日志类别，可用于调试解码问题
DECLARE_LOG_CATEGORY_EXTERN(LogHAPElectraDecoder, Log, All);
```

在控制台中使用 `Log LogHAPElectraDecoder Verbose` 可启用详细日志输出，排查 HAP 解码问题。

## Demo 示例

本插件不提供可编程的公共接口，无法编写独立的 Demo 代码。使用方式是启用插件后通过 Electra Media Player 播放 HAP 视频文件。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DirectX` | GPU 解码所需的 DirectX 图形 API 支持（HAP 解码在 GPU 上完成） |

插件还依赖 **ElectraCodecs** 插件（在 `.uplugin` 的 Plugins 依赖中声明），这是 Electra 媒体框架的编解码器基础设施。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-20 | `3ed2062b` | ElectraDecoders: modernized the decoder factory to be more usable for other clients | 现代化解码器工厂，提升对外部客户端的可用性 |
| 2026-01-21 | `7ea56be1` | CopyBuffer now always runs on the decoder thread and is no longer outsourced to a async task in orde | CopyBuffer 改为始终在解码线程执行，移除异步任务 |
| 2025-11-19 | `514ccff4` | ElectraCodecs: Add information about the decoder implementation being used for decoding. | 添加解码器实现信息输出，便于调试识别 |
| 2025-09-23 | `a0779f41` | ElectraDecoders: Added missing explicit ESPMode on shared pointers of D3D helper for consistency | 为 D3D 辅助对象的共享指针补充显式 ESPMode |
| 2025-09-17 | `ed6af5de` | ElectraDecoders: Passing any low level D3D12 failures up for better error reporting | D3D12 底层错误向上传递，改善错误报告机制 |

### 维护评价

**活跃维护**。该插件自 2023 年创建以来持续有更新，最近一次更新距今不到 1 个月。更新内容涵盖：
- 解码器架构现代化重构
- 线程模型优化（移除不必要的异步任务）
- 错误处理改进（D3D12 故障上报）
- 调试信息增强

作为 Electra 媒体框架编解码器生态的一部分，该插件随 ElectraCodecs 的迭代持续演进。由于默认未启用，适合有特定 HAP 视频播放需求的项目按需开启。推荐在需要 GPU 加速高分辨率视频回放时使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/HAPDecoderElectra)
- [HAP 编解码器官网](https://hap.video/)（第三方技术参考）
- [ElectraCodecs 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraCodecs)（本插件的依赖项）