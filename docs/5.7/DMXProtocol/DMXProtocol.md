# DMX Protocol

> DMX Protocols implementation

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DMXProtocol` (Runtime), `DMXProtocolArtNet` (Runtime), `DMXProtocolSACN` (Runtime), `DMXProtocolEditor` (Editor), `DMXProtocolBlueprintGraph` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2019-11-19 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXProtocol) | |

## 用途

DMX Protocol 插件为 Unreal Engine 提供了完整的 DMX（Digital Multiplex）协议通信框架，是虚拟制作（Virtual Production）中灯光控制的核心基础设施。

该插件解决的核心问题：

1. **协议抽象层**：将底层网络协议（Art-Net、sACN/ESTA）的复杂性封装为统一的端口（Port）接口，用户无需关心具体的网络包格式和传输细节
2. **端口管理系统**：通过 `FDMXPortManager` 提供输入端口（Input Port）和输出端口（Output Port）的统一管理，支持在 Project Settings 中配置，运行时动态访问
3. **信号缓冲与分发**：提供线程安全的信号队列机制（`FDMXRawListener`），支持单生产者-单消费者模式，确保高吞吐量的 DMX 数据处理
4. **多协议支持**：通过工厂模式（`IDMXProtocolFactory`）和模块化架构，允许 Art-Net 和 sACN 协议独立实现并注册到统一框架中
5. **蓝图集成**：通过 `UDMXProtocolBlueprintLibrary` 和 `DMXProtocolBlueprintGraph` 模块，让蓝图用户可以发送/接收 DMX 数据、配置端口参数

## 使用场景

- **舞台灯光控制**：你在做虚拟制作或演唱会灯光设计 → 用 DMX Protocol 通过 Art-Net/sACN 控制真实灯光设备
- **LED 墙控制**：你需要向 LED 墙控制器发送 DMX 数据 → 通过 Output Port 发送 DMX 信号
- **灯光预可视化**：你在做灯光 Previs → 用 Input Port 接收来自灯光控制台的 DMX 数据，驱动场景中的虚拟灯光
- **DMX 录制与回放**：你需要录制 DMX 数据用于后期 → 使用 `FDMXRawListener` 捕获所有原始信号
- **自定义协议开发**：你需要实现私有 DMX 协议 → 继承 `IDMXProtocol` 和 `IDMXProtocolFactory` 接口

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Send DMX Enabled` | 全局启用/禁用 DMX 发送 | `UDMXProtocolBlueprintLibrary` |
| `Is Send DMX Enabled` | 查询全局 DMX 发送是否启用 | `UDMXProtocolBlueprintLibrary` |
| `Set Receive DMX Enabled` | 全局启用/禁用 DMX 接收 | `UDMXProtocolBlueprintLibrary` |
| `Is Receive DMX Enabled` | 查询全局 DMX 接收是否启用 | `UDMXProtocolBlueprintLibrary` |
| `Get Local DMX Network Interface Card IPs` | 获取本机所有网络接口卡 IP 地址 | `UDMXProtocolBlueprintLibrary` |
| `Set DMX Input Port Device Address` | 设置输入端口的设备地址（网卡 IP） | `UDMXProtocolBlueprintLibrary` |
| `Set DMX Output Port Device Address` | 设置输出端口的设备地址（网卡 IP） | `UDMXProtocolBlueprintLibrary` |
| `Set DMX Output Port Destination Addresses` | 设置输出端口的目标地址（单播 IP 列表） | `UDMXProtocolBlueprintLibrary` |

### 端口引用类型

蓝图中通过以下结构体引用端口：

| 类型 | 说明 |
|---|---|
| `FDMXInputPortReference` | 输入端口引用，通过 GUID 关联到 Project Settings 中配置的端口 |
| `FDMXOutputPortReference` | 输出端口引用，通过 GUID 关联到 Project Settings 中配置的端口 |

### 使用示例（蓝图描述）

**发送 DMX 数据**：
1. 在 Project Settings → DMX → Communication Settings 中配置 Output Port（选择 Art-Net 或 sACN 协议、设置 IP 地址）
2. 在蓝图中获取 `FDMXOutputPortReference`（通过属性选择器选择已配置的端口）
3. 调用 Output Port 的 `SendDMX` 方法发送信号

**接收 DMX 数据**：
1. 在 Project Settings 中配置 Input Port
2. 在蓝图中获取 `FDMXInputPortReference`
3. 通过 `GameThreadGetDMXSignal` 获取指定 Universe 的最新 DMX 信号
4. 从 `FDMXSignal` 的 `ChannelData` 数组中读取各通道值（0-255）

## C++ 用法

### 头文件引入

```cpp
// 核心框架
#include "DMXProtocolModule.h"
#include "DMXProtocolCommon.h"
#include "DMXProtocolTypes.h"

// 端口管理
#include "IO/DMXPortManager.h"
#include "IO/DMXInputPort.h"
#include "IO/DMXOutputPort.h"
#include "IO/DMXRawListener.h"

// 蓝图库
#include "DMXProtocolBlueprintLibrary.h"

// 工具类
#include "DMXConversions.h"
#include "DMXProtocolUtils.h"
```

### 基本用法：获取端口并发送 DMX

```cpp
// 来源: IO/DMXPortManager.h, IO/DMXOutputPort.h

// 获取端口管理器
FDMXPortManager& PortManager = FDMXPortManager::Get();

// 获取所有输出端口
const TArray<FDMXOutputPortSharedRef>& OutputPorts = PortManager.GetOutputPorts();

if (OutputPorts.Num() > 0)
{
    FDMXOutputPortSharedRef OutputPort = OutputPorts[0];
    
    // 构建通道数据 (512 通道)
    TMap<int32, uint8> ChannelValueMap;
    ChannelValueMap.Add(1, 255);  // 通道 1 设为最大值
    ChannelValueMap.Add(2, 128);  // 通道 2 设为半值
    
    // 发送 DMX 信号到指定 Universe
    OutputPort->SendDMX(ChannelValueMap, 1 /* LocalUniverseID */);
}
```

### 基本用法：接收 DMX 数据

```cpp
// 来源: IO/DMXInputPort.h

FDMXPortManager& PortManager = FDMXPortManager::Get();
const TArray<FDMXInputPortSharedRef>& InputPorts = PortManager.GetInputPorts();

if (InputPorts.Num() > 0)
{
    FDMXInputPortSharedRef InputPort = InputPorts[0];
    
    // 在 Game Thread 获取指定 Universe 的最新信号
    FDMXSignalSharedPtr Signal;
    if (InputPort->GameThreadGetDMXSignal(1 /* LocalUniverseID */, Signal))
    {
        // 读取通道数据
        uint8 Channel1Value = Signal->ChannelData[0];  // 通道 1
        uint8 Channel2Value = Signal->ChannelData[1];  // 通道 2
        
        UE_LOG(LogTemp, Log, TEXT("Universe %d, Channel 1: %d, Channel 2: %d"),
            Signal->ExternUniverseID, Channel1Value, Channel2Value);
    }
}
```

### 进阶用法：使用 RawListener 监听所有 DMX 数据

```cpp
// 来源: IO/DMXRawListener.h, IO/DMXInputPort.h

// 创建 Raw Listener 监听输入端口的所有数据
FDMXInputPortSharedRef InputPort = FDMXPortManager::Get().GetInputPorts()[0];
TSharedRef<FDMXRawListener> RawListener = MakeShared<FDMXRawListener>(InputPort);
RawListener->Start();

// 在任意线程轮询数据
FDMXSignalSharedPtr Signal;
int32 LocalUniverseID;
while (RawListener->DequeueSignal(this /* Consumer */, Signal, LocalUniverseID))
{
    // 处理每一条收到的 DMX 信号
    // Signal->Timestamp       - 收到时间戳
    // Signal->ExternUniverseID - 外部 Universe ID
    // Signal->ChannelData     - 512 通道的原始数据
    // Signal->Priority        - 信号优先级
}

// 不再使用时停止监听
RawListener->Stop();
```

### 进阶用法：DMX 数据格式转换

```cpp
// 来源: DMXConversions.h

// 将归一化值 (0.0-1.0) 转换为字节数组
float NormalizedValue = 0.75f;
TArray<uint8> Bytes = FDMXConversions::NormalizedDMXValueToByteArray(
    NormalizedValue,
    EDMXFixtureSignalFormat::E16Bit,  // 使用 16 位格式
    true  // LSB 优先
);

// 获取信号格式的最大值
uint32 MaxValue = FDMXConversions::GetSignalFormatMaxValue(EDMXFixtureSignalFormat::E8Bit);
// MaxValue == 255

// 按信号格式钳制值
uint32 ClampedValue = FDMXConversions::ClampValueBySignalFormat(300, EDMXFixtureSignalFormat::E8Bit);
// ClampedValue == 255
```

### 进阶用法：全局控制 DMX 发送/接收

```cpp
// 来源: DMXProtocolBlueprintLibrary.h, DMXProtocolSettings.h

// 全局禁用 DMX 发送（不影响编辑器）
UDMXProtocolBlueprintLibrary::SetSendDMXEnabled(false, false);

// 全局禁用 DMX 接收（影响编辑器）
UDMXProtocolBlueprintLibrary::SetReceiveDMXEnabled(false, true);

// 查询状态
bool bSending = UDMXProtocolBlueprintLibrary::IsSendDMXEnabled();
bool bReceiving = UDMXProtocolBlueprintLibrary::IsReceiveDMXEnabled();
```

## Demo 示例

### 最小可编译示例：发送 DMX 到 Art-Net

**MyDMXActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IO/DMXOutputPort.h"
#include "MyDMXActor.generated.h"

UCLASS()
class AMyDMXActor : public AActor
{
    GENERATED_BODY()

public:
    AMyDMXActor();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

private:
    /** 输出端口引用，在 Project Settings 中配置 */
    UPROPERTY(EditAnywhere, Category = "DMX")
    FDMXOutputPortReference OutputPortRef;

    /** 缓存的输出端口实例 */
    FDMXOutputPortSharedPtr CachedOutputPort;

    /** 当前 DMX 值 */
    float CurrentValue = 0.f;
};
```

**MyDMXActor.cpp**
```cpp
#include "MyDMXActor.h"
#include "IO/DMXPortManager.h"

AMyDMXActor::AMyDMXActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyDMXActor::BeginPlay()
{
    Super::BeginPlay();

    // 通过 GUID 查找对应的输出端口实例
    FDMXPortManager& PortManager = FDMXPortManager::Get();
    CachedOutputPort = PortManager.FindOutputPortByGuid(OutputPortRef.GetPortGuid());
}

void AMyDMXActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (!CachedOutputPort.IsValid())
    {
        return;
    }

    // 生成一个呼吸灯效果
    CurrentValue += DeltaTime;
    uint8 DMXValue = static_cast<uint8>((FMath::Sin(CurrentValue * 2.f) * 0.5f + 0.5f) * 255.f);

    // 构建通道数据并发送
    TMap<int32, uint8> ChannelValueMap;
    ChannelValueMap.Add(1, DMXValue);   // 通道 1: 亮度
    ChannelValueMap.Add(2, 255);         // 通道 2: 红色
    ChannelValueMap.Add(3, 0);           // 通道 3: 绿色
    ChannelValueMap.Add(4, 0);           // 通道 4: 蓝色

    CachedOutputPort->SendDMX(ChannelValueMap, 1 /* LocalUniverseID */);
}
```

**Build.cs 依赖**
```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "DMXProtocol"
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DMXProtocol` | 核心框架：端口管理、信号处理、协议抽象接口 |
| `DMXProtocolArtNet` | Art-Net 协议实现（基于 UDP，端口 6454） |
| `DMXProtocolSACN` | sACN (ESTA E1.31) 协议实现（基于 UDP 多播） |
| `DMXProtocolEditor` | 编辑器 UI：端口配置面板、属性自定义 |
| `DMXProtocolBlueprintGraph` | 蓝图节点图支持：自定义蓝图节点 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 近期 | `ed12aec9a262` | DMX: Remove any uses of FORCEINLINE, replace with inline where appropriate | 代码规范化：将 `FORCEINLINE` 替换为 `inline`，避免不必要的内联导致的编译膨胀 |
| 近期 | `66356fe8dea4` | DMX: Improve implementation and robustness of the sACN protocol implementation | 功能改进：增强 sACN 协议实现的健壮性，修复可能的连接/数据传输问题 |
| 近期 | `57c0a8bf5ed2` | [trivial] Removed little-used but heavy header from the Core PCH | 编译优化：从 Core PCH 中移除不常用但体积大的头文件，加快编译速度 |

### 维护评价

**综合评价：活跃维护，推荐使用**

- **创建时间**：2019 年 11 月，已有约 6 年历史，属于成熟插件
- **维护状态**：近期仍有实质性更新（sACN 协议改进、代码规范化），说明 Epic 仍在积极维护
- **架构成熟度**：采用工厂模式 + 模块化设计，协议实现与核心框架解耦，扩展性良好
- **线程安全**：大量使用 `ESPMode::ThreadSafe` 的共享指针、原子变量、SPSC 队列，适合高吞吐量场景
- **已知限制**：
  - DMX 宇宙大小固定为 512 通道（DMX512 标准限制）
  - 最大 Universe ID 为 63999
  - `FDMXRawListener` 在 Game Thread 使用时可能因无限工作负载导致引擎卡顿
- **推荐**：虚拟制作项目的标准选择，API 稳定，文档注释详尽

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXProtocol)
- [官方文档]()（暂无）
- [测试用例]()（待确认）