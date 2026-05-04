# DMX Protocol

> DMX Protocols implementation（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DMXProtocol` (Runtime), `DMXProtocolArtNet` (Runtime), `DMXProtocolSACN` (Runtime), `DMXProtocolEditor` (Editor), `DMXProtocolBlueprintGraph` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2019-11-19 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXProtocol) | |

---

## 用途

DMX Protocol 插件为 Unreal Engine 的虚拟制片（Virtual Production）工作流提供了 **DMX512 协议**的完整实现框架。DMX512 是舞台灯光、特效设备控制领域的行业标准数字通信协议，通过单向串行数据链路控制最多 512 个通道（Universe）。

该插件的核心价值在于：

1. **协议抽象层**：通过 `IDMXProtocol` / `IDMXProtocolFactory` 接口，将 DMX 通信抽象为统一的编程接口，使上层代码无需关心底层传输方式
2. **Art-Net 实现**：基于 Art-Net 协议（Artistic Licence 开发的以太网 DMX 传输标准），支持通过标准以太网网络发送和接收 DMX 数据，最多可寻址 32,768 个 Universe
3. **sACN 实现**：基于 E1.31 流式 ACN（Streaming Architecture for Control Networks）协议，另一种通过以太网传输 DMX 的 ANSI 标准
4. **蓝图集成**：提供蓝图节点，让设计师和灯光师无需编写 C++ 即可在关卡蓝图或 Actor 蓝图中控制 DMX 设备
5. **编辑器工具**：提供 DMX 协议配置界面，用于设置网络接口、Universe 映射等参数

简而言之：**这个插件让 UE 能够通过网络发送和接收 DMX 灯光控制信号，是虚拟制片中 LED 墙灯光同步、实时灯光预览等功能的基础设施。**

---

## 使用场景

- 你在做虚拟制片项目，需要让 UE 控制真实的舞台灯光设备 → 用 DMXProtocol（Art-Net 或 sACN）
- 你需要通过 LED 墙（LED Volume）进行实时拍摄，灯光需要与屏幕内容同步 → 用 DMXProtocol 发送 DMX 信号给灯光控制台
- 你在做灯光预可视化（Previz），需要模拟 DMX 控制台的行为 → 用 DMXProtocol 的蓝图节点
- 你需要在 UE 中接收来自灯光控制台的 DMX 数据，实时驱动场景中的灯光 → 用 DMXProtocol 的接收功能
- 你在做主题公园或沉浸式体验项目，需要通过网络控制大量 DMX 设备 → 用 Art-Net 的多 Universe 支持

---

## 模块架构

本插件包含 5 个模块，按职责分层：

```
┌─────────────────────────────────────────────────┐
│           DMXProtocolBlueprintGraph              │  ← 蓝图节点（UncookedOnly）
│         （蓝图图编辑器集成）                        │
├─────────────────────────────────────────────────┤
│              DMXProtocolEditor                    │  ← 编辑器 UI（Editor）
│         （协议配置面板、资产编辑器）                  │
├─────────────────────────────────────────────────┤
│    DMXProtocolArtNet    │    DMXProtocolSACN      │  ← 协议实现（Runtime）
│    （Art-Net 传输）       │    （sACN 传输）         │
├─────────────────────────────────────────────────┤
│                 DMXProtocol                       │  ← 核心框架（Runtime）
│    （协议接口、Universe 管理、数据模型）              │
└─────────────────────────────────────────────────┘
```

### DMXProtocol（核心框架）

提供 DMX 协议的抽象接口和数据模型：
- `IDMXProtocol` — 协议实例接口，定义发送/接收 DMX 数据的通用方法
- `IDMXProtocolFactory` — 协议工厂接口，各协议实现通过此接口注册自身
- Universe 管理、端口配置、信号监控等基础设施

### DMXProtocolArtNet（Art-Net 实现）

Art-Net 4 协议的具体实现，通过 UDP 广播在以太网上传输 DMX 数据。

### DMXProtocolSACN（sACN 实现）

E1.31 流式 ACN 协议的具体实现，另一种以太网 DMX 传输标准。

### DMXProtocolEditor（编辑器工具）

提供编辑器内的 DMX 配置界面，包括协议选择、网络接口绑定、Universe 映射等。

### DMXProtocolBlueprintGraph（蓝图集成）

为蓝图图编辑器提供自定义节点和引脚类型，使 DMX 操作可在蓝图中可视化使用。

---

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| Send DMX | 向指定 Universe 的指定通道发送 DMX 值（0-255） | `UDMXProtocolBlueprintFunctionLibrary` |
| Receive DMX | 从指定 Universe 接收 DMX 数据 | `UDMXProtocolBlueprintFunctionLibrary` |
| Get DMX Protocol | 获取指定名称的 DMX 协议实例 | `UDMXProtocolBlueprintFunctionLibrary` |
| Get Universe | 获取指定 Universe 的通道数据 | `UDMXProtocolBlueprintFunctionLibrary` |

### 使用示例（蓝图描述）

**发送 DMX 数据到灯光设备：**

1. 在关卡蓝图中，添加一个 `Event BeginPlay` 节点
2. 连接到 `Get DMX Protocol` 节点，协议名称选择 "ArtNet" 或 "sACN"
3. 将返回的协议对象连接到 `Send DMX` 节点
4. 设置 Universe ID（例如 0）、起始通道（例如 1）
5. 创建一个 Byte 数组作为通道值（例如 [255, 128, 0] 表示通道 1 全亮、通道 2 半亮、通道 3 关闭）
6. 连接数组到 `Send DMX` 的数据输入引脚

**接收 DMX 数据驱动场景灯光：**

1. 在 Tick 事件中调用 `Receive DMX` 节点
2. 指定要监听的 Universe ID
3. 返回的通道数据数组可用于驱动 Point Light 的颜色和强度
4. 通过 `Set Light Color` 和 `Set Intensity` 节点实时更新灯光

---

## C++ 用法

### 头文件引入

```cpp
// 核心协议框架
#include "DMXProtocolModule.h"

// Art-Net 协议
#include "DMXProtocolArtNetModule.h"

// 协议接口
#include "Interfaces/IDMXProtocol.h"
#include "Interfaces/IDMXProtocolFactory.h"
```

### 基本用法

**获取协议实例并发送 DMX 数据：**

```cpp
// 来源: DMXProtocolArtNetModule.h 中的控制台命令实现逻辑

#include "DMXProtocolModule.h"
#include "Interfaces/IDMXProtocol.h"

void SendDMXExample()
{
    // 获取 DMX 协议模块
    FDMXProtocolModule& DMXModule = FDMXProtocolModule::Get();
    
    // 获取 Art-Net 协议实例
    IDMXProtocolPtr Protocol = DMXModule.GetProtocol(FName("ArtNet"));
    if (Protocol.IsValid())
    {
        // 准备 DMX 数据：Universe 1, 通道 10-13
        TMap<int32, uint8> ChannelValues;
        ChannelValues.Add(10, 6);
        ChannelValues.Add(11, 7);
        ChannelValues.Add(12, 8);
        ChannelValues.Add(13, 9);
        
        // 发送到 Universe 17
        Protocol->SendDMX(17, ChannelValues);
    }
}
```

### 进阶用法

**通过控制台命令发送 DMX（Art-Net 模块内置功能）：**

```cpp
// 来源: DMXProtocolArtNetModule.h - SendDMXCommandHandler

// 控制台命令格式：
// DMX.ArtNet.SendDMX [UniverseID] Channel:Value Channel:Value ...
// 示例：DMX.ArtNet.SendDMX 17 10:6 11:7 12:8 13:9
//
// UniverseID: 0 - 32767
// Channel: 0 - 511
// Value: 0 - 255

// 重置 Universe：
// DMX.ArtNet.ResetDMXSend [UniverseID]
```

**实现自定义 DMX 协议（通过工厂模式注册）：**

```cpp
// 来源: DMXProtocolArtNetModule.h - FDMXProtocolFactoryArtNet

#include "Interfaces/IDMXProtocolFactory.h"

// 自定义协议工厂
class FDMXProtocolFactoryMyCustom : public IDMXProtocolFactory
{
public:
    virtual IDMXProtocolPtr CreateProtocol(const FName& ProtocolName) override
    {
        // 创建并返回自定义协议实例
        return MakeShared<FDMXProtocolMyCustom>(ProtocolName);
    }
};

// 在模块启动时注册
void FDMXProtocolMyCustomModule::StartupModule()
{
    TArray<FDMXProtocolRegistrationParams> RegistrationParams;
    FDMXProtocolRegistrationParams Params;
    Params.ProtocolName = FName("MyCustom");
    Params.Factory = MakeUnique<FDMXProtocolFactoryMyCustom>();
    RegistrationParams.Add(MoveTemp(Params));
    
    // 注册到核心协议模块
    RegisterWithProtocolModule(RegistrationParams);
}
```

---

## Demo 示例

### 最小可编译示例：发送 Art-Net DMX 数据

**MyDMXActor.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Interfaces/IDMXProtocol.h"
#include "MyDMXActor.generated.h"

UCLASS()
class AMyDMXActor : public AActor
{
    GENERATED_BODY()

public:
    AMyDMXActor();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    /** 要发送到的 Universe ID */
    UPROPERTY(EditAnywhere, Category = "DMX")
    int32 UniverseID = 0;

    /** DMX 协议名称 (ArtNet 或 sACN) */
    UPROPERTY(EditAnywhere, Category = "DMX")
    FName ProtocolName = FName("ArtNet");

private:
    IDMXProtocolPtr DMXProtocol;
    float ElapsedTime = 0.0f;
};
```

**MyDMXActor.cpp**

```cpp
#include "MyDMXActor.h"
#include "DMXProtocolModule.h"

AMyDMXActor::AMyDMXActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyDMXActor::BeginPlay()
{
    Super::BeginPlay();

    // 获取 DMX 协议实例
    FDMXProtocolModule& DMXModule = FDMXProtocolModule::Get();
    DMXProtocol = DMXModule.GetProtocol(ProtocolName);

    if (!DMXProtocol.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("DMX Protocol '%s' not found!"), *ProtocolName.ToString());
    }
}

void AMyDMXActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (!DMXProtocol.IsValid())
    {
        return;
    }

    ElapsedTime += DeltaTime;

    // 生成一个简单的呼吸灯效果
    uint8 Brightness = static_cast<uint8>(FMath::Abs(FMath::Sin(ElapsedTime * 2.0f)) * 255.0f);

    // 构建通道数据：通道 1 = 亮度, 通道 2 = 红, 通道 3 = 绿, 通道 4 = 蓝
    TMap<int32, uint8> ChannelData;
    ChannelData.Add(1, Brightness);       // Dimmer
    ChannelData.Add(2, 255);              // Red
    ChannelData.Add(3, 128);              // Green
    ChannelData.Add(4, 0);                // Blue

    // 发送 DMX 数据
    DMXProtocol->SendDMX(UniverseID, ChannelData);
}
```

**Build.cs 依赖**

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "DMXProtocol",
    "DMXProtocolArtNet"  // 如果使用 Art-Net
    // "DMXProtocolSACN"  // 如果使用 sACN
});
```

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DMXProtocol` | 核心协议框架，所有 DMX 功能的基础 |
| `DMXProtocolArtNet` | Art-Net 协议实现，以太网 DMX 传输 |
| `DMXProtocolSACN` | sACN (E1.31) 协议实现，另一种以太网 DMX 传输 |
| `DMXProtocolEditor` | 编辑器配置 UI（仅编辑器环境） |
| `DMXProtocolBlueprintGraph` | 蓝图图编辑器集成（仅开发环境） |

**使用者需要依赖的模块**：
- `DMXProtocol` — 必须，提供核心接口
- `DMXProtocolArtNet` 或 `DMXProtocolSACN` — 按需选择具体协议实现

---

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 近期 | `ed12aec9a262` | DMX: Remove any uses of FORCEINLINE, replace with inline where appropriate | 代码规范清理，将 `FORCEINLINE` 替换为 `inline`，避免不必要的内联膨胀 |
| 近期 | `09ac80358139` | More bool to EAllowShrinking fixes | API 适配：将 bool 参数迁移为 EAllowShrinking 枚举，跟随引擎 API 变更 |
| 近期 | `35885cc95b35` | DMX - Fix log level for invalid ports prevents from packaging with invalid ports | Bug 修复：修复无效端口的日志级别问题，之前可能导致打包失败 |

### 维护评价

- **创建时间**：2019 年 11 月，约 6 年历史
- **最近更新**：近期有维护性更新，主要是代码规范清理和引擎 API 适配
- **活跃程度**：维护中，但近期更新以编译修复和代码清理为主，无新功能添加
- **实验性状态**：非实验性（`IsBetaVersion=false`），但 `EnabledByDefault=false` 需手动启用
- **已知限制**：作为虚拟制片工具链的一部分，依赖 UE 的 DMX 框架生态

**综合评价**：这是一个成熟的虚拟制片基础设施插件，由 Epic 官方维护。虽然近期没有重大功能更新，但仍在跟随引擎版本进行必要的维护。对于需要 DMX 灯光控制的虚拟制片项目，这是官方推荐的解决方案。**推荐在虚拟制片项目中使用。**

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXProtocol)
- [官方文档]()（暂无）
- [测试用例]()（待确认）