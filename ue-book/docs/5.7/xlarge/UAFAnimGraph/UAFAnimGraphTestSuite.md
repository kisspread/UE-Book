# UAF Anim Graph

> Framework for defining animation graphs.

| 属性 | 值 |
|---|---|
| 中文名 | UAF 动画图 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、运行时数据） |
| 模块 | `UAFAnimGraph` (Runtime), `UAFAnimGraphEditor` (Runtime), `UAFAnimGraphTestSuite` (Runtime), `UAFAnimGraphUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-29 |
| 年龄标签 | 🆕（约 1 个月） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFAnimGraph) | |

## 用途

UAF Anim Graph 是一个实验性的动画图定义框架，属于 Unreal Animation Framework (UAF) 体系。它提供了一套基于 **Trait（特征）** 的动画图构建方式，允许开发者通过组合小的、可复用的 trait 来定义动画图的节点行为，并通过事件系统在 trait 之间传递数据。此插件解决的核心问题是：在现有动画蓝图或状态机之外，提供一种更模块化、更灵活的动画图定义机制，适合需要高度定制化动画逻辑的项目。

## 使用场景

- 你在开发一个需要复杂动画混合逻辑的游戏，希望将动画逻辑拆分为独立的 trait 组件。
- 你需要自定义动画图的更新和求值流程，例如按需执行、条件分支等。
- 你正在研究 UE 的下一代动画系统，并希望尝试基于 trait 的架构。

## 蓝图用法

UAF Anim Graph 的核心 API 主要暴露于 C++ 层面，蓝图节点暂未直接公开。若需在蓝图中使用 trait 系统，请通过 UAF 核心模块的蓝图接口间接操作。建议在 C++ 中编写自定义 trait 并在蓝图中调用。

## C++ 用法

### 核心概念

- **Trait**: 动画图的最小功能单元，通过 `FAnimNextTraitSharedData` 结构定义输入/输出属性。
- **Trait Event**: 用于 trait 之间通信的事件对象，继承自 `FAnimNextTraitEvent`，可附加自定义数据。
- **Node Template**: 由多个 trait 组合而成的节点模板，通过 `FNodeTemplateRegistry` 管理。

### 头文件引入

```cpp
#include "AnimNextAnimGraphTraitGraphTest.h"   // 测试示例中的 trait 定义
#include "TraitCore/TraitEvent.h"
#include "TraitCore/TraitBinding.h"
#include "TraitCore/NodeTemplateRegistry.h"
```

### 自定义 Trait 示例

创建一个 trait 并定义其输入属性（在 .h 中）：

```cpp
// 来源于测试文件 AnimNextAnimGraphTraitGraphTest.h
USTRUCT()
struct FTestTraitSharedData : public FAnimNextTraitSharedData
{
    GENERATED_BODY()

    UPROPERTY(meta = (Input, Inline))
    int32 UpdateCount = 0;

    UPROPERTY(meta = (Input, Inline))
    int32 EvaluateCount = 0;

    // 潜伏属性（通过宏注册）
    #define TRAIT_LATENT_PROPERTIES_ENUMERATOR(GeneratorMacro) \
        GeneratorMacro(SomeLatentInt32) \
        GeneratorMacro(SomeOtherLatentInt32) \
        GeneratorMacro(SomeOutOfOrderLatentBool) \
        GeneratorMacro(SomeLatentVector) \
        GeneratorMacro(SomeLatentFloat) \

    GENERATE_TRAIT_LATENT_PROPERTIES(FTestTraitSharedData, TRAIT_LATENT_PROPERTIES_ENUMERATOR)
    #undef TRAIT_LATENT_PROPERTIES_ENUMERATOR
};
```

### 自定义 Trait 事件

```cpp
// 来源于测试文件 AnimNextAnimGraphTraitEventTest.h
struct FTraitAnimGraphTest_EventA : public FAnimNextTraitEvent
{
    DECLARE_ANIM_TRAIT_EVENT(FTraitAnimGraphTest_EventA, FAnimNextTraitEvent)

    bool bTestFlag = false;
    TArray<UE::UAF::FTraitUID> VisitedTraits;
};
```

### 加载动画图存档并解析节点

```cpp
// 来源于测试工具 AnimNextRuntimeTest.h
#include "AnimNextRuntimeTest.h"

// 从缓冲区加载动画图数据
UAnimNextAnimationGraph* AnimGraph = NewObject<UAnimNextAnimationGraph>();
TArray<FNodeHandle> NodeHandles;
TArray<uint8> ArchiveBuffer; // 从某处获取二进制数据

bool bSuccess = FTestUtils::LoadFromArchiveBuffer(*AnimGraph, NodeHandles, ArchiveBuffer);
check(bSuccess);
```

### 临时替换节点模板注册表（用于测试隔离）

```cpp
// 来源于测试工具 AnimNextRuntimeTest.h
{
    UE::UAF::FScopedClearNodeTemplateRegistry ScopedRegistry;
    // 在此作用域内，全局节点模板注册表被替换为临时实例
    // ScopedRegistry.TmpRegistry 可以手动添加模板
    // 作用域结束后自动恢复原注册表
}
```

## Demo 示例

以下是一个完整的可编译测试用例，展示如何创建 trait 事件并触发遍历（基于 `AnimNextAnimGraphTraitEventTest.h`）：

```cpp
// Demo.cpp
#include "CoreMinimal.h"
#include "TraitCore/TraitUID.h"
#include "TraitCore/TraitEvent.h"
#include "AnimNextAnimGraphTraitEventTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTraitEventDemoTest, "UAF.AnimGraph.TraitEventDemo", EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::EngineFilter)

bool FTraitEventDemoTest::RunTest(const FString& Parameters)
{
    // 创建事件 A
    FTraitAnimGraphTest_EventA EventA;
    EventA.bTestFlag = true;
    EventA.VisitedTraits.Add(UE::UAF::FTraitUID(1));

    // 创建事件 B（携带子事件）
    FTraitAnimGraphTest_EventB EventB;
    EventB.bTestFlag0 = true;
    EventB.ChildEvent = FAnimNextTraitEventPtr::MakeShared<FTraitAnimGraphTest_EventA>(EventA);

    // 模拟事件处理
    TestTrue("Event A flag is set", EventA.bTestFlag);
    TestEqual("Event B has one child", EventB.ChildEvent.IsValid(), true);

    return true;
}
#endif
```

## 模块依赖

此插件依赖 UAF 核心模块。使用 `UAFAnimGraph` 模块的模块需要在 `Build.cs` 中添加依赖（除标准 Core/Engine 外）：

| 模块 | 用途 |
|---|---|
| `UAF` | 提供基础 Trait 系统、事件定义、节点模板注册表等核心功能 |
| `AnimGraphRuntime` | 动画图运行时支持（通常依赖） |

若使用 `UAFAnimGraphEditor` 或测试套件，还需额外依赖编辑器和测试模块。

## 维护状态

### 近期更新

- 2025-10-01 `6f23619b` — 将拖放操作的 UEdGraphSchema 资产引用过滤移动到各自的实现中
- 2025-09-03 `bb48edd8` — 避免编辑器退出时的无效内存访问
- 2025-09-03 `bc59af4e` — 避免在旧版 UAF 内容上打开上下文菜单时崩溃
- 2025-09-02 `78089693` — 为 UAF pose 评估添加作用域命名事件
- 2025-08-29 `3663a91d` — 修复 UAF RigVM 重写变量资产的持久性

### 维护评价

- **创建时间**: 2025-08-29，约 1 个月。
- **更新频率**: 活跃，近 1 个月内有多项功能更新和崩溃修复。
- **当前状态**: 实验性插件（`IsExperimentalVersion=true`），API 可能不稳定且缺乏完整文档。
- **推荐度**: 仅适合探索性开发或参与官方实验；不建议用于生产项目，除非对可能的重大变更做好准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFAnimGraph)
- [官方文档](https://docs.unrealengine.com/5.7/Animation/UAF/)（暂无单独页面，统归于 UAF 文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/UAF/UAFAnimGraph/Source/UAFAnimGraphTestSuite/)