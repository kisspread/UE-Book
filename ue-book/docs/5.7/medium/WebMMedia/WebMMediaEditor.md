# WebM Video Player

> 未在 .uplugin 元数据中提供描述（源数据被截断）

| 属性 | 值 |
|---|---|
| 中文名 | WebM视频播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `WebMMedia` (Runtime), `WebMMediaEditor` (Runtime), `WebMMediaFactory` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/WebMMedia) | |

## 用途

`WebMMedia` 插件为 Unreal Engine 提供了对 **WebM 格式**（.webm）视频文件的播放能力。它基于 `libwebm`（WebM 容器解析）和 `LibVpx`（VP8/VP9 视频解码）第三方库，实现了媒体播放器接口，允许引擎使用标准 `UMediaPlayer` 控件播放 WebM 视频，并支持纹理输出和音频渲染。

该插件的主要目的是填补 UE 原生媒体框架对 WebM 格式支持的空白，使得开发者可以在项目中直接使用开放、免版税的 WebM 视频格式，常用于：

- 游戏内过场动画、UI 背景视频
- VR 环境中的 360° 视频播放
- 轻量级、无专利许可费的媒体资源分发

## 使用场景

- **你需要播放 .webm 格式的视频文件** → 启用此插件后，`UMediaPlayer` 可自动识别并播放 WebM 源。
- **你希望避免使用专有视频格式（如 H.264）的许可费用** → WebM 使用 VP8/VP9 编码，完全免版税。
- **你的目标平台为 Windows 64 位** → 插件目前仅支持 Win64（从 `.uplugin` 的 PlatformAllowList 看）。

## 蓝图用法

该插件本身不直接暴露大量可调用节点，而是通过引擎的通用媒体系统集成。主要交互在蓝图编辑器中：

- 创建 **Media Player** 资产（蓝图类 `MediaPlayer`）
- 创建 **File Media Source** 资产（`FileMediaSource`），并设置文件路径指向 `.webm` 文件
- 将 Media Player 与 Media Source 关联，使用 `Open Source` 节点播放

> **提示**：插件中的 `UWebMPlatFileMediaSourceFactory`（位于 `WebMMediaEditor` 模块）提供了在内容浏览器中通过“导入”按钮直接导入 `.webm` 文件的功能，它会自动创建 `File Media Source` 资产。

### 核心节点（引擎原生）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 打开媒体源并开始播放 | `UMediaPlayer` |
| `Play` | 开始/继续播放 | `UMediaPlayer` |
| `Pause` | 暂停播放 | `UMediaPlayer` |
| `Set Media Source` | 绑定媒体源资产 | `UMediaPlayer` |
| `On Media Opened` | 播放器成功打开媒体时触发的事件 | `UMediaPlayer` |
| `Get Texture` | 获取当前视频帧的纹理，可用于材质 | `UMediaTexture` |

### 使用示例（蓝图）

1. 在内容浏览器中右键 → **Media** → **Media Player**，创建一个 `MediaPlayer` 资产。
2. 右键 → **Media** → **File Media Source**，创建一个 `FileMediaSource` 资产，并设置 `FilePath` 为有效的 `.webm` 文件路径（或通过内容浏览器导入 `.webm` 文件，工厂会自动创建 `FileMediaSource`）。
3. 在关卡蓝图中，从 `MediaPlayer` 资产引用调用 `Open Source`，输入为刚创建的 `FileMediaSource`。
4. 连接 `Play` 节点到成功分支，即可启动播放。
5. 使用 `MediaTexture` 将视频帧渲染到 UI 或静态网格体上。

## C++ 用法

### 头文件引入

```cpp
#include "MediaPlayer.h"
#include "MediaSource.h" // 或 FileMediaSource.h
#include "MediaTexture.h"
```

### 基本用法

```cpp
// 创建媒体播放器对象
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
// 创建媒体源（若为文件路径）
UFileMediaSource* MediaSource = NewObject<UFileMediaSource>();
MediaSource->FilePath = TEXT("C:/MyVideo.webm");

// 打开媒体
MediaPlayer->OpenSource(MediaSource);

// 开始播放
MediaPlayer->Play();
```

如果需要获取视频纹理用于材质或 UI，可创建 `UMediaTexture` 并关联到播放器：

```cpp
UMediaTexture* MediaTexture = NewObject<UMediaTexture>();
MediaTexture->SetMediaPlayer(MediaPlayer);
// 之后将 MediaTexture 赋值给材质实例的 Texture 参数即可。
```

### 进阶用法

插件内部实现了 `IMediaPlayer` 接口，可直接获取播放器句柄进行更精细控制（如解码设置）。但大多数情况下，通过 `UMediaPlayer` 的蓝图兼容 API 即可满足需求。若需要直接访问底层播放器对象，可通过 `UMediaPlayer::GetPlayerPlugin()` 获取 `FName("WebMMedia")` 对应的播放器实例。

## Demo 示例

以下是一个最小可编译的 `AActor` 子类，在 BeginPlay 时自动播放指定路径的 WebM 文件。

**MyWebMPlayer.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "MediaSource.h"
#include "MediaTexture.h"
#include "MyWebMPlayer.generated.h"

UCLASS()
class AMyWebMPlayer : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    UMediaPlayer* MediaPlayer;

    UPROPERTY()
    UMediaTexture* MediaTexture;
};
```

**MyWebMPlayer.cpp**

```cpp
#include "MyWebMPlayer.h"
#include "FileMediaSource.h"

void AMyWebMPlayer::BeginPlay()
{
    Super::BeginPlay();

    // 创建媒体播放器
    MediaPlayer = NewObject<UMediaPlayer>(this);
    MediaPlayer->PlayOnOpen = true;

    // 创建媒体源（文件路径可根据实际修改）
    UFileMediaSource* MediaSource = NewObject<UFileMediaSource>();
    MediaSource->FilePath = TEXT("Content/Movies/MyVideo.webm"); // 参考路径

    // 打开媒体
    MediaPlayer->OpenSource(MediaSource);

    // 可选：创建材质纹理用于显示
    MediaTexture = NewObject<UMediaTexture>(this);
    MediaTexture->SetMediaPlayer(MediaPlayer);
    MediaTexture->UpdateResource();
}
```

> **注意**：上述示例假设项目已启用 `WebMMedia` 插件（默认关闭，需在插件设置中手动启用），并且 `FileMediaSource` 类属于 `MediaAssets` 模块，需要依赖 `MediaAssets`。

## 模块依赖

以下为使用 `WebMMedia` 插件时，你的模块 `Build.cs` 需要添加的**独特**依赖（省略了 Core、Engine 等标准依赖）：

| 模块 | 用途 |
|---|---|
| `Media` | UE 媒体框架核心接口 |
| `MediaAssets` | 蓝图友好的媒体资产类（`MediaPlayer`、`FileMediaSource` 等） |
| `WebMMedia` | 插件的主运行时模块（包含播放器实现） |

> 如果仅使用蓝图，无需额外 C++ 依赖。

## 维护状态

### 近期更新

- 2025-09-12 `828f0392` WebMMedia: Clearing all members on Close() to remove any tracks that were added before detecting the...
- 2025-08-29 `32884de4` Changing more uses of RHICreateTexture to RHICmdList.CreateTexture.
- 2025-07-10 `abb369e2` Added UE_INLINE_GENERATED_CPP_BY_NAME to source files...
- 2025-06-02 `3643a063` Remove old libwebm linux build files
- 2025-06-02 `8e5bc4b0` Updated linux build for libwebm

### 维护评价

- **创建时间**：2025-06-02（约 4 个月前），属于较新的插件。
- **活跃度**：最近三个月内有多次实质性更新（关闭清理、渲染适配、构建脚本调整），说明仍在积极维护。
- **状态**：`.uplugin` 中标记为 `IsBetaVersion: true`，表示原厂认为该插件尚处于实验/测试阶段，可能存在不稳定或接口变动。
- **推荐度**：推荐在新项目中使用，但应留意后续更新。若需要生产级稳定性，建议关注其正式版发布。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/WebMMedia)
- [官方文档](https://docs.unrealengine.com/5.3/en-US/WebMMedia/)（推测，可在线查找）
- 测试用例：无公开专用测试文件（可通过引擎自带的 `Media Player` 功能测试）。