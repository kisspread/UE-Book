# ConcertInsightsServer

> Listens for requests of clients to start synchronized tracing, which is initiated in the ConcertInsightsClient plugin.

| 属性 | 值 |
|---|---|
| 分类 | Networking |
| 默认启用 | 否（Hidden，仅限特定程序） |
| 包含内容 | 是 |
| 模块 | ConcertInsightsServer (Program) |
| 创建时间 | 2024-05-06 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertInsights/ConcertInsightsServer) | |

## 用途

ConcertInsightsServer 是 UE5 Multi-User Editing（Concert）体系中 Unreal Insights 追踪功能的服务端组件。它运行在 `UnrealMultiUserServer` / `UnrealMultiUserSlateServer` 程序中，负责监听客户端发来的同步追踪（Synchronized Trace）请求。

具体来说，当 ConcertInsightsClient（编辑器端）发起一次"同步追踪"请求时，本插件在 MU Server 上接收该请求，启动服务器端的 Unreal Insights 追踪，并管理追踪的生命周期——包括在发起追踪的客户端断开连接时自动通知所有参与者停止追踪。

本插件是 [ConcertInsights](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertInsights) 三件套之一：

- **ConcertInsightsCore** — 共享核心逻辑（追踪控制基类、网络消息定义）
- **ConcertInsightsClient**（编辑器端）— 编辑器中的客户端，提供状态栏 UI 发起追踪
- **ConcertInsightsServer**（本插件，MU Server 端）— 服务器端追踪控制
- **ConcertInsightsVisualizer** — Unreal Insights 中的可视化扩展，聚合多台机器的 .utrace 文件

## 使用场景

- 你在使用 Multi-User Editing 协作开发，需要同时在多台机器上收集 Unreal Insights 追踪数据，用于分析网络同步延迟、对象复制性能等
- 你在调试 VCam 等需要跨机器复制 Actor 的功能，需要关联分析多台机器的执行时序
- 你需要在 MU Server 上自动参与同步追踪，而不需要在服务器上手动操作

**注意**：本插件是高度实验性的（`IsExperimentalVersion: true`）。已知问题包括跨机器时间同步精度约 400ms（依赖 `FDateTime::UtcNow`，建议使用 PTP 等时间同步协议改进）。

## 蓝图用法

本插件没有暴露任何 BlueprintCallable 函数或 BlueprintReadWrite 属性。它是一个纯 C++ 后台模块，仅在 MU Server 程序中运行，通过内部委托机制与 Concert 网络层交互。

## C++ 用法

本插件的 API 主要通过 `IConcertInsightsServerModule` 接口访问模块实例，以及通过 `FServerTraceControls` 控制服务器端的同步追踪状态。

### 头文件引入

```cpp
#include "IConcertInsightsServerModule.h"    // 模块接口
// 注意：ServerTraceControls.h 是 Private 头文件，外部不应直接引用
```

### 基本用法：获取模块实例

```cpp
// 检查模块是否可用
if (UE::ConcertInsightsServer::IConcertInsightsServerModule::IsAvailable())
{
    // 获取模块引用（会按需加载）
    UE::ConcertInsightsServer::IConcertInsightsServerModule& Module =
        UE::ConcertInsightsServer::IConcertInsightsServerModule::Get();
}
```

（来源：`Source/ConcertInsightsServer/Public/IConcertInsightsServerModule.h`）

### 注意事项

⚠️ **已知 Bug**：`IConcertInsightsServerModule::IsAvailable()` 方法内部检查的模块名是 `"ConcertInsightsEditor"` 而非 `"ConcertInsightsServer"`（疑似从 Client 模块复制粘贴时遗留的错误）。在 MU Server 环境中直接使用 `Get()` 即可，`IsAvailable()` 返回值不可靠。

### 内部架构：FServerTraceControls

`FServerTraceControls` 继承自 `ConcertInsightsCore::FTraceControls`，是服务器端的追踪控制器。它的核心职责：

1. **监听服务器创建** — 构造时注册 `IConcertSyncServerModule::OnServerCreated()` 回调
2. **注册会话处理器** — 每当 Concert Server 创建新会话时，自动注册追踪请求处理器
3. **处理同步追踪请求** — 当客户端发送 `FConcertTrace_StartSyncTrace_Request` 时，服务器开始追踪
4. **管理追踪生命周期** — 追踪发起者断开时自动停止所有端点的追踪

关键逻辑（来源：`Source/ConcertInsightsServer/Private/ServerTraceControls.cpp`）：

```cpp
// 服务器过滤逻辑：不向服务器自身端点发送请求
bool FServerTraceControls::CanSendRequestsToEndpoint(const FGuid& EndpointId,
    const IConcertSession& Session) const
{
    return Session.GetSessionInfo().ServerEndpointId != EndpointId;
}

// 初始化参数：标识为 "Server"
ConcertInsightsCore::FInitArgs FServerTraceControls::GetInitEventArgs() const
{
    return { {}, TEXT("Server"), true };
}

// 追踪发起者断开时自动停止
void FServerTraceControls::OnSynchronizedTraceClientChanged(
    IConcertServerSession& Session,
    EConcertClientStatus Status,
    const FConcertSessionClientInfo& ClientInfo)
{
    if (Status == EConcertClientStatus::Disconnected
        && InProgressSynchronizedServerTrace->SynchronizedTraceInstigator
           == ClientInfo.ClientEndpointId)
    {
        StopSynchronizedTrace();
        CleanUpClientsChangedDelegate();
    }
}
```

### 进阶用法：理解同步追踪流程

完整的同步追踪流程涉及 ConcertInsights 三件套协作：

1. **用户操作**：在编辑器底部状态栏点击 "Multi User > Start synchronized trace"
2. **客户端发送请求**：ConcertInsightsClient 通过 Concert 会话向所有端点发送 `FConcertTrace_StartSyncTrace_Request`
3. **服务器接收**：ConcertInsightsServer 的 `FServerTraceControls::HandleTraceStartRequest()` 处理请求
4. **本地启动追踪**：调用 `FTraceAuxiliary::Start()` 启动 Unreal Insights 追踪，自动启用 `Concert` 频道
5. **发送初始化事件**：每个端点在追踪数据中写入 `CONCERT_TRACE_INIT` 事件（包含端点 ID、角色标识等）
6. **生成 .utrace 文件**：每台机器生成独立的 .utrace 文件
7. **停止追踪**：用户停止时或发起者断开时，所有端点停止追踪
8. **可视化分析**：使用 ConcertInsightsVisualizer 在 Unreal Insights 中打开任意一个 .utrace 文件，聚合查看所有机器的追踪数据

## Demo 示例

### 启用插件

本插件默认不启用，且仅在 `UnrealMultiUserServer` / `UnrealMultiUserSlateServer` 程序中加载。

在 MU Server 的配置文件（如 `Engine/Programs/UnrealMultiUserSlateServerConfig/DefaultEngine.ini`）中添加：

```ini
[/Script/EngineSettings.GameMapsSettings]
+ProgramEnabledPlugins=ConcertInsightsServer
```

### 完整设置示例（配合 ConcertInsights 全套）

在你的 `.uproject` 文件中启用客户端插件：

```json
{
    "Plugins": [
        {
            "Name": "MultiUserClient",
            "Enabled": true
        },
        {
            "Name": "ConcertInsightsClient",
            "Enabled": true
        },
        {
            "Name": "ConcertInsightsVisualizer",
            "Enabled": true
        }
    ]
}
```

MU Server 配置（`DefaultEngine.ini`）：

```ini
+ProgramEnabledPlugins=ConcertInsightsServer
```

Unreal Insights 配置（`Engine/Programs/UnrealInsights/DefaultEngine.ini`）：

```ini
+ProgramEnabledPlugins=ConcertInsightsVisualizer
```

启动 Insights 时使用控制台变量：
```
Insights.Concert.EnableGameThreadAggregation = true
```

## 模块依赖

从 `Build.cs` 的 `PublicDependencyModuleNames` 和 `PrivateDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心模块 |
| `ConcertInsightsCore` | 同步追踪共享逻辑（基类 FTraceControls、消息定义） |
| `ConcertSyncServer` | Concert 服务端框架（IConcertSyncServer、IConcertServerSession） |
| `CoreUObject` | UObject 系统支持 |
| `Slate` | UI 框架（用于内部扩展点） |
| `SlateCore` | Slate 核心 |
| `ToolMenus` | 工具菜单系统 |

## 维护状态

### 近期更新

```
ef1d668 | 2024-05-06 | Extend Unreal Insights to allow tracing protocols across multiple machines participating in a Multi User session.
```

该插件仅有一次提交记录（2024-05-06），是整个 ConcertInsights 工具链的初始提交，包含 Core、Client、Server、Visualizer 四个插件。

### 维护评价

- **创建时间**：2024-05-06（约 2 年前）
- **更新频率**：仅有初始提交一次，此后无更新
- **维护状态**：⚠️ 不活跃 — 自创建以来无任何后续更新
- **实验性标记**：`IsExperimentalVersion: true`，明确标记为实验性
- **已知问题**：README.txt 记录了跨机器时间同步精度约 400ms 的问题，尚未修复
- **推荐程度**：仅推荐用于实验和探索性用途。作为实验性功能，API 和行为可能在后续版本中发生重大变更或被移除。生产环境不建议依赖此插件。

**⚠️ 警告：该插件超过 2 年没有实质性更新，且官方 README 明确标注为 "highly experimental"。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertInsights/ConcertInsightsServer)
- [ConcertInsights 整体目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertInsights)
- [ConcertInsightsCore](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertInsights/ConcertInsightsCore)
- [ConcertInsightsClient](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertInsights/ConcertInsightsClient)
- [ConcertInsightsVisualizer](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertInsights/ConcertInsightsVisualizer)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- 测试用例：无（插件目录内无测试文件）
