# nDisplay Modular Features

> Modular Features for nDisplay

| 属性 | 值 |
|---|---|
| 中文名 | nDisplay模块化功能 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（C++模块） |
| 模块 | `DisplayClusterLightCardExtender` (Runtime), `DisplayClusterModularFeaturesEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-09-05 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplayModularFeatures) | |

## 用途

该插件为 nDisplay（Unreal Engine 的多显示器/虚拟制片解决方案）提供了一套模块化扩展框架。其核心作用是允许开发者通过实现标准接口（`IDisplayClusterLightCardActorExtender`）来扩展 `DisplayClusterLightCardActor`（灯光卡）的功能，例如为其添加自定义组件或属性，而无需直接修改引擎源码。灯光卡是 nDisplay 中用于模拟舞台灯光（如布光、遮罩）的虚拟资产。此插件将灯光卡的扩展点标准化，使得第三方或项目特定的功能（如特定的灯光效果、媒体播放、控制集成）可以作为“模块化特性”被动态加载和集成。

## 使用场景

- 你在使用 nDisplay 进行虚拟制片（Virtual Production），需要为虚拟的“灯光卡”资产添加自定义的灯光控制参数、媒体源输入或特效组件。
- 你的项目需要在 nDisplay 的 In-Camera VFX (ICVFX) 面板中集成自定义的编辑器工具或属性编辑界面。
- 你正在开发一个通用的 nDisplay 扩展工具包，希望以非侵入式的方式为灯光卡添加新功能。

## 蓝图用法

此插件主要为 C++ 接口，提供的蓝图可直接使用的节点较少。核心是通过 C++ 实现 `IDisplayClusterLightCardActorExtender` 接口，从而在编辑器中扩展灯光卡的细节面板和功能。结构体 `FDisplayClusterPositionalParams` 可在蓝图中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FDisplayClusterPositionalParams` | 表示灯光卡在舞台空间中的位置和旋转参数，可用于设置或获取灯光卡的方位角、仰角等属性。 | 结构体 |

### 使用示例（蓝图描述）

由于此插件的主要功能通过 C++ 接口实现，蓝图用法有限。你可以在蓝图中使用 `FDisplayClusterPositionalParams` 结构体来传递或接收灯光卡的定位数据。例如，通过蓝图函数库或 Actor 组件的函数，获取一个灯光卡的当前 `FDisplayClusterPositionalParams`，并将其用于其他计算或可视化。

## C++ 用法

用法主要基于对 `IDisplayClusterLightCardActorExtender` 和 `IDisplayClusterStageActor` 接口的实现。

### 头文件引入

```cpp
#include "DisplayClusterLightCardExtender/IDisplayClusterLightCardActorExtender.h"
#include "DisplayClusterLightCardExtender/StageActor/IDisplayClusterStageActor.h"
#include "DisplayClusterLightCardExtender/StageActor/DisplayClusterPositionalParams.h"
```

### 基本用法：实现灯光卡扩展器

要创建一个新的灯光卡扩展，你需要实现 `IDisplayClusterLightCardActorExtender` 接口并将其作为模块化特性注册。

```cpp
// MyLightCardExtender.h
#pragma once
#include "DisplayClusterLightCardExtender/IDisplayClusterLightCardActorExtender.h"

class FMyLightCardExtender : public IDisplayClusterLightCardActorExtender
{
public:
    // IModularFeature 接口
    static const FName ModularFeatureName;

    // IDisplayClusterLightCardActorExtender 接口
    virtual FName GetExtenderName() const override;
    virtual TSubclassOf<UActorComponent> GetAdditionalSubobjectClass() override;
#if WITH_EDITOR
    virtual FName GetCategory() const override;
    virtual bool ShouldShowSubcategories() const override;
#endif
};
```

```cpp
// MyLightCardExtender.cpp
#include "MyLightCardExtender.h"
#include "MyCustomLightCardComponent.h" // 你自定义的组件类

const FName FMyLightCardExtender::ModularFeatureName = TEXT("MyLightCardFeature");

FName FMyLightCardExtender::GetExtenderName() const
{
    return TEXT("My Custom Light Effect");
}

TSubclassOf<UActorComponent> FMyLightCardExtender::GetAdditionalSubobjectClass()
{
    return UMyCustomLightCardComponent::StaticClass();
}

#if WITH_EDITOR
FName FMyLightCardExtender::GetCategory() const
{
    return TEXT("My Tools");
}

bool FMyLightCardExtender::ShouldShowSubcategories() const
{
    return true;
}
#endif
```

### 进阶用法：与灯光卡舞台位置交互

通过 `IDisplayClusterStageActor` 接口，可以与灯光卡的位置系统进行交互。

```cpp
// 假设你有一个指向实现了 IDisplayClusterStageActor 接口的 Actor 的指针
AActor* StageActor = ...; // 例如，一个 DisplayClusterLightCardActor
IDisplayClusterStageActor* StageActorInterface = Cast<IDisplayClusterStageActor>(StageActor);

if (StageActorInterface)
{
    // 获取当前位置参数
    FDisplayClusterPositionalParams CurrentParams = StageActorInterface->GetPositionalParams();
    
    // 修改经度和纬度
    CurrentParams.Longitude += 15.0;
    CurrentParams.Latitude = FMath::Clamp(CurrentParams.Latitude + 5.0, -90.0, 90.0);
    
    // 将修改后的参数设置回去
    StageActorInterface->SetPositionalParams(CurrentParams);
    
    // 或者，通过标准位置/旋转参数计算一个世界变换
    FTransform StageOrigin = StageActorInterface->GetOrigin();
    FTransform TargetTransform = IDisplayClusterStageActor::PositionalParamsToActorTransform(CurrentParams, StageOrigin);
    StageActorInterface->SetActorTransform(TargetTransform); // 假设它是一个AActor
}
```

## Demo 示例

一个完整的、可编译的灯光卡扩展器示例。

### 头文件 (MyDemoLightCardExtender.h)

```cpp
#pragma once

#include "CoreMinimal.h"
#include "DisplayClusterLightCardExtender/IDisplayClusterLightCardActorExtender.h"

class UDemoLightCardComponent;

class FMyDemoLightCardExtender : public IDisplayClusterLightCardActorExtender
{
public:
    static const FName ModularFeatureName;

    // IDisplayClusterLightCardActorExtender Interface
    virtual FName GetExtenderName() const override;
    virtual TSubclassOf<UActorComponent> GetAdditionalSubobjectClass() override;
#if WITH_EDITOR
    virtual FName GetCategory() const override;
    virtual bool ShouldShowSubcategories() const override;
#endif
};
```

### 源文件 (MyDemoLightCardExtender.cpp)

```cpp
#include "MyDemoLightCardExtender.h"
#include "DemoLightCardComponent.h" // 你的自定义组件

const FName FMyDemoLightCardExtender::ModularFeatureName = TEXT("DemoLightCardExtender");

FName FMyDemoLightCardExtender::GetExtenderName() const
{
    return TEXT("Demo");
}

TSubclassOf<UActorComponent> FMyDemoLightCardExtender::GetAdditionalSubobjectClass()
{
    return UDemoLightCardComponent::StaticClass();
}

#if WITH_EDITOR
FName FMyDemoLightCardExtender::GetCategory() const
{
    return TEXT("Demo Tools");
}

bool FMyDemoLightCardExtender::ShouldShowSubcategories() const
{
    return true;
}
#endif

// 在你的模块 StartupModule 中注册
void FYourModule::StartupModule()
{
    // ... 其他初始化代码
    FMyDemoLightCardExtender* Extender = new FMyDemoLightCardExtender();
    IModularFeatures::Get().RegisterModularFeature(IDisplayClusterLightCardActorExtender::ModularFeatureName, Extender);
}

void FYourModule::ShutdownModule()
{
    // ... 其他清理代码
    IModularFeatures::Get().UnregisterModularFeature(IDisplayClusterLightCardActorExtender::ModularFeatureName, Extender);
    delete Extender;
}
```

## 模块依赖

要使用此插件的功能，你的模块通常需要依赖 `nDisplay` 核心插件。

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 插件的核心运行时模块，提供了灯光卡等基础类。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-09-26 | `3336c461` | [nDisplay] In-Camera VFX panel makes level dirty | 修复 ICVFX 面板导致关卡意外标记为已修改的 bug。 |
| 2024-08-01 | `1dd0608a` | nDisplay: Propagate RadialOffset changes from LC level instance to ICVFX panel proxy. | 改进灯光卡位置参数（RadialOffset）从关卡实例到 ICVFX 面板代理的同步。 |
| 2024-05-15 | `8b89d9f4` | [nDisplay] Media tiles configuration dialog for ICVFX cameras | 为 ICVFX 摄像机添加媒体分块（Tiles）配置对话框功能。 |

### 维护评价

该插件于 2022 年创建，标记为**实验性**且默认未启用。从 Git 历史看，最后一次实质性功能更新在 2024 年 8 月，最近一次改动（2025年9月）是修复一个编辑器状态相关的 bug。这表明该插件**处于维护状态，但活跃度较低**。由于其是 nDisplay 生态的一部分，且仍在接收 bug 修复，可以认为它是**稳定可用但需要谨慎对待的实验性功能**。推荐在明确需要扩展灯光卡功能时使用，但需意识到其“实验性”标签，未来 API 可能发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplayModularFeatures)
- [官方文档]() (无)