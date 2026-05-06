# WMF Media Player

> Implements a media player using the Windows Media Foundation framework.

| 属性 | 值 |
|---|---|
| 中文名 | WMF 媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `WmfMedia` (Runtime), `WmfMediaEditor` (Editor), `WmfMediaFactory` (Editor, RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2025-04-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/WmfMedia) | |

---

## 用途

`WmfMedia` 是 Unreal Engine 在 Windows 平台上的原生媒体播放解决方案，基于微软的 **Windows Media Foundation (WMF)** 框架开发。它解决了以下问题：

- 在 Win64 平台上播放常见的音频/视频文件（如 MP4、WMV、MP3、AAC 等）
- 支持硬件加速（DX11/DX12 解码），降低 CPU 占用
- 提供标准媒体播放接口（播放、暂停、跳转、循环、速率控制等）
- 兼容 UE 的 `MediaPlayer` 资产系统，可直接用于材质、UI 或音频

**为什么存在？** 相比于平台无关的媒体播放器（如 Media Foundation 的通用实现），WmfMedia 深度优化了 Windows 平台的解码性能，并修复了 WMF 在 DX11/DX12 下的解码像素布局问题，确保渲染正确。

---

## 使用场景

- **游戏内过场动画** – 使用 WMF 播放高码率 MP4 视频，配合硬件解码实现流畅播放
- **UI 背景/视频壁纸** – 将媒体播放器绑定到 `MediaTexture` 并显示在 UMG 或 3D 材质上
- **音乐/音效播放** – 播放 MP3、WMA 等音频文件，支持循环和速度调节
- **视频流/摄像头输入（扩展）** – WMF 原生支持设备流，可通过自定义源实现摄像头输入
- **编辑器预览** – 在内容浏览器中直接导入并预览媒体文件

---

## 蓝图用法

> **注意**：本模块（WmfMediaEditor）仅提供编辑器工厂，不暴露蓝图可调用节点。运行时蓝图 API 由 `MediaPlayer` 和 `BinkMediaPlayer`（如果启用）等通用类提供。WmfMedia 不新增专属蓝图节点，所有操作通过标准媒体框架完成。

### 核心节点（通用媒体框架）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 打开一个媒体源（资产或 URL） | `MediaPlayer` |
| `Play` | 开始播放 | `MediaPlayer` |
| `Pause` | 暂停播放 | `MediaPlayer` |
| `Set Rate` | 设置播放速率（0=暂停，1=正常，2=2倍速等） | `MediaPlayer` |
| `Get Duration` | 获取媒体总时长 | `MediaPlayer` |
| `Seek` | 跳转到指定时间（Timecode） | `MediaPlayer` |
| `Get Texture` | 获取当前帧纹理（用于 UI 或材质） | `MediaPlayer` |
| `Create Media Player` | 在蓝图中创建媒体播放器对象 | `MediaPlayer`（静态函数） |

### 使用示例（蓝图描述）

1. **播放本地视频**  
   - 在内容浏览器中创建 `FileMediaSource` 资产，指定视频文件路径。  
   - 创建 `MediaPlayer` 对象 → `Open Source`（选择 `FileMediaSource` 资产）→ `Play`。  
   - 创建 `MediaTexture` 资产 → 在其 Details 面板中设置 `Media Player` 引用。  
   - 将 `MediaTexture` 拖入 UMG 的 `Image` 控件。

2. **循环播放背景音乐**  
   - 创建 `MediaPlayer` 和 `MediaSoundComponent`。  
   - `Open Source` 打开音频文件 → `Play` → 在 `OnEndReached` 事件中再次调用 `Play`。

---

## C++ 用法

### 头文件引入

```cpp
#include "WmfMediaPlayer.h"   // 运行时模块主头文件
#include "WmfMediaSource.h"   // 媒体源
#include "WmfMediaSettings.h" // 配置
```

### 基本用法

从测试用例（`Engine/Plugins/Media/WmfMedia/Source/WmfMedia/Private/Tests/WmfMediaTest.cpp`）提取示例：

```cpp
// 创建媒体播放器
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
if (MediaPlayer == nullptr) return;

// 创建文件媒体源
UFileMediaSource* MediaSource = NewObject<UFileMediaSource>();
MediaSource->SetFilePath(TEXT("D:/Videos/test.mp4"));

// 打开并播放
{
    FMediaPlayerOptions Options;
    Options.SeekTime = FTimespan::FromSeconds(10.0);     // 从10秒处开始
    Options.PlayOnOpen = EMediaPlayerOptionBooleanOverride::Enabled;

    MediaPlayer->OpenSource(MediaSource, Options);
}

// 监听事件（需绑定到MediaPlayer的OnMediaOpened等委托）
MediaPlayer->OnMediaOpened.AddLambda([]
{
    UE_LOG(LogTemp, Log, TEXT("Media opened!"));
});
```

### 进阶用法

**实现自定义媒体源**（继承 `UMediaSource`）：

```cpp
#include "MediaSource.h"

UCLASS()
class UMyCustomMediaSource : public UMediaSource
{
    GENERATED_BODY()
public:
    virtual FString GetUrl() const override
    {
        return TEXT("file:///D:/Videos/myvideo.mp4"); // 或 rtsp://...
    }
};

// 使用
UMyCustomMediaSource* MySource = NewObject<UMyCustomMediaSource>();
MediaPlayer->OpenSource(MySource);
```

**与 MediaTexture 配合渲染到材质**：

```cpp
#include "MediaTexture.h"
#include "MediaPlayer.h"

UMediaPlayer* Player = CreateDefaultSubobject<UMediaPlayer>(TEXT("MediaPlayer"));
UMediaTexture* Texture = CreateDefaultSubobject<UMediaTexture>(TEXT("MediaTexture"));

Texture->SetMediaPlayer(Player);
// 然后 Texture 可作为 UMaterialInstanceDynamic 输入使用
```

**配置硬件解码参数**：

```cpp
// 在项目设置中调整 WMF 解码选项
// 或通过代码修改 UDeveloperSettings
UWmfMediaSettings* Settings = GetMutableDefault<UWmfMediaSettings>();
Settings->EnableHardwareDecoding = true;
Settings->HardwareDecodingFormat = EWmfHardwareVideoDecodingFormat::DX11;
Settings->SaveConfig();
```

---

## Demo 示例

一个完整的 C++ Actor，在游戏中播放本地视频并显示在 3D 平面上。

### DemoActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "Components/StaticMeshComponent.h"
#include "DemoActor.generated.h"

UCLASS()
class ADemoActor : public AActor
{
    GENERATED_BODY()

public:
    ADemoActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Media")
    UMediaPlayer* MediaPlayer;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Media")
    UMediaTexture* MediaTexture;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Media")
    UStaticMeshComponent* VideoPlane;
};
```

### DemoActor.cpp

```cpp
#include "DemoActor.h"
#include "FileMediaSource.h"
#include "Materials/MaterialInstanceDynamic.h"

ADemoActor::ADemoActor()
{
    PrimaryActorTick.bCanEverTick = false;

    VideoPlane = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("VideoPlane"));
    RootComponent = VideoPlane;

    MediaPlayer = CreateDefaultSubobject<UMediaPlayer>(TEXT("MediaPlayer"));
    MediaTexture = CreateDefaultSubobject<UMediaTexture>(TEXT("MediaTexture"));
    MediaTexture->SetMediaPlayer(MediaPlayer);
}

void ADemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建动态材质实例并设置纹理
    UMaterialInstanceDynamic* DynMat = VideoPlane->CreateDynamicMaterialInstance(0);
    if (DynMat)
    {
        DynMat->SetTextureParameterValue(TEXT("VideoTexture"), MediaTexture);
    }

    // 打开媒体源
    UFileMediaSource* MediaSource = NewObject<UFileMediaSource>();
    MediaSource->SetFilePath(TEXT("D:/Videos/intro.mp4"));

    FMediaPlayerOptions Options;
    Options.PlayOnOpen = EMediaPlayerOptionBooleanOverride::Enabled;
    Options.Loop = EMediaPlayerOptionBooleanOverride::Enabled;

    if (!MediaPlayer->OpenSource(MediaSource, Options))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open media source!"));
    }
}
```

---

## 模块依赖

WmfMedia 各模块的 Build.cs 依赖分析：

| 模块 | 用途 |
|---|---|
| `HeadMountedDisplay` | 支持 VR 环境下读取 HMD 状态（WmfMedia 运行时） |
| `D3D11RHI` | 硬件解码纹理共享（WmfMedia 运行时） |
| `D3D12RHI` | 类似，用于 DX12 解码（未在 Build.cs 列出，但实际使用） |
| `MediaUtils` | 媒体框架工具函数（隐式依赖） |

**无特殊依赖（仅标准 Core/Engine/Slate 等）**：`WmfMediaEditor` 和 `WmfMediaFactory` 只依赖引擎标准模块，无独特依赖。

---

## 维护状态

### 近期更新

基于 git log（2025 年 4 月至今）：

- 2025-09-03 `10aed468` – WmfMedia: Clamping number of inflight requests in case ProcessSample() is invoked multiple times in （修复处理样本重复调用的越界问题）
- 2025-08-29 `32884de4` – Changing more uses of RHICreateTexture to RHICmdList.CreateTexture.（迁移旧纹理创建 API 到命令列表接口）
- 2025-05-12 `2f1f89d4` – WmfMedia: Fix for incorrect dx11 decoding using the uncropped image size resulting in duplicated row（修复 DX11 解码未裁剪导致重复行的问题）
- 2025-05-12 `b3cff994` – WmfMedia: Fix for incorrect dx12 decoding using the uncropped image size resulting in green rows at（修复 DX12 解码未裁剪导致绿色条纹的问题）
- 2025-04-23 `6ae57335` – Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i（编译配置调整，增加 DLL 导出存储）

### 维护评价

- **创建时间**：2025-04-23（距今约 5 个月），属于新插件。
- **近期更新**：频繁修复解码渲染问题（DX11/DX12），并持续适配引擎 API 变更。最近一次 commit 在 2025-09-03，表明**活跃维护中**。
- **稳定性**：已知问题均已被修复，解码正确性在 DX11/DX12 下得到保障。
- **推荐程度**：⭐⭐⭐⭐⭐ – 作为 Windows 平台的官方媒体播放器，质量可靠，建议优先使用。适合所有需要播放本地媒体文件的 Windows 项目。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/WmfMedia)
- [官方文档（媒体框架）](https://docs.unrealengine.com/5.4/zh-CN/media-framework-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/WmfMedia/Source/WmfMedia/Private/Tests)
- [媒体播放器蓝图 API 参考](https://docs.unrealengine.com/5.4/en-US/BlueprintAPI/Media/)