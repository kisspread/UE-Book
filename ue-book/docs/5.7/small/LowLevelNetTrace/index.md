# Low-level network trace Plugin

> Actively monitors & reports system network throughput.

| 属性 | 值 |
|---|---|
| 中文名 | 低级网络追踪 |
| 分类 | Profiling |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `LowLevelNetTrace` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LowLevelNetTrace) | |

## 用途

此插件提供操作系统级的网络吞吐量实时监控功能。它通过底层接口（例如 Windows 的 `GetNetworkStatistics` 或 Linux 的 `/proc/net`）定期采集当前网络接口的上传和下载速率，并以快照形式供开发者查询。主要解决传统套接字级别统计无法覆盖全部系统网络流量的问题（例如第三方库或引擎外部进程产生的网络活动），适用于需要精确衡量游戏/应用整体网络带宽消耗的调试与优化场景。

## 使用场景

- 制作实时在线游戏时，需要监控网络带宽是否达到硬件或网络瓶颈，以调整数据压缩策略或降低发包频率。
- 在性能分析（Profiling）阶段，结合其他 Trace 工具，定位网络吞吐量异常高的时刻，分析是否由非必要数据导致。
- 开发自定义网络性能仪表盘（HUD），在开发或测试环境中实时显示系统级上下行速率。

## 蓝图用法

此插件完全由 C++ 实现，未暴露任何 BlueprintCallable 或 BlueprintReadWrite 属性。蓝图无法直接调用。若需在蓝图中使用，可创建 C++ 包装类（如 `UObject` 子类）来调用插件接口，然后通过 `BlueprintImplementableEvent` 传递快照数据。

## C++ 用法

### 头文件引入

```cpp
#include "LowLevelNetTraceModule.h"
```

### 基本用法

插件提供模块接口 `ILowLevelNetTraceModule`，通过静态方法 `Get()` 获取实例，并调用 `GetSnapshot` 填充 `FLowLevelNetTraceSnapshot` 结构体。

```cpp
// 只在非Shipping且启用Trace（UE_TRACE_ENABLED）时有效
// 通常建议在 GameThread 上调用

FLowLevelNetTraceSnapshot Snapshot;
if (ILowLevelNetTraceModule::Get().GetSnapshot(Snapshot))
{
    UE_LOG(LogTemp, Log, TEXT("Upload: %.2f Mbps, Download: %.2f Mbps (Time: %.2f)"),
        Snapshot.UploadMbps,
        Snapshot.DownloadMbps,
        Snapshot.TimeStamp);
}
```

**注意**：`GetSnapshot` 返回 `true` 仅当快照成功更新。快照数据代表采集时刻最近一个采样周期内的平均速率。

### 进阶用法

可定期采样并记录历史数据，用于生成折线图或报警：

```cpp
#include "Containers/Queue.h"
#include "HAL/Runnable.h"
#include "HAL/RunnableThread.h"

class FNetStatsCollector : public FRunnable
{
    TQueue<FLowLevelNetTraceSnapshot> SnapshotQueue;
    FRunnableThread* Thread = nullptr;
    bool bRunning = false;

public:
    void Start()
    {
        bRunning = true;
        Thread = FRunnableThread::Create(this, TEXT("NetStatsCollector"));
    }

    void Stop()
    {
        bRunning = false;
        if (Thread) Thread->WaitForCompletion();
    }

    virtual uint32 Run() override
    {
        while (bRunning)
        {
            FLowLevelNetTraceSnapshot Snapshot;
            if (ILowLevelNetTraceModule::Get().GetSnapshot(Snapshot))
            {
                SnapshotQueue.Enqueue(Snapshot);
            }
            FPlatformProcess::Sleep(1.0f); // 每秒采集一次
        }
        return 0;
    }

    void FlushSnapshots(TArray<FLowLevelNetTraceSnapshot>& OutArray)
    {
        FLowLevelNetTraceSnapshot Item;
        while (SnapshotQueue.Dequeue(Item))
        {
            OutArray.Add(Item);
        }
    }
};
```

## Demo 示例

以下是一个最小 C++ 示例，在游戏启动后每帧输出一次网络速率，持续 5 秒后自动停止。

### NetTraceDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NetTraceDemo.generated.h"

UCLASS()
class ANetTraceDemo : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;

private:
    float ElapsedTime = 0.0f;
};
```

### NetTraceDemo.cpp

```cpp
#include "NetTraceDemo.h"
#include "LowLevelNetTraceModule.h"

void ANetTraceDemo::BeginPlay()
{
    Super::BeginPlay();
    ElapsedTime = 0.0f;
}

void ANetTraceDemo::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    if (!ILowLevelNetTraceModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("LowLevelNetTrace module not loaded."));
        return;
    }

    FLowLevelNetTraceSnapshot Snapshot;
    if (ILowLevelNetTraceModule::Get().GetSnapshot(Snapshot))
    {
        UE_LOG(LogTemp, Log, TEXT("[NetTrace] UP: %.2f Mbps, DOWN: %.2f Mbps"),
            Snapshot.UploadMbps, Snapshot.DownloadMbps);
    }

    ElapsedTime += DeltaSeconds;
    if (ElapsedTime > 5.0f)
    {
        SetActorTickEnabled(false);
        UE_LOG(LogTemp, Log, TEXT("NetTrace demo finished."));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、日志、平台抽象 |

无特殊依赖（仅标准 Core/Engine 等）。

## 维护状态

### 近期更新

- 2024-09-09 f2b2d7f0 Experimental low-level network stats plugin that captures OS-level network throughput. (初始提交)

（最近一次提交距今超过一年，无后续更新）

### 维护评价

此插件为实验性功能（`IsBetaVersion=true`），创建于 2024-09-09，仅有一次初始提交，之后未进行任何实质性更新。当前状态属于**实验性且维护不活跃**。代码量极小（3 个头/实现文件），功能单一。由于没有后续维护记录，建议谨慎用于生产项目，并关注未来是否有更新。如果需要在正式项目中使用，建议自行 fork 并维护，或等待官方将其稳定化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LowLevelNetTrace)
- 官方文档：无
- 测试用例：无