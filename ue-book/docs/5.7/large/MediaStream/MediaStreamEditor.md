# Media Stream

> Content/type agnostic chainable media proxy with media player integration.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体流代理 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置资源） |
| 模块 | `MediaStream` (Runtime), `MediaStreamEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-21 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MediaStream) | |

## 用途

Media Stream 提供了一个**内容类型无关的、可链式代理的媒体流系统**，并与现有的 Media Player（媒体播放器）框架深度集成。它允许开发者通过链式代理（Chainable Proxy）的方式组合、转换和路由媒体流，而不需要关心底层媒体源的具体格式或协议。

**存在的理由**：Unreal Engine 原生的 Media Framework 直接关联媒体源与 Media Player，缺乏灵活的中间层。当你需要：

- 对同一个媒体源应用多个不同的后处理（如裁剪、缩放、叠加）
- 将多个媒体源合并成一个输出
- 动态切换媒体源而不重新创建 Player

时，Media Stream 的代理模型可以优雅地解决这些问题。它通过 `UMediaStream` 对象作为核心，管理源（Source）、处理管线（Scheme）和目标输出（MediaTexture），并支持在编辑器中直接预览和调试。

## 使用场景

- **多路视频拼接**：在虚拟演播室中，将多个摄像头画面通过 Media Stream 拼接成一个完整的全景视频。
- **动态广告牌**：在游戏世界中的屏幕（MediaTexture）上，根据游戏逻辑动态切换不同的视频流（如直播、预录、实时渲染），无需断开连接。
- **媒体处理链**：对输入视频进行色彩校正、裁剪、字幕叠加等操作，通过链式 Scheme 组合实现。
- **与 Sequencer 集成**：在关卡序列中控制媒体流的播放、暂停、跳转，实现时间线上的多轨媒体编辑。

## 蓝图用法

> **注意**：最近的提交（2025-08-19）移除了蓝图可调用节点。当前版本（基于提供的源码）中 `UMediaStream` 不直接公开 BlueprintCallable 函数。媒体流的控制（打开、播放、暂停等）主要通过编辑器 UI 或 C++ 实现。如果你是纯蓝图用户，建议使用原生的 Media Player 框架，或等待后续版本恢复蓝图支持。

### 可能的蓝图操作（通过原生 Media Player 兼容）

由于 Media Stream 与 `UMediaPlayer` 和 `UMediaTexture` 深度集成，你可以通过它们原有的蓝图节点间接控制：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 打开媒体源（需通过 MediaStream 提供的 Source）| `UMediaPlayer` |
| `Play` | 开始播放 | `UMediaPlayer` |
| `Pause` | 暂停播放 | `UMediaPlayer` |
| `Seek` | 跳转到指定时间 | `UMediaPlayer` |

但是，对于 Media Stream 特有的源选择和链式处理，暂无原生蓝图节点。如果需要在蓝图中使用，必须通过 C++ 扩展或使用 Function Library。

## C++ 用法

### 头文件引入

```cpp
#include "MediaStream.h"
#include "MediaStreamEditorModule.h" // 编辑器模块
```

### 基本用法：创建并配置 UMediaStream

```cpp
// 创建 Media Stream 对象（通常在 Actor 组件或游戏实例中）
UMediaStream* MediaStream = NewObject<UMediaStream>(this);

// 设置源（URL 或本地文件）
MediaStream->SetSource("file:///C:/videos/demo.mp4");

// 获取关联的 Media Player
UMediaPlayer* Player = MediaStream->GetPlayer();

// 将 Player 输出到 Media Texture
UMediaTexture* Texture = MediaStream->GetTexture();

// 将 MediaTexture 应用到材质
UMaterialInstanceDynamic* Material = ...;
Material->SetTextureParameterValue("VideoTex", Texture);

// 打开并播放
Player->OpenSource(MediaStream->GetSource());
Player->Play();
```

*来源: 基于 `UMediaStream` 公共接口（头文件未完全提供，但根据架构推断）*

### 进阶用法：自定义 Scheme 处理器

Media Stream 支持注册自定义的 Scheme（协议）处理器。Scheme 用于解析和预处理媒体源。

```cpp
// 继承 IMediaStreamSchemeHandler
class FMySchemeHandler : public IMediaStreamSchemeHandler
{
public:
    virtual bool CanHandle(const FString& InUrl) const override
    {
        return InUrl.StartsWith("myprotocol://");
    }
    
    virtual bool Open(IMediaStreamSource* InSource) override
    {
        // 自定义打开逻辑
        return true;
    }
    
    virtual FCustomWidgets GetCustomWidgets(UMediaStream* InStream) override
    {
        // 返回编辑器自定义 UI（可选）
        return {};
    }
};

// 在模块启动时注册
void FMyModule::StartupModule()
{
    IMediaStreamModule::Get().RegisterSchemeHandler(MakeShared<FMySchemeHandler>());
}
```

*来源: 基于 `IMediaStreamSchemeHandler` 接口和 `FMediaStreamSourceCustomization` 头文件*

### 编辑器 UI 自定义

`MediaStreamEditor` 模块提供了一系列 Slate Widget 用于在细节面板中控制 Media Stream：

```cpp
// 在自定义细节面板中添加媒体控制
void FMyCustomization::CustomizeDetails(IDetailLayoutBuilder& DetailBuilder)
{
    // 获取选中的 Media Stream 对象
    TArray<TWeakObjectPtr<UMediaStream>> Streams;
    DetailBuilder.GetObjectsBeingCustomized(Streams);
    
    // 添加控制按钮（播放、暂停等）
    SMediaStreamPlaybackControls::FArguments Args;
    TSharedRef<SWidget> Controls = UE::MediaStreamEditor::FMediaStreamWidgets::CreateControlsWidget(Streams);
    DetailBuilder.EditCategory("Media Control").AddCustomRow(FText::GetEmpty())
        .WholeRowContent()
        [
            Controls
        ];
}
```

*来源: `SMediaStreamPlaybackControls.h`, `FMediaStreamWidgets.h`*

## Demo 示例

以下是一个最小 C++ 示例，在 Actor 中创建一个 Media Stream 并播放本地视频。

**MyVideoActor.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaStream.h"
#include "MyVideoActor.generated.h"

UCLASS()
class AMyVideoActor : public AActor
{
    GENERATED_BODY()
    
public:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Media")
    UMediaStream* MediaStream;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Media")
    UMediaTexture* MediaTexture;

    AMyVideoActor();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
};
```

**MyVideoActor.cpp**

```cpp
#include "MyVideoActor.h"
#include "MediaPlayer.h"
#include "MediaSource.h"

AMyVideoActor::AMyVideoActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建 Media Stream
    MediaStream = CreateDefaultSubobject<UMediaStream>(TEXT("MediaStream"));
    
    // 创建 Media Texture（默认会自动创建，这里显式获取）
    MediaTexture = MediaStream->GetTexture();
}

void AMyVideoActor::BeginPlay()
{
    Super::BeginPlay();

    // 设置本地文件源
    MediaStream->SetSource("file:///Game/Movies/MyVideo.mp4");

    // 获取 Player 并打开
    UMediaPlayer* Player = MediaStream->GetPlayer();
    if (Player)
    {
        Player->PlayOnOpen = true;
        Player->OpenSource(MediaStream->GetSource());
    }
}

void AMyVideoActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 关闭播放
    if (IsValid(MediaStream) && IsValid(MediaStream->GetPlayer()))
    {
        MediaStream->GetPlayer()->Close();
    }

    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Media` | 核心媒体框架，提供 `UMediaPlayer`、`UMediaSource` 等基础 |
| `MediaAssets` | 提供 `UMediaTexture`、`UMediaComponent` 等资产 |
| `MediaUtils` | 媒体工具函数 |
| `LevelSequenceEditor` | 与 Sequencer 集成的编辑器功能 |
| `MediaCompositing` | 媒体合成（用于 Sequencer 轨道） |
| `MediaPlayerEditor` | 媒体播放器编辑器支持 |

**无特殊依赖（仅标准 Core/Engine/Slate 等）**：Core、CoreUObject、Engine、Slate、SlateCore 等未列出，因为它们已被普遍依赖。

## 维护状态

### 近期更新

- 2025-08-19 `e555c6cb` Media Stream: Removed Blueprint nodes.
- 2025-07-10 `9803c443` Added UE_INLINE_GENERATED_CPP_BY_NAME to source files.
- 2025-07-01 `7ef6bcad` Media Stream: Fixed for packaged games.
- 2025-05-28 `4ab4a67c` Media Stream: Fixed relevancy issue for Sequencer.
- 2025-05-21 `fe3f901d` Media Stream: Fixed sequencer binding issues.

### 维护评价

- **创建时间**：2025-05-21（距今约5个月）
- **最近更新**：2025-08-19，约2个月前
- **活跃度**：在创建后的3个月内频繁更新（修复打包、Sequencer集成等），表明正处于积极开发中。最后一次更新移除了蓝图节点，可能是一次架构调整。
- **已知问题**：暂无官方公告的已知问题，但作为 Experimental 插件，API 可能不稳定，后续变更不排除破坏性修改。
- **推荐使用**：如果你需要灵活的媒体代理链并与 Sequencer 深度集成，可以尝试。注意该插件当前 **无蓝图支持**（节点已被移除），主要面向 C++ 开发者。由于是实验性，不建议在正式发行产品中直接依赖，除非你愿意承担 API 变动的风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MediaStream)
- [官方文档](https://docs.unrealengine.com/5.3/zh-CN/working-with-media/)（Media Framework 通用文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MediaStream/Tests)（假设存在）