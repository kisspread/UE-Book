# Bink Media

> Implements a media player using Bink.

| 属性 | 值 |
|---|---|
| 中文名 | Bink 媒体 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BinkMediaPlayer` (Runtime), `BinkMediaPlayerEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-07-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/BinkMedia) | |

## 用途

Bink Media 插件将 RAD Game Tools 的 Bink 视频编解码器集成到 Unreal Engine 中，提供高性能的视频播放方案。Bink 以其极小的文件体积和飞快的解码速度著称，尤其适合游戏中的全动态视频（FMV）、过场动画、加载画面以及 UI 背景视频。该插件不仅支持普通视频播放，还提供了对多声道音频（5.1/7.1 环绕声）、多语言音轨以及 HDR 输出的完整支持，并能在加载屏幕（Movie Player）中直接播放视频。

## 使用场景

- **游戏过场动画**：使用 Bink 编码的 .bik 文件，在保持画质的同时大幅减小包体，并顺畅播放。
- **加载画面视频**：利用 `FBinkMovieStreamer` 在游戏加载时播放全屏视频，避免黑屏等待。
- **UI 背景/过场纹理**：将 `UBinkMediaTexture` 指定给材质，嵌入 UI 或场景物体上播放视频。
- **多语言发行**：借助 Bink 的内置音轨管理，为不同语言版本提供独立音轨。
- **HDR 视频播放**：支持 HDR 输出，配合 `Tonemap` 和 `OutputNits` 参数，适合高端显示设备。

## 蓝图用法

以下节点可直接在蓝图图表中使用，主要涉及媒体纹理控制和加载画面信息查询。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Media Player` | 将指定的 `UBinkMediaPlayer` 绑定到当前 `UBinkMediaTexture`，使纹理开始渲染视频 | `UBinkMediaTexture` |
| `Clear` | 将纹理清除为透明黑色 | `UBinkMediaTexture` |
| `Bink Draw Overlays` | 启用/覆盖 Bink 的屏幕覆盖绘制（如调试信息）| `UBinkFunctionLibrary` |
| `Bink Loading Movie Get Duration` | 返回当前加载视频的总时长（`FTimespan`）| `UBinkFunctionLibrary` |
| `Bink Loading Movie Get Time` | 返回当前加载视频的播放进度时间 | `UBinkFunctionLibrary` |

### 使用示例

1. **播放加载画面视频**  
   在项目设置 → 电影播放器中，将 `BinkMovieStreamer` 设为默认流式播放器，然后将 .bik 文件放入 `Content/Movies/` 目录，引擎会在加载时自动播放。

2. **在 UI 中播放视频**  
   - 创建 `BinkMediaPlayer` 资产，设置其 `MediaUrl` 为 .bik 文件路径。  
   - 创建 `BinkMediaTexture` 资产，将其 `MediaPlayer` 属性赋值为上一步创建的播放器。  
   - 在材质中使用该纹理，并在 UI 材质的 Base Color 引脚连接。  
   - 调用 `Set Media Player`（如果需要动态更换视频源）或通过播放器蓝图节点控制播放。

3. **查询加载视频进度**  
   在 `LoadingScreen` 蓝图中，使用 `Bink Loading Movie Get Duration` 和 `Bink Loading Movie Get Time` 节点驱动进度条或文本显示。

## C++ 用法

### 头文件引入

```cpp
#include "BinkMediaPlayer.h"
#include "BinkMediaTexture.h"
#include "BinkFunctionLibrary.h"
```

### 基本用法

**1. 创建媒体播放器并打开视频**  
插件提供了 `UBinkMediaPlayer` 作为核心播放器。以下示例在 Actor 中播放视频并映射到材质纹理：

```cpp
// MyActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "BinkMediaPlayer.h"
#include "BinkMediaTexture.h"
#include "MyActor.generated.h"

UCLASS()
class MYPROJECT_API AMyActor : public AActor
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Bink")
    UBinkMediaPlayer* MediaPlayer;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Bink")
    UBinkMediaTexture* MediaTexture;

    virtual void BeginPlay() override;
};
```

```cpp
// MyActor.cpp
#include "MyActor.h"

void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    if (MediaPlayer && MediaTexture)
    {
        // 将媒体纹理与播放器关联
        MediaTexture->MediaPlayer = MediaPlayer;

        // 打开视频文件（路径相对于 Content 目录，如 "Movies/MyVideo.bik"）
        MediaPlayer->OpenUrl(MediaPlayer->MediaUrl);

        // 开始播放
        MediaPlayer->Play();
    }
}
```

**2. 获取加载视频的信息**  
```cpp
FTimespan Duration = UBinkFunctionLibrary::BinkLoadingMovie_GetDuration();
FTimespan CurrentTime = UBinkFunctionLibrary::BinkLoadingMovie_GetTime();
```

**3. 自定义加载屏幕流式播放器**  
插件已内建 `FBinkMovieStreamer`，可在 `FMoviePlayer` 中使用。通常无需显式引用，引擎自动选择。

### 进阶用法

- **多音轨选择**：通过 `EBinkMediaPlayerBinkSoundTrack` 枚举指定音轨布局，在 `UBinkMediaPlayer` 的 `OpenUrl` 之后设置 `SoundTrack` 属性。  
- **HDR 渲染**：在 `UBinkMediaTexture` 上设置 `Tonemap = true` 和 `OutputNits`（如 2000 用于 HDR），并配合 HDR 显示端口。  
- **覆盖绘制模式**：使用 `UBinkMediaPlayer` 的 `BinkDrawStyle` 属性（`EBinkMediaPlayerBinkDrawStyle`）选择直接渲染到纹理或覆盖屏幕绘制，适合 UI 叠加场景。

## Demo 示例

以下是一个最小的完整示例，展示如何通过 C++ 播放 Bink 视频并将画面显示在场景中的一个静态网格体材质上。

### MyBinkActor.h
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "BinkMediaPlayer.h"
#include "BinkMediaTexture.h"
#include "Components/StaticMeshComponent.h"
#include "MyBinkActor.generated.h"

UCLASS()
class MYPROJECT_API AMyBinkActor : public AActor
{
    GENERATED_BODY()

public:
    AMyBinkActor();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Bink")
    UBinkMediaPlayer* MediaPlayer;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Bink")
    UBinkMediaTexture* MediaTexture;

    UPROPERTY(VisibleAnywhere, Category = "Bink")
    UStaticMeshComponent* DisplayMesh;

    virtual void BeginPlay() override;
};
```

### MyBinkActor.cpp
```cpp
#include "MyBinkActor.h"

AMyBinkActor::AMyBinkActor()
{
    PrimaryActorTick.bCanEverTick = false;

    DisplayMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("DisplayMesh"));
    RootComponent = DisplayMesh;
}

void AMyBinkActor::BeginPlay()
{
    Super::BeginPlay();

    if (!MediaPlayer) return;
    if (!MediaTexture) return;

    // 绑定纹理到播放器
    MediaTexture->MediaPlayer = MediaPlayer;

    // 创建一个动态材质实例，使用 MediaTexture
    if (DisplayMesh->GetMaterial(0))
    {
        UMaterialInstanceDynamic* DynMat = DisplayMesh->CreateDynamicMaterialInstance(0);
        if (DynMat)
        {
            DynMat->SetTextureParameterValue(TEXT("VideoTexture"), MediaTexture);
        }
    }

    // 打开并播放视频
    MediaPlayer->OpenUrl(MediaPlayer->MediaUrl);
    MediaPlayer->Play();
}
```

> **注意**：材质中需要有一个 `Texture2D` 参数命名为 `VideoTexture`，并将 `Sampler Type` 设为 `External`（或默认 Texture2D）。

## 模块依赖

使用 `BinkMediaPlayer` 模块时，你需要在你的 `Build.cs` 中添加：

| 模块 | 用途 |
|---|---|
| `BinkMediaPlayer` | 核心 Bink 播放器、纹理、函数库 |
| `MoviePlayer` | 加载屏幕视频流式播放器支持 |
| `RHI`、`RenderCore`、`Renderer` | 底层渲染资源与命令列表 |
| `Projects` | 项目路径查找（如内容目录） |
| `DesktopWidgets` (可选) | 编辑器/桌面平台的部件支持 |

如果使用编辑器工具（如媒体纹理属性编辑），还需依赖 `BinkMediaPlayerEditor`。

**省略常见依赖**：Core、CoreUObject、Engine、Slate、SlateCore、InputCore 等不列出。

## 维护状态

### 近期更新

- 2025-08-29 `32884de4` 修改更多 `RHICreateTexture` 调用为 `RHICmdList.CreateTexture`
- 2025-08-27 `7766f4c6` 修复电影流式播放器返回值，使其返回实际打开调用的结果
- 2025-08-08 `40e2c8da` 将 RHI 命令列表传递至 MoviePlayer 和 TickableObjectRenderThread 函数
- 2025-08-05 `dfd9e75a` Bink: 修复 CookOnTheFly 路径（长期存在的错误）
- 2025-07-27 `bd4ed858` 移除模块中对 `bAllowConfidentialPlatformDefines` 的需求

### 维护评价

- **年龄**：创建于 2025 年 7 月，当前不足一年，属于全新插件。  
- **活跃度**：近 3 个月内有多项功能性更新（RHI 传递、Bug 修复），表明正在积极维护。  
- **推荐使用**：适合需要高性能、低内存占用的视频播放场景。文档和 API 较完整，配合 Bink 编码器工具链可轻松制作游戏视频。  
- **已知限制**：不支持 tvOS 平台（已在 .uplugin 中设置 PlatformDenyList），服务器端不可用。

## 相关链接

- [源码（5.7 分支）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/BinkMedia)
- [Bink 官方工具与文档](https://www.radgametools.com/bink.htm)  
- [测试用例（插件内测试）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/BinkMedia/Source/BinkMediaPlayer/Private)