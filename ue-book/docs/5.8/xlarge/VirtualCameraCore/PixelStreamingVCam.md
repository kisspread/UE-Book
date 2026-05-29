# VirtualCameraCore

> Code for actors, components, and utilities for controlling and viewing cameras via physical devices. See VirtualCamera for content.

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟相机核心 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、插件内容） |
| 模块 | `DecoupledOutputProvider` (Runtime), `PixelStreamingVCam` (Runtime), `VCamBlueprintNodes` (Runtime), `VCamCore` (Runtime), `VCamCoreEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-18 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualCameraCore) | |

## 用途

`VirtualCameraCore` 是虚拟相机系统的**核心逻辑与基础设施模块**。它提供了一套可扩展的框架，用于将物理设备（如手机、平板、专业控制器）的输入映射到虚幻引擎内的虚拟相机，并实时预览/渲染相机画面。其核心价值在于将**相机控制逻辑、数据传输和最终输出**解耦，使得同一套控制逻辑可以适配不同的输出目标，例如通过 **Pixel Streaming** 实现远程预览和控制，或对接 **Live Link** 系统。

## 使用场景

-   **远程实时预览**：导演在平板电脑上通过 VirtualCamera 应用（如 Epic 的 VCAM app）实时查看并调整场景中的虚拟相机，而无需靠近运行虚幻引擎的工作站。
-   **多设备协作拍摄**：多个设备同时连接到同一个虚幻引擎实例，分别控制不同的虚拟相机，用于现场虚拟制片（Virtual Production）。
-   **自定义输入设备集成**：开发者可以基于 `VCamCore` 框架，为特定的硬件控制器（如跟踪摄像机、游戏手柄）编写适配逻辑。
-   **自动化测试与回放**：利用其模块化的设计，可以录制设备的输入数据并在测试中回放，实现相机运动的自动化验证。

## 蓝图用法

`VirtualCameraCore` 的蓝图节点主要分布在其子模块中。`VCamCore` 和 `VCamBlueprintNodes` 模块提供了核心的蓝图接口。`PixelStreamingVCam` 模块则提供了与像素流相关的蓝图功能。

### 核心节点

由于提供的代码分析主要集中在 `PixelStreamingVCam` 模块，以下为该模块中可能暴露的关键蓝图接口（基于 `UVCamPixelStreamingSubsystem` 和 `UVCamPixelStreamingSession` 等类推断）：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `获取像素流子系统` | 获取管理所有像素流会话的单例子系统。 | `UVCamPixelStreamingSubsystem` |
| `注册/注销会话` | 将一个像素流会话注册到子系统以进行管理。 | `UVCamPixelStreamingSubsystem` |
| `启动/停止信令服务器` | 根据需要自动管理内置信令服务器的生命周期。 | `UVCamPixelStreamingSubsystem` |

**使用示例（蓝图描述）**
1.  创建一个 `UVCamPixelStreamingSession` 对象。
2.  通过 `UVCamPixelStreamingSubsystem::Get()` 节点获取子系统实例。
3.  调用 `RegisterActiveOutputProvider` 节点，将会话注册到子系统。
4.  配置会话的属性（如 Streamer ID）。
5.  当会话激活时，系统会自动通过 `PixelStreaming` 开始推流，并通过 `Live Link` 发布变换数据。

## C++ 用法

`PixelStreamingVCam` 模块的核心逻辑封装在 `UVCamPixelStreamingSubsystem` 和 `FVCamPixelStreamingSessionLogic` 中。

### 头文件引入

```cpp
#include "PixelStreamingVCamModule.h"
#include "VCamPixelStreamingSubsystem.h"
#include "VCamPixelStreamingSession.h" // 假设存在
#include "Media/PixelStreamingMediaOutput.h"
```

### 基本用法

以下示例展示了如何在 C++ 中管理一个像素流会话的生命周期，基于 `VCamPixelStreamingSessionLogic.h` 中的逻辑。

```cpp
// 1. 获取子系统并注册会话
UVCamPixelStreamingSubsystem* Subsystem = UVCamPixelStreamingSubsystem::Get();
if (Subsystem)
{
    // 假设 PixelStreamingSession 是已创建的 UVCamPixelStreamingSession 实例
    Subsystem->RegisterActiveOutputProvider(PixelStreamingSession);
}

// 2. 会话激活时，逻辑内部会自动设置 Capture 和 Streamer
// 你可以监听会话的事件来获取状态变化
// 例如，当流媒体捕获状态改变时会触发 OnCaptureStateChanged
```

**来源**: `Private/VCamPixelStreamingSessionLogic.h`

### 进阶用法

集成 Live Link 功能，将远程设备的控制数据发布为 Live Link Subject。

```cpp
// 在注册会话后，子系统会通过 FLiveLinkManager 自动管理 Live Link Subject
// 你需要将接收到的变换数据推送给它
if (Subsystem && PixelStreamingSession)
{
    FTransform DeviceTransform = GetTransformFromDevice(); // 从设备获取的变换
    double Timestamp = FPlatformTime::Seconds();
    
    // 将变换数据推送到关联的 Live Link Subject
    Subsystem->PushTransformForSubject(*PixelStreamingSession, DeviceTransform, Timestamp);
}
```

**来源**: `Private/LiveLink/LiveLinkManager.h`, `Private/VCamPixelStreamingSubsystem.h`

## Demo 示例

一个最小化的 C++ 示例，演示如何创建并管理一个 `UVCamPixelStreamingSession`。

**VCamPixelStreamingDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "VCamPixelStreamingDemo.generated.h"

class UVCamPixelStreamingSession;
class UVCamPixelStreamingSubsystem;

UCLASS()
class AVCamPixelStreamingDemo : public AActor
{
    GENERATED_BODY()
    
public:
    AVCamPixelStreamingDemo();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UPROPERTY(Transient)
    TObjectPtr<UVCamPixelStreamingSession> StreamingSession;

    UFUNCTION(BlueprintCallable, Category = "Demo")
    void StartPixelStreaming();

    UFUNCTION(BlueprintCallable, Category = "Demo")
    void StopPixelStreaming();
};
```

**VCamPixelStreamingDemo.cpp**
```cpp
#include "VCamPixelStreamingDemo.h"
#include "VCamPixelStreamingSubsystem.h"
#include "VCamPixelStreamingSession.h"

AVCamPixelStreamingDemo::AVCamPixelStreamingDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AVCamPixelStreamingDemo::BeginPlay()
{
    Super::BeginPlay();
    // 自动开始流式传输
    StartPixelStreaming();
}

void AVCamPixelStreamingDemo::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    StopPixelStreaming();
    Super::EndPlay(EndPlayReason);
}

void AVCamPixelStreamingDemo::StartPixelStreaming()
{
    UVCamPixelStreamingSubsystem* Subsystem = UVCamPixelStreamingSubsystem::Get();
    if (Subsystem && !StreamingSession)
    {
        // 创建一个新的像素流会话（实际创建方式可能更复杂，需通过工厂或资产）
        StreamingSession = NewObject<UVCamPixelStreamingSession>(this);
        if (StreamingSession)
        {
            // 配置StreamerId等属性
            StreamingSession->SetStreamerId(FString::Printf(TEXT("VCam_Demo_%s"), *GetName()));
            // 注册到子系统进行管理
            Subsystem->RegisterActiveOutputProvider(StreamingSession);
            // 会话内部逻辑将在激活时自动处理捕获和推流
            StreamingSession->Activate();
        }
    }
}

void AVCamPixelStreamingDemo::StopPixelStreaming()
{
    UVCamPixelStreamingSubsystem* Subsystem = UVCamPixelStreamingSubsystem::Get();
    if (Subsystem && StreamingSession)
    {
        Subsystem->UnregisterActiveOutputProvider(StreamingSession);
        StreamingSession = nullptr;
    }
}
```

## 模块依赖

`PixelStreamingVCam` 模块（当前分析的模块）的 Build.cs 文件指定了以下依赖：
*注意：根据要求，此处省略了 Core, CoreUObject, Engine 等常见依赖。*

| 模块 | 用途 |
|---|---|
| `LevelEditor` | 提供编辑器关卡视口相关功能。 |
| `UnrealEd` | 提供编辑器扩展和资产定义等功能。 |
| **Pixel Streaming 相关模块** | (在实际构建中会依赖，但在提供的 Build.cs 片段中未明确列出) |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `876d5541` | Fix the crash with PIE/Simulate | 修复了在“PIE/模拟”模式下发生的崩溃问题。 |
| 2026-05-12 | `d6533f70` | Virtual Production: Fixed warning regarding EngineAssetDefinitions plugin not being included... | 修复了与“引擎资产定义”插件未包含相关的警告。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories... | 将多个虚拟制片资产迁移至新的资产分类目录。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏 `UE_LOG` 迁移为新的 `UE_LOGF` 格式。 |
| 2026-03-09 | `8afaf39f` | Move UVPFullScreenWidget into new non-experimental plugin... | 将全屏控件资产移出实验性插件，进入正式的视口覆盖插件。 |

### 维护评价

- **活跃维护**：最近半年内有多次实质性更新，包括功能改进（资产迁移）、Bug修复（PIE崩溃）和代码现代化（日志宏迁移）。
- **重要性**：作为虚拟制片工作流的核心组件，Epic Games 有动力持续维护和改进它。
- **实验性状态**：插件元数据标记为 `IsBetaVersion = true`，表明它虽然功能强大，但API和行为可能在未来版本中发生变化。
- **推荐**：**推荐使用**，特别是对于需要远程控制虚拟相机或进行多设备协作的项目。建议密切关注其API更新日志，因为它是测试版软件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualCameraCore)
- 官方文档：无（`.uplugin` 中 DocsURL 为空）
- [PixelStreamingVCam 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualCameraCore/Source/PixelStreamingVCam)