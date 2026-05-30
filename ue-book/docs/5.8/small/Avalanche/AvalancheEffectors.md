# Motion Design (AvalancheEffectors 模块)

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计效果器 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AvalancheEffectors` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheEffectors) | |

## 用途

AvalancheEffectors 模块是 Motion Design 插件的**效果器系统组件**，负责将 Motion Design 的自定义 Outliner 层级结构桥接到 Cloner（克隆器）系统中。

核心功能：
- **场景树自定义解析**：实现 `ICEClonerSceneTreeCustomResolver` 接口，让 Cloner 能够读取 Motion Design 特有的 Actor 层级关系
- **层级变更监听**：监听 Motion Design Outliner 中的父子关系变化，并将这些变化通知给 Cloner 系统
- **跨系统集成**：作为 Motion Design Outliner 和 Cloner 效果器之间的桥梁，确保克隆体能够正确跟随设计层级

这个模块存在的原因是：Motion Design 使用自定义的 Actor 层级管理（而非标准的 Unreal Actor 层级），Cloner 需要一种方式来获取这个自定义层级。

## 使用场景

- 你在 Motion Design 中创建了复杂的克隆体效果 → Cloner 通过此模块感知你的自定义层级
- 你在 Motion Design Outliner 中拖拽调整 Actor 父子关系 → Cloner 实时更新克隆体的层级结构
- 你需要效果器根据 Motion Design 层级产生不同行为 → 此模块提供层级查询能力

## 蓝图用法

此模块不暴露蓝图 API，它是 Motion Design 和 Cloner 之间的内部桥接层。用户通过 Motion Design 的 Outliner 和 Cloner 组件间接使用。

### 核心节点

此模块无公开蓝图节点。功能通过以下系统间接暴露：

| 系统 | 说明 |
|---|---|
| Cloner 组件 | 使用此模块获取层级信息 |
| Motion Design Outliner | 提供层级数据源 |

## C++ 用法

此模块主要供内部使用，不推荐直接在用户代码中引用。如果需要扩展 Cloner 的层级解析能力，可参考以下接口。

### 头文件引入

```cpp
#include "AvalancheEffectorsModule.h"
```

### 基本用法

模块实现了 `ICEClonerSceneTreeCustomResolver` 接口，示例展示了该接口的基本结构：

```cpp
// 来源: Source/AvalancheEffectors/Private/AvalancheEffectorsSceneTreeResolver.h

// 自定义场景树解析器，让 Cloner 能读取 Motion Design 的 Actor 层级
class FAvalancheEffectorsSceneTreeResolver : public ICEClonerSceneTreeCustomResolver
{
public:
    explicit FAvalancheEffectorsSceneTreeResolver(ULevel* InLevel);

    // 激活解析器，开始监听层级变化
    virtual void Activate() override;
    
    // 停止解析器
    virtual void Deactivate() override;

    // 获取指定 Actor 的直接子 Actor（用于 Cloner 确定克隆体层级）
    virtual bool GetDirectChildrenActor(AActor* InActor, TArray<AActor*>& OutActors) const override;

    // 层级变更通知委托
    virtual FOnActorHierarchyChanged::RegistrationType& OnActorHierarchyChanged() override;
};
```

### 进阶用法

模块在启动时自动注册自定义解析器工厂：

```cpp
// 来源: Source/AvalancheEffectors/Private/AvalancheEffectorsModule.h

class FAvalancheEffectorsModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;   // 注册场景树解析器
    virtual void ShutdownModule() override;  // 清理解析器

protected:
    // 静态工厂方法：为指定 Level 创建场景树解析器实例
    static TSharedPtr<ICEClonerSceneTreeCustomResolver> CreateSceneTreeResolver(ULevel* InLevel);
};
```

内部层级变更监听（仅编辑器环境）：

```cpp
// 来源: Source/AvalancheEffectors/Private/AvalancheEffectorsSceneTreeResolver.h

#if WITH_EDITOR
    // 监听 Motion Design Outliner 加载完成
    void OnOutlinerLoaded();
    
    // 监听层级关系变更（Actor 被移动、父子关系改变等）
    void OnOutlinerHierarchyChanged(
        AActor* InActor, 
        const AActor* InParent, 
        EAvaOutlinerHierarchyChangeType InChange
    );
#endif
```

## Demo 示例

由于此模块是内部桥接模块，不直接面向用户编程。以下是理解其工作原理的最小示例：

```cpp
// MyCustomClonerExtension.h
#pragma once

#include "CoreMinimal.h"
#include "Cloner/CEEffectorComponent.h"

class FMyCustomHierarchyBridge
{
public:
    // 模拟 AvalancheEffectors 的核心功能：获取 Actor 的子层级
    static bool GetDirectChildrenActor(AActor* InActor, TArray<AActor*>& OutChildren)
    {
        if (!InActor || !InActor->GetLevel())
        {
            return false;
        }

        // 遍历 Level 中的所有 Actor，查找以 InActor 为父的 Actor
        ULevel* Level = InActor->GetLevel();
        for (AActor* Actor : Level->Actors)
        {
            if (Actor && Actor->GetAttachParentActor() == InActor)
            {
                OutChildren.Add(Actor);
            }
        }
        return OutChildren.Num() > 0;
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ClonerEffector` | Cloner/效果器系统核心，提供 `ICEClonerSceneTreeCustomResolver` 接口 |
| `AvalancheCore` | Motion Design 核心模块 |
| `AvalancheOutliner` | Motion Design 自定义 Outliner，提供层级数据 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将 Motion Design 标签页移至独立分组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 新增 MRQ 分析统计功能 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 新增节目控制工具栏的页面加载选项 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增强制禁用 Text3D 和形状碰撞的项目设置 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 优化视口客户端关联通知机制 |

### 维护评价

**🟢 活跃维护**

- **创建时间**：2025 年 5 月从 Experimental 迁移到 VirtualProduction
- **更新频率**：Motion Design 插件整体持续活跃开发，每周有多次提交
- **模块状态**：AvalancheEffectors 作为内部桥接模块，功能稳定，随主插件一起维护
- **注意事项**：此模块高度依赖 ClonerEffector 和 AvalancheOutliner，属于内部实现细节
- **推荐使用**：不推荐直接使用此模块，推荐通过 Motion Design UI 和 Cloner 组件间接使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheEffectors)
- [插件主页](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [ClonerEffector 模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ClonerEffector)