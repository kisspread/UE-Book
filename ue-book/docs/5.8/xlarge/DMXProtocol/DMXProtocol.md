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
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXProtocol) | |

## 用途
DMXProtocol 插件是 Unreal Engine 虚拟制作管线中控制灯光和设备的核心基础系统。它并非一个简单的网络工具，而是一个完整的工业级 DMX 通信框架。其主要解决的问题包括：
1.  **抽象协议复杂性**：将 Art-Net、sACN 等专业灯光控制协议的底层网络通信、数据包解析、缓冲管理封装成易于使用的高级端口（Input/Output Port）抽象。
2.  **统一项目配置**：在引擎的项目设置中提供全局的 DMX 输入/输出端口定义，管理所有与外部 DMX 网络的通信通道。
3.  **支持设备集成**：为连接舞台灯光、LED 灯具、媒体服务器等各类 DMX 设备提供标准化的控制接口，并支持优先级、环回（Loopback）、发送延迟等高级特性。
4.  **赋能蓝图与 C++**：为设计师（通过蓝图）和程序员（通过 C++）提供清晰、线程安全的 API，用于接收、处理和发送 DMX 信号。

简而言之，它是 UE5 虚拟制片中“灯光控制总线”的底层实现和管理层。

## 使用场景
-   **虚拟制片（Virtual Production）**：在 LED Volume 摄影棚中，通过 DMX 控制现场灯具（如背光、特效灯）与屏幕上的虚拟场景（如日景、夜景）实时同步。
-   **大型演出与活动**：在演唱会、舞台剧中，用 UE5 作为内容生成和控制中心，驱动庞大的 DMX 灯光系统执行复杂的灯光秀。
-   **建筑与展览**：控制动态建筑立面照明或交互式艺术装置的灯光。
-   **设备测试与监控**：在引擎内模拟或监控来自 DMX 控制台的信号，用于设备测试或开发自定义控制界面。

## 蓝图用法

### 核心节点
主要节点集中在 `UDMXProtocolBlueprintLibrary` 中，提供了全局控制和配置功能。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Send DMX Enabled` | 全局启用或禁用 DMX 发送 | `UDMXProtocolBlueprintLibrary` |
| `Is Send DMX Enabled` | 查询全局 DMX 发送状态 | `UDMXProtocolBlueprintLibrary` |
| `Set Receive DMX Enabled` | 全局启用或禁用 DMX 接收 | `UDMXProtocolBlueprintLibrary` |
| `Is Receive DMX Enabled` | 查询全局 DMX 接收状态 | `UDMXProtocolBlueprintLibrary` |
| `Get Local DMX Network Interface Card IPs` | 获取本机可用的网卡 IP 列表 | `UDMXProtocolBlueprintLibrary` |
| `Set DMX Input Port Device Address` | 设置指定输入端口的本机网卡 IP 地址 | `UDMXProtocolBlueprintLibrary` |
| `Set DMX Output Port Device Address` | 设置指定输出端口的本机网卡 IP 地址 | `UDMXProtocolBlueprintLibrary` |
| `Set DMX Output Port Destination Addresses` | 设置指定输出端口的单播目标 IP 地址列表 | `UDMXProtocolBlueprintLibrary` |

### 使用示例
1.  **在关卡蓝图中，当玩家按下按键时，向指定的输出端口发送 DMX 信号**：
    *   首先，你需要通过 `FDMXPortManager` 获取或缓存一个 `FDMXOutputPort` 的引用（C++ 侧完成）。
    *   在蓝图中，调用该输出端口引用的 `Send DMX` 节点，传入要控制的**本地 Universe ID** 和一个包含**通道号到数值**映射的 `TMap<int32, uint8>`。
    *   例如，设置本地 Universe 1 的通道 1 为 255，即可点亮相应灯具。

2.  **创建一个监听特定输入端口的 Actor**：
    *   在 Actor 的事件图表中，使用 `FDMXRawListener` 的 C++ 封装或对应的蓝图接口（如果有）。
    *   在 `BeginPlay` 中，将监听器绑定到通过 `FDMXPortManager` 获取的特定 `FDMXInputPort`。
    *   在 `Tick` 事件或定时器中，从监听器中 `Dequeue Signal` 来获取最新的 DMX 数据，并处理 `ChannelData` 数组。

## C++ 用法

### 头文件引入
```cpp
// 核心管理
#include "IO/DMXPortManager.h"
// 协议模块
#include "DMXProtocolModule.h"
// 输入输出端口
#include "IO/DMXInputPort.h"
#include "IO/DMXOutputPort.h"
// 蓝图库
#include "DMXProtocolBlueprintLibrary.h"
// 监听器
#include "IO/DMXRawListener.h"
// 协议接口
#include "Interfaces/IDMXProtocol.h"
```

### 基本用法
**获取端口并发送 DMX**
```cpp
// 获取端口管理器
FDMXPortManager& PortManager = FDMXPortManager::Get();

// 假设项目设置中已配置好输出端口，通过索引或配置获取
const TArray<FDMXOutputPortSharedRef>& OutputPorts = PortManager.GetOutputPorts();
if (OutputPorts.Num() > 0)
{
    FDMXOutputPortSharedRef MyOutputPort = OutputPorts[0];

    // 准备要发送的通道数据
    TMap<int32, uint8> ChannelData;
    ChannelData.Add(1, 255); // 通道1，全亮
    ChannelData.Add(2, 128); // 通道2，半亮

    // 发送到本地 Universe 1
    MyOutputPort->SendDMX(1, ChannelData);
}
```
*(基于 `DMXPortManager.h` 和 `DMXOutputPort.h` 的标准用法)*

**接收 DMX 数据**
```cpp
// 在你的类中持有监听器指针
TSharedPtr<FDMXRawListener> MyRawListener;

void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    // 获取输入端口
    FDMXPortManager& PortManager = FDMXPortManager::Get();
    const TArray<FDMXInputPortSharedRef>& InputPorts = PortManager.GetInputPorts();
    if (InputPorts.Num() > 0)
    {
        // 为第一个输入端口创建原始监听器
        MyRawListener = MakeShared<FDMXRawListener>(InputPorts[0]);
        MyRawListener->Start();
    }
}

void AMyActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (MyRawListener.IsValid())
    {
        FDMXSignalSharedPtr ReceivedSignal;
        int32 LocalUniverse;
        // 尝试出队一个信号
        while (MyRawListener->DequeueSignal(this, ReceivedSignal, LocalUniverse))
        {
            // 处理信号
            const TArray<uint8>& ChannelData = ReceivedSignal->ChannelData;
            uint8 Channel1Value = (ChannelData.Num() > 0) ? ChannelData[0] : 0;
            // ... 应用灯光效果
        }
    }
}

void AMyActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MyRawListener.IsValid())
    {
        MyRawListener->Stop();
        MyRawListener.Reset();
    }
    Super::EndPlay(EndPlayReason);
}
```
*(基于 `DMXRawListener.h` 和 `DMXSignal` 结构体)*

### 进阶用法
**通过协议接口直接注册端口（用于协议开发或深度定制）**
```cpp
// 获取 sACN 协议实例
IDMXProtocolPtr SacnProtocol = IDMXProtocol::Get(FDMXProtocolModule::DefaultProtocolSACNName);
if (SacnProtocol.IsValid())
{
    // 创建一个输出端口配置
    FGuid MyPortGuid = FGuid::NewGuid();
    FDMXOutputPortConfig OutputPortConfig(MyPortGuid);
    OutputPortConfig.MakeValid(); // 填充默认值

    // 通过端口管理器创建端口（通常这是推荐方式）
    // 但这里展示协议如何接收注册：
    // TArray<TSharedPtr<IDMXSender>> Senders = SacnProtocol->RegisterOutputPort(MyOutputPort);
}
```
*(基于 `IDMXProtocol.h` 接口)*

## Demo 示例
一个简单的 Actor 组件，监听指定的 DMX 输入端口，并根据通道 1 的值旋转自身。
```cpp
// MyDMXReceiverComponent.h
#pragma once
#include "Components/ActorComponent.h"
#include "MyDMXReceiverComponent.generated.h"

class FDMXRawListener;
class FDMXInputPort;

UCLASS(ClassGroup=(DMX), meta=(BlueprintSpawnableComponent))
class UMyDMXReceiverComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyDMXReceiverComponent();
    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    TSharedPtr<FDMXRawListener> RawListener;
    TSharedPtr<FDMXInputPort> InputPort;
};
```

```cpp
// MyDMXReceiverComponent.cpp
#include "MyDMXReceiverComponent.h"
#include "IO/DMXPortManager.h"
#include "IO/DMXRawListener.h"
#include "IO/DMXInputPort.h"

UMyDMXReceiverComponent::UMyDMXReceiverComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
}

void UMyDMXReceiverComponent::BeginPlay()
{
    Super::BeginPlay();

    FDMXPortManager& PortManager = FDMXPortManager::Get();
    const TArray<FDMXInputPortSharedRef>& InputPorts = PortManager.GetInputPorts();

    // 监听第一个可用的输入端口
    if (InputPorts.Num() > 0)
    {
        InputPort = InputPorts[0];
        RawListener = MakeShared<FDMXRawListener>(InputPort.ToSharedRef());
        RawListener->Start();
    }
}

void UMyDMXReceiverComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    if (RawListener.IsValid() && GetOwner())
    {
        FDMXSignalSharedPtr Signal;
        int32 UniverseID;
        while (RawListener->DequeueSignal(this, Signal, UniverseID))
        {
            if (Signal->ChannelData.Num() > 0)
            {
                // 根据通道 1 的值 (0-255) 计算旋转角 (0-360度)
                float Value = Signal->ChannelData[0] / 255.0f;
                FRotator NewRotation(0.0f, Value * 360.0f, 0.0f);
                GetOwner()->SetActorRotation(NewRotation);
            }
        }
    }
}

void UMyDMXReceiverComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (RawListener.IsValid())
    {
        RawListener->Stop();
        RawListener.Reset();
    }
    InputPort.Reset();
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖
要使用 DMXProtocol 插件的功能（如 `FDMXPortManager`），你的模块需要在 `Build.cs` 中添加依赖。
主要的、非通用的依赖是 `DMXProtocolCore`，它包含了所有 IO 和核心逻辑。
```csharp
// YourModule.Build.cs
PublicDependencyModuleNames.AddRange(new string[] { ... "DMXProtocolCore" ... });
```
*(常见依赖如 Core, CoreUObject, Engine 等已省略)*

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏迁移到新的 UE_LOGF，统一日志格式。 |
| 2026-04-08 | `86879cf0` | Fix unreachable code warnings | 修复不可达代码的编译警告，提高代码质量。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修正之前一次查找替换操作带来的错误。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回滚了某个具体的改动集（CL51314860）。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复因委托初始化顺序导致注册缺失的严重问题，影响插件启动。 |

### 维护评价
DMX Protocol 插件是虚拟制作管线的基石组件，**处于活跃维护状态**。从提交记录可见，Epic Games 工程团队持续对其进行维护和优化，包括：
-   **稳定性修复**：解决关键的初始化顺序问题（如 `OnPostEngineInit`）和编译警告。
-   **代码现代化**：迁移日志宏，遵循最新的引擎编码规范。
-   **积极的故障响应**：针对引入问题的提交能够快速回滚（如 `CL51314860`）。

**结论**：该插件代码成熟，功能完善，且有官方持续支持。对于任何涉及专业 DMX 设备集成的 UE5 项目（尤其是虚拟制片），它都是**强烈推荐使用**且**值得信赖**的核心基础设施。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXProtocol)