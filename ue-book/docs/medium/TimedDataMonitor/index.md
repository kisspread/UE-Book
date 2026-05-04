# Timed Data Monitor

> Utilities to monitor inputs that can be time synchronized.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TimedDataMonitor` (UncookedOnly), `TimedDataMonitorEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-01-22 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/TimedDataMonitor) | |

## 用途

Timed Data Monitor 是一个 Virtual Production 工具，用于**监控和诊断所有时间同步数据输入的缓冲区健康状态**。在影视虚拟制片（Virtual Production）场景中，摄像机追踪、视频输入、音频流等多种外部数据源需要与引擎时间保持精确同步。当这些数据流出现延迟抖动、丢帧、缓冲区溢出/下溢等问题时，画面会出现撕裂、卡顿或不同步。

该 plugin 的核心功能是：

1. **收集所有实现 `ITimedDataInput` 接口的数据源**（通过 `ITimedDataInputCollection` 自动发现）
2. **持续监控每个数据通道的缓冲区状态**：样本数量、最旧/最新样本时间、溢出/下溢计数、丢帧数
3. **计算评估时间与样本之间的统计距离**（指数移动平均均值和标准差）
4. **自动校准（Calibrate）**：调整 TimecodeProvider 的 FrameDelay，使所有数据源的评估时间对齐
5. **提供编辑器面板**：以可视化方式展示所有数据源的实时缓冲区状态

**需要手动启用**：`EnabledByDefault=false`，需在 Plugins 面板中手动启用。

## 使用场景

- 你在做虚拟制片（Virtual Production），使用 nDisplay + 摄像机追踪 + MediaCapture，需要确认所有视频流和追踪数据是否时间同步 → 使用 Timed Data Monitor
- 你需要诊断为什么 LED Wall 上的画面和实际摄像机画面之间有延迟 → 用 Timed Data Monitor 的校准功能自动调整 TimecodeProvider FrameDelay
- 你在运行时想监控 MediaIO 输入的缓冲区健康状态，检测丢帧和缓冲区溢出 → 通过蓝图调用 Subsystem API
- 你需要在生产环境中对多个视频通道做自动化校准流程 → 使用 `CalibrateLatent` 蓝图节点

## 蓝图用法

所有蓝图功能通过 `UTimedDataMonitorSubsystem` 暴露，可通过 `GEngine->GetEngineSubsystem<UTimedDataMonitorSubsystem>()` 或蓝图上下文自动获取。

### 全局查询

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetAllInputs` | 获取所有已注册的时间数据输入标识符列表 | `UTimedDataMonitorSubsystem` |
| `GetAllChannels` | 获取所有通道标识符列表 | `UTimedDataMonitorSubsystem` |
| `GetAllEnabledChannels` | 获取所有已启用的通道标识符列表 | `UTimedDataMonitorSubsystem` |
| `GetEvaluationState` | 获取所有输入中最差的评估状态 | `UTimedDataMonitorSubsystem` |
| `ResetAllBufferStats` | 重置所有通道的缓冲区统计（溢出/下溢/丢帧计数） | `UTimedDataMonitorSubsystem` |

### 输入（Input）操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DoesInputExist` | 检查输入标识符是否有效 | `UTimedDataMonitorSubsystem` |
| `GetInputEnabled` / `SetInputEnabled` | 查询/设置输入的启用状态 | `UTimedDataMonitorSubsystem` |
| `GetInputDisplayName` | 获取输入的显示名称 | `UTimedDataMonitorSubsystem` |
| `GetInputChannels` | 获取输入下的所有通道标识符 | `UTimedDataMonitorSubsystem` |
| `GetInputEvaluationType` / `SetInputEvaluationType` | 查询/设置评估模式（Timecode / PlatformTime） | `UTimedDataMonitorSubsystem` |
| `GetInputEvaluationOffsetInSeconds` / `SetInputEvaluationOffsetInSeconds` | 查询/设置评估时间偏移（秒） | `UTimedDataMonitorSubsystem` |
| `GetInputEvaluationOffsetInFrames` / `SetInputEvaluationOffsetInFrames` | 查询/设置评估时间偏移（帧） | `UTimedDataMonitorSubsystem` |
| `GetInputFrameRate` | 获取输入的帧率 | `UTimedDataMonitorSubsystem` |
| `GetInputDataBufferSize` / `SetInputDataBufferSize` | 查询/设置输入缓冲区大小 | `UTimedDataMonitorSubsystem` |
| `GetInputConnectionState` | 获取输入的连接状态 | `UTimedDataMonitorSubsystem` |
| `GetInputEvaluationState` | 获取输入的评估状态 | `UTimedDataMonitorSubsystem` |
| `GetInputOldestDataTime` / `GetInputNewestDataTime` | 获取输入中最旧/最新的样本时间 | `UTimedDataMonitorSubsystem` |

### 通道（Channel）操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DoesChannelExist` | 检查通道标识符是否有效 | `UTimedDataMonitorSubsystem` |
| `IsChannelEnabled` / `SetChannelEnabled` | 查询/设置通道启用状态 | `UTimedDataMonitorSubsystem` |
| `GetChannelInput` | 获取通道所属的输入标识符 | `UTimedDataMonitorSubsystem` |
| `GetChannelDisplayName` | 获取通道显示名称 | `UTimedDataMonitorSubsystem` |
| `GetChannelConnectionState` | 获取通道连接状态 | `UTimedDataMonitorSubsystem` |
| `GetChannelEvaluationState` | 获取通道评估状态 | `UTimedDataMonitorSubsystem` |
| `GetChannelOldestDataTime` / `GetChannelNewestDataTime` | 获取通道中最旧/最新的样本时间 | `UTimedDataMonitorSubsystem` |
| `GetChannelFrameDataTimes` | 获取通道中每一帧的样本时间 | `UTimedDataMonitorSubsystem` |
| `GetChannelNumberOfSamples` | 获取通道中可用的样本数量 | `UTimedDataMonitorSubsystem` |
| `GetChannelDataBufferSize` / `SetChannelDataBufferSize` | 查询/设置通道缓冲区大小 | `UTimedDataMonitorSubsystem` |
| `GetChannelBufferUnderflowStat` | 获取缓冲区下溢计数 | `UTimedDataMonitorSubsystem` |
| `GetChannelBufferOverflowStat` | 获取缓冲区溢出计数 | `UTimedDataMonitorSubsystem` |
| `GetChannelFrameDroppedStat` | 获取丢帧计数 | `UTimedDataMonitorSubsystem` |
| `GetChannelLastEvaluationDataStat` | 获取最后一次评估的详细数据 | `UTimedDataMonitorSubsystem` |

### 统计与校准

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetChannelEvaluationDistanceToNewestSampleMean` | 获取评估时间到最新样本的平均距离（秒） | `UTimedDataMonitorSubsystem` |
| `GetChannelEvaluationDistanceToOldestSampleMean` | 获取评估时间到最旧样本的平均距离（秒） | `UTimedDataMonitorSubsystem` |
| `GetChannelEvaluationDistanceToNewestSampleStandardDeviation` | 获取评估时间到最新样本距离的标准差 | `UTimedDataMonitorSubsystem` |
| `GetChannelEvaluationDistanceToOldestSampleStandardDeviation` | 获取评估时间到最旧样本距离的标准差 | `UTimedDataMonitorSubsystem` |
| `CalibrateLatent` | 异步校准：调整 TimecodeProvider FrameDelay 使所有输入对齐 | `UTimedDataMonitorSubsystem` |
| `ApplyTimeCorrection` | 时间校正：假设所有样本同时产生，将其与平台时间对齐 | `UTimedDataMonitorSubsystem` |

### 使用示例（蓝图描述）

**监控缓冲区健康状态**：

1. 创建一个蓝图，在 Event Tick 中调用 `GetAllEnabledChannels` 获取所有通道
2. 对每个通道调用 `GetChannelEvaluationState`，如果返回 `OutsideRange` 或 `NoSample`，说明该通道数据不健康
3. 调用 `GetChannelBufferUnderflowStat` / `GetChannelBufferOverflowStat` 获取具体的缓冲区错误计数

**自动校准流程**：

1. 创建一个蓝图，使用 `CalibrateLatent` 节点（Latent 异步节点）
2. 设置 `FTimedDataMonitorCalibrationParameters`：重试次数、是否允许缓冲区调整、标准差参数
3. 连接 Completion 输出引脚，检查 `FTimedDataMonitorCalibrationResult` 的 ReturnCode
4. 校准成功后，所有数据源的 TimecodeProvider FrameDelay 会自动调整

## C++ 用法

### 头文件引入

```cpp
#include "TimedDataMonitorSubsystem.h"
#include "TimedDataMonitorCalibration.h"
#include "TimedDataMonitorTypes.h"
```

### 基本用法

获取 Subsystem 并查询所有注册的时间数据输入：

```cpp
// 获取 Subsystem 实例
UTimedDataMonitorSubsystem* MonitorSubsystem = GEngine->GetEngineSubsystem<UTimedDataMonitorSubsystem>();

// 获取所有已注册的输入
TArray<FTimedDataMonitorInputIdentifier> AllInputs = MonitorSubsystem->GetAllInputs();

// 遍历每个输入，检查状态
for (const FTimedDataMonitorInputIdentifier& InputId : AllInputs)
{
    // 检查连接状态
    ETimedDataInputState ConnectionState = MonitorSubsystem->GetInputConnectionState(InputId);
    
    // 获取输入的评估模式
    ETimedDataInputEvaluationType EvalType = MonitorSubsystem->GetInputEvaluationType(InputId);
    
    // 获取该输入下的所有通道
    TArray<FTimedDataMonitorChannelIdentifier> Channels = MonitorSubsystem->GetInputChannels(InputId);
    
    for (const FTimedDataMonitorChannelIdentifier& ChannelId : Channels)
    {
        // 获取通道评估状态
        ETimedDataMonitorEvaluationState EvalState = MonitorSubsystem->GetChannelEvaluationState(ChannelId);
        
        // 获取缓冲区统计
        int32 NumSamples = MonitorSubsystem->GetChannelNumberOfSamples(ChannelId);
        int32 UnderflowCount = MonitorSubsystem->GetChannelBufferUnderflowStat(ChannelId);
        int32 OverflowCount = MonitorSubsystem->GetChannelBufferOverflowStat(ChannelId);
        int32 DroppedFrames = MonitorSubsystem->GetChannelFrameDroppedStat(ChannelId);
    }
}
```

### 进阶用法

**异步校准（Calibration）**：

```cpp
// 使用 FTimedDataMonitorCalibration 执行异步校准
TUniquePtr<FTimedDataMonitorCalibration> Calibration = MakeUnique<FTimedDataMonitorCalibration>();

FTimedDataMonitorCalibrationParameters Params;
Params.NumberOfRetries = 4;
Params.bBufferResizeAllowed = true;
Params.bUseStandardDeviation = true;
Params.NumberOfStandardDeviation = 3;
Params.bResetStatisticsBeforeUsingStandardDeviation = true;
Params.AmountOfSecondsToWaitAfterStatisticReset = 2.0f;

Calibration->CalibrateWithTimecode(Params,
    FTimedDataMonitorCalibration::FOnCalibrationCompletedSignature::CreateLambda(
        [](FTimedDataMonitorCalibrationResult Result)
        {
            if (Result.ReturnCode == ETimedDataMonitorCalibrationReturnCode::Succeeded)
            {
                UE_LOG(LogTemp, Log, TEXT("Calibration succeeded!"));
            }
            else
            {
                UE_LOG(LogTemp, Warning, TEXT("Calibration failed with code: %d"),
                    (int32)Result.ReturnCode);
            }
        }
    )
);
```

**时间校正（Time Correction）**：

```cpp
UTimedDataMonitorSubsystem* Monitor = GEngine->GetEngineSubsystem<UTimedDataMonitorSubsystem>();

FTimedDataMonitorInputIdentifier InputId = Monitor->GetAllInputs()[0];

FTimedDataMonitorTimeCorrectionParameters CorrectionParams;
CorrectionParams.bBufferResizeAllowed = true;
CorrectionParams.bUseStandardDeviation = true;
CorrectionParams.NumberOfStandardDeviation = 3;

FTimedDataMonitorTimeCorrectionResult Result = Monitor->ApplyTimeCorrection(InputId, CorrectionParams);

if (Result.ReturnCode == ETimedDataMonitorTimeCorrectionReturnCode::Succeeded)
{
    UE_LOG(LogTemp, Log, TEXT("Time correction applied successfully"));
}
```

**监听数据源变化**：

```cpp
UTimedDataMonitorSubsystem* Monitor = GEngine->GetEngineSubsystem<UTimedDataMonitorSubsystem>();

// C++ delegate
Monitor->OnIdentifierListChanged().AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("Timed data source list changed"));
});

// Blueprint delegate (dynamic)
Monitor->OnIdentifierListChanged_Dynamic.AddDynamic(this, &UMyClass::OnSourceListChanged);
```

## 编辑器面板

该 plugin 提供了一个 Nomad Tab 编辑器面板 `STimedDataMonitorPanel`，注册在 **Window > Virtual Production** 菜单下。

面板包含以下子组件：

- **Genlock 状态** (`STimedDataGenlock`)：显示 CustomTimeStep 的同步状态、FPS、DeltaTime、IdleTime
- **Timecode Provider** (`STimedDataTimecodeProvider`)：显示 TimecodeProvider 的同步状态、当前 Timecode、FrameDelay 配置
- **数据源列表** (`STimedDataInputListView`)：树形列表，显示所有 Input → Channel 层级，包含评估偏移、缓冲区大小、溢出/下溢/丢帧计数等
- **时序图** (`STimingDiagramWidget`)：每个通道的缓冲区可视化，显示样本在时间轴上的分布
- **缓冲区可视化** (`STimedDataMonitorBufferVisualizer`)：可选的缓冲区详细可视化

面板功能：

- **Calibrate 按钮**：执行 Timecode 校准或时间校正
- **Reset 按钮**：重置缓冲区统计 / 清除消息 / 重置评估时间
- **右键菜单**：对选中输入执行 Apply Time Correction / Reset Time Correction

编辑器设置位于 **Editor Preferences > Plugins > Timed Data Monitor** (`UTimedDataMonitorEditorSettings`)，可配置：

- UI 刷新频率 (`RefreshRate`，默认 0.2 秒)
- 是否在缓冲区可视化中绘制帧时间标记
- 帧时间警告阈值
- 标准差显示范围
- Reset 按钮行为

## 关键枚举类型

### ETimedDataMonitorEvaluationState

| 值 | 说明 |
|---|---|
| `NoSample` (0) | 缓冲区中没有样本 |
| `OutsideRange` (1) | 评估时间不在缓冲区范围内 |
| `InsideRange` (2) | 评估时间在缓冲区范围内（健康） |
| `Disabled` (3) | 通道已禁用 |

### ETimedDataMonitorCalibrationReturnCode

| 值 | 说明 |
|---|---|
| `Succeeded` | 校准成功 |
| `Failed_NoTimecode` | TimecodeProvider 未同步 |
| `Failed_UnresponsiveInput` | 至少一个输入无响应 |
| `Failed_InvalidEvaluationType` | 输入评估类型不是 Timecode |
| `Failed_InvalidFrameRate` | 输入没有定义帧率 |
| `Failed_NoDataBuffered` | 输入没有缓冲数据 |
| `Failed_BufferCouldNotBeResize` | 缓冲区无法调整大小 |
| `Failed_Reset` | 校准被手动重置 |
| `Retry_NotEnoughData` | 缓冲区大小正确但数据不足，需要重试 |
| `Retry_IncreaseBufferSize` | 需要增大缓冲区，需要重试 |

## Demo 示例

### 最小监控示例

**MyTimedDataMonitor.h**：

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MyTimedDataMonitor.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class UMyTimedDataMonitor : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType,
        FActorComponentTickFunction* ThisTickFunction) override;
};
```

**MyTimedDataMonitor.cpp**：

```cpp
#include "MyTimedDataMonitor.h"
#include "TimedDataMonitorSubsystem.h"
#include "Engine/Engine.h"

void UMyTimedDataMonitor::BeginPlay()
{
    Super::BeginPlay();
}

void UMyTimedDataMonitor::TickComponent(float DeltaTime, ELevelTick TickType,
    FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    UTimedDataMonitorSubsystem* Monitor = GEngine->GetEngineSubsystem<UTimedDataMonitorSubsystem>();
    if (!Monitor)
    {
        return;
    }

    // 检查全局评估状态
    ETimedDataMonitorEvaluationState GlobalState = Monitor->GetEvaluationState();
    if (GlobalState == ETimedDataMonitorEvaluationState::InsideRange)
    {
        UE_LOG(LogTemp, Verbose, TEXT("All timed data inputs are healthy"));
    }

    // 检查每个通道的缓冲区统计
    for (const FTimedDataMonitorChannelIdentifier& ChannelId : Monitor->GetAllEnabledChannels())
    {
        int32 Underflow = Monitor->GetChannelBufferUnderflowStat(ChannelId);
        int32 Overflow = Monitor->GetChannelBufferOverflowStat(ChannelId);
        int32 Dropped = Monitor->GetChannelFrameDroppedStat(ChannelId);

        if (Underflow > 0 || Overflow > 0 || Dropped > 0)
        {
            FText Name = Monitor->GetChannelDisplayName(ChannelId);
            UE_LOG(LogTemp, Warning,
                TEXT("Channel '%s': Underflow=%d, Overflow=%d, Dropped=%d"),
                *Name.ToString(), Underflow, Overflow, Dropped);
        }
    }
}
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "TimedDataMonitor",
    "Core",
    "CoreUObject",
    "Engine"
});
```

## 控制台变量

| CVar | 默认值 | 说明 |
|---|---|---|
| `TimedDataMonitor.EnableStatUpdate` | `1` | 启用/禁用通道评估统计计算 |
| `TimedDataMonitor.Statistics.Weight` | `0.1` | 指数移动平均的权重，越接近 1 对新值越敏感 |

非 Shipping/Test 构建还提供以下控制台命令：

| 命令 | 说明 |
|---|---|
| `TimedDataMonitor.StartFileLogging` | 开始将每帧每通道的统计数据记录到文件 |
| `TimedDataMonitor.StopFileLogging` | 停止记录并导出文件 |

## 模块依赖

### TimedDataMonitor（Runtime 模块）

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `CoreUObject` | UObject 系统 |
| `StageDataCore` | Stage 消息系统（FStageProviderEventMessage） |
| `TimeManagement` | 时间管理接口（ITimedDataInput, ITimedDataInputCollection, TimecodeProvider） |
| `Engine` | 引擎核心（私有依赖） |

### TimedDataMonitorEditor（Editor 模块）

| 模块 | 用途 |
|---|---|
| `TimedDataMonitor` | Runtime 模块本体 |
| `TimeManagement` | 时间管理接口 |
| `UnrealEd` | 编辑器框架 |
| `Slate` / `SlateCore` | UI 框架 |
| `EditorStyle` | 编辑器样式 |
| `EditorWidgets` | 编辑器通用控件 |
| `WorkspaceMenuStructure` | 工作区菜单注册 |

## 维护状态

### 近期更新

- `ce6ff39` (2025-09-12) — Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue for FTSTicker::RemoveTicker usage.
  解读：修复编译警告，FTSTicker::RemoveTicker 标记了 [[nodiscard]]，需要检查返回值。纯编译兼容性修复。

- `52f52bc` (2025-05-02) — Timecode: Cvar to force or remove subframes from its ToString function.
  解读：Timecode 相关功能更新，新增 CVar 控制 Timecode 的子帧显示。与 TimedDataMonitor 间接相关。

- `d39c9da` (2025-03-13) — Fix compile error in STimedDataListView
  解读：修复编辑器列表视图的编译错误。纯编译修复。

### 维护评价

- **创建时间**：2020 年 1 月，已有约 6 年历史
- **Beta 状态**：`.uplugin` 中 `IsBetaVersion=true`，且 `EnabledByDefault=false`，说明 Epic 仍将其视为实验性功能
- **最近更新**：最近 3 次提交（2025-03 至 2025-09）都是编译修复或间接相关更新，**没有功能性改进**
- **维护状态**：**维护不活跃** — 核心功能稳定但无新特性开发
- **推荐使用**：适合 Virtual Production 场景使用，功能完整但需注意仍标记为 Beta。如果你在做 VP 时间同步诊断，这是唯一可用的官方工具

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/TimedDataMonitor)
- 官方文档（无，.uplugin 中 DocsURL 为空）
- [ITimedDataInput 接口源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Runtime/TimeManagement)
