# Low-level Network Trace

> Actively monitors & reports system network throughput.

| 属性 | 值 |
|---|---|
| 中文名 | 底层网络追踪 |
| 分类 | Profiling |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `LowLevelNetTrace` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/LowLevelNetTrace) | |

## 用途

该插件在操作系统层面捕获网络吞吐量数据（上传/下载速率），并将其作为快照（Snapshot）供引擎其他模块读取。采集到的数据同时会发送到 Unreal Insights 进行可视化分析。

它解决的核心问题是：**在运行时实时监控底层网络带宽使用情况**，而非 UE 网络层的逻辑统计。这在调试多人游戏的网络瓶颈、优化数据传输策略时非常有用。

**当前限制**：仅在主机平台（Console）上实现，PC 等平台可能无法使用。

## 使用场景

- 你正在开发多人在线游戏，需要监控设备实际网络带宽 → 用此插件获取 OS 级别的上下行速率
- 你需要通过 Unreal Insights 分析网络吞吐量趋势 → 启动时加 `-trace=counters` 参数即可自动上报
- 你需要根据当前网络带宽动态调整数据发送频率或内容 → 通过 `GetSnapshot()` 读取实时带宽

## 蓝图用法

该插件没有暴露任何蓝图节点。所有 API 仅面向 C++。

## C++ 用法

### 头文件引入

```cpp
#include "LowLevelNetTraceModule.h"
```

### 基本用法

通过模块接口获取当前网络吞吐量快照：

```cpp
// 检查模块是否可用
if (ILowLevelNetTraceModule::IsAvailable())
{
    FLowLevelNetTraceSnapshot Snapshot;
    if (ILowLevelNetTraceModule::Get().GetSnapshot(Snapshot))
    {
        // Snapshot.UploadMbps   —— 当前上传速率 (Mbps)
        // Snapshot.DownloadMbps —— 当前下载速率 (Mbps)
        // Snapshot.TimeStamp    —— 快照时间戳
        UE_LOG(LogTemp, Log, TEXT("上传: %.2f Mbps, 下载: %.2f Mbps"),
            Snapshot.UploadMbps, Snapshot.DownloadMbps);
    }
}
```

### 进阶用法

周期性轮询带宽数据并据此做自适应调整：

```cpp
void AMyNetworkManager::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (!ILowLevelNetTraceModule::IsAvailable())
    {
        return;
    }

    FLowLevelNetTraceSnapshot Snapshot;
    if (ILowLevelNetTraceModule::Get().GetSnapshot(Snapshot))
    {
        // 根据下载带宽动态调整数据接收策略
        if (Snapshot.DownloadMbps < 1.0)
        {
            // 低带宽：降低同步频率
            SetNetworkSyncRate(LowRate);
        }
        else if (Snapshot.DownloadMbps > 10.0)
        {
            // 高带宽：提高同步精度
            SetNetworkSyncRate(HighRate);
        }
    }
}
```

## Demo 示例

### MinimalNetworkMonitor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LowLevelNetTraceModule.h"
#include "MinimalNetworkMonitor.generated.h"

UCLASS()
class AMinimalNetworkMonitor : public AActor
{
    GENERATED_BODY()

public:
    AMinimalNetworkMonitor();

    virtual void Tick(float DeltaTime) override;

private:
    float AccumulatedTime = 0.0f;
    float PollInterval = 1.0f; // 每秒查询一次
};
```

### MinimalNetworkMonitor.cpp

```cpp
#include "MinimalNetworkMonitor.h"
#include "LowLevelNetTraceModule.h"

AMinimalNetworkMonitor::AMinimalNetworkMonitor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMinimalNetworkMonitor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    AccumulatedTime += DeltaTime;
    if (AccumulatedTime < PollInterval)
    {
        return;
    }
    AccumulatedTime = 0.0f;

    if (!ILowLevelNetTraceModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("LowLevelNetTrace 模块未加载"));
        return;
    }

    FLowLevelNetTraceSnapshot Snapshot;
    if (ILowLevelNetTraceModule::Get().GetSnapshot(Snapshot))
    {
        UE_LOG(LogTemp, Log,
            TEXT("[NetTrace] 上传: %.2f Mbps | 下载: %.2f Mbps | 时间戳: %.3f"),
            Snapshot.UploadMbps,
            Snapshot.DownloadMbps,
            Snapshot.TimeStamp);
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-09-09 | `f2b2d7f0` | Experimental low-level network stats plugin that captures OS-level network throughput. | 初始提交，实现主机平台 OS 级网络吞吐量采集及 Insights 上报 |

### 维护评价

⚠️ **该插件自创建以来仅有一条提交记录，至今约 1 年无任何更新。**

- **状态**：实验性（`IsBetaVersion=true`），处于非常早期阶段
- **平台支持**：仅主机平台实现了采集逻辑，PC 等平台可能无法正常工作
- **API 表面积**：极小（仅 `GetSnapshot()` 一个接口），功能单一
- **风险提示**：该插件来自 Epic Games 内部需求（JIRA UE-221612），目前未见后续迭代，短期内不建议将其作为生产环境的核心依赖。仅建议用于**内部调试和性能分析**场景。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/LowLevelNetTrace)