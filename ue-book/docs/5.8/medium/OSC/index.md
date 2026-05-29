# OSC (Open Sound Control)

> Implements the OSC 1.0 specification, allowing users to send and receive OSC messages and bundles between remote clients or applications.

| 属性 | 值 |
|---|---|
| 中文名 | 开放声音控制 |
| 分类 | Input Devices |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OSC` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-05-31 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OSC) | |

## 用途

OSC（Open Sound Control）是一种用于在网络中传输控制数据的开放协议，广泛应用于音频软件、互动装置、灯光控制等领域。本插件完整实现了 OSC 1.0 规范，让你可以在 UE5 与外部应用程序（如 Max/MSP、TouchDesigner、Ableton Live、OSC 控制器等）之间双向通信。

**核心能力：**
- 创建 OSC Server 监听并接收来自远程客户端的消息/包
- 创建 OSC Client 向远程端点发送消息/包
- 构建和解析 OSC Message（带地址和参数）与 Bundle（消息分组）
- 基于地址模式（Pattern）的事件分发，支持通配符匹配
- 客户端白名单过滤
- 支持所有 OSC 标准数据类型：Float、Int32、Int64、String、Blob、Bool、Color、Double 等

## 使用场景

- 你在做交互装置/沉浸式体验，需要从 TouchDesigner 或 Max/MSP 发送控制信号到 UE5 → 用 OSC Server 接收
- 你需要通过手机上的 OSC 控制器（如 TouchOSC）远程操控 UE5 中的角色或参数 → 用 OSC Server + 地址模式匹配
- 你需要将 UE5 中的事件实时发送到音频软件（如 Ableton Live）→ 用 OSC Client 发送
- 你在做多机联动的大型投影装置，多台电脑需要同步状态 → 用 OSC Client/Server 组合 + 组播（Multicast）

## 蓝图用法

### 创建 Server 和 Client

使用 `UOSCManager` 的静态工厂函数创建实例：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create OSC Server` | 创建并返回一个 OSC Server，可指定监听 IP、端口、组播回环和是否立即开始监听 | `UOSCManager` |
| `Create OSC Client` | 创建并返回一个 OSC Client，可指定目标 IP 和端口 | `UOSCManager` |

### Server 监听与事件

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Listen` | 开始监听传入的 OSC 消息 | `UOSCServer` |
| `Stop` | 停止监听并清理网络资源 | `UOSCServer` |
| `Set Address` | 设置监听地址和端口（Server 未激活时才可调用） | `UOSCServer` |
| `Is Active` | 返回 Server 是否正在监听 | `UOSCServer` |
| `On Osc Message Received` | 接收到 OSC 消息时触发的事件（可蓝图绑定） | `UOSCServer` |
| `On Osc Bundle Received` | 接收到 OSC 包时触发的事件（可蓝图绑定） | `UOSCServer` |

### Client 发送

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Send IP Address` | 设置发送目标 IP 和端口 | `UOSCClient` |
| `Send OSC Message` | 发送一条 OSC 消息到目标地址 | `UOSCClient` |
| `Send OSC Bundle` | 发送一个 OSC 包到目标地址 | `UOSCClient` |

### 消息构建（添加参数）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Float to OSC Message` | 向消息末尾添加 Float 参数 | `UOSCManager` |
| `Add Integer to OSC Message` | 向消息末尾添加 Int32 参数 | `UOSCManager` |
| `Add Integer (64-bit) to OSC Message` | 向消息末尾添加 Int64 参数 | `UOSCManager` |
| `Add String to OSC Message` | 向消息末尾添加 String 参数 | `UOSCManager` |
| `Add Bool to OSC Message` | 向消息末尾添加 Bool 参数 | `UOSCManager` |
| `Add Blob to OSC Message` | 向消息末尾添加 Blob（字节数组）参数 | `UOSCManager` |
| `Clear OSC Message` | 清除消息中的所有参数 | `UOSCManager` |

### 消息解析（获取参数）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get OSC Message Float At Index` | 从消息指定索引获取 Float 值 | `UOSCManager` |
| `Get OSC Message Integer at Index` | 从消息指定索引获取 Int32 值 | `UOSCManager` |
| `Get OSC Message String at Index` | 从消息指定索引获取 String 值 | `UOSCManager` |
| `Get OSC Message Bool At Index` | 从消息指定索引获取 Bool 值 | `UOSCManager` |
| `Get OSC Message Floats` | 获取消息中所有 Float 值 | `UOSCManager` |
| `Get OSC Message Strings` | 获取消息中所有 String 值 | `UOSCManager` |

### 地址操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get OSC Message Address` | 获取消息的 OSC 地址 | `UOSCManager` |
| `Set OSC Message Address` | 设置消息的 OSC 地址 | `UOSCManager` |
| `Convert String to OSC Address` | 将字符串转换为 OSC 地址对象 | `UOSCManager` |
| `OSC Address Path Matches Pattern` | 判断地址路径是否匹配地址模式（支持通配符） | `UOSCManager` |
| `Is OSC Address Valid Path` | 检查地址是否为合法路径 | `UOSCManager` |
| `Is OSC Address Valid Pattern` | 检查地址是否为合法匹配模式 | `UOSCManager` |

### 地址模式分发

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Bind Event to On OSC Address Pattern Matches Path` | 将事件绑定到指定地址模式，当收到匹配的消息时自动触发 | `UOSCServer` |
| `Unbind Event from On OSC Address Pattern Matches Path` | 解除特定事件绑定 | `UOSCServer` |
| `Unbind All Events from On OSC Address Pattern Matching` | 清除所有地址模式绑定 | `UOSCServer` |

### Bundle 操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add OSC Message to Bundle` | 将消息添加到包中 | `UOSCManager` |
| `Add OSC Bundle to Bundle` | 将子包添加到包中（嵌套包） | `UOSCManager` |
| `Get OSC Messages From Bundle` | 从包中获取所有消息 | `UOSCManager` |
| `Get OSC Bundles From Bundle` | 从包中获取所有子包 | `UOSCManager` |

### 蓝图使用示例

**发送端（Client）：**
1. 使用 `Create OSC Client` 创建 Client，IP 设为 `"192.168.1.100"`，端口设为 `8000`
2. 使用 `Convert String to OSC Address` 创建地址 `"/avatar/parameters/vrc_expression"`
3. 创建 FOSCMessage，用 `Add Float to OSC Message` 添加参数
4. 设置消息地址，调用 `Send OSC Message` 发送

**接收端（Server）：**
1. 使用 `Create OSC Server` 创建 Server，IP 设为 `"0.0.0.0"`（监听所有网卡），端口 `8000`，勾选 `Start Listening`
2. 绑定 `On Osc Message Received` 事件
3. 在事件回调中，用 `Get OSC Message Address` 获取地址，用 `Get OSC Message Float At Index` 解析参数
4. 或使用 `Bind Event to On OSC Address Pattern Matches Path` 实现按地址自动分发

## C++ 用法

### 头文件引入

```cpp
#include "OSCManager.h"
#include "OSCServer.h"
#include "OSCClient.h"
#include "OSCMessage.h"
#include "OSCBundle.h"
#include "OSCAddress.h"
```

### 基本用法：发送和接收 OSC 消息

```cpp
// 创建 OSC Server 并监听
UOSCServer* Server = UOSCManager::CreateOSCServer(
    TEXT("0.0.0.0"),  // 监听所有网络接口
    9000,              // 端口号
    false,             // 不启用组播回环
    true,              // 立即开始监听
    TEXT("MyServer"),
    GetTransientPackage()
);

// 绑定接收事件
Server->OnOscMessageReceived.AddDynamic(this, &AMyActor::OnMessageReceived);

// 创建 OSC Client 并发送
UOSCClient* Client = UOSCManager::CreateOSCClient(
    TEXT("192.168.1.100"),  // 目标 IP
    9000,                   // 目标端口
    TEXT("MyClient"),
    GetTransientPackage()
);

// 构建 OSC 消息
FOSCMessage Message;
UOSCManager::SetOSCMessageAddress(Message, FOSCAddress(TEXT("/test/parameter")));
UOSCManager::AddFloat(Message, 0.75f);
UOSCManager::AddString(Message, TEXT("Hello OSC"));

// 发送消息
Client->SendOSCMessage(Message);
```

### 接收回调实现

```cpp
// 头文件中声明
UFUNCTION()
void OnMessageReceived(const FOSCMessage& Message, const FString& IPAddress);

// 实现
void AMyActor::OnMessageReceived(const FOSCMessage& Message, const FString& IPAddress)
{
    // 获取地址
    FOSCAddress Address = UOSCManager::GetOSCMessageAddress(Message);
    FString Path = UOSCManager::GetOSCAddressFullPath(Address);
    UE_LOG(LogTemp, Log, TEXT("Received from %s: %s"), *IPAddress, *Path);

    // 读取参数
    float Value;
    if (UOSCManager::GetFloat(Message, 0, Value))
    {
        UE_LOG(LogTemp, Log, TEXT("  Float param: %f"), Value);
    }

    FString StrValue;
    if (UOSCManager::GetString(Message, 1, StrValue))
    {
        UE_LOG(LogTemp, Log, TEXT("  String param: %s"), *StrValue);
    }
}
```

### 基于地址模式的事件分发

```cpp
// 绑定特定地址模式的事件处理器
Server->BindEventToOnOSCAddressPatternMatchesPath(
    FOSCAddress(TEXT("/avatar/*")),
    FOSCDispatchMessageEventBP::CreateUObject(this, &AMyActor::OnAvatarMessage)
);

// 处理函数
void AMyActor::OnAvatarMessage(const FOSCMessage& Message, const FString& IPAddress)
{
    // 只有地址匹配 /avatar/* 的消息才会触发此回调
    // 可用于精细的消息路由
}
```

### 进阶用法：Bundle 打包发送与 Client 白名单

```cpp
// 创建 Bundle 并添加多条消息
FOSCBundle Bundle;

FOSCMessage Msg1;
UOSCManager::SetOSCMessageAddress(Msg1, FOSCAddress(TEXT("/light/brightness")));
UOSCManager::AddFloat(Msg1, 1.0f);
UOSCManager::AddMessageToBundle(Msg1, Bundle);

FOSCMessage Msg2;
UOSCManager::SetOSCMessageAddress(Msg2, FOSCAddress(TEXT("/light/color")));
UOSCManager::AddInt32(Msg2, 255);
UOSCManager::AddMessageToBundle(Msg2, Bundle);

// 发送 Bundle（原子性：接收端会一次性收到所有消息）
Client->SendOSCBundle(Bundle);

// Server 端启用客户端白名单过滤
Server->SetAllowlistClientsEnabled(true);
Server->AddAllowlistedClient(TEXT("192.168.1.100"), 9000);
Server->AddAllowlistedClient(TEXT("192.168.1.101"));
```

## Demo 示例

完整的最小发送/接收示例：

```cpp
// OSCDemoActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "OSCMessage.h"
#include "OSCAddress.h"
#include "OSCTypes.h"
#include "OSCServer.h"
#include "OSCClient.h"
#include "OSCDemoActor.generated.h"

UCLASS()
class AOSCDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AOSCDemoActor();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    // 接收回调（蓝图可绑定版本）
    UFUNCTION()
    void OnOscMessageReceived(const FOSCMessage& Message, const FString& IPAddress);

    // 发送一条测试消息
    UFUNCTION(BlueprintCallable)
    void SendTestMessage(float Value);

private:
    UPROPERTY()
    TObjectPtr<UOSCServer> Server;

    UPROPERTY()
    TObjectPtr<UOSCClient> Client;

    // 监听端口
    UPROPERTY(EditAnywhere, Category = "OSC")
    int32 ListenPort = 9000;

    // 发送目标 IP
    UPROPERTY(EditAnywhere, Category = "OSC")
    FString TargetIP = TEXT("127.0.0.1");
};
```

```cpp
// OSCDemoActor.cpp
#include "OSCDemoActor.h"
#include "OSCManager.h"
#include "OSCLog.h"

AOSCDemoActor::AOSCDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AOSCDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建 Server：监听本机 9000 端口
    Server = UOSCManager::CreateOSCServer(
        TEXT("0.0.0.0"), ListenPort, false, true,
        TEXT("DemoServer"), GetTransientPackage()
    );

    // 绑定接收事件
    if (Server)
    {
        Server->OnOscMessageReceived.AddDynamic(this, &AOSCDemoActor::OnOscMessageReceived);
        UE_LOG(LogOSC, Log, TEXT("OSC Server listening on port %d"), ListenPort);
    }

    // 创建 Client：向本机 9000 端口发送
    Client = UOSCManager::CreateOSCClient(
        TargetIP, ListenPort, TEXT("DemoClient"), GetTransientPackage()
    );
}

void AOSCDemoActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (Server)
    {
        Server->Stop();
    }
    Super::EndPlay(EndPlayReason);
}

void AOSCDemoActor::OnOscMessageReceived(const FOSCMessage& Message, const FString& IPAddress)
{
    FOSCAddress Address = UOSCManager::GetOSCMessageAddress(Message);
    UE_LOG(LogOSC, Log, TEXT("Received [%s] from %s"),
        *UOSCManager::GetOSCAddressFullPath(Address), *IPAddress);

    // 读取第一个 float 参数
    float FloatValue = 0.f;
    if (UOSCManager::GetFloat(Message, 0, FloatValue))
    {
        UE_LOG(LogOSC, Log, TEXT("  Param[0] float = %f"), FloatValue);
    }
}

void AOSCDemoActor::SendTestMessage(float Value)
{
    if (!Client) return;

    FOSCMessage Message;
    UOSCManager::SetOSCMessageAddress(Message, FOSCAddress(TEXT("/demo/test")));
    UOSCManager::AddFloat(Message, Value);
    UOSCManager::AddString(Message, TEXT("hello"));

    Client->SendOSCMessage(Message);
}
```

## 模块依赖

从源码分析，该插件使用了底层 Socket API（`FSocket`、`FIPv4Endpoint`、`FInternetAddr`）和线程（`FRunnable`）：

| 模块 | 用途 |
|---|---|
| `Sockets` | 底层 Socket 操作，用于 UDP 收发数据 |
| `Networking` | IPv4 端点和网络地址处理 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新 API |
| 2025-10-22 | `bb8c25da` | Fix for `FOSCAddress::PopContainer` to return the popped value, and for `FOSCAddress::PopContainers` | 修复 PopContainer/PopContainers 返回值 |
| 2025-10-07 | `96352708` | Renaming Base<Plugin>.ini to Default<Plugin>.ini | 重命名插件配置文件 |
| 2025-10-01 | `d082c6eb` | Fix OSC::FStream::WriteBlob | 修复 WriteBlob 写入逻辑 |
| 2025-09-12 | `fd5c41be` | Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue f | 修复 nodiscard 返回值忽略警告 |

### 维护评价

**活跃维护中。** 该插件虽然创建于 2019 年（约 6 年前），但在 2025-2026 年持续有实质性更新：包括 bug 修复（PopContainer 返回值、WriteBlob 逻辑）、API 现代化（UE_LOG 迁移）和代码质量改进（nodiscard 警告修复）。5.5 版本还进行了一次重大重构，将内部类型迁移到 `UE::OSC` 命名空间并标记旧 API 为 deprecated，说明 Epic 在积极维护此插件。

**注意事项：**
- `EnabledByDefault=false`，需要在项目设置中手动启用
- 部分旧 API（`FOSCType`、`FOSCStream`、`IOSCPacket`）在 5.5 已标记 deprecated，新代码应使用 `UE::OSC::FOSCData`、`UE::OSC::FStream`、`UE::OSC::IPacket`
- Server 在 5.5 后改为异步任务驱动（不再依赖 GameThread Tick），性能更好

**推荐使用。** 对于需要与外部 OSC 应用通信的项目，这是 Epic 官方维护的完整实现，API 稳定且蓝图友好。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OSC)
- [OSC 协议规范](http://opensoundcontrol.org/)（第三方）