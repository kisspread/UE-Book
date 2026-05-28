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
| 创建时间 | 2017-08-30 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ImgMedia) | |

## 用途

ImgMedia 是 UE 内置的**图像序列媒体播放器**，它将一个包含大量图片文件的目录当作视频来播放。核心解决问题是：将影视/视觉特效行业常用的逐帧图像序列（每帧一个文件）无缝集成到 UE 的 Media Framework 中，像播放普通视频一样播放图像序列。

该插件的实际能力远超 .uplugin 描述：

1. **多格式支持**：EXR（主推，支持分层、分块、GPU 解码）、BMP、JPG、PNG、DDS
2. **EXR 高级特性**：多 Mip 层级、分块（Tiling）、指定 Layer（通配符）、GPU 加速解码（`ExrReaderGpu` 模块）、异步 IO
3. **智能缓存**：全局 LRU 帧缓存（`FImgMediaGlobalCache`）、智能预取（Smart Cache）、带宽估算
4. **基于可见性的 Tile 加载**：通过 `FImgMediaTileVisibilityResolver` 和场景视图扩展（`FImgMediaSceneViewExtension`），仅加载摄像机可见的 Tile 区域，大幅降低内存和带宽开销
5. **线程调度**：专用线程池（`FImgMediaScheduler`）管理并行帧加载任务
6. **TMV 容器格式**：支持 `.tmv` 容器文件（非逐帧文件序列），使用 Demuxer 解复用
7. **颜色空间管理**：支持自定义源色彩空间和编码覆盖

## 使用场景

- 你在做影视后期/虚拟制片，需要将 After Effects / Nuke 导出的 EXR 序列在引擎中实时预览 → 用 ImgMedia
- 你在做 Motion Graphics，需要在场景中播放高分辨率图像序列作为背景/屏幕内容 → 用 ImgMedia
- 你需要仅加载摄像机可见的 Tile 区域以节省 VRAM → ImgMedia 的 Tile Visibility 系统自动处理
- 你在做 VR 180/360 内容，需要将球面图像序列作为媒体源 → 配合 `FImgMediaSphereVisibilityProvider` 使用
- 你有一个巨大的 EXR 序列但 GPU 足够强，希望用 GPU 解码 → ExrReaderGpu 模块自动启用

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSequencePath` | 获取图像序列目录路径（已展开 token） | `UImgMediaSource` |
| `SetSequencePath` | 从图像文件路径推断并设置序列目录 | `UImgMediaSource` |
| `SetTokenizedSequencePath` | 设置带 token 的序列路径（如 `{project_dir}`） | `UImgMediaSource` |
| `GetProxies` | 获取可用的代理目录列表 | `UImgMediaSource` |

### 使用示例（蓝图描述）

**基本图像序列播放**：
1. 创建一个 `UImgMediaSource` 资产（右键 → Media → Img Media Source）
2. 设置 `SequencePath` 指向图像序列目录（如 `D:/MyProject/Sequences/FireFX`）
3. 创建 `UMediaPlayer`，在编辑器中打开该 ImgMediaSource
4. 创建 `UMediaTexture`，将其设置为 MediaPlayer 的输出
5. 在材质中采样 MediaTexture，应用到网格体上
6. 运行时通过蓝图调用 MediaPlayer 的 Open/Play 控制播放

**使用帧率覆盖和 Layer**：
- 在 ImgMediaSource 资产的细节面板中，设置 `FrameRateOverride`（如 30/1）覆盖 EXR 文件内嵌的帧率
- 设置 `LayerName`（支持通配符如 `beauty.*`）仅读取 EXR 的特定层

**代理系统**：
- 创建多个子目录（如 `Proxies/HalfRes`、`Proxies/QuarterRes`）
- 设置 `ProxyOverride` 属性选择使用哪个代理
- 开发阶段使用低分辨率代理节省资源

## C++ 用法

### 头文件引入

```cpp
#include "ImgMediaSource.h"      // UImgMediaSource
#include "IImgMediaModule.h"     // IImgMediaModule 接口
#include "ImgMediaGlobalCache.h" // FImgMediaGlobalCache
#include "ImgMediaSceneViewExtension.h" // FImgMediaSceneViewExtension
```

### 基本用法

创建和配置 ImgMediaSource：

```cpp
// 创建 UImgMediaSource
UImgMediaSource* MediaSource = NewObject<UImgMediaSource>();

// 设置序列路径（绝对路径或带 token 的路径）
MediaSource->SetSequencePath(TEXT("D:/Projects/Sequences/Explosion"));

// 使用 token 的路径
MediaSource->SetTokenizedSequencePath(TEXT("{project_dir}/Content/Sequences/Explosion"));

// 设置帧率覆盖（可选，0/0 = 使用文件内嵌帧率）
MediaSource->FrameRateOverride = FFrameRate(24, 1);

// 设置 EXR Layer（可选）
MediaSource->LayerName = TEXT("beauty.*");

// 用 MediaPlayer 打开
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
MediaPlayer->OpenSource(MediaSource);
MediaPlayer->Play();
```

来源：`Public/ImgMediaSource.h`

### 进阶用法

**自定义 Tile 可见性提供器**（平面投影）：

```cpp
#include "Assets/Providers/ImgMediaPlaneVisibilityProvider.h"

// 构造参数
FImgMediaPlaneVisibilityProviderParams Params;
Params.MeshComponent = MyMeshComponent;  // 渲染图像序列的网格体
Params.SceneViewExtension = SceneViewExtension;
Params.MipMapLODBias = -1.0f;  // 负值偏向前更高画质

// 创建并注册提供器
TSharedPtr<FImgMediaPlaneVisibilityProvider> Provider =
    MakeShared<FImgMediaPlaneVisibilityProvider>(Params);
// 通过 FMediaTextureTracker 注册（5.8+ 替代了旧的 AddTargetObject）
```

**访问全局帧缓存**：

```cpp
#include "ImgMediaGlobalCache.h"

FImgMediaGlobalCache* GlobalCache = IImgMediaModule::GetGlobalCache();
if (GlobalCache)
{
    SIZE_T CurrentSize = GlobalCache->GetCurrentSize();
    SIZE_T MaxSize = GlobalCache->GetMaxSize();
}
```

来源：`Public/ImgMediaGlobalCache.h`

**监听播放器创建**：

```cpp
#include "IImgMediaModule.h"

IImgMediaModule::Get().OnImgMediaPlayerCreated.AddLambda(
    [](const TSharedPtr<FImgMediaPlayer>& Player)
    {
        // 每当新的图像序列播放器被创建时触发
    });
```

来源：`Public/IImgMediaModule.h`

## Demo 示例

**自定义 C++ Actor 播放图像序列**：

```cpp
// ImgMediaDemoActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "ImgMediaSource.h"
#include "ImgMediaDemoActor.generated.h"

UCLASS()
class AImgMediaDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AImgMediaDemoActor();

    UPROPERTY(EditAnywhere, Category = "Media")
    FString SequencePath;

    UPROPERTY(EditAnywhere, Category = "Media")
    FFrameRate FrameRateOverride;

    UPROPERTY(EditAnywhere, Category = "Media")
    FString LayerName;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Media")
    TObjectPtr<UMediaPlayer> MediaPlayer;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Media")
    TObjectPtr<UMediaTexture> MediaTexture;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Media")
    TObjectPtr<UImgMediaSource> MediaSource;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    TObjectPtr<UStaticMeshComponent> MeshComponent;

    UFUNCTION(BlueprintCallable, Category = "Media")
    void PlaySequence();

    UFUNCTION(BlueprintCallable, Category = "Media")
    void StopSequence();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
};
```

```cpp
// ImgMediaDemoActor.cpp
#include "ImgMediaDemoActor.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "ImgMediaSource.h"
#include "Components/StaticMeshComponent.h"
#include "Materials/MaterialInstanceDynamic.h"

AImgMediaDemoActor::AImgMediaDemoActor()
{
    MeshComponent = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    RootComponent = MeshComponent;

    MediaPlayer = CreateDefaultSubobject<UMediaPlayer>(TEXT("MediaPlayer"));
    MediaTexture = CreateDefaultSubobject<UMediaTexture>(TEXT("MediaTexture"));
    MediaTexture->SetMediaPlayer(MediaPlayer);
}

void AImgMediaDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建并配置 ImgMediaSource
    MediaSource = NewObject<UImgMediaSource>(this);
    MediaSource->SetSequencePath(SequencePath);
    MediaSource->FrameRateOverride = FrameRateOverride;
    MediaSource->LayerName = LayerName;

    // 打开源并开始播放
    if (MediaSource->Validate())
    {
        MediaPlayer->OpenSource(MediaSource);
        MediaPlayer->Play();
    }
}

void AImgMediaDemoActor::PlaySequence()
{
    if (MediaPlayer && !MediaPlayer->IsPlaying())
    {
        MediaPlayer->Play();
    }
}

void AImgMediaDemoActor::StopSequence()
{
    if (MediaPlayer)
    {
        MediaPlayer->Close();
    }
}

void AImgMediaDemoActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MediaPlayer)
    {
        MediaPlayer->Close();
    }
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OpenExrWrapper` | OpenEXR 库的 UE 封装层，用于读取 EXR 格式图像 |
| `ExrReaderGpu` | EXR 文件的 GPU 加速解码器，通过结构化缓冲区 + Compute Shader 实现异步解码 |
| `MediaUtils` | Media Framework 工具层（样本队列、时间源等） |
| `MediaAssets` | Media Framework 资产类型（MediaPlayer、MediaTexture、MediaSource） |
| `RenderCore` | GPU 结构化缓冲区分配、RHI 命令队列（用于 ExrReaderGpu） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `edcd0d53` | [ImgMedia] refresh single-frame sequences on tile visibility changes | 单帧序列在 Tile 可见性变化时刷新 |
| 2026-05-26 | `cf292c45` | [ImgMedia] Use AR-constrained view rect for tile mip selection | 使用 AR 约束视口矩形进行 Tile Mip 选择 |
| 2026-05-26 | `96b8b04b` | Media IO: Fix to recent CL 54396736 for ImgMedia and NDI players emitting incorrect SourceOpened analytics | 修复 ImgMedia 和 NDI 播放器错误发送 SourceOpened 分析事件 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and processing pipeline | 为多种媒体播放器添加引擎分析信息 |
| 2026-05-22 | `7d256b73` | [Media] Add shared Media category to the Level Editor Window menu | 在关卡编辑器窗口菜单中添加共享 Media 分类 |

### 维护评价

ImgMedia 是 UE Media Framework 的核心组件之一，**持续活跃维护**中。

- **创建时间**：2017 年 8 月（Media Framework 3.0 大重构期间）
- **近期更新**：2026 年 5 月仍有实质性功能更新（Tile 可见性改进、AR 约束、分析事件），表明该插件处于**活跃开发**状态
- **关键特性**：支持 EXR 分层/分块/GPU 解码、智能缓存预取、基于视口的 Tile 按需加载、多种图像格式、TMV 容器格式
- **架构成熟度**：经过 9 年迭代，架构稳定，线程模型清晰（游戏线程 → 调度器 → 工作线程 → 渲染线程）
- **推荐使用**：**强烈推荐**。这是 UE 中播放图像序列的标准方案，尤其适合影视/VFX/虚拟制片工作流。EXR 格式支持最全面，性能优化最到位

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ImgMedia)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ImgMedia/Source/ImgMedia/Private/Tests)