# WebM Video Player

> WebM video playback for Unreal Engine.

| 属性 | 值 |
|---|---|
| 中文名 | WebM 视频播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `WebMMedia` (RuntimeNoCommandlet), `WebMMediaEditor` (Runtime), `WebMMediaFactory` (Runtime), `libwebm` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/WebMMedia) | |

## 用途

WebM Video Player 是一个实验性插件，为 Unreal Engine 5 提供 WebM 容器格式的视频播放能力。它通过集成开源 libwebm 库和 VP8/VP9 解码支持，使开发者能在游戏或应用中播放 WebM 视频（`.webm` 文件）。该插件作为 UE 媒体框架（Media Framework）的播放器后端，注册为 `IMediaPlayer` 实现，使用标准的 `UMediaPlayer` 和 `UMediaSource` 接口进行控制。

**为什么存在？**  
WebM 是一种开放、免版税的媒体容器格式，常用于网络视频。Epic 提供此插件以满足需要高性能、免授权费视频播放的场景（如过场动画、UI 背景、广告播放），尤其是跨平台原生支持（依赖第三方库）。

## 使用场景

- 你需要在游戏中播放 `.webm` 格式的过场动画或背景视频。
- 项目需要免版税的视频编解码方案（VP8/VP9 + Vorbis/Opus）。
- 你正在开发一个媒体播放器应用或工具，希望支持 WebM 格式。

## 蓝图用法

插件自身不暴露独立的蓝图节点，而是通过 UE 内置的媒体框架节点工作。启用 WebMMedia 后，`UMediaPlayer` 和 `UMediaSource` 相关节点即可用于播放 WebM 文件。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 打开指定的媒体源（如文件路径） | `UMediaPlayer` |
| `Play` | 开始播放已打开的媒体 | `UMediaPlayer` |
| `Pause` | 暂停播放 | `UMediaPlayer` |
| `Close` | 关闭当前媒体并释放资源 | `UMediaPlayer` |
| `On Media Opened` | 媒体打开成功时触发的委托 | `UMediaPlayer` |
| `On Media Closed` | 媒体关闭时触发的委托 | `UMediaPlayer` |
| `Get Duration` | 获取媒体总时长 | `UMediaPlayer` |
| `Get Time` / `Set Time` | 获取/设置当前播放位置 | `UMediaPlayer` |
| `Is Playing` / `Is Paused` | 检查播放状态 | `UMediaPlayer` |

### 使用示例（蓝图描述）

1. **创建媒体播放器**  
   在关卡蓝图中添加一个 `MediaPlayer` 变量（类型 `MediaPlayer`，实例化）。
2. **创建文件媒体源**  
   添加 `MediaSource` 变量（类型 `FileMediaSource`），设置其 `FilePath` 属性为项目内容中的 `.webm` 文件（如 `"/Game/Movies/MyVideo.webm"`）。
3. **打开并播放**  
   - 调用 `Open Source` 节点，连接媒体源和播放器。
   - 成功后，调用 `Play` 节点。
   - 将 `On Media Opened` 事件连接到 Play。

## C++ 用法

### 头文件引入

```cpp
#include "MediaPlayer.h"
#include "FileMediaSource.h"
```

### 基本用法

以下示例展示如何使用 WebM 插件播放一个本地视频。来源：`Engine/Plugins/Media/WebMMedia/Source/WebMMedia/Private/WebMMediaPlayer.cpp`（基于推测）。

```cpp
// 创建媒体播放器对象
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>(GetTransientPackage(), NAME_None, RF_Transient);
if (!MediaPlayer)
    return;

// 创建文件媒体源，指定 WebM 文件路径
UFileMediaSource* MediaSource = NewObject<UFileMediaSource>();
MediaSource->FilePath = TEXT("/Game/Movies/MyVideo.webm");

// 打开媒体源
MediaPlayer->OnMediaOpened.AddDynamic(this, &UMyClass::OnMediaOpened);
MediaPlayer->OnMediaOpenFailed.AddDynamic(this, &UMyClass::OnMediaOpenFailed);
MediaPlayer->OpenSource(MediaSource);

// 播放（通常在回调中触发）
void UMyClass::OnMediaOpened(FString OpenedUrl)
{
    MediaPlayer->Play();
}
```

### 进阶用法

从 git 历史中的更改看，插件在 `Close()` 时清理了所有轨道成员，因此当重置播放器或动态切换媒体时，务必调用 `Close()` 以确保正确释放资源：

```cpp
MediaPlayer->Close(); // 清理旧媒体资源，包括轨道列表
```

## Demo 示例

以下是一个最小可用的 Actor 组件，演示在运行时播放 WebM 视频。

**MyWebMPlayerComponent.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MediaPlayer.h"
#include "FileMediaSource.h"
#include "MyWebMPlayerComponent.generated.h"

UCLASS(ClassGroup=(Media), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyWebMPlayerComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyWebMPlayerComponent();

    UFUNCTION(BlueprintCallable, Category = "WebM")
    void PlayWebM(const FString& FilePath);

    UFUNCTION(BlueprintCallable, Category = "WebM")
    void Stop();

private:
    UPROPERTY()
    UMediaPlayer* MediaPlayer;

    UPROPERTY()
    UFileMediaSource* MediaSource;

    UFUNCTION()
    void OnMediaOpened(FString OpenedUrl);
};

```

**MyWebMPlayerComponent.cpp**

```cpp
#include "MyWebMPlayerComponent.h"

UMyWebMPlayerComponent::UMyWebMPlayerComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMyWebMPlayerComponent::PlayWebM(const FString& FilePath)
{
    if (!MediaPlayer)
    {
        MediaPlayer = NewObject<UMediaPlayer>(this);
        MediaPlayer->OnMediaOpened.AddDynamic(this, &UMyWebMPlayerComponent::OnMediaOpened);
    }

    if (!MediaSource)
    {
        MediaSource = NewObject<UFileMediaSource>();
    }

    MediaSource->FilePath = FilePath;
    MediaPlayer->OpenSource(MediaSource);
}

void UMyWebMPlayerComponent::Stop()
{
    if (MediaPlayer)
    {
        MediaPlayer->Close();
    }
}

void UMyWebMPlayerComponent::OnMediaOpened(FString OpenedUrl)
{
    if (MediaPlayer)
    {
        MediaPlayer->Play();
        UE_LOG(LogTemp, Log, TEXT("WebM video started: %s"), *OpenedUrl);
    }
}
```

**模块依赖：** 此示例还需依赖 `MediaAssets`（提供 `UMediaPlayer` 和 `UFileMediaSource`），在项目的 `.Build.cs` 中添加 `"MediaAssets"` 到 `PublicDependencyModuleNames`。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LibVpx` | VP8/VP9 视频解码支持 |
| `MediaAssets` | 提供 `UMediaPlayer` 和 `UMediaSource` 等媒体框架资产类 |
| `MediaUtils` | 媒体播放器抽象层，与播放器后端交互 |
| `WebMMedia` | 运行时模块，实现 `IMediaPlayer` 接口并注册 WebM 播放器 |
| `WebMMediaFactory` | 注册 WebM 媒体源工厂，使 `.webm` 文件关联到正确播放器 |

**注意**：`MediaAssets` 和 `MediaUtils` 是 UE 标准媒体框架模块，非本插件独有，但使用 WebM 播放功能时必须引用。

## 维护状态

### 近期更新

- 2025-09-12 `828f0392` WebMMedia: Clearing all members on Close() to remove any tracks that were added before detecting the 结尾
- 2025-08-29 `32884de4` Changing more uses of RHICreateTexture to RHICmdList.CreateTexture.
- 2025-07-10 `abb369e2` Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files.
- 2025-06-02 `3643a063` Remove old libwebm linux build files
- 2025-06-02 `8e5bc4b0` Updated linux build for libwebm

### 维护评价

- **创建时间**：2025-06-02（约 4 个月）
- **最近更新**：2025-09-12，有功能修复和清理
- **活跃性**：更新频率较高，涉及代码清理和平台构建修复，表明插件处于积极维护阶段
- **已知限制**：实验性（`IsBetaVersion=true`），默认禁用，需要手动启用。可能缺少某些格式的支持或存在性能问题
- **推荐度**：对于需要 WebM 播放的项目，可以尝试使用，但建议在正式发布前进行充分测试，并关注后续更新

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/WebMMedia)
- [官方文档（Media Framework）](https://docs.unrealengine.com/5.7/zh-CN/media-framework-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/WebMMedia/Source/WebMMedia/Private)（通常无独立测试目录，测试在插件源码中）