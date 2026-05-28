# ConcertInsightsCore

> Shared logic for starting synchronized tracing

| 属性 | 值 |
|---|---|
| 中文名 | 多用户同步追踪核心 |
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ConcertInsightsCore` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-05-06 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertInsights/ConcertInsightsCore) | |

## 用途

ConcertInsightsCore 是 ConcertInsights 系列插件的**底层共享模块**，为 Multi-User Editing（多用户协作编辑）会话提供跨机器同步追踪的基础能力。

**解决的核心问题**：在多用户协作编辑时，多台机器各自独立运行 Unreal Insights 追踪，生成的 `.utrace` 文件之间没有关联，无法在分析时对应到同一时刻的事件。ConcertInsightsCore 提供了：

1. **同步启动追踪**：通过 Concert 网络会话，向所有参与协作的机器发送"同时开始追踪"的指令，确保各机器的追踪时间线一致。
2. **初始化事件关联**：每个机器在开始追踪时发送带有唯一序列 ID 的初始化事件，使得 Unreal Insights 分析工具能够将多个 `.utrace` 文件聚合展示。
3. **远程请求处理**：监听来自其他端点的追踪启动/停止请求，并做出响应。

此插件本身是 **Hidden** 的（不会出现在插件浏览器中），它是 `ConcertInsightsClient` 和 `ConcertInsightsServer` 的内部依赖，不面向最终用户直接使用。

## 使用场景

- 你在使用 Multi-User Editing 进行多人协作时，需要**同时对所有参与机器开启性能追踪**，以便在 Unreal Insights 中对照分析网络事件延迟和同步问题
- 你正在开发 ConcertInsights 系列的自定义扩展，需要基于 `FTraceControls` 基类实现自己的追踪控制逻辑
- 你需要解析 Concert 同步追踪的网络消息结构（`FConcertTrace_StartSyncTrace_Request` 等 USTRUCT）

## 蓝图用法

本插件主要面向 C++ 层，没有 `BlueprintCallable` 函数。但以下 USTRUCT 具有 `UPROPERTY` 标记，可在蓝图中作为数据结构使用：

### 可用数据结构

| 结构体 | 说明 |
|---|---|
| `FConcertTrace_StartTraceArgs` | 追踪启动参数（连接类型、目标地址、通道） |
| `FConcertTrace_StartSyncTrace_Request` | 同步追踪启动请求消息 |
| `FConcertTrace_StartSyncTrace_Response` | 同步追踪启动响应（含错误码） |
| `FConcertTrace_StopSyncTrace` | 同步追踪停止消息 |

> **注意**：这些结构体通常在内部网络通信中使用，不建议直接在蓝图中操作。如需在蓝图中控制追踪，应使用 ConcertInsightsClient 插件提供的状态栏 UI。

## C++ 用法

### 头文件引入

```cpp
#include "TraceControls.h"
#include "TraceMessages.h"
```

### 基本用法

以下示例展示了如何子类化 `FTraceControls` 来实现自定义追踪控制器：

```cpp
// 来源: Source/ConcertInsightsCore/Public/TraceControls.h
#include "TraceControls.h"

namespace MyTool
{
    class FMyTraceControls : public UE::ConcertInsightsCore::FTraceControls
    {
    public:
        FMyTraceControls() = default;
        
    protected:
        // 必须实现：提供初始化事件参数
        virtual UE::ConcertInsightsCore::FInitArgs GetInitEventArgs() const override
        {
            return UE::ConcertInsightsCore::FInitArgs{
                .EndpointId = TOptional<FGuid>{},
                .DisplayString = TEXT("MyCustomTool"),
                .bIsServer = false
            };
        }
        
        // 可选：决定是否向某个端点发送追踪请求
        virtual bool CanSendRequestsToEndpoint(const FGuid& EndpointId, const IConcertSession& Session) const override
        {
            // 例如：只向服务器发送请求
            return EndpointId == Session.GetServerEndpointId();
        }
        
        // 可选：当远程同步追踪请求被接受时的回调
        virtual void OnSynchronizedTraceAccepted(
            const FConcertSessionContext& Context,
            const FConcertTrace_StartSyncTrace_Request& Request,
            const TSharedRef<IConcertSession>& Session) override
        {
            UE_LOG(LogTemp, Log, TEXT("Synchronized trace accepted from endpoint %s"), *Context.SenderEndpointId.ToString());
        }
    };
}
```

### 进阶用法

在 Concert 会话中使用追踪控制的完整流程：

```cpp
// 来源: Source/ConcertInsightsCore/Public/TraceControls.h
#include "TraceControls.h"
#include "IConcertSession.h"

void AMyActor::InitTraceControls(TSharedRef<IConcertSession> Session)
{
    // 使用工厂方法创建（确保发送 Init 事件）
    TraceControls = UE::ConcertInsightsCore::FTraceControls::Make<FMyTraceControls>();
    
    // 注册会话以监听远程追踪请求
    TraceControls->RegisterTraceRequestsHandler(Session);
    
    // 监听同步追踪开始/停止事件
    TraceControls->OnSynchronizedTraceStarted().AddLambda([this]()
    {
        UE_LOG(LogTemp, Log, TEXT("Synchronized trace started"));
    });
    
    TraceControls->OnSynchronizedTraceStopped().AddLambda([this]()
    {
        UE_LOG(LogTemp, Log, TEXT("Synchronized trace stopped"));
    });
    
    // 启动同步追踪（带自定义参数）
    FText FailReason;
    UE::ConcertInsightsCore::FStartTraceArgs Args;
    Args.ConnectionType = EConcertTraceTargetType::File;
    Args.Target = TEXT("MyTrace");
    Args.Channels = TEXT("default,Concert");
    
    bool bSuccess = TraceControls->StartSynchronizedTrace(Session, Args, &FailReason);
    if (!bSuccess)
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to start sync trace: %s"), *FailReason.ToString());
    }
    
    // 或者使用默认参数启动
    // TraceControls->StartSynchronizedTrace(Session);
    
    // 停止追踪
    // TraceControls->StopSynchronizedTrace();
}
```

### 关键接口一览

| 类/方法 | 说明 |
|---|---|
| `FTraceControls::Make<T>()` | 静态工厂方法，创建子类实例并确保 Init 事件发送 |
| `RegisterTraceRequestsHandler()` | 注册会话，开始监听远程追踪请求 |
| `StartSynchronizedTrace()` | 向所有参与端点发送同步追踪启动请求 |
| `StopSynchronizedTrace()` | 停止同步追踪 |
| `IsTracing()` / `IsInSynchronizedTrace()` | 查询当前追踪状态 |
| `GetDefaultSynchronizedTraceArgs()` | 虚函数，子类可重写以自定义默认追踪参数 |
| `OnLeaveSession()` | 会话离开时调用的清理方法 |

## Demo 示例

以下是一个最小的自定义追踪控制模块实现：

```cpp
// MyTraceModule.h
#pragma once

#include "TraceControls.h"

class FMyTraceModule : public UE::ConcertInsightsCore::FTraceControls
{
public:
    FMyTraceModule();
    
    /** 在会话连接后调用 */
    void OnSessionReady(TSharedRef<IConcertSession> Session);

protected:
    virtual UE::ConcertInsightsCore::FInitArgs GetInitEventArgs() const override;
    virtual UE::ConcertInsightsCore::FStartTraceArgs GetDefaultSynchronizedTraceArgs() const override;

private:
    bool bIsServer = false;
};
```

```cpp
// MyTraceModule.cpp
#include "MyTraceModule.h"
#include "IConcertSession.h"

FMyTraceModule::FMyTraceModule()
{
}

void FMyTraceModule::OnSessionReady(TSharedRef<IConcertSession> Session)
{
    RegisterTraceRequestsHandler(Session);
    
    OnSynchronizedTraceStarted().AddLambda([]()
    {
        UE_LOG(LogTemp, Display, TEXT("Multi-machine tracing has begun!"));
    });
}

UE::ConcertInsightsCore::FInitArgs FMyTraceModule::GetInitEventArgs() const
{
    return UE::ConcertInsightsCore::FInitArgs{
        .EndpointId = TOptional<FGuid>{},
        .DisplayString = TEXT("MyTraceModule"),
        .bIsServer = bIsServer
    };
}

UE::ConcertInsightsCore::FStartTraceArgs FMyTraceModule::GetDefaultSynchronizedTraceArgs() const
{
    UE::ConcertInsightsCore::FStartTraceArgs Args;
    Args.ConnectionType = EConcertTraceTargetType::Network;
    Args.Target = TEXT("localhost");
    Args.Channels = TEXT("default,Concert");
    return Args;
}
```

## 模块依赖

基于源码中的 `#include` 和类型引用推断的依赖关系：

| 模块 | 用途 |
|---|---|
| `ConcertTransport` | Concert 网络传输层，提供 `FConcertTrace_*` 消息结构体和追踪宏 |
| `Concert` | Multi-User 会话管理，提供 `IConcertSession` 接口 |
| `TraceLog` | 追踪系统基础设施，提供 `FTraceAuxiliary` |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 将日志宏从 UE_LOG 迁移到新的 UE_LOGF 格式 |
| 2024-05-13 | `ee845008` | Fix duplicate loca keys | 修复本地化键重复问题 |
| 2024-05-06 | `ef1d668c` | Extend Unreal Insights to allow tracing protocols accross multiple machines participating in a Multi User session. | 首次提交，引入跨多用户会话的同步追踪协议框架 |

### 维护评价

- **创建时间**：约 1 年前（2024-05-06）
- **更新频率**：创建后仅进行过一次小修复和一次日志宏迁移，无功能性更新
- **实验性状态**：标记为 `IsExperimentalVersion=true`，`Hidden=true`，`EnabledByDefault=false`
- **定位**：作为 ConcertInsightsClient / ConcertInsightsServer 的底层共享库，本身不需要频繁更新
- **推荐程度**：⚠️ **谨慎使用**。这是一个实验性的底层框架模块，API 可能在未来版本发生变化。如果你需要在 Multi-User 会话中进行同步追踪，建议直接使用上层的 ConcertInsightsClient/ConcertInsightsServer 插件。仅在需要自定义追踪控制逻辑时才直接依赖此模块。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertInsights/ConcertInsightsCore)
- 官方文档：无（此插件无 DocsURL）
- [父级插件目录](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertInsights)（含 ConcertInsightsClient 和 ConcertInsightsServer）