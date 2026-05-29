# UObject Example Plugin

> An example of a plugin which declares its own UObject type. This can be used as a starting point when creating your own plugin.

| 属性 | 值 |
|---|---|
| 中文名 | UObject示例插件 |
| 分类 | Examples |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `UObjectPlugin` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/UObjectPlugin) | |

## 用途

该插件的核心功能是**展示如何在引擎插件模块中正确声明和定义自定义的 UObject 和 UStruct 类型**。它不是一个具有运行时功能的实用插件，而是一个纯粹的**代码模板和教程插件**。它的存在是为了给开发者提供一个标准、可编译的起点，指导他们如何组织插件目录结构、编写构建脚本以及正确使用 UnrealHeaderTool (UHT) 宏（如 `UCLASS`, `USTRUCT`, `UPROPERTY`）来定义属于插件自己的类型。

## 使用场景

- 当你需要**从零开始创建一个新的 Unreal Engine 插件**，并且计划在其中定义自定义的 `UObject` 派生类或 `UStruct` 结构体时，可以将此插件作为目录结构和代码组织的最佳实践参考。
- 在学习 Unreal Engine 插件开发的过程中，用于理解插件模块与引擎核心模块（如 `CoreUObject`）之间的依赖关系。

## 蓝图用法

由于该插件的 `UMyPluginObject` 类属性被声明为 `private`，且没有暴露任何 `BlueprintCallable` 或 `BlueprintReadWrite` 的接口，因此**没有可供直接在蓝图中使用的功能节点**。

其主要的可访问接口是模块本身：
| 节点 | 说明 | 所在类 |
|---|---|---|
| `IUObjectPlugin::IsAvailable()` | 检查 `UObjectPlugin` 模块是否已加载并可用。 | `IUObjectPlugin` |

**使用示例（蓝图描述）**：
在蓝图中，你可以通过 `Is Module Loaded` 节点来检查 `UObjectPlugin` 模块是否加载。这通常用于在尝试访问该模块定义的类型之前进行条件判断，但在实际项目中很少需要，因为该示例插件本身没有提供额外的蓝图功能。

## C++ 用法

### 头文件引入

```cpp
#include "IUObjectPlugin.h" // 用于访问模块实例
#include "MyPluginObject.h" // 用于使用示例中定义的UObject和UStruct
```

### 基本用法

从插件源码中提取的核心用法是访问模块和使用自定义类型。

```cpp
// 1. 检查并获取插件模块实例（源文件：Source/UObjectPlugin/Public/IUObjectPlugin.h）
if (IUObjectPlugin::IsAvailable())
{
    IUObjectPlugin& PluginModule = IUObjectPlugin::Get();
    // PluginModule 可用于访问模块内定义的其他功能（本示例中为空）
}

// 2. 创建和使用插件中定义的自定义UObject（源文件：Source/UObjectPlugin/Classes/MyPluginObject.h）
UMyPluginObject* MyObject = NewObject<UMyPluginObject>();
// 注意：MyPluginObject 的属性是私有的，无法直接访问。
// 它的用途主要是作为自定义UObject声明的范例。
```

### 进阶用法

结合模块检查和对象创建，构成一个完整的使用示例。

```cpp
// 确保模块加载后，安全地创建一个自定义对象
if (IUObjectPlugin::IsAvailable())
{
    // 模块可用，现在可以安全地创建插件中定义的UObject
    UMyPluginObject* ExampleObject = NewObject<UMyPluginObject>(GetTransientPackage(), TEXT("MyExampleObj"));
    if (ExampleObject)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully created an instance of UMyPluginObject."));
    }
}
else
{
    UE_LOG(LogTemp, Warning, TEXT("UObjectPlugin module is not loaded. Cannot create UMyPluginObject."));
}
```

## Demo 示例

以下是一个完整的、可编译的最小示例，演示如何在另一个模块中检查并使用 `UObjectPlugin` 插件提供的类型。

**MyActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyActor.generated.h"

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()

public:
    AMyActor();

    UFUNCTION(BlueprintCallable, Category = "Plugin Demo")
    void CheckAndCreatePluginObject();

private:
    UPROPERTY()
    class UMyPluginObject* CachedPluginObject;
};
```

**MyActor.cpp**
```cpp
#include "MyActor.h"
#include "IUObjectPlugin.h" // 依赖插件的公共接口
#include "MyPluginObject.h" // 依赖插件定义的UObject

AMyActor::AMyActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyActor::CheckAndCreatePluginObject()
{
    if (!IUObjectPlugin::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("UObjectPlugin is not available. Skipping."));
        return;
    }

    // 创建一个 UObjectPlugin 模块中定义的 UObject
    CachedPluginObject = NewObject<UMyPluginObject>(this);
    if (CachedPluginObject)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully created a UMyPluginObject from the Plugin."));
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine 等）。使用此插件或其示例代码无需额外的特殊模块依赖，它依赖的 `CoreUObject` 是任何包含 `UObject` 的模块的基础。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-07-10 | `abb369e2` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied to all plugins.) | 为所有具有对应 .gen.cpp 的源文件添加了内联宏，属于全引擎范围的代码规范性更新。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 对引擎插件目录进行维护性调整。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新插件内链接为安全协议，属于维护性改动。 |
| 2019-12-27 | `28d3d740` | (Integrating from Dev-EngineMerge to Main) | 从开发分支合并到主线，无具体功能说明。 |
| 2019-09-02 | `e7f83a71` | Convert all remaining “Developer” modules to “UncookedOnly”, to preserve existing behavior. | 将模块类型从“Developer”改为“UncookedOnly”，影响插件在打包时的行为。 |

### 维护评价

该插件创建于 2014 年，是一个非常古老的示例插件。其最近的更新记录均为**全引擎范围的代码维护、协议更新或构建系统调整**，而非针对插件功能本身的更新。这表明：
1.  **功能稳定**：插件提供的示例代码（UObject/UStruct声明）已足够经典和完善，无需修改。
2.  **维护不活跃**：作为纯教学示例，它不接收新功能开发，仅随引擎版本进行必要的兼容性调整。
3.  **状态良好**：虽然更新频率低，但它依然存在于最新的引擎版本中，并且编译和运行正常。

**总结**：这是一个功能完整、极其稳定但已**停止功能演进**的教学示例插件。对于学习插件中UObject声明的基础知识仍有参考价值，不建议在其中添加任何新的、实际的运行时功能。推荐作为**学习模板**使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/UObjectPlugin)
- [模块接口头文件](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Developer/UObjectPlugin/Source/UObjectPlugin/Public/IUObjectPlugin.h)
- [示例UObject头文件](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Developer/UObjectPlugin/Source/UObjectPlugin/Classes/MyPluginObject.h)