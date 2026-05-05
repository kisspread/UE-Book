# Storm Sync

> Sync, Pull, Push, asset dependencies.
>
> This plugin is a recommended part of the Motion Design work flow.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（资产、配置等） |
| 模块 | `StormSyncCore` (Runtime), `StormSyncDrives` (Runtime), `StormSyncEditor` (Runtime), `StormSyncImport` (Runtime), `StormSyncTests` (Runtime), `StormSyncTransportClient` (Runtime), `StormSyncTransportCore` (Runtime), `StormSyncTransportServer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/StormSync) | |

## 用途

Storm Sync 是一个用于在多台机器（例如工作站和渲染农场节点）之间同步 Unreal Engine 资产及其依赖关系的插件。它解决了在分布式工作流（特别是 Motion Design 和虚拟制片）中，确保所有参与方的项目资产保持一致性的核心问题。该插件提供了资产依赖关系的分析、打包、传输（推送/拉取）以及同步状态管理的完整工具链，是 Epic Games 官方推荐的 Motion Design 工作流的一部分。

## 使用场景

-   **Motion Design 团队协作**：设计师在工作站上创建或修改资产后，可以通过 Storm Sync 将变更及其所有依赖项推送到共享存储或直接同步到渲染农场节点，确保渲染结果与设计意图一致。
-   **虚拟制片资产分发**：在虚拟制片现场，需要将最新的场景资产、材质或蓝图同步到 LED 墙渲染服务器或实时合成工作站，Storm Sync 可以自动化这个过程。
-   **版本控制与回滚**：通过记录资产依赖关系快照，可以方便地回滚到特定版本的资产集合状态。
-   **自动化构建管线集成**：在 CI/CD 流程中，可以使用 Storm Sync 的命令行或 API 来确保构建服务器拥有正确的资产版本。

## 蓝图用法

基于 `StormSyncTransportServer` 模块的接口，可以控制服务器的发现和监听状态。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Discovery Manager` | 启动发现管理器，使服务器能被客户端在网络中发现。 | `IStormSyncTransportServerModule` |
| `Start Server Endpoint` | 启动本地传输端点（TCP 服务器），开始监听客户端连接。会自动启动发现管理器。 | `IStormSyncTransportServerModule` |
| `Is Running` | 检查 Storm Sync 服务器端点是否正在运行。 | `IStormSyncTransportServerModule` |
| `Get Server Status` | 获取服务器运行状态及状态描述文本。 | `IStormSyncTransportServerModule` |
| `Get Server Endpoint Message Address Id` | 获取服务器端点的消息总线地址 ID（如果正在运行）。 | `IStormSyncTransportServerModule` |

### 使用示例（蓝图描述）

1.  **初始化服务器**：在游戏模式或某个管理器的 `BeginPlay` 事件中，调用 `IStormSyncTransportServerModule::Get()` 获取模块实例，然后调用 `Start Server Endpoint` 节点，并传入一个友好的端点名称（如 “MyRenderNode”）。
2.  **状态监控**：创建一个定时器，定期调用 `Is Running` 和 `Get Server Status` 节点，并将状态文本显示在 UI 上，用于监控服务器健康状况。
3.  **客户端发现**：在客户端蓝图中，使用 `IStormSyncTransportClientModule` 的相应节点来发现并连接到由上述服务器启动的端点。

## C++ 用法

### 头文件引入

```cpp
#include "IStormSyncTransportServerModule.h"
```

### 基本用法

以下代码展示了如何获取服务器模块实例并启动服务。
*（来源：基于 `IStormSyncTransportServerModule.h` 接口推断）*

```cpp
// 获取 Storm Sync 服务器模块
IStormSyncTransportServerModule& ServerModule = IStormSyncTransportServerModule::Get();

// 检查模块是否可用
if (IStormSyncTransportServerModule::IsAvailable())
{
    // 启动服务器端点，使用项目设置中配置的端口
    ServerModule.StartServerEndpoint(TEXT("MyProductionServer"));

    // 检查服务器是否成功启动
    if (ServerModule.IsRunning())
    {
        UE_LOG(LogTemp, Log, TEXT("Storm Sync Server is running."));
        FText StatusText;
        ServerModule.GetServerStatus(StatusText);
        UE_LOG(LogTemp, Log, TEXT("Status: %s"), *StatusText.ToString());
    }
}
```

### 进阶用法

可以创建自定义的本地端点实例用于测试，或获取心跳发射器进行高级监控。
*（来源：基于 `IStormSyncTransportServerModule.h` 和 `IStormSyncTransportServerLocalEndpoint.h` 接口推断）*

```cpp
// 仅用于测试：创建独立的服务器端点实例
TSharedPtr<IStormSyncTransportServerLocalEndpoint> TestEndpoint = ServerModule.CreateServerLocalEndpoint(TEXT("TestEndpoint"));
if (TestEndpoint.IsValid())
{
    // 手动指定一个端口启动监听
    FIPv4Endpoint Endpoint(FIPv4Address::InternalLoopback, 19876);
    TestEndpoint->StartTcpListener(Endpoint);

    // 检查 TCP 服务器状态
    if (TestEndpoint->IsTcpServerActive())
    {
        FString Address = TestEndpoint->GetTcpServerEndpointAddress();
        UE_LOG(LogTemp, Log, TEXT("Test TCP Server listening on: %s"), *Address);
    }
}

// 获取心跳发射器引用（用于监控服务器活性）
FStormSyncHeartbeatEmitter& HeartbeatEmitter = ServerModule.GetHeartbeatEmitter();
// ... 可以进一步使用 HeartbeatEmitter 进行自定义监控逻辑
```

## Demo 示例

一个最小化的服务器启动示例。

**StormSyncServerActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "StormSyncServerActor.generated.h"

UCLASS()
class AStormSyncServerActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    void StartSyncServer();
    void StopSyncServer();
};
```

**StormSyncServerActor.cpp**
```cpp
#include "StormSyncServerActor.h"
#include "IStormSyncTransportServerModule.h"

void AStormSyncServerActor::BeginPlay()
{
    Super::BeginPlay();
    StartSyncServer();
}

void AStormSyncServerActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    StopSyncServer();
    Super::EndPlay(EndPlayReason);
}

void AStormSyncServerActor::StartSyncServer()
{
    if (IStormSyncTransportServerModule::IsAvailable())
    {
        IStormSyncTransportServerModule& ServerModule = IStormSyncTransportServerModule::Get();
        ServerModule.StartServerEndpoint(GetName());
        UE_LOG(LogTemp, Log, TEXT("Storm Sync Server started for actor: %s"), *GetName());
    }
}

void AStormSyncServerActor::StopSyncServer()
{
    // 服务器模块的生命周期通常由插件管理，此处仅作日志记录
    UE_LOG(LogTemp, Log, TEXT("Storm Sync Server actor shutting down."));
}
```

## 模块依赖

`StormSyncTransportServer` 模块依赖于以下核心模块：

| 模块 | 用途 |
|---|---|
| `StormSyncTransportCore` | 提供传输层的核心接口和类型定义，如 `IStormSyncTransportLocalEndpoint`。 |
| `Networking` | 提供底层的网络功能，如 TCP 监听器 (`FTcpListener`)。 |
| `Sockets` | 提供套接字抽象层。 |

*注：其他依赖（如 `Core`, `CoreUObject`, `Engine`）为标准依赖，已省略。*

## 维护状态

### 近期更新

-   `5e98ccb853ee` Motion Design: moved the following plugins from /Plugins/Experimental to /Plugins/VirtualProduction: ActorModifier, ActorModifierCore, Motion Design, ClonerEffector, CustomDetailsView, Material Designer, GeometryMask, OperatorStack, PropertyAnimator, PropertyAnimatorCore, StormSync, StormSync Motion Design Bridge
    *（解读：这是一次重要的结构性迁移，将 StormSync 从实验性插件提升为 Virtual Production 分类下的正式插件，表明其已达到一定的稳定性和成熟度。）*

### 维护评价

-   **创建时间**：2024年1月，是一个相对较新的插件。
-   **最近更新**：最近一次提交是将其从 `Experimental` 目录迁移到 `VirtualProduction` 目录，这是一个积极的信号，表明 Epic Games 认为其已准备好用于生产环境。
-   **活跃度**：作为 Motion Design 工作流的官方推荐部分，预计会持续维护和更新。
-   **已知限制**：作为网络同步插件，其性能和可靠性高度依赖于网络环境和资产依赖关系的复杂性。
-   **推荐使用**：**推荐**。对于需要在多台机器间同步资产的虚拟制片和 Motion Design 项目，这是一个官方支持的、设计良好的解决方案。建议关注其后续版本的功能增强和性能优化。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/StormSync)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/StormSync/Source/StormSyncTests)