# Stage Monitor

> Plugin enabling monitoring in the context of a virtual production stage where multiple machines are in operation（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟制片监控 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `StageDataProvider` (Runtime), `StageMonitor` (UncookedOnly), `StageMonitorCommon` (Runtime), `StageMonitorEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StageMonitoring) | |

## 用途

StageMonitoring 是一个用于虚拟制片（Virtual Production）场景下的**多机监控系统**。在 LED 墙、nDisplay 等多机协同运行的场景中，需要实时掌握每台机器的运行状态，包括：

- **帧率与卡顿监控**：检测游戏线程、渲染线程和 GPU 的耗时，当帧时间超过阈值时发出卡顿警告
- **Timecode Provider 状态监控**：监控时间码提供器是否同步正常，状态变化时通知监控端
- **Genlock 信号监控**：监控 Genlock 同步信号是否丢失，确保引擎帧率与外部同步源保持一致
- **Take Recorder 状态监控**：在编辑器中监控录制状态（开始/停止/进行中）

该插件使用 **Message Bus（消息总线）** 实现 Provider（被监控机器）与 Monitor（监控端）之间的通信。被监控机器作为 DataProvider 向外广播状态，监控端通过发现机制自动连接并接收状态更新。

## 使用场景

- 你在使用 nDisplay 配置多台渲染节点 → 用 StageMonitor 集中监控所有节点的帧率和同步状态
- 你需要在虚拟制片现场检测卡顿 → 启用 hitch detection，在帧时间超阈值时实时报警
- 你使用 Timecode Provider 或 Genlock 同步 → 用 watchdog 监控同步状态变化和信号丢失
- 你在编辑器中录制 Take → 监控 Take Recorder 的录制状态，与其他机器同步

## 蓝图用法

该插件的公共 API 较少，核心功能通过模块接口和消息总线在 C++ 层面运行。以下是可用的接口：

### 核心节点

该插件主要通过 C++ 模块接口使用，没有直接暴露 BlueprintCallable 函数。数据通过消息总线（Message Endpoint）在运行时自动传播。

### 数据结构

以下结构体在蓝图中可见，可用于读取消息内容：

| 结构体 | 说明 |
|---|---|
| `FHitchDetectionMessage` | 卡顿检测消息，包含各线程耗时、FPS 等信息 |
| `FTimecodeProviderStateEvent` | Timecode Provider 状态变化事件 |
| `FGenlockHitchEvent` | Genlock 同步信号丢失事件 |
| `FGenlockStateEvent` | Genlock 自定义时间步进状态变化事件 |

## C++ 用法

### 头文件引入

```cpp
#include "IStageDataProviderModule.h"
```

### 基本用法

获取 StageDataProvider 模块实例：

```cpp
// 来源: Public/IStageDataProviderModule.h

// 检查模块是否可用
if (IStageDataProviderModule::IsAvailable())
{
    // 获取模块实例
    IStageDataProviderModule& DataProviderModule = IStageDataProviderModule::Get();
}
```

### 进阶用法

#### 卡顿检测消息的处理

当检测到卡顿时，`FHitchDetectionMessage` 会包含详细的性能数据：

```cpp
// 来源: Private/FramePerformanceProvider.h

// FHitchDetectionMessage 包含以下字段：
// - GameThreadWithWaitsMS: 游戏线程耗时（含等待），单位 ms
// - RenderThreadWithWaitsMS: 渲染线程耗时（含等待），单位 ms
// - GameThreadMS: 游戏线程耗时（不含等待），单位 ms
// - RenderThreadMS: 渲染线程耗时（不含等待），单位 ms
// - GPU_MS: GPU 耗时，单位 ms
// - TimingThreshold: 触发卡顿的阈值，单位 ms
// - HitchedTimeFPS: 触发卡顿时对应线程的 FPS
// - AverageFPS: 卡顿发生时的平均 FPS
```

#### Genlock 监控

```cpp
// 来源: Private/GenlockWatchdog.h

// FGenlockHitchEvent - 同步信号丢失事件
// - MissedSyncSignals: 两次 tick 之间丢失的同步信号数量

// FGenlockStateEvent - 状态变化事件
// - NewState: 新状态 (Closed, Synchronized, Error, 等)
```

#### Timecode Provider 监控

```cpp
// 来源: Private/TimecodeProviderWatchdog.h

// FTimecodeProviderStateEvent 包含：
// - ProviderName: Timecode Provider 名称
// - ProviderType: Provider 类名
// - FrameRate: Provider 帧率
// - NewState: 新状态 (Closed, Synchronized, Error, 等)
```

## Demo 示例

### 监控卡顿检测消息

```cpp
// StageHitchListener.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "StageHitchListener.generated.h"

UCLASS(ClassGroup=(Stage), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UStageHitchListener : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
    
    /** 当前是否有卡顿 */
    UPROPERTY(BlueprintReadOnly, Category = "Stage Monitor")
    bool bHasHitch = false;
    
    /** 最近一次卡顿的游戏线程耗时 */
    UPROPERTY(BlueprintReadOnly, Category = "Stage Monitor")
    float LastHitchGameThreadMS = 0.f;
    
    /** 最近一次卡顿的 GPU 耗时 */
    UPROPERTY(BlueprintReadOnly, Category = "Stage Monitor")
    float LastHitchGPU_MS = 0.f;

private:
    // 消息端点及绑定逻辑在 .cpp 中实现
};
```

```cpp
// StageHitchListener.cpp
#include "StageHitchListener.h"
#include "IStageDataProviderModule.h"

void UStageHitchListener::BeginPlay()
{
    Super::BeginPlay();
    
    // 确保 StageDataProvider 模块已加载
    if (IStageDataProviderModule::IsAvailable())
    {
        IStageDataProviderModule& Module = IStageDataProviderModule::Get();
        // 此处可通过消息总线绑定消息处理
        UE_LOG(LogTemp, Log, TEXT("StageDataProvider module is available"));
    }
}

void UStageHitchListener::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

从各模块的 Build.cs 分析，该插件有以下插件级依赖：

| 插件 | 用途 |
|---|---|
| `Takes` | 录制系统支持（Take Recorder 状态监控） |
| `VirtualProductionUtilities` | 虚拟制片工具集（基础 VP 工具函数） |

无特殊模块依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 支持 FString 和 FSharedString 两种类型 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到新的 UE_LOGF 宏 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 消除 FJsonObject 中的字符串重复以减少内存占用 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复之前错误的查找替换后重新提交 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回滚之前的提交 CL51314860 |

### 维护评价

- **年龄**：约 6 年，从 UE4 时代延续至今
- **近期更新**：2026 年有多次更新，但均为**内部重构**（JSON 处理优化、日志宏迁移），非功能性改动
- **实验性状态**：`IsBetaVersion=true`，仍标记为 Beta
- **手动启用**：`Installed=false`，需要手动启用
- **活跃度**：维护中有持续的基础设施更新，但无近期功能新增

**综合评价**：该插件处于**维护中但无新功能开发**的状态。核心功能稳定，近期更新集中在内部优化。作为虚拟制片多机监控方案仍然可用，但因 Beta 状态和手动启用的要求，建议在正式项目中谨慎评估。如果需要多机监控功能，这仍是 UE5 官方提供的唯一方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StageMonitoring)
- [官方文档](https://docs.unrealengine.com)（无专属文档页面）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StageMonitoring)（待确认）