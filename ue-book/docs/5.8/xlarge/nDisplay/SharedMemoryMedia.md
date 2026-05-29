# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 多屏同步渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、着色器、配置模板） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterConfiguration` (Runtime), `SharedMemoryMedia` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterWarp` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMultiUser` (Runtime), 等共 30 个模块 |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是一个**虚拟制片（Virtual Production）**核心插件，解决的核心问题是：**将单个 UE 场景的渲染输出同步分配到多台 PC 驱动的多块屏幕上**，支持单目和立体渲染。

具体来说，nDisplay 实现了：

1. **集群同步渲染**：多台 PC（渲染节点）协同工作，各自负责渲染画面的一部分或特定投影角度，所有节点通过帧锁定（Frame Lock）或 Genlock 保持画面同步
2. **投影映射与变形**：支持 MPCDI 标准的投影配置，处理曲面屏幕（如 LED 墙）、CAVE 系统等复杂投影几何
3. **进程间帧数据传输**：通过 SharedMemoryMedia 子模块，利用**共享内存 + 跨 GPU 纹理**实现超低延迟的帧数据 IPC，避免走网络或磁盘 I/O
4. **ICVFX 工作流**：为 LED Volume 虚拟制片提供 In-Camera VFX 支持，包括 Light Card 管理、色域映射等

> **注意**：此插件默认禁用（`EnabledByDefault: false`），需要在项目设置中手动启用。

## 使用场景

- 你在搭建 **LED Volume 虚拟摄影棚**，需要多台渲染 PC 驱动 LED 墙的不同区域 → 用 nDisplay
- 你在搭建 **CAVE 沉浸式环境**，需要多面投影同步 → 用 nDisplay
- 你需要将渲染画面通过**共享内存**低延迟地传输给同一台机器上的另一个 UE 进程 → 用 SharedMemoryMedia
- 你需要在多台 PC 之间进行 **ICVFX 摄像机内特效**拍摄 → 用 nDisplay
- 你需要通过 **Movie Pipeline** 离线渲染多屏合成输出 → 用 nDisplay 的 MoviePipeline 模块

## 蓝图用法

基于 SharedMemoryMedia 子模块源码分析，以下是最常用的蓝图接口：

### 核心类与枚举

| 类/枚举 | 说明 |
|---|---|
| `USharedMemoryMediaOutput` | 媒体输出，定义共享内存名称和纹理参数 |
| `USharedMemoryMediaSource` | 媒体源，定义接收模式和唯一名称 |
| `ESharedMemoryMediaSourceMode` | 接收模式枚举：Framelocked / Genlocked / Freerun |

### SharedMemoryMediaOutput 属性

| 属性 | 类型 | 说明 |
|---|---|---|
| `UniqueName` | `FString` | 共享内存唯一标识名，必须与 MediaSource 中的一致 |
| `bInvertAlpha` | `bool` | 是否反转 Alpha 通道 |
| `bCrossGpu` | `bool` | 是否跨 GPU 共享纹理（禁用可提升性能） |

### SharedMemoryMediaSource 属性

| 属性 | 类型 | 说明 |
|---|---|---|
| `UniqueName` | `FString` | 共享内存唯一标识名，必须与 MediaOutput 中的一致 |
| `Mode` | `ESharedMemoryMediaSourceMode` | 接收模式 |
| `bZeroLatency` | `bool` | 零延迟模式（仅 FrameLocked 模式下生效，可能影响帧率） |

### 接收模式说明

| 模式 | 说明 | 推荐场景 |
|---|---|---|
| `Framelocked` | 匹配源帧号和本地帧号 | **nDisplay 渲染节点必须使用此模式** |
| `Genlocked` | 不匹配帧号，但不跳帧，发送端更快时会被拖慢 | Genlock 同步环境 |
| `Freerun` | 始终抓取最新帧，过快时可能跳帧 | 非同步场景 |

### 使用示例（蓝图描述）

**发送端（Media Capture）**：
1. 创建一个 `SharedMemoryMediaOutput` 资产，设置 `UniqueName` 为 `"MyCluster"`，`bCrossGpu` 为 `true`
2. 在蓝图中使用 `Media Capture` 节点绑定该 Output 和一个 `SceneCaptureComponent2D`
3. 调用 `Start Capture` 开始捕获

**接收端（Media Player）**：
1. 创建一个 `SharedMemoryMediaSource` 资产，设置 `UniqueName` 为 `"MyCluster"`（与发送端一致），`Mode` 设为 `Framelocked`
2. 在 Media Player 组件中打开该 Source 即可接收帧数据

## C++ 用法

### 头文件引入

```cpp
// 媒体输出
#include "SharedMemoryMediaOutput.h"

// 媒体源
#include "SharedMemoryMediaSource.h"

// 媒体捕获
#include "SharedMemoryMediaCapture.h"
```

### 基本用法

创建并配置共享内存媒体输出（发送端）：

```cpp
#include "SharedMemoryMediaOutput.h"
#include "SharedMemoryMediaCapture.h"

// 创建共享内存媒体输出
USharedMemoryMediaOutput* MediaOutput = NewObject<USharedMemoryMediaOutput>();
MediaOutput->UniqueName = TEXT("MyCluster");
MediaOutput->bInvertAlpha = true;
MediaOutput->bCrossGpu = true;

// 验证配置
FString FailureReason;
bool bValid = MediaOutput->Validate(FailureReason);

// 创建媒体捕获实例并启动
UMediaCapture* Capture = MediaOutput->CreateMediaCapture();
if (Capture)
{
    Capture->CaptureSceneViewport(nullptr);  // 绑定到当前视口
}
```

### 进阶用法

配置接收端媒体源，使用不同的同步模式：

```cpp
#include "SharedMemoryMediaSource.h"

// FrameLock 模式（nDisplay 渲染节点推荐）
USharedMemoryMediaSource* Source = NewObject<USharedMemoryMediaSource>();
Source->UniqueName = TEXT("MyCluster");
Source->Mode = ESharedMemoryMediaSourceMode::Framelocked;
Source->bZeroLatency = true;

// 验证源配置
bool bSourceValid = Source->Validate();

// 获取 URL 用于 Media Player 打开
FString Url = Source->GetUrl();
```

### 平台特定扩展

SharedMemoryMedia 使用工厂模式支持多 RHI 平台：

```cpp
#include "SharedMemoryMediaPlatform.h"

// 获取平台工厂实例
FSharedMemoryMediaPlatformFactory* Factory = FSharedMemoryMediaPlatformFactory::Get();

// 创建当前 RHI 对应的平台实现
TSharedPtr<FSharedMemoryMediaPlatform> Platform = 
    Factory->CreateInstanceForRhi(GDynamicRHI->GetInterfaceType());

// 使用平台抽象创建共享纹理
FTextureRHIRef Texture = Platform->CreateSharedTexture(
    EPixelFormat::PF_B8G8R8A8, 
    true,       // sRGB
    1920, 1080, // 尺寸
    FGuid::NewGuid(), 
    0,          // Buffer Index
    true        // Cross-GPU
);
```

## Demo 示例

以下是一个完整的共享内存媒体捕获器最小示例，展示如何在运行时通过 C++ 设置发送端和接收端：

### SharedMemoryMediaDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "SharedMemoryMediaDemo.generated.h"

class USharedMemoryMediaOutput;
class USharedMemoryMediaSource;
class UMediaCapture;
class UMediaPlayer;
class UMediaTexture;

UCLASS(ClassGroup=(Media), meta=(BlueprintSpawnableComponent))
class USharedMemoryMediaDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    USharedMemoryMediaDemoComponent();

    /** 启动媒体捕获（发送端） */
    UFUNCTION(BlueprintCallable, Category = "SharedMemoryMedia")
    bool StartCapture(const FString& UniqueName);

    /** 停止媒体捕获 */
    UFUNCTION(BlueprintCallable, Category = "SharedMemoryMedia")
    void StopCapture();

    /** 打开媒体源进行接收 */
    UFUNCTION(BlueprintCallable, Category = "SharedMemoryMedia")
    bool OpenSource(const FString& UniqueName, ESharedMemoryMediaSourceMode Mode);

protected:
    virtual void BeginDestroy() override;

    UPROPERTY()
    TObjectPtr<USharedMemoryMediaOutput> MediaOutput;

    UPROPERTY()
    TObjectPtr<UMediaCapture> MediaCapture;

    UPROPERTY()
    TObjectPtr<USharedMemoryMediaSource> MediaSource;

    UPROPERTY()
    TObjectPtr<UMediaPlayer> MediaPlayer;

    UPROPERTY()
    TObjectPtr<UMediaTexture> MediaTexture;
};
```

### SharedMemoryMediaDemo.cpp

```cpp
#include "SharedMemoryMediaDemo.h"

#include "SharedMemoryMediaOutput.h"
#include "SharedMemoryMediaSource.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"

USharedMemoryMediaDemoComponent::USharedMemoryMediaDemoComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

bool USharedMemoryMediaDemoComponent::StartCapture(const FString& UniqueName)
{
    // 创建输出配置
    MediaOutput = NewObject<USharedMemoryMediaOutput>(this);
    MediaOutput->UniqueName = UniqueName;
    MediaOutput->bInvertAlpha = true;
    MediaOutput->bCrossGpu = true;

    // 验证
    FString FailureReason;
    if (!MediaOutput->Validate(FailureReason))
    {
        UE_LOG(LogTemp, Error, TEXT("SharedMemoryMedia Output 验证失败: %s"), *FailureReason);
        return false;
    }

    // 创建并启动捕获
    MediaCapture = MediaOutput->CreateMediaCapture();
    if (!MediaCapture.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("无法创建 MediaCapture"));
        return false;
    }

    UE_LOG(LogTemp, Log, TEXT("SharedMemoryMedia 捕获已启动: %s"), *UniqueName);
    return true;
}

void USharedMemoryMediaDemoComponent::StopCapture()
{
    if (MediaCapture.IsValid())
    {
        MediaCapture->StopCapture(true);
        MediaCapture = nullptr;
    }
    MediaOutput = nullptr;
}

bool USharedMemoryMediaDemoComponent::OpenSource(const FString& UniqueName, 
    ESharedMemoryMediaSourceMode Mode)
{
    // 创建媒体源
    MediaSource = NewObject<USharedMemoryMediaSource>(this);
    MediaSource->UniqueName = UniqueName;
    MediaSource->Mode = Mode;
    MediaSource->bZeroLatency = (Mode == ESharedMemoryMediaSourceMode::Framelocked);

    if (!MediaSource->Validate())
    {
        UE_LOG(LogTemp, Error, TEXT("SharedMemoryMedia Source 验证失败"));
        return false;
    }

    // 创建媒体播放器和纹理
    MediaPlayer = NewObject<UMediaPlayer>(this);
    MediaTexture = NewObject<UMediaTexture>(this);
    MediaTexture->SetMediaPlayer(MediaPlayer);

    // 打开源
    FString Url = MediaSource->GetUrl();
    bool bOpened = MediaPlayer->OpenUrl(Url);

    if (bOpened)
    {
        UE_LOG(LogTemp, Log, TEXT("SharedMemoryMedia 源已打开: %s, 模式: %d"), 
            *UniqueName, static_cast<int32>(Mode));
    }

    return bOpened;
}

void USharedMemoryMediaDemoComponent::BeginDestroy()
{
    StopCapture();
    if (MediaPlayer)
    {
        MediaPlayer->Close();
    }
    Super::BeginDestroy();
}
```

## 模块依赖

SharedMemoryMedia 子模块的依赖：

| 模块 | 用途 |
|---|---|
| `D3D12RHI` | D3D12 跨 GPU 共享纹理的创建与管理 |

DisplayCluster 核心模块的特殊依赖：

| 模块 | 用途 |
|---|---|
| `LevelEditor` | 编辑器内 nDisplay 配置面板集成 |
| `EditorWidgets` | 编辑器自定义控件（配置界面） |
| `ScalableMPCDI` | MPCDI（Multi-Primary Configurable Display Infrastructure）投影格式支持（External 模块） |

> 大部分子模块的 Build.cs 文件未提供完整依赖列表。实际开发中，请参考各子模块的 `.Build.cs` 文件确认具体依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | MovieGraph 支持 EXR 多层输出 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | MoviePipeline 合并 WarpBlendAlpha 到 WarpBlend 模式 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 摄像机命名和 MPCDI/ICVFX 着色器不透明 Alpha 问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 输出帧编码回退时正确处理非默认 DisplayGamma |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理小于视口尺寸时的闪烁问题 |

### 维护评价

**活跃维护** ⭐⭐⭐⭐⭐

- **创建时间**：2018 年（约 8 年历史），是 UE 虚拟制片的基石插件
- **更新频率**：2026 年 5 月仍有密集更新（一周内 5 次提交），包含新功能（EXR 多层）和 Bug 修复
- **代码规模**：1351 个源文件，30 个模块，是 UE 中最大的插件之一
- **维护团队**：由 Epic Games 官方维护，虚拟制片是 UE 的战略方向
- **成熟度**：已广泛应用于 LED Volume、CAVE 等实际项目，非实验性

**强烈推荐使用**。如果你的项目涉及多屏渲染、虚拟制片或 LED Volume，nDisplay 是官方唯一的解决方案，且持续获得活跃更新和功能增强。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- 官方文档：[nDisplay Overview](https://docs.unrealengine.com/en-US/RenderingAndGraphics/nDisplay/Overview/)（未在 .uplugin 中提供，请参考官方文档站）
- 测试用例：`Source/DisplayClusterTests/`（插件内含专用测试模块）