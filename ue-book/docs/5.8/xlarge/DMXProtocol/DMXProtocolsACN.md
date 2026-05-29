# DMX Protocol

> DMX Protocols implementation（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | DMX 协议 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DMXProtocol` (Runtime), `DMXProtocolArtNet` (Runtime), `DMXProtocolSACN` (Runtime), `DMXProtocolEditor` (Editor), `DMXProtocolBlueprintGraph` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXProtocol) | |

## 用途

DMX Protocol 插件为 Unreal Engine 提供了完整的 DMX 协议支持框架，是 Virtual Production（虚拟制作）中控制灯光设备的核心基础设施。它实现了工业标准的 Art-Net 和 sACN (E1.31) 两种主流 DMX over IP 协议，并提供统一的抽象层。

该插件解决的问题是：让 Unreal Engine 能够与现实世界中的 DMX 灯光设备进行通信。在影视虚拟制片、演唱会灯光设计、主题公园互动体验等场景中，需要精确同步数字世界与物理灯光。此插件通过标准化协议实现这一目标，支持单播 (Unicast) 和组播 (Multicast) 等多种网络通信模式。

## 使用场景

- **虚拟制片**：在 LED Volume 摄影棚中，将 Unreal Engine 中的虚拟灯光与真实的 LED 墙体灯光进行同步。
- **舞台灯光控制**：通过 Unreal Engine 设计并实时控制演唱会、剧院、主题公园的灯光效果。
- **互动装置**：创建与访客互动的灯光艺术装置。
- **大型活动**：需要统一控制数百甚至上千个 DMX 宇宙的大型活动。

## 蓝图用法

该插件主要提供运行时协议引擎，蓝图可访问的功能通常通过上层插件（如 DMX Engine）提供。在本插件层面，可通过控制台命令进行调试。

### 核心节点

该插件自身不直接暴露蓝图节点。其蓝图交互能力主要通过其上层模块 `DMXProtocolBlueprintGraph` 提供，该模块包含蓝图函数库和自定义 K2 节点。

### 使用示例（蓝图描述）

通常，用户在上层插件中通过 `DMX Input Port` 和 `DMX Output Port` 蓝图组件来接收和发送 DMX 数据。本插件在底层负责解析和封装 Art-Net/sACN 数据包。

**调试用法（控制台命令）**：
1. **发送测试 DMX**：在控制台输入 `DMX.SACN.SendDMX 7 25:156 26:0 27:10`，将向第 7 号宇宙的 25、26、27 通道发送指定值。
2. **重置宇宙**：在控制台输入 `DMX.SACN.ResetDMXSend 7`，重置第 7 号宇宙的发送状态。

## C++ 用法

### 头文件引入

```cpp
#include "DMXProtocolSACNModule.h"
#include "DMXProtocolSACN.h"
```

### 基本用法

该插件主要作为底层引擎运行，C++ 用法通常涉及协议注册和端口管理。核心类为 `FDMXProtocolSACN`。

**创建并获取 sACN 协议实例**（来源：`DMXProtocolSACNModule.h`）：
```cpp
// 通常在模块启动时自动注册，可通过名称获取协议指针
IDMXProtocolPtr SACNProtocol = IDMXProtocol::GetProtocol(FName("SACN"));
if (SACNProtocol.IsValid())
{
    // 可以检查协议状态
    bool bIsEnabled = SACNProtocol->IsEnabled();
    int32 MinUniverse = SACNProtocol->GetMinUniverseID(); // 通常为 1
    int32 MaxUniverse = SACNProtocol->GetMaxUniverseID(); // 通常为 63999
}
```

**管理输出端口**（来源：`DMXProtocolSACN.h`）：
```cpp
// 假设已有一个输出端口共享指针 TSharedRef<FDMXOutputPort> MyOutputPort
TArray<TSharedPtr<IDMXSender>> Senders = SACNProtocol->RegisterOutputPort(MyOutputPort);
// 每个 Sender 对应一个网络接口和目的地，用于实际发送数据
```

### 进阶用法

**直接管理 Sender 和 Receiver**（用于自定义网络配置）：
```cpp
// 创建单播发送器（来源：DMXProtocolSACNSender.h）
FString NetworkInterfaceIP = TEXT("192.168.1.100");
FString UnicastDestIP = TEXT("192.168.1.200");
TSharedPtr<FDMXProtocolSACNSender> Sender = FDMXProtocolSACNSender::TryCreateUnicastSender(
    SACNProtocolShared, NetworkInterfaceIP, UnicastDestIP);

if (Sender.IsValid())
{
    // 绑定输出端口到此发送器
    Sender->AssignOutputPort(MyOutputPort);
    
    // 手动构建并发送信号（通常由端口自动处理）
    // FDMXSignalSharedRef Signal = ...;
    // Sender->SendDMXSignal(Signal);
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何检查 sACN 协议并获取其参数。

**MyDMXComponent.h**
```cpp
// MyDMXComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "DMXProtocolSACNModule.h" // 引入 sACN 模块头文件
#include "MyDMXComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyDMXComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

private:
    void CheckSACNProtocol();
};
```

**MyDMXComponent.cpp**
```cpp
// MyDMXComponent.cpp
#include "MyDMXComponent.h"
#include "DMXProtocol.h" // 核心协议接口
#include "DMXProtocolSACN.h" // sACN 协议实现

void UMyDMXComponent::BeginPlay()
{
    Super::BeginPlay();
    CheckSACNProtocol();
}

void UMyDMXComponent::CheckSACNProtocol()
{
    // 通过模块单例获取协议管理器
    FDMXProtocolSACNModule& SACNModule = FDMXProtocolSACNModule::Get();
    
    // 获取已注册的 sACN 协议实例
    IDMXProtocolPtr Protocol = IDMXProtocol::GetProtocol(FName("SACN"));
    
    if (Protocol.IsValid() && Protocol->IsEnabled())
    {
        UE_LOG(LogTemp, Log, TEXT("sACN Protocol is active."));
        UE_LOG(LogTemp, Log, TEXT("Supported Universe Range: %d - %d"),
            Protocol->GetMinUniverseID(),
            Protocol->GetMaxUniverseID());
            
        // 检查支持的通信类型
        const TArray<EDMXCommunicationType> InputTypes = Protocol->GetInputPortCommunicationTypes();
        for (EDMXCommunicationType Type : InputTypes)
        {
            // 输出通信类型，例如 Broadcast, Multicast, Unicast
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("sACN Protocol is not available or disabled."));
    }
}
```

## 模块依赖

从各模块的 `Build.cs` 分析，使用者通常需要依赖以下模块。

| 模块 | 用途 |
|---|---|
| `DMXProtocol` | 核心 DMX 协议抽象层，提供 `IDMXProtocol` 等核心接口 |
| `DMXProtocolSACN` | sACN (E1.31) 协议的具体实现 |
| `DMXProtocolArtNet` | Art-Net 协议的具体实现 |
| `Networking` | 提供网络套接字 (`FSocket`) 支持 |
| `Sockets` | 依赖于 `Networking`，提供底层网络功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移到新的 `UE_LOGF` 格式 |
| 2026-04-08 | `86879cf0` | Fix unreachable code warnings | 修复代码中“不可达代码”的编译器警告 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了上一次错误查找替换后的第二次修正 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回滚了 CL51314860 的修改 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复因委托初始化顺序导致的注册失败问题 |

### 维护评价

**维护状态：活跃维护中**

- **创建时间**：插件于 2020 年创建，已有约 6 年历史，属于成熟插件。
- **近期活跃度**：从 Git 历史看，2026 年仍有频繁更新，且最近一次更新距今（2026年4月）不足一个月，表明仍在积极维护。更新内容主要是代码质量改进（日志迁移、警告修复）和稳定性修复（委托初始化），而非新功能，说明插件已进入稳定期。
- **已知限制**：sACN 协议支持的宇宙数量为 1-63999，符合 E1.31 标准。需要注意网络配置（如多播 TTL）对性能的影响。
- **推荐度**：**强烈推荐**。作为 Epic 官方维护的 Virtual Production 核心组件，其稳定性、性能和标准兼容性都经过了大规模项目验证。对于需要 DMX 集成的项目，这是首选方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXProtocol)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/dmx-in-unreal-engine/) (Unreal Engine DMX 综合文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXProtocol/Tests)