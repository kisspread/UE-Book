# Property Binding Utils

> Utility code for implementing property bindings

| 属性 | 值 |
|---|---|
| 中文名 | 属性绑定工具 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `PropertyBindingUtils` (Runtime), `PropertyBindingUtilsEditor` (Editor), `PropertyBindingUtilsTestSuite` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-15 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/PropertyBindingUtils) | |

## 用途

本插件为 UE5 提供了一套通用的**属性绑定**实现框架。它最初从 `StateTree` 插件中提取并重构而成，旨在为游戏逻辑、UI 或其他系统提供一种标准化的机制，以动态地将数据源（如 Actor 的属性）与目标（如 UI 元素、Gameplay 效果）连接起来。这解决了在不同系统间进行数据驱动通信时代码耦合度高、实现不一致的问题。

## 使用场景

-   你需要在 UI 中动态显示角色的生命值、法力值等状态。
-   你在设计一个数据驱动的 Gameplay 系统，希望效果的强度能根据某个属性自动变化。
-   你需要在 StateTree 或其他逻辑系统中，实现节点输出到另一个节点输入的动态连接。
-   你正在开发一个需要通用属性绑定能力的自定义系统或工具。

## 蓝图用法

此插件的核心是运行时框架，蓝图主要用于获取属性信息和创建上下文。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get All Property Descriptors` | 获取指定类上所有可用作绑定源的属性描述符列表。 | `UPropertyBindingUtilsBPLibrary` |
| `Create Property Binding Context` | 为一个对象创建用于执行绑定操作的上下文。 | `UPropertyBindingUtilsBPLibrary` |

### 使用示例（蓝图描述）

1.  在蓝图中，使用 `Get All Property Descriptors` 节点传入你想要绑定的 Actor 类（例如 `BP_MyCharacter`）。这将返回一个包含 `FPropertyBindingDataView` 的数组，每个元素代表一个可绑定的属性（如 “Health”， “Mana”）。
2.  通过一个有效的对象（例如拥有该属性的 Actor 实例）调用 `Create Property Binding Context`，创建一个 `FPropertyBindingContext`。
3.  使用此上下文与具体的属性描述符，配合其他系统（如 StateTree 的绑定节点）来完成数据的读取或写入操作。

## C++ 用法

### 头文件引入

```cpp
#include "PropertyBindingUtilsModule.h"
// 根据需要引入具体头文件，如：
#include "PropertyBindingDataView.h"
#include "PropertyBindingContext.h"
```

### 基本用法

```cpp
// 1. 获取对象的属性描述符集合
TArray<FPropertyBindingDataView> Descriptors;
FPropertyBindingUtilsModule::Get().GetPropertyDataViews(MyActorInstance, Descriptors);

// 2. 创建绑定上下文
FPropertyBindingContext BindingContext;
BindingContext.SetObject(MyActorInstance);
```
*来源：`PropertyBindingUtilsTestSuite` 测试用例*

### 进阶用法

插件主要为 `StateTree` 等系统提供底层支持。在 StateTree 的任务或评估器中，会使用这些工具来动态解析节点的输入输出绑定。
```cpp
// 在 StateTree 节点编译或执行时，利用 PropertyBindingUtils 解析绑定关系
if (const FPropertyBindingDataView* Descriptor = FindDescriptor(InPropertyName))
{
    if (FPropertyBindingContext Context = CreateContext(InOwnerObject))
    {
        // 使用描述符和上下文进行属性访问
        Descriptor->GetValue(Context, OutValue);
    }
}
```
*推断自 `StateTree` 相关提交及模块依赖关系*

## Demo 示例

以下是一个最小示例，展示如何在 C++ 中获取对象的属性描述符。

**MyBindingDemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyBindingDemoActor.generated.h"

UCLASS()
class AMyBindingDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AMyBindingDemoActor();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Demo")
    float Health = 100.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Demo")
    FString CharacterName = TEXT("Hero");

    void PrintBindableProperties() const;
};
```

**MyBindingDemoActor.cpp**
```cpp
#include "MyBindingDemoActor.h"
#include "PropertyBindingUtilsModule.h"
#include "PropertyBindingDataView.h"

AMyBindingDemoActor::AMyBindingDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyBindingDemoActor::PrintBindableProperties() const
{
    TArray<FPropertyBindingDataView> Descriptors;
    // 获取当前对象实例的所有可绑定属性
    FPropertyBindingUtilsModule::Get().GetPropertyDataViews(this, Descriptors);

    UE_LOG(LogTemp, Log, TEXT("--- Bindable Properties for %s ---"), *GetName());
    for (const FPropertyBindingDataView& Desc : Descriptors)
    {
        UE_LOG(LogTemp, Log, TEXT("Property: %s | Type: %s"), 
            *Desc.GetPropertyName().ToString(),
            *Desc.GetPropertyType().GetName());
    }
}
```

## 模块依赖

此插件本身提供了基础运行时和编辑器功能，无特殊外部依赖。在使用其服务的系统（如 StateTree）中，这些依赖是隐式的。

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `bd1b81a6` | [StateTree] Implement task completion binding support for StateTree property bindings. | 为 StateTree 属性绑定添加了任务完成绑定支持。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏迁移至新的 UE_LOGF 格式。 |
| 2026-03-31 | `55512aa0` | PropertyBindings: Provide a detailed error message when promoting a parameter ensures due to failed | 为参数提升失败时提供更详细的错误信息。 |
| 2026-03-26 | `7113aa71` | [StateTree] Centralize FStateTreeEditorNode initialization via InitializeAs() | 通过 InitializeAs() 方法集中 StateTree 编辑器节点的初始化。 |
| 2026-03-13 | `86c9c6c7` | [StateTree] Add the output binding batch index info to the compilation output log. | 在编译输出日志中添加输出绑定批次索引信息。 |

### 维护评价

-   **活跃维护**：插件自 2024 年初创建以来，近期（2026年3-4月）仍有针对核心功能（如 StateTree 集成）和代码质量的频繁更新。
-   **实验性状态**：标记为 `IsBetaVersion=true` 且默认不启用，表明其 API 和功能可能尚未稳定，未来可能有破坏性变更。
-   **推荐建议**：该插件主要面向引擎开发者和高级使用者，用于构建如 StateTree 之类的复杂系统。对于普通游戏项目，如果不需要自定义底层绑定机制，通常无需直接启用此插件。由于其是基础工具，建议在相关系统（如 StateTree）的文档指导下使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/PropertyBindingUtils)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/PropertyBindingUtils/Source/PropertyBindingUtilsTestSuite)