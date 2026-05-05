# UAF Tests

> UAF Automated Tests（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资产） |
| 模块 | `UAFAnimGraphTestSuite` (Runtime), `UAFAnimNodeTestData` (Runtime), `UAFCQTestSuite` (Runtime), `UAFTestSuite` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-30 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites) | |

## 用途

这是 Unreal Animation Framework (UAF) 的自动化测试套件插件。它不提供任何面向最终用户的功能，而是为 UAF 核心系统（Trait 系统、动画图、动画节点等）提供全面的自动化测试覆盖。

该插件解决的问题是：确保 UAF 框架的各个组件（Trait 事件传递、Trait 序列化、Trait 共享数据、动画图实例化、GC 处理等）在引擎迭代过程中保持正确性和稳定性。

## 使用场景

- **UAF 框架开发者**：在修改 Trait 核心系统后运行测试，验证没有引入回归
- **动画系统贡献者**：在提交动画图相关改动前，确认现有测试仍然通过
- **CI/CD 流水线**：作为引擎自动化测试的一部分，持续验证 UAF 子系统的健康状态

> ⚠️ 此插件仅用于测试目的，不应在生产项目中启用。

## 蓝图用法

此插件不包含任何蓝图可调用的 API。所有内容均为 C++ 自动化测试代码。

## C++ 用法

此插件的代码仅供 UAF 内部测试使用，不建议外部模块直接引用。以下内容用于理解测试结构和 UAF Trait 系统的工作方式。

### 头文件引入

```cpp
// Trait 事件测试
#include "AnimNextAnimGraphTraitEventTest.h"

// Trait 共享数据测试
#include "AnimNextAnimGraphTraitGraphTest.h"

// Trait 接口测试
#include "AnimNextAnimGraphTraitInterfacesTest.h"

// 运行时测试工具
#include "AnimNextRuntimeTest.h"

// GC 测试工具
#include "GCTestsUtil.h"
```

### Trait 事件系统测试

测试 Trait 事件在 Trait 树中的传播机制。事件可以携带标志位和访问记录，用于验证事件是否按预期路径遍历。

```cpp
// 来源: Private/AnimNextAnimGraphTraitEventTest.h

// 简单事件：携带一个布尔标志和访问过的 Trait 列表
struct FTraitAnimGraphTest_EventA : public FAnimNextTraitEvent
{
    DECLARE_ANIM_TRAIT_EVENT(FTraitAnimGraphTest_EventA, FAnimNextTraitEvent)

    bool bTestFlag = false;
    TArray<UE::UAF::FTraitUID> VisitedTraits;
};

// 复杂事件：支持子事件嵌套，用于测试事件链式传播
struct FTraitAnimGraphTest_EventB : public FAnimNextTraitEvent
{
    DECLARE_ANIM_TRAIT_EVENT(FTraitAnimGraphTest_EventB, FAnimNextTraitEvent)

    bool bTestFlag0 = false;
    bool bTestFlag1 = false;
    TArray<UE::UAF::FTraitUID> VisitedTraits;
    FAnimNextTraitEventPtr ChildEvent;
};
```

### Trait 共享数据测试

测试 Trait 共享数据的属性定义、输入/输出绑定以及延迟属性（Latent Properties）机制。

```cpp
// 来源: Private/AnimNextAnimGraphTraitGraphTest.h

// 测试共享数据：包含内联属性和延迟属性
USTRUCT()
struct FTestTraitSharedData : public FAnimNextTraitSharedData
{
    GENERATED_BODY()

    // 内联输入属性（直接求值）
    UPROPERTY(meta = (Input, Inline))
    int32 UpdateCount = 0;

    UPROPERTY(meta = (Input, Inline))
    int32 EvaluateCount = 0;

    // 延迟输入属性（通过图节点求值）
    UPROPERTY(meta = (Input))
    int32 SomeLatentInt32 = 5;           // MathAdd with constants, latent

    UPROPERTY(meta = (Input))
    int32 SomeOtherLatentInt32 = 7;      // GetParameter, latent

    UPROPERTY(meta = (Input))
    FVector SomeLatentVector = FVector::OneVector;  // GetParameter, latent

    // 延迟属性枚举器宏 - 定义属性的求值顺序
    #define TRAIT_LATENT_PROPERTIES_ENUMERATOR(GeneratorMacro) \
        GeneratorMacro(SomeLatentInt32) \
        GeneratorMacro(SomeOutOfOrderLatentBool) \
        GeneratorMacro(SomeOtherLatentInt32) \
        GeneratorMacro(SomeLatentVector) \
        GeneratorMacro(SomeLatentFloat)

    GENERATE_TRAIT_LATENT_PROPERTIES(FTestTraitSharedData, TRAIT_LATENT_PROPERTIES_ENUMERATOR)
    #undef TRAIT_LATENT_PROPERTIES_ENUMERATOR
};
```

### Trait 接口测试

测试 Trait 的子节点（Child）接口，包括单子节点和多子节点的句柄管理。

```cpp
// 来源: Private/AnimNextAnimGraphTraitInterfacesTest.h

// 单子节点 Trait
USTRUCT()
struct FTraitWithOneChildSharedData : public FAnimNextTraitSharedData
{
    GENERATED_BODY()

    UPROPERTY()
    FAnimNextTraitHandle Child;
};

// 多子节点 Trait（固定数组）
USTRUCT()
struct FTraitWithChildrenSharedData : public FAnimNextTraitSharedData
{
    GENERATED_BODY()

    UPROPERTY()
    FAnimNextTraitHandle Children[2];
};
```

### 运行时测试工具

提供用于测试节点模板注册表的 RAII 作用域工具类。

```cpp
// 来源: Private/AnimNextRuntimeTest.h

// 作用域内清除节点模板注册表，离开作用域时自动恢复
// 用于隔离测试，避免注册表状态污染
struct FScopedClearNodeTemplateRegistry final
{
    UE_NONCOPYABLE(FScopedClearNodeTemplateRegistry);

    UAFANIMGRAPHTESTSUITE_API FScopedClearNodeTemplateRegistry();
    UAFANIMGRAPHTESTSUITE_API ~FScopedClearNodeTemplateRegistry();

    int32 OldTemplateBufferSize = 0;
    TMap<uint32, FNodeTemplateRegistryHandle> OldTemplateUIDToHandleMap;
};

// 创建临时空注册表并替换全局注册表，离开作用域时恢复
// 仅用于测试节点注册表本身
struct FScopedNewNodeTemplateRegistry final
{
    UE_NONCOPYABLE(FScopedNewNodeTemplateRegistry);

    UAFANIMGRAPHTESTSUITE_API FScopedNewNodeTemplateRegistry();
    UAFANIMGRAPHTESTSUITE_API ~FScopedNewNodeTemplateRegistry();

    FNodeTemplateRegistry TmpRegistry;
};
```

### GC 测试工具

测试 UAF Trait 系统与 Unreal GC（垃圾回收）的集成，确保 UObject 引用被正确追踪。

```cpp
// 来源: Private/GCTestsUtil.h

// 包含 UObject 引用的 Trait 共享数据，用于测试 GC 引用追踪
USTRUCT()
struct FUAFTestAnimSequenceSharedData : public FAnimNextTraitSharedData
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = "Default")
    TObjectPtr<UAnimSequence> AnimSequence;

    // UEnum 属性 - 验证不会产生 GC 处理的误报
    UPROPERTY(EditAnywhere, Category = "Default")
    EAnimInterpolationType DummyProp0 = EAnimInterpolationType::Linear;

    #define TRAIT_LATENT_PROPERTIES_ENUMERATOR(GeneratorMacro) \
        GeneratorMacro(AnimSequence) \
        GeneratorMacro(DummyProp0)

    GENERATE_TRAIT_LATENT_PROPERTIES(FUAFTestAnimSequenceSharedData, TRAIT_LATENT_PROPERTIES_ENUMERATOR)
    #undef TRAIT_LATENT_PROPERTIES_ENUMERATOR
};

// 持有动画图实例的 UObject，用于测试图实例的 GC 生命周期
UCLASS()
class UGraphInstanceHolder : public UObject
{
    GENERATED_BODY()

public:
    TSharedPtr<FAnimNextGraphInstance> GraphInstance;

    static void AddReferencedObjects(UObject* InThis, FReferenceCollector& Collector);
};
```

## Demo 示例

此插件为纯测试插件，不提供可复用的 Demo。如需了解 UAF Trait 系统的使用方式，请参考 UAF 主插件的文档和示例。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AnimNextCore` | Trait 核心系统（TraitUID、TraitEvent、TraitBinding、TraitSharedData 等） |
| `AnimNext` | 动画图实例、RigUnit 基类 |
| `AnimNextEditor` | 编辑器相关测试支持 |

## 维护状态

### 近期更新

- 2026-04-14 `12eb7efc` Fix FBindableXxx binding serialization issues when used with UAF traits
- 2026-04-14 `35e60df1` Migrate UE_LOG to UE_LOGF.
- 2026-04-10 `797a6da6` Rename GetComponent to GetOrAddComponent to match functionality
- 2026-04-06 `4ba19be0` Add function binding support to FBindableValue
- 2026-03-30 `0df5eb4c` Add FBindableTransform for binding to FTransform values (it has less overhead than using FBindableSt

### 维护评价

- **创建时间**：2026-03-30，非常新的插件
- **实验性标记**：`IsExperimentalVersion=true`，表明 UAF 框架仍处于实验阶段
- **测试覆盖范围**：67 个源文件，覆盖 Trait 事件、共享数据、接口、序列化、GC 等多个维度，测试较为全面
- **维护状态**：作为 UAF 框架的配套测试套件，预计将随 UAF 框架的开发持续更新
- **使用建议**：仅限 UAF 框架开发者和贡献者使用，不建议在生产项目中启用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites)
- 官方文档：无
- [UAF 主插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF)