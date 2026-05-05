# Concert Replication Scripting

> Exposes Concert Replication types for scripting, e.g. in Blueprints

| 属性 | 值 |
|---|---|
| 分类 | Networking |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ConcertReplicationScripting` (Runtime), `ConcertReplicationScriptingEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2023-12-08 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertScripting/ConcertReplicationScripting) | |

## 用途

Concert Replication Scripting 是 UE5 Multi-User Editing (Concert) 系统中专门用于**将 Replication 属性链暴露给蓝图脚本**的插件。它解决的核心问题是：在 Concert 多用户编辑会话中，属性复制（Replication）系统的数据结构（如 `FConcertPropertyChain`）是纯 C++ 类型，无法直接在蓝图中操作。此插件通过封装 `FConcertPropertyChainWrapper` 结构体和提供 `UConcertReplicationBlueprintFunctionLibrary`，让蓝图用户可以：

- 查询某个 UClass 中所有可复制的属性路径
- 手动构造属性链路径（通过字符串数组）
- 获取子属性、判断属性层级关系
- 在编辑器 Details 面板中通过下拉菜单可视化选择属性

该插件本质上是 Concert Replication 系统的**蓝图友好包装层**，不提供独立的网络功能，而是为更高层的 Concert 工具（如多用户属性同步配置）提供脚本化接口。

## 使用场景

- 你在开发基于 Concert 的多用户编辑工具，需要在蓝图中动态查询或设置属性复制路径
- 你需要为编辑器编写自定义的属性选择 UI，让用户从下拉菜单中选择要同步的属性
- 你在构建自动化管线，需要以编程方式枚举某个 Actor 类的所有可复制属性
- 你需要在蓝图中比较两个属性路径的父子关系，用于筛选逻辑

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MakePropertyChainByLiteralPath` | 通过字符串数组路径构造属性链，失败返回 false | `UConcertReplicationBlueprintFunctionLibrary` |
| `GetPropertiesIn` | 获取指定类中所有通过过滤器的可复制属性 | `UConcertReplicationBlueprintFunctionLibrary` |
| `GetAllProperties` | 获取指定类中所有可复制属性 | `UConcertReplicationBlueprintFunctionLibrary` |
| `GetChildProperties` | 获取某个属性的所有子属性，可选仅直接子属性 | `UConcertReplicationBlueprintFunctionLibrary` |
| `ToString` | 将属性链转换为可读字符串 | `UConcertReplicationBlueprintFunctionLibrary` |
| `GetPropertyStringPath` | 获取属性路径字符串数组，如 `["RelativeLocation", "X"]` | `UConcertReplicationBlueprintFunctionLibrary` |
| `GetPropertyFromRoot` | 从根属性方向按索引获取路径中的属性名 | `UConcertReplicationBlueprintFunctionLibrary` |
| `GetPropertyFromLeaf` | 从叶子属性方向按索引获取路径中的属性名 | `UConcertReplicationBlueprintFunctionLibrary` |
| `IsChildOf` | 判断一个属性是否是另一个属性的子属性（任意深度） | `UConcertReplicationBlueprintFunctionLibrary` |
| `IsDirectChildOf` | 判断一个属性是否是另一个属性的直接子属性 | `UConcertReplicationBlueprintFunctionLibrary` |

### 蓝图类型

| 类型 | 显示名 | 说明 |
|---|---|---|
| `FConcertPropertyChainWrapper` | Concert Property Chain | 单个属性链，包裹 `FConcertPropertyChain` |
| `FConcertPropertyChainWrapperContainer` | Concert Property Chain Container | 属性链数组容器，支持 Details 自定义 |

### 使用示例（蓝图描述）

**获取 Actor 的所有可复制属性**：

1. 创建一个 `Get All Properties` 节点，`Class` 引脚连接 `AActor` 类引用
2. 输出 `TArray<FConcertPropertyChainWrapper>` 即为该类所有可同步属性
3. 遍历数组，用 `To String` 打印每个属性路径

**手动构造属性路径**：

1. 创建 `Make Property Chain By Literal Path` 节点
2. `Class` 连接 `AActor` 类引用
3. `Path to Property` 连接一个字符串数组，例如 `["RelativeLocation", "X"]`
4. 成功时 `Result` 输出有效的 `FConcertPropertyChainWrapper`

**使用自定义委托过滤属性**：

1. 创建 `Get Properties In` 节点
2. `Filter` 引脚连接自定义事件/函数，签名：`bool(FConcertPropertyChainWrapper)` → 返回 `true` 表示包含该属性
3. 例如：只返回叶子属性（不含子属性的属性）

## C++ 用法

### 头文件引入

```cpp
#include "ConcertReplicationBlueprintFunctionLibrary.h"
#include "ConcertPropertyChainWrapper.h"
#include "ConcertPropertyChainWrapperContainer.h"
```

### 基本用法

从蓝图函数库的静态方法可以直接调用，也可以操作底层的 `FConcertPropertyChainWrapper` 结构体。

```cpp
// 获取 AActor 的所有可复制属性
TArray<FConcertPropertyChainWrapper> AllProperties =
    UConcertReplicationBlueprintFunctionLibrary::GetAllProperties(AActor::StaticClass());

// 手动构造属性路径
FConcertPropertyChainWrapper Result;
TArray<FName> Path = { "RelativeLocation", "X" };
bool bSuccess = UConcertReplicationBlueprintFunctionLibrary::MakePropertyChainByLiteralPath(
    AActor::StaticClass(), Path, Result);

if (bSuccess)
{
    FString Str = UConcertReplicationBlueprintFunctionLibrary::ToString(Result);
    // Str = "RelativeLocation.X"
}
```

### 进阶用法

```cpp
// 获取特定属性的子属性
FConcertPropertyChainWrapper ParentProp;
TArray<FName> ParentPath = { "RelativeLocation" };
UConcertReplicationBlueprintFunctionLibrary::MakePropertyChainByLiteralPath(
    AActor::StaticClass(), ParentPath, ParentProp);

// 获取所有子属性（递归）
TArray<FConcertPropertyChainWrapper> Children =
    UConcertReplicationBlueprintFunctionLibrary::GetChildProperties(
        ParentProp, AActor::StaticClass(), false);

// 仅获取直接子属性
TArray<FConcertPropertyChainWrapper> DirectChildren =
    UConcertReplicationBlueprintFunctionLibrary::GetChildProperties(
        ParentProp, AActor::StaticClass(), true);

// 判断属性关系
FConcertPropertyChainWrapper ChildTest;
TArray<FName> ChildPath = { "RelativeLocation", "X" };
UConcertReplicationBlueprintFunctionLibrary::MakePropertyChainByLiteralPath(
    AActor::StaticClass(), ChildPath, ChildTest);

bool bIsChild = UConcertReplicationBlueprintFunctionLibrary::IsChildOf(ChildTest, ParentProp);      // true
bool bIsDirect = UConcertReplicationBlueprintFunctionLibrary::IsDirectChildOf(ChildTest, ParentProp); // true

// 使用过滤器获取属性
FPropertyChainPredicate Filter;
Filter.BindLambda([](const FConcertPropertyChainWrapper& Prop) -> bool
{
    // 只要叶子属性（路径长度为 1）
    return UConcertReplicationBlueprintFunctionLibrary::GetPropertyStringPath(Prop).Num() == 1;
});
TArray<FConcertPropertyChainWrapper> LeafProps =
    UConcertReplicationBlueprintFunctionLibrary::GetPropertiesIn(AActor::StaticClass(), Filter);
```

## Demo 示例

以下是一个最小的自定义编辑器工具示例，使用此插件枚举属性并打印结果。

### Build.cs

```csharp
using UnrealBuildTool;

public class MyReplicationTool : ModuleRules
{
    public MyReplicationTool(ReadOnlyTargetRules Target) : base(Target)
    {
        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "ConcertReplicationScripting"  // 依赖此插件
        });
    }
}
```

### MyReplicationTool.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "ConcertPropertyChainWrapper.h"
#include "MyReplicationTool.generated.h"

UCLASS(BlueprintType)
class UMyReplicationTool : public UObject
{
    GENERATED_BODY()

public:
    /** 列出指定类的所有可复制属性 */
    UFUNCTION(BlueprintCallable, Category = "Replication Tool")
    static TArray<FString> ListReplicatableProperties(TSubclassOf<UObject> Class);

    /** 查找属性路径 */
    UFUNCTION(BlueprintCallable, Category = "Replication Tool")
    static bool FindPropertyPath(TSubclassOf<UObject> Class, const TArray<FName>& Path, FString& OutString);
};
```

### MyReplicationTool.cpp

```cpp
#include "MyReplicationTool.h"
#include "ConcertReplicationBlueprintFunctionLibrary.h"

TArray<FString> UMyReplicationTool::ListReplicatableProperties(TSubclassOf<UObject> Class)
{
    TArray<FString> Result;
    TArray<FConcertPropertyChainWrapper> Props =
        UConcertReplicationBlueprintFunctionLibrary::GetAllProperties(Class);

    for (const FConcertPropertyChainWrapper& Prop : Props)
    {
        Result.Add(UConcertReplicationBlueprintFunctionLibrary::ToString(Prop));
    }
    return Result;
}

bool UMyReplicationTool::FindPropertyPath(TSubclassOf<UObject> Class, const TArray<FName>& Path, FString& OutString)
{
    FConcertPropertyChainWrapper Result;
    if (UConcertReplicationBlueprintFunctionLibrary::MakePropertyChainByLiteralPath(Class, Path, Result))
    {
        OutString = UConcertReplicationBlueprintFunctionLibrary::ToString(Result);
        return true;
    }
    return false;
}
```

## 模块依赖

### Runtime 模块 (`ConcertReplicationScripting`)

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `ConcertSyncCore` | Concert 复制核心，提供 `FConcertPropertyChain` 和 `PropertyChainUtils` |
| `ConcertTransport` | (私有) 提供 `LogConcert` 日志类别 |

### Editor 模块 (`ConcertReplicationScriptingEditor`)

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `Slate` / `SlateCore` | UI 框架，用于自定义属性编辑器控件 |
| `ConcertReplicationScripting` | Runtime 模块，提供核心类型 |
| `ConcertSyncCore` | Concert 复制核心 |
| `InputCore` | (私有) 输入系统 |
| `PropertyEditor` | (私有) 属性编辑器自定义框架 |
| `UnrealEd` | (私有) 编辑器工具 |
| `ConcertTransport` | (私有) 日志 |
| `ConcertSharedSlate` | (私有) Concert 共享 UI 组件 |

### Plugin 依赖

| 插件 | 用途 |
|---|---|
| `ConcertSharedSlate` | Concert 共享 Slate UI 组件 |
| `ConcertSyncCore` | Concert 同步核心，提供复制数据结构 |

## 编辑器 UI 自定义

Editor 模块提供了两个关键的 Details 面板自定义：

- **`FConcertPropertyCustomization`**：为 `FConcertPropertyChainWrapper` 类型提供下拉选择 UI（`SConcertPropertyChainCombo`），用户可以从类的可复制属性中选择一个
- **`FConcertPropertyContainerCustomization`**：为 `FConcertPropertyChainWrapperContainer` 类型提供类似的下拉选择 UI

两者共享一个 `FClassRememberer` 实例，缓存用户上次选择的 UClass，避免每次都要重新选择。编辑器中使用 `FConcertPropertyChainWrapper` 或 `FConcertPropertyChainWrapperContainer` 类型的 UPROPERTY 时，Details 面板会自动显示友好的属性选择下拉菜单。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2024-06-03 | `c394e7b8` | Refactor FPropertyData to contain the objects for which the properties are being displayed. IPropertyTreeView to accept |
| 2024-05-01 | `a2b56134` | Slate: Deprecate SListView::ItemHeight and STreeViewItemHeight（全局 Slate 变更，非本插件专属） |
| 2024-04-11 | `33250188` | Refactor replication UI in preparation of matrix view: Introduced IPropertyAssignmentView |

### 维护评价

- **创建时间**：2023 年 12 月，相对较新
- **最近更新**：2024 年 6 月，最近一次实质性更新距今约 2 年
- **代码规模**：约 26 个源文件，代码量适中
- **功能稳定性**：模块 Startup/Shutdown 为空实现，核心逻辑集中在蓝图函数库和编辑器自定义中，结构清晰
- **维护状态**：维护不活跃。最近 3 次 commit 主要是 UI 重构和 Slate 框架级变更（非本插件功能更新），自 2024 年中以来无实质性功能更新
- **已知限制**：`ShortName` 注释中提到使用了缩短模块名（`CS`/`CSE`）以避免 200 字符路径限制，这是一个已知的工程权衡
- **推荐使用**：✅ 推荐。作为 Concert 系统的蓝图接口层，功能稳定且必要。如果你在使用 Multi-User Editing 并需要脚本化操作复制属性，这是唯一的官方接口

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertScripting/ConcertReplicationScripting)
- [ConcertSyncCore 源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertSync)
- [ConcertScripting 父插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertScripting)
