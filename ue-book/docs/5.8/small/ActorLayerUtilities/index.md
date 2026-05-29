# Actor Layer Utilities

> Utilites for interacting with actor layers from blueprints（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Actor层工具集 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ActorLayerUtilities` (Runtime), `ActorLayerUtilitiesEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-10-22 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ActorLayerUtilities) | |

## 用途

这个插件为蓝图提供了操作“Actor层”（Actor Layers）的工具集。Actor层是一种用于在编辑器中逻辑分组和管理场景内Actor的系统（类似于Photoshop的图层）。此插件的核心目的是在**运行时**和**编辑器工具蓝图**中，提供一套标准化的API，以便通过蓝图查询、添加或移除Actor所属的层，从而实现基于层的批量Actor管理和逻辑筛选。

## 使用场景

- 你需要根据逻辑分组（如“敌人”、“玩家友方”、“可交互对象”）来批量管理Actor，并在运行时（如游戏逻辑）或编辑器工具中根据层进行过滤和操作。
- 你在制作一个关卡编辑器工具或数据处理工具，需要在编辑器蓝图中遍历并修改特定层内所有Actor的属性。
- 你需要一个不依赖特定Actor组件或标签的、更轻量的层级管理方案。

## 蓝图用法

此插件主要为蓝图提供功能。核心节点位于 `UBlueprintActorLayerLibrary` 工具类中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add To Actor Layer` | 向目标Actor添加一个指定的层 | `UBlueprintActorLayerLibrary` |
| `Remove From Actor Layer` | 从目标Actor移除一个指定的层 | `UBlueprintActorLayerLibrary` |
| `Is In Layer` | 检查目标Actor是否属于指定的层 | `UBlueprintActorLayerLibrary` |
| `Get Actors From Layer` | 获取属于指定层的所有Actor的数组 | `UBlueprintActorLayerLibrary` |

### 使用示例（蓝图描述）

1.  **批量添加层**：在一个For Loop中，选中多个Actor，对每个Actor调用 `Add To Actor Layer` 节点，并连接相同的 `FActorLayer` 结构体变量（可在蓝图中定义层名称）。
2.  **按层过滤执行操作**：先调用 `Get Actors From Layer` 获取目标层（如“Explosive”）的所有Actor，然后将结果传递给 `ForEachLoop`，对每个Actor执行“爆炸”逻辑。
3.  **条件检查**：在某个Actor的事件中，调用 `Is In Layer` 检查它是否属于“Invincible”层，如果是则跳过伤害计算。

## C++ 用法

底层API通过 `IActorLayerUtilities` 接口提供。通常用于开发更底层的编辑器工具或蓝图库函数。

### 头文件引入

```cpp
#include "ActorLayerUtilities.h"
```

### 基本用法

通过模块获取接口，然后使用其方法操作Actor层。
*示例来源于 `ActorLayerUtilities.Build.cs` 及接口定义推断。*

```cpp
// 获取 ActorLayerUtilities 模块的单例
FActorLayerUtilitiesModule& ActorLayerUtilitiesModule = FModuleManager::LoadModuleChecked<FActorLayerUtilitiesModule>(TEXT("ActorLayerUtilities"));
IActorLayerUtilities* ActorLayerUtilities = ActorLayerUtilitiesModule.GetActorLayerUtilities();

// 检查 Actor 是否在特定层
FActorLayer MyLayer;
MyLayer.Name = FName(TEXT("MyCustomLayer"));
bool bIsInLayer = ActorLayerUtilities->IsInLayer(SomeActor, MyLayer);

// 添加 Actor 到层
ActorLayerUtilities->AddToLayer(SomeActor, MyLayer);
```

### 进阶用法

获取某个层内的所有Actor，这在编写编辑器批量处理工具时非常有用。
*用法基于 `GetActorsFromLayer` 等公开方法。*

```cpp
// 定义目标层
FActorLayer TargetLayer;
TargetLayer.Name = FName(TEXT("BatchProcess"));

// 获取该层所有 Actor
TArray<AActor*> ActorsInLayer;
ActorLayerUtilities->GetActorsFromLayer(GetWorld(), TargetLayer, ActorsInLayer);

// 遍历处理
for (AActor* Actor : ActorsInLayer)
{
    // 对每个Actor执行自定义逻辑
    Actor->SetActorHiddenInGame(true);
}
```

## Demo 示例

一个最小化的示例，展示如何创建一个蓝图函数库，封装检查Actor是否在指定层的功能。

**ActorLayerCheckLibrary.h**
```cpp
#pragma once
#include "Kismet/BlueprintFunctionLibrary.h"
#include "ActorLayerUtilities.h"
#include "ActorLayerCheckLibrary.generated.h"

UCLASS()
class UActorLayerCheckLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Actor Layer")
    static bool IsActorInLayerByName(AActor* Actor, FName LayerName);
};
```

**ActorLayerCheckLibrary.cpp**
```cpp
#include "ActorLayerCheckLibrary.h"

bool UActorLayerCheckLibrary::IsActorInLayerByName(AActor* Actor, FName LayerName)
{
    if (!Actor) return false;

    FActorLayer Layer;
    Layer.Name = LayerName;

    // 通过全局函数访问工具接口
    IActorLayerUtilities* Utilities = IActorLayerUtilities::Get();
    return Utilities ? Utilities->IsInLayer(Actor, Layer) : false;
}
```

## 模块依赖

使用此插件的功能，你的模块（特别是Editor模块）需要依赖以下特定模块：

| 模块 | 用途 |
|---|---|
| `ActorLayerUtilities` | 提供运行时（Runtime）层操作的核心接口和蓝图库 |
| `Layer` | UE引擎的底层Actor层系统 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2023-05-15 | `da92084a` | Optimized out more private modules includes and dependencies. | 优化了头文件，移除了对私有模块的冗余包含和依赖。 |
| 2023-01-13 | `3c9aacb1` | [Engine/Plugins] | 引擎插件的通用更新（可能涉及批量修改）。 |
| 2023-01-12 | `2f78497e` | [Engine/Plugins] | 引擎插件的通用更新。 |
| 2022-10-26 | `b5b86c79` | This change is a strategical submit for a coming change that removes lots of includes in headers tha... | 为后续清理头文件包含所做的策略性提交。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 将内置插件的供应商链接更新为使用安全协议（HTTPS）。 |

### 维护评价

- **状态**: **维护不活跃**
- **分析**: 该插件功能相对简单且稳定。最近一次实质性更新（依赖优化）在2023年5月，之后近两年内只有格式化或链接类的无关紧要的提交。这表明插件已进入成熟期，核心功能不再有积极开发。
- **风险与建议**: 作为运行时/编辑器混合插件，其基础API依赖引擎的Layer系统，只要该系统存在，插件就能继续工作。**目前无明显已知问题**。对于新项目，如果需求仅限于蓝图中的基本层操作，该插件仍可使用且稳定。但如果需要更复杂或新的层管理特性，则不太可能从该插件获得更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ActorLayerUtilities)
- [官方文档]() （暂无）
- [测试用例]() （此插件目录内无专用测试用例）