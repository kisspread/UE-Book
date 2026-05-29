# Timed Data Monitor

> Utilities to monitor inputs that can be time synchronized.

| 属性 | 值 |
|---|---|
| 中文名 | 时间数据监控器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TimedDataMonitor` (UncookedOnly), `TimedDataMonitorEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-01-29 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/TimedDataMonitor) | |

## 用途

TimedDataMonitor 插件专为虚拟制作（Virtual Production）工作流设计，用于监控和管理需要精确时间同步的数据输入源，如来自 LiveLink 的摄像机追踪、动作捕捉数据或媒体 I/O 的视频信号。它解决的核心问题是：在复杂的虚拟制片环境中，多个异步数据源需要与引擎的全局时间（如时间码）保持同步，否则会导致画面、声音或动作错位。该插件通过提供一个中央监控子系统（`UTimedDataMonitorSubsystem`）和自动校准工具，使用户能够实时查看各数据通道的连接状态、评估性能（如缓冲区健康度、延迟统计），并能自动调整时间偏移（Offset）以对齐不同源的时间基准。

## 使用场景

- **虚拟制片监控面板**：你在使用 LED 墙幕进行拍摄时，需要监控摄像机追踪数据、视频素材（MediaIO）与引擎渲染之间的同步状态，确保没有丢帧或延迟。
- **多源动作捕捉**：在游戏或动画制作中，多个演员身上的动捕设备数据通过 LiveLink 传入，你需要监控它们的连接状态和时间一致性。
- **复杂实时合成**：你的工作流涉及来自不同硬件（如视频信号发生器、外部传感器）的实时数据，需要确保它们与场景时间对齐，避免画面撕裂或音画不同步。
- **自动时间校准**：你需要工具来自动分析各输入源的时间基准，并计算出一个统一的时间偏移量，以应用到 Timecode Provider 上，简化手动对齐流程。

## 蓝图用法

插件通过 `UTimedDataMonitorSubsystem` 引擎子系统暴露其核心功能，可在蓝图中访问。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get All Inputs` | 获取当前所有已注册的时间数据输入标识符列表。 | `UTimedDataMonitorSubsystem` |
| `Get All Channels` | 获取所有输入下的所有数据通道标识符列表。 | `UTimedDataMonitorSubsystem` |
| `Get Input Connection State` | 获取指定输入下所有通道中最差的连接状态（如“已断开”）。 | `UTimedDataMonitorSubsystem` |
| `Get Channel Evaluation State` | 获取指定通道的数据评估状态（如“无样本”、“在范围内”）。 | `UTimedDataMonitorSubsystem` |
| `Calibrate (Latent)` | 启动一个异步校准流程，尝试自动对齐所有输入的时间。 | `UTimedDataMonitorSubsystem` |
| `Apply Time Correction` | 对指定输入应用一个时间校正参数。 | `UTimedDataMonitorSubsystem` |
| `Set Input Enabled` | 在监控器中启用或禁用对指定输入的监控。 | `UTimedDataMonitorSubsystem` |
| `Get Channel Number Of Samples` | 获取指定通道缓冲区中的样本数量。 | `UTimedDataMonitorSubsystem` |
| `Get Input Evaluation Distance To Newest Sample Mean` | 获取指定输入评估时间与最新样本的平均时间距离（秒）。 | `UTimedDataMonitorSubsystem` |
| `Reset All Buffer Stats` | 重置所有输入的缓冲区统计信息（如丢帧数、溢出数）。 | `UTimedDataMonitorSubsystem` |

### 使用示例（蓝图描述）

1.  **监控连接状态**：在您的 UI 蓝图中，首先调用 `Get All Inputs`。遍历此列表，对每个 `InputIdentifier`，调用 `Get Input Connection State` 获取其连接状态（如 `ETimedDataInputState::Connected`），并更新对应的 UI 指示灯（绿色/红色）。
2.  **检查数据健康度**：选择一个特定的 `ChannelIdentifier`，调用 `Get Channel Evaluation State` 查看其数据是否可用。调用 `Get Channel Buffer Underflow Stat` 和 `Get Channel Buffer Overflow Stat` 来监控缓冲区健康，如果值持续增加，则可能提示需要增加缓冲区大小。
3.  **执行自动校准**：创建一个按钮，其点击事件连接到 `Calibrate (Latent)` 节点。传入一个 `FTimedDataMonitorCalibrationParameters` 结构（可在细节面板中配置重试次数、是否允许缓冲区调整等）。使用 `Latent` 节点，在校准完成后（成功或失败）执行后续逻辑，例如根据 `FTimedDataMonitorCalibrationResult` 显示成功消息或错误详情。

## C++ 用法

### 头文件引入

```cpp
#include "TimedDataMonitorSubsystem.h"
```

### 基本用法

```cpp
// 假设你在一个 UObject（如 GameInstance、Actor 或 Subsystem）中操作
// 通过 GEngine 获取子系统实例
UTimedDataMonitorSubsystem* MonitorSubsystem = GEngine->GetEngineSubsystem<UTimedDataMonitorSubsystem>();
if (MonitorSubsystem)
{
    // 1. 获取所有输入标识符
    TArray<FTimedDataMonitorInputIdentifier> AllInputs = MonitorSubsystem->GetAllInputs();

    // 2. 检查第一个输入的连接状态
    if (AllInputs.Num() > 0)
    {
        const FTimedDataMonitorInputIdentifier& FirstInput = AllInputs[0];
        ETimedDataInputState ConnectionState = MonitorSubsystem->GetInputConnectionState(FirstInput);
        UE_LOG(LogTemp, Log, TEXT("Input 0 Connection State: %s"), *UEnum::GetValueAsString(ConnectionState));
    }

    // 3. 设置某个输入的缓冲区大小
    if (AllInputs.Num() > 0)
    {
        const FTimedDataMonitorInputIdentifier& FirstInput = AllInputs[0];
        MonitorSubsystem->SetInputDataBufferSize(FirstInput, 5); // 设置缓冲区大小为5帧
    }
}
```
*（基础操作代码）*

### 进阶用法

```cpp
// 异步校准示例（例如在某个自定义的编辑器工具中）
#include "TimedDataMonitorCalibration.h"

void UMyEditorUtilityWidget::RunCalibration()
{
    UTimedDataMonitorSubsystem* MonitorSubsystem = GEngine->GetEngineSubsystem<UTimedDataMonitorSubsystem>();
    if (!MonitorSubsystem) return;

    // 配置校准参数
    FTimedDataMonitorCalibrationParameters CalibrationParams;
    CalibrationParams.NumberOfRetries = 6;
    CalibrationParams.bBufferResizeAllowed = true;
    CalibrationParams.bUseStandardDeviation = true;

    // 启动异步校准
    MonitorSubsystem->CalibrateLatent(
        GetWorld(),
        FLatentActionInfo(0, FGuid::NewGuid().ToString(), TEXT("OnCalibrationFinished"), this),
        CalibrationParams,
        CalibrationResult // 这个输出参数会在 Latent Action 完成后被填充
    );
}

// Latent Action 完成后的回调（需要是 UFUNCTION）
void UMyEditorUtilityWidget::OnCalibrationFinished()
{
    // CalibrationResult 现在包含了结果
    if (CalibrationResult.ReturnCode == ETimedDataMonitorCalibrationReturnCode::Succeeded)
    {
        UE_LOG(LogTemp, Log, TEXT("Calibration Succeeded!"));
    }
    else
    {
        UE_LOG(LogWarning, Log, TEXT("Calibration Failed with code: %s"),
            *UEnum::GetValueAsString(CalibrationResult.ReturnCode));
    }
}
```
*（结合了异步校准与回调处理的用法）*

## Demo 示例

一个最小的 Actor 示例，用于在 Tick 中监控所有时间数据输入的平均评估距离。

**MyTimedDataMonitorActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyTimedDataMonitorActor.generated.h"

UCLASS()
class AMyTimedDataMonitorActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void Tick(float DeltaTime) override;

private:
    UPROPERTY()
    class UTimedDataMonitorSubsystem* MonitorSubsystem;
};
```

**MyTimedDataMonitorActor.cpp**
```cpp
#include "MyTimedDataMonitorActor.h"
#include "TimedDataMonitorSubsystem.h"
#include "Engine/Engine.h"

void AMyTimedDataMonitorActor::BeginPlay()
{
    Super::BeginPlay();
    MonitorSubsystem = GEngine->GetEngineSubsystem<UTimedDataMonitorSubsystem>();
}

void AMyTimedDataMonitorActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    if (!MonitorSubsystem) return;

    TArray<FTimedDataMonitorInputIdentifier> Inputs = MonitorSubsystem->GetAllInputs();
    for (const auto& InputId : Inputs)
    {
        // 获取每个输入评估到最新样本的平均距离（秒），可用于性能分析
        float MeanDistance = MonitorSubsystem->GetInputEvaluationDistanceToNewestSampleMean(InputId);
        if (MeanDistance > 0.1f) // 如果平均延迟超过100毫秒，发出警告
        {
            UE_LOG(LogTemp, Warning, TEXT("Input %s has high evaluation latency: %f s"),
                *InputId.ToString(), MeanDistance);
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLink` | 插件的核心数据来源之一，用于接收和管理各种实时数据流（如摄像机、动画）。 |
| `MediaIOCore` | 用于处理媒体输入/输出（如视频捕捉卡），是虚拟制片中视频同步的关键模块。 |
| `TimeManagement` | 提供时间码（Timecode）和帧率（Frame Rate）等基础时间管理功能，是时间同步的基石。 |
| `StageDataCore` | 为虚拟制片提供舞台数据（Stage Data）的抽象和通信框架。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-02-21 | `251322d6` | LiveLink and TDM: Option to save settings. | 为 LiveLink 和时间数据监控器添加了保存设置的选项。 |
| 2026-02-21 | `58f7b461` | [Backout] - CL51083024 | 回滚了之前的更改 (CL51083024)。 |
| 2026-02-21 | `c8c1981c` | LiveLink and TDM: Option to save settings. | 为 LiveLink 和时间数据监控器添加了保存设置的选项。 |
| 2026-01-08 | `2906cc5f` | LiveLinkHub - Disable Timed Data Monitor temporarily to work around crash | 在 LiveLinkHub 中暂时禁用时间数据监控器以规避崩溃。 |
| 2026-01-07 | `0c117b61` | LiveLinkHub - Enable Timed Data Monitor | 在 LiveLinkHub 中启用时间数据监控器。 |

### 维护评价

该插件创建于 2020 年初，距今已超过 5 年。从近期 Git 提交记录看（截至 2026 年 2 月），它仍在被 Epic Games 的虚拟制作团队维护，最近的更新集中在改善设置的持久化（保存/加载）以及解决与 LiveLinkHub 集成的稳定性问题（如临时禁用以规避崩溃）。然而，其 `.uplugin` 文件明确标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`，这表明它**仍被视为实验性功能**，API 和行为可能发生变化，且不推荐在最终产品中默认启用。它适用于正在探索或构建自定义虚拟制作监控管线的团队，但使用时需要做好应对潜在 breaking changes 和不稳定性的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/TimedDataMonitor)
- [官方文档]() (无)
- [测试用例]() (未在提供的路径中找到，可能在引擎其他测试目录下)