# DMX Protocol

> DMX Protocols implementation

| 属性 | 值 |
|---|---|
| 中文名 | DMX协议 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DMXProtocol` (Runtime), `DMXProtocolArtNet` (Runtime), `DMXProtocolSACN` (Runtime), `DMXProtocolEditor` (Editor), `DMXProtocolBlueprintGraph` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXProtocol) | |

## 用途

本插件为 Unreal Engine 实现了 DMX（Digital Multiplex）通信协议栈。DMX 是娱乐行业（舞台灯光、特效、LED 墙）中用于控制设备的标准协议。

插件的核心价值在于：
1.  **协议抽象**：定义了统一的 `IDMXProtocol` 接口和核心管理类 `FDMXProtocolModule`，将具体的协议实现（如 ArtNet, SACN）与引擎解耦。
2.  **协议实现**：提供了 ArtNet 和 sACN (E1.31) 两种主流 DMX-over-IP 协议的实现。
3.  **蓝图集成**：提供了蓝图图表面板自定义引脚工厂，使 `FDMXPortReference` 等类型可以在蓝图中作为节点的输入/输出端口显示，并允许用户从下拉列表中选择配置好的 DMX 端口。
4.  **端口管理**：实现了 `FDMXPort`、`FDMXInputPort`、`FDMXOutputPort` 等类，用于管理 DMX 数据的发送和接收通道（Universe）。

**简单来说，这个插件解决了让 UE 项目能够通过网络发送和接收 DMX 数据，从而实现与外部灯光控制台、LED 控制器等物理设备同步或控制的问题。**

## 使用场景

-   **虚拟制片 (Virtual Production)**：在 LED Volume 虚拟制片场景中，同步屏幕上的虚拟灯光与现场照明设备（如聚光灯、氛围灯）的状态和颜色。
-   **灯光秀预览与调试**：在编辑器中设计复杂的灯光序列，通过 DMX 输出驱动真实或虚拟的灯光设备进行预览。
-   **互动装置与控制**：创建由游戏逻辑或蓝图控制的灯光装置，通过 DMX 协议发送指令。
-   **设备集成**：接收来自 DMX 控制台（如 grandMA）的信号，用于触发 UE 内的游戏事件或控制媒体播放。

## 蓝图用法

该插件的蓝图功能主要通过 **DMXProtocolBlueprintGraph** 模块体现，它增强了蓝图编辑器，使其能够理解和编辑 DMX 相关的数据类型（如端口引用）。

### 核心节点

`DMXProtocolBlueprintGraph` 模块主要提供编辑器扩展，并不直接向蓝图用户暴露可调用函数节点。其作用是自定义蓝图图表中 DMX 相关数据类型引脚的外观和交互方式。

| 组件 | 说明 | 所在类 |
|---|---|---|
| DMX 图表面板引脚工厂 | 在蓝图编辑器中，为 `FDMXInputPortReference` 和 `FDMXOutputPortReference` 类型的属性创建自定义引脚外观和选择逻辑。 | `FDMXProtocolGraphPanelPinFactory` |
| 输入端口引用引脚控件 | 为 `FDMXInputPortReference` 类型的蓝图引脚提供一个下拉列表，用于选择项目中配置好的 DMX 输入端口。 | `SDMXInputPortReferenceGraphPin` |
| 输出端口引用引脚控件 | 为 `FDMXOutputPortReference` 类型的蓝图引脚提供一个下拉列表，用于选择项目中配置好的 DMX 输出端口。 | `SDMXOutputPortReferenceGraphPin` |

### 使用示例（蓝图描述）

1.  在 **DMX 项目设置** 中配置好 ArtNet 或 sACN 的输入/输出端口。
2.  在蓝图中，定义一个 `FDMXOutputPortReference` 类型的变量，或在一个拥有 `FDMXOutputPortReference` 属性的自定义节点上，你会看到一个经过自定义的图表面板引脚。
3.  该引脚会显示为一个带有下拉箭头的控件。点击下拉箭头，列表会自动填充你在项目设置中配置的所有可用 DMX 输出端口。
4.  选择一个端口后，蓝图在运行时就可以通过该引脚关联的协议（ArtNet/sACN）向对应的网络地址发送 DMX 数据。

## C++ 用法

### 头文件引入

使用核心协议管理功能：
```cpp
#include "DMXProtocolModule.h"
#include "Interfaces/IDMXProtocol.h"
#include "DMXProtocolCommon.h"
```

使用蓝图图表引脚工厂（通常用于编辑器自定义）：
```cpp
#include "DMXProtocolBlueprintGraphModule.h"
#include "DMXProtocolGraphPanelPinFactory.h"
```

### 基本用法

```cpp
// 示例：获取 DMX 协议模块并查询状态
#include "DMXProtocolModule.h"

void CheckDMXStatus()
{
    // 获取 DMX 协议管理模块的单例
    FDMXProtocolModule& DMXModule = FDMXProtocolModule::Get();

    // 检查 ArtNet 协议是否可用
    if (TSharedPtr<IDMXProtocol> ArtNetProtocol = DMXModule.GetProtocol(EDMXProtocolType::ArtNet))
    {
        UE_LOG(LogTemp, Log, TEXT("ArtNet Protocol is active. Name: %s"), *ArtNetProtocol->GetProtocolName().ToString());
    }

    // 列出所有已注册的协议
    TArray<FName> ProtocolNames = DMXModule.GetProtocolNames();
    for (const FName& Name : ProtocolNames)
    {
        UE_LOG(LogTemp, Log, TEXT("Registered DMX Protocol: %s"), *Name.ToString());
    }
}
```
*(概念性示例，基于模块接口推断)*

### 进阶用法

```cpp
// 示例：（概念性）实现并注册一个自定义的 DMX 协议
// 通常，ArtNet 和 sACN 已经内置。自定义协议需要在插件早期阶段（如模块 StartupModule）注册。

#include "Interfaces/IDMXProtocol.h"

// 1. 定义一个类继承自 IDMXProtocol
class FMyCustomDMXProtocol : public IDMXProtocol
{
    // ... 实现所有纯虚函数，如 Init, Shutdown, SendDMX, ReceiveDMX 等 ...
};

// 2. 在自定义模块的 StartupModule 中注册
void FMyModule::StartupModule()
{
    if (FDMXProtocolModule::IsAvailable())
    {
        TSharedPtr<FMyCustomDMXProtocol> MyProtocol = MakeShared<FMyCustomDMXProtocol>();
        FDMXProtocolModule::Get().RegisterProtocol(MyProtocol);
    }
}
```
*(概念性示例，展示接口扩展性)*

## Demo 示例

以下示例展示了如何在运行时模块中初始化 DMX 协议库并简单地查询状态。

**MyDMXActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyDMXActor.generated.h"

UCLASS()
class AMyDMXActor : public AActor
{
    GENERATED_BODY()

public:
    AMyDMXActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    void CheckProtocols();
};
```

**MyDMXActor.cpp**
```cpp
#include "MyDMXActor.h"
#include "DMXProtocolModule.h"
#include "Interfaces/IDMXProtocol.h"

AMyDMXActor::AMyDMXActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyDMXActor::BeginPlay()
{
    Super::BeginPlay();
    // 延迟一帧检查，确保所有模块已加载完毕
    GetWorldTimerManager().SetTimerForNextTick(this, &AMyDMXActor::CheckProtocols);
}

void AMyDMXActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    Super::EndPlay(EndPlayReason);
    // DMX 协议模块会自动管理生命周期，通常无需手动清理
}

void AMyDMXActor::CheckProtocols()
{
    if (!FDMXProtocolModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("DMXProtocolModule is not available."));
        return;
    }

    FDMXProtocolModule& DMXModule = FDMXProtocolModule::Get();

    // 查询内置协议
    if (TSharedPtr<IDMXProtocol> ArtNet = DMXModule.GetProtocol(EDMXProtocolType::ArtNet))
    {
        UE_LOG(LogTemp, Log, TEXT("ArtNet Protocol initialized: %s"), ArtNet->GetProtocolName().ToString().ToChar());
    }

    if (TSharedPtr<IDMXProtocol> SACN = DMXModule.GetProtocol(EDMXProtocolType::sACN))
    {
        UE_LOG(LogTemp, Log, TEXT("sACN Protocol initialized: %s"), SACN->GetProtocolName().ToString().ToChar());
    }
}
```

## 模块依赖

根据插件包含的模块，其依赖关系如下：

| 模块 | 用途 |
|---|---|
| `DMXProtocol` | 所有其他 DMX 协议模块的基础，定义了核心接口、管理类和通用数据结构。 |
| `DMXProtocolArtNet` | ArtNet 协议实现，依赖于 `DMXProtocol` 核心模块。 |
| `DMXProtocolSACN` | sACN (E1.31) 协议实现，依赖于 `DMXProtocol` 核心模块。 |
| `DMXProtocolEditor` | 提供 DMX 相关资产的编辑器界面和自定义（如项目设置），依赖于 `DMXProtocol` 核心模块。 |
| `DMXProtocolBlueprintGraph` | 提供蓝图编辑器中 DMX 数据类型的自定义引脚外观，依赖于 `DMXProtocol` 核心模块。 |

**注意**：该插件没有列出特殊的模块依赖（如 `Networking`, `Sockets`），但其内部实现（ArtNet/sACN）必然依赖引擎的网络子系统。使用者只需依赖其提供的运行时模块即可。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新的格式化日志宏。 |
| 2026-04-08 | `86879cf0` | Fix unreachable code warnings | 修复不可达代码警告，提升代码质量。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 在修复了错误的查找替换后，进行第二次提交。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了编号为 51314860 的变更。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing registrations | 将委托获取方式从属性改为函数，修复缺失注册问题。 |

### 维护评价

该插件创建于 2020 年 9 月，已有近 6 年历史。从最近的提交记录看，**仍在活跃维护中**。
-   **积极方面**：近期有多次提交，主要集中在**代码现代化**（如日志宏迁移）和**编译问题修复**（如消除警告），这表明该插件被用于重要项目，并且 Epic 团队在持续确保其与最新引擎版本的兼容性和稳定性。
-   **注意事项**：最近的更新多为修复和适配，没有看到重大新功能或协议版本更新。这可能意味着其核心功能已趋于稳定。
-   **推荐使用**：**强烈推荐**在任何需要 DMX 功能的虚拟制片或相关项目中使用。它是官方实现，稳定且得到了维护。对于 ArtNet 和 sACN 这两个主流协议的支持已经足够满足绝大多数需求。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXProtocol)
-   官方文档：无（`.uplugin` 中未提供 DocsURL）
-   测试用例：未在提供的信息中找到明确的测试文件路径。