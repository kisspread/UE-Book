# FLAC audio decoder for Electra

> Implements FLAC audio playback with the Electra media player

| 属性 | 值 |
|---|---|
| 中文名 | FLAC 音频解码器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `FlacDecoderElectra` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/FlacDecoderElectra) | |

## 用途

该插件为 Electra 媒体播放器提供了 FLAC（Free Lossless Audio Codec）音频解码能力。Electra 是 UE 内置的跨平台媒体播放框架，原生支持多种音视频格式，但缺少对 FLAC 的支持。此插件通过注册一个 `IElectraCodecFactory` 实现，让 Electra 能够解码 FLAC 音频流，用于游戏内背景音乐、语音对白等无损音频场景。

## 使用场景

- 项目使用 Electra 媒体播放器播放音频，并且需要支持 FLAC 格式（例如高保真音乐、无损音效）。
- 已有通过 `FMediaPlayer` 或 Electra 播放音频的代码，希望扩展格式支持而不切换播放器。
- 开发 Windows 平台产品，需要质量无损、压缩率较高的音频格式（FLAC 比 WAV 更节省空间）。

## 蓝图用法

该插件内部工作，不提供蓝图可调用的函数或节点。启用插件后，Electra 自动获得 FLAC 解码能力，无需额外蓝图逻辑。

### 核心节点

无。

## C++ 用法

### 头文件引入

```cpp
#include "FlacDecoder/ElectraMediaFlacDecoder.h"
```

### 基本用法

插件在 `StartupModule` 中自动注册解码器，无需手动调用。但若需要精细控制生命周期，可以显式调用：

```cpp
// 注册 FLAC 解码器到 Electra
FElectraMediaFlacDecoder::Startup();

// 当不再需要解码器时注销
FElectraMediaFlacDecoder::Shutdown();
```

`CreateFactory()` 通常由 Electra 内部使用，返回编解码工厂的单例。

### 进阶用法

在自定义模块的加载/卸载阶段管理解码器生命周期（通常不需要，因为插件模块已自动处理）：

```cpp
// MyModule.cpp
#include "FlacDecoder/ElectraMediaFlacDecoder.h"

void FMyModule::StartupModule()
{
    // 如果插件未自动启用，可以手动调用（实际插件已处理）
    FElectraMediaFlacDecoder::Startup();
}

void FMyModule::ShutdownModule()
{
    FElectraMediaFlacDecoder::Shutdown();
}
```

## Demo 示例

一个最小示例，演示如何在自定义模块中引用并确认解码器可用。

**MyFlacDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyFlacDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MyFlacDemo.cpp**
```cpp
#include "MyFlacDemo.h"
#include "FlacDecoder/ElectraMediaFlacDecoder.h"

void FMyFlacDemoModule::StartupModule()
{
    if (FElectraMediaFlacDecoder::CreateFactory().IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("FLAC decoder factory is ready."));
    }
}

void FMyFlacDemoModule::ShutdownModule()
{
    // 无需手动关闭，插件模块会处理
}

IMPLEMENT_MODULE(FMyFlacDemoModule, MyFlacDemo)
```

需要确保在模块的 `.Build.cs` 中依赖 `FlacDecoderElectra` 和 `ElectraCodecs`（见模块依赖）。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ElectraCodecs` | 提供 Electra 编解码框架，工厂注册接口及基础解码器接口 |

启动该插件后，你自己的模块 **不需要额外依赖** `FlacDecoderElectra`（除非你想手动调用 `Startup/Shutdown`）。通常只需在 `.uproject` 中启用 `FlacDecoderElectra` 即可。

## 维护状态

### 近期更新

| 日期 | Hash | Commit 说明 |
|---|---|---|
| 2025-08-06 | `831eeb24` | 重构 ElectraSamples、ElectraUtils 以及解码器输出 |
| 2025-06-10 | `2d174355` | 移除平台资源委托和包装插件 |
| 2024-10-22 | `50c3f01e` | 为解码器添加比特流处理器 |
| 2024-09-26 | `9dd9ac6f` | 添加字典参数以在实例创建时接收解码器信息 |
| 2024-08-27 | `bcce1e72` | 在 Windows 上启用 FLAC 音频解码 |

### 维护评价

- **创建时间**：2024年8月，至今约1年。
- **更新频率**：2025年仍有功能性更新（如解码器输出重构），活跃维护中。
- **已知问题**：无公开问题或限制。
- **推荐度**：推荐使用。该插件是 Electra 播放 FLAC 的唯一官方方案，适用于 Windows 平台无损音频需求。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/FlacDecoderElectra)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Programs/UnrealAutomationTool/.../)（暂无独立测试）