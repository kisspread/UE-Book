# AVF Media Player

> Implements a media player using Apple AV Foundation.

| 属性 | 值 |
|---|---|
| 中文名 | AVF媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AvfMedia` (RuntimeNoCommandlet), `AvfMediaCapture` (RuntimeNoCommandlet), `AvfMediaEditor` (Editor), `AvfMediaFactory` (Editor), `AvfMediaFactory` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2025-04-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AvfMedia) | |

## 用途

该插件利用 Apple 的 AV Foundation 框架为 UE5 提供原生的媒体播放能力，支持 iOS、macOS 和 tvOS 平台。它包含两个核心播放器：  
- **AvfMedia**：标准媒体文件播放器，支持本地视频文件、流媒体等。  
- **AvfMediaCapture**：摄像头/麦克风实时捕获播放器（仅 iOS/Mac），用于将设备摄像头画面或麦克风音频以媒体流形式输入引擎。

此外还提供编辑器工厂模块（`AvfMediaFactory`）使编辑器能够识别并创建对应的媒体播放器实例，以及一个编辑器模块（`AvfMediaEditor`）用于在编辑器中设置捕获设备参数（如选择摄像头、帧率等）。

该插件解决了在 Apple 平台上需要高效、原生硬件加速的媒体回放与捕获需求，并利用 AV Foundation 的零拷贝、Metal 纹理共享等特性获得最佳性能。

## 使用场景

- 在 iOS 或 macOS 应用中播放本地或远程视频文件 → 使用 **AvfMedia** 播放器（通过标准 `MediaPlayer` 蓝图节点）。
- 在 iOS 或 macOS 应用中实时预览摄像头画面或录制麦克风音频 → 使用 **AvfMediaCapture** 播放器（需 C++ 代码初始化）。
- 在编辑器中调试视频播放或摄像头捕获 → 通过 `MediaPlayer` actor 并选择 "AVF Media Player" 作为播放器，或使用 `AvfMediaEditor` 提供的捕获设备选择 UI。
- 开发 AR/VR 应用需要实时相机输入 → 结合 `SceneCapture` 或 `MediaTexture` 将摄像头画面渲染到材质上。

## 蓝图用法

该插件**不直接暴露**任何 `BlueprintCallable` 函数。所有媒体播放操作均通过引擎标准的 **Media Framework** 蓝图节点实现：

| 节点 | 说明 | 所属类 |
|---|---|---|
| `Open Source` | 打开媒体源（URL 或设备名称） | `MediaPlayer` |
| `Get Video Track` | 获取视频轨道信息 | `MediaPlayer` |
| `Play` / `Pause` | 播放/暂停 | `MediaPlayer` |
| `Create Media Texture` | 将视频帧绑定到材质 | `MediaTexture` / `MediaPlayer` |

**使用示例（蓝图）**：  
1. 添加 `MediaPlayer` 组件。  
2. 调用 `Open Source`，Source 选择 "AVF Media Player"，URL 填 `file:///path/to/video.mp4`（文件）或设备 UID（捕获模式）。  
3. 创建 `MediaTexture` 并关联该 `MediaPlayer`，将材质输出到 UI 或 3D 对象。  
4. 调用 `Play` 即可播放。

> **注意**：`AvfMediaCapture` 捕获播放器要求以 `capture://` 协议打开，URL 格式为 `capture://摄像头设备UID`（音频为 `capture://audio`）。需在 C++ 中查询可用设备列表，蓝图无法直接枚举设备。

## C++ 用法

### 头文件引入

```cpp
// 使用标准媒体框架
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "MediaSoundComponent.h"

// 使用 AvfMediaCapture 专用接口
#include "AvfMediaCapturePlayer.h"
#include "AvfMediaCaptureHelper.h"   // 权限与设备枚举
```

### 基本用法：播放视频文件

```cpp
// 创建 MediaPlayer 并打开 AVF 媒体源
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
MediaPlayer->SetLooping(false);

// 使用 AvfMediaFactory 自动选择合适的播放器
MediaPlayer->OpenSource("file:///var/mobile/Media/example.mp4");
MediaPlayer->Play();
```

来源：`Engine/Plugins/Media/AvfMedia/Source/AvfMedia/Private/Player/AvfMediaPlayer.cpp`（推断）

### 进阶用法：实时摄像头捕获

```cpp
// 1. 请求摄像头权限
EAvfMediaCaptureAuthStatus Auth = [AvfMediaCaptureHelper authorizationStatusForMediaType:AVMediaTypeVideo];
if (Auth == EAvfMediaCaptureAuthStatus::NotDetermined)
{
    [AvfMediaCaptureHelper requestAccessForMediaType:AVMediaTypeVideo completionCallback:^(EAvfMediaCaptureAuthStatus NewAuth){
        // 权限结果回调
    }];
}

// 2. 创建并打开捕获播放器
TSharedPtr<FAvfMediaCapturePlayer, ESPMode::ThreadSafe> CapturePlayer = MakeShared<FAvfMediaCapturePlayer>(EventSink);
const FString DeviceURL = TEXT("capture://FrontCameraUID_From_Enumeration"); // 可从 [AVCaptureDevice devicesWithMediaType:AVMediaTypeVideo] 获取
CapturePlayer->Open(DeviceURL, nullptr);

// 3. 通过 IMediaSamples 获取视频帧样本（在 Tick 或回调中）
IMediaSamples& Samples = CapturePlayer->GetSamples();
TSharedPtr<IMediaTextureSample, ESPMode::ThreadSafe> Sample;
while (Samples.FetchVideo(FTimespan::Zero(), Sample))
{
    // 使用 Sample->GetBuffer() 获取纹理数据
}

// 4. 停止捕获
CapturePlayer->Close();
```

来源：`Engine/Plugins/Media/AvfMedia/Source/AvfMediaCapture/Private/Player/AvfMediaCapturePlayer.h`、`AvfMediaCaptureHelper.h`

### 权限处理

`AvfMediaCaptureHelper` 提供了便捷的权限状态查询与申请：

```cpp
// 检查麦克风权限
EAvfMediaCaptureAuthStatus AudioAuth = [AvfMediaCaptureHelper authorizationStatusForMediaType:AVMediaTypeAudio];

// 请求权限（若未决定则弹窗）
[AvfMediaCaptureHelper requestAccessForMediaType:AVMediaTypeVideo completionCallback:^(EAvfMediaCaptureAuthStatus Status){
    if (Status == EAvfMediaCaptureAuthStatus::Authorized)
    {
        // 开始捕获
    }
}];
```

注意：调用 `requestAccessForMediaType:completionCallback:` 会立即返回并异步回调；若已授权则直接回调。

## Demo 示例

以下是一个最小化的 C++ `AMediaPlayerActor`，演示如何使用 `AvfMediaCapturePlayer` 捕获摄像头并输出到 `MediaTexture`：

```cpp
// CaptureActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "AvfMediaCapturePlayer.h"
#include "CaptureActor.generated.h"

UCLASS()
class ACaptureActor : public AActor
{
    GENERATED_BODY()

public:
    ACaptureActor();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
    virtual void Tick(float DeltaTime) override;

private:
    TSharedPtr<FAvfMediaCapturePlayer, ESPMode::ThreadSafe> CapturePlayer;
    UPROPERTY()
    UMediaTexture* CameraTexture;
};
```

```cpp
// CaptureActor.cpp
#include "CaptureActor.h"
#include "IMediaEventSink.h"
#include "IMediaSamples.h"
#include "IMediaTextureSample.h"

ACaptureActor::ACaptureActor()
{
    PrimaryActorTick.bCanEverTick = true;
    CameraTexture = CreateDefaultSubobject<UMediaTexture>(TEXT("CameraTexture"));
}

void ACaptureActor::BeginPlay()
{
    Super::BeginPlay();

    // 请求权限（简化：假设已授权）
    [AvfMediaCaptureHelper requestAccessForMediaType:AVMediaTypeVideo
         completionCallback:^(EAvfMediaCaptureAuthStatus Status) {
        if (Status == EAvfMediaCaptureAuthStatus::Authorized)
        {
            // 在游戏线程中执行
            AsyncTask(ENamedThreads::GameThread, [this]()
            {
                IMediaEventSink& DummySink = *((IMediaEventSink*)FMemory::Malloc(sizeof(IMediaEventSink)));
                CapturePlayer = MakeShared<FAvfMediaCapturePlayer, ESPMode::ThreadSafe>(DummySink);
                // 打开第一个摄像头（实际应枚举）
                if (CapturePlayer->Open(TEXT("capture://"), nullptr))
                {
                    CameraTexture->SetMediaPlayer(/* 需要转换成 UMediaPlayer */);
                    CapturePlayer->GetSamples(); // 开始接收帧
                }
            });
        }
    }];
}

void ACaptureActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (CapturePlayer.IsValid())
    {
        CapturePlayer->Close();
        CapturePlayer.Reset();
    }
    Super::EndPlay(EndPlayReason);
}

void ACaptureActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    // 渲染循环由 MediaTexture 自动驱动，无需手动处理帧获取
}
```

> 注意：上述代码为演示目的，实际使用需处理 `IMediaEventSink` 虚函数实现、UMediaPlayer 包装等细节。建议直接使用内置的 `UMediaPlayer` + 对应 URL 即可简化操作。

## 模块依赖

以下模块除标准 Core/Engine 外，使用 `AvfMediaCapture` 时需额外依赖：

| 模块 | 用途 |
|---|---|
| `Media` | 提供 `IMediaPlayer`、`IMediaSamples` 等接口 |
| `MediaUtils` | 辅助工具（如 FMediaPlayerFacade） |
| `MediaAssets` | 提供 `UMediaPlayer`、`UMediaTexture` 等资产类 |
| `ApplicationCore` | 提供平台回调与线程管理 |
| `RHI` | 纹理共享（Metal 纹理） |
| `RenderCore` | 渲染线程同步 |

- `AvfMedia` 核心模块依赖与 `AvfMediaCapture` 类似，增加了 `MediaCodecs` 等。
- 编辑器模块 `AvfMediaEditor` 额外依赖 `UnrealEd`、`PropertyEditor`。
- 工厂模块 `AvfMediaFactory` 通常依赖 `MediaAssets` 和 `CoreUObject`。

## 维护状态

### 近期更新

- 2025-06-26 `d2ec2238` Generalized IOSAsyncTask to AppleAsyncTask in preparation for using WebKit in the macOS WebBrowser e
- 2025-06-02 `2c095ca4` Replace EBulkDataType in MetalRHI with Metal-specific RHI functions
- 2025-05-06 `5243d97b` Merging //UE5/Dev-ParallelRendering to Main (//UE5/Main)
- 2025-04-23 `6ae57335` Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i
- 2025-04-10 `ea97db60` Movie Render Queue: High-res tiling support for paging scene view state persistent data to system m

### 维护评价

该插件于 2025 年 4 月创建（初始提交），至今约 3 个月。最近更新集中在 2025 年 6 月，属于活跃维护期。更新内容涉及通用异步任务重构和 MetalRHI 调整，均为功能性改进，反映了团队对 Apple 平台的持续支持。  
**无明显已知问题或弃用警告**，推荐在项目中用于 Apple 平台的媒体播放与捕获。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AvfMedia)
- [官方文档（论坛讨论帖）](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AvfMedia/Tests)（未提供，推断路径）