# Chaos Cloth

> Adds Chaos Cloth modules.

| 属性 | 值 |
|---|---|
| 中文名 | Chaos 布料 |
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosCloth` (Runtime), `ChaosClothEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth) | |

## 用途

Chaos Cloth 插件为 Unreal Engine 5 提供了基于 Chaos 物理引擎的布料模拟系统。它负责处理布料（如服装、旗帜、窗帘等）的物理计算和渲染，为角色或物体提供动态、逼真的布料效果。该插件将原先分散的布料模拟功能整合到 Chaos 物理框架下，取代了旧的布料方案。

## 使用场景

- **角色服装模拟**：为游戏角色创建逼真的飘动裙摆、披风、斗篷等动态衣物。
- **环境物体**：模拟旗帜、窗帘、桌布等场景中布料的物理运动。
- **过场动画**：在电影级过场中实现复杂的布料交互效果。
- **需要高性能物理模拟的项目**：当项目深度集成 Chaos 物理引擎并需要布料模拟时，Chaos Cloth 是官方推荐方案。

## 蓝图用法

该插件主要通过编辑器自定义和扩展来工作，直接暴露给蓝图的节点相对较少。其核心功能通常通过`UChaosClothComponent`（属于`ClothComponent`模块，非本插件提供）和编辑器内的属性面板来使用。

### 核心属性与自定义

在布料资产编辑器的属性面板中，带权重图的属性（如风力影响、刚度等）会使用由 `FChaosClothWeightedValueCustomization` 自定义的界面，允许同时编辑一个基础数值和一个可选的权重贴图，以实现精细控制。

| 功能 | 说明 | 所在类 |
|---|---|---|
| 权重图属性自定义 | 为同时拥有数值和权重图的布料属性提供统一的编辑界面 | `FChaosClothWeightedValueCustomization` |

### 编辑器视图扩展

`FSimulationEditorExtender` 为布料模拟的编辑器预览窗口添加了调试可视化选项。

| 节点/选项 | 说明 | 所在类 |
|---|---|---|
| 视图菜单扩展 | 在布料资产编辑器的“Show”菜单中添加 Chaos 布料专用的调试显示选项 | `FSimulationEditorExtender` |
| 调试绘制 | 在编辑器视口中绘制布料模拟的线框、碰撞体等调试信息 | `FSimulationEditorExtender` |

## C++ 用法

### 头文件引入

```cpp
#include "ChaosSimulationEditorExtender.h" // 用于编辑器扩展
#include "ChaosClothWeightedValueCustomization.h" // 用于自定义属性自定义
```

### 基本用法 (编辑器扩展)

`FSimulationEditorExtender` 是主要的可编程接口，用于向布料资产编辑器注入自定义的调试可视化和菜单选项。通常，你无需直接创建此对象，模块在启动时会自动注册它。

```cpp
// 源自 ChaosClothEditor/Private/ChaosClothEditorModule.cpp
// 模块启动时注册扩展器
void FChaosClothEditorModule::StartupModule()
{
    // ... 其他初始化代码 ...
    ChaosEditorExtender = Chaos::FSimulationEditorExtender();
    // 将扩展器注册到 Persona（角色编辑器）系统中
    IModularFeatures::Get().RegisterModularFeature(ISimulationEditorExtender::GetModularFeatureName(), &ChaosEditorExtender);
}

// 模块关闭时注销
void FChaosClothEditorModule::ShutdownModule()
{
    IModularFeatures::Get().UnregisterModularFeature(ISimulationEditorExtender::GetModularFeatureName(), &ChaosEditorExtender);
}
```

### 进阶用法 (自定义属性界面)

`FChaosClothWeightedValueCustomization` 继承自 `FMathStructCustomization`，用于自定义编辑器中特定结构体属性的显示方式，使其能在同一行同时显示数值滑块和权重贴图入口。

```cpp
// 通常，在编辑器模块中为特定的 UStruct 注册属性自定义。
// 这是框架行为，较少需要手动调用，但了解其接口有助于扩展或调试。
// 示例：在某个 PropertyModule 注册代码中可能看到类似逻辑
FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>(TEXT("PropertyEditor"));
// 为某个结构体（如 FChaosClothWeightedValue）注册自定义
PropertyModule.RegisterCustomPropertyTypeLayout(
    FChaosClothWeightedValue::StaticStruct()->GetFName(),
    FOnGetPropertyTypeCustomizationInstance::CreateStatic(&FChaosClothWeightedValueCustomization::MakeInstance)
);
```

## Demo 示例

以下示例展示了如何在自定义的编辑器模块中监听并响应 Chaos 布料模拟的调试绘制事件。

```cpp
// MyClothDebugModule.h
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"
#include "ISimulationEditorExtender.h"

class FMyClothDebugModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    // 实现一个自定义的编辑器扩展器
    class FMySimulationEditorExtender : public ISimulationEditorExtender
    {
    public:
        virtual UClass* GetSupportedSimulationFactoryClass() override;
        virtual void DebugDrawSimulation(const IClothingSimulationInterface* Simulation, USkeletalMeshComponent* OwnerComponent, FPrimitiveDrawInterface* PDI) override;
        // ... 其他接口实现 ...
    };

    FMySimulationEditorExtender MyExtender;
};
```

```cpp
// MyClothDebugModule.cpp
#include "MyClothDebugModule.h"
#include "ChaosClothEditor/ChaosSimulationEditorExtender.h" // 包含接口定义
#include "ClothSimData.h" // 可能包含 IClothingSimulationInterface 等

#define LOCTEXT_NAMESPACE "MyClothDebugModule"

void FMyClothDebugModule::StartupModule()
{
    // 注册我们自定义的扩展器
    IModularFeatures::Get().RegisterModularFeature(ISimulationEditorExtender::GetModularFeatureName(), &MyExtender);
}

void FMyClothDebugModule::ShutdownModule()
{
    IModularFeatures::Get().UnregisterModularFeature(ISimulationEditorExtender::GetModularFeatureName(), &MyExtender);
}

UClass* FMyClothDebugModule::FMySimulationEditorExtender::GetSupportedSimulationFactoryClass()
{
    // 声明此扩展器支持 Chaos 布料模拟工厂
    return UChaosClothSimulationFactory::StaticClass(); // 假设的类名，需根据实际代码确认
}

void FMyClothDebugModule::FMySimulationEditorExtender::DebugDrawSimulation(
    const IClothingSimulationInterface* Simulation,
    USkeletalMeshComponent* OwnerComponent,
    FPrimitiveDrawInterface* PDI)
{
    // 在这里添加自定义的调试绘制代码
    // 例如，绘制布料的边或特定碰撞体
    if (Simulation && PDI)
    {
        // 获取布料数据并绘制...
        PDI->DrawLine(FVector::ZeroVector, FVector(100, 0, 0), FLinearColor::Red, SDPG_Foreground);
    }
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyClothDebugModule, MyClothDebug)
```

## 模块依赖

根据插件元数据及模块用途，要使用此插件，你的项目或模块可能需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `ChaosCloth` | Chaos 布料模拟的核心运行时逻辑。 |
| `ClothComponent` | 提供 `UChaosClothComponent` 等具体组件，是实际在 Actor 上使用的部分。 |
| `Chaos` | Chaos 物理引擎核心。 |
| `ClothSimulationData` | 定义布料模拟数据的接口和结构。 |
| `ChaosCaching` | 用于缓存和播放布料模拟数据，插件元数据中明确依赖。 |
| `Buoyancy`, `Water` | 用于布料与水体交互的模拟，插件元数据中明确依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量转换为浮点数时产生的编译警告。 |
| 2026-04-23 | `85f3a947` | [Chaos Cloth] Clamp SolverLOD in ChaosClothingSimulationSolver to prevent out of bound crash when so... | 钳制求解器LOD级别以防止越界崩溃，提升了稳定性。 |
| 2026-04-21 | `9322be91` | Minor cloth debug draw improvements: | 对布料调试绘制进行了小幅改进。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-03-31 | `0d36bcd0` | Chaos Cloth : | Chaos 布料相关的提交（信息不完整，但表明仍在活动）。 |

### 维护评价

**活跃维护**。该插件于 2024 年 3 月从 Experimental 状态迁移至正式版本，并持续得到维护。从 Git 历史看，在 2026 年 3 月至 5 月期间仍有至少 5 次提交，内容包括错误修复、稳定性提升和代码现代化改进（如日志宏迁移）。这表明 Epic Games 的开发团队仍在积极维护此核心物理模拟模块，没有废弃迹象。作为 UE5 Chaos 物理生态系统的关键组成部分，它被推荐用于需要布料模拟的新项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth)
- 官方文档链接未提供（`DocsURL` 为空）。
- 测试用例链接未在提供的信息中明确给出，通常位于 `Engine/Plugins/ChaosCloth/Tests/` 或 `Engine/Tests/` 目录下。