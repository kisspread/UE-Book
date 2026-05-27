# UAF Tests

> UAF Automated Tests

| 属性 | 值 |
|---|---|
| 中文名 | 统一动画框架测试套件 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资产、测试蓝图） |
| 模块 | `UAFAnimGraphTestSuite` (Runtime), `UAFAnimNodeTestData` (Runtime), `UAFCQTestSuite` (Runtime), `UAFTestSuite` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-02-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites) | |

## 用途

该插件并非面向最终用户的功能性插件，而是 **统一动画框架 (Unified Animation Framework， UAF) 的专用自动化测试套件**。它的存在是为了验证 UAF 动画系统核心特性的正确性、稳定性和性能，确保框架在持续开发过程中不会引入回归错误。

它通过一系列单元测试和集成测试，覆盖了 UAF 的以下核心方面：
1.  **动画图 (AnimGraph) 与特质 (Trait) 系统**：测试特质的创建、连接、求值和更新逻辑。
2.  **序列化**：验证特质共享数据 (SharedData) 的序列化与反序列化过程。
3.  **垃圾回收 (GC)**：确保包含 UAF 对象（如动画序列）的测试图在垃圾回收时行为正确。
4.  **事件处理**：测试特质间事件的传播和处理机制。
5.  **蓝图集成**：通过测试蓝图资产验证 UAF 系统在蓝图环境下的可用性。

## 使用场景

- **UAF 动画系统开发人员**：在修改或扩展 UAF 核心代码（如 `AnimNext` 模块）后，运行此测试套件以验证改动未破坏现有功能。
- **动画技术美术师或开发者**：如果在项目中使用了 UAF 框架，并且遇到难以复现的动画图异常，可以参考或修改此插件中的测试用例，以构建最小重现案例。
- **框架贡献者**：在向 Epic 的 UAF 框架提交 Pull Request 时，需要确保所有相关测试（包括此套件中的测试）全部通过。

## 蓝图用法

虽然该插件主要以 C++ 自动化测试为主，但它包含一些可供蓝图使用的测试工具节点，主要用于在编辑器或运行时触发或验证测试。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `LoadFromArchiveBuffer` | 从二进制缓冲区加载动画图数据并解析节点句柄，用于测试序列化功能。 | `UE::UAF::FTestUtils` (C++ 静态函数，可在蓝图中通过蓝图函数库调用) |
| `FScopedClearNodeTemplateRegistry` | **C++ RAII 作用域对象**，用于在测试期间临时清空全局节点模板注册表，并在作用域结束时恢复原状。 | `UE::UAF::FScopedClearNodeTemplateRegistry` |
| `FScopedNewNodeTemplateRegistry` | **C++ RAII 作用域对象**，用于在测试期间创建并切换到一个全新的临时节点模板注册表，作用域结束后恢复原始注册表。 | `UE::UAF::FScopedNewNodeTemplateRegistry` |

### 使用示例（蓝图描述）

这些节点主要用于 C++ 自动化测试。在蓝图中直接使用的机会较少。一个可能的场景是编写一个**编辑器工具蓝图**，用于：
1.  创建一个 `FScopedNewNodeTemplateRegistry` 作用域（通过 C++ 蓝图库函数）。
2.  在该作用域内，使用 `LoadFromArchiveBuffer` 加载一个测试动画图。
3.  运行一些验证逻辑，检查图是否按预期工作。
4.  作用域结束，自动恢复节点注册表，避免污染其他测试或编辑器状态。

**注意**：绝大多数测试用例是 `IMPLEMENT_SIMPLE_AUTOMATION_TEST` 宏定义的，只能在编辑器的 **Session Frontend -> Automation** 面板或通过命令行运行，无法直接在蓝图关卡中调用。

## C++ 用法

此插件的用法主要体现在 **编写和运行针对 UAF 框架的自动化测试**。

### 头文件引入

```cpp
#include "UAFAnimGraphTestSuite.h" // 访问测试工具和数据结构
// 或者根据具体测试模块引入
#include "AnimNextAnimGraphTraitTest.h"
```

### 基本用法：定义测试特质 (Trait) 的共享数据 (SharedData)

这是构建 UAF 测试的基础。每个特质需要一个继承自 `FAnimNextTraitSharedData` 的结构体来存储其配置和状态。

```cpp
// 来源： Engine/Plugins/Experimental/UAF/UAFTestSuites/Source/UAFAnimGraphTestSuite/Private/AnimNextTraitBaseTest.h

// 一个简单的特质共享数据，包含一个用于标识的UID
USTRUCT()
struct FTraitA_BaseSharedData : public FAnimNextTraitSharedData
{
	GENERATED_BODY()

	UPROPERTY(meta = (Inline))
	uint32 TraitUID;

	FTraitA_BaseSharedData();
};

// 一个用于测试序列化的共享数据，包含多种基础类型
USTRUCT()
struct FTraitSerialization_BaseSharedData : public FAnimNextTraitSharedData
{
	GENERATED_BODY()

	UPROPERTY(meta = (Inline))
	int32 Integer = 0;
	UPROPERTY(meta = (Inline))
	FVector Vector = FVector::ZeroVector;
	UPROPERTY(meta = (Inline))
	FString String;
	// ... 更多属性
};
```

### 进阶用法：处理特质事件 (Trait Events) 和 GC

**特质事件测试**：
```cpp
// 来源： Engine/Plugins/Experimental/UAF/UAFTestSuites/Source/UAFAnimGraphTestSuite/Private/AnimNextAnimGraphTraitEventTest.h

// 定义一个自定义特质事件，携带标志位和访问记录
struct FTraitAnimGraphTest_EventA : public FAnimNextTraitEvent
{
	DECLARE_ANIM_TRAIT_EVENT(FTraitAnimGraphTest_EventA, FAnimNextTraitEvent)

	bool bTestFlag = false;
	TArray<UE::UAF::FTraitUID> VisitedTraits; // 记录事件访问过的特质UID
};
```

**垃圾回收 (GC) 安全测试**：
```cpp
// 来源： Engine/Plugins/Experimental/UAF/UAFTestSuites/Source/UAFAnimGraphTestSuite/Private/GCTestsUtil.h

// 一个持有UObject（UAnimSequence）的共享数据，用于测试GC安全性
USTRUCT()
struct FUAFTestAnimSequenceSharedData : public FAnimNextTraitSharedData
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, Category = "Default")
	TObjectPtr<UAnimSequence> AnimSequence;
	// ... 属性

	#define TRAIT_LATENT_PROPERTIES_ENUMERATOR(GeneratorMacro) \
		GeneratorMacro(AnimSequence)
	GENERATE_TRAIT_LATENT_PROPERTIES(FUAFTestAnimSequenceSharedData, TRAIT_LATENT_PROPERTIES_ENUMERATOR)
	#undef TRAIT_LATENT_PROPERTIES_ENUMERATOR
};

// 一个持有动画图实例的UObject，用于确保GC能正确遍历引用
UCLASS()
class UGraphInstanceHolder : public UObject
{
	GENERATED_BODY()
public:
	TSharedPtr<FAnimNextGraphInstance> GraphInstance;
	// 必须重写此函数以告知GC该对象持有的引用
	static void AddReferencedObjects(UObject* InThis, FReferenceCollector& Collector);
};
```

## Demo 示例

一个最小的、可编译的 UAF 自动化测试用例框架。

### TestTraitExample.h
```cpp
#pragma once
#include "AnimNextTraitSharedData.h"
#include "Misc/AutomationTest.h"

// 1. 定义一个简单的特质共享数据
USTRUCT()
struct FExampleTraitSharedData : public FAnimNextTraitSharedData
{
	GENERATED_BODY()

	UPROPERTY()
	int32 Value = 42;
};

// 2. 声明一个自动化测试
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FUAFTestSuite_ExampleTest,
	"UAF.Traits.Example.BasicFunctionality",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
```

### TestTraitExample.cpp
```cpp
#include "TestTraitExample.h"
#include "AnimNextAnimGraph.h"
#include "AnimNextTrait.h"

bool FUAFTestSuite_ExampleTest::RunTest(const FString& Parameters)
{
	// 3. 创建一个临时的动画图实例
	UUAFAnimGraph* AnimGraph = NewObject<UUAFAnimGraph>();
	FAnimNextGraphInstance GraphInstance;
	GraphInstance.Initialize(AnimGraph, nullptr);

	// 4. 创建一个特质实例（伪代码，实际需要通过特质工厂创建）
	// FAnimNextTrait Trait;
	// Trait.Initialize(GraphInstance, /* TraitTemplate */);

	// 5. 模拟设置共享数据
	FExampleTraitSharedData SharedData;
	SharedData.Value = 100;

	// 6. 执行断言
	TestEqual(TEXT("Trait value should be 100"), SharedData.Value, 100);

	// 7. 清理（由引擎自动处理UObject）
	return true;
}
```

## 模块依赖

该插件作为 UAF 框架的测试套件，主要依赖 UAF 框架本身及其相关模块。对于希望**扩展或复用**其中测试代码的开发者，需要在自己的模块 Build.cs 中添加以下依赖。

| 模块 | 用途 |
|---|---|
| `AnimNextCore` | UAF 动画框架的核心运行时模块，提供特质、动画图、事件等基础类型。 |
| `AnimGraphRuntime` | 动画图运行时支持。 |
| `RigVM` | 用于测试动画图与 RigVM 的集成（见 `GCTestsUtil.h` 中的 `FRigUnit`）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复编译器警告，提升跨平台兼容性。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正格式化字符串的位数匹配问题，防止潜在错误。 |
| 2026-04-14 | `12eb7efc` | Fix FBindableXxx binding serialization issues when used with UAF traits | 修复与UAF特质结合使用时，绑定序列化的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移，采用新的格式化标准。 |
| 2026-04-10 | `797a6da6` | Rename GetComponent to GetOrAddComponent to match functionality | 重命名函数以更准确地反映其“获取或创建”的功能。 |

### 维护评价

- **创建时间**：插件于 2026 年 2 月首次提交，历史非常短。
- **更新频率**：截至 2026 年 5 月仍有活跃更新，最近几次提交集中在 **修复编译警告、跨平台兼容性和序列化问题**，属于持续的维护和健壮性改进工作。
- **活跃度**：**活跃维护中**。作为 Epic 官方实验性动画框架的测试套件，它与核心 `AnimNext` 模块同步更新，以确保框架的稳定性。
- **已知问题**：无公开的已知问题。但因为它标记为 **实验性 (`IsExperimentalVersion`)** 且 **默认未启用**，其内部 API 和测试用例可能会随着 UAF 框架的演进而发生 breaking changes。
- **推荐使用**：**仅推荐给正在开发或深度定制 UAF 动画框架的开发者**。对于普通项目用户，无需关注此插件。它是一个优秀的参考，展示了如何为复杂的动画中间件编写全面的自动化测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites)
- [测试用例目录](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites/Source) (各模块 `Private/` 目录下的 `*Test*.cpp` 文件)