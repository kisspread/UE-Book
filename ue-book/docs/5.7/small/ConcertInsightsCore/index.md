# ConcertInsightsCore

> Shared logic for starting synchronized tracing

| 属性 | 值 |
|---|---|
| 分类 | Networking |
| 默认启用 | 否（Hidden=true） |
| 包含内容 | 否 |
| 模块 | ConcertInsightsCore (EditorAndProgram) |
| 创建时间 | 2024-05-06 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertInsights/ConcertInsightsCore) | |

## 用途

ConcertInsightsCore 是 UE5 Multi-User Editing（Concert）系统中 **同步 tracing** 的底层基础设施模块。它解决的核心问题是：在多机参与的 Multi-User Session 中，如何让所有参与者的 Unreal Insights trace 同时开始、同时停止，并在事后由 Unreal Insights 将分散在各机器上的 `.utrace` 文件自动聚合在一起进行分析。

该模块本身不包含 UI 或编辑器逻辑，而是提供 `FTraceControls` 基类和网络消息定义（`TraceMessages.h`），供上层模块 ConcertInsightsClient（编辑器端）和 ConcertInsightsServer（服务器端）继承使用。

**注意**：该插件标记为 `IsExperimentalVersion=true`，且 `Hidden=true`，不会出现在插件浏览器中。它是 ConcertInsights 插件族的内部依赖，不建议单独使用。

## 使用场景

- 你在开发 Multi-User Editing 工具链，需要在所有参与者之间同步启动 Unreal Insights 性能分析
- 你在构建自定义的 Concert 会话管理器，希望集成同步 trace 能力
- 你需要在 `.utrace` 文件中写入 Concert 协议级别的 trace 事件（`CONCERT_TRACE_INIT`），以便 Unreal Insights 能跨机器关联 trace 数据

## 蓝图用法

该插件没有暴露任何 `BlueprintCallable` 或 `BlueprintReadWrite` 接口。所有 API 都是 C++ 层面的。

## C++ 用法

### 头文件引入

```cpp
#include "TraceControls.h"
#include "TraceMessages.h"
#include "IConcertInsightsSyncTraceModule.h"
```

### 核心类：FTraceControls

`FTraceControls` 是同步 trace 的核心管理类，设计为被子类化。它监听来自其他 Concert 端点的远程 trace 请求，并在本地启动/停止 Unreal Insights tracing。

#### 子类化 FTraceControls

`FTraceControls` 有一个纯虚函数 `GetInitEventArgs()` 必须被实现：

```cpp
// 来源: TraceControls.h
class FMyTraceControls : public UE::ConcertInsightsCore::FTraceControls
{
protected:
    // 必须实现：提供 trace 初始化事件的参数
    virtual UE::ConcertInsightsCore::FInitArgs GetInitEventArgs() const override
    {
        return FInitArgs{
            .EndpointId = GetMyEndpointId(),
            .DisplayString = TEXT("MyEditor"),
            .bIsServer = false
        };
    }
    
    // 可选：控制是否向特定端点发送请求
    virtual bool CanSendRequestsToEndpoint(const FGuid& EndpointId, const IConcertSession& Session) const override
    {
        // 例如：跳过服务器端点
        return EndpointId != Session.GetSessionInfo().ServerEndpointId;
    }
};
```

#### 创建和注册

```cpp
// 使用工厂方法创建（会自动发送 init 事件如果 tracing 已在运行）
auto TraceControls = FTraceControls::Make<FMyTraceControls>();

// 注册到 Concert session 以接收远程请求
TraceControls->RegisterTraceRequestsHandler(MySession);
```

#### 启动同步 Trace

```cpp
// 来源: TraceControls.h / TraceControls.cpp
// 方式一：使用默认参数（Network 类型，localhost，default,Concert 通道）
TraceControls->StartSynchronizedTrace(MySession);

// 方式二：自定义参数
FStartTraceArgs Args;
Args.ConnectionType = EConcertTraceTargetType::Network;
Args.Target = TEXT("192.168.1.100");
Args.Channels = TEXT("default,Concert,Frame");
TraceControls->StartSynchronizedTrace(MySession, Args);

// 方式三：带失败原因反馈
FText FailReason;
if (!TraceControls->StartSynchronizedTrace(MySession, &FailReason))
{
    UE_LOG(LogTemp, Error, TEXT("Failed to start: %s"), *FailReason.ToString());
}
```

#### 停止同步 Trace

```cpp
TraceControls->StopSynchronizedTrace();
```

#### 监听事件

```cpp
// 来源: TraceControls.h
TraceControls->OnSynchronizedTraceStarted().AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("Synchronized trace started!"));
});

TraceControls->OnSynchronizedTraceStopped().AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("Synchronized trace stopped."));
});
```

### 网络消息（TraceMessages.h）

这些 USTRUCT 定义了 Concert 协议中用于同步 trace 的消息格式：

| 结构体 | 方向 | 说明 |
|---|---|---|
| `FConcertTrace_StartSyncTrace_Request` | 发起方 → 其他端点 | 请求所有端点开始 tracing |
| `FConcertTrace_StartSyncTrace_Response` | 其他端点 → 发起方 | 响应：Joined（已加入）/ Rejected（已拒绝）/ Timeout |
| `FConcertTrace_StopSyncTrace` | 发起方 → 其他端点 | 通知所有端点停止 tracing |
| `FConcertTrace_StartTraceArgs` | 嵌套 | 启动参数：连接类型、目标地址、通道列表 |

错误码枚举 `EConcertTraceErrorCode`：
- `Joined` — 端点接受了请求并开始 tracing
- `Rejected` — 端点已在 tracing，拒绝了请求
- `Timeout` — 端点未响应

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库（Public） |
| `Concert` | Multi-User Editing 的核心框架，提供 `IConcertSession` 等接口 |
| `ConcertTransport` | Concert 的网络传输层 |
| `CoreUObject` | UObject 系统（USTRUCT/UENUM 生成） |
| `Slate` / `SlateCore` | UI 框架（依赖可能因历史原因引入） |
| `TraceLog` | Unreal Insights 的 trace 基础设施 |

插件依赖：
- **ConcertMain** — Multi-User Editing 的主插件

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2024-05-13 | `ee84500` | Fix duplicate loca keys — 修复本地化键重复问题 |
| 2024-05-06 | `ef1d668` | 初始提交：Extend Unreal Insights to allow tracing protocols across multiple machines participating in a Multi User session |

### 维护评价

- **创建时间**：2024 年 5 月，约 2 年前
- **更新频率**：仅 2 次 commit，初始提交 + 一次小修复，此后无更新
- **状态**：实验性（`IsExperimentalVersion=true`），作为 ConcertInsights 插件族的内部模块，更新频率取决于上层模块的需求
- **推荐**：仅在开发 Multi-User Editing 相关工具时使用。该模块是底层基础设施，普通用户不应直接依赖

⚠️ 该模块自 2024 年 5 月后未有实质性更新，但作为稳定的基础层，低更新频率可能是正常现象。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertInsights/ConcertInsightsCore)
- [ConcertInsightsClient](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertInsights/ConcertInsightsClient) — 编辑器端实现
- [ConcertInsightsServer](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertInsights/ConcertInsightsServer) — 服务器端实现
- [ConcertInsightsVisualizer](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertInsights/ConcertInsightsVisualizer) — 可视化工具
- [ConcertMain](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertMain) — Multi-User Editing 主插件
