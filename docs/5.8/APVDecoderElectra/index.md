# Advanced Professional Video (APV) Decoder for Electra

> OpenAPV video decoder

| 属性 | 值 |
|---|---|
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `APVDecoderElectra` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-11-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/APVDecoderElectra) | |

## 用途

该插件为 Unreal Engine 的 Electra 媒体播放器框架提供对 **OpenAPV (Advanced Professional Video)** 视频格式的解码支持。APV 是一种面向专业视频制作和广播领域的高质量视频编解码器。此插件的存在使得开发者能够在使用 Electra 媒体播放器时，解码和播放 APV 格式的视频文件，扩展了引擎的媒体格式支持范围。

## 使用场景

- 你正在开发一个需要处理专业视频素材（如广播、后期制作）的应用程序，并且素材采用了 APV 编码格式。
- 你的项目使用了 Electra 媒体播放器作为核心媒体播放组件，现在需要增加对 APV 格式的支持。

## 蓝图用法

该插件主要提供底层的 C++ 解码器实现，未暴露直接的蓝图可调用函数。其功能通过 Electra 媒体播放器的内部管线自动调用，无需在蓝图中显式操作。

## C++ 用法

### 头文件引入

```cpp
#include "APVDecoderElectraModule.h"
```

### 基本用法

该插件的核心是向 Electra 的解码器工厂注册 APV 解码器。通常，这个过程在模块启动时自动完成。

```cpp
// 来自 Source/APVDecoderElectra/Private/APVDecoder/ElectraMediaAPVDecoder.h
// 解码器的注册与注销由模块生命周期管理
class FElectraMediaAPVDecoder
{
public:
    // 在模块启动时调用，向 Electra 注册 APV 解码器
    static void Startup();
    // 在模块关闭时调用，注销 APV 解码器
    static void Shutdown();
};
```

### 进阶用法

作为 Electra 解码器插件，其主要工作是与 `ElectraCodecs` 插件协同。开发者通常不需要直接调用 `Startup`/`Shutdown`，而是通过正确配置项目依赖，让引擎在加载 `APVDecoderElectra` 模块时自动完成解码器的注册。当 Electra 播放器遇到 APV 编码的视频流时，会自动使用此解码器进行解码。

## Demo 示例

以下是一个最小化的示例，展示如何在你的模块中确保 APV 解码器可用（通常由引擎自动处理，此示例用于演示底层原理）。

**MyMediaModule.h**
```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FMyMediaModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MyMediaModule.cpp**
```cpp
#include "MyMediaModule.h"
#include "APVDecoderElectraModule.h" // 引入插件模块头文件

#define LOCTEXT_NAMESPACE "FMyMediaModule"

void FMyMediaModule::StartupModule()
{
    // 注意：实际项目中，APV 解码器的注册由 APVDecoderElectra 模块自身完成。
    // 此处仅为演示如何访问相关模块。
    UE_LOG(LogAPVElectraDecoder, Log, TEXT("MyMediaModule 启动，APV 解码器插件已加载。"));
}

void FMyMediaModule::ShutdownModule()
{
    UE_LOG(LogAPVElectraDecoder, Log, TEXT("MyMediaModule 关闭。"));
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyMediaModule, MyMedia)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UEOpenAPV` | 提供 OpenAPV 编解码器的核心库，是解码功能的基础。 |

## 维护状态

### 近期更新

- 2026-04-20 `3ed2062b` ElectraDecoders：现代化了解码器工厂，使其对其他客户端更易用。
- 2026-01-12 `611dda1f` Electra：将MP4相关工具移至专用插件。
- 2026-01-08 `ccd8e12c` ElectraCodecs：添加了APV比特流解析器和解码器配置记录。
- 2025-11-27 `52c2bc9e` ElectraCodecs：添加了实验性的APV解码器插件。

### 维护评价

该插件的维护状态为**活跃且持续优化**。从提交记录看，其在约5个月内有4次提交，频率稳定。内容从引入实验性解码器，到完善核心解析功能，再到优化架构以提升通用性，显示出清晰的功能演进和积极的维护投入。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/APVDecoderElectra)