# DMX Engine

> Functionality and assets for communication with DigitalMultiplexer (DMX) enabled devices

| 属性 | 值 |
|---|---|
| 中文名 | DMX 引擎 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DMXBlueprintGraph` (UncookedOnly), `DMXEditor` (Runtime), `DMXRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约5年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXEngine) | |

## 用途

DMXEngine 是一个为虚幻引擎提供 DMX (Digital Multiplex) 协议完整支持的插件。DMX 是娱乐行业控制灯光、LED 像素条、特效设备等的行业标准协议。该插件解决了在虚拟制片、现场演出、建筑可视化等场景中，虚幻引擎需要与真实的 DMX 设备进行实时、同步通信的核心问题。它允许用户在引擎内直接接收 DMX 信号来控制虚拟对象，或发送 DMX 信号来驱动真实的灯光和设备，从而实现虚拟场景与物理世界的精准联动。

## 使用场景

- **XR 虚拟制片**：在 LED 虚拟影棚中，使用 DMX 协议控制摄像机跟踪系统、灯光和道具，确保虚拟背景与实拍元素完全同步。
- **实时灯光控制**：在引擎内设计复杂的灯光秀，并通过 DMX 输出直接控制舞台或演唱会的成百上千盏灯光。
- **互动装置艺术**：创建对观众动作或音频输入做出反应的灯光/视觉装置，将引擎作为中央处理大脑。
- **建筑与室内可视化**：使用 DMX 协议驱动大型 LED 像素墙，以高保真方式展示设计方案的最终效果。
- **主题公园与展览**：开发控制游乐设施、特效和互动展品的应用程序。

## 蓝图用法

该插件为蓝图提供了强大的 DMX 交互能力，主要通过 `DMXRuntime` 模块暴露功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create DMX Interface` | 创建一个 DMX 接口对象，用于连接和通信 | `UDMXSubsystem` |
| `Send DMX` | 通过指定的接口发送一帧 DMX 数据 | `UDMXSubsystem` |
| `Receive DMX` | 通过指定的接口接收一帧 DMX 数据 | `UDMXSubsystem` |
| `Get Fixture Patch` | 根据名称获取一个灯具预设，用于解析 DMX 通道 | `UDMXSubsystem` |

### 使用示例（蓝图描述）

在蓝图中，首先使用 `Create DMX Interface` 节点并配置协议（如 Art-Net）和 IP 地址来初始化通信。然后，可以通过 `Receive DMX` 节点的回调事件持续监听来自物理调光台的信号，并将接收到的通道值映射到场景中的灯光强度或颜色属性上。反之，也可以在游戏逻辑中通过 `Send DMX` 节点，将引擎内的事件（如角色位置、粒子效果）转换为 DMX 数据发送出去，驱动外部设备。

## C++ 用法

C++ 侧的使用主要涉及 `DMXRuntime` 模块的类，用于程序化地控制 DMX 通信和处理数据。

### 头文件引入

```cpp
#include "DMXSubsystem.h"
#include "DMXProtocolModule.h"
```

### 基本用法

获取 DMX 子系统实例，并创建一个接口用于发送数据。

```cpp
// 在您的游戏模块或 Actor 中
UDMXSubsystem* DMXSubsystem = UDMXSubsystem::GetDMXSubsystem();
if (DMXSubsystem)
{
    // 创建或获取一个已有的接口配置
    FDMXInterfaceConfig InterfaceConfig;
    InterfaceConfig.ProtocolName = NAME_ArtNet;
    InterfaceConfig.IPAddress = TEXT("192.168.1.100");
    
    UDMXInterface* DMXInterface = DMXSubsystem->CreateInterface(InterfaceConfig);
    
    // 准备一帧 DMX 数据 (512 字节)
    TArray<uint8> DMXData;
    DMXData.SetNum(512);
    DMXData[0] = 255; // 第一个通道设为最大值
    
    // 发送数据
    if (DMXInterface)
    {
        DMXInterface->SendDMX(DMXData);
    }
}
```

### 进阶用法

结合 `DMXFixturePatch` 解析复杂的灯具数据，并监听信号变化。

```cpp
// 定义一个用于监听 DMX 数据变化的委托
FDMXDataReceivedDelegate DataReceivedDelegate;
DataReceivedDelegate.BindUObject(this, &AMyActor::OnDMXDataReceived);

// 绑定到特定接口
if (DMXInterface)
{
    DMXInterface->OnDataReceived.Add(DataReceivedDelegate);
}

// 处理函数示例
void AMyActor::OnDMXDataReceived(const FDMXDataBuffer& Data)
{
    // 获取一个预定义的灯具预设，它描述了通道到属性的映射
    UDMXFixturePatch* FixturePatch = DMXSubsystem->GetFixturePatch(TEXT("MyMovingHead"));
    if (FixturePatch)
    {
        // 使用预设解析数据
        FDMXChannelData ChannelData = FixturePatch->GetAbsoluteChannelData(Data);
        float Pan = ChannelData.GetValueOfChannel(0) / 255.0f;
        float Tilt = ChannelData.GetValueOfChannel(1) / 255.0f;
        
        // 应用到虚拟灯具上
        MyLightActor->SetPanAndTilt(Pan, Tilt);
    }
}
```

## Demo 示例

一个可编译的最小示例，展示如何创建一个 Actor 来持续监听并响应特定的 DMX 通道变化。

**MyDMXListenerActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "DMXSubsystem.h"
#include "MyDMXListenerActor.generated.h"

UCLASS()
class AMyDMXListenerActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMyDMXListenerActor();
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UFUNCTION()
    void OnDMXDataReceived(const FDMXDataBuffer& Data);

    UPROPERTY()
    UDMXInterface* DMXInterface;
};
```

**MyDMXListenerActor.cpp**
```cpp
#include "MyDMXListenerActor.h"

AMyDMXListenerActor::AMyDMXListenerActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyDMXListenerActor::BeginPlay()
{
    Super::BeginPlay();
    
    UDMXSubsystem* DMXSubsystem = UDMXSubsystem::GetDMXSubsystem();
    if (DMXSubsystem)
    {
        // 创建监听接口 (假设接收来自 IP 192.168.1.50 的 Art-Net 数据)
        FDMXInterfaceConfig Config;
        Config.ProtocolName = NAME_ArtNet;
        Config.IPAddress = TEXT("0.0.0.0"); // 监听所有地址
        
        DMXInterface = DMXSubsystem->CreateInterface(Config);
        
        if (DMXInterface)
        {
            DMXInterface->OnDataReceived.AddDynamic(this, &AMyDMXListenerActor::OnDMXDataReceived);
        }
    }
}

void AMyDMXListenerActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (DMXInterface)
    {
        DMXInterface->OnDataReceived.RemoveDynamic(this, &AMyDMXListenerActor::OnDMXDataReceived);
    }
    Super::EndPlay(EndPlayReason);
}

void AMyDMXListenerActor::OnDMXDataReceived(const FDMXDataBuffer& Data)
{
    // 简单示例：将第一个 DMX 通道的值打印到日志
    if (Data.Num() > 0)
    {
        UE_LOG(LogTemp, Log, TEXT("Received DMX Channel 1 Value: %d"), Data[0]);
    }
}
```

## 模块依赖

该插件依赖于虚幻引擎的核心系统以及虚拟制片相关的特定模块。

| 模块 | 用途 |
|---|---|
| `DMXProtocol` | 提供底层 DMX 协议（如 Art-Net, sACN）的实现框架 |
| `CommonUI` | 编辑器中使用的通用 UI 组件 |
| `MediaAssets` | 可能用于集成视频媒体流的同步功能 |
| `AudioMixer` | 可能用于音频信号同步或分析 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `96d3b290` | DMX - Fix a crash when trying to edit a sequence with a fixture patch that no longer contains a mode | 修复了编辑包含已删除模式的灯具预设的序列时发生的编辑器崩溃问题 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the ... | 将多个虚拟制片资产（可能包括DMX相关资产）迁移至新的资产分类目录 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将插件中的旧版 `UE_LOG` 宏迁移至新版的 `UE_LOGF` 宏 |
| 2026-03-10 | `a69ab07d` | [IsSavingPackage] | 可能涉及修改与资产保存（Package Saving）流程相关的逻辑或接口 |
| 2026-03-05 | `a3b601d8` | Remove includes guarded by `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_5`. Delete header files that now | 清理了在 UE 5.5 中已废弃的头文件包含路径，并删除了相关的旧头文件 |

### 维护评价

DMXEngine 是一个创建于 **2020 年**、拥有约 **5 年历史** 的成熟插件。尽管不是引擎的核心模块，但它**维护状态非常活跃**。从近期提交记录可见，**在 2026 年仍有持续的实质性更新**，包括重要的 Bug 修复（解决编辑器崩溃）、架构适配（新日志宏、资产分类调整）和代码现代化清理（移除废弃包含）。没有任何迹象表明该插件被废弃。

**结论**：强烈推荐在涉及 DMX 控制的虚幻引擎项目中使用此插件。它由 Epic Games 官方维护，功能完整，且更新及时，能够跟上引擎版本的迭代。对于需要与物理灯光设备交互的虚拟制片、现场活动和装置艺术项目，它是不可或缺的工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXEngine)
- [官方文档](https://docs.unrealengine.com/en-US/ProductionPipelines/VirtualProduction/DMX/) (虚幻引擎虚拟制片文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/DMX) (引擎通用测试目录)