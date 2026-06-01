# Motion Design

> Compositing, designer and broadcasting tool.
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动效设计 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（基础框架） |
| 模块 | `Avalanche` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime) ... |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche 并非一个单一功能的插件，而是一个庞大的**Motion Design（动效设计）集成框架与工具集**。它解决的是在虚幻引擎中进行专业级动态图形（Motion Graphics）、直播包装、虚拟场景动态化设计时工作流零散、效率低下的问题。

其核心价值在于：
1.  **整合工作流**：将场景树管理、属性动画、克隆特效、材质设计、形状生成、文本处理、遮罩、远程控制、媒体输出等数十个子系统整合到一个统一的框架下。
2.  **提供专用工具**：为设计师提供类似传统Motion Design软件（如After Effects）的直观编辑环境（如Viewport工具、Sequencer集成、专门的大纲视图）。
3.  **优化输出管线**：通过集成Movie Render Queue (MRQ) 等功能，支持高质量的离线渲染和实时广播输出。

从源码结构看，它是一个xlarge级别的插件，包含超过40个模块，涵盖了从运行时核心（AvalancheCore）、编辑器工具（AvalancheEditor）、各类特效（Effectors、Modifiers、Shapes）到特定领域功能（Media、Sequence、Transition）的完整技术栈。

## 使用场景

-   **你是一名动效设计师**，需要在虚幻引擎中制作复杂的动态图形、UI动画或产品展示 → 使用Avalanche的整个工具集。
-   **你正在制作直播包装或虚拟演播室节目**，需要实时控制场景元素的动画、切换画面和输出 → 使用AvalancheMedia、AvalancheSequence和AvalancheSequencer模块。
-   **你需要为大型虚拟制作项目创建可程序化控制的动态场景** → 使用AvalancheSceneTree管理场景结构，配合AvalanchePropertyAnimator和AvalancheRemoteControl实现参数化驱动。
-   **你需要高级的克隆、阵列、置换等特效** → 使用AvalancheEffectors模块。
-   **你需要一个节点式的材质和动画设计环境** → 使用AvalancheMaterial和AvalancheAttribute模块。

## 蓝图用法

由于Avalanche规模巨大，此处仅以 `AvalancheSceneTree` 子模块为例，展示其场景树管理相关的蓝图接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Root Node` | 获取场景树的根节点 | `UAvaSceneTreeBlueprintLibrary` |
| `Find Tree Node` | 通过 `FAvaSceneItem` 查找对应的树节点 | `UAvaSceneTreeBlueprintLibrary` |
| `Get Child Actors` | 获取指定父Actor在场景树中的所有子Actor | `UAvaSceneTreeBlueprintLibrary` |
| `Get Root Actors` | 获取指定关卡中场景树的所有根Actor | `UAvaSceneTreeBlueprintLibrary` |
| `Sort Items` | 按照树节点的顺序对场景项进行排序 | `UAvaSceneTreeBlueprintLibrary` |

### 使用示例（蓝图描述）

假设你有一个Avalanche场景树，并希望获取名为 `BG_Parent` 的Actor的所有子Actor：
1.  使用 `Find Actor Node` 或类似方法，通过Actor引用获取其对应的 `FAvaSceneItem`。
2.  调用 `Get Child Actors` 节点，将上一步获取的 `FAvaSceneItem` 作为 `InParentItem` 输入。
3.  节点的输出即为该父Actor在场景树结构下的所有直接子Actor的数组。
4.  你可以对这个数组进行后续的动画、特效操作。

## C++ 用法

`AvalancheSceneTree` 模块的核心是 `FAvaSceneTree`、`FAvaSceneItem` 和 `FAvaSceneTreeNode` 这三个结构体，它们共同定义和管理了场景的层次化数据。

### 头文件引入

```cpp
#include "AvaSceneTree.h"
```

### 基本用法

```cpp
// 来源: Public/AvaSceneTree.h, Public/AvaSceneItem.h

// 1. 创建一个场景项 (Scene Item)
// 从UObject创建
FAvaSceneItem ItemFromActor(MyActor, nullptr); // Outer为nullptr，使用对象自身路径
// 从字符串创建
FAvaSceneItem ItemFromString(TEXT("Some.Custom.Path"));

// 2. 使用场景树管理项
FAvaSceneTree MySceneTree;
// 假设ParentItem是某个已存在的父项
FAvaSceneTreeNode& NewNode = MySceneTree.GetOrAddTreeNode(ItemFromActor, ParentItem);

// 3. 查找与遍历
FAvaSceneTreeNode* FoundNode = MySceneTree.FindTreeNode(ItemFromActor);
if (FoundNode && FoundNode->IsValid())
{
    int32 ParentGlobalIndex = FoundNode->GetParentIndex();
    TConstArrayView<int32> ChildrenIndices = FoundNode->GetChildrenIndices();
    // 可以使用GlobalIndex从MySceneTree.GetSceneItemCount()和GetItemAtIndex获取实际数据
}

// 4. 解析对象（性能优化）
MySceneTree.ResolveObjects(MyWorld); // 填充对象到节点的映射
const FAvaSceneTreeNode* FastNode = MySceneTree.FindObjectTreeNode(MyActor, MyWorld);
```

### 进阶用法

```cpp
// 来源: Public/AvaSceneTree.h, AvaSceneTreeNode.h

// 1. 树结构分析
TArray<const FAvaSceneTreeNode*> NodesToAnalyze = {NodeA, NodeB};
const FAvaSceneTreeNode* LCA = FAvaSceneTree::FindLowestCommonAncestor(NodesToAnalyze);
if (LCA)
{
    int32 Height = LCA->CalculateHeight();
    // Height表示从该节点到最深叶子节点的边数
}

// 2. 路径查找
const FAvaSceneTreeNode* SourceNode = /* ... */;
const FAvaSceneTreeNode* TargetNode = /* ... */;
TArray<const FAvaSceneTreeNode*> PathFromSource = TargetNode->FindPath({SourceNode});

// 3. 确定性排序
if (!MySceneTree.IsSorted())
{
    MySceneTree.SortItems(); // 内部基于树节点顺序
}
// 排序后，GetItemAtIndex返回的顺序将反映场景树的层级结构。
```

## Demo 示例

以下示例展示如何在代码中创建一个简单的场景树结构。

**MyAvalancheTreeActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "AvaSceneTree.h" // 包含场景树头文件
#include "MyAvalancheTreeActor.generated.h"

UCLASS()
class AMyAvalancheTreeActor : public AActor
{
	GENERATED_BODY()
public:
	AMyAvalancheTreeActor();

	virtual void BeginPlay() override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Avalanche")
	FAvaSceneTree SceneTree;
};
```

**MyAvalancheTreeActor.cpp**
```cpp
#include "MyAvalancheTreeActor.h"
#include "AvaSceneItem.h" // 需要包含来构造FAvaSceneItem

AMyAvalancheTreeActor::AMyAvalancheTreeActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyAvalancheTreeActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建两个子Actor的引用（假设在关卡中已放置）
    AActor* Child1 = /* 通过SpawnActor或FindActor获取 */;
    AActor* Child2 = /* 通过SpawnActor或FindActor获取 */;

    if (Child1 && Child2)
    {
        // 为本Actor创建根项
        FAvaSceneItem RootItem(this, nullptr);

        // 为子Actor创建项，并指定本Actor为父项
        FAvaSceneItem ChildItem1(Child1, nullptr);
        FAvaSceneItem ChildItem2(Child2, nullptr);

        // 将项添加到树中，并建立父子关系
        SceneTree.GetOrAddTreeNode(ChildItem1, RootItem);
        SceneTree.GetOrAddTreeNode(ChildItem2, RootItem);

        // 解析对象以便快速查找
        SceneTree.ResolveObjects(GetWorld());

        // 验证
        const FAvaSceneTreeNode* RootNode = SceneTree.FindTreeNode(RootItem);
        if (RootNode)
        {
            UE_LOG(LogTemp, Log, TEXT("Root node has %d children."), RootNode->GetChildrenIndices().Num());
        }
    }
}
```

## 模块依赖

作为整个Avalanche框架的核心场景树管理模块，`AvalancheSceneTree` 自身依赖相对简单。

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准Core/Engine/Slate等） | 基础的结构体定义和序列化。 |

**注意**：要使用完整的Avalanche功能，你的项目需要启用 `Avalanche` 主插件，它会处理其庞大的依赖网络（如 Remote Control, Text3D, Media Compositing 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将动效设计相关编辑器面板（场景设置、大纲视图）移动到独立的编辑器组中，优化界面组织。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 为使用节目单(Rundown)页面设置时添加了电影渲染队列(MRQ)分析功能。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在演出控制工具栏中添加了页面加载选项（全部、下一个、选定），并新增相关功能。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增项目设置，可强制禁用3D文本和形状的碰撞。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 优化视口代码，通过在客户端关联或断开关联时进行通知来减少冗余代码。 |

### 维护评价

- **活跃维护**：`Avalanche` 是Epic Games官方开发的重磅产品，从提交记录看，在文档生成时间点（2026年5月）前后保持着非常高频的更新，几乎每天都有功能提交。
- **创建时间新**：插件于2025年5月正式从实验性阶段迁移至虚拟制作核心目录，非常年轻。
- **推荐使用**：这是官方推荐的、面向专业Motion Design和虚拟制作的解决方案。虽然功能庞大、学习曲线陡峭，但对于目标应用场景，它是目前引擎内最完整、最集成的工具链。建议有相关需求的项目积极采用，并关注其快速迭代带来的新功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档]() (待 Epic 发布)
- [测试用例]() (大部分测试可能位于模块内部或引擎测试目录)