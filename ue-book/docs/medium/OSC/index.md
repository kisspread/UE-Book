# OSC (Open Sound Control)

> Implements the OSC 1.0 specification, allowing users to send and receive OSC messages and bundles between remote clients or applications.

| 属性 | 值 |
|---|---|
| 分类 | Input Devices |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OSC` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-05-31 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/OSC) | |

## 用途

OSC (Open Sound Control) 插件实现了 OSC 1.0 协议规范，让 UE5 项目能够通过 UDP 网络发送和接收 OSC 消息（Message）和数据包（Bundle）。

OSC 协议是一种在音频、多媒体和表演领域广泛使用的网络通信协议，常用于：
- 与数字音频工作站（DAW）如 Ableton Live、Max/MSP 通信
- 控制灯光设备（DMX over OSC）
- 虚拟制作中的设备联动
- 体感控制器、MIDI 设备的网络传输
- 多个应用/设备间的实时参数同步

插件提供 Client-Server 架构：**Client** 负责发送 OSC 消息，**Server** 负责监听并接收消息。两者通过 UDP Socket 通信，支持单播和组播（Multicast）。

> **注意**：该插件默认未启用，需要在 Edit → Plugins 中手动启用，或在 `.uproject` 的 Plugins 数组中添加 `{"Name": "OSC", "Enabled": true}`。

## 使用场景

- 你在做虚拟制作/LED 墙项目，需要用 OSC 控制媒体播放器 → 用 `UOSCClient` 发送播放/暂停命令
- 你需要从 TouchDesigner 或 Max/MSP 接收传感器数据 → 用 `UOSCServer` 监听消息并绑定回调
- 你需要与灯光控制台（如 ETC Eos）通信 → 用 OSC 地址模式匹配（Address Pattern Matching）路由消息
- 你需要将 UE5 中的 Actor 位置实时发送给外部应用 → 用 `UOSCClient` + `FOSCMessage` 打包数据
- 你在做互动装置，多个 UE5 实例需要同步状态 → 一个实例做 Client 发送，另一个做 Server 接收

## 蓝图用法

### 创建 Server 和 Client

通过 `UOSCManager` 静态函数创建 Server/Client 实例：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateOSCServer` | 创建 OSC 服务端，可配置 IP、端口、组播回环、是否立即监听 | `UOSCManager` |
| `CreateOSCClient` | 创建 OSC 客户端，配置目标 IP 和端口 | `UOSCManager` |

### Server 操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Listen` | 开始监听传入的 OSC 消息 | `UOSCServer` |
| `Stop` | 停止监听 | `UOSCServer` |
| `SetAddress` | 设置监听地址和端口（需先停止） | `UOSCServer` |
| `IsActive` | 返回是否正在监听 | `UOSCServer` |
| `SetMulticastLoopback` | 设置组播回环 | `UOSCServer` |
| `BindEventToOnOSCAddressPatternMatchesPath` | 绑定地址模式匹配的委托 | `UOSCServer` |
| `UnbindEventFromOnOSCAddressPatternMatchesPath` | 解绑特定地址模式的委托 | `UOSCServer` |
| `UnbindAllEventsFromOnOSCAddressPatternMatching` | 清除所有地址模式绑定 | `UOSCServer` |
| `GetBoundOSCAddressPatterns` | 获取所有已绑定的地址模式 | `UOSCServer` |
| `SetAllowlistClientsEnabled` | 启用/禁用客户端白名单 | `UOSCServer` |
| `AddAllowlistedClient` | 添加白名单客户端 | `UOSCServer` |
| `RemoveAllowlistedClient` | 移除白名单客户端 | `UOSCServer` |
| `GetIpAddress` | 获取服务器 IP 地址 | `UOSCServer` |
| `GetPort` | 获取服务器端口 | `UOSCServer` |

### Client 操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SendOSCMessage` | 发送 OSC 消息 | `UOSCClient` |
| `SendOSCBundle` | 发送 OSC 数据包（可包含多条消息） | `UOSCClient` |
| `SetSendIPAddress` | 设置目标地址和端口 | `UOSCClient` |
| `GetSendIPAddress` | 获取当前目标地址和端口 | `UOSCClient` |

### Server 事件委托

| 委托 | 说明 | 类型 |
|---|---|---|
| `OnOscMessageReceived` | 收到单条消息时触发（蓝图可用） | `FOSCReceivedMessageEvent` |
| `OnOscBundleReceived` | 收到 Bundle 时触发（蓝图可用） | `FOSCReceivedBundleEvent` |
| `OnOscMessageReceivedNative` | 收到消息时触发（C++ 原生） | `FOSCReceivedMessageNativeEvent` |
| `OnOscBundleReceivedNative` | 收到 Bundle 时触发（C++ 原生） | `FOSCReceivedBundleNativeEvent` |

### 消息构建

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddFloat` | 向消息添加 float 参数 | `UOSCManager` |
| `AddInt32` | 向消息添加 int32 参数 | `UOSCManager` |
| `AddInt64` | 向消息添加 int64 参数 | `UOSCManager` |
| `AddString` | 向消息添加字符串参数 | `UOSCManager` |
| `AddBool` | 向消息添加布尔参数 | `UOSCManager` |
| `AddBlob` | 向消息添加二进制数据 | `UOSCManager` |
| `AddAddress` | 向消息添加 OSC 地址（作为字符串参数） | `UOSCManager` |
| `ClearMessage` | 清除消息所有参数 | `UOSCManager` |

### 消息读取

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetFloat` | 按索引获取 float 参数 | `UOSCManager` |
| `GetInt32` | 按索引获取 int32 参数 | `UOSCManager` |
| `GetInt64` | 按索引获取 int64 参数 | `UOSCManager` |
| `GetString` | 按索引获取字符串参数 | `UOSCManager` |
| `GetBool` | 按索引获取布尔参数 | `UOSCManager` |
| `GetBlob` | 按索引获取二进制数据 | `UOSCManager` |
| `GetAllFloats` | 获取消息中所有 float 值 | `UOSCManager` |
| `GetAllInt32s` | 获取消息中所有 int32 值 | `UOSCManager` |
| `GetAllStrings` | 获取消息中所有字符串值 | `UOSCManager` |

### Bundle 操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddMessageToBundle` | 将消息添加到 Bundle | `UOSCManager` |
| `AddBundleToBundle` | 将 Bundle 添加到另一个 Bundle | `UOSCManager` |
| `GetMessagesFromBundle` | 获取 Bundle 中所有消息 | `UOSCManager` |
| `GetMessageFromBundle` | 按索引获取 Bundle 中的消息 | `UOSCManager` |
| `GetBundlesFromBundle` | 获取 Bundle 中所有子 Bundle | `UOSCManager` |
| `ClearBundle` | 清空 Bundle | `UOSCManager` |

### 地址操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OSCAddressIsValidPath` | 验证地址是否为合法路径 | `UOSCManager` |
| `OSCAddressIsValidPattern` | 验证地址是否为合法匹配模式 | `UOSCManager` |
| `OSCAddressPathMatchesPattern` | 判断模式是否匹配路径 | `UOSCManager` |
| `ConvertStringToOSCAddress` | 字符串转 OSC 地址 | `UOSCManager` |
| `GetOSCMessageAddress` | 获取消息的地址 | `UOSCManager` |
| `SetOSCMessageAddress` | 设置消息的地址 | `UOSCManager` |
| `GetOSCAddressFullPath` | 获取地址的完整路径字符串 | `UOSCManager` |
| `GetOSCAddressMethod` | 获取地址的 Method 名称 | `UOSCManager` |
| `OSCAddressPushContainer` | 向地址推入 Container | `UOSCManager` |
| `OSCAddressPopContainer` | 从地址弹出 Container | `UOSCManager` |

### 使用示例（蓝图描述）

**发送 OSC 消息：**

1. 事件 BeginPlay → `CreateOSCClient`（SendIPAddress="127.0.0.1", Port=8000, ClientName="MyClient"）→ 返回 `UOSCClient`
2. 构建消息：`FOSCMessage` 变量 → `AddString`（Message ref, "/synth/play"）→ `AddFloat`（Message ref, 440.0）→ `SendOSCMessage`（Client, Message ref）

**接收 OSC 消息：**

1. 事件 BeginPlay → `CreateOSCServer`（ReceiveIPAddress="0.0.0.0", Port=9000, bMulticastLoopback=false, bStartListening=true）→ 返回 `UOSCServer`
2. 从 Server 拖出引脚 → `Assign` `OnOscMessageReceived` → 在回调中用 `GetOSCMessageAddress` 获取地址、`GetFloat` 读取参数

**地址模式匹配（路由分发）：**

1. 创建 Server 后 → `BindEventToOnOSCAddressPatternMatchesPath`（Pattern="/synth/*", Event=自定义委托）
2. 当收到地址匹配 `/synth/anything` 的消息时，自定义委托自动触发，其他消息走 `OnOscMessageReceived`

## C++ 用法

### 头文件引入

```cpp
#include "OSCManager.h"
#include "OSCClient.h"
#include "OSCServer.h"
#include "OSCMessage.h"
#include "OSCBundle.h"
#include "OSCAddress.h"
#include "OSCTypes.h"
```

### 基本用法 — 创建 Client 并发送消息

```cpp
// 创建 OSC Client 并发送一条消息
// 来源: OSCManager.cpp CreateOSCClient

UOSCClient* Client = UOSCManager::CreateOSCClient(
    TEXT("192.168.1.100"),   // 目标 IP
    8000,                     // 目标端口
    TEXT("MyClient"),         // 客户端名称
    this                      // Outer（防止 GC）
);

// 构建 OSC 消息
FOSCMessage Message;
Message.SetAddress(FOSCAddress(TEXT("/oscillator/frequency")));
UOSCManager::AddFloat(Message, 440.0f);
UOSCManager::AddString(Message, TEXT("sine"));

// 发送
Client->SendOSCMessage(Message);
```

### 基本用法 — 创建 Server 并接收消息

```cpp
// 创建 OSC Server 并监听消息
// 来源: OSCManager.cpp CreateOSCServer

UOSCServer* Server = UOSCManager::CreateOSCServer(
    TEXT("0.0.0.0"),         // 监听所有接口
    8095,                     // 端口
    false,                    // 组播回环
    true,                     // 立即开始监听
    TEXT("MyServer"),         // 服务器名称
    this                      // Outer
);

// 绑定蓝图委托
Server->OnOscMessageReceived.AddDynamic(this, &AMyActor::OnMessageReceived);

// 绑定 C++ 原生委托（推荐，性能更好）
Server->OnOscMessageReceivedNative.AddUObject(this, &AMyActor::OnMessageNative);

// C++ 回调签名
void AMyActor::OnMessageNative(const FOSCMessage& Message, const FString& IPAddress, uint16 Port)
{
    const FOSCAddress& Address = Message.GetAddress();
    UE_LOG(LogTemp, Log, TEXT("Received from %s on %s"), *IPAddress, *Address.GetFullPath());

    // 读取参数
    if (const FOSCData* Arg = Message.GetArgumentsChecked().IsValidIndex(0) ? &Message.GetArgumentsChecked()[0] : nullptr)
    {
        if (Arg->IsFloat())
        {
            float Value = Arg->GetFloat();
        }
    }
}
```

### 进阶用法 — 地址模式匹配

```cpp
// Server 支持按地址模式路由消息，无需手动 if/else
// 来源: OSCServer.h BindEventToOnOSCAddressPatternMatchesPath

// 注册地址模式（支持通配符）
FOSCAddress Pattern(TEXT("/synth/*/frequency"));

FOSCDispatchMessageEvent DispatchDelegate;
DispatchDelegate.BindDynamic(this, &AMyActor::OnSynthFrequencyChanged);
Server->BindEventToOnOSCAddressPatternMatchesPath(Pattern, DispatchDelegate);

// 回调签名（带地址模式）
void AMyActor::OnSynthFrequencyChanged(
    const FOSCAddress& AddressPattern,
    const FOSCMessage& Message,
    const FString& IPAddress,
    int32 Port)
{
    // AddressPattern 是注册时的模式
    // Message 是实际收到的消息
    // 可以从 Message.GetAddress() 获取完整路径
}
```

### 进阶用法 — Bundle 打包多条消息

```cpp
// Bundle 可以将多条消息打包成一个 UDP 数据包发送，保证原子性
// 来源: OSCManager.cpp AddMessageToBundle

FOSCMessage Msg1;
Msg1.SetAddress(FOSCAddress(TEXT("/mixer/channel/1/volume")));
UOSCManager::AddFloat(Msg1, 0.8f);

FOSCMessage Msg2;
Msg2.SetAddress(FOSCAddress(TEXT("/mixer/channel/2/volume")));
UOSCManager::AddFloat(Msg2, 0.5f);

FOSCBundle Bundle;
UOSCManager::AddMessageToBundle(Msg1, Bundle);
UOSCManager::AddMessageToBundle(Msg2, Bundle);

Client->SendOSCBundle(Bundle);
```

### 进阶用法 — 使用 UE::OSC::FOSCData 直接操作

```cpp
// C++ 可以直接使用 FOSCData 类型系统，比蓝图更高效
// 来源: OSCTypes.h

using namespace UE::OSC;

FOSCData FloatData(3.14f);           // float
FOSCData IntData(42);                // int32
FOSCData Int64Data((int64)12345678); // int64
FOSCData StrData(TEXT("hello"));     // string
FOSCData BoolData(true);             // bool
FOSCData BlobData(TArray<uint8>{1, 2, 3}); // blob
FOSCData ColorData(FColor::Red);     // color (RGBA)

// 类型检查
if (FloatData.IsFloat()) { float V = FloatData.GetFloat(); }
if (StrData.IsString()) { FString S = StrData.GetString(); }

// 特殊值
const FOSCData& Nil = FOSCData::NilData();
const FOSCData& Inf = FOSCData::Infinitum();
```

## Demo 示例

### 完整最小示例：OSC 回声服务器

**MyOSCEchoActor.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "OSCMessage.h"
#include "MyOSCEchoActor.generated.h"

class UOSCServer;
class UOSCClient;

UCLASS()
class AMyOSCEchoActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UFUNCTION()
    void OnOSCMessageReceived(const FOSCMessage& Message, const FString& IPAddress, int32 Port);

private:
    UPROPERTY()
    TObjectPtr<UOSCServer> Server;

    UPROPERTY()
    TObjectPtr<UOSCClient> EchoClient;
};
```

**MyOSCEchoActor.cpp**

```cpp
#include "MyOSCEchoActor.h"
#include "OSCManager.h"
#include "OSCServer.h"
#include "OSCClient.h"
#include "OSCAddress.h"

void AMyOSCEchoActor::BeginPlay()
{
    Super::BeginPlay();

    // 在 9000 端口监听
    Server = UOSCManager::CreateOSCServer(
        TEXT("0.0.0.0"), 9000, false, true, TEXT("EchoServer"), this);

    // Client 发回同一地址
    EchoClient = UOSCManager::CreateOSCClient(
        TEXT("127.0.0.1"), 9001, TEXT("EchoClient"), this);

    Server->OnOscMessageReceived.AddDynamic(this, &AMyOSCEchoActor::OnOSCMessageReceived);
}

void AMyOSCEchoActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (Server) Server->Stop();
    if (EchoClient) EchoClient->Stop();
    Super::EndPlay(EndPlayReason);
}

void AMyOSCEchoActor::OnOSCMessageReceived(const FOSCMessage& Message, const FString& IPAddress, int32 Port)
{
    // 将收到的消息原样发回（回声）
    FOSCMessage Reply = Message;
    EchoClient->SendOSCMessage(Reply);

    UE_LOG(LogTemp, Log, TEXT("Echoed message from %s:%d [%s]"),
        *IPAddress, Port, *Message.GetAddress().GetFullPath());
}
```

**Build.cs 依赖：**

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "OSC"       // 添加 OSC 模块依赖
});
```

## 调试控制台命令

插件注册了以下控制台命令，可在运行时诊断：

| 命令 | 说明 |
|---|---|
| `osc.servers` | 打印所有 OSC Server 的诊断信息（IP、端口、绑定的地址模式） |
| `osc.clients` | 打印所有 OSC Client 的诊断信息 |
| `osc.server.connect <Name> [IP] [Port]` | 重连指定 Server |
| `osc.server.connectById <Id> [IP] [Port]` | 按 ID 重连 Server |
| `osc.client.connect <Name> [IP] [Port]` | 重连指定 Client |
| `osc.client.connectById <Id> [IP] [Port]` | 按 ID 重连 Client |

## 模块依赖

你的模块需要依赖以下模块才能使用 OSC 插件：

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、容器、字符串 |
| `CoreUObject` | UObject 系统、反射 |
| `Engine` | 世界、Actor 等引擎核心 |
| `OSC` | OSC 协议实现（插件自身模块） |

OSC 插件内部还私有依赖了 `InputCore`、`Networking`、`Sockets`，但使用者无需关心。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-10-01 | `f9399052` | Fix OSC::FStream::WriteBlob | 修复 Blob 写入的 bug，影响二进制数据传输的正确性 |
| 2025-09-12 | `ce6ff392` | Addressing nodiscard attribute issues for FTSTicker::RemoveTicker | 代码规范修复，处理 [[nodiscard]] 警告 |
| 2025-06-11 | `afdf8d75` | Replace some usages of FORCEINLINE with inline in Online modules | 编译优化，减少不必要的内联 |

### 维护评价

- **活跃维护**：最近 6 个月内有实质性修复（WriteBlob bug fix），说明 Epic 仍在关注此插件
- **成熟稳定**：创建于 2019 年（约 7 年前），代码经过多次重构，UE 5.5 进行了大规模 API 清理（大量 `UE_DEPRECATED` 标记，迁移到 `UE::OSC` 命名空间）
- **架构合理**：Server 使用独立线程（`FServerReceiver` 继承 `FRunnable`）接收数据，通过 SPSC 队列分发到 GameThread，不阻塞主线程
- **默认禁用**：`EnabledByDefault=false`，属于可选功能插件，需要手动启用
- **无独立测试**：插件目录内无自动化测试用例
- **推荐使用**：对于需要 OSC 通信的场景，这是 Epic 官方维护的实现，质量可靠

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/OSC)
- [官方文档]()（.uplugin 中未提供文档 URL）
- [RemoteControlProtocolOSC 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControlProtocolOSC)（基于此插件的 Remote Control 扩展）
