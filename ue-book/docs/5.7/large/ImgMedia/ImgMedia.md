# Image Sequence Media Player

> Implements a media player for image sequences in EXR and other formats.

| 属性 | 值 |
|---|---|
| 中文名 | 图像序列媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ExrReaderGpu` (Runtime), `ImgMedia` (Runtime), `ImgMediaEditor` (Runtime), `ImgMediaEngine` (Runtime), `ImgMediaFactory` (Runtime), `OpenExrWrapper` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-08-15 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ImgMedia) | |

## 用途

`Image Sequence Media Player` 插件提供了一种在虚幻引擎中播放图像序列（image sequence）的方式。它将磁盘上一系列静态图片（如 BMP、EXR、PNG、JPG）视为视频帧，支持逐帧读取、缓存和渲染。核心功能包括：

- 支持多种图像格式，但对 EXR 格式进行深度优化（CPU/GPU 读取、tile/mipmap 支持）。
- 高效的 tile-based 加载：只读取视口内可见的 tile，节省带宽和内存。
- 自动 mipmap 生成：根据相机距离自动选择合适的分辨率级别。
- 全局 LRU 缓存：多个播放器共享缓存帧，减少重复 IO。
- 代理（proxy）目录支持：在开发过程中使用低分辨率版本代替高分辨率源。
- 时间码和帧率覆盖：可手动指定序列帧率或设置起始时间码。

该插件解决了直接使用 `MediaPlayer` + `MediaSource` 播放图像序列的需求，特别适用于虚拟制片、实景拍摄后处理、逐帧动画等场景。

## 使用场景

- **虚拟制片**：将实拍的高分辨率 EXR 序列作为背景或动态纹理播放，并支持实时 mipmap 和 tile 加载以优化性能。
- **逐帧动画播放**：使用 PNG/JPG 序列作为 UI 动效或角色纹理，通过 `UImgMediaSource` 简单配置即可。
- **代理工作流**：在编辑器中用低分辨率代理快速迭代，打包时切换回全分辨率，提高开发效率。
- **离线序列预览**：配合 `MediaFramework` 在关卡中预览大型 EXR 序列，并支持暂停、倒放等控制。

## 蓝图用法

主要暴露给蓝图的类是 `UImgMediaSource`，继承自 `UBaseMediaSource`。以下为常用蓝图节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSequencePath` | 设置图像序列所在的目录路径（相对或绝对） | `UImgMediaSource` |
| `GetSequencePath` | 获取当前设置的序列路径 | `UImgMediaSource` |
| `GetProxies` | 获取序列目录下所有代理子目录的名称 | `UImgMediaSource` |
| `GetFrameRateOverride` | 获取用户手动覆盖的帧率 | `UImgMediaSource` |
| `IsPathRelativeToProjectRoot` | 判断序列路径是否相对于项目根目录 | `UImgMediaSource` |

### 使用示例

1. **创建并配置图像序列媒体源**
   - 在内容浏览器中右键 → 媒体 → Media Source → 选择 `ImgMediaSource`。
   - 设置 `Sequence Path` 为包含序列图片的文件夹（例如 `/Game/MySequence/`）。
   - 可选：调整 `Frame Rate Override`（0,0 表示不覆盖）或 `Proxy Override`。

2. **播放图像序列**
   - 将 `UMediaPlayer` 与 `UMediaTexture` 关联。
   - 在蓝图调用 `Open Source` 节点，指定上述 `ImgMediaSource`。
   - 调用 `Play` 即可播放。

3. **获取代理列表**
   - 调用 `Get Proxies` 节点，返回字符串数组，例如 `["LowRes", "Thumbnail"]`。
   - 可在编辑器中选择某个代理进行预览。

## C++ 用法

以下示例展示如何通过 C++ 创建 `UImgMediaSource` 并播放序列。

### 头文件引入

```cpp
#include "ImgMediaSource.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
```

### 基本用法

```cpp
// 创建或获取 ImgMediaSource 对象
UImgMediaSource* MediaSource = NewObject<UImgMediaSource>();
MediaSource->SetSequencePath("/Game/MySequence/"); // 设置图片目录
MediaSource->FrameRateOverride = FFrameRate(24, 1); // 可选：覆盖帧率

// 创建 MediaPlayer 并打开
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
MediaPlayer->OpenSource(MediaSource);

// 关联 MediaTexture
UMediaTexture* MediaTexture = NewObject<UMediaTexture>();
MediaTexture->SetMediaPlayer(MediaPlayer);
// 然后可将 MediaTexture 应用到材质中
```

*来源：`Plugins/Media/ImgMedia/Source/ImgMedia/Public/ImgMediaSource.h`*

### 进阶用法：使用代理和帧率覆盖

```cpp
// 获取代理列表
TArray<FString> Proxies;
MediaSource->GetProxies(Proxies);
if (Proxies.Num() > 0)
{
    MediaSource->ProxyOverride = Proxies[0]; // 使用第一个代理
}

// 设置起始时间码
MediaSource->StartTimecode = FTimecode(100, 24, true); // 00:00:04;04（假设24fps）
```

*来源：`ImgMediaSource.h` 中的 `GetProxies()` 和 `StartTimecode` 属性。*

## Demo 示例

以下是一个最小化 C++ 示例，展示了如何从代码创建并播放一个图像序列。

### MyMediaActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyMediaActor.generated.h"

class UMediaPlayer;
class UMediaTexture;
class UImgMediaSource;

UCLASS()
class AMyMediaActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMediaActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category="Media")
    FString SequencePath;

    UPROPERTY(VisibleAnywhere, Category="Media")
    UMediaPlayer* MediaPlayer;

    UPROPERTY(VisibleAnywhere, Category="Media")
    UMediaTexture* MediaTexture;

    UPROPERTY(EditAnywhere, Category="Media")
    UImgMediaSource* MediaSource;
};
```

### MyMediaActor.cpp

```cpp
#include "MyMediaActor.h"
#include "ImgMediaSource.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"

AMyMediaActor::AMyMediaActor()
{
    PrimaryActorTick.bCanEverTick = false;

    MediaPlayer = CreateDefaultSubobject<UMediaPlayer>(TEXT("MediaPlayer"));
    MediaTexture = CreateDefaultSubobject<UMediaTexture>(TEXT("MediaTexture"));
    MediaSource = CreateDefaultSubobject<UImgMediaSource>(TEXT("MediaSource"));
}

void AMyMediaActor::BeginPlay()
{
    Super::BeginPlay();

    if (MediaSource && !SequencePath.IsEmpty())
    {
        MediaSource->SetSequencePath(SequencePath);
        // 可选：设置代理
        // TArray<FString> Proxies;
        // MediaSource->GetProxies(Proxies);
        // if (Proxies.Num() > 0) MediaSource->ProxyOverride = Proxies[0];

        MediaPlayer->OpenSource(MediaSource);
        MediaTexture->SetMediaPlayer(MediaPlayer);
        MediaPlayer->Play();
    }
}
```

在蓝图中设置 `SequencePath` 为包含图片的目录路径（如 `/Game/MySequence`），然后运行观看效果。

## 模块依赖

该模块的运行时核心依赖 `OpenExrWrapper` 和 `ExrReaderGpu`（用于 GPU 读取 EXR）。编辑器部分额外依赖 `UnrealEd`。以下为 `ImgMedia` 模块的依赖列表：

| 模块 | 用途 |
|---|---|
| `OpenExrWrapper` | 封装 OpenEXR 库，提供 EXR 文件解析和读取功能 |
| `ExrReaderGpu` | GPU 端 EXR 读取优化，支持异步复制 |
| `UnrealEd` | 编辑器集成（仅在编辑器模式下需要） |

无其他特殊依赖（标准 Core/Engine/Slate 等已省略）。

## 维护状态

### 近期更新

- 2025-10-17 `f81b388d` [ImgMedia] Fix out of memory crash caused by unprotected large frame gaps.
- 2025-10-10 `ebdf8ce6` [ImgMedia] Handle global cache frame eviction while scrubbing.
- 2025-09-29 `f131b1dc` [ImgMedia] Fixing non-safe game tickable created in async load.
- 2025-08-21 `2c158c4d` Change GetUsedTextures MaterialInterface to use TOptional parameters instead of Enum+bool pairs
- 2025-08-15 `ae8bb436` ImgMedia: Setting frame duration as per the sequence frame rate instead of the value from the global

### 维护评价

该插件于2025年8月创建，至今已有约2个月，但已有多次实质性更新，包括修复内存溢出、缓存逐块、线程安全等问题。更新频率较高（平均每月≥2次），表明开发团队正在积极维护。目前没有发现废弃或性能倒退的迹象。推荐在需要播放图像序列的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ImgMedia)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)（旧版，但 Media Framework 概念通用）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ImgMedia/Tests)（如果存在）