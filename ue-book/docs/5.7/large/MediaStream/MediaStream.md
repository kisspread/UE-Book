# Media Stream

> Content/type agnostic chainable media proxy with media player integration.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体流代理 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资源） |
| 模块 | `MediaStream` (Runtime), `MediaStreamEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-21 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MediaStream) | |

## 用途

标准 `UMediaPlayer` 只能绑定单个 `UMediaSource`，切换源需要手动销毁和重建播放器，且缺乏统一的来源引用方式。 `MediaStream` 插件提供了一个**抽象层**，使用 `FMediaStreamSource`（包含 `Scheme` 和 `Path`）来表示任意媒体源，通过注册的 Scheme Handler 自动创建响应的 `UMediaPlayer`，支持：

- **内容类型无关**：可通过统一 `Scheme` 引用资产、文件、注册流名、子对象等（`asset://`、`file://`、`managed://`、`subobject://`）。
- **链式代理**：`UMediaStreamProxyPlayer` 可将一个 MediaStream 的播放器和纹理转发给另一个 MediaStream，实现播放器链。
- **播放器自动管理**：在源改变时自动创建/更新/销毁 `UMediaPlayer`，并应用配置（循环、音量、缓存、轨道选择等）。
- **编辑器集成**：提供蓝图节点、Actor/Component、属性自定义（如文件选择器、资产选择器）。

本质上是 UE 媒体框架的一个**中间件**，简化了复杂媒体播放场景下的流程控制。

## 使用场景

- 你需要一个“媒体播放列表”组件，支持切换不同来源（文件、资产、网络流），同时保持相同纹理和配置 → 使用 `UMediaStream` + `UMediaStreamLocalPlayer`（内置 `UMediaPlaylist` 支持）。
- 你希望在关卡蓝图中动态设置媒体源，无需关心底层是 `UMediaSource` 还是 `UMediaPlayer` → 使用 `UMediaStreamSourceBlueprintLibrary` 函数创建源。
- 你有一个媒体播放器需要被多个 UI 或 Actor 共享，且各自可能有不同纹理配置 → 使用 `UMediaStreamProxyPlayer` 转发另一个 MediaStream 的播放器。
- 你需要在编辑器内通过可视化方式选择媒体文件或资产 → 利用 Scheme Handler 提供的属性自定义（文件选择器、资产选择器）。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Source` （`UMediaStream::SetSource`） | 设置新的媒体源，自动创建/更新播放器 | `UMediaStream` |
| `Ensure Player` （`UMediaStream::EnsurePlayer`） | 确保播放器存在（可选强制重建） | `UMediaStream` |
| `Get Player` （`UMediaStream::GetPlayer`） | 获取当前 `IMediaStreamPlayer` 接口 | `UMediaStream` |
| `Set Requested Seek Time` （`BP_SetRequestedSeekTime`） | 设置请求的跳转时间 | `UMediaStreamLocalPlayer` |
| `Set Requested Seek Frame` （`BP_SetRequestedSeekFrame`） | 设置请求的跳转帧 | `UMediaStreamLocalPlayer` |
| `Set Playback State` （`BP_SetPlaybackState`） | 设置播放/暂停状态 | `UMediaStreamLocalPlayer` |
| `Set Playlist Index` （`BP_SetPlaylistIndex`） | 为内置播放列表设置当前索引 | `UMediaStreamLocalPlayer` |
| `Make Media Source From Asset / File / Stream Name` | 根据不同类型创建 `FMediaStreamSource` | `UMediaStreamSourceBlueprintLibrary` |
| `Is Valid Media Source` | 检查源是否有效（Scheme 非 None 且 Path 非空） | `UMediaStreamSourceBlueprintLibrary` |
| `Can Handle Object` | 检查某类是否有注册的 Object Handler | `UMediaStreamObjectHandlerSubsystem` |
| `Create Media Player` | 手动通过 Object Handler 创建播放器 | `UMediaStreamObjectHandlerSubsystem` |

### 使用示例（蓝图描述）

**动态切换媒体源**  
调用 `Make Media Source From File`（节点上需指定 `MediaStream` 和文件路径），返回 `FMediaStreamSource`，将其连接到 `Set Source` 节点的 `In Source` 引脚。`Media Stream` 自身上设置一个 `UMediaStream` 变量（或使用 `MediaStreamComponent` 上的 `MediaStream` 引用）。执行 `Set Source` 后，会自动创建内部播放器并开始播放（如果 `bPlayOnOpen` 配置为 true）。

**播放控制**  
通过 `Get Player` 返回的 `Object` 引用的 `UMediaStreamLocalPlayer`，调用 `Set Playback State` 设置播放/暂停，或 `Set Requested Seek Time` 跳转到指定时间。

**代理播放**  
创建一个 `UMediaStreamProxyPlayer` 子对象，设置其 `ProxyStreamSoft` 指向另一个 `UMediaStream`，然后将其设为 `UMediaStream` 的 Player（通过 C++ 或 `UMediaStream::EnsurePlayer` 内部创建）。之后所有播放控制（播放、暂停、跳转）将转发到被代理的流。

## C++ 用法

### 头文件引入

```cpp
#include "MediaStream.h"
#include "MediaStreamSourceBlueprintLibrary.h"
#include "MediaStreamObjectHandlerSubsystem.h"
#include "MediaStreamPlayerConfig.h"
#include "MediaStreamTextureConfig.h"
```

### 基本用法

```cpp
// 创建一个 MediaStream 对象
UMediaStream* MediaStream = NewObject<UMediaStream>(GetTransientPackage());
MediaStream->AddToRoot();

// 从文件创建源
FMediaStreamSource Source = UMediaStreamSourceBlueprintLibrary::MakeMediaSourceFromFile(MediaStream, TEXT("D:/Videos/sample.mp4"));

// 设置源（自动创建播放器并应用配置）
bool bSuccess = MediaStream->SetSource(Source);
if (bSuccess)
{
    // 此时内部已创建 UMediaStreamLocalPlayer，自动开始播放
}

// 播放控制
TScriptInterface<IMediaStreamPlayer> Player = MediaStream->GetPlayer();
if (Player)
{
    Player->SetPlaybackState(EMediaStreamPlaybackState::Play);
    Player->SetRequestedSeekTime(10.0f);
}

// 清理
MediaStream->Close();
MediaStream->RemoveFromRoot();
```
*来源：从 `UMediaStream::SetSource`、`UMediaStreamSourceBlueprintLibrary` 头文件推断*

### 进阶用法

**自定义 Scheme Handler 注册**  
可注册自定义 URL scheme（如 `rtsp://`、`mms://`）来解析来源并创建播放器：

```cpp
// 自定义 Scheme Handler 示例（需要实现 IMediaStreamSchemeHandler）
class FMyRTSPHandler : public IMediaStreamSchemeHandler
{
public:
    static const FLazyName Scheme; // RTSP

    virtual FMediaStreamSource CreateSource(UObject* InOuter, const FString& InPath) override
    {
        FMediaStreamSource Source;
        Source.Scheme = Scheme;
        Source.Path = InPath;
        return Source;
    }

    virtual UMediaPlayer* CreateOrUpdatePlayer(const FMediaStreamSchemeHandlerCreatePlayerParams& InParams) override
    {
        // 根据 InParams.MediaStream 和 InParams.CurrentPlayer 创建/更新播放器
        // 例如使用第三方插件打开 RTSP 流
        return nullptr; // 实现省略
    }

#if WITH_EDITOR
    virtual void CreatePropertyCustomization(UMediaStream* InMediaStream, FCustomWidgets& InOutCustomWidgets) override
    {
        // 可选：添加自定义 UI 控件
    }
#endif
};

// 注册
FMediaStreamSchemeHandlerManager::Get().RegisterSchemeHandler<FMyRTSPHandler>("rtsp"_Lazy);
```
*来源：从 `IMediaStreamSchemeHandler`、`FMediaStreamSchemeHandlerManager` 接口推导*

**链式代理播放**  
创建两个 MediaStream，将一个作为另一个的代理：

```cpp
UMediaStream* SourceStream = NewObject<UMediaStream>(GetTransientPackage());
UMediaStream* ProxyStream = NewObject<UMediaStream>(GetTransientPackage());

// 设置源流播放文件
FMediaStreamSource FileSource = UMediaStreamSourceBlueprintLibrary::MakeMediaSourceFromFile(SourceStream, TEXT("D:/video.mp4"));
SourceStream->SetSource(FileSource);

// 为代理流创建一个 UMediaStreamProxyPlayer 子对象
UMediaStreamProxyPlayer* ProxyPlayer = NewObject<UMediaStreamProxyPlayer>(ProxyStream);
ProxyPlayer->SetProxyStreamSoft(SourceStream); // 指向源流
ProxyPlayer->SetReadOnly(true);                // 只读，不修改源配置

// 设置代理流使用该代理播放器
// 注意：UMediaStream 内部创建 Player 时会匹配子对象类型，需要确保 ProxyPlayer 被正确识别。
// 更直接的方式是通过 EnsurePlayer 并手动设置，但这里展示概念。
```
*来源：`UMediaStreamProxyPlayer` 头文件及 `IMediaStreamPlayer` 接口设计*

## Demo 示例

以下是一个完整的最小 C++ Actor，展示如何使用 `MediaStreamComponent` 播放媒体文件。

### .h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "MediaStreamActor.h"
#include "MediaStreamDemoActor.generated.h"

UCLASS()
class AMediaStreamDemoActor : public AMediaStreamActor
{
    GENERATED_BODY()

public:
    AMediaStreamDemoActor();

    UFUNCTION(BlueprintCallable, Category = "Demo")
    void PlayVideo(const FString& FilePath);

    UFUNCTION(BlueprintCallable, Category = "Demo")
    void StopVideo();
};
```

### .cpp

```cpp
#include "MediaStreamDemoActor.h"
#include "MediaStream.h"
#include "MediaStreamComponent.h"
#include "MediaStreamSourceBlueprintLibrary.h"

AMediaStreamDemoActor::AMediaStreamDemoActor()
{
    // 基类 AMediaStreamActor 已创建 MediaStreamComponent
}

void AMediaStreamDemoActor::PlayVideo(const FString& FilePath)
{
    if (!MediaStreamComponent || !MediaStreamComponent->MediaStream)
        return;

    UMediaStream* Stream = MediaStreamComponent->MediaStream;
    // 从文件创建源
    FMediaStreamSource Source = UMediaStreamSourceBlueprintLibrary::MakeMediaSourceFromFile(Stream, FilePath);
    if (UMediaStreamSourceBlueprintLibrary::IsValidMediaSource(Source))
    {
        Stream->SetSource(Source);
    }
}

void AMediaStreamDemoActor::StopVideo()
{
    if (MediaStreamComponent && MediaStreamComponent->MediaStream)
    {
        MediaStreamComponent->MediaStream->Close();
    }
}
```

将此 Actor 放置到关卡，调用 `PlayVideo` 并传入绝对路径即可播放。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MediaAssets` | 提供 `UMediaPlayer`、`UMediaTexture`、`UMediaPlaylist` 等核心媒体类型 |
| `MediaCompositing` | 提供序列器内的媒体合成支持（如 `UMediaPlane`） |
| `LevelSequenceEditor` | 编辑器依赖，用于序列器内媒体流相关绑定（仅 Editor 模块需要） |

> **注意**：`MediaCompositing` 和 `LevelSequenceEditor` 是 .uplugin 中声明的插件依赖，如果仅在 Runtime 模块中使用基本播放功能，可能不需要它们，但 .uplugin 默认启用了它们。Build.cs 中需确保这些模块在依赖链中。

## 维护状态

### 近期更新

- 2025-08-19 `e555c6cb` Media Stream: Removed Blueprint nodes.
- 2025-07-10 `9803c443` Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files.
- 2025-07-01 `7ef6bcad` Media Stream: Fixed for packaged games
- 2025-05-28 `4ab4a67c` Media Stream: Fixed relevancy issue for Sequencer.
- 2025-05-21 `fe3f901d` Media Stream: Fixed sequencer binding issues

### 维护评价

插件自 2025-05-21 创建后，持续收到功能修复和适配更新（如打包修复、序列器绑定修复），最近一次提交在 2025-08-19（移除蓝图节点，可能意味着重构）。整体处于**活跃维护**状态，推荐用于实验性或新项目。但尚未经过大规模社区使用验证，注意实验性标记，在生产环境中需谨慎评估。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MediaStream)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MediaStream/Tests)（推测路径，实际可能位于 Engine/Tests 下）