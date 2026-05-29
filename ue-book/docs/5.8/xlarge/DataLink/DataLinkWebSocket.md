# Motion Design Data Link

> （无描述信息）

| 属性 | 值 |
|---|---|
| 中文名 | 数据链路 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DataLink` (Runtime), `DataLinkDataTable` (Runtime), `DataLinkEdGraph` (Runtime), `DataLinkEditor` (Runtime), `DataLinkHttp` (Runtime), `DataLinkJson` (Runtime), `DataLinkJsonEditor` (Runtime), `DataLinkWebSocket` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DataLink) | |

## 用途

DataLink 是一个用于 Unreal Engine 虚拟制片（Motion Design）的数据连接框架。它提供了一套基于节点（Node）的系统，用于在引擎内部或与外部服务之间进行数据交互、查询和转换。其核心目标是简化复杂的数据集成流程，特别是在需要连接实时数据源（如WebSocket服务器、HTTP API）或处理特定格式数据（如JSON、DataTable）的场景。

`DataLinkWebSocket` 模块是该框架的一个具体实现，专注于提供WebSocket协议的连接能力。它允许在Motion Design图表中创建一个WebSocket节点，连接到指定的服务器地址，发送预设或动态的消息，并接收服务器返回的数据。

## 使用场景

- 你在虚拟制片项目中需要实时接收来自外部控制台、设备或软件（如TouchDesigner）的参数或指令。
- 你需要通过WebSocket协议与自定义后端服务进行双向通信，以更新场景中的资产属性或触发事件。
- 你正在构建一个需要低延迟数据流的应用，例如实时捕捉数据、交互式灯光或实时合成。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Web Socket` | 在Motion Design图表中添加一个WebSocket数据源节点。 | `UDataLinkWebSocket` |

### 使用示例（蓝图描述）

1. 在 Motion Design 编辑器中，从节点列表拖入 **`Web Socket`** 节点。
2. 在节点的 **Details** 面板中，配置 **`WebSocketSettings`**：
   - **`URL`**: 填入目标WebSocket服务器的地址，例如 `ws://localhost:8080`。
   - **`Protocols`**: （可选）添加子协议。
   - **`UpgradeHeaders`**: （可选）添加自定义请求头。
3. 在节点的 **`ConnectMessages`** 数组中，添加希望在连接成功后立即发送给服务器的消息字符串。
4. 将 **`Web Socket`** 节点的输出引脚（通常包含连接状态和收到的消息）连接到图表中其他需要接收数据的节点。
5. 该节点将自动在图表执行时尝试连接、发送消息，并将接收到的数据传递给下游。

## C++ 用法

### 头文件引入

```cpp
#include "DataLinkWebSocketSubsystem.h"
#include "DataLinkWebSocket.h"
#include "DataLinkWebSocketSettings.h"
```

### 基本用法

（以下代码为基于源码结构的逻辑示例，展示API用法）

```cpp
// 假设在一个上下文环境中（如某个Actor或Subsystem）
void SetupWebSocketConnection()
{
    // 1. 获取 WebSocket 子系统
    UDataLinkWebSocketSubsystem* WebSocketSubsystem = UDataLinkWebSocketSubsystem::TryGet();
    if (!WebSocketSubsystem)
    {
        UE_LOG(LogTemp, Error, TEXT("无法获取 DataLinkWebSocketSubsystem"));
        return;
    }

    // 2. 配置连接参数
    FDataLinkWebSocketSettings Settings;
    Settings.URL = TEXT("ws://echo.websocket.events"); // 示例回显服务器

    // 3. 创建 WebSocket 连接
    UDataLinkWebSocketSubsystem::FCreateWebSocketResult CreateResult;
    bool bSuccess = WebSocketSubsystem->CreateWebSocket(Settings, CreateResult);
    if (bSuccess && CreateResult.WebSocket.IsValid())
    {
        TSharedPtr<IWebSocket>& WebSocket = CreateResult.WebSocket;

        // 4. 绑定回调函数
        WebSocket->OnConnected().AddLambda([]()
        {
            UE_LOG(LogTemp, Log, TEXT("WebSocket 已连接"));
        });

        WebSocket->OnMessage().AddLambda([](const FString& InMessage)
        {
            UE_LOG(LogTemp, Log, TEXT("收到消息: %s"), *InMessage);
        });

        WebSocket->OnConnectionError().AddLambda([](const FString& InError)
        {
            UE_LOG(LogTemp, Error, TEXT("连接错误: %s"), *InError);
        });

        WebSocket->OnClosed().AddLambda([](int32 InStatusCode, const FString& InReason, bool bInWasClean)
        {
            UE_LOG(LogTemp, Log, TEXT("连接已关闭: %d - %s"), InStatusCode, *InReason);
        });

        // 5. 发送初始消息
        WebSocket->Send(TEXT("Hello from Unreal Engine!"));

        // 6. 可以保存 Handle 以便后续管理
        UE::DataLink::FWebSocketHandle Handle = CreateResult.Handle;
        // ... 后续可使用 WebSocketSubsystem->CloseWebSocket(Handle) 关闭连接
    }
}
```

### 进阶用法

结合 `FDataLinkExecutor` 和 `UDataLinkNode` 的使用模式，通常在 `UDataLinkWebSocket::OnExecute` 内部处理连接的生命周期和消息路由。对于使用者来说，主要交互点在于正确配置 `FDataLinkWebSocketSettings` 并处理来自节点输出引脚的数据。

## Demo 示例

（此处展示一个继承自 `UDataLinkWebSocket` 的最小自定义节点示例）

```cpp
// MyCustomWebSocketNode.h
#pragma once
#include "DataLinkWebSocket.h"
#include "MyCustomWebSocketNode.generated.h"

UCLASS(DisplayName="Custom WebSocket Node", Category="My Nodes")
class UMyCustomWebSocketNode : public UDataLinkWebSocket
{
    GENERATED_BODY()

protected:
    // 重写构建引脚，可以添加或修改默认输入输出
    virtual void OnBuildPins(FDataLinkPinBuilder& Inputs, FDataLinkPinBuilder& Outputs) const override
    {
        Super::OnBuildPins(Inputs, Outputs);
        // 可在此添加额外的输入引脚，例如动态消息
        Inputs.Add(TEXT("DynamicMessage"), FDataLinkPinProperties::MakeString());
    }

    // 重写执行逻辑，可以修改消息处理方式
    virtual EDataLinkExecutionReply OnExecute(FDataLinkExecutor& InExecutor) const override
    {
        // 在此处可以获取 DynamicMessage 引脚的值，并将其添加到发送队列等
        // 然后调用 Super::OnExecute 或实现完全自定义的逻辑
        return Super::OnExecute(InExecutor);
    }
};
```

```cpp
// MyCustomWebSocketNode.cpp
#include "MyCustomWebSocketNode.h"
// 构造函数等实现文件
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DataLink` | 核心的数据链路节点执行和图框架。 |
| `WebSockets` | 提供底层的 WebSocket 客户端实现。 |
| `Json` | 用于解析和处理JSON格式的消息数据（如果涉及）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构JSON对象以同时支持两种字符串类型，优化内存。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到 UE_LOGF 格式。 |
| 2026-03-02 | `e97b93d4` | Fixes for CL 51336460 - Remove string duplication in FJsonObject to free memory | 修复JSON对象中的字符串重复问题以释放内存。 |
| 2026-02-25 | `ec13ba36` | [Backout] - CL51209244 | 回退了之前的某次提交。 |

### 维护评价

该插件创建于 2025 年 8 月，目前处于 **实验性（Beta）** 状态且未默认启用。从 Git 历史看，近期（2026年4月）仍有针对其依赖模块（如JSON处理）的优化和维护活动，表明该项目仍在活跃开发中，主要焦点在于内部优化和与Motion Design主插件的集成。

由于其为较新的实验性功能，API和节点接口可能在未来版本中发生变化。推荐在虚拟制片项目中试用，但需注意在生产环境中可能需要应对版本升级带来的适配工作。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DataLink)
- （暂无官方文档链接）