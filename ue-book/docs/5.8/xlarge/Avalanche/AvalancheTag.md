# Motion Design

> Compositing, designer and broadcasting tool.\n\nPlugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 运动设计标签 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（运行时代码） |
| 模块 | `AvalancheTag` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheTag) | |

## 用途

AvalancheTag 是 Motion Design 插件中的标签系统模块。它解决的核心问题是：在复杂的虚拟制作场景中，需要一个灵活的方式来标识和引用各种资产、效果或操作。它提供了标签标识符、标签集合、标签句柄等概念，让用户可以方便地组织和操作对象。该模块是底层标识系统，为 Motion Design 的其他功能（如克隆器/效果器、属性动画、场景修饰器等）提供统一的标签引用机制。

## 使用场景

- **在复杂的广播图形制作中**：你需要为一组摄像机、灯光或图形元素打上相同的标签，以便于后续通过一个操作（如应用效果、切换属性）同时影响所有带有该标签的对象。
- **在蓝图中引用标签**：你需要在蓝图中方便地引用、比较或检查标签，而不是直接使用硬编码的字符串或名称，以提高代码的可维护性和灵活性。
- **创建标签别名**：你需要为一组常用的标签组合定义一个别名（如 “主场景灯光”），这样在任何需要引用这组标签的地方，都可以直接使用这个别名，而不需要反复列举。
- **跨资产引用标签**：你需要一个“软引用”的机制来保存对标签的引用，这样在加载资产时可以避免不必要的依赖关系，同时也能在需要时解析到实际的标签。

## 蓝图用法

该模块提供了 `UAvaTagLibrary` 蓝图函数库，封装了常用的标签操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ResolveTagHandle` | 将一个 `FAvaTagHandle` 解析为它所代表的 `FAvaTag` 数组（一个句柄可能指向一个标签，也可能指向一个包含多个标签的别名）。 | `UAvaTagLibrary` |
| `ResolveTagHandles` | 将一个 `FAvaTagHandleContainer` 容器解析为其包含的所有 `FAvaTag` 数组。 | `UAvaTagLibrary` |
| `ResolveTagSoftHandle` | 将一个软引用的 `FAvaTagSoftHandle` 转换为硬引用的 `FAvaTagHandle`。此操作会加载引用的 `UAvaTagCollection` 资产。 | `UAvaTagLibrary` |

### 使用示例（蓝图描述）

假设你有一个 `FAvaTagHandle` 变量 `MyTagHandle`。
1. 你可以使用 `ResolveTagHandle` 节点，将 `MyTagHandle` 连接到输入，输出一个 `TArray<FAvaTag>`。然后可以遍历这个数组，获取每个标签的 `TagName` 进行打印或判断。
2. 如果你有一个 `FAvaTagHandleContainer` 变量 `TagContainer`，可以使用 `ResolveTagHandles` 节点一次性解析出容器内所有句柄指向的标签。
3. 如果你有一个 `FAvaTagSoftHandle` 变量（通常保存在资产中），在运行时需要使用时，可以调用 `ResolveTagSoftHandle` 节点将其转换为 `FAvaTagHandle`，然后就可以像使用普通句柄一样操作它。

## C++ 用法

该模块的核心类型是 `FAvaTag`（标签）、`FAvaTagId`（标签标识符）、`FAvaTagCollection`（标签集合）、`FAvaTagHandle`（标签句柄）和 `FAvaTagAlias`（标签别名）。

### 头文件引入

```cpp
#include "AvaTag.h"
#include "AvaTagId.h"
#include "AvaTagHandle.h"
#include "AvaTagCollection.h"
#include "AvaTagAlias.h"
```

### 基本用法

```cpp
// 假设你已经获取或创建了一个 UAvaTagCollection* 标签集合对象 `MyCollection`
// 以及一个 FAvaTagId `MyTagId`（通常由系统生成）

// 1. 创建一个标签句柄，用于引用 `MyCollection` 中 `MyTagId` 所代表的标签或别名
FAvaTagHandle MyHandle(MyCollection, MyTagId);

// 2. 检查句柄是否有效
if (MyHandle.IsValid())
{
    // 3. 获取句柄指向的标签列表（一个句柄可能对应多个标签，如果是别名的话）
    FAvaTagList TagList = MyHandle.GetTags();
    for (const FAvaTag* Tag : TagList)
    {
        if (Tag)
        {
            UE_LOG(LogTemp, Log, TEXT("Found Tag: %s"), *Tag->TagName.ToString());
        }
    }
}

// 4. 比较两个句柄
FAvaTagHandle AnotherHandle = ...;
// 检查它们是否指向完全相同的标签/别名（相同的源和相同的 TagId）
bool bIsExactMatch = MyHandle.MatchesExact(AnotherHandle);
// 检查它们解析后的标签集合是否有重叠
bool bOverlaps = MyHandle.Overlaps(AnotherHandle);
```

### 进阶用法

```cpp
// 使用标签句柄容器来管理多个标签句柄
FAvaTagHandleContainer HandleContainer;
HandleContainer.AddTagHandle(FaTagHandle1);
HandleContainer.AddTagHandle(FaTagHandle2);

// 检查容器是否包含某个特定的句柄（精确匹配）
bool bContainsHandle = HandleContainer.ContainsTagHandle(SomeSpecificHandle);

// 检查容器是否包含某个特定的标签（即使来自不同的句柄）
bool bContainsTag = HandleContainer.ContainsTag(HandleToCheck);

// 解析容器内所有句柄对应的标签
TArray<FAvaTag> AllResolvedTags = HandleContainer.ResolveTags();

// 使用标签别名（Alias）
// 在 UAvaTagCollection 中定义别名后，可以通过其 FAvaTagId 创建句柄
FAvaTagHandle AliasHandle(MyCollection, AliasTagId);
// 获取别名代表的多个标签
FAvaTagList TagsFromAlias = AliasHandle.GetTags(); // 返回多个标签

// 使用软引用句柄 (FAvaTagSoftHandle)
FAvaTagSoftHandle SoftHandle(TSoftObjectPtr<UAvaTagCollection>(MyCollectionPath), MyTagId);
// 在需要时将其转换为硬引用句柄（会触发集合资产加载）
FAvaTagHandle HardHandle = SoftHandle.MakeTagHandle();
```

## Demo 示例

以下示例展示了如何在代码中创建一个简单的标签集合并使用标签句柄。

**MyTagManager.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "AvaTagHandle.h"
#include "AvaTagCollection.h"
#include "MyTagManager.generated.h"

UCLASS()
class UMyTagManager : public UObject
{
    GENERATED_BODY()

public:
    // 初始化标签集合
    void InitializeTagCollection();

    // 创建并返回一个标签句柄
    UFUNCTION(BlueprintCallable, Category = "My Tags")
    FAvaTagHandle CreateHandleForTag(FName InTagName);

private:
    UPROPERTY()
    TObjectPtr<UAvaTagCollection> TagCollection;
};
```

**MyTagManager.cpp**
```cpp
#include "MyTagManager.h"
#include "AvaTagId.h"

void UMyTagManager::InitializeTagCollection()
{
    // 创建一个标签集合对象（通常作为资产或子对象）
    TagCollection = NewObject<UAvaTagCollection>(this, TEXT("MyCollection"));

    // 创建一些标签 ID 和对应的标签
    FAvaTagId PlayerId(EForceInit);
    FAvaTag PlayerTag;
    PlayerTag.TagName = "Player";

    FAvaTagId EnemyId(EForceInit);
    FAvaTag EnemyTag;
    EnemyTag.TagName = "Enemy";

    // 注意：实际向 TagCollection 添加标签的逻辑在 UAvaTagCollection 内部完成
    // 这里为了演示，假设我们通过某种方式（如编辑器）添加了这些标签。
    // 在运行时，通常直接引用已存在的标签集合资产。
}

FAvaTagHandle UMyTagManager::CreateHandleForTag(FName InTagName)
{
    if (!TagCollection)
    {
        return FAvaTagHandle();
    }

    // 假设我们有一种方式根据标签名找到对应的 TagId（在示例中，实际需要遍历或建立映射）
    // 这里简化为直接使用一个假设的 ID。在真实场景中，TagId 通常来自资产数据。
    TArray<FAvaTagId> AllIds = TagCollection->GetTagIds(false); // 获取所有非别名的 TagId
    for (const FAvaTagId& Id : AllIds)
    {
        FName FoundName = TagCollection->GetTagName(Id);
        if (FoundName == InTagName)
        {
            // 找到了对应的标签，创建并返回句柄
            return FAvaTagHandle(TagCollection, Id);
        }
    }

    return FAvaTagHandle(); // 未找到，返回无效句柄
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将 Motion Design 相关的编辑器面板归类到独立分组中。 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 为 Rundown 页面设置增加了 MRQ 分析功能。 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 为播出控制工具栏添加了页面加载选项，并增加了相关功能。 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 增加了项目设置，可强制禁用 Text3D 和形状的碰撞。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 优化了视口客户端关联/断开关联时的通知逻辑。 |

### 维护评价

**活跃维护**。该模块（及整个 Motion Design 插件）在 2025 年 5 月创建，时间不到一年，属于较新的功能。从 git 历史看，至 2026 年 5 月仍有持续的功能性更新和优化，表明 Epic Games 正在积极开发和维护此插件。作为 Motion Design 虚拟制作工具链的核心标识系统，它预计将得到长期支持。目前没有发现废弃迹象，适合在项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheTag)
- 官方文档（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Tests) (相关测试位于插件的 Tests 目录下)