# Android Media Player

> Implements a media player using the Android Media library.

| 属性 | 值 |
|---|---|
| 中文名 | Android 媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AndroidMedia` (RuntimeNoCommandlet), `AndroidMediaEditor` (Editor), `AndroidMediaFactory` (Editor), `AndroidMediaFactory` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2025-03-28 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AndroidMedia) | |

## 用途

该插件为 Unreal Engine 提供 Android 平台上的原生媒体播放能力。它封装了 Android 系统自带的 `MediaPlayer` API（包括 Camera2 API 和 MediaPlayer2 API），使得在 Android 设备上播放本地文件、网络流媒体以及设备摄像头实时画面成为可能。

- 解决 Android 平台无原生媒体播放的问题（替代 Windows/OSX 上的 WMF/AVF 等播放器）。
- 支持硬件加速解码，提供高性能视频渲染。
- 提供工厂模式和编辑器工具，方便在内容浏览器中导入媒体源。

## 使用场景

- 在 Android 游戏中播放过场动画、背景视频、UI 视频。
- 开发需要实时摄像头画面输入的应用（如 AR/VR 或自定义相机预览）。
- 在编辑器中为 Android 平台预览媒体文件（借助 `AndroidMediaEditor` 模块的 `UAndroidFileMediaSourceFactory` 工厂）。

## 蓝图用法

该插件主要暴露运行时媒体播放器相关的 UObject 类。以下节点需在 Android 平台或其他支持该插件的构建配置下生效。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 打开一个媒体源（文件、URL 或摄像头） | `UMediaPlayer` |
| `Play` | 开始播放 | `UMediaPlayer` |
| `Pause` | 暂停播放 | `UMediaPlayer` |
| `Close` | 关闭当前媒体 | `UMediaPlayer` |
| `Get Texture` | 获取当前帧渲染到的纹理（可用于材质） | `UMediaTexture` |

### 使用示例（蓝图描述）

1. **播放本地视频文件**：
   - 在内容浏览器中右键 → “Media” → “File Media Source”，选择一个 `.mp4` 文件。
   - 拖入关卡蓝图，连接 `UMediaPlayer` 的 `Open Source` 节点到该媒体源资产。
   - 调用 `Play` 节点。
   - 创建 `UMediaTexture` 资源并赋值给材质，将材质应用到任意 Actor（如平面）即可显示视频。

2. **播放网络流**：
   - 使用 `Create Media Source` 节点（需 `Platform Media Source` 或 `Stream Media Source`），设置 URL（如 `rtsp://...` 或 `http://...`）。
   - 其余步骤同本地文件。

> 注意：部分节点仅在 Android 运行时可用，在编辑器中模拟可能无效。

## C++ 用法

### 头文件引入

```cpp
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "FileMediaSource.h"
```

### 基本用法

```cpp
// 创建媒体播放器对象
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
UMediaTexture* MediaTexture = NewObject<UMediaTexture>();
MediaTexture->SetMediaPlayer(MediaPlayer);

// 创建文件媒体源
UFileMediaSource* FileSource = NewObject<UFileMediaSource>();
FileSource->FilePath = TEXT("/Game/Videos/MyVideo.mp4"); // 实际路径需转换为绝对路径

// 打开源并播放
if (MediaPlayer->OpenSource(FileSource))
{
    MediaPlayer->Play();
}
```

### 进阶用法

在 Android 平台切换摄像头源：

```cpp
// 创建设备摄像头媒体源（需要对应插件支持）
UPlatformMediaSource* CameraSource = NewObject<UPlatformMediaSource>();
CameraSource->SetDesiredPlayerName(TEXT("AndroidMediaPlayer"));

// 打开并显示摄像头画面
MediaPlayer->OpenSource(CameraSource);
MediaPlayer->Play();
```

该插件内部使用 Android 的 `Camera2 API`（自 2025-06-18 更新后），支持前后摄像头切换，需在运行时通过 Java 层调用。

## Demo 示例

以下是一个最小 C++ 示例，创建 Actor 并播放本地视频到材质上。

**MyVideoActor.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "MyVideoActor.generated.h"

UCLASS()
class AMyVideoActor : public AActor
{
    GENERATED_BODY()

public:
    UPROPERTY(VisibleAnywhere)
    class UMediaPlayer* MediaPlayer;

    UPROPERTY(VisibleAnywhere)
    class UMediaTexture* MediaTexture;

    UFUNCTION(BlueprintCallable, CallInEditor)
    void PlayVideo(const FString& FilePath);

    UFUNCTION(BlueprintCallable, CallInEditor)
    void StopVideo();

    virtual void BeginPlay() override;
};
```

**MyVideoActor.cpp**

```cpp
#include "MyVideoActor.h"
#include "FileMediaSource.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Components/StaticMeshComponent.h"

AMyVideoActor::AMyVideoActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建组件
    UStaticMeshComponent* Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Screen"));
    RootComponent = Mesh;

    // 创建媒体播放器和纹理
    MediaPlayer = CreateDefaultSubobject<UMediaPlayer>(TEXT("MediaPlayer"));
    MediaTexture = CreateDefaultSubobject<UMediaTexture>(TEXT("MediaTexture"));
    MediaTexture->SetMediaPlayer(MediaPlayer);
}

void AMyVideoActor::BeginPlay()
{
    Super::BeginPlay();

    // 在编辑器中预览时可能不会自动播放，此处为运行时示例
    if (MediaPlayer && !MediaPlayer->IsPlaying())
    {
        // 假设已设置文件路径
    }
}

void AMyVideoActor::PlayVideo(const FString& FilePath)
{
    if (!MediaPlayer) return;

    UFileMediaSource* FileSource = NewObject<UFileMediaSource>();
    FileSource->FilePath = FilePath;

    if (MediaPlayer->OpenSource(FileSource))
    {
        MediaPlayer->Play();
    }
}

void AMyVideoActor::StopVideo()
{
    if (MediaPlayer)
    {
        MediaPlayer->Close();
    }
}
```

> 需要将材质蓝图中的纹理参数设置为 `MediaTexture` 才能显示视频。

## 模块依赖

> 以下模块为 AndroidMedia 插件特有的依赖（已省略通用依赖如 Core, Engine, Slate 等）。

| 模块 | 用途 |
|---|---|
| `MediaUtils` | 提供媒体播放器框架的公用工具类。 |
| `MediaAssets` | 定义媒体源、媒体播放器、媒体纹理等资产类型。 |
| `AndroidMedia` | 本插件的运行时核心模块，必须依赖它才能使用播放器。 |
| `AndroidRuntimeSettings`（仅在编辑器）| 读取 Android 平台设置，如摄像头权限等。 |

## 维护状态

### 近期更新

- 2025-08-29 `32884de4` — 使用 RHICmdList.CreateTexture 替代旧的 RHICreateTexture 调用（渲染代码现代化）。
- 2025-06-18 `79ad0f74` — 更新摄像头播放器从 CameraPlayer14 到 Camera2 API（功能和性能提升）。
- 2025-05-31 `52e3dac1` — 使用 UnrealCodeFixup 更新头文件 DLL 存储声明。
- 2025-04-10 `ea97db60` — Movie Render Queue：高分辨率 tiling 支持分页场景视图状态持久数据。
- 2025-03-28 `b892a182` — 为 MediaPlayer14 新增 BitmapRenderer。

### 维护评价

- **创建时间**：2025-03-28（约 5 个月）。
- **更新频率**：近期有多次功能性（摄像头 API 更新）和代码质量（渲染现代化、编译修复）更新，显示团队在积极维护。
- **活跃度**：高。最近的两次提交（2025-08 和 2025-06）均包含实质改动。
- **已知问题**：未记录在提供信息中，但由于是较新插件且持续更新，通常功能稳定。
- **推荐使用**：✅ 强烈推荐，适用于所有 Android 平台需媒体播放功能的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AndroidMedia)
- [官方文档（UE 论坛）](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AndroidMedia/Source)（部分源码即包含测试逻辑）