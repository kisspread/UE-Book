# NDI Media

> Implements media source and media output using NDI protocol

| 属性 | 值 |
|---|---|
| 中文名 | NDI 媒体 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（NDI SDK 库文件） |
| 模块 | `NDIMedia` (Runtime), `NDIMediaEditor` (Editor), `NDIMediaRendering` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-14 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/NDIMedia) | |

## 用途

NDIMedia 插件为 UE5 提供了基于 [NDI（Network Device Interface）](https://ndi.video/) 协议的媒体输入输出能力。NDI 是一种广泛应用于虚拟制作（Virtual Production）和直播领域的 IP 视频传输标准，允许在局域网内以低延迟传输高质量视频流。

该插件的核心功能包括：

- **NDI 媒体源（Media Source）**：从网络接收 NDI 视频流，作为媒体播放器的输入源
- **NDI 媒体输出（Media Output）**：将 UE5 的画面通过 NDI 协议推送到网络，供其他 NDI 兼容软件（如 vMix、OBS、TouchDesigner）接收
- **GPU 着色器转换**：内置 UYVA、P216、PA16 等 NDI 专用 YUV 格式的 GPU 着色器，高效转换为 BGR 格式进行渲染

插件默认不启用且标记为实验性，说明 Epic 仍在迭代中，API 可能发生变化。

## 使用场景

- 你在做虚拟制作（Virtual Production），需要将 UE5 实时画面推送到广播切换台（如 vMix、ATEM）→ 用 NDI Media Output
- 你需要从外部 NDI 摄像机或软件接收视频画面作为 UE5 中的 Media Texture → 用 NDI Media Source
- 你在做实时合成（Compositing），需要在 UE5 和其他视频处理软件之间双向传输视频 → 同时使用 NDI Media Source 和 Output
- 你需要通过局域网传输带 Alpha 通道的视频流 → 支持 UYVA/PA16 格式的 Alpha 传输

## 蓝图用法

NDI Media 通过 UE 的 Media Framework 体系工作，主要通过 Media Player、Media Source 和 Media Output 资产使用，而非直接暴露大量蓝图函数。

### 核心资产类型

| 资产类型 | 说明 | 所在模块 |
|---|---|---|
| `UNDIMediaSource` | NDI 视频源，配置 NDI 发送端的网络地址 | `NDIMedia` |
| `UNDIMediaOutput` | NDI 视频输出，将 UE 画面推送到 NDI 网络 | `NDIMedia` |
| `UNDIMediaTextureReceiver` | NDI 接收器纹理，显示接收到的 NDI 视频 | `NDIMedia` |

### 使用示例（蓝图描述）

**接收 NDI 视频流：**
1. 创建 `MediaPlayer` 资产
2. 创建 `UNDIMediaSource` 资产，填入目标 NDI 源名称
3. 在蓝图中调用 `MediaPlayer → Open Source`，连接 NDI Media Source
4. 创建 `MediaTexture`，绑定到 MediaPlayer，即可在材质中使用

**发送 UE 画面为 NDI 流：**
1. 创建 `UNDIMediaOutput` 资产，配置发送名称和格式
2. 创建 `MediaCapture` 资产
3. 在蓝图中调用 `MediaCapture → Capture Scene`，绑定 NDI Media Output
4. 其他 NDI 客户端即可发现并接收该画面

## C++ 用法

### 头文件引入

```cpp
// NDI 媒体核心模块
#include "NDIMediaModule.h"

// NDI 渲染着色器（用于自定义渲染管线）
#include "Internal/NDIMediaShaders.h"
```

### 基本用法 — 配置 NDI 媒体输出

```cpp
// 创建 NDI Media Output 并开始捕获
// 参考自 UE MediaIOFramework 标准用法

UNDIMediaOutput* NDIOutput = NewObject<UNDIMediaOutput>();
NDIOutput->SetNDIName(TEXT("UE5_Output"));

UMediaCapture* MediaCapture = NewObject<UMediaCapture>();
MediaCapture->CaptureSceneViewport(NDIOutput);
```

### 进阶用法 — 使用 NDI 着色器进行自定义 GPU 转换

```cpp
// 使用内置着色器将 NDI UYVA 纹理转换为 BGR
// 来源: Internal/NDIMediaShaders.h

FRHITexture* YUVTexture = ...;  // YUV 平面纹理
FRHITexture* AlphaTexture = ...; // Alpha 纹理
FIntPoint OutputSize(1920, 1080);
FMatrix44f ColorTransform = FMatrix44f::Identity;
FMatrix44f CSTransform = FMatrix44f::Identity;

FNDIMediaShaderUYVAtoBGRAPS::FParameters ShaderParams(
    YUVTexture,
    AlphaTexture,
    OutputSize,
    ColorTransform,
    UE::Color::EEncoding::sRGB,
    CSTransform,
    MediaShaders::EToneMapMethod::None
);

// 在渲染线程中绑定着色器参数
FRHIBatchedShaderParameters BatchedParameters = ...;
FNDIMediaShaderUYVAtoBGRAPS::SetParameters(BatchedParameters, ShaderParams);
```

## Demo 示例

### NDI 接收器组件

```cpp
// NDIReceiverComponent.h
#pragma once

#include "Components/ActorComponent.h"
#include "NDIReceiverComponent.generated.h"

class UMediaPlayer;
class UMediaTexture;
class UNDIMediaSource;

UCLASS(ClassGroup=(NDI), meta=(BlueprintSpawnableComponent))
class UNDIReceiverComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UNDIReceiverComponent();

    /** 开始接收指定 NDI 源 */
    UFUNCTION(BlueprintCallable, Category = "NDI")
    void ConnectToNDISource(const FString& NDISourceName);

    /** 断开连接 */
    UFUNCTION(BlueprintCallable, Category = "NDI")
    void Disconnect();

    /** 获取接收的视频纹理 */
    UFUNCTION(BlueprintPure, Category = "NDI")
    UMediaTexture* GetVideoTexture() const { return VideoTexture; }

private:
    UPROPERTY()
    TObjectPtr<UMediaPlayer> MediaPlayer;

    UPROPERTY()
    TObjectPtr<UMediaTexture> VideoTexture;

    UPROPERTY()
    TObjectPtr<UNDIMediaSource> NDIMediaSource;
};
```

```cpp
// NDIReceiverComponent.cpp
#include "NDIReceiverComponent.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "NDIMediaSource.h"  // 需要确认实际头文件路径

UNDIReceiverComponent::UNDIReceiverComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
    MediaPlayer = CreateDefaultSubobject<UMediaPlayer>(TEXT("MediaPlayer"));
    VideoTexture = CreateDefaultSubobject<UMediaTexture>(TEXT("VideoTexture"));
    VideoTexture->SetMediaPlayer(MediaPlayer);
}

void UNDIReceiverComponent::ConnectToNDISource(const FString& NDISourceName)
{
    if (!NDIMediaSource)
    {
        NDIMediaSource = NewObject<UNDIMediaSource>(this);
    }
    // 设置 NDI 源名称（具体 API 参考实际头文件）
    MediaPlayer->OpenSource(NDIMediaSource);
}

void UNDIReceiverComponent::Disconnect()
{
    if (MediaPlayer)
    {
        MediaPlayer->Close();
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MediaIOFramework` | 提供 Media Source / Media Output 基类和 Media Capture 框架 |
| `MediaPlayerEditor` | 编辑器中的媒体播放器资产编辑支持 |

## 模块结构

| 模块 | 类型 | 职责 |
|---|---|---|
| `NDIMedia` | Runtime | NDI 核心功能：Media Source、Media Output、接收器实现 |
| `NDIMediaEditor` | Editor | 编辑器集成：资产工厂、属性自定义面板 |
| `NDIMediaRendering` | Runtime | GPU 着色器：UYVA/P216/PA16 到 BGR 的格式转换 |
| `NDISDK` | External | 第三方 NDI SDK 5.6.1 库文件封装 |

### NDIMediaRendering 着色器说明

该模块包含三个全局着色器，用于将 NDI 专用视频格式转换为可渲染的 BGR 格式：

| 着色器类 | 输入格式 | 说明 |
|---|---|---|
| `FNDIMediaShaderUYVAtoBGRAPS` | UYVA（8-bit 4:2:2 + Alpha） | 带 Alpha 通道的 8 位 YUV 转 BGR |
| `FNDIMediaShaderP216toBGRAPS` | P216（16-bit 4:2:2 双平面 Y+UV） | 16 位高精度 YUV 转 BGR |
| `FNDIMediaShaderPA16toBGRAPS` | PA16（16-bit 4:2:2 三平面 Y+UV+A） | 16 位高精度带 Alpha 的 YUV 转 BGR |

所有着色器均需要 ES3_1 以上特性等级支持。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `96b8b04b` | Media IO: Fix to recent CL 54396736 for ImgMedia and NDI players emitting incorrect SourceOpened ana | 修复 NDI 播放器发送错误的 SourceOpened 分析事件 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 为媒体播放器和捕获添加引擎分析信息 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 调整虚拟制作资产分类 |
| 2026-05-12 | `c657503b` | [Media] Add missing UAssetDefinition entries for concrete UMediaSource and UMediaOutput subclasses t | 为 MediaSource/MediaOutput 子类添加缺失的资产定义 |
| 2026-04-23 | `efcad028` | HDR: Fix HDR normalization factor across media causing incorrect brightness levels going from/to the | 修复 HDR 媒体归一化因子导致的亮度异常 |

### 维护评价

- **活跃维护中**：最近几个月有持续的功能更新和 Bug 修复
- **实验性状态**：`IsExperimentalVersion=true` 且 `EnabledByDefault=false`，API 可能变化
- **Epic 官方维护**：由 Epic Games 开发，纳入了虚拟制作管线的迭代
- **HDR 支持**：最近修复了 HDR 相关问题，说明在向高质量渲染场景推进
- **建议**：可用于虚拟制作项目的原型验证和内部测试，生产环境使用需注意 API 稳定性风险

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/NDIMedia)
- [NDI 官方文档](https://ndi.video/sdk/)
- [UE Media Framework 文档](https://docs.unrealengine.com/en-US/InteractiveExperiences/MediaFramework/)