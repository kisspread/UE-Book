# ConcertInsightsServer

> Listens for requests of clients to start synchronized tracing, which is initiated in the ConcertInsightsClient plugin.

| 属性 | 值 |
|---|---|
| 中文名 | 协同跟踪服务器 |
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ConcertInsightsServer` (Runtime) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2024-05-06 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertInsights/ConcertInsightsServer) | |

## 用途

ConcertInsightsServer 是 Unreal Insights 跟踪系统在多人协作开发（Concert）场景下的**服务端组件**。它的核心功能是作为“协调者”，监听来自 ConcertInsightsClient 插件的同步跟踪请求，并协调所有参与同一 Concert 会话的客户端和服务器一起启动或停止跟踪。

**它解决的问题是**：在多人开发环境中，需要对分布在多台机器上的多个游戏实例进行**同步的性能分析和调试数据收集**。例如，你需要分析网络同步延迟或特定帧在不同客户端和服务器上的表现，就需要在同一时间点对所有相关进程启动跟踪。此插件提供了实现该功能的服务端逻辑。

## 使用场景

- **多人协作开发调试**：你的团队在使用 Unreal 的多人会话（Concert）功能进行协作，需要分析多人游戏中的同步问题或网络性能。
- **端到端性能分析**：你需要收集来自客户端和服务器的一套相关联的跟踪数据，以便在 Unreal Insights 中进行对比分析。

## 蓝图用法

此插件主要是一个服务端逻辑模块，其核心类（如 `FServerTraceControls`）并未暴露公开的蓝图 API。同步跟踪的发起和状态监控通常通过 `ConcertInsightsClient` 插件的状态栏 UI 或 C++ 接口进行。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsAvailable` | 检查 ConcertInsightsServer 模块是否已加载并可用 | `IConcertInsightsServerModule` |

**使用示例（蓝图描述）**
在你的蓝图或 C++ 代码中，可以通过 `IConcertInsightsServerModule::IsAvailable()` 来安全地检查该插件功能是否就绪，然后再尝试获取模块实例。

## C++ 用法

### 头文件引入

```cpp
#include "IConcertInsightsServerModule.h"
```

### 基本用法

检查模块是否可用并获取其接口。

```cpp
// 检查 ConcertInsightsServer 模块是否加载
if (UE::ConcertInsightsServer::IConcertInsightsServerModule::IsAvailable())
{
    // 获取模块接口引用（通常是单例）
    UE::ConcertInsightsServer::IConcertInsightsServerModule& ServerModule = UE::ConcertInsightsServer::IConcertInsightsServerModule::Get();
    // ... 可以通过 ServerModule 进行操作，但当前公开接口有限
}
```

*来源： `IConcertInsightsServerModule.h`*

### 进阶用法

此插件的主要逻辑封装在内部类 `FServerTraceControls` 中，用于监听 Concert 服务器事件并管理同步跟踪的状态。它是一个运行时模块，会自动在模块启动时实例化并注册事件处理器。**普通开发者通常无需直接与之交互**，其行为由系统（Concert）和 `ConcertInsightsClient` 触发。

## Demo 示例

这是一个最小示例，展示如何在 C++ 代码中安全地检查 `ConcertInsightsServer` 模块是否可用。由于该插件主要提供后台服务，没有直接的用户操作代码。

```cpp
// MyActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyActor.generated.h"

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()

public:
    AMyActor();

    UFUNCTION(BlueprintCallable, Category = "Debug")
    void CheckConcertInsightsServerStatus();

private:
    void LogMessage(const FString& Message);
};
```

```cpp
// MyActor.cpp
#include "MyActor.h"
#include "IConcertInsightsServerModule.h" // 引入插件模块接口头文件

AMyActor::AMyActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyActor::CheckConcertInsightsServerStatus()
{
    // 使用插件提供的静态函数检查模块是否加载
    if (UE::ConcertInsightsServer::IConcertInsightsServerModule::IsAvailable())
    {
        LogMessage(TEXT("ConcertInsightsServer 模块已加载并可用。"));
    }
    else
    {
        LogMessage(TEXT("ConcertInsightsServer 模块未加载。请检查插件设置。"));
    }
}

void AMyActor::LogMessage(const FString& Message)
{
    UE_LOG(LogTemp, Log, TEXT("%s"), *Message);
}
```

## 模块依赖

此插件的 `Build.cs` 文件中声明了依赖。要使用它，你的模块可能需要链接以下模块：

| 模块 | 用途 |
|---|---|
| `ConcertSyncCore` | 提供 Concert 多人会话同步的核心接口和结构 |
| `ConcertInsightsCore` | 提供 `ConcertInsightsClient` 和 `ConcertInsightsServer` 共享的跟踪控制逻辑 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-05-06 | `ef1d668c` | Extend Unreal Insights to allow tracing protocols accross multiple machines participating in a Multi User session. | 创建插件，实现跨机器多人会话同步跟踪的服务端监听功能。 |

### 维护评价

- **创建时间**：该插件于 2024 年 5 月创建，非常年轻。
- **近期活动**：在创建提交后，没有新的功能更新记录。
- **维护状态**：**维护不活跃**。自创建以来约一年半没有实质性功能更新或bug修复的提交记录。
- **已知问题与限制**：作为 `IsExperimentalVersion=true` 的实验性插件，其 API 和行为可能不稳定，且默认不启用。
- **推荐使用**：**谨慎使用**。该插件属于实验性功能，主要用于 Epic 内部或特定的多人调试场景。对于大多数项目，除非有明确的多人同步跟踪需求，否则无需启用或依赖此插件。建议关注 `ConcertInsightsVisualizer`（分析端）的更新以判断该工具链的整体活跃度。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertInsights/ConcertInsightsServer)
- 官方文档：无
- 测试用例：未在插件目录内找到测试文件。