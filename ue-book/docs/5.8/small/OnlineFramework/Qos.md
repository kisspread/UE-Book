# Online Framework Plugin

> Shared code for interacting with online gameplay services.

| 属性 | 值 |
|---|---|
| 中文名 | 在线框架 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Hotfix` (Runtime), `Lobby` (Runtime), `LoginFlow` (Runtime), `Party` (Runtime), `PatchCheck` (Runtime), `PlayTimeLimit` (Runtime), `Qos` (Runtime), `Rejoin` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-13 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework) | |

## 用途

OnlineFramework 是 Epic Games 为在线游戏服务提供的**通用中间层框架**。它不是某个具体在线子系统的实现，而是为各种在线子系统（如 EOS、Steam、Xbox Live 等）提供共用的功能模块。

该插件包含以下独立功能模块：

| 模块 | 功能概述 |
|---|---|
| **Qos** | 质量服务评估——通过 ICMP Ping 测试各数据中心的延迟，自动选择最佳游戏区域（Region） |
| **Party** | 聚会/组队系统——管理玩家组队、邀请、跨平台聚会同步 |
| **Lobby** | 大厅系统——游戏大厅的创建、加入和管理 |
| **Hotfix** | 热修复——无需客户端更新即可下发服务端配置修正 |
| **LoginFlow** | 登录流程——在线服务的登录身份验证流程管理 |
| **PatchCheck** | 补丁检查——检测客户端是否需要更新补丁 |
| **PlayTimeLimit** | 游戏时长限制——家长控制相关的时间限制管理 |
| **Rejoin** | 重连机制——断线后的会话重连支持 |

这些模块被设计为**与具体平台无关**的通用实现，上层的 OnlineSubsystem（如 OnlineSubsystemEOS）会依赖这些模块来提供完整功能。

## 使用场景

- 你需要让玩家自动连接到延迟最低的服务器区域 → 使用 **Qos** 模块
- 你需要实现跨平台组队和邀请系统 → 使用 **Party** 模块
- 你需要在不发版的情况下远程修改游戏配置 → 使用 **Hotfix** 模块
- 你需要实现游戏大厅的创建和管理 → 使用 **Lobby** 模块
- 你需要检测客户端版本是否最新 → 使用 **PatchCheck** 模块
- 你需要实现断线重连 → 使用 **Rejoin** 模块

## 模块总览

### Qos（质量服务评估）

核心功能：通过 UDP Ping 测试多个数据中心的延迟，为玩家自动选择最佳区域。

**关键概念**：
- **Region**（区域）：游戏服务器的大区域划分（如 US-East、EU、Asia）
- **Datacenter**（数据中心）：区域内的具体服务器集群
- **Subspace**：数据中心的子空间（通过分隔符标识，如 `DE_S` 是 `DE` 的子空间）
- **QosEvaluator**：执行实际 Ping 测试的评估器
- **QosBeacon**：用于会话级别延迟测试的 Beacon 客户端/服务端

### Party（聚会组队）

管理玩家组队状态，支持跨平台聚会同步、邀请、加入请求等功能。

### Hotfix（热修复）

提供无需客户端更新的服务端配置下发能力，支持"启动时加载"模式。

### Lobby（大厅）

游戏大厅生命周期管理，包括创建、加入、成员管理等。

### LoginFlow（登录流程）

在线服务登录状态机，处理身份验证、Token 交换等流程。

### PatchCheck（补丁检查）

客户端版本检查，确保玩家运行最新版本。

### PlayTimeLimit（游戏时长限制）

家长控制功能，基于服务端下发的时间策略限制玩家游戏时长。

### Rejoin（重连）

断线后的会话重连支持，保存会话信息以便恢复。

## 蓝图用法

该插件大部分 API 是 C++ 接口，蓝图可直接使用的节点较少。以下是可暴露给蓝图的核心功能：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BeginQosEvaluation` | 开始异步 QoS 评估（Ping 所有数据中心） | `UQosRegionManager` |
| `GetRegionId` | 获取当前选择的区域 ID | `UQosRegionManager` / `FQosInterface` |
| `GetBestRegion` | 获取延迟最低的最佳区域 ID | `UQosRegionManager` / `FQosInterface` |
| `GetRegionOptions` | 获取所有可用区域列表 | `UQosRegionManager` / `FQosInterface` |
| `SetSelectedRegion` | 设置当前选择的区域 | `UQosRegionManager` / `FQosInterface` |
| `ForceSelectRegion` | 强制设置区域（绕过 QoS 验证） | `FQosInterface` |
| `IsUsableRegion` | 检查指定区域是否可用 | `UQosRegionManager` / `FQosInterface` |
| `IsQosEvaluationInProgress` | QoS 评估是否正在进行 | `UQosRegionManager` / `FQosInterface` |
| `GetAllSubregionPingsMap` | 获取所有子区域的延迟映射 | `UQosRegionManager` |
| `GetSubregionPreferences` | 获取指定区域内按延迟排序的子区域列表 | `UQosRegionManager` |
| `ClearSelectedRegion` | 清除已选区域（用于登出） | `FQosInterface` |
| `DumpRegionStats` | 输出当前区域/数据中心调试信息 | `FQosInterface` |

### 使用示例（蓝图描述）

**自动选择最佳区域的典型流程**：

1. 游戏启动时，调用 `BeginQosEvaluation` 开始评估
2. 绑定 `OnQosEvalComplete` 委托，等待评估完成
3. 评估完成后，调用 `GetRegionOptions` 获取可用区域列表
4. 调用 `GetBestRegion` 获取最佳区域，或让用户从列表中选择
5. 调用 `SetSelectedRegion` 设置最终区域
6. 后续的游戏会话搜索使用该区域进行

## C++ 用法

### 头文件引入

```cpp
// Qos 接口（推荐方式）
#include "QosInterface.h"

// 直接访问 RegionManager
#include "QosRegionManager.h"

// Qos Beacon（会话级延迟测试）
#include "QosBeaconClient.h"
#include "QosBeaconHost.h"
```

### 基本用法

**获取 QosInterface 单例并启动评估**：

```cpp
// 来源: Public/QosInterface.h
#include "QosInterface.h"

// 获取 Qos 接口单例
TSharedRef<FQosInterface> QosInterface = FQosInterface::Get();

// 初始化（如果需要重新创建 RegionManager）
QosInterface->Init();

// 启动异步 QoS 评估
QosInterface->BeginQosEvaluation(
    GetWorld(),
    AnalyticsProvider,  // 可选，用于上报统计
    FSimpleDelegate::CreateLambda([QosInterface]()
    {
        // 评估完成回调
        FString BestRegion = QosInterface->GetBestRegion();
        UE_LOG(LogQos, Log, TEXT("Best region: %s"), *BestRegion);
    })
);
```

**获取和设置区域**：

```cpp
// 来源: Public/QosInterface.h

// 检查评估是否完成
if (!QosInterface->IsQosEvaluationInProgress())
{
    // 获取当前区域
    FString CurrentRegion = QosInterface->GetRegionId();
    
    // 获取最佳区域
    FString BestRegion = QosInterface->GetBestRegion();
    
    // 获取所有可用区域
    const TArray<FRegionQosInstance>& Options = QosInterface->GetRegionOptions();
    for (const FRegionQosInstance& Option : Options)
    {
        UE_LOG(LogTemp, Log, TEXT("Region: %s, Usable: %d"),
            *Option.GetRegionId(), Option.IsUsable());
    }
    
    // 设置选中区域
    QosInterface->SetSelectedRegion(BestRegion);
    
    // 检查某个区域是否可用
    bool bUsable = QosInterface->IsUsableRegion(TEXT("US-East"));
}
```

**监听区域变化事件**：

```cpp
// 来源: Public/QosInterface.h

// 注册区域变化回调
QosInterface->OnQosRegionIdChanged().AddLambda(
    [](const FString& OldRegionId, const FString& NewRegionId)
    {
        UE_LOG(LogTemp, Log, TEXT("Region changed: %s -> %s"),
            *OldRegionId, *NewRegionId);
    }
);

// 注册 QoS 设置变化回调
QosInterface->RegisterQoSSettingsChangedDelegate(
    FSimpleDelegate::CreateLambda([]()
    {
        UE_LOG(LogTemp, Log, TEXT("QoS settings changed"));
    })
);
```

### 进阶用法

**获取子区域偏好和详细 Ping 数据**：

```cpp
// 来源: Public/QosRegionManager.h

UQosRegionManager* RegionManager = /* 通过某种方式获取 */;

// 获取区域内按延迟排序的子区域列表
TArray<FString> Subregions;
RegionManager->GetSubregionPreferences(TEXT("EU"), Subregions);
for (const FString& Subregion : Subregions)
{
    UE_LOG(LogTemp, Log, TEXT("Subregion: %s"), *Subregion);
}

// 获取所有子区域的延迟映射
TMap<FString, int64> PingMap = RegionManager->GetAllSubregionPingsMap();
for (const auto& Pair : PingMap)
{
    UE_LOG(LogTemp, Log, TEXT("Subregion %s: %lld ms"), *Pair.Key, Pair.Value);
}

// 获取配置中的最大允许延迟
int32 MaxPing = RegionManager->GetMaxPingMs();

// 检查子空间排序是否启用
bool bSubspaceBias = RegionManager->IsSubspaceBiasOrderEnabled();
```

**使用 QosBeacon 进行会话级延迟测试**：

```cpp
// 来源: Public/QosBeaconClient.h, Public/QosBeaconHost.h

// 服务端：创建 Qos Beacon Host
AQosBeaconHost* BeaconHost = GetWorld()->SpawnActor<AQosBeaconHost>();
BeaconHost->Init(SessionName);

// 客户端：使用 Qos Beacon Client 测试到特定会话的延迟
AQosBeaconClient* BeaconClient = /* 通过连接获得 */;

// 监听响应
BeaconClient->OnQosRequestComplete().BindLambda(
    [](EQosResponseType Response, int32 ResponseTimeMs)
    {
        if (Response == EQosResponseType::Success)
        {
            UE_LOG(LogTemp, Log, TEXT("Qos response time: %d ms"), ResponseTimeMs);
        }
    }
);

// 发送 QoS 请求
BeaconClient->SendQosRequest(DesiredSessionResult);
```

## Demo 示例

以下示例展示如何在游戏模块中集成 QoS 区域选择：

```cpp
// MyGameModule.h
#pragma once

#include "CoreMinimal.h"
#include "QosInterface.h"

class FMyGameModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    /** 启动区域评估并获取最佳区域 */
    void EvaluateAndSelectRegion();

    /** 获取当前选中的区域 */
    FString GetCurrentRegion() const;

private:
    void OnQosEvalComplete();
    void OnRegionChanged(const FString& OldRegionId, const FString& NewRegionId);

    FDelegateHandle RegionChangedHandle;
};
```

```cpp
// MyGameModule.cpp
#include "MyGameModule.h"
#include "QosInterface.h"
#include "QosModule.h"

#define LOCTEXT_NAMESPACE "MyGameModule"

void FMyGameModule::StartupModule()
{
    if (FQosModule::IsAvailable())
    {
        TSharedRef<FQosInterface> QosInterface = FQosInterface::Get();
        QosInterface->Init();

        // 监听区域变化
        RegionChangedHandle = QosInterface->OnQosRegionIdChanged().AddRaw(
            this, &FMyGameModule::OnRegionChanged);
    }
}

void FMyGameModule::ShutdownModule()
{
    if (FQosModule::IsAvailable())
    {
        TSharedRef<FQosInterface> QosInterface = FQosInterface::Get();
        QosInterface->OnQosRegionIdChanged().Remove(RegionChangedHandle);
        
        // 登出时清除区域
        QosInterface->ClearSelectedRegion();
    }
}

void FMyGameModule::EvaluateAndSelectRegion()
{
    if (!FQosModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("Qos module not available"));
        return;
    }

    TSharedRef<FQosInterface> QosInterface = FQosInterface::Get();

    if (QosInterface->IsQosEvaluationInProgress())
    {
        UE_LOG(LogTemp, Warning, TEXT("QoS evaluation already in progress"));
        return;
    }

    // 启动评估，使用空的 AnalyticsProvider
    QosInterface->BeginQosEvaluation(
        GWorld->GetWorld(),
        nullptr,
        FSimpleDelegate::CreateRaw(this, &FMyGameModule::OnQosEvalComplete)
    );
}

void FMyGameModule::OnQosEvalComplete()
{
    TSharedRef<FQosInterface> QosInterface = FQosInterface::Get();

    // 检查是否找到所有区域
    if (!QosInterface->AllRegionsFound())
    {
        UE_LOG(LogTemp, Warning, TEXT("Not all regions were found during QoS eval"));
    }

    // 获取最佳区域
    FString BestRegion = QosInterface->GetBestRegion();
    UE_LOG(LogTemp, Log, TEXT("Best region determined: %s"), *BestRegion);

    // 设置选中区域
    QosInterface->SetSelectedRegion(BestRegion);

    // 列出所有可用选项
    const TArray<FRegionQosInstance>& Options = QosInterface->GetRegionOptions();
    for (const FRegionQosInstance& Option : Options)
    {
        if (Option.IsUsable())
        {
            FString BestSubregion = Option.GetBestSubregion();
            int32 BestPing = Option.GetBestAvgPing();
            UE_LOG(LogTemp, Log, TEXT("  Region %s: best subregion=%s, ping=%dms"),
                *Option.GetRegionId(), *BestSubregion, BestPing);
        }
    }
}

void FMyGameModule::OnRegionChanged(const FString& OldRegionId, const FString& NewRegionId)
{
    UE_LOG(LogTemp, Log, TEXT("Region changed from '%s' to '%s'"),
        *OldRegionId, *NewRegionId);
}

FString FMyGameModule::GetCurrentRegion() const
{
    if (FQosModule::IsAvailable())
    {
        return FQosInterface::Get()->GetRegionId();
    }
    return TEXT("NONE");
}

#undef LOCTEXT_NAMESPACE
```

## 模块依赖

该插件的 Party 模块显式依赖 `OnlineSubsystemGDK`（Xbox 平台相关）。

| 模块 | 用途 |
|---|---|
| `OnlineSubsystemGDK` | Party 模块依赖，Xbox/PC 平台在线子系统 |
| `OnlineSubsystem` | Qos 模块隐式依赖的基础在线子系统 |
| `Icmp` | Qos 模块使用的 ICMP Ping 库 |

无其他特殊依赖（仅标准 Core/Engine/Slate/Networking 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `09a2dfc6` | [Hotfix on Load] Fix issue where certain baked hotfixes will not apply when no backend hotfixes exis | 修复内置热修复在无后端配置时无法生效的问题 |
| 2026-05-12 | `0b9170a8` | Guard Invite and RTJ social party calls when epic parties mirroring is enabled. | 当 Epic 聚会镜像启用时保护邀请和加入请求调用 |
| 2026-04-30 | `fe1eaff2` | Add a hook for PartyPlatformSessionMonitor to allow the game party to add a special key to the platf | 为 PartyPlatformSessionMonitor 添加钩子以支持自定义平台会话键 |
| 2026-04-29 | `0badc43f` | Restore LogHotfixManager summary logs for hotfix on load | 恢复热修复加载时的摘要日志输出 |
| 2026-04-28 | `85cae1c6` | Broadcast party initialization after we've processed our first update | 在处理首次更新后广播聚会初始化完成事件 |

### 维护评价

**维护状态：活跃维护中**

- **创建时间**：2016 年 7 月，已维护超过 9 年
- **更新频率**：2026 年 4-5 月仍有密集更新（每周多次提交），涉及 Hotfix、Party 等多个模块
- **更新内容**：包含功能增强（钩子添加）、Bug 修复（热修复应用问题）、行为改进（聚会保护机制）等实质性改动
- **定位重要性**：作为 Epic 在线游戏基础设施的核心框架层，被 Fortnite 等大型项目深度使用
- **默认启用**：`EnabledByDefault=false`，需要手动启用，适用于需要在线功能的项目
- **已知限制**：该插件提供的是通用框架，实际的在线服务功能需要配合具体的 OnlineSubsystem 插件（如 OnlineSubsystemEOS）使用

**推荐使用**：如果你的项目需要任何在线多人游戏功能（区域选择、组队、大厅、热修复等），强烈推荐启用此插件作为基础设施层。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework)
- [官方文档]()（未提供）