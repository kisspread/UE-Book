# Motion Design Scene State

> （无描述）

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计场景状态 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、场景状态资产） |
| 模块 | `SceneState` (Runtime), `SceneStateBinding` (Runtime), `SceneStateBlueprint` (Runtime), `SceneStateBlueprintEditor` (Runtime), `SceneStateEditor` (Runtime), `SceneStateEvent` (Runtime), `SceneStateEventEditor` (Runtime), `SceneStateEventGraph` (Runtime), `SceneStateGameplay` (Runtime), `SceneStateGameplayEditor` (Runtime), `SceneStateMachineEditor` (Runtime), `SceneStateMachineGraph` (Runtime), `SceneStateTasks` (Runtime), `SceneStateTransitionGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneState) | |

## 用途

SceneState 是 UE5 虚拟制片（Virtual Production）中 **Motion Design** 工作流的场景状态管理系统。它提供了一个完整的**状态机框架**，用于驱动虚拟制片场景中的动态元素行为。

该插件的核心功能包括：

- **场景状态机（Scene State Machine）**：类似于行为树或蓝图状态机，但专为虚拟制片场景设计，管理场景中各元素的状态转换
- **数据绑定（Scene State Binding）**：将场景状态与外部数据源连接，实现数据驱动的场景动画
- **事件系统（Scene State Event）**：基于事件触发的状态转换机制
- **任务系统（Scene State Tasks）**：状态机中的具体执行逻辑单元
- **Sequencer 集成**：与 Sequencer 时间线深度集成，支持在时间线中控制场景状态

该插件原先位于 `Engine/Plugins/Experimental/` 目录下，后迁移至 `VirtualProduction/`，说明 Epic 认为其已达到可用于虚拟制片项目的成熟度，但仍标记为 Beta 版本。

## 使用场景

- 你在制作虚拟制片（VP）项目的 Motion Design 内容 → 用 SceneState 管理场景中动态元素的状态流转
- 你需要一个可视化的状态机来驱动场景中多个 Actor 的行为切换 → 用场景状态机图编辑器
- 你需要将场景状态与外部数据（如外部 API、传感器数据）绑定 → 用 SceneStateBinding
- 你需要在 Sequencer 时间线中精确控制场景状态变化 → 插件提供原生 Sequencer 集成
- 你需要基于事件（如交互、定时、数据变化）触发场景状态转换 → 用 SceneStateEvent 系统

## 蓝图用法

由于该插件主要面向编辑器和运行时混合场景，且核心逻辑在状态机图编辑器中，公开的蓝图 API 有限。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 创建场景状态 Actor | 从场景状态资产生成 Actor | `USceneStateActorFactory` |
| 场景状态对象 | 场景状态的核心运行时对象 | `USceneStateObject` |

### 使用示例（蓝图描述）

1. **创建场景状态 Actor**：在内容浏览器中选择一个场景状态资产，拖拽到视口即可自动通过 `USceneStateActorFactory` 生成对应的 Actor
2. **状态机编辑**：双击场景状态资产打开状态机图编辑器，在图形界面中定义状态节点、转换条件和绑定关系

## C++ 用法

### 头文件引入

```cpp
#include "SceneStateGameplayModule.h"
#include "SceneStateGameplayContextEditor.h"
#include "SceneStateSequencerSchema.h"
#include "SceneStateActorFactory.h"
```

### 基本用法

场景状态的 C++ 扩展主要通过编辑器模块接口实现：

```cpp
// 实现自定义的上下文编辑器
// 来源: Private/SceneStateGameplayContextEditor.h
namespace UE::SceneState::Editor
{

class FGameplayContextEditor : public IContextEditor
{
public:
    // 获取该编辑器支持的上下文对象类（如 Actor、ActorComponent）
    virtual void GetContextClasses(TArray<TSubclassOf<UObject>>& OutContextClasses) const override;
    
    // 创建上下文视图控件
    virtual TSharedPtr<SWidget> CreateViewWidget(const FContextParams& InContextParams) const override;
    
    // 为给定的 WorldContext 创建游戏视口客户端
    UGameViewportClient* CreateViewportClient(FWorldContext& InWorldContext) const;
};

} // UE::SceneState::Editor
```

### 进阶用法

Sequencer 集成是该插件的核心能力之一：

```cpp
// 实现 Sequencer Schema 以支持场景状态组件在 Sequencer 中的绑定
// 来源: Private/SceneStateSequencerSchema.h
namespace UE::SceneState::Editor
{

class FSequencerSchema : public UE::Sequencer::IObjectSchema
{
public:
    // 获取对象的父对象（用于 Sequencer 的层级导航）
    virtual UObject* GetParentObject(UObject* InObject) const override;
    
    // 判断对象与 Sequencer 的相关性
    virtual UE::Sequencer::FObjectSchemaRelevancy GetRelevancy(const UObject* InObject) const override;
    
    // 扩展 Sequencer 的对象绑定右键菜单
    virtual TSharedPtr<FExtender> ExtendObjectBindingMenu(
        TSharedRef<FUICommandList> InCommandList, 
        TWeakPtr<ISequencer> InSequencerWeak, 
        TConstArrayView<UObject*> InContextSensitiveObjects) const override;
    
    // 将场景状态组件添加到 Sequencer
    static void AddSceneStateComponents(
        TWeakPtr<ISequencer> InSequencerWeak, 
        TArray<TWeakObjectPtr<USceneStateComponent>> InComponents);
};

} // UE::SceneState::Editor
```

## Demo 示例

以下展示如何创建自定义的场景状态 Actor 工厂：

```cpp
// SceneStateActorFactory.h
#pragma once

#include "ActorFactory.h"
#include "SceneStateActorFactory.generated.h"

UCLASS()
class USceneStateActorFactory : public UActorFactory
{
    GENERATED_BODY()

public:
    USceneStateActorFactory();

    // 判断是否可以从给定资产创建 Actor
    virtual bool CanCreateActorFrom(const FAssetData& InAssetData, FText& OutErrorMessage) override;
    
    // Actor 生成后的初始化处理
    virtual void PostSpawnActor(UObject* InAsset, AActor* InNewActor) override;

private:
    // 根据资产获取对应的场景状态类
    TSubclassOf<USceneStateObject> GetSceneStateClass(UObject* InAsset) const;
};
```

```cpp
// SceneStateActorFactory.cpp
#include "SceneStateActorFactory.h"

USceneStateActorFactory::USceneStateActorFactory()
{
    // 配置工厂支持的 Actor 类型
}

bool USceneStateActorFactory::CanCreateActorFrom(const FAssetData& InAssetData, FText& OutErrorMessage)
{
    // 验证资产数据是否包含有效的场景状态对象
    if (!InAssetData.IsValid())
    {
        OutErrorMessage = NSLOCTEXT("SceneState", "InvalidAsset", "Invalid scene state asset");
        return false;
    }
    return true;
}

void USceneStateActorFactory::PostSpawnActor(UObject* InAsset, AActor* InNewActor)
{
    Super::PostSpawnActor(InAsset, InNewActor);
    // 将场景状态资产关联到新生成的 Actor
}

TSubclassOf<USceneStateObject> USceneStateActorFactory::GetSceneStateClass(UObject* InAsset) const
{
    // 根据资产类型返回对应的场景状态类
    return USceneStateObject::StaticClass();
}
```

## 模块依赖

由于该插件包含 14 个模块，依赖关系复杂。以下是各模块的主要独特依赖：

| 模块 | 用途 |
|---|---|
| `Sequencer` | 场景状态与 Sequencer 时间线的集成 |
| `StateTreeModule` | 状态机核心引擎支持 |

> 注：该插件的模块间存在大量内部依赖（SceneState → SceneStateBinding → SceneStateEvent → SceneStateTasks 等），使用单个模块时需注意引入所有必要的运行时依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联/解关联的通知机制 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退之前的提交 CL53913857 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 再次应用视口客户端通知机制重构 |
| 2026-04-17 | `6e111b5d` | Motion Design Scene State: fixed issues with bindings not checking for null event payload struct (op | 修复绑定系统未检查空事件载荷结构体的问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移至新的 UE_LOGF 宏 |

### 维护评价

**积极维护中**

- 该插件创建于 2025 年 8 月，距今约 1 年，属于较新的功能
- 最近 1 个月内有频繁更新（2026 年 5 月有多次提交），表明处于活跃开发阶段
- 更新内容包括功能重构和 Bug 修复，说明 Epic 正在积极打磨该功能
- 标记为 `IsBetaVersion = true`，属于实验性功能，API 可能发生变化
- 作为 Virtual Production Motion Design 工作流的核心组件，预计会持续维护
- **建议**：可在生产项目中小范围试用，但需关注 API 变更，不建议在大型项目中重度依赖

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneState)
- [官方文档]()（暂无）
- [测试用例]()（暂未发现独立测试目录）