# PlainPropsEngine

> New Serialization Stack Prototype - Engine Bindings（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 纯属性引擎 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资产、命令行工具） |
| 模块 | `PlainPropsEngine` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-01 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PlainPropsEngine) | |

## 用途

这是一个实验性的新序列化栈（PlainProps）的**引擎绑定模块**原型。它不是最终用户直接使用的功能，而是一个底层基础设施组件。

其核心目的是将 Unreal Engine 的一些核心系统（如动画、Niagara、蓝图资产）**接入**到基于“纯属性”（PlainProps）概念的新序列化框架中。该框架旨在提供一种更直接、可能更高效的序列化方式，以替代或补充当前基于反射的 UObject 属性序列化系统。本插件定义了如何将引擎特定的数据类型（如动画资产、粒子系统、蓝图类）绑定到这个新系统中。

## 使用场景

- 你是一名**引擎开发者**或**早期采用者**，正在评估或迁移至新的 PlainProps 序列化栈，需要将引擎核心资产类型集成进去。
- 你在开发一个新的、需要高性能序列化的**核心系统**，并希望测试与新序列化栈的兼容性。

## 蓝图用法

此插件主要提供 C++ 底层绑定和测试基础设施，**不包含直接供蓝图使用的公共 API 节点**。其功能通过 C++ 调用 PlainProps 框架来暴露。

### 核心资产类型（用于测试）

插件中定义了用于测试新序列化栈的资产类型，可在编辑器中创建和查看。

| 类 | 说明 |
|---|---|
| `UPlainPropsInstancedStructTestAsset` | 一个测试用数据资产，包含多种 `FInstancedStruct` 变体，用于验证新序列化栈对混合类型数组的支持。 |

## C++ 用法

用法主要围绕将引擎类型注册到 PlainProps 序列化系统。

### 头文件引入

```cpp
#include "PlainPropsEngineTestUtils.h"
```

### 基本用法：绑定引擎类型

（来源：`Source/Public/PlainPropsEngineTestUtils.h`）
通过调用 `BindAllTypes` 函数，可以触发对所有已注册引擎类型（动画、Niagara等）的自定义绑定过程。

```cpp
#include "PlainPropsEngineTestUtils.h"
#include "PlainProps/PlainPropsBindings.h" // 假设的 PlainProps 头文件

// 在某个初始化点（如模块启动或特定命令）
void InitializePlainPropsBindings()
{
    // 使用默认模式和批量类型进行绑定
    PlainProps::UE::BindAllTypes(PlainProps::UE::EBindMode::Default, PlainProps::UE::EBatchType::SingleThreaded);
}
```

### 进阶用法：创建测试资产

（来源：`Source/Private/PlainPropsTestAssets.h` 和 `Source/Public/PlainPropsTestTypes.h`）
插件提供工厂函数创建测试资产，并定义了多种 `FInstancedStruct` 的测试 Schema。

```cpp
#include "PlainPropsTestAssets.h"
#include "PlainPropsTestTypes.h"

void TestPlainPropsSerialization()
{
    // 1. 创建包含测试数据的资产
    TArray<UObject*> TestAssets = PlainProps::UE::CreateTestAssets();
    UPlainPropsInstancedStructTestAsset* TestAsset = Cast<UPlainPropsInstancedStructTestAsset>(TestAssets[0]);

    if (TestAsset)
    {
        // 2. 访问测试资产中的 FInstancedStruct
        const FInstancedStruct& StructA = TestAsset->StructA;
        if (const FPlainPropsInstancedStructTestSchemaA* DataA = StructA.GetPtr<FPlainPropsInstancedStructTestSchemaA>())
        {
            UE_LOG(LogTemp, Log, TEXT("StructA Values: X=%f, Y=%f, Z=%f"), DataA->X, DataA->Y, DataA->Z);
        }

        // 3. 混合数组中包含多种类型
        for (const FInstancedStruct& Entry : TestAsset->MixedArray)
        {
            if (Entry.IsValid())
            {
                // 根据实际类型处理...
            }
        }
    }
}
```

## Demo 示例

以下示例展示了如何定义一个简单的自定义结构体，并利用测试基础设施观察其在新序列化栈中的行为。

**MyStruct.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "InstancedStruct.h"
#include "MyStruct.generated.h"

USTRUCT(BlueprintType)
struct FMyCustomData
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FString Name = TEXT("Demo");

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 Health = 100;
};
```

**MyPlainPropsTest.cpp**
```cpp
#include "CoreMinimal.h"
#include "UObject/Package.h"
#include "MyStruct.h"
#include "PlainPropsEngineTestUtils.h" // 用于绑定函数
#include "PlainProps/PlainPropsBindings.h" // 假设的 PlainProps 头文件

class FMyPlainPropsDemo
{
public:
    void RunDemo()
    {
        // 1. 确保新序列化栈的绑定已初始化
        PlainProps::UE::BindAllTypes(PlainProps::UE::EBindMode::Default, PlainProps::UE::EBatchType::SingleThreaded);

        // 2. 创建一个 FInstancedStruct 包含我们的自定义类型
        FInstancedStruct MyStructInstance = FInstancedStruct::Make<FMyCustomData>();
        if (FMyCustomData* Data = MyStructInstance.GetMutablePtr<FMyCustomData>())
        {
            Data->Name = TEXT("Hello, PlainProps!");
            Data->Health = 95;
        }

        // 3. 此时，MyStructInstance 内的数据可以通过新序列化栈进行处理。
        //    具体的序列化/反序列化 API 调用取决于 PlainProps 框架的公共接口。
        //    例如: PlainProps::Serialize(MyStructInstance, Archive);
        //    或者观察测试用例如何保存/加载 UPlainPropsInstancedStructTestAsset。

        UE_LOG(LogTemp, Log, TEXT("Created FInstancedStruct with FMyCustomData for PlainProps."));
    }
};
```

## 模块依赖

从 `Build.cs` 分析，该插件的模块 `PlainPropsEngine` 依赖了以下非标准模块：

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 用于在编辑器环境下执行自定义的引擎类型绑定命令和资产处理。 |
| `BlueprintGraph` | 用于支持蓝图相关类型的序列化绑定。 |

此外，它还通过 `.uplugin` 声明依赖 `PlainProps`、`PlainPropsUObject`、`GameplayAbilities` 和 `Niagara` 插件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `b6b85039` | PlainProps: Add template constructors for FMemberSpec and TOptionalId to handle implicit conversions | 增加模板构造函数以处理隐式转换，提升灵活性。 |
| 2026-04-14 | `efdd698c` | PlainProps: Replace incorrect checkSlow in the debug version of DiffMap with correct handling of dif | 修复调试版本中的一个错误检查，确保正确处理差异。 |
| 2026-04-07 | `a203e4ac` | PlainProps: FInstancedStruct support | **核心功能更新**：为新序列化栈添加了对 `FInstancedStruct` 的支持。 |
| 2026-04-02 | `a73f0306` | PlainProps: Minor cleanup for Meta and Blueprint bindings | 对元数据和蓝图绑定进行小范围清理优化。 |
| 2026-04-02 | `ee2494f9` | PlainProps: Load a blueprint asset completely in the new serialization stack with no Serialize and S | 实现蓝图资产完全通过新序列化栈加载，不依赖传统 Serialize 方法。 |

### 维护评价

- **活跃维护**：创建于 2025 年 9 月，并于 2026 年 4 月仍有**实质性、功能性的更新**（如添加 `FInstancedStruct` 支持、实现蓝图资产加载）。
- **实验性明确**：`.uplugin` 中 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，表明这是尚在开发和验证中的原型代码。
- **定位清晰**：作为 `PlainProps` 大系统的引擎侧绑定，其进度与核心框架（`PlainProps`，`PlainPropsUObject`）同步。
- **使用警告**：**此插件处于高度实验阶段，API 不稳定，仅建议用于研究、测试和对新序列化栈的早期集成。** 不应用于正式项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PlainPropsEngine)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PlainPropsEngine/Tests) (待确认，通常插件测试在此路径下)