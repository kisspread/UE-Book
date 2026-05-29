# DMX Protocol

> DMX Protocols implementation

| 属性 | 值 |
|---|---|
| 中文名 | DMX 协议 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DMXProtocol` (Runtime), `DMXProtocolArtNet` (Runtime), `DMXProtocolSACN` (Runtime), `DMXProtocolEditor` (Editor), `DMXProtocolBlueprintGraph` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXProtocol) | |

## 用途

DMX Protocol 是 Unreal Engine 虚拟制片管线中的**网络灯光控制协议框架**。它实现了行业标准的 DMX512 灯光控制协议的以太网传输，包括 **Art-Net** 和 **sACN (Streaming ACN)** 两种主流协议。

该插件解决了以下核心问题：

- **网络灯光控制**：通过以太网将 DMX512 数据发送到灯光设备，实现舞台、演播室等场景的灯光远程控制
- **多协议支持**：提供统一的协议接口层（`IDMXProtocol`），下层支持 Art-Net 和 sACN 两种协议实现
- **输入/输出端口抽象**：通过 `FDMXInputPort` 和 `FDMXOutputPort` 抽象网络接口，支持单播（Unicast）和广播（Broadcast）两种通信模式
- **RDM 支持**：Art-Net 实现中包含 RDM（Remote Device Management）相关的数据包结构，支持设备发现和管理
- **虚拟制片集成**：在虚拟制片流程中，DMX 数据可用于驱动舞台灯光与 Unreal Engine 中的虚拟场景同步

## 使用场景

- 你正在搭建一个虚拟制片（Virtual Production）演播室，需要通过 Art-Net 或 sACN 协议控制实体灯光设备
- 你需要在 Unreal Engine 中模拟和控制舞台灯光，与真实的 DMX 控制台或灯光设备进行网络通信
- 你在做一个实时演出的灯光控制程序，需要通过网络发送 DMX 信号到灯光控制器
- 你需要通过 RDM 协议发现和管理网络上的灯光设备
- 你需要在蓝图中快速发送 DMX 信号来调试灯光设备

## 蓝图用法

该插件主要通过 `DMXProtocolBlueprintGraph` 模块提供蓝图集成能力。根据源码分析，核心蓝图接口通过输入/输出端口抽象实现。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SendDMXSignal` | 通过已注册的输出端口发送 DMX 信号 | `FDMXProtocolArtNetSender` |
| `RegisterInputPort` | 注册一个 DMX 输入端口以接收数据 | `FDMXProtocolArtNet` |
| `RegisterOutputPort` | 注册一个 DMX 输出端口以发送数据 | `FDMXProtocolArtNet` |
| `UnregisterInputPort` | 取消注册输入端口 | `FDMXProtocolArtNet` |
| `UnregisterOutputPort` | 取消注册输出端口 | `FDMXProtocolArtNet` |

### 使用示例（蓝图描述）

**发送 DMX 数据**：
1. 通过 `RegisterOutputPort` 节点注册一个输出端口，指定网络接口 IP 和目标地址
2. 创建一个 `FDMXSignal` 数据结构，设置目标 Universe ID 和通道值
3. 调用 `SendDMXSignal` 节点将信号发送到已注册的输出端口

**接收 DMX 数据**：
1. 通过 `RegisterInputPort` 节点注册一个输入端口，指定监听的网络接口
2. 接收器会在后台线程持续监听网络数据
3. 当收到匹配 Universe 的 DMX 数据时，会自动分发到已绑定的输入端口

### 控制台调试命令

插件还注册了控制台命令，可在开发时直接在控制台调试：

```
DMX.ArtNet.SendDMX 17 10:6 11:7 12:8 13:9
```
- 向 Universe 17 发送 DMX 数据
- 设置通道 10=6, 11=7, 12=8, 13=9
- Universe 范围：0-32767，通道范围：0-511，值范围：0-255

```
DMX.ArtNet.ResetDMXSend 7
```
- 重置 Universe 7 的 DMX 发送状态

## C++ 用法

### 头文件引入

```cpp
#include "DMXProtocol.h"
#include "DMXProtocolArtNet.h"
#include "Interfaces/IDMXProtocol.h"
```

### 基本用法

从 `FDMXProtocolArtNetReceiver` 的接口提取的接收器使用模式：

```cpp
// 创建 Art-Net 接收器
TSharedPtr<FDMXProtocolArtNet> ArtNetProtocol = /* 获取协议实例 */;
TSharedPtr<FDMXProtocolArtNetReceiver> Receiver = 
    FDMXProtocolArtNetReceiver::TryCreate(ArtNetProtocol, TEXT("192.168.1.100"));

// 绑定输入端口到接收器
TSharedPtr<FDMXInputPort> InputPort = /* 创建输入端口 */;
Receiver->AssignInputPort(InputPort);

// 检查接收器是否包含指定输入端口
if (Receiver->ContainsInputPort(InputPort))
{
    int32 NumPorts = Receiver->GetNumAssignedInputPorts();
    UE_LOG(LogDMXProtocol, Log, TEXT("Receiver has %d assigned input ports"), NumPorts);
}
```

### 进阶用法

同时管理多个输入端口和发送器的完整模式：

```cpp
// 创建协议实例
FDMXProtocolArtNet ArtNetProtocol(FName("Art-Net"));
ArtNetProtocol.Init();

// 注册输入端口（接收 DMX 数据）
FDMXInputPortSharedRef InputPort = /* 创建输入端口 */;
ArtNetProtocol.RegisterInputPort(InputPort);

// 注册输出端口（发送 DMX 数据），返回发送器列表
FDMXOutputPortSharedRef OutputPort = /* 创建输出端口 */;
TArray<TSharedPtr<IDMXSender>> Senders = ArtNetProtocol.RegisterOutputPort(OutputPort);

// 通过发送器发送 DMX 信号
for (auto& Sender : Senders)
{
    FDMXSignalSharedRef Signal = /* 创建 DMX 信号 */;
    Sender->SendDMXSignal(Signal);
}

// 检查通信类型支持
TArray<EDMXCommunicationType> InputTypes = ArtNetProtocol.GetInputPortCommunicationTypes();
TArray<EDMXCommunicationType> OutputTypes = ArtNetProtocol.GetOutputPortCommunicationTypes();

// 验证 Universe ID
int32 UniverseID = 16;
if (ArtNetProtocol.IsValidUniverseID(UniverseID))
{
    // Universe ID 有效（范围：0-32767）
}

// 清理
ArtNetProtocol.UnregisterInputPort(InputPort);
ArtNetProtocol.UnregisterOutputPort(OutputPort);
ArtNetProtocol.Shutdown();
```

## Demo 示例

### ArtNet 发送器的完整最小示例

```cpp
// DMXSenderExample.h
#pragma once

#include "CoreMinimal.h"
#include "Interfaces/IDMXProtocol.h"
#include "DMXProtocolArtNet.h"

class FDMXSenderExample
{
public:
    /** 初始化 Art-Net 协议并发送 DMX 数据 */
    void InitializeAndSend();

private:
    /** Art-Net 协议实例 */
    TSharedPtr<FDMXProtocolArtNet, ESPMode::ThreadSafe> ArtNetProtocol;

    /** DMX 输出端口 */
    FDMXOutputPortSharedRef* OutputPort = nullptr;
};
```

```cpp
// DMXSenderExample.cpp
#include "DMXSenderExample.h"
#include "DMXProtocolModule.h"
#include "Interfaces/IDMXSender.h"

void FDMXSenderExample::InitializeAndSend()
{
    // 1. 创建 Art-Net 协议实例
    ArtNetProtocol = MakeShared<FDMXProtocolArtNet, ESPMode::ThreadSafe>(FName("Art-Net"));
    
    if (!ArtNetProtocol->Init())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize Art-Net protocol"));
        return;
    }

    // 2. 检查协议是否启用
    if (!ArtNetProtocol->IsEnabled())
    {
        UE_LOG(LogTemp, Warning, TEXT("Art-Net protocol is not enabled"));
        return;
    }

    // 3. 验证 Universe ID
    int32 TargetUniverse = 1;
    if (!ArtNetProtocol->IsValidUniverseID(TargetUniverse))
    {
        TargetUniverse = ArtNetProtocol->MakeValidUniverseID(TargetUniverse);
        UE_LOG(LogTemp, Warning, TEXT("Adjusted Universe ID to: %d"), TargetUniverse);
    }

    // 4. 注册输出端口并获取发送器
    // FDMXOutputPortSharedRef OutputPortRef = /* 根据项目代码创建输出端口 */;
    // TArray<TSharedPtr<IDMXSender>> Senders = ArtNetProtocol->RegisterOutputPort(OutputPortRef);

    // 5. 发送 DMX 数据
    // for (auto& Sender : Senders)
    // {
    //     FDMXSignalSharedRef Signal = /* 创建 DMX 信号数据 */;
    //     Sender->SendDMXSignal(Signal);
    // }

    // 6. 关闭时清理
    // ArtNetProtocol->UnregisterOutputPort(OutputPortRef);
    // ArtNetProtocol->Shutdown();
}
```

## 模块依赖

从各模块的 Build.cs 分析，该插件的特殊依赖如下：

| 模块 | 用途 |
|---|---|
| `DMXProtocol` | 核心协议框架，Art-Net 和 sACN 模块都依赖此模块 |
| `Networking` | 网络套接字通信，用于 UDP 数据包收发 |
| `Sockets` | 底层套接字 API，Art-Net 使用端口 6454/3330 |
| `DMXProtocolRuntime` | DMX 运行时数据结构（输入/输出端口、信号等） |
| `DMXProtocolEditor` | 编辑器 UI 和属性自定义 |
| `UnrealEd` | 编辑器扩展支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新的 UE_LOGF 格式 |
| 2026-04-08 | `86879cf0` | Fix unreachable code warnings | 修复不可达代码的编译警告 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复之前的错误查找替换操作 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退之前的提交 CL51314860 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复委托注册问题，迁移到新的 API 调用方式 |

### 维护评价

**活跃维护** - 该插件仍在积极维护中。

- **创建时间**：2020 年 9 月，是 UE5 早期引入的虚拟制片核心模块
- **近期更新**：2026 年有多次实质性更新，包括代码质量修复（编译警告）、API 迁移（日志宏、委托 API）等
- **维护状态**：作为虚拟制片管线的基础组件，Epic Games 持续维护该模块以保持与 UE5 引擎更新的兼容性
- **已知限制**：需要 `EnabledByDefault=false`，需手动在插件设置中启用
- **推荐使用**：✅ 如果你在进行虚拟制片相关的灯光控制开发，这是官方推荐的 DMX 协议实现，可以放心使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXProtocol)
- [Art-Net 协议官方规范](https://art-net.org.uk/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXProtocol/Tests)