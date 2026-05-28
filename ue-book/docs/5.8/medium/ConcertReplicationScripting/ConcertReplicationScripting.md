# Concert Replication Scripting

> Exposes Concert Replication types for scripting, e.g. in Blueprints

| 属性 | 值 |
|---|---|
| 中文名 | 协同编辑属性脚本 |
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ConcertReplicationScripting` (Runtime), `ConcertReplicationScriptingEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-12-08 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertScripting/ConcertReplicationScripting) | |

## 用途

该插件的核心作用是**将 Unreal Engine 的多人协同编辑（Concert）系统中的属性同步（Replication）功能，暴露为蓝图和脚本可调用的接口**。

在多人协同编辑会话中，参与者可以实时同步场景中的对象属性（如位置、旋转、材质参数等）。这个插件并非用于网络多人游戏中的属性复制，而是专为**编辑器内的多人协作编辑流程**设计。它解决的问题是：让开发者能够通过蓝图脚本或 C++ 代码，以编程方式查询、构建和操作用于协同编辑会话的“属性链”（Property Chain），从而实现更灵活、自动化的协同编辑工作流，例如批量设置需要同步的属性，或根据自定义逻辑过滤属性。

## 使用场景

- **自动化协同编辑设置**：在大型项目中，需要为数百个 Actor 的特定属性（如所有灯光的 Intensity 和 Color）配置同步。使用此插件，可以编写蓝图或编辑器工具，自动枚举这些属性并应用配置，无需手动逐一设置。
- **创建自定义同步过滤器**：你希望只同步某个 Actor 的一部分骨骼网格体属性（例如，只同步影响动画的骨骼变换，而忽略布料模拟的顶点数据）。可以通过此插件在蓝图中编写一个过滤器函数，精确控制哪些属性参与同步。
- **开发协同编辑扩展工具**：作为技术美术或工具程序员，你需要为团队开发一个更易于使用的协同编辑 UI，该 UI 需要动态显示特定类型 Actor 的可同步属性列表。此插件提供了获取和遍历属性链的 API，是构建此类工具的基础。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Make Property Chain By Literal Path` | 根据指定的属性路径字符串数组，为某个类创建属性链 | `UConcertReplicationBlueprintFunctionLibrary` |
| `Get All Properties` | 获取某个类中所有可用于协同复制的属性 | `UConcertReplicationBlueprintFunctionLibrary` |
| `Get Properties In` | 使用自定义过滤器函数，获取某个类中符合条件的属性 | `UConcertReplicationBlueprintFunctionLibrary` |
| `Get Child Properties` | 获取指定父属性的所有子属性 | `UConcertReplicationBlueprintFunctionLibrary` |
| `To String` | 将属性链转换为易读的字符串 | `UConcertReplicationBlueprintFunctionLibrary` |
| `Get Property String Path` | 将属性链作为字符串数组返回 | `UConcertReplicationBlueprintFunctionLibrary` |
| `Get Property From Root` | 从属性链的根开始按索引获取属性名 | `UConcertReplicationBlueprintFunctionLibrary` |
| `Get Property From Leaf` | 从属性链的叶节点开始按索引获取属性名 | `UConcertReplicationBlueprintFunctionLibrary` |
| `Is Child Of` | 检查一个属性是否是另一个属性的子属性 | `UConcertReplicationBlueprintFunctionLibrary` |
| `Is Direct Child Of` | 检查一个属性是否是另一个属性的直接子属性 | `UConcertReplicationBlueprintFunctionLibrary` |

### 使用示例（蓝图描述）

**示例1：获取所有可同步属性并打印名称**
1. 调用 `Get All Properties` 节点，输入你感兴趣的类（例如 `StaticMeshActor`）。
2. 将返回的 `TArray<FConcertPropertyChainWrapper>` 连接到一个 `ForEachLoop` 节点。
3. 在循环体中，对每个属性链调用 `To String` 节点，并通过 `Print String` 打印出来。这样你就能看到该类所有可同步的属性路径。

**示例2：手动创建特定属性路径**
1. 创建一个 `Make Literal Name Array` 节点，并填入属性路径，例如 `["StaticMeshComponent", "RelativeLocation", "X"]`。
2. 调用 `Make Property Chain By Literal Path` 节点，将目标类（如 `StaticMeshActor`）和上一步创建的数组作为输入。
3. 返回的 `FConcertPropertyChainWrapper` 即代表该特定属性（StaticMeshComponent的X坐标），可用于后续的同步设置操作。

**示例3：使用自定义过滤器获取属性**
1. 创建一个自定义函数，输入为 `FConcertPropertyChainWrapper`，返回布尔值。在函数内实现你的过滤逻辑（例如，只保留路径中包含 “Color” 的属性）。
2. 调用 `Get Properties In` 节点，输入目标类和你创建的函数。
3. 返回的数组将只包含通过你自定义过滤器的属性链。

## C++ 用法

### 头文件引入

```cpp
#include "ConcertReplicationBlueprintFunctionLibrary.h"
#include "ConcertPropertyChainWrapper.h"
#include "ConcertPropertyChainWrapperContainer.h"
```

### 基本用法

从头文件中提取的示例，展示如何查询和使用属性链包装器。

```cpp
// 假设你要查询 AStaticMeshActor 的所有可同步属性
TSubclassOf<UObject> ActorClass = AStaticMeshActor::StaticClass();

// 1. 获取所有属性
TArray<FConcertPropertyChainWrapper> AllProperties = 
    UConcertReplicationBlueprintFunctionLibrary::GetAllProperties(ActorClass);

// 2. 遍历并打印属性路径
for (const FConcertPropertyChainWrapper& PropertyWrapper : AllProperties)
{
    FString PropertyPathStr = 
        UConcertReplicationBlueprintFunctionLibrary::ToString(PropertyWrapper);
    UE_LOG(LogTemp, Log, TEXT("Syncable Property: %s"), *PropertyPathStr);
    
    // 获取路径的字符串数组形式
    const TArray<FName>& PathComponents = 
        UConcertReplicationBlueprintFunctionLibrary::GetPropertyStringPath(PropertyWrapper);
    // PathComponents 可能为 ["StaticMeshComponent", "RelativeLocation", "Z"]
}

// 3. 手动创建一个特定的属性链
TArray<FName> ManualPath = { TEXT("StaticMeshComponent"), TEXT("RelativeLocation"), TEXT("X") };
FConcertPropertyChainWrapper SpecificProperty;
bool bSuccess = UConcertReplicationBlueprintFunctionLibrary::MakePropertyChainByLiteralPath(
    ActorClass, ManualPath, SpecificProperty);

if (bSuccess)
{
    // SpecificProperty 现在代表 StaticMeshComponent->RelativeLocation->X 这个属性
    // 可以将其用于 Concert 的复制设置中
}
```

### 进阶用法

结合 `FConcertPropertyChainWrapperContainer` 和自定义逻辑。

```cpp
// 假设我们有一个容器，用于存储需要同步的属性
FConcertPropertyChainWrapperContainer SyncPropertiesContainer;

// 我们想要为 APointLight 类只同步强度（Intensity）和颜色（Color）属性
TSubclassOf<UObject> LightClass = APointLight::StaticClass();

// 获取所有属性，然后过滤
TArray<FConcertPropertyChainWrapper> AllLightProps = 
    UConcertReplicationBlueprintFunctionLibrary::GetAllProperties(LightClass);

for (const FConcertPropertyChainWrapper& Prop : AllLightProps)
{
    // 将属性链转为字符串用于匹配
    FString PropString = UConcertReplicationBlueprintFunctionLibrary::ToString(Prop);
    if (PropString.Contains(TEXT("Intensity")) || PropString.Contains(TEXT("Color")))
    {
        // 将符合条件的属性添加到容器中
        SyncPropertiesContainer.PropertyChains.Add(Prop);
    }
}

// 现在 SyncPropertiesContainer 中包含了我们筛选出的属性链
// 它可以直接作为参数传递给 Concert 复制系统的相关函数
```

## Demo 示例

```cpp
// MyReplicationFilter.h
#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "ConcertPropertyChainWrapper.h"
#include "MyReplicationFilter.generated.h"

UCLASS()
class UMyReplicationFilter : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    // 一个自定义的属性过滤器，用于蓝图
    UFUNCTION(BlueprintCallable, Category = "Concert|Replication")
    static TArray<FConcertPropertyChainWrapper> GetPropertiesForSync(TSubclassOf<UObject> ActorClass);
};
```

```cpp
// MyReplicationFilter.cpp
#include "MyReplicationFilter.h"
#include "ConcertReplicationBlueprintFunctionLibrary.h"

TArray<FConcertPropertyChainWrapper> UMyReplicationFilter::GetPropertiesForSync(TSubclassOf<UObject> ActorClass)
{
    if (!ActorClass) return {};

    // 获取所有属性
    TArray<FConcertPropertyChainWrapper> AllProperties = 
        UConcertReplicationBlueprintFunctionLibrary::GetAllProperties(ActorClass);

    TArray<FConcertPropertyChainWrapper> FilteredProperties;
    
    // 自定义过滤逻辑：例如，我们只想要包含“Transform”或“Color”的属性
    for (const FConcertPropertyChainWrapper& Prop : AllProperties)
    {
        const TArray<FName>& Path = 
            UConcertReplicationBlueprintFunctionLibrary::GetPropertyStringPath(Prop);
        
        for (const FName& Component : Path)
        {
            if (Component.ToString().Contains(TEXT("Transform")) || 
                Component.ToString().Contains(TEXT("Color")))
            {
                FilteredProperties.Add(Prop);
                break; // 找到匹配就跳出内层循环，处理下一个属性
            }
        }
    }

    return FilteredProperties;
}
```

## 模块依赖

该插件旨在为其他模块提供脚本接口，其自身依赖主要集中在底层的协同编辑框架。

| 模块 | 用途 |
|---|---|
| `Concert` | 提供底层协同编辑会话管理的核心功能。 |
| `ConcertSharedCore` | 提供协同编辑中共享的数据类型和基础结构，如 `FConcertPropertyChain`。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数的编译警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 `UE_LOG` 宏迁移到新的 `UE_LOGF` 宏。 |
| 2024-06-03 | `c394e7b8` | Refactor FPropertyData to contain the objects for which the properties are being displayed. IPropert... | 重构了 `FPropertyData` 以包含显示属性所对应的对象（提交信息不完整，但意在改进属性数据结构）。 |
| 2024-05-01 | `a2b56134` | Slate: Deprecate SListView::ItemHeight and STreeViewItemHeight. ItemHeight and ItemWidth are only us... | Slate 框架废弃了 `SListView::ItemHeight` 和 `STreeViewItemHeight`（提交信息不完整，但这是引擎范围的 UI 改动，可能影响了此插件的编辑器 UI 部分）。 |
| 2024-04-11 | `33250188` | Refactor replication UI in preparation of matrix view: ... | 重构复制 UI 以为矩阵视图做准备（提交信息不完整，但表明其编辑器 UI 部分在持续演进）。 |

### 维护评价

该插件相对年轻（约2年），创建于2023年底。从提交历史看，**目前仍在持续维护中**。
- **优点**：
    - 作为 Epic 官方的协同编辑工具链的一部分，有持续的内部使用和开发需求，因此长期支持有保障。
    - 近期的提交（2026年）主要是编译器警告修复和宏迁移，属于常规维护，表明代码在跟随引擎主线发展。
    - 前期（2024年）有多次针对其编辑器 UI 的重构，说明其功能在不断优化。
- **注意点**：
    - 它是一个**运行时（Runtime）模块**，但其主要使用者是编辑器内的工具和蓝图。这意味着即使你的游戏是单机的，打包后也可能包含此模块（除非你手动禁用），但通常不会产生运行时开销。
    - 其 `EnabledByDefault` 为 `false`，意味着在新的工程中需要手动启用该插件。
- **推荐使用**：如果你正在开发需要多人协同编辑 UE 场景的工具或工作流，**强烈推荐**使用此插件提供的 API 来构建自动化脚本，它能极大提升效率并减少手动错误。对于普通的游戏开发，除非你需要扩展编辑器内的协同编辑功能，否则无需关心此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertScripting/ConcertReplicationScripting)
- [官方文档]() (无)
- [测试用例]() (未在插件目录内提供)