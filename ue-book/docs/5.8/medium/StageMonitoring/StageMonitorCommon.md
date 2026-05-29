# Stage Monitor

> Plugin enabling monitoring in the context of a virtual production stage where multiple machines are in operation

| 属性 | 值 |
|---|---|
| 中文名 | 舞台监控 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `StageDataProvider` (Runtime), `StageMonitor` (UncookedOnly), `StageMonitorCommon` (Runtime), `StageMonitorEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StageMonitoring) | |

## 用途

Stage Monitoring 是虚拟制片（Virtual Production）专用的多机监控系统。在 LED Volume / nDisplay 等虚拟制片场景中，通常有多台机器协同运行（渲染、追踪、合成等），这个插件解决的核心问题是：

- **集中监控**：从一个监控端查看所有参与虚拟制片的机器状态
- **性能监测**：实时采集每台机器的帧率、线程耗时、GPU 时间、内存使用等性能指标
- **异常检测**：自动检测卡顿（Hitch），在帧率低于阈值时发出告警
- **节点状态追踪**：跟踪每台机器是否在加载地图、编译资源、热重载等状态
- **会话管理**：通过 SessionId 区分不同的制片会话，避免数据混乱
- **角色过滤**：基于 GameplayTag 的 VP 角色（如 Camera、Wall、Render 等）过滤，决定哪些机器需要被监控
- **数据导出**：支持将会话数据导出为文件，可排除特定消息类型、只保留周期性消息的最后一帧

插件依赖 **Takes** 和 **VirtualProductionUtilities** 两个插件，说明它集成在更大的虚拟制片管线中，与 Take 录制系统联动。

## 使用场景

- 你有一个 LED Volume 舞台，多台机器运行 nDisplay → 用 StageMonitoring 集中监控所有机器的性能
- 你需要在直播/录制过程中实时检测渲染卡顿 → 用 HitchDetection 功能
- 你想按机器的 VP 角色（Camera、Wall 等）选择性监控 → 用 RoleFiltering
- 你需要在拍摄结束后分析各机器的性能数据 → 用数据导出功能
- 你想在编辑器中手动启动/停止监控而不需要自动启动 → 用命令行参数控制

## 蓝图用法

StageMonitoring 主要通过编辑器设置和命令行参数进行配置，蓝图接口较少。核心交互通过 `UStageMonitoringSettings` 的 Project Settings 面板完成。

### 配置入口

所有设置集中在 **Project Settings → Plugins → Stage Monitoring** 中，主要分为三个区域：

| 设置区域 | 说明 |
|---|---|
| **Settings** | 全局设置：SessionId 配置、超时间隔 |
| **Monitor Settings** | 监控端设置：角色过滤、发现消息间隔、自动启动 |
| **Provider Settings** | 数据提供端设置：角色过滤、帧性能采集间隔、卡顿检测 |
| **Export Settings** | 导出设置：是否只保留最后一条周期性消息、排除的消息类型 |

### 命令行参数

| 参数 | 说明 | 示例 |
|---|---|---|
| `-StageSessionId=N` | 覆盖项目的 SessionId | `-StageSessionId=42` |
| `-StageMonitorAutoStart=1` | 覆盖自动启动设置，强制启动监控 | `-StageMonitorAutoStart=1` |
| `-StageFriendlyName=Name` | 为当前实例设置友好名称，便于在监控中识别 | `-StageFriendlyName=RenderNode01` |

## C++ 用法

### 头文件引入

```cpp
#include "StageMonitorUtils.h"
#include "StageMonitoringSettings.h"
```

### 基本用法：读取性能消息

`FFramePerformanceProviderMessage` 是核心性能数据结构，包含每台机器的运行时指标。

```cpp
// 来源: Source/StageMonitorCommon/Public/StageMonitorUtils.h

// 节点状态枚举
EStageMonitorNodeStatus Status = EStageMonitorNodeStatus::Ready;
// 可选值: Unknown, LoadingMap, Ready, HotReload, AssetCompiling

// 构造一条帧性能消息（通常由 DataProvider 自动采集）
FFramePerformanceProviderMessage PerfMessage(
    EStageMonitorNodeStatus::Ready,
    5.2f,   // GameThreadTime (ms)
    0.1f,   // GameThreadWaitTime (ms)
    6.8f,   // RenderThreadTime (ms)
    0.0f,   // RenderThreadWaitTime (ms)
    8.3f,   // GPUTime (ms)
    1.0f,   // IdleTime (ms)
    1024 * 1024 * 512,  // CPU_MEM (bytes)
    1024 * 1024 * 2048, // GPU_MEM (bytes)
    3       // CompilationTasksRemaining
);

// 读取性能数据
float FPS = PerfMessage.AverageFPS;
float GPU = PerfMessage.GPU_MS;
uint64 CPUMem = PerfMessage.CPU_MEM;
int32 RemainingCompiles = PerfMessage.CompilationTasksRemaining;
```

### 基本用法：获取实例描述符

```cpp
// 来源: Source/StageMonitorCommon/Public/StageMonitorUtils.h

// 获取当前实例的描述信息（机器名、进程ID等）
FStageInstanceDescriptor Descriptor = StageMonitorUtils::GetInstanceDescriptor();
```

### 进阶用法：通过 Settings 进行自定义配置

```cpp
// 来源: Source/StageMonitorCommon/Public/StageMonitoringSettings.h

// 获取全局设置对象
const UStageMonitoringSettings* Settings = GetDefault<UStageMonitoringSettings>();

// 检查 SessionId 配置
if (Settings->bUseSessionId)
{
    int32 SessionId = Settings->GetStageSessionId();
    UE_LOG(LogTemp, Log, TEXT("Current Session ID: %d"), SessionId);
}

// 检查超时间隔
float Timeout = Settings->TimeoutInterval; // 默认 10 秒

// 检查 Monitor 是否应在启动时自动运行
bool bShouldAutoStart = Settings->MonitorSettings.ShouldAutoStartOnLaunch();

// 检查卡顿检测配置
const FStageHitchDetectionSettings& HitchSettings = Settings->ProviderSettings.HitchDetectionSettings;
if (HitchSettings.bEnableHitchDetection)
{
    FFrameRate MinFPS = HitchSettings.MinimumFrameRate; // 默认 24fps
    UE_LOG(LogTemp, Log, TEXT("Hitch detection enabled, minimum FPS: %f"), MinFPS.AsDecimal());
}
```

### 进阶用法：角色过滤

```cpp
// 来源: Source/StageMonitorCommon/Public/StageMonitoringSettings.h

const UStageMonitoringSettings* Settings = GetDefault<UStageMonitoringSettings>();

// Provider 角色过滤
const FStageDataProviderSettings& ProviderSettings = Settings->ProviderSettings;
if (ProviderSettings.bUseRoleFiltering)
{
    // 检查当前机器的角色是否在支持列表中
    FGameplayTagContainer AllowedRoles = ProviderSettings.SupportedRoles;
    
    // 检查特定消息类型的角色排除规则
    for (const auto& Pair : ProviderSettings.MessageTypeRoleExclusion)
    {
        FStageMessageTypeWrapper MessageType = Pair.Key;
        FGameplayTagContainer ExcludedRoles = Pair.Value;
        // Pair.Key.MessageType 为消息类型的 FName
        // Pair.Value 为被排除的角色容器
    }
}
```

## Demo 示例

```cpp
// MyStageObserver.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "StageMonitorUtils.h"
#include "MyStageObserver.generated.h"

/**
 * 简单的舞台监控数据收集器示例
 * 作为 GameInstance 子系统，每秒记录一次本机性能状态
 */
UCLASS()
class UMyStageObserver : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    /** 手动获取一条当前帧性能快照 */
    FFramePerformanceProviderMessage CaptureCurrentPerformance() const;

    /** 检查当前是否处于卡顿状态 */
    bool IsCurrentlyHitching() const;

private:
    FTimerHandle CaptureTimerHandle;
    void OnCaptureTimer();
};
```

```cpp
// MyStageObserver.cpp
#include "MyStageObserver.h"
#include "Engine/Engine.h"
#include "StageMonitoringSettings.h"

void UMyStageObserver::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    // 读取全局配置中的采集间隔
    const UStageMonitoringSettings* Settings = GetDefault<UStageMonitoringSettings>();
    float Interval = Settings->ProviderSettings.FramePerformanceSettings.UpdateInterval;

    // 注册定时采集
    if (UWorld* World = GetWorld())
    {
        World->GetTimerManager().SetTimer(
            CaptureTimerHandle,
            this,
            &UMyStageObserver::OnCaptureTimer,
            Interval,
            true
        );
    }

    UE_LOG(LogTemp, Log, TEXT("StageObserver initialized, capture interval: %.2f s"), Interval);
}

void UMyStageObserver::Deinitialize()
{
    if (UWorld* World = GetWorld())
    {
        World->GetTimerManager().ClearTimer(CaptureTimerHandle);
    }
    Super::Deinitialize();
}

FFramePerformanceProviderMessage UMyStageObserver::CaptureCurrentPerformance() const
{
    extern ENGINE_API float GAverageFPS;
    extern ENGINE_API float GGameThreadTime;
    extern ENGINE_API float GRenderThreadTime;

    // 获取 GPU 时间
    float GPUTimeMS = 0.0f;
    if (GDynamicRHI)
    {
        GPUTimeMS = RHIGetGPUFrameCycles() / (GNumExplicitGPUsForRendering * 1000.0f);
    }

    // 获取内存
    FPlatformMemoryStats MemStats = FPlatformMemory::GetStats();

    // 构造性能消息
    return FFramePerformanceProviderMessage(
        EStageMonitorNodeStatus::Ready,
        GGameThreadTime,
        0.0f,  // GameThreadWaitTime
        GRenderThreadTime,
        0.0f,  // RenderThreadWaitTime
        GPUTimeMS,
        0.0f,  // IdleTime
        MemStats.UsedPhysical,
        0,     // GPU Memory (需 RHI 支持)
        0      // CompilationTasksRemaining
    );
}

bool UMyStageObserver::IsCurrentlyHitching() const
{
    const UStageMonitoringSettings* Settings = GetDefault<UStageMonitoringSettings>();
    const FStageHitchDetectionSettings& HitchSettings = Settings->ProviderSettings.HitchDetectionSettings;

    if (!HitchSettings.bEnableHitchDetection)
    {
        return false;
    }

    // 检查当前 FPS 是否低于阈值
    float CurrentFPS = CaptureCurrentPerformance().AverageFPS;
    return CurrentFPS < HitchSettings.MinimumFrameRate.AsDecimal();
}

void UMyStageObserver::OnCaptureTimer()
{
    FFramePerformanceProviderMessage Message = CaptureCurrentPerformance();

    UE_LOG(LogTemp, Verbose, TEXT("[Stage] FPS: %.1f | GPU: %.2f ms | CPU Mem: %llu MB"),
        Message.AverageFPS,
        Message.GPU_MS,
        Message.CPU_MEM / (1024 * 1024));

    if (IsCurrentlyHitching())
    {
        UE_LOG(LogTemp, Warning, TEXT("[Stage] HITCH DETECTED! FPS: %.1f"), Message.AverageFPS);
    }
}
```

## 模块依赖

插件本身依赖 **Takes** 和 **VirtualProductionUtilities** 插件。

从源码中的类型使用（`FStageProviderPeriodicMessage`、`FStageInstanceDescriptor`、`FGameplayTagContainer`）推断，各模块依赖如下：

| 模块 | 用途 |
|---|---|
| `StageMonitorCommon` | 提供共享设置结构、性能消息类型、工具函数（其他三个模块的基础） |
| `VirtualProductionUtilities` | 提供 VP 角色 GameplayTag、网络消息基础设施 |
| `Takes` | 与 Take 录制系统集成 |
| `GameplayTags` | 角色过滤使用的 Tag 容器 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 JSON 对象以支持 FString 和 FSharedString 两种字符串类型 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到新的 UE_LOGF 格式 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 修复 FJsonObject 中的字符串重复问题以释放内存 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复上一次错误的查找替换操作 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回滚提交 CL51314860 |

### 维护评价

- **创建时间**：2020-09-24，约 5 年历史
- **更新频率**：近期（2026 年）有多次更新，但主要是底层基础设施重构（JSON、日志宏迁移），非功能性增强
- **活跃状态**：仍在维护中，但更新内容以框架级改动为主，功能层面趋于稳定
- **实验性状态**：`IsBetaVersion=true`，从未去掉 beta 标签，表明功能可能尚未完全定型
- **限制**：文档缺失（DocsURL 为空），BlueprintCallable 接口较少，主要面向 C++ 集成

**综合评价**：这是一个成熟但标记为 Beta 的虚拟制片专用工具。适合在 VP 阶段使用，但需要注意其 Beta 状态可能意味着 API 不完全稳定。推荐在需要多机监控的 VP 项目中使用，但建议关注版本升级时的兼容性变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StageMonitoring)
- [官方文档]()（暂无）