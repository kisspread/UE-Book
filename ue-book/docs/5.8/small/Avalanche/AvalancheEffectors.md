# Motion Design

> Compositing, designer and broadcasting tool.
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 运动设计工具 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（Motion Design 核心资产、工具） |
| 模块 | `Avalanche` (Runtime), `AvalancheCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheMedia` (Runtime), ... （共43个模块） |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche（内部代号，对外名称为 **Motion Design**）是 UE5 中一个庞大的、专为**虚拟制作 (Virtual Production) 和广播**打造的综合性运动图形 (Motion Graphics) 设计与实时合成工具集。它不同于面向游戏的传统开发插件，旨在解决影视、电视、直播和 XR 制作中对于高效、实时、可编程的动态图形、场景编排和播出控制的需求。

该插件通过一套完整的工具链，让设计师和工程师能在编辑器中直接创建、编辑、预览和播出复杂的 2D/3D 运动图形序列，并与 Sequencer、Media Framework、远程控制等核心系统深度集成。

## 使用场景

- **虚拟制作与XR直播**：在虚拟演播室或 LED 墙场景中，实时生成、更新和播出动态字幕、LOGO动画、节目包装元素。
- **Motion Graphics 设计**：直接在 UE 编辑器中设计复杂的图形动画序列，替代部分传统后期合成软件的工作流。
- **广播与节目播出**：管理多页（Page）的播出内容，通过工具栏控制页面的加载、切换，并集成了 Media Render Queue (MRQ) 进行高质量帧渲染和输出。
- **场景编排与特效**：利用克隆器（Cloner）、效应器（Effector）、修改器（Modifier）等工具，高效地创建大量重复或程序化变化的动画效果。

## 蓝图用法

Motion Design 插件暴露了大量蓝图接口，以下按功能分组列出核心节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddCloner` / `SetClonerSettings` | 在指定 Actor 上添加或配置克隆器组件，用于生成阵列对象。 | `UClonerComponent` |
| `AddEffector` / `SetEffectorSettings` | 添加或配置效应器组件，用于影响克隆器生成的对象（如缩放、旋转、位移）。 | `UEffectorComponent` |
| `AddMotionModifier` | 为组件（如StaticMesh、Text3D）添加运动修改器（如振荡、路径跟随）。 | `UAvaComponentModifier` |
| `SetPage` / `GetPages` | 在节目播出中设置或获取当前激活的页面。 | `UAvaShowPageSubsystem` |
| `RemoteControlSetPropertyValue` | 通过远程控制接口，从蓝图或外部应用设置场景中属性的值。 | `URemoteControlPreset` |

### 使用示例（蓝图描述）

1.  **创建克隆阵列**：从 `Cloner` 类拖出节点，连接到目标网格体 Actor。通过 `Set Cloner Settings` 节点设置网格体数量、分布形状（网格、圆形、沿路径）和间距。可将一个 `Effector` Actor 连接到克隆器，通过 `Effector` 的位置和参数控制阵列的动画变化。
2.  **管理播出页面**：在 UI 蓝图中，获取 `Show Page Subsystem`。调用 `Set Page` 节点并传入页面名称或索引，可切换当前播出的内容页。监听 `On Page Loaded` 事件来触发加载完成后的逻辑。

## C++ 用法

### 头文件引入

根据要使用的具体模块引入对应的头文件。例如，使用效应器模块：

```cpp
#include "AvalancheEffectors/Cloner/ICEClonerSceneTreeCustomResolver.h"
```

### 基本用法

Motion Design 的核心功能通过其组件和子系统暴露。以下示例展示了如何为自定义的克隆器实现一个场景树解析器。

```cpp
// MyCustomSceneTreeResolver.h
#pragma once
#include "AvalancheEffectors/Cloner/ICEClonerSceneTreeCustomResolver.h"

class AActor;
class ULevel;

class FMyCustomSceneTreeResolver : public ICEClonerSceneTreeCustomResolver
{
public:
    explicit FMyCustomSceneTreeResolver(ULevel* InLevel) : LevelWeak(InLevel) {}
    virtual ~FMyCustomSceneTreeResolver() override = default;

    // ICEClonerSceneTreeCustomResolver 接口实现
    virtual void Activate() override { /* 在此注册事件监听 */ }
    virtual void Deactivate() override { /* 在此注销事件监听 */ }
    virtual bool GetDirectChildrenActor(AActor* InActor, TArray<AActor*>& OutActors) const override
    {
        // 自定义如何获取某个 Actor 的子 Actor 列表
        // 例如，忽略某些类型的子 Actor，或从其他数据源获取
        // 默认实现通常基于 Actor 的 Attachment 层级
        return false;
    }
    virtual FOnActorHierarchyChanged::RegistrationType& OnActorHierarchyChanged() override
    {
        return OnHierarchyChangedDelegate;
    }

private:
    FOnActorHierarchyChanged OnHierarchyChangedDelegate;
    TWeakObjectPtr<ULevel> LevelWeak;
};
```

### 进阶用法

结合远程控制与程序化场景生成。

```cpp
// 在某个管理类中
#include "AvalancheRemoteControl/Public/RemoteControlModule.h"
#include "AvalancheCore/Public/AvaSubsystem.h"

void UMySceneGenerator::GenerateDynamicGraphics()
{
    // 1. 使用 AvalancheCore 子系统管理场景对象
    UAvaSubsystem* AvaSubsystem = UAvaSubsystem::Get(GetWorld());
    if (AvaSubsystem)
    {
        // 通过 Avalance 的 Outliner 或 SceneTree 管理 Actor
    }

    // 2. 通过远程控制接口批量更新材质参数
    if (URemoteControlPreset* Preset = GetMyRemoteControlPreset())
    {
        FRemoteControlPreset::FPropertyId PropertyId = Preset->GetExposedPropertyIdByName(TEXT("Color"));
        if (PropertyId != FRemoteControlPreset::InvalidPropertyId)
        {
            FLinearColor NewColor = FLinearColor::Red;
            Preset->SetPropertyValue(PropertyId, NewColor);
        }
    }
}
```

## Demo 示例

一个最小的、利用 `AvalancheEffectors` 模块接口的自定义场景树解析器实现。

```cpp
// MyClonerResolver.h
#pragma once
#include "AvalancheEffectors/Cloner/ICEClonerSceneTreeCustomResolver.h"

class ULevel;

class FMyClonerResolver : public ICEClonerSceneTreeCustomResolver
{
public:
    explicit FMyClonerResolver(ULevel* InLevel);
    virtual ~FMyClonerResolver() override;

    //~ ICEClonerSceneTreeCustomResolver Interface
    virtual void Activate() override;
    virtual void Deactivate() override;
    virtual bool GetDirectChildrenActor(AActor* InActor, TArray<AActor*>& OutActors) const override;
    virtual FOnActorHierarchyChanged::RegistrationType& OnActorHierarchyChanged() override;
    //~ End ICEClonerSceneTreeCustomResolver Interface

private:
    FOnActorHierarchyChanged OnHierarchyChangedDelegate;
    TWeakObjectPtr<ULevel> LevelWeak;
};

// MyClonerResolver.cpp
#include "MyClonerResolver.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"

FMyClonerResolver::FMyClonerResolver(ULevel* InLevel)
    : LevelWeak(InLevel)
{
}

FMyClonerResolver::~FMyClonerResolver()
{
    Deactivate();
}

void FMyClonerResolver::Activate()
{
    // 此处可绑定到 ULevel 或 UWorld 的 Actor 添加/删除事件，以通知层级变化
    // 例如：LevelWeak->OnActorSpawned.AddRaw(this, &FMyClonerResolver::HandleActorSpawned);
}

void FMyClonerResolver::Deactivate()
{
    // 解除所有事件绑定
}

bool FMyClonerResolver::GetDirectChildrenActor(AActor* InActor, TArray<AActor*>& OutActors) const
{
    // 实现自定义的子 Actor 检索逻辑
    // 例如：只返回带有特定 Tag 的子 Actor
    if (InActor)
    {
        InActor->GetAttachedActors(OutActors, /*bResetArray=*/ true);
        // 过滤逻辑...
    }
    return true;
}

FOnActorHierarchyChanged::RegistrationType& FMyClonerResolver::OnActorHierarchyChanged()
{
    return OnHierarchyChangedDelegate;
}
```

## 模块依赖

`AvalancheEffectors` 模块及其相关模块依赖于许多 Epic 自有的高级模块。以下是不常见的、与本插件功能直接相关的依赖：

| 模块 | 用途 |
|---|---|
| `ClonerEffector` | 核心的克隆器与效应器功能实现。 |
| `GeometryCache` | 处理几何体缓存动画。 |
| `RemoteControl` | 提供远程控制属性和函数的能力。 |
| `ActorModifierCore` | Actor 修改器系统的核心框架。 |
| `Text3D` | 提供 3D 文本生成和动画功能。 |
| `SVGImporter` | 支持导入 SVG 文件并转换为可用于 Motion Design 的资产。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own group | 将运动设计的编辑器选项卡（场景设置、大纲视图）移动到独立的分组中，优化UI布局。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 为节目单页面设置了使用 Media Render Queue 时的分析事件，用于数据追踪。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and added corresponding MRQ command line options | 在节目控制工具栏中增加了页面加载选项（全部、下一个、选定），并添加了相应的 MRQ 命令行参数。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加了项目设置选项，用于强制禁用 Text3D 和形状的碰撞检测。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated with a viewport. | （底层视口优化）通过通知客户端其与视口的关联状态变化，重构了相关代码。 |

### 维护评价

**活跃维护**。Motion Design 插件于 **2025 年 5 月**从实验区迁移到正式的 Virtual Production 插件目录，标志着其稳定性和重要性得到官方认可。从最近的 git 记录来看（截至 2026 年 5 月），更新非常频繁，几乎每周都有功能增强、UI 优化和新特性（如 MRQ 分析、页面加载选项）加入。这表明该插件是 Epic 在虚拟制作领域的重点开发项目，处于**积极活跃的维护和功能迭代状态**，非常适合用于生产环境。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档]() （暂无公开文档链接，建议参考 UE5 官方文档站搜索 “Motion Design” 或 “Virtual Production”）
- [测试用例]() （测试文件通常位于 `Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheFunctionalTest/`）