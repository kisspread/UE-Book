# Avid DNxHD® decoder for Electra

> Avid DNxHD® video decoder

| 属性 | 值 |
|---|---|
| 中文名 | Avid DNxHD 解码器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AvidDNxHDDecoderElectra` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-06-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AvidDNxHDDecoderElectra) | |

## 用途

Avid DNxHD® 是一种广泛用于影视后期制作的中间编码格式（压缩视频格式）。此插件为 Electra 媒体播放器框架提供针对 Avid DNxHD 视频流的解码能力，使得 Unreal Engine 能够直接播放包含 DNxHD 轨道的媒体文件（如 `.mov`、`.mxf` 等）。它是 ElectraCodecs 解码器体系的一部分，作为独立插件存在，方便用户按需启用，避免不必要的模块加载。

本质上是将 Avid DNxHD 解码器（通常基于 DirectX 硬件加速或软件实现）集成到 Electra 的异步解码管线中，从而在渲染线程之外完成视频帧的解码。

## 使用场景

- 在影视预可视化（Previs）、虚拟制片（Virtual Production）流程中，需要播放 DNxHD 格式的现场素材或剪辑回放。
- 使用 Electra 播放器播放包含 DNxHD 编码的视频文件，但希望避免因未启用解码器导致播放失败。
- 自定义视频播放器基于 ElectraPlayerComponent 或 ElectraPlayer 时，需要支持专业广播级格式。

## 蓝图用法

此插件不暴露任何可直接在蓝图中调用的节点或函数。它作为解码器后端通过 ElectraCodecs 插件自动注册，无需用户手动操作。只需要在项目设置（Plugins）中启用本插件和 `ElectraCodecs` 插件，播放 DNxHD 媒体时内部会自动调用。

### 启用步骤

1. **编辑 → 插件** → 搜索 “Avid DNxHD decoder for Electra”，勾选启用。
2. **同样启用 “ElectraCodecs” 插件**（自动依赖会提示）。
3. 重启编辑器。

之后，使用 `Media Player` + `Media Source` 播放包含 DNxHD 的视频即可（前提是 Media Source 设置使用 Electra 播放器）。

## C++ 用法

插件仅导出一个静态类 `FElectraMediaAvidDNxHDDecoder`，用于手动控制解码器的初始化和关闭。通常情况下不需要直接调用，因为模块启动时会自动调用 `Startup()`，关闭时自动调用 `Shutdown()`。但在某些自定义场景（如动态加载/卸载解码器）下可以使用。

### 头文件引入

```cpp
#include "Windows/ElectraMediaAvidDNxHDDecoder.h"
```

### 基本用法

```cpp
// 手动启动解码器（通常在模块加载时调用）
FElectraMediaAvidDNxHDDecoder::Startup();

// ... 使用 Electra 播放 DNxHD 视频 ...

// 手动关闭解码器（通常在模块卸载时调用）
FElectraMediaAvidDNxHDDecoder::Shutdown();
```

**来源文件**：`Engine/Plugins/Media/AvidDNxHDDecoderElectra/Source/Private/Windows/ElectraMediaAvidDNxHDDecoder.h`

### 进阶用法

此插件与 ElectraCodecs 深度集成，通过 `ElectraCodecs` 的扩展点注册解码器工厂。如果要自定义解码器注册行为，可以阅读 `IAvidDNxHDDecoderElectraModule` 接口（未公开头文件）或修改 `Source/Private/AvidDNxHDDecoderElectraModule.cpp` 中的模块启动逻辑。

## Demo 示例

以下是一个最小 C++ 示例，展示如何在游戏模块中调用启动/关闭，并确保 DNxHD 解码器可用。假设您的模块已添加对 `AvidDNxHDDecoderElectra` 和 `ElectraCodecs` 的依赖。

```cpp
// MyVideoPlayerModule.h
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyVideoPlayerModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};

// MyVideoPlayerModule.cpp
#include "MyVideoPlayerModule.h"
#include "Windows/ElectraMediaAvidDNxHDDecoder.h"

void FMyVideoPlayerModule::StartupModule()
{
    // 启动DNxHD解码器（如果插件已加载）
    FElectraMediaAvidDNxHDDecoder::Startup();
}

void FMyVideoPlayerModule::ShutdownModule()
{
    FElectraMediaAvidDNxHDDecoder::Shutdown();
}

IMPLEMENT_MODULE(FMyVideoPlayerModule, MyVideoPlayer);
```

**注意**：实际使用中无需手动调用，模块自动处理。此示例仅用于展示手动控制的可能性。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ElectraCodecs` | 提供 Electra 解码器框架，本插件通过它注册 DNxHD 解码器 |
| `DirectX` | 底层视频解码所需的 DirectX 接口（通常用于硬件加速） |

其余依赖（Core、CoreUObject、Engine 等）为常见基础依赖，不逐一列出。

## 维护状态

### 近期更新

根据 git log（截至 2025-09-24）：

- 2025-09-24 `f9460684` — ElectraDecoders: Added missing explicit ESPMode on shared pointers of D3D helper for consistency
- 2025-09-23 `569bf4e1` — ElectraDecoders: Passing any low level D3D12 failures up for better error reporting
- 2025-08-29 `caefc315` — [Electra] Avid DNxHD support 12 bits (HQX) format.
- 2025-08-06 `831eeb24` — Reworked ElectraSamples, ElectraUtils and the decoder output of Electra Player
- 2025-06-10 `2d174355` — Electra: Removal of the platform resource delegate and the wrapping plugin

### 维护评价

- **创建时间**：2025-06-10（约4个月前）
- **最近更新频率**：创建后几乎每月都有提交，包括功能更新（支持12位HQX格式）和代码重构。
- **活跃度**：非常活跃，目前仍在积极维护，近期修复了 D3D12 错误处理和指针一致性。
- **已知限制**：目前仅支持 Win64 平台（x64），不支持 arm64 和 Server 目标。
- **是否推荐使用**：✅ 推荐。对于需要 DNxHD 解码的 Electra 播放需求，这是官方唯一的标准实现。建议与 `ElectraCodecs` 插件一同启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AvidDNxHDDecoderElectra)
- [ElectraCodecs 插件文档](https://docs.unrealengine.com/5.4/en-US/electra-codecs-in-unreal-engine/)（需自行查阅版本）