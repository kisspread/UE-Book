# DMX DisplayCluster

> Allows integration between DMX and DisplayCluster

| 属性 | 值 |
|---|---|
| 中文名 | DMX与nDisplay集成 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据资产） |
| 模块 | `DMXDisplayCluster` (Runtime), `DMXDisplayClusterLightCard` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-05-11 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXDisplayCluster) | |

## 用途

此插件专门用于将 DMX 灯光控制协议集成到 nDisplay（DisplayCluster）渲染集群中，解决虚拟制片工作流中“通过 DMX 控制台控制虚拟 LED 墙光照”的问题。其核心功能是作为桥梁，接收外部 DMX 信号，并将其映射并应用到 nDisplay 集群中的“光照卡（Light Card）”组件上，从而实现对虚拟场景中物理 LED 屏幕光照属性（如亮度、色温、旋转等）的实时、标准化控制。它不是通用的 DMX 集成插件，而是针对虚拟制片中特定工作流的专用工具。

## 使用场景

- 你在进行虚拟制片，并希望通过行业标准的 DMX 512 控制台来实时调整 LED 墙（由 nDisplay 驱动）的“环境光照”或“补光”效果。
- 你需要为不同片场或项目创建标准化的 DMX 通道映射文件，以便灯光师可以无缝切换控制不同的虚拟光照设置。
- 你的灯光团队习惯于使用 grandMA 或其他 DMX 控制台工作，并希望将同样的控制逻辑应用于虚拟制作环境中的数字资产。

## 蓝图用法

蓝图功能主要围绕创建和控制 `UDMXDisplayClusterLightCardComponent` 以及与 `UDMXDisplayClusterSubsystem` 交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create DMX Light Card Component` | 在指定的 Actor 上创建一个 DMX 光照卡组件实例 | `UDMXDisplayClusterSubsystem` |
| `Set DMX Universe` | 设置组件监听的 DMX 宇宙号 | `UDMXDisplayClusterLightCardComponent` |
| `Set Starting Channel` | 设置组件在 DMX 宇宙中的起始通道号 | `UDMXDisplayClusterLightCardComponent` |
| `Apply DMX` | 强制组件根据当前缓存的 DMX 值更新其光照属性 | `UDMXDisplayClusterLightCardComponent` |
| `Calculate DMX Value` | 根据光照卡属性（如亮度）反算出对应的 DMX 通道值 | `UDMXDisplayClusterSubsystem` |

### 使用示例（蓝图描述）

1.  在你的 nDisplay 场景 Actor 上，通过 `DMXDisplayClusterSubsystem` 的 `Create DMX Light Card Component` 节点添加一个光照卡组件。
2.  使用 `Set DMX Universe` 和 `Set Starting Channel` 节点为该组件配置 DMX 地址。
3.  当需要程序化控制时，可使用 `Calculate DMX Value` 节点计算出特定亮度值对应的 DMX 值。
4.  外部 DMX 数据会自动更新组件状态。若需手动刷新，可调用 `Apply DMX` 节点。

## C++ 用法

### 头文件引入

```cpp
#include “DMXDisplayClusterSubsystem.h”
#include “DMXDisplayClusterLightCardComponent.h”
```

### 基本用法

以下代码展示如何获取子系统并创建一个光照卡组件。
（来源: 测试用例及公开接口推断）

```cpp
// 获取 DMX DisplayCluster 子系统
UDMXDisplayClusterSubsystem* DMXSubsystem = GEngine->GetEngineSubsystem<UDMXDisplayClusterSubsystem>();
if (DMXSubsystem)
{
    // 在目标 Actor 上创建一个 DMX 光照卡组件
    UDMXDisplayClusterLightCardComponent* NewLightCard = DMXSubsystem->CreateDMXLightCardComponent(TargetActor);
    if (NewLightCard)
    {
        // 配置其 DMX 地址
        NewLightCard->SetDMXUniverse(1);
        NewLightCard->SetStartingChannel(100);
    }
}
```

### 进阶用法

监听并处理 DMX 信号变化，并将其与 nDisplay 的视图或 Actor 属性关联。
（来源: 多个测试用例及组件逻辑推断）

```cpp
// 假设你已经有一个 UDMXDisplayClusterLightCardComponent* MyLightCard;

// 可以绑定到其属性变更委托
MyLightCard->OnDMXValueChanged.AddDynamic(this, &AMyActor::HandleDMXUpdate);

// 在回调函数中处理 DMX 数据
void AMyActor::HandleDMXUpdate(UDMXDisplayClusterLightCardComponent* Component, const FDMXAttributeName& Attribute, float Value)
{
    if (Attribute == FDMXAttributeName(“Brightness”))
    {
        // 可以使用 Value 直接控制其他 Actor 的亮度或材质参数
        SomePointLight->SetIntensity(Value * MaxIntensity);
    }
}
```

## Demo 示例

一个完整的最小可编译示例，展示如何通过 C++ 创建组件并响应 DMX 值变化。

**MyDMXActor.h**
```cpp
#pragma once

#include “CoreMinimal.h”
#include “GameFramework/Actor.h”
#include “DMXDisplayClusterLightCardComponent.h”
#include “MyDMXActor.generated.h”

UCLASS()
class MYPROJECT_API AMyDMXActor : public AActor
{
    GENERATED_BODY()

public:
    AMyDMXActor();

protected:
    virtual void BeginPlay() override;

    UFUNCTION()
    void OnBrightnessChanged(UDMXDisplayClusterLightCardComponent* Component, const FDMXAttributeName& Attribute, float Value);

    UPROPERTY(VisibleAnywhere)
    UDMXDisplayClusterLightCardComponent* DMXLightCard;
};
```

**MyDMXActor.cpp**
```cpp
#include “MyDMXActor.h”
#include “DMXDisplayClusterSubsystem.h”

AMyDMXActor::AMyDMXActor()
{
    PrimaryActorTick.bCanEverTick = false;
    DMXLightCard = CreateDefaultSubobject<UDMXDisplayClusterLightCardComponent>(TEXT(“DMXLightCard”));
}

void AMyDMXActor::BeginPlay()
{
    Super::BeginPlay();

    // 配置 DMX 地址
    if (DMXLightCard)
    {
        DMXLightCard->SetDMXUniverse(2);
        DMXLightCard->SetStartingChannel(1);
        // 绑定到亮度属性变更
        DMXLightCard->OnDMXValueChanged.AddDynamic(this, &AMyDMXActor::OnBrightnessChanged);
    }
}

void AMyDMXActor::OnBrightnessChanged(UDMXDisplayClusterLightCardComponent* Component, const FDMXAttributeName& Attribute, float Value)
{
    // 简单地打印接收到的 DMX 亮度值
    UE_LOG(LogTemp, Log, TEXT(“Received DMX Brightness: %f”), Value);
    // 在此处添加控制其他元素的逻辑
}
```

## 模块依赖

根据 `DMXDisplayCluster.Build.cs` 和 `DMXDisplayClusterLightCard.Build.cs`，除了常见的 Core/Engine 模块外，该插件还有以下特殊依赖：

| 模块 | 用途 |
|---|---|
| `DMX` | 核心 DMX 协议处理与信号路由模块 |
| `DMXBlueprintGraph` | 提供 DMX 相关的蓝图节点支持（编辑器相关） |
| `DisplayCluster` | nDisplay 核心运行时模块，管理集群与视图 |
| `DisplayClusterLightCard` | nDisplay 光照卡运行时模块，提供基础光照卡功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-09-26 | `d63fc61b` | DMX: Let DMXDisplayClusterLightCardComponent follow the logic of latest DisplayClusterLightCardActor | 使 DMX 光照卡组件的逻辑与最新的 DisplayCluster 光照卡 Actor 保持同步 |
| 2024-09-17 | `29962d04` | DMX: Remove experimental and beta flags from DMX plugins. All DMX plugins are now production ready | 移除 DMX 相关插件的测试版和实验性标志，所有 DMX 插件现已进入生产就绪状态 |
| 2023-09-06 | `66eba088` | nDisplay: Added invoke of OnObjectPropertyChanged to the DMX Light Card component when applying chan | 在应用通道变更时，向 DMX 光照卡组件添加了 OnObjectPropertyChanged 事件的调用 |
| 2023-06-05 | `6509b485` | nDisplay: Fixed issue where the DMXDisplayClusterLightCard module was not loading in before the ligh | 修复了 DMXDisplayClusterLightCard 模块未能在光照卡模块之前加载的问题 |
| 2023-01-20 | `9ac9217c` | DMX - Keep light cards flush to wall when controlled via DMX and bAlwaysFlushToWall is set | 修复了当通过 DMX 控制且设置 bAlwaysFlushToWall 时，光照卡能够保持紧贴墙壁 |

### 维护评价

**活跃维护**。该插件自 2021 年创建，最近一次实质性更新（移除测试标志、同步最新逻辑）发生在 2024 年 9 月，表明 Epic Games 仍在积极维护并将其整合到最新的虚拟制片工作流中。插件已明确从实验性转为生产就绪状态，适用于虚拟制片项目。其功能专一且稳定，是 nDisplay 与 DMX 工作流集成的标准解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXDisplayCluster)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXDisplayCluster/Tests)
- [关联插件: DisplayCluster (nDisplay)](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DisplayCluster)