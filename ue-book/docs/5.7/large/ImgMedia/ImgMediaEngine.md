# Image Sequence Media Player

> Implements a media player for image sequences in EXR and other formats.

| 属性 | 值 |
|---|---|
| 中文名 | 图像序列媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ImgMedia` (Runtime), `ImgMediaEditor` (Editor), `ImgMediaEngine` (Runtime), `ImgMediaFactory` (Runtime), `ExrReaderGpu` (Runtime), `OpenExrWrapper` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-08-15 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ImgMedia) | |

## 用途

Image Sequence Media Player 插件提供对图像序列（如 EXR、PNG、JPG 等）的播放支持，适用于需要逐帧加载大量高分辨率图像作为视频源的场景（例如电影级渲染回放、虚拟制片、高动态范围内容）。相比传统视频编解码，图像序列可避免压缩伪影，支持自定义帧率和可选的 mipmap 选择性加载，显著降低显存占用。

**ImgMediaEngine 子模块**（当前焦点）原本提供用于协助图像序列播放的 ActorComponent，通过注册媒体纹理实现按距离或视野动态加载的 mipmap 策略。该组件自 UE 5.3 起已弃用，官方推荐改用 `MediaPlate` 组件获取等效功能。

## 使用场景

- 在虚拟制片或影视预演中播放高分辨率 EXR 序列帧
- 需要精确控制每一帧的加载时机和显存预取
- 希望根据视点距离自动降低非重点部分的纹理精度（mipmap 感知）
- 将图像序列作为动态背景或全景天空球素材

## 蓝图用法

> **注意**：`ImgMediaPlaybackComponent` 自 UE 5.3 起已弃用，以下功能仅适用于旧版本迁移参考。新项目请直接使用 `MediaPlate`。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `LODBias` | 调整 mipmap 级别的偏移量。正值强制使用更高 lod（更模糊），负值要求更高精度 | `UDEPRECATED_ImgMediaPlaybackComponent` |

### 使用示例（蓝图描述）

1. 在关卡中放置一个任意 Actor（如静态网格体）。
2. 为该 Actor 添加 `ImgMediaPlaybackComponent`（已弃用）。
3. 在组件的细节面板中设置 `LODBias` 值（默认 0）。
4. 确保该 Actor 上绑定的 `MediaTexture` 使用的是 `Image Sequence Media Source`。
5. 运行时，系统会根据视口到该 Actor 的距离自动选择 mipmap 级别，`LODBias` 会叠加到计算结果上。

## C++ 用法

### 头文件引入

```cpp
#include "Unreal/ImgMediaPlaybackComponent.h"
```

### 基本用法

```cpp
// 创建一个继承自 AActor 的类，并在其构造函数中添加已弃用的 ImgMediaPlaybackComponent
AMyMediaActor::AMyMediaActor()
{
    PlaybackComponent = CreateDefaultSubobject<UDEPRECATED_ImgMediaPlaybackComponent>(TEXT("ImgMediaPlayback"));
    PlaybackComponent->LODBias = 1.0f; // 强制降低纹理精度以提升性能
}
```

> **警告**：该组件已在 UE 5.3 中标记为 `UE_DEPRECATED(5.3, "...")`，未来版本可能移除。

### 进阶用法

（无额外高级 API 暴露）

## Demo 示例

由于 `ImgMediaEngine` 模块仅提供弃用组件，不推荐编写新代码使用。以下示例展示如何通过 `MediaPlate` 替代（推荐做法）：

**MyMediaActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlate.h"
#include "MyMediaActor.generated.h"

UCLASS()
class AMyMediaActor : public AActor
{
    GENERATED_BODY()
public:
    AMyMediaActor();
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Media")
    UMediaPlateComponent* MediaPlate;
};
```

**MyMediaActor.cpp**
```cpp
#include "MyMediaActor.h"
#include "MediaPlateComponent.h"
#include "MediaPlayer.h"

AMyMediaActor::AMyMediaActor()
{
    MediaPlate = CreateDefaultSubobject<UMediaPlateComponent>(TEXT("MediaPlate"));
    MediaPlate->SetLooping(true);
    
    // 设置图像序列媒体源（可通过蓝图指定具体资产）
    static ConstructorHelpers::FObjectFinder<UMediaSource> MediaSource(TEXT("/Game/Media/MyImageSequence.MediaSource"));
    if (MediaSource.Succeeded())
    {
        MediaPlate->MediaPlayer->SetSource(MediaSource.Object);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OpenExrWrapper` | 提供 EXR 格式的低级读写接口 |
| `ExrReaderGpu` | GPU 端 EXR 帧读取加速 |
| `MediaUtils`, `MediaAssets` | Unreal 媒体框架基础模块 |
| `Renderer`, `RHI` | 纹理资源管理与渲染管线 |

以上为 `ImgMediaEngine` 的实际间接依赖。若仅使用 `ImgMediaEngine`，无需额外依赖声明（因为组件已弃用，新项目不应引用）。

## 维护状态

### 近期更新

- 2025-10-17 f81b388d 修复因未处理的大帧间隙导致的 OOM 崩溃
- 2025-10-10 ebdf8ce6 处理全局缓存帧在 scrubbing 时的剔除问题
- 2025-09-29 f131b1dc 修复异步加载中创建的非安全游戏 tickable 对象
- 2025-08-21 2c158c4d 修改 `GetUsedTextures` 材质接口为使用 TOptional 参数替代枚举+bool 对
- 2025-08-15 ae8bb436 将帧持续时间设置为按序列帧率计算而不是全局值

### 维护评价

- **活跃维护**：最新 commits 集中在功能性 Bug 修复和性能优化，更新频率高（最近两月内）。
- **模块状态**：`ImgMediaEngine` 子模块自 5.3 起已弃用，其功能被 `MediaPlate` 替代。使用该组件的旧项目应尽快迁移。
- **推荐使用**：整体插件积极维护，但 `ImgMediaEngine` 不应在新项目中使用。推荐直接使用 `MediaPlate` 实现图像序列播放与智能 mipmap 管理。

## 相关链接

- [源代码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ImgMedia)
- [官方论坛 Media Framework 文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)
- [MediaPlate 官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/media-framework-in-unreal-engine)（推荐替代组件）