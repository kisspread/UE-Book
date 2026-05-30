# Cloners and Effectors

> Niagara based cloner system with various layouts and effector affecting each clone instances

| 属性 | 值 |
|---|---|
| 中文名 | 克隆器与效应器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、Niagara 资产、材质模板） |
| 模块 | `ClonerEffector` (Runtime), `ClonerEffectorEditor` (Runtime), `ClonerEffectorMeshBuilder` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ClonerEffector) | |

## 用途

ClonerEffector 是 Motion Design（运动设计）工具套件的核心组件，基于 Niagara 粒子系统构建。它解决的核心问题是：**高效地生成和操控大量克隆实例**。

- **Cloner（克隆器）**：将单个 Actor 或网格体按指定布局（网格 Grid、径向 Radial、曲线 Spline、线性 Line 等）复制为成百上千个实例，并支持动态更改布局参数。每个克隆实例可以拥有独立的变换、材质和生命周期。
- **Effector（效应器）**：通过空间位置和距离衰减影响克隆器中的实例，控制实例的缩放、旋转、颜色、透明度等属性。支持多种缓动曲线（Easing），可实现波浪、脉冲等视觉效果。

该插件从 `Engine/Plugins/Experimental` 迁移到 `Engine/Plugins/VirtualProduction`，说明它已达到生产可用状态，专为虚拟制片（Virtual Production）中的运动设计场景打造。

## 使用场景

- 你需要在虚拟制片场景中快速生成大量重复物体（如人群、阵列灯光、装饰物）→ 使用 Cloner
- 你需要让一组物体产生波浪式、脉冲式动画效果 → 用 Effector 驱动克隆实例的变换
- 你需要在 Sequencer 中对克隆效果进行关键帧动画 → 插件提供 Sequencer Track 集成
- 你需要按曲线路径排列物体（如沿 Spline 排列路灯）→ 使用 Spline Layout 克隆器
- 你需要在 Motion Design 工作流中控制实例级材质参数 → 克隆器支持每个实例的 MID（材质实例动态参数）

## 蓝图用法

### 核心组件

| 组件 | 说明 | 用途 |
|---|---|---|
| `UCEClonerComponent` | 克隆器组件 | 附加到 Actor 上，按布局规则生成克隆实例 |
| `UCEEffectorComponent` | 效应器组件 | 附加到 Actor 上，通过空间距离影响克隆实例属性 |

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FillClonerMenu` | 填充克隆器右键菜单 | `UCEEditorClonerSubsystem` |
| `FillEffectorMenu` | 填充效应器右键菜单 | `UCEEditorEffectorSubsystem` |

### 编辑器子系统用法

Cloner 和 Effector 各有对应的编辑器子系统，提供菜单填充和编辑器操作：

```
蓝图中获取子系统 → Call Get() → FillClonerMenu / FillEffectorMenu
```

## C++ 用法

### 头文件引入

```cpp
// Runtime 模块
#include "ClonerEffectorModule.h"

// Editor 模块
#include "CEEditorModule.h"

// 子系统
#include "Subsystems/CEEditorClonerSubsystem.h"
#include "Subsystems/CEEditorEffectorSubsystem.h"

// 菜单上下文
#include "Cloner/Menus/CEEditorClonerMenuContext.h"
#include "Effector/Menus/CEEditorEffectorMenuContext.h"
```

### 基本用法：获取编辑器子系统

克隆器和效应器各有一个编辑器子系统（`UEditorSubsystem`），用于管理编辑器侧操作。

```cpp
// 获取克隆器编辑器子系统（单例）
UCEEditorClonerSubsystem* ClonerSubsystem = UCEEditorClonerSubsystem::Get();
if (ClonerSubsystem)
{
    // 构建菜单上下文
    TSet<UObject*> SelectedObjects = /* 从编辑器选择获取 */;
    FCEEditorClonerMenuContext Context(SelectedObjects);
    
    // 检查上下文是否包含克隆器
    if (Context.ContainsAnyCloner())
    {
        // 获取已禁用的克隆器
        TSet<UCEClonerComponent*> DisabledCloners = Context.GetDisabledCloners();
    }
}

// 获取效应器编辑器子系统
UCEEditorEffectorSubsystem* EffectorSubsystem = UCEEditorEffectorSubsystem::Get();
```

### 基本用法：菜单选项配置

```cpp
#include "Cloner/Menus/CEEditorClonerMenuOptions.h"
#include "Effector/Menus/CEEditorEffectorMenuOptions.h"

// 配置克隆器菜单选项 - 启用/禁用 + 创建效应器
FCEEditorClonerMenuOptions ClonerOptions;
ClonerOptions.CreateSubMenu(true).UseTransact(true);
// 或使用枚举位标志构造
// FCEEditorClonerMenuOptions({ECEEditorClonerMenuType::Enable, ECEEditorClonerMenuType::Disable});

// 配置效应器菜单选项
FCEEditorEffectorMenuOptions EffectorOptions;
EffectorOptions.CreateSubMenu(false).UseTransact(true);
```

### 基本用法：创建 Actor 工厂

插件提供了专用的 Actor 工厂，用于在编辑器中放置 Cloner 和 Effector Actor。

```cpp
#include "Cloner/CEClonerActorFactory.h"
#include "Effector/CEEffectorActorFactory.h"

// 克隆器工厂 - 设置布局后生成
UCEClonerActorFactory* ClonerFactory = NewObject<UCEClonerActorFactory>();
ClonerFactory->SetClonerLayout(FName("Grid"));  // 设置网格布局

// 效应器工厂 - 设置类型后生成
UCEEffectorActorFactory* EffectorFactory = NewObject<UCEEffectorActorFactory>();
EffectorFactory->SetEffectorTypeName(FName("Radial"));  // 设置径向效应器
```

### 进阶用法：自定义细节面板

插件注册了多个 `IDetailCustomization` 来自定义 Details 面板显示，展示了如何扩展 Cloner/Effector 的编辑器 UI。

```cpp
// 克隆器组件细节面板自定义（已在插件内部注册）
// 显示布局选择、Sequencer 轨道创建按钮、布局相关函数按钮
class FCEEditorClonerComponentDetailCustomization : public IDetailCustomization
{
    virtual void CustomizeDetails(IDetailLayoutBuilder& InDetailBuilder) override;
};

// 效应器类型细节面板自定义 - 展示缓动曲线选择器
class FCEEditorEffectorTypeDetailCustomization : public IDetailCustomization
{
    // 缓动枚举 + 图像预览 + 下拉选择器
    void PopulateEasingInfos();
    const FSlateBrush* GetEasingImage(FName InName) const;
};
```

### 进阶用法：Sequencer 轨道集成

```cpp
#include "Cloner/Sequencer/MovieSceneClonerTrackEditor.h"

// 克隆器支持 Sequencer 动画轨道
// 通过委托监听轨道创建事件
FMovieSceneClonerTrackEditor::OnAddClonerTrack.AddLambda(
    [](const TSet<UCEClonerComponent*>& InCloners)
    {
        // 处理克隆器轨道创建
    });

// 检查轨道是否存在
uint32 TrackCount = 0;
FMovieSceneClonerTrackEditor::OnClonerTrackExists.Broadcast(MyCloner, TrackCount);
```

### 进阶用法：节流管理器

交互式编辑属性时，插件自动禁用 Slate 节流以确保视口实时预览。

```cpp
#include "CEEditorThrottleManager.h"

// 创建作用域 - 属性变更期间自动禁用 Slate 节流
{
    FCEEditorThrottleScope Scope(FName("LayoutSpacing"));
    // 在此作用域内修改属性，视口会实时更新
    // 析构时自动恢复节流
}
```

### 进阶用法：Actor 过滤拾取器

```cpp
#include "Cloner/Customizations/CEEditorClonerCustomActorPickerNodeBuilder.h"

// 自定义 Actor 拾取器 - 只显示满足条件的 Actor
FOnShouldFilterActor FilterDelegate;
FilterDelegate.BindLambda([](const AActor* InActor) -> bool
{
    // 返回 true 表示过滤掉该 Actor
    return InActor->IsA<AStaticMeshActor>() == false;
});

auto PickerBuilder = MakeShared<FCEEditorClonerCustomActorPickerNodeBuilder>(
    PropertyHandle, FilterDelegate);
```

## Demo 示例

### 最小示例：创建带效应器的克隆器 Actor

```cpp
// ClonerEffectorDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ClonerEffectorDemo.generated.h"

UCLASS()
class AClonerEffectorDemo : public AActor
{
    GENERATED_BODY()

public:
    AClonerEffectorDemo();

    virtual void BeginPlay() override;

    /** 克隆器组件 */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Cloner")
    TObjectPtr<USceneComponent> RootScene;

    /** 创建克隆器 Actor 并设置布局 */
    UFUNCTION(BlueprintCallable, Category = "Cloner|Demo")
    AActor* SpawnClonerWithLayout(FName LayoutName, FVector Location);

    /** 创建效应器 Actor 并链接到克隆器 */
    UFUNCTION(BlueprintCallable, Category = "Effector|Demo")
    AActor* SpawnEffectorForCloner(AActor* ClonerActor, FName EffectorType, FVector Location);
};
```

```cpp
// ClonerEffectorDemo.cpp
#include "ClonerEffectorDemo.h"

#include "Cloner/CEClonerActorFactory.h"
#include "Effector/CEEffectorActorFactory.h"

AClonerEffectorDemo::AClonerEffectorDemo()
{
    RootScene = CreateDefaultSubobject<USceneComponent>(TEXT("RootScene"));
    RootComponent = RootScene;
}

void AClonerEffectorDemo::BeginPlay()
{
    Super::BeginPlay();

    // 示例：在 BeginPlay 中生成克隆器和效应器
    // 实际使用中通常在编辑器中手动放置
}

AActor* AClonerEffectorDemo::SpawnClonerWithLayout(FName LayoutName, FVector Location)
{
    UCEClonerActorFactory* Factory = NewObject<UCEClonerActorFactory>();
    Factory->SetClonerLayout(LayoutName);
    
    // PostSpawnActor 会将布局应用到生成的 Actor
    // 注意：实际工厂生成流程需要通过编辑器放置系统
    return nullptr;
}

AActor* AClonerEffectorDemo::SpawnEffectorForCloner(AActor* ClonerActor, FName EffectorType, FVector Location)
{
    UCEEffectorActorFactory* Factory = NewObject<UCEEffectorActorFactory>();
    Factory->SetEffectorTypeName(EffectorType);
    
    return nullptr;
}
```

## 模块依赖

从源码分析，该编辑器模块依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `ClonerEffector` | 运行时核心模块，提供 Cloner/Effector 组件和数据 |
| `Niagara` | 粒子系统基础，克隆器基于 Niagara 实现 |
| `SequencerCore` | Sequencer 轨道编辑器集成 |
| `ToolMenus` | 编辑器右键菜单和工具栏扩展 |
| `PropertyEditor` | 细节面板自定义（IDetailCustomization） |

其他模块依赖 ClonerEffectorRuntime / Engine / Slate / UMG 等标准模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-12 | `6a7d961a` | Motion Design: fix cloner MIDs getting gc'd on save, causing the mesh renderer to have an array of d | 修复克隆器动态材质实例在保存时被 GC 导致网格渲染器数组损坏 |
| 2026-05-12 | `9d568373` | Motion Design: fixed warning logs when cloner asset isn't generated yet and failing to find a data i | 修复克隆器资产未生成时的警告日志和数据表查找失败 |
| 2026-05-12 | `adfb4114` | Motion Design: fixed cloners spawning default actors while in async loading thread. Instead, these a | 修复克隆器在异步加载线程中生成默认 Actor 的问题，改为延迟生成 |
| 2026-05-12 | `ae187efa` | Motion Design: fixed motion design scene tree returning potentially null actors. Also added null che | 修复场景树返回潜在空 Actor 的问题，增加空指针检查 |

### 维护评价

- **创建时间**：2025 年 5 月从 Experimental 迁移到 VirtualProduction，属于较新的插件
- **最近更新**：2026 年 5 月仍在活跃维护，连续修复多个运行时 bug（GC、异步加载、空指针）
- **维护状态**：🟢 **活跃维护中** — 作为 Motion Design 套件的核心组件，由 Epic 团队持续更新
- **已知问题**：近期修复的问题表明该插件仍在打磨稳定性（MID GC 问题、异步线程安全问题）
- **推荐使用**：✅ **推荐** — 已从实验性毕业到 VirtualProduction，适合虚拟制片项目使用。但作为新插件，预计还会持续迭代改进

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ClonerEffector)
- [官方文档]()（暂无）
- [测试用例]()（暂未发现独立测试文件）