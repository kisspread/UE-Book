# Online Framework Plugin

> Shared code for interacting with online gameplay services.

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Qos` (Runtime), `Party` (Runtime), `Lobby` (Runtime), `Hotfix` (Runtime), `LoginFlow` (Runtime), `PatchCheck` (Runtime), `PlayTimeLimit` (Runtime), `Rejoin` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-12 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineFramework) | |

## 用途

OnlineFramework 是 Epic 为在线游戏服务提供的**共享基础设施插件**。它不是一个完整的在线子系统实现，而是提供了一组独立的、可复用的运行时模块，用于解决在线游戏中的常见问题：

- **Qos**：服务器质量评估（延迟测量、区域选择）
- **Party**：玩家组队/派对系统
- **Lobby**：大厅/房间管理
- **Hotfix**：运行时热修复机制
- **LoginFlow**：登录流程管理
- **PatchCheck**：版本/补丁检查
- **PlayTimeLimit**：游戏时长限制（防沉迷）
- **Rejoin**：断线重连支持

这些模块设计为与具体的在线子系统（如 EOS、Steam）解耦，提供通用的在线功能抽象层。**默认不启用**，需要在项目设置中手动开启所需模块。

## 使用场景

- 你需要为多人游戏选择最佳服务器区域 → 用 **Qos** 模块
- 你需要实现玩家组队/派对功能 → 用 **Party** 模块
- 你需要游戏大厅/房间匹配 → 用 **Lobby** 模块
- 你需要在不更新客户端的情况下修复服务端问题 → 用 **Hotfix** 模块
- 你需要检查客户端版本是否最新 → 用 **PatchCheck** 模块
- 你需要实现防沉迷/游戏时长限制 → 用 **PlayTimeLimit** 模块
- 你需要断线后重新加入游戏 → 用 **Rejoin** 模块

## 模块概览

| 模块 | 功能 | 文档 |
|---|---|---|
| **Qos** | 服务器质量评估、区域选择、延迟测量 | [Qos.md](Qos.md) |
| **Party** | 玩家组队/派对系统 | 待补充 |
| **Lobby** | 游戏大厅/房间管理 | 待补充 |
| **Hotfix** | 运行时热修复 | 待补充 |
| **LoginFlow** | 登录流程管理 | 待补充 |
| **PatchCheck** | 版本/补丁检查 | 待补充 |
| **PlayTimeLimit** | 游戏时长限制 | 待补充 |
| **Rejoin** | 断线重连 | 待补充 |

## 维护状态

### 近期更新

```
- e2c4240ef205 [QoS] GetSubregionPreferences - Return all subregions sorted by ping.
- 93a13080d9ef Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar instead of on types.
- 66e9bb39ff7e Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base
```

- `e2c4240`：Qos 模块功能更新，改进子区域偏好返回逻辑
- `93a1308`：构建系统重构，统一 DLL 导出声明方式
- `66e9bb3`：代码清理，移除 5.2 版本废弃的 include 顺序兼容代码

### 维护评价

OnlineFramework 作为 Epic 官方维护的在线基础设施插件，持续获得更新。最近的提交涉及功能改进和代码现代化，表明仍在**活跃维护**中。该插件默认不启用（`EnabledByDefault: false`），说明它面向有特定在线需求的项目，而非通用功能。作为 2016 年创建的插件，经过近 9 年的迭代，已经相当成熟稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineFramework)

---

# Qos 模块

> 服务器质量评估（Quality of Service）模块，用于测量服务器延迟并帮助客户端选择最佳游戏区域。

## 用途

Qos 模块解决了多人游戏中的一个核心问题：**如何让玩家连接到延迟最低的服务器？**

它通过以下机制实现：
1. **区域发现**：获取所有可用的游戏服务器区域
2. **延迟测量**：使用 Beacon 系统对每个区域进行 ping 测试
3. **区域选择**：基于测量结果推荐最佳区域
4. **子区域优化**：在同一区域内选择最优的子区域

该模块使用 UE 的 Beacon 网络系统（而非 ICMP ping），可以穿透 NAT 并获得更准确的游戏延迟数据。

## 蓝图用法

Qos 模块主要是 C++ 接口，蓝图直接使用较少。但可以通过 `UQosRegionManager` 访问区域信息。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetRegionId` | 获取当前选中的区域 ID | `FQosInterface` |
| `GetBestRegion` | 获取延迟最低的区域 ID | `FQosInterface` |
| `GetRegionOptions` | 获取所有可用区域列表 | `FQosInterface` |
| `SetSelectedRegion` | 设置选中的区域 | `FQosInterface` |
| `IsUsableRegion` | 检查区域是否可用 | `FQosInterface` |
| `BeginQosEvaluation` | 开始异步 QoS 评估 | `FQosInterface` |

### 使用示例（蓝图描述）

由于 Qos 主要是 C++ 接口，典型使用流程：

1. 在游戏启动时调用 `BeginQosEvaluation` 开始评估
2. 监听 `OnQosEvalComplete` 委托
3. 评估完成后调用 `GetRegionOptions` 获取可用区域
4. 调用 `GetBestRegion` 或 `GetSubregionPreferences` 获取推荐区域
5. 调用 `SetSelectedRegion` 设置最终选择

## C++ 用法

### 头文件引入

```cpp
#include "QosInterface.h"
#include "QosRegionManager.h"
```

### 基本用法

```cpp
// 获取 Qos 接口单例
TSharedRef<FQosInterface> QosInterface = FQosInterface::Get();

// 初始化
QosInterface->Init();

// 开始 QoS 评估
QosInterface->BeginQosEvaluation(
    GetWorld(),
    AnalyticsProvider,
    FSimpleDelegate::CreateLambda([QosInterface]()
    {
        // 评估完成回调
        FString BestRegion = QosInterface->GetBestRegion();
        UE_LOG(LogTemp, Log, TEXT("Best region: %s"), *BestRegion);
    })
);
```

### 进阶用法

```cpp
// 获取所有可用区域并选择
const TArray<FRegionQosInstance>& RegionOptions = QosInterface->GetRegionOptions();

for (const FRegionQosInstance& Region : RegionOptions)
{
    UE_LOG(LogTemp, Log, TEXT("Region: %s, Ping: %d ms"), 
        *Region.RegionId, Region.PingMs);
}

// 获取子区域偏好
TArray<FString> Subregions;
QosInterface->GetSubregionPreferences(SelectedRegionId, Subregions);

// 设置选中区域
if (QosInterface->IsUsableRegion(DesiredRegionId))
{
    QosInterface->SetSelectedRegion(DesiredRegionId);
}

// 监听评估完成
QosInterface->OnQosEvalComplete().AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("QoS evaluation complete"));
});
```

## Demo 示例

### QosRegionSelector.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "QosRegionSelector.generated.h"

class FQosInterface;

UCLASS()
class AQosRegionSelector : public AActor
{
    GENERATED_BODY()

public:
    AQosRegionSelector();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "QoS")
    void StartRegionEvaluation();

    UFUNCTION(BlueprintCallable, Category = "QoS")
    FString GetRecommendedRegion() const;

    UFUNCTION(BlueprintCallable, Category = "QoS")
    TArray<FString> GetAvailableRegions() const;

    DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnRegionEvaluationComplete);

    UPROPERTY(BlueprintAssignable, Category = "QoS")
    FOnRegionEvaluationComplete OnRegionEvaluationComplete;

private:
    void OnQosEvaluationComplete();

    TSharedPtr<FQosInterface> QosInterface;
};
```

### QosRegionSelector.cpp

```cpp
#include "QosRegionSelector.h"
#include "QosInterface.h"
#include "QosModule.h"

AQosRegionSelector::AQosRegionSelector()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AQosRegionSelector::BeginPlay()
{
    Super::BeginPlay();

    // 获取 Qos 接口
    if (FQosModule::IsAvailable())
    {
        QosInterface = &FQosModule::Get().GetQosInterface();
        QosInterface->Init();
    }
}

void AQosRegionSelector::StartRegionEvaluation()
{
    if (!QosInterface.IsValid())
    {
        return;
    }

    QosInterface->BeginQosEvaluation(
        GetWorld(),
        nullptr, // AnalyticsProvider
        FSimpleDelegate::CreateUObject(this, &AQosRegionSelector::OnQosEvaluationComplete)
    );
}

FString AQosRegionSelector::GetRecommendedRegion() const
{
    if (!QosInterface.IsValid())
    {
        return TEXT("NONE");
    }

    return QosInterface->GetBestRegion();
}

TArray<FString> AQosRegionSelector::GetAvailableRegions() const
{
    TArray<FString> RegionIds;

    if (!QosInterface.IsValid())
    {
        return RegionIds;
    }

    const TArray<FRegionQosInstance>& Options = QosInterface->GetRegionOptions();
    for (const FRegionQosInstance& Region : Options)
    {
        RegionIds.Add(Region.RegionId);
    }

    return RegionIds;
}

void AQosRegionSelector::OnQosEvaluationComplete()
{
    UE_LOG(LogTemp, Log, TEXT("QoS evaluation complete. Best region: %s"), 
        *GetRecommendedRegion());

    OnRegionEvaluationComplete.Broadcast();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OnlineSubsystemUtils` | 在线子系统工具类，提供 Beacon 基础设施 |
| `OnlineSubsystem` | 在线子系统接口 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineFramework/Source/Qos)