# Live Link XR

> Live Link plugin for using XR tracked devices

| 属性 | 值 |
|---|---|
| 中文名 | XR 追踪源 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveLinkXR` (Runtime), `LiveLinkXROpenXRExt` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-06-23 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkXR) | |

## 用途

LiveLinkXR 是 Unreal Engine Live Link 系统与 OpenXR 运行时之间的桥梁插件。它将 XR 追踪设备（头显 HMD、手柄 Controller、全身追踪器 Tracker Puck）的位置和旋转数据实时导入 Live Link，使得虚拟制片、动作捕捉、虚拟摄像机等工作流可以消费 XR 设备的追踪数据。

该插件解决的核心问题是：**在不编写自定义 OpenXR 扩展代码的情况下，通过标准 Live Link 协议将任意 OpenXR 追踪设备的数据暴露给引擎其他系统**。

插件默认未启用且处于 Beta 状态，说明它面向的是虚拟制片领域的专业用户，而非通用项目。

## 使用场景

- 你在做虚拟制片，需要将 HTC Vive Tracker（追踪器）绑定到真实摄像机上做虚拟摄像机追踪 → 用 LiveLinkXR
- 你需要将多个 XR 控制器的实时位姿数据通过 Live Link 分发给动画蓝图或 MetaHuman → 用 LiveLinkXR
- 你在做混合现实拍摄，需要同时获取 HMD、手柄和多个 Tracker Puck 的追踪数据 → 配置 `FLiveLinkXRConnectionSettings` 分别开启
- 你需要以自定义频率采样 XR 追踪数据（如 120Hz 用于快速运动） → 设置 `LocalUpdateRateInHz`

## 蓝图用法

本插件不提供 `BlueprintCallable` 节点。所有配置通过 **Live Link 面板 UI** 或 **C++ 代码**完成。

### 配置界面

在编辑器中通过 Live Link 面板创建源：

1. 打开 **Window → Live Link**
2. 点击 **Source → Live Link XR**
3. 在弹出面板中配置连接设置

| 配置项 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bTrackTrackers` | `bool` | `true` | 追踪所有 Tracker Puck |
| `bTrackControllers` | `bool` | `false` | 追踪所有手柄 |
| `bTrackHMDs` | `bool` | `false` | 追踪所有头显 |
| `LocalUpdateRateInHz` | `uint32` | `60` | 追踪数据采样率 (Hz)，范围 1-1000 |

> `bTrackHMDs` 和 `bTrackControllers` 默认关闭，因为 HMD 和手柄通常已被引擎自身的 XR 系统消费，重复导入会造成冲突。典型用法是仅开启 Tracker Puck。

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkXR.h"
#include "LiveLinkXRSource.h"
#include "LiveLinkXRConnectionSettings.h"
#include "LiveLinkXRSourceSettings.h"
```

### 基本用法

通过代码创建 Live Link XR 数据源，连接 OpenXR 追踪设备。

```cpp
// Source/LiveLinkXR/Public/LiveLinkXRSource.h
#include "LiveLinkXRSource.h"
#include "LiveLinkXRConnectionSettings.h"

// 配置连接参数：只追踪 Tracker Puck，采样率 90Hz
FLiveLinkXRConnectionSettings ConnectionSettings;
ConnectionSettings.bTrackTrackers = true;
ConnectionSettings.bTrackControllers = false;
ConnectionSettings.bTrackHMDs = false;
ConnectionSettings.LocalUpdateRateInHz = 90;

// 创建 XR 数据源
TSharedPtr<FLiveLinkXRSource> XRSource = MakeShared<FLiveLinkXRSource>(ConnectionSettings);

// FLiveLinkXRSource 内部会自行创建线程（FRunnable）来轮询追踪数据
// 数据会通过 LiveLinkClient 自动分发到对应的 Subject
```

### 进阶用法

手动创建并注册源到 Live Link Client，同时修改运行时采样率。

```cpp
#include "LiveLinkXRSource.h"
#include "LiveLinkXRSourceSettings.h"
#include "ILiveLinkClient.h"
#include "LiveLinkModule.h"

// 获取 LiveLink 模块
FLiveLinkModule& LiveLinkModule = FLiveLinkModule::Get();
ILiveLinkClient* Client = LiveLinkModule.GetClient();

if (Client)
{
    // 创建源
    FLiveLinkXRConnectionSettings Settings;
    Settings.bTrackTrackers = true;
    Settings.bTrackControllers = true;
    Settings.bTrackHMDs = false;
    Settings.LocalUpdateRateInHz = 120;

    TSharedPtr<FLiveLinkXRSource> Source = MakeShared<FLiveLinkXRSource>(Settings);

    // 通过工厂注册（或直接通过 Client 添加）
    FGuid SourceGuid = Client->AddSource(Source);

    // 源启动后，可以在运行时通过 SourceSettings 调整采样率
    // 内部使用 std::atomic<uint32> 保证线程安全
    ULiveLinkXRSourceSettings* SourceSettings = NewObject<ULiveLinkXRSourceSettings>();
    SourceSettings->LocalUpdateRateInHz = 240;  // 切换到 240Hz
    Client->SetSourceSettings(SourceGuid, SourceSettings);
}
```

## Demo 示例

一个最小化示例：以编程方式创建 XR 追踪源并在 Tick 中读取追踪状态。

### MyXRTrackerComponent.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MyXRTrackerComponent.generated.h"

class FLiveLinkXRSource;
struct FLiveLinkXRConnectionSettings;

UCLASS(ClassGroup=(VirtualProduction), meta=(BlueprintSpawnableComponent))
class UMyXRTrackerComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyXRTrackerComponent();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    /** 追踪更新频率 */
    UPROPERTY(EditAnywhere, Category="XR Tracker", meta=(ClampMin=1, ClampMax=1000))
    uint32 UpdateRateHz = 60;

    /** 是否追踪手柄 */
    UPROPERTY(EditAnywhere, Category="XR Tracker")
    bool bTrackControllers = false;

private:
    TSharedPtr<FLiveLinkXRSource> XRSource;
};
```

### MyXRTrackerComponent.cpp

```cpp
#include "MyXRTrackerComponent.h"

#include "LiveLinkXRSource.h"
#include "LiveLinkXRConnectionSettings.h"
#include "LiveLinkXR.h"

UMyXRTrackerComponent::UMyXRTrackerComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMyXRTrackerComponent::BeginPlay()
{
    Super::BeginPlay();

    // 配置连接设置
    FLiveLinkXRConnectionSettings ConnectionSettings;
    ConnectionSettings.bTrackTrackers = true;
    ConnectionSettings.bTrackControllers = bTrackControllers;
    ConnectionSettings.bTrackHMDs = false;
    ConnectionSettings.LocalUpdateRateInHz = UpdateRateHz;

    // 创建 XR 数据源，内部自动启动追踪线程
    XRSource = MakeShared<FLiveLinkXRSource>(ConnectionSettings);

    // 源会通过 ReceiveClient 回调自动注册到 Live Link
    // 追踪数据以 FLiveLinkFrameData 的形式分发到对应的 Subject
    UE_LOG(LogLiveLinkXR, Log, TEXT("XR Tracker source started at %u Hz"), UpdateRateHz);
}

void UMyXRTrackerComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (XRSource.IsValid())
    {
        // RequestSourceShutdown 会设置 bStopping 标志，终止追踪线程
        XRSource->RequestSourceShutdown();
        XRSource.Reset();
    }

    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLink` | Live Link 框架核心，提供 `ILiveLinkSource`、`ILiveLinkClient` 等接口 |
| `OpenXR` | OpenXR 运行时接口，获取 XR 设备追踪数据 |
| `OpenXRHMD` | OpenXR HMD 扩展，设备枚举与位姿查询 |
| `LiveLinkInterface` | Live Link 数据类型定义（`FLiveLinkFrameData` 等） |

> 前置插件依赖：`OpenXR`（在 .uplugin 的 Plugins 字段中声明）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 宏 |
| 2025-07-21 | `82674f19` | OpenXR extension names: use openxr.h define rather than hard coding the names. | 使用 openxr.h 宏定义替代硬编码的扩展名称 |
| 2025-03-13 | `b059f7b4` | Fix trivial unreachable code warnings. | 修复不可达代码的编译警告 |
| 2024-10-02 | `7810d15e` | LiveLinkXR: Minor refactor to remove depedency on private header in OpenXRHMD module | 消除对 OpenXRHMD 私有头文件的依赖 |
| 2024-03-22 | `001e4d27` | LiveLinkXR: Remove Linux from supported platforms. | 移除 Linux 平台支持，仅保留 Win64 |

### 维护评价

- **年龄**：约 5 年，自 2020 年创建
- **更新频率**：每 3-6 个月有一次维护性提交，主要是编译修复、依赖清理和日志规范化
- **维护状态**：**维护中但不活跃** — 无功能性更新，仅做代码质量维护
- **Beta 状态**：`.uplugin` 中 `IsBetaVersion=true`，表明 Epic 将其视为未完全稳定的组件
- **平台限制**：2024 年移除了 Linux 支持，目前仅限 Win64
- **已知限制**：5.1 版本废弃了 `EXRTrackedDeviceType` 相关接口

**总体建议**：适合虚拟制片专业工作流使用，但需注意其 Beta 状态。如果你的项目依赖 XR Tracker 追踪数据且运行在 Win64 平台，这是一个有效的现成方案。不建议在生产环境中将其视为核心依赖而不做降级预案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkXR)
- [Live Link 官方文档](https://docs.unrealengine.com/en-US/AnimatingObjects/SkeletalMeshAnimation/LiveLinkPlugin/)