# Discovery Beacon Receiver

> Listens for messages on a multicast socket and replies with information about the engine.

| 属性 | 值 |
|---|---|
| 中文名 | 发现信标接收器 |
| 分类 | Messaging |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DiscoveryBeaconReceiver` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-12-01 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/DiscoveryBeaconReceiver) | |

## 用途

这个插件提供了一个基类 `FDiscoveryBeaconReceiver`，用于在本地网络中实现引擎的自动发现功能。它运行一个独立的线程，在指定的多播地址和端口上监听特定的“信标”消息。当收到符合协议标识符和版本的信标请求时，它会回复一个包含引擎连接信息（如 IP、端口）的响应，使远程应用程序能够自动探测并连接到网络上兼容的 Unreal Engine 实例。

其核心目的是支持如 **LiveLinkVCAM** 等需要快速发现网络中引擎实例的虚拟制作工作流。

## 使用场景

- 你在开发一个虚拟制作工作站（如 VCAM 控制器），需要自动发现局域网中运行的 Unreal Engine 实例进行连接和操控。
- 你需要实现一个自定义的网络发现协议，用于在本地网络中找到并识别特定的 Unreal Engine 服务。
- 你希望扩展引擎的网络发现机制，为其他需要自动发现引擎实例的插件或工具提供基础。

## 蓝图用法

此插件主要提供 C++ 基类，**未暴露任何蓝图节点**。其核心功能通过继承和重写 C++ 类来实现。

## C++ 用法

### 头文件引入

```cpp
#include "DiscoveryBeaconReceiver.h"
```

### 基本用法

`FDiscoveryBeaconReceiver` 是一个抽象基类，需要继承并实现其纯虚函数来定义具体的发现行为。

1.  **继承并实现接口**：
    创建一个自定义类，继承 `FDiscoveryBeaconReceiver` 并实现三个纯虚函数。
    ```cpp
    // MyBeaconReceiver.h
    #include "DiscoveryBeaconReceiver.h"

    class FMyBeaconReceiver : public FDiscoveryBeaconReceiver
    {
    public:
        FMyBeaconReceiver()
            : FDiscoveryBeaconReceiver(
                TEXT("MyAppBeacon"), // 描述，用于日志
                {0x01, 0x02, 0x03}, // 自定义协议标识符
                1 // 协议版本
            )
        {}

    protected:
        // 1. 指定监听的多播地址
        virtual bool GetDiscoveryAddress(FIPv4Address& OutAddress) const override;

        // 2. 指定监听的端口
        virtual int32 GetDiscoveryPort() const override;

        // 3. 处理收到的信标消息并生成响应数据
        virtual bool MakeBeaconResponse(uint8 BeaconProtocolVersion, FArrayReader& InMessageData, FArrayWriter& OutResponseData) const override;
    };
    ```

2.  **实现发现地址和端口**：
    通常使用一个标准的多播地址（如 `230.0.0.1`）和端口（如 `14578`）。
    ```cpp
    // MyBeaconReceiver.cpp
    #include "Sockets/Public/IPv4Address.h"

    bool FMyBeaconReceiver::GetDiscoveryAddress(FIPv4Address& OutAddress) const
    {
        // 返回一个多播地址，用于在网络上发现
        OutAddress = FIPv4Address(230, 0, 0, 1);
        return true;
    }

    int32 FMyBeaconReceiver::GetDiscoveryPort() const
    {
        return 14578; // 使用约定的端口
    }
    ```

3.  **实现信标响应**：
    这是核心逻辑，用于将引擎的连接信息写入响应数据。
    ```cpp
    #include "Serialization/BufferArchive.h"

    bool FMyBeaconReceiver::MakeBeaconResponse(uint8 BeaconProtocolVersion, FArrayReader& InMessageData, FArrayWriter& OutResponseData) const
    {
        // 1. 验证收到的协议版本是否兼容
        if (BeaconProtocolVersion > 1) // 我们只支持版本 1 或更低
        {
            UE_LOG(LogDiscoveryBeaconReceiver, Warning, TEXT("Unsupported beacon protocol version: %d"), BeaconProtocolVersion);
            return false;
        }

        // 2. 写入引擎实例的唯一标识符 (GUID)
        OutResponseData << Guid;

        // 3. 写入用于 RPC 连接的端口 (例如 Level Editor 的消息总线端口)
        int32 RPCPort = /* 从某个配置或系统获取 */ 27015;
        OutResponseData << RPCPort;

        // 4. 可以添加其他自定义信息，如引擎版本、项目名称等
        FString EngineVersion = FEngineVersion::Current().ToString();
        OutResponseData << EngineVersion;

        UE_LOG(LogDiscoveryBeaconReceiver, Log, TEXT("Responded to beacon with GUID: %s"), *Guid.ToString());
        return true;
    }
    ```

4.  **启动与关闭**：
    在你的应用程序生命周期中管理接收器。
    ```cpp
    // 在应用程序初始化时
    TSharedPtr<FMyBeaconReceiver> MyReceiver = MakeShared<FMyBeaconReceiver>();
    MyReceiver->Startup(); // 打开套接字并启动监听线程

    // 在应用程序关闭时
    MyReceiver->Shutdown(); // 关闭套接字并停止线程
    ```

### 进阶用法

- **自定义协议标识符**：为你的应用生成并使用唯一的字节序列（`ProtocolIdentifier`），避免与其他插件冲突。
- **扩展消息数据**：在 `MakeBeaconResponse` 中，除了基础信息外，还可以根据 `InMessageData` 中接收到的客户端请求，返回更丰富的状态或能力信息。
- **多实例处理**：每个 `FDiscoveryBeaconReceiver` 实例代表一个独立的信标通道，你可以为不同的服务启动多个实例，使用不同的协议标识符或端口。

## Demo 示例

### MyBeaconReceiver.h
```cpp
// MyBeaconReceiver.h
#pragma once

#include "CoreMinimal.h"
#include "DiscoveryBeaconReceiver.h"

class FMyBeaconReceiver final : public FDiscoveryBeaconReceiver
{
public:
    FMyBeaconReceiver();
    virtual ~FMyBeaconReceiver() override = default;

protected:
    // FDiscoveryBeaconReceiver interface
    virtual bool GetDiscoveryAddress(FIPv4Address& OutAddress) const override;
    virtual int32 GetDiscoveryPort() const override;
    virtual bool MakeBeaconResponse(uint8 BeaconProtocolVersion, FArrayReader& InMessageData, FArrayWriter& OutResponseData) const override;
    // End of FDiscoveryBeaconReceiver interface

private:
    // 你的自定义协议标识符
    static const TArray<uint8> MyProtocolIdentifier;
};
```

### MyBeaconReceiver.cpp
```cpp
// MyBeaconReceiver.cpp
#include "MyBeaconReceiver.h"
#include "IPv4Address.h"
#include "Serialization/BufferArchive.h"

const TArray<uint8> FMyBeaconReceiver::MyProtocolIdentifier = {0xDE, 0xAD, 0xBE, 0xEF, 0x01};

FMyBeaconReceiver::FMyBeaconReceiver()
    : FDiscoveryBeaconReceiver(TEXT("MyGameDiscovery"), MyProtocolIdentifier, 1)
{
}

bool FMyBeaconReceiver::GetDiscoveryAddress(FIPv4Address& OutAddress) const
{
    // 使用链路本地多播地址
    OutAddress = FIPv4Address(239, 192, 0, 1);
    return true;
}

int32 FMyBeaconReceiver::GetDiscoveryPort() const
{
    return 19001;
}

bool FMyBeaconReceiver::MakeBeaconResponse(uint8 BeaconProtocolVersion, FArrayReader& InMessageData, FArrayWriter& OutResponseData) const
{
    if (BeaconProtocolVersion != 1)
    {
        return false;
    }

    // 写入引擎GUID和游戏服务器端口
    OutResponseData << GetGuid();
    int32 GamePort = 7777; // 假设游戏服务器在7777端口
    OutResponseData << GamePort;

    return true;
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Sockets/Networking 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 UE_LOG 宏迁移到新的 UE_LOGF 宏，属于日志系统优化。 |
| 2024-03-07 | `94ba11bb` | [LiveLinkVCAM] Fix Unreal failing to respond to discovery beacons on Mac | 修复了在 Mac 平台上引擎无法响应发现信标的 Bug，提高了跨平台兼容性。 |
| 2023-12-15 | `9f1f93f0` | [LiveLinkVCAM] Implement beacon receiver to enable local network detection of VCAM-compatible engine | 初始实现了信标接收器功能，用于支持 LiveLinkVCAM 在本地网络中发现引擎。 |
| 2023-12-01 | `a674b680` | [UnrealStage] Refactor beacon receiver to a generic base class | 将原先的信标接收器重构为通用基类，以便于其他系统（如 VCAM）复用。 |

### 维护评价

- **创建时间**：约 2 年前，是一个相对较新的插件。
- **更新频率**：创建后经历了 2 次实质性功能/修复更新（跨平台修复、重构），以及 1 次代码现代化更新（日志宏迁移）。更新频率较低，但每次更新都有明确目的。
- **活跃度**：插件仍在维护中，最近一次更新在 2026 年。它作为 LiveLinkVCAM 虚拟制作工作流的基础设施部分，预计会随着该工作流的发展而持续维护。
- **已知限制**：插件本身只提供基类，不包含具体的实现。使用者需要自行实现协议细节。`EnabledByDefault=false` 表明它不是基础运行时必需组件。
- **推荐使用**：**推荐**。如果你需要实现网络发现功能，特别是与虚拟制作（VCAM）相关，这是一个设计良好且经过实战检验的基础组件。它为构建自定义发现协议提供了清晰、线程安全的框架。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/DiscoveryBeaconReceiver)
- [官方文档]() （无）
- [测试用例]() （插件目录内未发现公开测试文件）