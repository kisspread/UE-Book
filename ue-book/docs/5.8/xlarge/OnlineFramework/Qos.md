# Online Framework Plugin

> Shared code for interacting with online gameplay services.

| 属性 | 值 |
|---|---|
| 中文名 | 在线框架 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（运行时模块、基础网络服务） |
| 模块 | `Qos` (Runtime), `Party` (Runtime), `Lobby` (Runtime), `LoginFlow` (Runtime), `Hotfix` (Runtime), `PatchCheck` (Runtime), `PlayTimeLimit` (Runtime), `Rejoin` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-13 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework) | |

## 用途

`OnlineFramework` 是 UE 在线游戏服务的**底层基础框架插件**。它并不直接对接具体平台（如 Steam, PlayStation Network），而是提供一系列平台无关的、标准化的在线游戏服务抽象。这些服务包括：自动选择最优服务器区域的 **QoS（服务质量）评测**、玩家之间的 **Party（派对）系统**、游戏 **Lobby（大厅）** 管理、热修复 **Hotfix** 应用、登录流程控制等。

该插件存在的意义在于为上层的 `OnlineSubsystem` 插件（如 `OnlineSubsystemSteam`, `OnlineSubsystemLive`）提供可复用的基础功能。开发者通常不直接使用 `OnlineFramework`，而是通过具体的 `OnlineSubsystem` 插件间接使用其能力。它**默认禁用**，需要被依赖它的 `OnlineSubsystem` 插件显式启用。

## 使用场景

- 你正在开发一款需要多人在线的竞技游戏（如大逃杀、MOBA），需要为玩家**自动选择延迟最低的服务器区域**。
- 你需要一个与平台无关的**游戏派对系统**，让玩家能够组队、邀请好友、准备就绪。
- 你的游戏需要动态下载和应用**热修复补丁**，而无需客户端重启。
- 你需要管理**登录流程**、**游戏版本检查**以及**游戏时长限制**（针对家长控制）等通用在线服务。

## 模块总览

`OnlineFramework` 插件由多个独立的运行时模块组成，每个模块负责特定的在线服务功能：

| 模块 | 主要职责 |
|---|---|
| **Qos** | **服务质量评测**。通过 Ping 测试多个数据中心，评估延迟，帮助客户端自动选择最佳游戏区域。 |
| **Party** | **派对系统**。管理玩家组队、邀请、状态同步和准备流程。 |
| **Lobby** | **游戏大厅**。提供创建、搜索和加入游戏大厅的功能，是匹配和会话的基础设施。 |
| **Hotfix** | **热修复**。允许从后端服务器动态下载配置或代码补丁，并在不重启客户端的情况下应用。 |
| **LoginFlow** | **登录流程**。定义和管理玩家登录游戏的标准流程和状态机。 |
| **PatchCheck** | **版本检查**。在游戏启动时检查客户端版本是否需要更新。 |
| **PlayTimeLimit** | **游戏时长限制**。实现基于时间的游戏游玩限制功能，常用于家长控制系统。 |
| **Rejoin** | **重新加入**。提供玩家意外断开后重新加入上一场游戏的机制。 |

## Qos 模块详解

Qos (Quality of Service) 模块是 `OnlineFramework` 中最核心和复杂的模块之一。它负责通过 ICMP Ping 测试一系列预定义的 QoS 服务器，评估网络延迟，从而确定客户端与各个数据中心的连接质量。

### 核心类与结构

1.  **`UQosRegionManager`**：Qos 模块的核心管理器。
    *   负责启动异步 QoS 评测 (`BeginQosEvaluation`)。
    *   管理所有可用区域 (`FQosRegionInfo`) 和数据中心 (`FQosDatacenterInfo`) 的元数据。
    *   存储和更新评测结果 (`TArray<FRegionQosInstance> RegionOptions`)。
    *   处理命令行覆盖 (`ForceRegionId`) 和配置参数（如 `NumTestsPerRegion`， `PingTimeout`）。

2.  **`FQosInterface`**：Qos 模块的对外接口（单例）。
    *   提供了访问 `UQosRegionManager` 功能的简洁API。
    *   其他模块（如具体 `OnlineSubsystem`）通过 `FQosModule::Get().GetQosInterface()` 获取此接口来查询区域信息。

3.  **`UQosEvaluator`**：实际执行 Ping 测试的评估器。
    *   由 `UQosRegionManager` 创建和管理。
    *   使用 `FIcmpEchoMany` 异步批量 Ping 多个目标服务器。
    *   收集并计算每个数据中心的平均延迟。

4.  **`AQosBeaconClient` / `AQosBeaconHost`**：基于网络信标 (Beacon) 的 QoS 测试客户端/主机。
    *   用于测试与特定游戏会话（Session）服务器的连接质量，与基于数据中心的通用 Ping 测试互补。

### 核心数据结构

*   **`FQosRegionInfo`**：描述一个逻辑区域（如 “NA”, “EU”）。包含区域ID、显示名称、是否启用、是否对用户可见等。
*   **`FQosDatacenterInfo`**：描述一个具体的数据中心。属于某个区域 (`RegionId`)，包含一组 Ping 服务器地址 (`TArray<FQosPingServerInfo> Servers`)。
*   **`FDatacenterQosInstance`**：单个数据中心的**运行时评测实例**。包含其静态定义 (`FQosDatacenterInfo Definition`)、评测结果 (`EQosDatacenterResult Result`)、平均延迟 (`AvgPingMs`) 和历史 Ping 值。
*   **`FRegionQosInstance`**：单个逻辑区域的运行时实例，包含其下所有数据中心的评测选项 (`TArray<FDatacenterQosInstance> DatacenterOptions`)。可提供该区域的最佳延迟 (`GetBestAvgPing`) 和首选子区域 (`GetBestSubregion`)。

### 子空间 (Subspace) 偏置排序

Qos 模块支持一种高级排序逻辑，当同一个区域内存在 “子空间” (Subspace，如 “DE_S”) 和 “非子空间” (Non-Subspace, 如 “DE”) 数据中心时，可以**有偏向地优先推荐非子空间**，即使它的 Ping 稍高。这通过 `FQosSubspaceComparisonParams` 配置一系列规则（如最大 Ping 差值、比例阈值等）来实现，由 `FDatacenterQosInstance::IsLessWhenBiasedTowardsNonSubspace` 和相关静态函数执行。

### 蓝图用法

Qos 模块主要面向 C++ 运行时逻辑，不直接暴露大量蓝图节点。其主要输出——最佳区域信息——通常由上层的 `OnlineSubsystem` 蓝图库（如 `OnlineSubsystem` 提供的会话搜索节点）间接使用。

### C++ 用法

#### 基本用法：启动 QoS 评测并获取最佳区域

```cpp
// 引入必要的头文件
#include "QosInterface.h"
#include "QosRegionManager.h"

// 在合适的地方（如游戏初始化）启动QoS评测
void UMyGameInstance::StartQosCheck()
{
    TSharedRef<FQosInterface> QosInterface = FQosModule::Get().GetQosInterface();
    
    // 确保接口已初始化
    if (QosInterface->Init())
    {
        // 启动异步评测，完成后执行回调
        QosInterface->BeginQosEvaluation(GetWorld(), GetAnalyticsProvider(), 
            FSimpleDelegate::CreateUObject(this, &UMyGameInstance::OnQosEvalComplete));
    }
}

// QoS评测完成回调
void UMyGameInstance::OnQosEvalComplete()
{
    TSharedRef<FQosInterface> QosInterface = FQosModule::Get().GetQosInterface();
    
    // 获取推荐的最佳区域ID
    FString BestRegion = QosInterface->GetBestRegion();
    UE_LOG(LogTemp, Log, TEXT("QoS evaluation complete. Best region: %s"), *BestRegion);
    
    // 获取所有可选区域（可用于显示区域选择UI）
    const TArray<FRegionQosInstance>& RegionOptions = QosInterface->GetRegionOptions();
    for (const FRegionQosInstance& Region : RegionOptions)
    {
        UE_LOG(LogTemp, Log, TEXT("Region: %s, Best Ping: %dms"), 
            *Region.GetRegionId(), Region.GetBestAvgPing());
    }
    
    // 设置选定区域（通常基于自动检测或用户选择）
    if (QosInterface->IsUsableRegion(BestRegion))
    {
        QosInterface->SetSelectedRegion(BestRegion);
    }
}
```

#### 进阶用法：监听区域变更事件

```cpp
// 在类头文件中声明委托句柄
FDelegateHandle OnRegionChangedHandle;

// 开始监听
void UMyGameSubsystem::SubscribeToRegionChanges()
{
    TSharedRef<FQosInterface> QosInterface = FQosModule::Get().GetQosInterface();
    OnRegionChangedHandle = QosInterface->OnQosRegionIdChanged().AddUObject(
        this, &UMyGameSubsystem::HandleRegionChanged);
}

// 回调处理函数
void UMyGameSubsystem::HandleRegionChanged(const FString& OldRegionId, const FString& NewRegionId)
{
    UE_LOG(LogTemp, Warning, TEXT("QoS Region changed from %s to %s"), *OldRegionId, *NewRegionId);
    // 在这里执行区域切换后的逻辑，如重新建立连接等
}

// 取消监听
void UMyGameSubsystem::UnsubscribeFromRegionChanges()
{
    TSharedRef<FQosInterface> QosInterface = FQosModule::Get().GetQosInterface();
    QosInterface->OnQosRegionIdChanged().Remove(OnRegionChangedHandle);
}
```

## 其他模块简介

*   **Party**：提供 `UOnlinePartySubsystem` 等接口，用于创建派对、邀请玩家、同步成员状态和准备情况。其会话管理可能与平台特定的会话系统集成。
*   **Lobby**：提供大厅的创建、搜索和加入功能，是构建匹配系统的基础。
*   **Hotfix**：通过 `UHotfixSubsystem` 管理热修复内容的下载和应用，支持 “立即加载” 和 “启动时加载” 两种模式。
*   **LoginFlow**：定义登录过程中的各个状态和转换，为登录界面提供状态驱动。
*   **PatchCheck**：在游戏启动初期检查应用版本，必要时提示或强制更新。
*   **PlayTimeLimit**：实现基于时间的游玩限制，通常与平台家长控制系统联动。
*   **Rejoin**：保存玩家上一场游戏的信息，允许其在断线后快速重新加入。

## 模块依赖

由于 `OnlineFramework` 是一个基础框架，其各个模块的依赖较为底层。使用它的 `OnlineSubsystem` 插件需要依赖这些模块。

| 模块 | 用途 |
|---|---|
| `OnlineSubsystem` | 核心在线子系统抽象层。**所有模块都间接依赖它**，这是 `OnlineFramework` 存在的基础。 |
| `OnlineSubsystemUtils` | 提供 `OnlineSubsystem` 相关的通用工具和蓝图支持。 |
| `OnlineSubsystemGDK` | (特定于Party模块) 用于 Xbox/GDK 平台的特定在线服务集成。 |
| `Networking` | 底层网络通信。 |
| `Sockets` | Socket 网络编程。 |
| `ICMP` | 用于执行 Ping 操作。 |
| `Beacon` | 网络信标系统，用于轻量级客户端-主机通信（如 QosBeacon）。 |
| `Json` | 用于处理配置和数据交换。 |
| `Analytics` | 用于收集和上报 QoS 评测等分析数据。 |
| `HTTP` | 用于热修复内容的下载。 |

**注**：对于最终项目，你通常不需要直接依赖 `OnlineFramework`。你只需依赖对应的 `OnlineSubsystem` 插件（如 `OnlineSubsystemSteam`），该插件会声明对所需 `OnlineFramework` 模块的依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `09a2dfc6` | [Hotfix on Load] Fix issue where certain baked hotfixes will not apply when no backend hotfixes exis | 修复了在无后端热修复时，某些内置热修复无法应用的问题。 |
| 2026-05-12 | `0b9170a8` | Guard Invite and RTJ social party calls when epic parties mirroring is enabled. | 当启用 Epic 派对镜像功能时，保护邀请和“加入对方游戏”的社交派对调用。 |
| 2026-04-30 | `fe1eaff2` | Add a hook for PartyPlatformSessionMonitor to allow the game party to add a special key to the platf | 为 `PartyPlatformSessionMonitor` 添加钩子，允许游戏派对向平台会话中添加特殊密钥。 |
| 2026-04-29 | `0badc43f` | Restore LogHotfixManager summary logs for hotfix on load | 恢复了 `HotfixManager` 关于“加载时热修复”的摘要日志输出。 |
| 2026-04-28 | `85cae1c6` | Broadcast party initialization after we've processed our first update | 在我们处理完第一次派对更新后，再广播派对初始化完成事件。 |

### 维护评价

`OnlineFramework` 是一个**仍在活跃维护**的关键基础设施插件。

*   **年龄**：创建于 2016 年，已有 8 年历史，是 UE 在线功能的基石。
*   **活跃度**：从近期提交记录看，**2026 年 4 月至 5 月仍有功能增强和 Bug 修复**，特别是针对 Hotfix 和 Party 模块，说明 Epic 仍在积极投入。
*   **状态**：作为基础框架，其核心逻辑稳定，更新主要是适配新平台（如 GDK）和改进现有子系统（Party, Hotfix）。
*   **推荐度**：**强烈推荐**。如果你使用任何标准的 `OnlineSubsystem` 插件进行多人游戏开发，你已经在间接使用它。它的存在使得在线功能的开发更加模块化和标准化。

## 相关链接

*   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework)
*   [官方文档](https://docs.unrealengine.com/5.8/en-US/online-subsystem-plugin-in-unreal-engine/)（注：此为通用在线子系统文档，OnlineFramework 是其底层实现的一部分）
*   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework/Source/Qos/Tests)（以 Qos 模块为例，其他模块测试路径类似）