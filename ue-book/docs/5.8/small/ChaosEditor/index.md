# ChaosEditor

> Destruction Tools

| 属性 | 值 |
|---|---|
| 中文名 | 混沌编辑器 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `FractureEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-06-08 |
| 年龄标签 | 🏛️ 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosEditor) | |

## 用途

ChaosEditor 是一个编辑器工具插件，它为 Unreal Engine 的 Chaos 物理破坏系统提供了一套完整的几何体集合（Geometry Collection）破碎、编辑和可视化工具集。该插件的核心价值在于，它为美术和设计师提供了一个在编辑器内交互式创建、预览和编辑实时破坏效果的“破碎模式”（Fracture Editor Mode）。它解决了从原始网格体生成可控的破碎层级、优化碰撞体积、管理材质以及配置物理模拟属性等一系列复杂问题，是构建基于 Chaos 系统的物理破坏内容的核心创作工具。

## 使用场景

- **建筑/环境破坏**：你需要为一栋建筑或一面墙壁制作可被物理模拟破坏的破碎效果 → 使用 ChaosEditor 中的 Voronoi 破碎、切片、砖块等工具将静态网格体转换为几何体集合，并调整破碎层级。
- **精确控制破坏碎片**：你希望破碎后的碎片大小、形状或断裂模式符合特定设计需求（如制作解谜游戏中的特定断裂点）→ 使用自定义 Voronoi、网格切割等工具来精确控制破碎模式。
- **优化物理模拟**：几何体集合破碎后，你需要优化其凸包碰撞形状以提高物理模拟性能和稳定性 → 使用凸包工具（Convex Tool）来调整、简化或删除凸包。
- **管理破碎材质**：破碎后，你需要为断裂面指定内部材质，或将已有的静态网格体材质正确分配到几何体集合的各个面上 → 使用材质工具（Materials Tool）进行批量分配和调整。

## 蓝图用法

ChaosEditor 的主要功能通过编辑器中的“破碎模式”工具栏进行交互，其核心 API（如 `FFractureEditorModeToolkit`、`UFractureToolCutterBase` 等）主要是 C++ 类，未暴露为蓝图可调用的节点。所有操作均在编辑器模式下通过工具栏按钮和细节面板参数完成。

## C++ 用法

虽然该插件主要通过编辑器模式 UI 操作，但其核心逻辑可以通过 C++ 访问，用于扩展或自动化工具链。

### 头文件引入

```cpp
#include "FractureEditor/FractureToolContext.h"
#include "FractureEditor/FractureTool.h"
#include "FractureEditor/FractureEditorMode.h"
```

### 基本用法

通过 `FFractureToolContext` 来获取和操作当前选中的几何体集合及其骨骼选择。

```cpp
// 假设已经处于破碎编辑器模式并选中了某个几何体集合组件
// 来源: 概念源自 FractureToolContext.h

// 1. 获取当前选中的几何体集合组件
TSet<UGeometryCollectionComponent*> SelectedComponents;
FFractureToolContext::GetSelectedGeometryCollectionComponents(SelectedComponents);

// 2. 为第一个选中的组件创建工具上下文
if (SelectedComponents.Num() > 0)
{
    UGeometryCollectionComponent* Comp = *SelectedComponents.CreateConstIterator();
    FFractureToolContext Context(Comp);

    // 3. 检查当前选择并执行一些操作
    if (Context.IsValid())
    {
        // 获取当前选中的骨骼索引
        const TArray<int32>& SelectedBones = Context.GetSelection();
        UE_LOG(LogTemp, Log, TEXT("当前选中 %d 个骨骼"), SelectedBones.Num());

        // 将选择限制为叶节点（最细碎的碎片）
        Context.ConvertSelectionToLeafNodes();
        
        // 获取几何体集合数据
        TSharedPtr<FGeometryCollection, ESPMode::ThreadSafe> GeometryCollection = Context.GetGeometryCollection();
        if (GeometryCollection.IsValid())
        {
            // 可以在此访问几何体集合的顶点、面片等数据
        }
    }
}
```

### 进阶用法

结合背景任务工具，在后台线程执行耗时的破碎或凸包计算操作，避免阻塞编辑器。

```cpp
// 来源: 概念源自 FractureToolBackgroundTask.h
#include "FractureEditor/FractureToolBackgroundTask.h"

// 创建一个自定义的几何体集合操作（例如一个简化的凸包生成操作）
class FMyCustomGeometryOp : public UE::Fracture::FGeometryCollectionOperator
{
public:
    FMyCustomGeometryOp(const FGeometryCollection& Source) : FGeometryCollectionOperator(Source) {}
    
    virtual FGeometryCollection Compute() override
    {
        // 在后台线程中执行耗时的几何体操作
        // ... 生成凸包等 ...
        
        // 将结果存储在 CollectionCopy 中
        CollectionCopy->AddAttribute(...);
        
        return *CollectionCopy; // 返回处理后的几何体集合
    }
};

// 启动一个可取消的后台任务
void StartBackgroundFracture(FGeometryCollection& GeometryCollection)
{
    auto Op = MakeUnique<FMyCustomGeometryOp>(GeometryCollection);
    
    // 启动任务，并获取一个用于轮询和取消的执行器
    TUniquePtr<UE::Fracture::TBackgroundOpExecuter<FMyCustomGeometryOp>> BackgroundTask = 
        UE::Fracture::StartBackgroundTask(MoveTemp(Op));
    
    // 在编辑器的 Tick 中轮询任务状态（通常在一个工具类的 OnTick 中）
    // UE::Fracture::TickBackgroundTask(BackgroundTask, bCancel, SuccessCallback);
}
```

## Demo 示例

一个演示如何通过 C++ 创建工具上下文并检查选择的简单示例。

**MyFractureTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "FractureEditor/FractureToolContext.h"

class FMyFractureTool
{
public:
    void AnalyzeSelection();
};
```

**MyFractureTool.cpp**
```cpp
#include "MyFractureTool.h"
#include "GeometryCollection/GeometryCollectionComponent.h"

void FMyFractureTool::AnalyzeSelection()
{
    // 获取所有选中的几何体集合组件
    TSet<UGeometryCollectionComponent*> GeomComps;
    FFractureToolContext::GetSelectedGeometryCollectionComponents(GeomComps);

    for (UGeometryCollectionComponent* Comp : GeomComps)
    {
        if (!Comp) continue;

        // 为每个组件创建一个上下文
        FFractureToolContext Context(Comp);
        if (!Context.IsValid()) continue;

        UE_LOG(LogTemp, Log, TEXT("正在分析组件: %s"), *Comp->GetName());
        UE_LOG(LogTemp, Log, TEXT("  选中骨骼数: %d"), Context.GetSelection().Num());
        UE_LOG(LogTemp, Log, TEXT("  组件边界范围: %s"), *Context.GetWorldBounds().ToString());

        // 获取几何体集合资产
        UGeometryCollection* FracturedAsset = Context.GetFracturedGeometryCollection();
        if (FracturedAsset)
        {
            UE_LOG(LogTemp, Log, TEXT("  关联的几何体集合资产: %s"), *FracturedAsset->GetName());
        }
    }
}
```

## 模块依赖

从插件的依赖项分析，使用者（通常是其他编辑器插件或工具）需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `FractureEditor` | 本插件提供的核心破碎编辑器模式和工具类 |
| `GeometryCollectionPlugin` | 提供 `GeometryCollection` 和 `GeometryCollectionComponent` 的核心类型 |
| `PlanarCut` | 提供平面切割（Planar Cut）破碎方法的底层实现 |
| `MeshModelingToolsetExp` | 提供交互式工具（如变换 Gizmo）的底层支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下双精度常量截断为浮点数产生的编译警告。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了 32 位与 64 位格式说明符不匹配的问题。 |
| 2026-04-14 | `eaf81cf6` | Add new fracture mode utility to split islands | 在破碎模式中新增了用于分离独立网格岛屿的实用工具。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到 UE_LOGF，以支持新的日志格式化功能。 |
| 2026-04-06 | `3e98cc7e` | TLazyObjectPtr Deprecation pt 3: | TLazyObjectPtr 废弃计划的第三部分更新。 |

### 维护评价

ChaosEditor 插件自 2019 年创建以来，一直处于活跃维护状态。从最近的 Git 提交记录可以看出，它仍在持续接收功能更新（如新增岛屿分离工具）、错误修复（编译警告、格式化问题）和代码现代化工作（如日志宏迁移）。尽管它被标记为“实验性”（`IsBetaVersion=true`），并且位于 `Experimental` 目录下，但其长期且持续的更新历史表明它是一个成熟且至关重要的 Chaos 物理破坏内容创作工具。**推荐使用**，但需注意其“实验性”标签可能意味着 API 在未来版本中仍有变动的可能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosEditor)
- [官方文档]() （无）