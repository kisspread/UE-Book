# Chaos Cloth

> Adds Chaos Cloth modules.

| 属性 | 值 |
|---|---|
| 中文名 | Chaos 布料模拟 |
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosCloth` (Runtime), `ChaosClothEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth) | |

## 用途

ChaosCloth 是基于 Chaos 物理引擎的布料模拟插件，为骨骼网格体提供高质量的实时布料物理效果。它替代了旧版的 NvCloth 实现，使用 Chaos 物理求解器进行布料的动力学模拟，支持布料的拉伸、弯曲、碰撞等物理行为。

该插件最初位于 `Experimental` 目录下，于 2024 年 3 月正式移出实验阶段，同时废弃了独立的 ChaosCloth Editor 插件，将编辑器功能合并到本插件中。

Editor 模块提供了布料资产编辑器的扩展功能，包括：布料模拟的可视化调试绘制、属性面板中带权重贴图的数值控件自定义等。

## 使用场景

- 你在做角色服装、披风、旗帜等需要物理模拟的布料效果 → 使用 ChaosCloth
- 你需要在骨骼网格体上配置布料模拟参数（风力、重力、碰撞等） → ChaosCloth Editor 提供编辑器内可视化配置
- 你的项目需要水面交互的布料效果（如水面上的漂浮织物） → 该插件已依赖 Water 和 Buoyancy 插件
- 你希望在编辑器中实时预览布料模拟效果并进行调试绘制 → 使用 ChaosClothEditor 模块

## 蓝图用法

本插件主要提供运行时布料模拟后端和编辑器扩展，核心功能通过骨骼网格体的 Cloth 系统暴露。布料资产的创建和参数调整主要在编辑器内完成，而非通过蓝图节点直接调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 布料模拟由骨骼网格体组件自动驱动 | 布料模拟随骨骼网格体组件的 Tick 自动运行 | — |

> ChaosCloth 的主要交互通过编辑器中的布料资产编辑器和骨骼网格体组件的布料相关设置进行，而非自定义蓝图函数库。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosCloth/ChaosClothConfig.h"          // 布料配置
#include "ChaosCloth/ChaosClothSimulation.h"       // 布料模拟
```

编辑器扩展相关：

```cpp
#include "ChaosClothEditor/ChaosSimulationEditorExtender.h"
#include "ChaosClothEditor/ChaosClothEditorModule.h"
```

### 基本用法

编辑器模块会自动注册 `FSimulationEditorExtender`，为布料编辑器提供可视化调试功能。模块生命周期管理如下：

```cpp
// ChaosClothEditor 模块启动时自动注册编辑器扩展
void FChaosClothEditorModule::StartupModule()
{
    // ChaosEditorExtender 在模块启动时注册到布料编辑器系统
}

void FChaosClothEditorModule::ShutdownModule()
{
    // 模块关闭时自动清理
}
```

### 进阶用法 — 编辑器调试绘制扩展

`FSimulationEditorExtender` 实现了 `ISimulationEditorExtender` 接口，为布料编辑器视口提供调试可视化：

```cpp
// 获取支持的模拟工厂类
UClass* FSimulationEditorExtender::GetSupportedSimulationFactoryClass();

// 扩展视口的 Show 菜单，添加布料可视化选项
void FSimulationEditorExtender::ExtendViewportShowMenu(
    FMenuBuilder& MenuBuilder,
    TSharedRef<IPersonaPreviewScene> PreviewScene);

// 在视口中绘制布料模拟的调试几何信息
void FSimulationEditorExtender::DebugDrawSimulation(
    const IClothingSimulationInterface* Simulation,
    USkeletalMeshComponent* OwnerComponent,
    FPrimitiveDrawInterface* PDI);

// 在视口中绘制布料模拟的调试文本信息
void FSimulationEditorExtender::DebugDrawSimulationTexts(
    const IClothingSimulationInterface* Simulation,
    USkeletalMeshComponent* OwnerComponent,
    FCanvas* Canvas,
    const FSceneView* SceneView);
```

调试可视化通过 `TBitArray<> Flags` 管理各可视化选项的开关状态，并支持临时隐藏所有布料 Section：

```cpp
// 临时显示/隐藏网格体上所有布料 Section
void ShowClothSections(USkeletalMeshComponent* MeshComponent, bool bIsClothSectionsVisible) const;

// 根据当前启用的选项判断是否应禁用模拟
bool ShouldDisableSimulation() const;
```

## Demo 示例

### 自定义布料编辑器扩展

以下示例展示如何利用 `ISimulationEditorExtender` 接口创建一个自定义的调试可视化扩展：

```cpp
// MyClothDebugExtender.h
#pragma once

#include "ChaosSimulationEditorExtender.h"
#include "IPersonaPreviewScene.h"

class FMyClothDebugExtender : public ISimulationEditorExtender
{
public:
    virtual ~FMyClothDebugExtender() override = default;

    virtual UClass* GetSupportedSimulationFactoryClass() override;

    virtual void ExtendViewportShowMenu(
        FMenuBuilder& MenuBuilder,
        TSharedRef<IPersonaPreviewScene> PreviewScene) override
    {
        // 添加自定义调试选项到视口 Show 菜单
        MenuBuilder.AddMenuEntry(
            NSLOCTEXT("MyClothDebug", "ShowParticleIds", "Show Cloth Particle IDs"),
            NSLOCTEXT("MyClothDebug", "ShowParticleIdsTooltip", "Display particle indices on cloth mesh"),
            FSlateIcon(),
            FUIAction(
                FExecuteAction::CreateLambda([this]()
                {
                    bShowParticleIds = !bShowParticleIds;
                }),
                FCanExecuteAction(),
                FIsActionChecked::CreateLambda([this]()
                {
                    return bShowParticleIds;
                })
            ),
            NAME_None,
            EUserInterfaceActionType::ToggleButton);
    }

    virtual void DebugDrawSimulation(
        const IClothingSimulationInterface* Simulation,
        USkeletalMeshComponent* OwnerComponent,
        FPrimitiveDrawInterface* PDI) override
    {
        if (!bShowParticleIds || !Simulation || !OwnerComponent)
        {
            return;
        }

        // 在每个布料粒子位置绘制小球
        // 实际使用时需通过 Simulation 接口获取粒子位置数据
    }

    virtual void DebugDrawSimulationTexts(
        const IClothingSimulationInterface* Simulation,
        USkeletalMeshComponent* OwnerComponent,
        FCanvas* Canvas,
        const FSceneView* SceneView) override
    {
        if (!bShowParticleIds || !Simulation || !OwnerComponent)
        {
            return;
        }

        // 在每个粒子位置绘制 ID 文本
    }

private:
    bool bShowParticleIds = false;
};
```

```cpp
// MyClothDebugExtender.cpp
#include "MyClothDebugExtender.h"
#include "ChaosCloth/ChaosClothingSimulationFactory.h"

UClass* FMyClothDebugExtender::GetSupportedSimulationFactoryClass()
{
    return UChaosClothingSimulationFactory::StaticClass();
}
```

### 布师权重值属性自定义

Editor 模块通过 `FChaosClothWeightedValueCustomization` 自定义了布料属性面板中带权重贴图的数值控件。该控件在标准数学结构体自定义的基础上，将结构体成员的简短名称直接显示在表头行中：

```cpp
// 属性自定义类已内置于 ChaosClothEditor 模块
// 注册后自动应用于所有标记了权重贴图的布料属性
// 如需手动注册自定义：
#include "ChaosClothEditor/ChaosClothWeightedValueCustomization.h"

// 通过属性自定义注册系统应用
// 在模块启动时由 FChaosClothEditorModule::StartupModule() 自动完成
```

## 模块依赖

从 Build.cs 和 .uplugin 的 Plugins 依赖关系提取：

| 模块/插件 | 用途 |
|---|---|
| `ChaosCaching` | Chaos 物理缓存系统，用于布料模拟数据的缓存 |
| `Buoyancy` | 浮力系统，支持布料与水面的浮力交互 |
| `Water` | 水面系统，支持布料与水面的交互效果 |

> 本插件的 Build.cs 依赖详情未在提供的源码中展示，但根据 .uplugin 的 Plugins 字段，以上三个插件为必选前置依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 到 float 截断的编译警告 |
| 2026-04-23 | `85f3a947` | [Chaos Cloth] Clamp SolverLOD in ChaosClothingSimulationSolver to prevent out of bound crash when so | 限制 SolverLOD 值防止越界崩溃 |
| 2026-04-21 | `9322be91` | Minor cloth debug draw improvements: | 布料调试绘制的小幅改进 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到 UE_LOGF 新日志宏 |
| 2026-03-31 | `0d36bcd0` | Chaos Cloth : | Chaos 布料相关改动 |

### 维护评价

ChaosCloth 处于**活跃维护**状态。从 2024 年 3 月从 Experimental 移出后，持续有功能性更新和 bug 修复。近期（2026 年 3-5 月）连续有多次提交，涵盖崩溃修复、编译警告清理、调试绘制改进等，表明 Epic 团队仍在积极维护该模块。

作为 Chaos 物理引擎的布料解决方案，它是 UE5 官方推荐的布料模拟后端，**推荐使用**。该插件默认启用，表明 Epic 认为其已达到生产可用状态。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth)
- 官方文档（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosCloth/Tests)