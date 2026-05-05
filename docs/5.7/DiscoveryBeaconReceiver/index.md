# Discovery Beacon Receiver

> Listens for messages on a multicast socket and replies with information about the engine.

| 属性 | 值 |
|---|---|
| 分类 | Messaging |
| 默认启用 | Installed=false（需手动启用） |
| 包含内容 | true |
| 模块 | DiscoveryBeaconReceiver (Runtime) |
| 创建时间 | 2023-12-01 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/DiscoveryBeaconReceiver) | |

## 用途

DiscoveryBeaconReceiver 是一个**局域网服务发现**基础设施插件。它在后台线程上监听 UDP 多播（multicast）信标消息，当收到匹配协议标识的消息时，自动回复引擎实例信息（版本号、GUID、自定义响应数据），使局域网上的外部应用能自动发现并列出当前运行中的 Unreal 引擎实例。

它本身**不包含具体的发现逻辑**，而是一个抽象基类 `FDiscoveryBeaconReceiver`。你需要继承它并实现三个纯虚函数来定义：监听哪个地址/端口、如何构建响应数据。UE5 已有两个现成的子类：

- **VirtualCameraBeaconReceiver** — VCAM 应用通过 Pixel Streaming 发现引擎实例
- **WebSocketMessagingBeaconReceiver** — 外部 WebSocket 消息客户端发现引擎实例

## 使用场景

- 你在做 Virtual Production，需要用 iPad 上的 VCAM app 自动发现局域网中的 Unreal 编辑器
- 你在做外部工具集成，需要让非 UE 程序自动发现局域网内的引擎实例并获取连接信息
- 你需要实现自定义的局域网服务发现协议——继承 `FDiscoveryBeaconReceiver` 并实现协议即可

## 蓝图用法

该插件没有暴露任何 BlueprintCallable 接口。它是纯 C++ 的底层网络基础设施，完全在后台线程运行。

## C++ 用法

### 头文件引入

```cpp
#include "DiscoveryBeaconReceiver.h"
```

### 核心类：FDiscoveryBeaconReceiver

`FDiscoveryBeaconReceiver` 继承自 `FRunnable`，在独立线程中监听 UDP 多播报文。

**构造函数**需要三个参数：

| 参数 | 说明 |
|---|---|
| `InDescription` | 调试用的名字，会出现在日志和线程名中 |
| `InProtocolIdentifier` | 字节数组，用于标识哪些消息是发给你的（如 `{ 'U', 'E', 'V', 'C', 'a', 'm' }`） |
| `InProtocolVersion` | 你回复消息时携带的协议版本号 |

**生命周期方法**：

| 方法 | 说明 |
|---|---|
| `Startup()` | 创建 UDP 多播 socket，加入多播组，启动监听线程 |
| `Shutdown()` | 终止监听线程，销毁 socket |

**需要实现的三个纯虚函数**：

| 纯虚函数 | 返回 | 说明 |
|---|---|---|
| `GetDiscoveryAddress(FIPv4Address& OutAddress)` | `bool` | 返回监听的多播 IP 地址（如 `239.x.x.x`） |
| `GetDiscoveryPort()` | `int32` | 返回监听端口，负值表示无效 |
| `MakeBeaconResponse(uint8, FArrayReader&, FArrayWriter&)` | `bool` | 构建响应数据；必须消费完 `InMessageData` 的所有数据，否则消息被忽略 |

### 基本用法（VirtualCamera 子类示例）

来自 `Engine/Plugins/VirtualProduction/VirtualCameraCore/Source/PixelStreamingVCam/Private/Networking/VirtualCameraBeaconReceiver.cpp`：

```cpp
// 1. 定义协议标识和版本
namespace Constants
{
    constexpr uint8 ProtocolVersion = 0;
    const TArray<uint8> ProtocolIdentifier = { 'U', 'E', 'V', 'C', 'a', 'm' };
}

// 2. 继承 FDiscoveryBeaconReceiver
class FVirtualCameraBeaconReceiver : public FDiscoveryBeaconReceiver
{
public:
    FVirtualCameraBeaconReceiver()
        : FDiscoveryBeaconReceiver(
            TEXT("VCAMBeaconResponder"),   // 调试名
            Constants::ProtocolIdentifier, // 协议标识
            Constants::ProtocolVersion     // 协议版本
        )
    {}

    virtual void Startup() override
    {
        PixelStreamingPort = IPixelStreamingEditorModule::Get().GetViewerPort();
        FDiscoveryBeaconReceiver::Startup(); // 调用基类启动
    }

protected:
    virtual bool GetDiscoveryAddress(FIPv4Address& OutAddress) const override
    {
        // 从设置读取多播地址
        const auto& Settings = *GetDefault<UVirtualCameraCoreUserSettings>();
        return FIPv4Address::Parse(Settings.DiscoveryEndpoint, OutAddress);
    }

    virtual int32 GetDiscoveryPort() const override
    {
        return GetDefault<UVirtualCameraCoreUserSettings>()->DiscoveryPort;
    }

    virtual bool MakeBeaconResponse(uint8 BeaconProtocolVersion,
        FArrayReader& InMessageData, FArrayWriter& OutResponseData) const override
    {
        // 写入连接信息：端口、就绪状态、友好名称
        OutResponseData << (uint32&)PixelStreamingPort;
        OutResponseData << (uint8&)bIsStreamingReady;
        OutResponseData << (FString&)GetFriendlyName();
        return true; // true = 发送回复
    }
};
```

### 进阶用法（JSON/CBOR 序列化响应）

WebSocketMessaging 子类展示了更复杂的响应格式（来自 `WebSocketMessagingBeaconReceiver.cpp`）：

```cpp
// MakeBeaconResponse 中可以序列化为 JSON 或 CBOR
bool MakeBeaconResponse(uint8 InBeaconProtocolVersion,
    FArrayReader& InMessageData, FArrayWriter& OutResponseData) const override
{
    FWebSocketMessagingBeaconPayload Reply;
    if (Settings && Settings->EnableTransport)
    {
        Reply.Services.Add({ TEXT("WebSocketMessaging"), Settings->GetServerPort() });
    }

    // 根据设置选择序列化格式
    if (PayloadFormat == EWebSocketMessagingTransportFormat::Json)
    {
        return SerializeToJson(Reply, OutResponseData);  // UTF-8 JSON
    }
    return SerializeToCbor(Reply, OutResponseData);       // CBOR 二进制
}
```

## Demo 示例

一个最小的自定义 Beacon Receiver：

**MyBeaconReceiver.h**：
```cpp
#pragma once
#include "DiscoveryBeaconReceiver.h"

class FMyBeaconReceiver : public FDiscoveryBeaconReceiver
{
public:
    FMyBeaconReceiver();

protected:
    virtual bool GetDiscoveryAddress(FIPv4Address& OutAddress) const override;
    virtual int32 GetDiscoveryPort() const override;
    virtual bool MakeBeaconResponse(uint8 BeaconProtocolVersion,
        FArrayReader& InMessageData, FArrayWriter& OutResponseData) const override;
};
```

**MyBeaconReceiver.cpp**：
```cpp
#include "MyBeaconReceiver.h"
#include "Interfaces/IPv4/IPv4Address.h"
#include "Serialization/ArrayReader.h"
#include "Serialization/ArrayWriter.h"

static constexpr uint8 MyProtocolVersion = 1;
static const TArray<uint8> MyProtocolId = { 'M', 'Y', 'A', 'P', 'P' };

FMyBeaconReceiver::FMyBeaconReceiver()
    : FDiscoveryBeaconReceiver(TEXT("MyBeacon"), MyProtocolId, MyProtocolVersion)
{
}

bool FMyBeaconReceiver::GetDiscoveryAddress(FIPv4Address& OutAddress) const
{
    // 239.0.0.x 是组织本地多播地址范围
    return FIPv4Address::Parse(TEXT("239.0.0.1"), OutAddress);
}

int32 FMyBeaconReceiver::GetDiscoveryPort() const
{
    return 19876; // 自定义端口
}

bool FMyBeaconReceiver::MakeBeaconResponse(uint8 BeaconProtocolVersion,
    FArrayReader& InMessageData, FArrayWriter& OutResponseData) const
{
    // 必须消费完所有输入数据
    InMessageData.Seek(InMessageData.Num());

    // 写入响应
    FString AppName = TEXT("MyGame");
    OutResponseData << (FString&)AppName;
    return true;
}
```

**Build.cs 依赖**：
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "DiscoveryBeaconReceiver"
});
```

**启动/关闭**（在你的模块 `StartupModule`/`ShutdownModule` 中）：
```cpp
// StartupModule
BeaconReceiver = MakeShared<FMyBeaconReceiver>();
BeaconReceiver->Startup();

// ShutdownModule
BeaconReceiver->Shutdown();
BeaconReceiver.Reset();
```

## 模块依赖

你的模块需在 Build.cs 中声明以下依赖：

| 模块 | 用途 |
|---|---|
| `DiscoveryBeaconReceiver` | 提供 `FDiscoveryBeaconReceiver` 基类 |

该插件自身依赖（私有）：

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、FRunnable、线程 |
| `CoreUObject` | UObject 基础 |
| `Serialization` | FArrayReader/FArrayWriter 序列化 |
| `Engine` | 私有依赖 |
| `Networking` | 私有依赖 |
| `Sockets` | UDP Socket 操作 |

## 信标协议格式

基类处理的消息格式（字节序为小端）：

**请求（外部 → 引擎）**：
```
[ProtocolIdentifier bytes] [uint8: ProtocolVersion] [自定义数据...]
```

**响应（引擎 → 外部）**：
```
[uint8: EngineProtocolVersion] [FGuid: 16字节实例ID] [自定义响应数据...]
```

引擎会检查消息前缀是否匹配 `ProtocolIdentifier`，不匹配则忽略。匹配后读取协议版本，调用子类的 `MakeBeaconResponse` 构建回复。如果子类返回 `true` 但消息数据未完全消费（`!MessageData.AtEnd()`），回复将被丢弃。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2024-03-26 | `c7b4cb8` | Fix Unreal failing to respond to discovery beacons on Mac | 修复 Mac 平台上信标不回复的问题 |
| 2023-12-14 | `9f1f93f` | Implement beacon receiver to enable local network detection of VCAM-compatible engine instances | 为 VCAM 实现了完整的信标接收器功能 |
| 2023-12-01 | `a674b68` | Refactor beacon receiver to a generic base class | 初始提交：将信标接收器重构为通用基类 |

### 维护评价

- **创建于 2023-12-01**，约 2.5 年历史 🆕
- 最后一次功能性更新在 2024-03-26（Mac 平台修复），之后无新 commit
- 作为底层基础设施类，代码量极小（约 200 行），逻辑稳定，不需要频繁更新
- 目前有两个活跃的下游使用者：VirtualCameraCore 和 WebSocketMessaging
- **评价**：稳定可用。作为抽象基类它已经完成了设计目标，不需要更多功能。如果你需要局域网服务发现能力，直接继承使用即可。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/DiscoveryBeaconReceiver)
- [VirtualCameraBeaconReceiver（使用示例）](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/VirtualProduction/VirtualCameraCore/Source/PixelStreamingVCam/Private/Networking/VirtualCameraBeaconReceiver.cpp)
- [WebSocketMessagingBeaconReceiver（使用示例）](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/WebSocketMessaging/Source/WebSocketMessaging/Private/WebSocketMessagingBeaconReceiver.cpp)
