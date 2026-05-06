# Bink Media

> Implements a media player using Bink.

| 属性 | 值 |
|---|---|
| 中文名 | Bink 媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BinkMediaPlayer` (Runtime), `BinkMediaPlayerEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-07-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/BinkMedia) | |

## 用途

Bink Media 插件将 RAD Game Tools 的 Bink 视频格式集成到 Unreal Engine。Bink 是一种专有的、高度优化的视频编解码器，专为游戏过场动画和预渲染内容设计——它在保持极低 CPU/GPU 开销的同时提供了优秀的压缩比。该插件提供了：

- **运行时播放**：通过 `UBinkMediaPlayer` 在游戏世界中播放 Bink 视频（`.bk2` 文件）
- **纹理输出**：通过 `UBinkMediaTexture` 将视频帧渲染到任意材质上
- **编辑器内预览**：在编辑器中直接预览和调试 Bink 视频，无需运行游戏
- **全屏/过场动画支持**：可配合 `MoviePlayer` 模块实现启动动画或无缝过场

该插件解决了在 Unreal Engine 中使用 Bink 格式时的编解码器接入、纹理更新、音视频同步等复杂问题，让开发者只需调用简单的 API 即可播放高质量视频。

## 使用场景

- 制作高质量的游戏过场动画（尤其是需要与游戏内容无缝衔接时）
- 作为背景视频（例如主菜单动画、教程视频）
- 使用 Bink 为 UI 提供视频元素（通过动态材质）
- 需要低 CPU 开销的视频播放（Bink 通常比 H.264 解码更省资源）
- 在打包体积和视觉质量之间取得平衡（Bink 压缩效率高）

## 蓝图用法

以下节点来自 `UBinkMediaPlayer` 类的公共接口（基于编辑器模块头文件中的使用推断，该类通常标记所有核心方法为 `BlueprintCallable`）。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play` | 开始播放媒体 | `UBinkMediaPlayer` |
| `Pause` | 暂停播放 | `UBinkMediaPlayer` |
| `Rewind` | 倒带到开头位置 | `UBinkMediaPlayer` |
| `Seek` (Time) | 跳转到指定的时间点 | `UBinkMediaPlayer` |
| `SetRate` (Rate) | 设置播放速率（1.0 = 正常，0.0 = 暂停，2.0 = 两倍速） | `UBinkMediaPlayer` |
| `GetRate` | 返回当前播放速率 | `UBinkMediaPlayer` |
| `GetTime` | 返回当前播放时间（`FTimespan`） | `UBinkMediaPlayer` |
| `GetDuration` | 返回媒体总时长（`FTimespan`） | `UBinkMediaPlayer` |
| `GetUrl` | 返回当前媒体 URL | `UBinkMediaPlayer` |
| `SupportsScrubbing` | 检查是否支持拖动（通常为 `true`） | `UBinkMediaPlayer` |
| `SupportsSeeking` | 检查是否支持跳转（通常为 `true`） | `UBinkMediaPlayer` |
| `OpenUrl` (Url) | 打开一个 Bink 媒体源（`.bk2` 文件路径或网络 URL） | `UBinkMediaPlayer` |
| `OnMediaChanged` | 当媒体内容改变时触发的事件分发器 | `UBinkMediaPlayer` |

### 使用示例（蓝图描述）

1. **播放本地 Bink 文件**  
   - 在关卡蓝图中，使用 `OpenUrl` 节点，输入值例如 `"Content/BinkVideos/MyVideo.bk2"`（相对于 Content 目录）。  
   - 将返回的成功/失败信号连接到 `Play` 节点。  
   - 也可将 `UBinkMediaPlayer` 拖入蓝图，绑定到材质中的 `UBinkMediaTexture`。

2. **实现进度条拖动**  
   - 用 `GetDuration` 获取总时长，除以 `GetTime` 得到 0~1 比值。  
   - 用 `SetRate(0)` 暂停播放，调用 `Seek` 后恢复速率（如编辑器 Viewer 中的实现）。

## C++ 用法

### 头文件引入

```cpp
#include "BinkMediaPlayer.h"
#include "BinkMediaTexture.h"
```

### 基本用法

创建一个 `UBinkMediaPlayer` 对象，设置 URL 并开始播放。

```cpp
// 在你的 Actor 或 Component 中
#include "BinkMediaPlayer.h"
#include "BinkMediaTexture.h"

class AMyVideoActor : public AActor
{
    GENERATED_BODY()
public:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Media")
    UBinkMediaPlayer* MediaPlayer;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Media")
    UBinkMediaTexture* MediaTexture;

    virtual void BeginPlay() override
    {
        Super::BeginPlay();
        
        MediaPlayer = NewObject<UBinkMediaPlayer>(this);
        if (MediaPlayer)
        {
            MediaPlayer->OpenUrl("Content/BinkVideos/Intro.bk2");
            MediaPlayer->Play();
        }
    }
};
```

*来源：基于编辑器模块的工厂使用和常见运行时模式，但未提供明确 test case。*

### 进阶用法：在 Material 中播放

将 `UBinkMediaTexture` 赋给材质的 Base Color，然后驱动其播放。

```cpp
// 创建 MediaTexture 并关联 MediaPlayer
MediaTexture = NewObject<UBinkMediaTexture>(this);
MediaTexture->SetMediaPlayer(MediaPlayer);

// 将 MediaTexture 赋给动态材质实例
if (MyMesh && MyMesh->GetMaterial(0))
{
    UMaterialInstanceDynamic* DynMat = UMaterialInstanceDynamic::Create(MyMesh->GetMaterial(0), this);
    DynMat->SetTextureParameterValue("VideoTexture", MediaTexture);
    MyMesh->SetMaterial(0, DynMat);
}
```

## Demo 示例

一个完整的 Actor 类，用于在关卡中播放 Bink 视频并显示在平面上。

**MyBinkActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyBinkActor.generated.h"

UCLASS()
class AMYBINKACTOR : public AActor
{
    GENERATED_BODY()
public:
    AMYBINKACTOR();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Media")
    class UStaticMeshComponent* Mesh;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Media")
    class UBinkMediaPlayer* MediaPlayer;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Media")
    class UBinkMediaTexture* MediaTexture;

    virtual void BeginPlay() override;
};
```

**MyBinkActor.cpp**
```cpp
#include "MyBinkActor.h"
#include "BinkMediaPlayer.h"
#include "BinkMediaTexture.h"
#include "Components/StaticMeshComponent.h"
#include "Materials/MaterialInstanceDynamic.h"

AMYBINKACTOR::AMYBINKACTOR()
{
    PrimaryActorTick.bCanEverTick = false;

    Mesh = CreateDefaultSubobject<UStaticMeshComponent>("DisplayMesh");
    RootComponent = Mesh;

    MediaPlayer = CreateDefaultSubobject<UBinkMediaPlayer>("MediaPlayer");
    MediaTexture = CreateDefaultSubobject<UBinkMediaTexture>("MediaTexture");
    MediaTexture->SetMediaPlayer(MediaPlayer);
}

void AMYBINKACTOR::BeginPlay()
{
    Super::BeginPlay();

    // 打开并播放 Bink 视频
    MediaPlayer->OpenUrl("Content/BinkVideos/MyVideo.bk2");
    MediaPlayer->Play();

    // 将 MediaTexture 应用到材质
    if (Mesh && Mesh->GetMaterial(0))
    {
        UMaterialInstanceDynamic* DynMat = UMaterialInstanceDynamic::Create(Mesh->GetMaterial(0), this);
        DynMat->SetTextureParameterValue("VideoTexture", MediaTexture);
        Mesh->SetMaterial(0, DynMat);
    }
}
```

*注意：需要确保 `Content/BinkVideos/MyVideo.bk2` 文件存在，并且在项目设置中启用了 `BinkMedia` 插件。*

## 模块依赖

要使用 `BinkMedia` 插件，你的模块的 `Build.cs` 中需要添加以下依赖（已省略常见的 Core/Engine 模块）：

**运行时模块**（`BinkMediaPlayer`）的独特依赖：

| 模块 | 用途 |
|---|---|
| `MediaAssets` | 提供媒体框架的资产类型支持 |
| `MoviePlayer` | 用于启动动画/全屏视频播放 |
| `RenderCore` / `RHI` | 渲染管线集成，纹理更新 |
| `Projects` | 文件路径和项目设置支持 |

**编辑器模块**（`BinkMediaPlayerEditor`）的额外依赖：

| 模块 | 用途 |
|---|---|
| `BinkMediaPlayer` | 运行时模块（必须） |
| `MetalRHI` | 特定平台渲染接口（仅当目标平台需要时） |
| `DesktopWidgets` | 编辑器中的文件对话框（工厂使用） |

**外部 SDK**（`BinkMediaPlayerSDK`）通常由插件内部处理，无需用户额外依赖。

## 维护状态

### 近期更新

| 日期 | Hash | Commit 说明 |
|---|---|---|
| 2025-08-29 | `32884de4` | 将更多 `RHICreateTexture` 调用改为 `RHICmdList.CreateTexture` (RHI 现代化) |
| 2025-08-27 | `7766f4c6` | 修复视频流读取器 `Open` 返回值的错误 |
| 2025-08-08 | `40e2c8da` | 将 RHI 命令列表传递通过 MoviePlayer 和 TickableObjectRenderThread 函数 |
| 2025-08-05 | `dfd9e75a` | 修复 CookOnTheFly 路径（长期 bug，感谢 BugHawk） |
| 2025-07-27 | `bd4ed858` | 初始创建，移除不必要的 `bAllowConfidentialPlatformDefines` |

### 维护评价

**创建时间**：2025-07-27  
**年龄**：约 1 个月（新插件）  
**维护活跃度**：非常活跃，自创建以来几乎每周都有功能性修复和适配更新。  
**质量信号**：  
- 最近的更新聚焦于 RHI 现代化（命令列表传递）和已知 bug 修复，表明团队正在积极地跟进引擎演进并解决用户反馈。  
- 没有发现弃用标记或警告。  
- “长期 bug” 的修复说明社区反馈有渠道且被认真对待。  

**推荐使用** ✅ 推荐。作为官方插件，Bink Media 稳定且性能优异，适合需要高质量视频播放的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/BinkMedia)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/WorkingWithMedia/IntegratingMedia/BinkVideo/)（基于 `.uplugin` 中 `GetDocumentationLink` 返回的路径）  
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/BinkMedia/Source)（未单独提供测试，但可通过源码中的工厂和编辑器功能推断）