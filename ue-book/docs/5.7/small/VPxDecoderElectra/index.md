# VP8 and VP9 software decoder for Electra

> Implements VP8 and VP9 playback with the Electra media player on desktop machines

| 属性 | 值 |
|---|---|
| 中文名 | VP8/VP9软件解码器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `VPxDecoderElectra` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-03-25 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/VPxDecoderElectra) | |

## 用途

VPxDecoderElectra 为 Electra 媒体播放器（`ElectraPlayer`）添加 VP8 和 VP9 视频编码的软件解码支持。默认情况下，Electra 播放器使用硬件解码器，但对于桌面平台（Windows、Mac、Linux），VP8/VP9 硬件解码支持不够普遍，此插件提供纯 CPU 的软件解码方案，确保在任何显卡上都能播放 WebM/MKV 等容器中的 VP8/VP9 视频流。

该插件通过实现 `IElectraCodecFactory` 接口，将解码器注册到 Electra 的解码器管线中，当播放器遇到 VP8/VP9 编码流时自动调用。

## 使用场景

- 你需要播放 WebM 格式的视频（如从 YT-DLP 下载的 VP8/VP9 视频）
- 目标平台为 Windows、Mac 或 Linux，且不能依赖硬件解码支持
- 项目使用了 `ElectraPlayer`（或基于 `MediaPlayer` 搭配 `MediaSource`）作为视频播放方案
- 需要可靠、跨平台的 VP8/VP9 解码能力

## 蓝图用法

该插件完全用 C++ 实现，没有暴露任何 BlueprintCallable 函数或 BlueprintReadWrite 属性。解码器在 Electra 媒体播放器内部自动使用，无需在蓝图手动调用。

若需要使用 Electra 播放器播放 VP8/VP9 视频，只需在蓝图中使用标准的 `MediaPlayer` 和 `MediaSource` 资产，并将媒体源指定为 WebM 文件即可。解码器的启用由插件在后端自动完成。

## C++ 用法

### 头文件引入

```cpp
#include "VPxDecoder/ElectraMediaVPxDecoder.h"
```

### 基本用法

该插件通常作为模块被 Electra 在启动时自动加载。若需手动注册/注销解码器（如仅在特定条件下启用），可使用以下静态方法：

```cpp
// 启动时注册 VP8/VP9 解码器工厂
FElectraMediaVPxDecoder::Startup();

// 关机前注销
FElectraMediaVPxDecoder::Shutdown();
```

`CreateFactory()` 返回 `TSharedPtr<IElectraCodecFactory>`，可用于测试或手动插入解码器管线：

```cpp
TSharedPtr<IElectraCodecFactory> VPxFactory = FElectraMediaVPxDecoder::CreateFactory();
// 将 factory 添加到 Electra 解码器注册表中（通常不需要手动操作）
```

### 进阶用法

一般情况下，将插件启用后（设置文件或 `Build.cs` 中添加依赖），Electra 播放器会自动使用此解码器。无需额外代码。例如，通过 `IMediaPlayer` 播放一个 WebM 文件时：

```cpp
#include "MediaPlayer.h"
#include "MediaSource.h"

UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
UMediaSource* MediaSource = CreateMediaSourceFromFile("/Game/Movies/SampleVP9.webm");
MediaPlayer->OpenSource(MediaSource);
// 播放器内部会自动匹配 VP9 解码器
```

如果希望显式检查解码器是否已注册，可以调用 `FElectraMediaVPxDecoder::CreateFactory()` 并检查返回值是否有效。

## Demo 示例

以下是一个最小可编译的 C++ 示例，演示如何使用 Electra 播放器播放 VP9 视频，无需手动注册解码器（依赖插件自动注册）。

### Demo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "VPxDemoComponent.generated.h"

UCLASS(BlueprintType, meta=(BlueprintSpawnableComponent))
class UVPxDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Media")
    UMediaPlayer* MediaPlayer;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Media")
    UMediaSource* VP9MediaSource;

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "Media")
    void PlayVP9Video();

    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
};
```

### Demo.cpp

```cpp
#include "VPxDemoComponent.h"
#include "MediaPlayer.h"
#include "MediaSource.h"

void UVPxDemoComponent::BeginPlay()
{
    Super::BeginPlay();
    // 通常不需要额外初始化，插件会自动注册
    // 但若想确认解码器可用，可调用 FElectraMediaVPxDecoder::Startup();
}

void UVPxDemoComponent::PlayVP9Video()
{
    if (!MediaPlayer || !VP9MediaSource)
    {
        UE_LOG(LogTemp, Warning, TEXT("MediaPlayer or MediaSource not set."));
        return;
    }
    MediaPlayer->OpenSource(VP9MediaSource);
}

void UVPxDemoComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    Super::EndPlay(EndPlayReason);
    // 播放器关闭后解码器自动注销
}
```

**注意**：示例依赖于 `VPxDecoderElectra` 插件已启用，且项目 `.Build.cs` 中添加了 `"VPxDecoderElectra"` 和 `"ElectraPlayer"` 模块依赖。

## 模块依赖

要在自己的模块中使用 VPxDecoderElectra，需在 `Build.cs` 中添加以下依赖：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "VPxDecoderElectra",
    "ElectraCodecs",
    "ElectraSamples"
});
```

其中 `ElectraCodecs` 是解码器工厂的注册基础设施，`ElectraSamples` 提供视频样本处理支持。

| 模块 | 用途 |
|---|---|
| `ElectraCodecs` | 提供 `IElectraCodecFactory` 接口，解码器注册机制 |
| `DirectX` (Win64) | 用于 D3D12 辅助纹理和同步，提升多平台兼容性（在 Mac/Linux 上可能使用其他图形 API） |

**注意**：`DirectX` 依赖仅在 Win64 平台上生效；Mac 和 Linux 使用 Metal/Vulkan 原生接口。

## 维护状态

### 近期更新

- 2025-09-24 `f9460684` 为 D3D 辅助共享指针添加显式 `ESPMode`，增强一致性
- 2025-09-23 `569bf4e1` 传递底层 D3D12 失败信息，改善错误报告
- 2025-08-06 `831eeb24` 重构 ElectraSamples/ElectraUtils 和解码器输出
- 2025-06-10 `2d174355` 移除平台资源委托和包装插件
- 2025-03-25 `23436173` 初始创建，修复 VP9 在 WebM/MKV 容器中的 HDR 元数据传递，添加 VP9 Alpha 通道支持

### 维护评价

- **创建时间**：2025-03-25（约 6 个月）
- **近期更新**：最近一个月内（2025-09-24）仍有直接代码提交，修复一致性和错误报告。
- **活跃度**：开发团队持续维护 Electra 系列媒体解码器，VPxDecoder 作为其重要组成部分保持同步更新。
- **已知问题**：仅支持桌面平台（Win64/Mac/Linux），不支持移动端或 Console。依赖 `DirectX`（Windows）可能导致在纯 D3D11 项目中的额外编译配置。
- **推荐度**：强烈推荐用于需要在桌面平台可靠播放 VP8/VP9 内容的项目。插件轻量、无内容资产，启用简单。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/VPxDecoderElectra)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/electra-media-player-in-unreal-engine/)（Electra 媒体播放器）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraFCPlugin/Tests)（Electra 通用测试，VPx 解码器集成测试包含在内）