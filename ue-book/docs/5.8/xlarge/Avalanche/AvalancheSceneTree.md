# Avalanche Scene Tree

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 场景树 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AvalancheSceneTree` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheSceneTree) | |

## 用途

`AvalancheSceneTree` 模块是 `Motion Design` (Avalanche) 插件的核心数据结构组件之一。它为 Motion Graphics (MGFX) 和虚拟制片工作流提供了一个独立的、可序列化的**场景对象树**结构。

该模块解决的核心问题是：在复杂的动态图形场景中，需要高效地管理和查询大量对象（如文本、形状、克隆体、效果器等）的**父子关系和层级顺序**。传统的 Actor/Component 层级虽然强大，但对于 MGFX 工作流来说可能过于繁重或难以灵活控制。`AvalancheSceneTree` 提供了一个轻量级的、专门设计的树状结构，用于表示和操作这些对象之间的视觉和逻辑关系，支持快速查找、排序、遍历和公共祖先计算等操作。

## 使用场景

-   你正在使用 Motion Design (Avalanche) 插件制作电视节目包装、赛事直播图形或虚拟演播室内容 → 需要 `AvalancheSceneTree` 来管理图形元素的层级。
-   你需要在蓝图或 C++ 中程序化地查询某个 MGFX 元素的所有子元素或父元素 → 使用 `GetChildActors` 或 `GetRootActors` 等函数。
-   你需要在编辑器或运行时对 MGFX 对象列表进行稳定排序 → 使用 `SortItems` 和树节点的索引信息。

## 蓝图用法

该模块的 `FAvaSceneTree` 结构体暴露了一些用于查询的蓝图函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Child Actors` | 获取指定父 Actor 在场景树中的所有子 Actor。 | `FAvaSceneTree` |
| `Get Root Actors` | 获取指定关卡中所有位于场景树根部的 Actor。 | `FAvaSceneTree` |
| `Get Scene Item Count` | 获取树中场景项（FAvaSceneItem）的总数。 | `FAvaSceneTree` |
| `Sort Items` | 根据树节点的顺序对内部的场景项列表进行排序。 | `FAvaSceneTree` |

### 使用示例（蓝图描述）

1.  获取一个 `FAvaSceneTree` 结构体（通常从管理 MGFX 场景的上下文或组件中获取）。
2.  拖拽其输出引脚，搜索并添加 `Get Root Actors` 节点，指定当前 `ULevel*`，即可获得场景树中所有根级别的 Actor 列表。
3.  对于列表中的任意一个 `AActor*`，可以将其连接到另一个 `FAvaSceneTree` 的 `Get Child Actors` 节点的 `InParentActor` 输入，从而获得它的子级 Actor 列表。
4.  连接 `Sort Items` 节点，可以在遍历或发送事件前确保元素顺序与视觉层级一致。

## C++ 用法

`AvalancheSceneTree` 模块的核心是 `FAvaSceneTree` 和 `FAvaSceneItem` 结构体。`FAvaSceneItem` 是树中每个节点的唯一标识，`FAvaSceneTree` 管理这些节点的层级关系。

### 头文件引入

```cpp
#include “AvaSceneTree.h”
#include “AvaSceneItem.h”
```

### 基本用法

以下代码片段展示了如何操作场景树。

```cpp
// 1. 创建一个场景项，以 UObject*（如 AActor*）和其 Outer（通常是 UWorld*）作为标识
UObject* MyActor = /* ... */;
UObject* MyOuter = MyActor->GetWorld();
FAvaSceneItem ActorItem(MyActor, MyOuter);

// 2. 向树中添加节点（通常由系统内部完成，此处演示接口）
FAvaSceneTree SceneTree;
// 添加节点时，InParentItem 指定其父节点项
FAvaSceneTreeNode& NewNode = SceneTree.GetOrAddTreeNode(ActorItem, ParentItem);

// 3. 查找特定场景项对应的树节点
FAvaSceneTreeNode* FoundNode = SceneTree.FindTreeNode(ActorItem);

// 4. 获取某个父节点的所有子 Actor
AActor* ParentActor = /* ... */;
TArray<AActor*> Children = SceneTree.GetChildActors(ParentActor);

// 5. 在进行序列化或解析后，调用此方法以构建内部对象映射，加速查找
SceneTree.ResolveObjects(MyOuter);

// 6. 现在可以使用基于 UObject* 的快速查找
const FAvaSceneTreeNode* FoundNodeFast = SceneTree.FindObjectTreeNode(MyActor, MyOuter);
```

**注意**：`ResolveObjects` 方法会根据 `FAvaSceneItem` 的 `IdType`（如 `ObjectPath`）来尝试将 `FString` 路径解析为实际的 `UObject*`，并建立映射表。之后使用 `FindObjectTreeNode` 进行查找会比 `FindTreeNode` 更高效。

### 进阶用法：排序与路径查找

```cpp
// 假设我们有一组需要排序和比较顺序的树节点指针
TArray<const FAvaSceneTreeNode*> NodesToSort;
// ... 填充 NodesToSort ...

// 1. 对整个树的内部项列表进行排序（基于树节点索引）
if (!SceneTree.IsSorted())
{
    SceneTree.SortItems();
}

// 2. 比较两个节点的顺序（用于 UI 列表排序）
bool bAIsBeforeB = FAvaSceneTree::CompareTreeItemOrder(NodeA, NodeB);

// 3. 查找一组节点的最低公共祖先
const FAvaSceneTreeNode* CommonAncestor = FAvaSceneTree::FindLowestCommonAncestor(NodesToSort);
if (CommonAncestor && CommonAncestor->IsValid())
{
    int32 AncestorIndex = CommonAncestor->GetGlobalIndex();
    // 对公共祖先进行操作...
}

// 4. 从一个节点向上查找路径到多个目标节点
TArray<const FAvaSceneTreeNode*> TargetNodes;
// ... 填充 TargetNodes ...
TArray<const FAvaSceneTreeNode*> PathFromNodeToRoot = SomeNode->FindPath(TargetNodes);
```

## Demo 示例

以下是一个最小的控制台应用示例（非实际 UE 模块，用于演示 API 使用逻辑）。

```cpp
// DemoSceneTree.cpp
#include <iostream>
#include “AvaSceneTree.h”
#include “AvaSceneItem.h”

// 假设存在一个简单的 UObject 模拟
struct FMyObject {
    FString Name;
    FMyObject* Outer = nullptr;
    FString GetPathName(const FMyObject* StopOuter) const {
        if (StopOuter == Outer) return Name;
        return Outer->GetPathName(StopOuter) + “.” + Name;
    }
};

int main() {
    // 模拟创建对象层级
    FMyObject World; World.Name = “World”;
    FMyObject ActorA; ActorA.Name = “A”; ActorA.Outer = &World;
    FMyObject ActorB; ActorB.Name = “B”; ActorB.Outer = &World;
    FMyObject ActorC; ActorC.Name = “C”; ActorC.Outer = &ActorA;

    FAvaSceneTree Tree;
    // 为每个对象创建场景项（注意：示例中 InStopOuter 使用 World）
    FAvaSceneItem ItemA(&ActorA, &World);
    FAvaSceneItem ItemB(&ActorB, &World);
    FAvaSceneItem ItemC(&ActorC, &World);
    FAvaSceneItem RootItem(&World, nullptr); // 根节点

    // 构建树结构：A 和 B 是根节点的子节点，C 是 A 的子节点
    Tree.GetOrAddTreeNode(ItemA, RootItem);
    Tree.GetOrAddTreeNode(ItemB, RootItem);
    Tree.GetOrAddTreeNode(ItemC, ItemA);

    // 排序并获取根节点下的子项数量（对应子 Actor）
    Tree.SortItems();
    std::cout << “Scene Item Count: ” << Tree.GetSceneItemCount() << std::endl; // 输出 3

    // 查找 ItemC 的父节点（理论上是 ItemA）
    const FAvaSceneTreeNode* NodeC = Tree.FindTreeNode(ItemC);
    if (NodeC && NodeC->IsValid()) {
        const FAvaSceneTreeNode* ParentNode = NodeC->GetParentTreeNode();
        if (ParentNode && ParentNode->IsValid()) {
            const FAvaSceneItem* ParentItem = Tree.GetItemAtIndex(ParentNode->GetGlobalIndex());
            if (ParentItem && ParentItem->IsValid()) {
                // 可以进一步解析 ParentItem 为对象
                std::cout << “Parent of C is a valid node.” << std::endl;
            }
        }
    }

    return 0;
}
```

## 模块依赖

无特殊依赖（仅标准 Core/CoreUObject/Engine）。该模块提供核心数据结构，其他 `Avalanche` 模块（如 `AvalancheCore`、`AvalancheOutliner`）会依赖它来管理场景元素。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将 Motion Design 的编辑器面板（场景设置、大纲）移至独立的组。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 为使用“节目单页面”设置时添加了 Movie Render Queue 的分析功能。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在节目控制工具栏中添加了页面加载选项（全部、下一个、选中）。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加了项目设置，用于强制禁用 Text3D 和形状的碰撞。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口：通过通知客户端其关联或解除关联来优化必要的重复代码。 |

### 维护评价

-   **活跃维护**：插件创建于 2025 年 5 月，至今约 1 年。从最近的 git 记录看，它在 **2026 年 5 月仍保持高频率更新**，主要集中在功能增强、UI 改进和新的分析数据收集上。这表明该插件是 Epic 重点开发和维护的核心虚拟制片工具之一。
-   **推荐使用**：`AvalancheSceneTree` 作为 `Motion Design` 插件的基础数据结构，是使用该插件进行 Motion Graphics 创作不可或缺的一部分。鉴于其活跃的维护状态和重要的功能定位，**强烈推荐**需要在 Unreal Engine 中进行专业级动态图形或虚拟制片内容开发的用户学习和使用此模块。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheSceneTree)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/motion-design-in-unreal-engine) (Motion Design 整体文档)