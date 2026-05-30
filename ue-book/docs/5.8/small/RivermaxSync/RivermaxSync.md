# Rivermax Sync

> Adding NVIDIA Rivermax synchronization capabilities for nDisplay

| 属性 | 值 |
|---|---|
| 中文名 | Rivermax 同步 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RivermaxSync` (Runtime), `RivermaxSyncEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-03-22 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Rivermax/RivermaxSync) | |

## 用途

该插件为 nDisplay 多节点集群渲染提供基于 NVIDIA Rivermax 的 PTP（Precision Time Protocol）媒体输出同步能力。在虚拟制片场景中，多个 nDisplay 节点各自负责渲染画面的一部分并通过媒体输出推送到 LED 墙上，如果各节点的输出帧不同步就会出现画面撕裂或错位。RivermaxSync 利用 Rivermax 的硬件级 PTP 时间同步，确保所有集群节点在精确的同一时刻输出各自的媒体帧，从而消除视觉瑕疵。

它解决的核心问题是：**nDisplay 集群中多节点 Media Output 的帧级精确同步**。

## 使用场景

- 你在使用 nDisplay 进行大型 LED 墙虚拟制片，多台渲染机器各自输出一部分画面 → 用 RivermaxSync 保证所有机器的媒体输出帧对齐
- 你的 nDisplay 集群配备了 NVIDIA Rivermax 网卡（支持 PTP 硬件同步）→ 使用此插件的 PTP 同步策略替代基于以太网屏障的软件同步
- 你需要监控集群中各节点的 PTP 同步状态，及时发现不同步的节点 → 插件提供 Stage Monitor 事件上报 PTP 偏移量

## 蓝图用法

该插件暴露的蓝图 API 较少，核心类为可蓝图子类化的同步策略策略类。

### 核心节点

该插件的同步策略通过 nDisplay 的 Media Output Synchronization Policy 系统配置，而非直接通过蓝图节点调用。核心可配置属性如下：

| 属性 | 说明 | 所在类 |
|---|---|---|
| `MarginMs` | 同步容限，单位毫秒，范围 1-20，默认 5ms | `UMediaOutputSynchronizationPolicyRivermax` |

### 使用示例（蓝图/编辑器配置）

1. 在 nDisplay 配置中，找到媒体输出同步策略设置
2. 将同步策略类选择为 **"Rivermax (PTP)"**
3. 调整 `Margin (ms)` 属性，值越小同步精度越高，但对网络延迟要求也越高（建议 3-10ms）
4. 确保集群中所有节点的 Rivermax 网卡已正确配置 PTP 时钟同步

配置完成后，系统会自动使用 Rivermax PTP 协议进行帧同步，并通过 Stage Monitor 上报不同步节点的 PTP 帧偏移信息。

## C++ 用法

### 头文件引入

```cpp
#include "MediaOutputSynchronizationPolicyRivermax.h"
```

### 基本用法

该插件主要通过继承和注册机制工作。核心类 `UMediaOutputSynchronizationPolicyRivermax` 已在编辑器中注册为可选的同步策略，通常无需直接在 C++ 中实例化。如需以编程方式获取同步处理器：

```cpp
// 获取 Rivermax PTP 同步策略实例（Source: Public/MediaOutputSynchronizationPolicyRivermax.h）
UMediaOutputSynchronizationPolicyRivermax* SyncPolicy = NewObject<UMediaOutputSynchronizationPolicyRivermax>();

// 配置同步容限（毫秒）
SyncPolicy->MarginMs = 10.0f;

// 获取底层同步处理器
TSharedPtr<IDisplayClusterMediaOutputSynchronizationPolicyHandler> Handler = SyncPolicy->GetHandler();
```

### 进阶用法

处理 PTP 同步事件，监控集群节点的同步状态：

```cpp
// PTP 不同步事件结构体（Source: Public/MediaOutputSynchronizationPolicyRivermax.h）
// FRivermaxClusterPtpUnsyncEvent 携带各节点相对于基准节点的 PTP 帧偏移

// 监听 PTP 不同步事件时，可获取以下信息：
// - NodePtpFrameDeltas: TMap<FString, int64>，节点ID到帧偏移量的映射
// - PtpBaseNodeId: FString，作为 PTP 基准的节点ID
// - ToString(): 可读的事件描述字符串

// 示例：遍历不同步节点
FRivermaxClusterPtpUnsyncEvent PtpEvent = /* 从 Stage Monitor 获取 */;
for (const auto& [NodeId, FrameDelta] : PtpEvent.NodePtpFrameDeltas)
{
    UE_LOG(LogRivermaxSync, Warning, TEXT("Node %s is %lld frames out of PTP sync (base: %s)"),
        *NodeId, FrameDelta, *PtpEvent.PtpBaseNodeId);
}
```

## Demo 示例

```cpp
// RivermaxSyncDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaOutputSynchronizationPolicyRivermax.h"
#include "RivermaxSyncDemo.generated.h"

UCLASS()
class ARivermaxSyncDemo : public AActor
{
    GENERATED_BODY()

public:
    ARivermaxSyncDemo();

    // Rivermax PTP 同步策略实例
    UPROPERTY(EditAnywhere, Category = "Rivermax Sync")
    UMediaOutputSynchronizationPolicyRivermax* SyncPolicy;

    // 用于测试的同步容限值
    UPROPERTY(EditAnywhere, Category = "Rivermax Sync", meta = (ClampMin = "1", ClampMax = "20"))
    float SyncMarginMs = 5.0f;

    UFUNCTION(BlueprintCallable, Category = "Rivermax Sync")
    void InitializeSyncPolicy();

    UFUNCTION(BlueprintCallable, Category = "Rivermax Sync")
    FString GetPtpSyncStatus() const;
};
```

```cpp
// RivermaxSyncDemo.cpp
#include "RivermaxSyncDemo.h"

ARivermaxSyncDemo::ARivermaxSyncDemo()
{
    PrimaryActorTick.bCanEverTick = false;
    SyncPolicy = nullptr;
}

void ARivermaxSyncDemo::InitializeSyncPolicy()
{
    SyncPolicy = NewObject<UMediaOutputSynchronizationPolicyRivermax>(this);
    if (SyncPolicy)
    {
        SyncPolicy->MarginMs = SyncMarginMs;
        
        // 获取 Rivermax PTP 处理器以验证初始化
        TSharedPtr<IDisplayClusterMediaOutputSynchronizationPolicyHandler> Handler = SyncPolicy->GetHandler();
        if (Handler.IsValid())
        {
            UE_LOG(LogRivermaxSync, Log, TEXT("Rivermax PTP sync policy initialized with margin %.1f ms"), SyncMarginMs);
        }
    }
}

FString ARivermaxSyncDemo::GetPtpSyncStatus() const
{
    if (!SyncPolicy)
    {
        return TEXT("Sync policy not initialized");
    }
    return FString::Printf(TEXT("Rivermax PTP Sync - Margin: %.1f ms"), SyncPolicy->MarginMs);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RivermaxCore` | NVIDIA Rivermax 核心库，提供底层 Rivermax API 封装 |
| `RivermaxMedia` | Rivermax 媒体 I/O 模块，处理视频帧的发送/接收 |
| `DisplayCluster` / `nDisplay` | nDisplay 集群渲染框架，提供多节点同步基础设施 |

> 注：该插件还依赖 UnrealEd（编辑器功能），这在 Runtime 模块中较为少见，说明其与编辑器配置深度耦合。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `c7e14abd` | Rivermax: Added linux support for rivermax output | 新增 Linux 平台的 Rivermax 输出支持 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至 UE_LOGF 新格式 |
| 2025-09-18 | `d4ef24be` | Rivermax: Fix a possible mod 0 depending on cvar value. | 修复 CVar 值为零时可能导致模零异常的 Bug |
| 2025-09-07 | `cd57697b` | Rivermax: | Rivermax 相关改动（信息不完整） |
| 2025-04-06 | `8c1407ab` | Rivermax Plugin Refactor: | Rivermax 插件整体重构 |

### 维护评价

该插件自 2023 年创建以来保持**持续活跃维护**：

- **近期更新频繁**：2025-2026 年有多次实质性更新，包括 Bug 修复（mod 0 修复）、架构重构、平台扩展（Linux 支持）
- **仍在迭代中**：标记为 `IsBetaVersion=true`，说明仍在完善阶段
- **活跃开发**：2026 年仍有新功能（Linux 支持），表明 Epic 持续投入
- **注意事项**：作为 Beta 版本，API 和行为可能在后续版本中发生变化；仅支持 Win64 和 Linux 平台
- **推荐程度**：⭐⭐⭐☆ — 适合在受控的虚拟制片环境中使用和测试，暂不建议用于需要长期稳定性的生产环境

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Rivermax/RivermaxSync)
- [nDisplay 文档](https://docs.unrealengine.com/5.8/en-US/n-display-in-unreal-engine/)
- [Rivermax 插件源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Rivermax)