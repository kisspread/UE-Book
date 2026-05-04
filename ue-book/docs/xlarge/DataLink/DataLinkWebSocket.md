# Motion Design Data Link

> （Description 字段为空）

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DataLink` (Runtime), `DataLinkDataTable` (Runtime), `DataLinkEdGraph` (Runtime), `DataLinkEditor` (Runtime), `DataLinkHttp` (Runtime), `DataLinkJson` (Runtime), `DataLinkJsonEditor` (Runtime), `DataLinkWebSocket` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DataLink) | |

## 用途

DataLink 是一个面向虚拟制作（Motion Design）的数据连接框架，用于将外部数据源（HTTP API、WebSocket 服务器、JSON 文件等）实时接入 Unreal Engine 的蓝图和材质系统。

该插件解决的核心问题是：**在虚拟制作场景中，需要从多种外部数据源获取实时数据并驱动场景元素**。例如：
- 从 WebSocket 服务器接收实时传感器数据
- 通过 HTTP API 获取远程配置或状态
- 解析 JSON 数据并映射到蓝图变量

插件采用**节点图（Node Graph）**架构，每个数据源是一个 `UDataLinkNode`，通过引脚（Pin）系统连接输入输出，支持数据流的可视化编排。

## 模块架构

| 模块 | 类型 | 用途 |
|---|---|---|
| `DataLink` | Runtime | 核心框架：节点基类、执行器、引脚系统 |
| `DataLinkDataTable` | Runtime | DataTable 数据源节点 |
| `DataLinkEdGraph` | Runtime | 节点图的编辑器图形表示 |
| `DataLinkEditor` | Runtime | 编辑器 UI 和工具 |
| `DataLinkHttp` | Runtime | HTTP 请求数据源节点 |
| `DataLinkJson` | Runtime | JSON 解析数据源节点 |
| `DataLinkJsonEditor` | Runtime | JSON 节点的编辑器支持 |
| `DataLinkWebSocket` | Runtime | WebSocket 连接数据源节点 |

## 使用场景

- 你在做虚拟制作/广播图形 → 用 DataLink 从外部系统获取实时数据驱动场景
- 你需要从 WebSocket 服务器接收实时消息 → 用 DataLinkWebSocket 节点
- 你需要调用 REST API 获取数据 → 用 DataLinkHttp 节点
- 你需要解析 JSON 文件或字符串 → 用 DataLinkJson 节点

---

# DataLinkWebSocket 模块

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Web Socket` | WebSocket 连接节点，连接到指定 URL 的 WebSocket 服务器并收发消息 | `UDataLinkWebSocket` |

### 输入引脚

| 引脚名 | 类型 | 说明 |
|---|---|---|
| `InputWebSocketSettings` | `FDataLinkWebSocketSettings` | WebSocket 连接设置（URL、协议、升级头） |
| `InputWebSocketMessages` | `FDataLinkWebSocketMessages` | 连接成功后要发送的消息列表 |

### 输出引脚

输出引脚通过 `OnBuildPins` 动态构建，通常包含接收到的 WebSocket 消息。

### 使用示例（蓝图描述）

1. 在 DataLink 节点图中添加一个 **Web Socket** 节点
2. 创建一个 `FDataLinkWebSocketSettings` 结构体，设置：
   - **URL**: WebSocket 服务器地址，如 `ws://localhost:8080`
   - **Protocols**: 协议列表（可选）
   - **UpgradeHeaders**: 升级请求头（可选）
3. 创建一个 `FDataLinkWebSocketMessages` 结构体，添加连接后要发送的消息
4. 将设置和消息连接到 Web Socket 节点的输入引脚
5. 连接输出引脚到下游节点处理接收到的数据

## C++ 用法

### 头文件引入

```cpp
#include "DataLinkWebSocket.h"
#include "DataLinkWebSocketSettings.h"
```

### 基本用法

WebSocket 设置结构体的使用：

```cpp
// 来源: DataLinkWebSocketSettings.h
FDataLinkWebSocketSettings Settings;
Settings.URL = TEXT("ws://localhost:8080");
Settings.Protocols.Add(TEXT("my-protocol"));
Settings.UpgradeHeaders.Add(TEXT("Authorization"), TEXT("Bearer token123"));

// 检查两个设置是否相同
FDataLinkWebSocketSettings OtherSettings;
bool bSame = Settings.Equals(OtherSettings);

// 重置设置
Settings.Reset();
```

### 消息结构体

```cpp
// 来源: DataLinkWebSocket.h
FDataLinkWebSocketMessages Messages;
Messages.ConnectMessages.Add(TEXT("Hello Server"));
Messages.ConnectMessages.Add(TEXT("Subscribe: channel1"));
```

### WebSocket 句柄

```cpp
// 来源: DataLinkWebSocketHandle.h
UE::DataLink::FWebSocketHandle Handle = UE::DataLink::FWebSocketHandle::GenerateNewHandle();
if (Handle.IsValid())
{
    // 使用句柄...
}
Handle.Reset();
```

## Demo 示例

### 自定义 DataLink 节点（继承 UDataLinkNode）

```cpp
// MyDataLinkNode.h
#pragma once

#include "DataLinkNode.h"
#include "MyDataLinkNode.generated.h"

UCLASS(DisplayName="My Custom Node", Category="Custom")
class UMyDataLinkNode : public UDataLinkNode
{
    GENERATED_BODY()

protected:
    virtual void OnBuildPins(FDataLinkPinBuilder& Inputs, FDataLinkPinBuilder& Outputs) const override;
    virtual EDataLinkExecutionReply OnExecute(FDataLinkExecutor& InExecutor) const override;
    virtual void OnStop(const FDataLinkExecutor& InExecutor) const override;
};
```

```cpp
// MyDataLinkNode.cpp
#include "MyDataLinkNode.h"

void UMyDataLinkNode::OnBuildPins(FDataLinkPinBuilder& Inputs, FDataLinkPinBuilder& Outputs) const
{
    // 定义输入引脚
    Inputs.Add(TEXT("InputData"));
    
    // 定义输出引脚
    Outputs.Add(TEXT("OutputData"));
}

EDataLinkExecutionReply UMyDataLinkNode::OnExecute(FDataLinkExecutor& InExecutor) const
{
    // 获取输入数据
    // 处理逻辑
    // 设置输出数据
    // InExecutor.SetOutputData(...);
    
    return EDataLinkExecutionReply::Completed;
}

void UMyDataLinkNode::OnStop(const FDataLinkExecutor& InExecutor) const
{
    // 清理资源
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `WebSockets` | WebSocket 客户端实现 |
| `DataLink` | 核心框架（UDataLinkNode 基类、FDataLinkExecutor 等） |

## 维护状态

### 近期更新

```
- ce6ff392ddca Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue for FTSTicker::RemoveTicker usage.
- 94f961385e8e Motion Design: Moved scene state and data link plugins out of experimental into virtualproduction
```

- `ce6ff392ddca` 修复编译警告，处理 `FTSTicker::RemoveTicker` 的 nodiscard 属性
- `94f961385e8e` 将插件从 Experimental 目录迁移到 VirtualProduction 目录

### 维护评价

- **状态**: 🆕 新插件，刚从实验性迁移到正式目录
- **风险**: `IsBetaVersion=true`，API 可能发生变化
- **活跃度**: 刚创建不久（2025-04-22），处于早期开发阶段
- **建议**: 可以尝试使用，但注意 API 可能不稳定，不建议用于生产环境的关键路径

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DataLink)
- [DataLinkWebSocket 源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DataLink/Source/DataLinkWebSocket)