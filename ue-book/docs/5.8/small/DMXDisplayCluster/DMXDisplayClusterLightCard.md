# DMX DisplayCluster

> Allows integration between DMX and DisplayCluster（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | DMX 显示集群集成 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（代码模块） |
| 模块 | `DMXDisplayCluster` (Runtime), `DMXDisplayClusterLightCard` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-05-11 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXDisplayCluster) | |

## 用途

此插件的核心作用是将 Unreal Engine 的 DMX（数字多路复用）控制系统与 nDisplay 集群渲染系统连接起来。它解决的关键问题是：在现场虚拟制作（Virtual Production）环境中，允许使用专业的 DMX 灯光控制台来远程、实时地操控 nDisplay 集群中虚拟场景的灯光（例如 LightCard 演员）。这使得虚拟场景的灯光氛围可以与现场实体灯光保持精确同步，提升了现场导演对最终画面的实时掌控能力。

插件通过 `DMXDisplayClusterLightCard` 模块实现其主要功能，该模块注册为 nDisplay LightCard 演员的扩展器，为 LightCard 添加了接收和处理 DMX 信号的能力。

## 使用场景

- **LED 墙虚拟拍摄**：在大型 LED 墙的拍摄现场，灯光师使用 DMX 控制台调整现场实体灯光的同时，需要同步调整 LED 墙上显示的虚拟背景（如天空、光源）的亮度、色温、位置等属性。
- **实时虚拟制片**：导演希望在拍摄过程中，通过灯光控制台一键切换虚拟场景的“日景”或“夜景”氛围，而无需暂停拍摄进入编辑器。
- **混合现实制作**：需要将 XR 舞台的虚拟灯光与 AR 透视头显中看到的虚拟物体灯光进行精确匹配。

## 蓝图用法

`DMXDisplayClusterLightCard` 模块本身主要提供 C++ 扩展接口，其功能在 nDisplay 的 LightCard 编辑器界面中自动生效。在蓝图层面，主要通过配置相关的 Actor 和组件来使用。

### 核心节点

由于 `UDMXDisplayClusterLightCardComponent` 类标记为 `NotBlueprintable`，且未暴露公共的 `BlueprintCallable` 函数，因此没有直接可用的蓝图节点。其工作方式是作为“扩展器”自动附加到 nDisplay 的 LightCard 演员上，功能通过编辑器属性面板配置。

### 使用示例（蓝图描述）

1.  在你的 nDisplay 配置（DisplayCluster 配置资产）中，创建或选择一个 **LightCard 演员**。
2.  在 LightCard 演员的 **Details（细节）** 面板中，找到 `DMX` 分类。
3.  在该分类下，配置 `Fixture Patch` 属性，将其指向一个已在 DMX 库中定义好的、代表该虚拟灯光的 **DMX Fixture Patch**。
4.  展开 `Value Ranges` 属性，根据你所使用的 DMX 控制台输出值的范围，配置 `Min` 和 `Max` 值。这些范围将控制 DMX 信号值如何映射到 LightCard 的实际属性（如位置、旋转、缩放、温度等）。
5.  现场灯光师即可通过 DMX 控制台发送信号，实时控制该 LightCard。

## C++ 用法

### 头文件引入

```cpp
#include “DMXDisplayClusterLightCardComponent.h”
#include “Components/DMXComponent.h”
```

### 基本用法

此插件的核心是 `UDMXDisplayClusterLightCardComponent`，它通常不会被手动创建和添加。当 `DMXDisplayClusterLightCard` 模块启用后，它会自动将自身注册为 nDisplay LightCard 演员的扩展器，使得每个 LightCard 演员都会自动获得该组件的功能。开发者的主要工作是配置其属性。

配置通常在编辑器中进行，但也可以在 C++ 中动态设置。

**示例：获取并配置 LightCard 上的 DMX 组件** (基于组件结构逻辑)
```cpp
// 假设你已经有一个指向 nDisplay LightCard 演员的指针 ADisplayClusterLightCardActor* MyLightCard
// 获取其上的 DMX LightCard 组件
UDMXDisplayClusterLightCardComponent* DMXLightCardComp = MyLightCard->FindComponentByClass<UDMXDisplayClusterLightCardComponent>();

if (DMXLightCardComp)
{
    // 在运行时动态设置 DMX Fixture Patch（通常来自资产引用）
    UDMXEntityFixturePatch* MyFixturePatch = LoadObject<UDMXEntityFixturePatch>(nullptr, TEXT(“/Game/DMX/Patches/LightCard01”));
    DMXLightCardComp->SetFixturePatch(MyFixturePatch); // 注意：SetFixturePatch 来自父类 UDMXComponent

    // 调整值范围（例如，设置旋转范围为 0-180 度）
    DMXLightCardComp->ValueRanges.MaxYaw = 180.0;
    DMXLightCardComp->ValueRanges.MaxPitch = 180.0;
    DMXLightCardComp->ValueRanges.MaxSpin = 180.0;
}
```

### 进阶用法

插件通过 `IDisplayClusterLightCardActorExtender` 接口实现扩展。在 `FDMXDisplayClusterLightCardModule::StartupModule()` 中，它会调用 `IDisplayClusterLightCardActorExtenderRegistry::Get().RegisterExtender(this)` 来注册自身。`GetAdditionalSubobjectClass()` 方法返回 `UDMXDisplayClusterLightCardComponent::StaticClass()`，这告诉 nDisplay 系统，对于每一个 LightCard 演员，都应额外创建一个此类型的组件。

## Demo 示例

以下示例展示了如何创建一个简单的 Actor，该 Actor 包含逻辑来查找并配置其关联的 nDisplay LightCard 上的 DMX 组件。**请注意，在实际虚拟制片项目中，配置通常通过编辑器UI完成。**

**DMXConfigurableLightCardActor.h**
```cpp
#pragma once

#include “CoreMinimal.h”
#include “GameFramework/Actor.h”
#include “DMXConfigurableLightCardActor.generated.h”

class UDMXDisplayClusterLightCardComponent;

UCLASS()
class ADMXConfigurableLightCardActor : public AActor
{
    GENERATED_BODY()

public:
    ADMXConfigurableLightCardActor();

protected:
    virtual void BeginPlay() override;

    // 在这里引用一个DMX Fixture Patch资产
    UPROPERTY(EditAnywhere, Category = “DMX”)
    TObjectPtr<UDMXEntityFixturePatch> TargetFixturePatch;
};
```

**DMXConfigurableLightCardActor.cpp**
```cpp
#include “DMXConfigurableLightCardActor.h”
#include “DMXDisplayClusterLightCardComponent.h”
#include “DisplayClusterLightCardActor.h” // nDisplay LightCard Actor基类

ADMXConfigurableLightCardActor::ADMXConfigurableLightCardActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ADMXConfigurableLightCardActor::BeginPlay()
{
    Super::BeginPlay();

    // 查找场景中已经存在的、由nDisplay管理的LightCard演员
    // 注意：在实际项目中，你可能需要更精确的查找逻辑，例如通过标签
    TArray<AActor*> FoundActors;
    UGameplayStatics::GetAllActorsOfClass(GetWorld(), ADisplayClusterLightCardActor::StaticClass(), FoundActors);

    if (FoundActors.Num() > 0)
    {
        // 假设我们控制第一个找到的LightCard
        ADisplayClusterLightCardActor* TargetLightCard = Cast<ADisplayClusterLightCardActor>(FoundActors[0]);
        if (TargetLightCard)
        {
            // 获取插件自动附加的DMX组件
            UDMXDisplayClusterLightCardComponent* DMXComp = TargetLightCard->FindComponentByClass<UDMXDisplayClusterLightCardComponent>();
            if (DMXComp && TargetFixturePatch)
            {
                // 设置其Fixture Patch，使其开始接收DMX数据
                DMXComp->SetFixturePatch(TargetFixturePatch);
            }
        }
    }
}
```

## 模块依赖

此插件依赖于 Unreal Engine 的 DMX 和 nDisplay 核心系统。在你的项目 `.Build.cs` 文件中，如果需要在自己的模块中与这个插件交互，通常需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `DMXDisplayCluster` | 插件的基础运行时模块 |
| `DMXDisplayClusterLightCard` | 实现LightCard与DMX集成的具体模块 |
| `DMX` | 提供DMX协议、Fixture、Patch等核心功能 |
| `DisplayCluster` | 提供nDisplay集群渲染和LightCard等核心功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-09-26 | `d63fc61b` | DMX: Let DMXDisplayClusterLightCardComponent follow the logic of latest DisplayClusterLightCardActor | 让DMX灯卡组件同步最新DisplayCluster灯卡演员的逻辑 |
| 2024-09-17 | `29962d04` | DMX: Remove experimental and beta flags from DMX plugins. All DMX plugins are now production ready | 移除DMX插件的实验性与测试版标记，全部DMX插件现已为生产就绪 |
| 2023-09-06 | `66eba088` | nDisplay: Added invoke of OnObjectPropertyChanged to the DMX Light Card component when applying chan | nDisplay: DMX灯卡组件在应用通道时新增触发OnObjectPropertyChanged |
| 2023-06-05 | `6509b485` | nDisplay: Fixed issue where the DMXDisplayClusterLightCard module was not loading in before the ligh | nDisplay: 修复了DMXDisplayClusterLightCard模块未能在灯卡加载前完成加载的问题 |
| 2023-01-20 | `9ac9217c` | DMX - Keep light cards flush to wall when controlled via DMX and bAlwaysFlushToWall is set | DMX - 当通过DMX控制且设置了bAlwaysFlushToWall时，保持灯卡紧贴墙面 |

### 维护评价

- **活跃维护**：插件在 2024 年 9 月有重要的功能性更新（移除实验性标志，并对齐最新逻辑），表明它正在被积极维护并进入成熟阶段。
- **功能稳定**：更新记录主要围绕 bug 修复、兼容性改进和与最新引擎功能同步，说明其核心功能已趋于稳定。
- **生产就绪**：明确移除了“实验性”和“测试版”标签，官方声明其为生产就绪状态。
- **推荐使用**：**强烈推荐**在虚拟制片项目中需要使用 DMX 控制 nDisplay LightCard 的场景使用此插件。它提供了官方、稳定且持续维护的集成方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXDisplayCluster)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/Plugins/VirtualProduction/DMX/)（通用 DMX 文档，涵盖此插件功能）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXDisplayCluster/Source/DMXDisplayClusterLightCard/Tests)（如果存在）