# Motion Design Scene State

> （描述为空）

| 属性 | 值 |
|---|---|
| 中文名 | 场景状态 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SceneState` (Runtime), `SceneStateBinding` (Runtime), `SceneStateBlueprint` (Runtime), `SceneStateBlueprintEditor` (Runtime), `SceneStateEditor` (Runtime), `SceneStateEvent` (Runtime), `SceneStateEventEditor` (Runtime), `SceneStateEventGraph` (Runtime), `SceneStateGameplay` (Runtime), `SceneStateGameplayEditor` (Runtime), `SceneStateMachineEditor` (Runtime), `SceneStateMachineGraph` (Runtime), `SceneStateTasks` (Runtime), `SceneStateTransitionGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneState) | |

## 用途

SceneState 插件是一个面向运动设计（Motion Design）和虚拟制作（Virtual Production）的运行时状态与数据绑定系统。其核心在于提供一套统一、类型安全的属性绑定框架，用于在场景状态的各种数据（如根数据、任务、事件处理器、状态机等）之间建立数据流。这解决了在复杂、动态的虚拟制作场景中，如何高效、可靠地在不同组件和系统间同步和驱动属性数据的问题。它不仅仅是一个简单的数据拷贝系统，还支持通过属性引用（Property Reference）进行引用传递和写入，以及通过绑定函数（Binding Function）进行数据转换和自定义计算。

## 使用场景

- **运动设计实时控制**：在控制舞台灯光、动画参数或材质效果时，需要将一个输入设备（如旋钮、滑块）的值，实时映射到多个下游系统的属性上（如光强、颜色、位置偏移）。
- **动态参数驱动**：当一个任务（Task）的输出属性（例如计算出的速度）需要影响另一个任务的输入属性（例如移动组件的速度）时，通过属性绑定自动化数据传递，避免手动蓝图连线。
- **复杂状态机内的数据共享**：在驱动一个复杂的场景状态机时，多个状态或转换条件可能需要访问和修改同一个底层数据源（如一个共享的 `Property Bag`），该系统确保数据访问的路径是正确和有效的。
- **构建可复用的自定义逻辑块**：通过实现 `ISceneStateBindingCollectionOwner` 接口和定义带有 `RefType` 元数据说明符的属性引用，可以创建能够在蓝图中使用的、支持绑定输入输出的任务节点。

## 蓝图用法

此插件主要提供的是底层的属性绑定基础设施，直接面向蓝图的节点较少，更多用于支持其他蓝图节点（如任务）的功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FSceneStateBlueprintPropertyReference` (Struct) | 蓝图中可用的属性引用类型，可在任务参数中使用，用于指定要引用的属性类型（如 Float, Vector, Actor 等）。 | `FSceneStateBlueprintPropertyReference` |

### 使用示例（蓝图描述）

1.  **在任务参数中使用属性引用**：
    *   创建一个自定义任务（Task），其 `UPROPERTY` 中包含一个 `FSceneStateBlueprintPropertyReference` 类型的变量，并添加 `RefType` 元数据（如 `RefType="float"`）来限定可引用的属性类型。
    *   在场景状态蓝图或状态机编辑器中配置此任务时，你将看到一个属性选择器，它允许你从场景状态数据结构的可用属性中选择一个 `float` 类型的属性。
    *   任务执行时，可以通过绑定系统获得对该属性的引用并读写其值。

## C++ 用法

### 头文件引入

使用 `SceneStateBinding` 模块的核心功能：
```cpp
#include "SceneStateBindingCollection.h"
#include "SceneStateBindingDataHandle.h"
#include "SceneStatePropertyReference.h"
#include "SceneStatePropertyReferenceUtils.h"
```

### 基本用法

以下示例展示了如何获取一个属性绑定集合，并通过已解析的引用来访问数据。注意：这通常在框架内部调用，而非用户直接使用，但有助于理解其机制。

```cpp
// 假设 InBindingCollection 是一个有效的 FSceneStateBindingCollection
// 假设 InResolvedReference 是一个从绑定集合中获取的已解析引用
// 假设 InDataView 是包含目标数据的视图

FSceneStateBindingCollection& BindingCollection = /* ... 获取绑定集合 ... */;
const FSceneStateBindingResolvedReference& ResolvedReference = /* ... 从某处获取 ... */;
FPropertyBindingDataView DataView = /* ... 获取数据视图 ... */;

// 通过绑定集合解析属性，获取数据的原始内存指针
uint8* PropertyPtr = BindingCollection.ResolveProperty(ResolvedReference, DataView);
if (PropertyPtr)
{
    // 假设我们知道这是一个 float 属性
    float* FloatPtr = reinterpret_cast<float*>(PropertyPtr);
    *FloatPtr = 42.0f; // 写入值
}
```

### 进阶用法

结合数据句柄和类型检查来更安全地操作数据。

```cpp
#include "SceneStateBindingCollection.h"
#include "SceneStateBindingDataHandle.h"
#include "SceneStatePropertyReferenceUtils.h"

// 检查某个属性是否为有效的属性引用
const FProperty* SomeProperty = /* ... */;
bool bIsRef = UE::SceneState::IsPropertyReference(SomeProperty);

// 创建一个指向特定类型数据的句柄
FSceneStateBindingDataHandle TaskDataHandle(ESceneStateDataType::Task, /*TaskIndex*/0);

// 在编辑器中，根据属性引用获取其允许绑定的Pin类型
#if WITH_EDITOR
FSceneStateBlueprintPropertyReference BlueprintRef;
// ... 配置 BlueprintRef 的类型和 TypeObject ...
TArray<FEdGraphPinType, TInlineAllocator<1>> AllowedPinTypes = UE::SceneState::GetPropertyReferencePinTypes(BlueprintRef);
#endif
```

## Demo 示例

一个最小示例，演示如何定义一个拥有属性引用成员的简单结构体，并使用类型辅助模板进行验证。

**SceneStateBindingDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "SceneStatePropertyReference.h" // 基类
#include "SceneStateBlueprintPropertyReference.h" // 蓝图版本
#include "SceneStatePropertyReferenceUtils.h" // 类型辅助
#include "SceneStateBindingDemo.generated.h"

USTRUCT(BlueprintType)
struct FMyTaskInputParams
{
	GENERATED_BODY()

	// 这是一个蓝图可用的属性引用，只能绑定到 bool 类型的属性
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Input", meta=(RefType="bool"))
	FSceneStateBlueprintPropertyReference EnabledReference;

	// 这是一个属性引用，可以绑定到 float 或 TArray<float>
	UPROPERTY(EditAnywhere, Category="Input", meta=(RefType="float", CanRefToArray))
	FSceneStatePropertyReference SpeedReference;
};

// 演示如何使用 TDataTypeHelper
void ValidatePropertyCompatibility(const FProperty* InProperty)
{
	// 检查属性是否可以被当作 float 类型处理
	bool bIsValidFloat = UE::SceneState::TDataTypeHelper<float>::IsValid(InProperty);

	// 检查属性是否可以被当作 FVector 类型处理 (Vector 是 UScriptStruct)
	bool bIsValidVector = UE::SceneState::TDataTypeHelper<FVector>::IsValid(InProperty);

	// 检查属性是否可以被当作 AActor* 类型处理
	bool bIsValidActor = UE::SceneState::TDataTypeHelper<AActor*>::IsValid(InProperty);
}
```

## 模块依赖

此插件的 `SceneStateBinding` 模块为其他模块提供了核心绑定逻辑。由于未提供具体的 `Build.cs` 文件，无法列出精确依赖。通常，此类运行时绑定模块会依赖：
- `PropertyBindingRuntime`（提供基础的属性绑定框架 `FPropertyBindingBindingCollection` 等）
- `StructUtils`（用于 `FInstancedStruct` 等）
- `CoreUObject`（用于反射和 `UStruct` 操作）

使用者（如 `SceneStateTasks` 模块）需要依赖 `SceneStateBinding` 模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated with a scene | 重构视口关联逻辑，优化代码结构。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退了之前的某个提交 CL53913857。 |
| 2026-04-17 | `6e111b5d` | Motion Design Scene State: fixed issues with bindings not checking for null event payload struct (ops) | 修复了绑定在事件负载结构体为空时未进行检查的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF。 |

### 维护评价

- **活跃维护**：插件创建于 2025 年 8 月，属于非常新的功能。截至 2026 年 5 月仍有频繁的功能性提交和错误修复（如空指针检查、日志系统迁移、代码重构）。
- **状态**：目前标记为 `IsBetaVersion` (实验性)，且 `EnabledByDefault` 为 `false`，表明它仍处于开发和完善阶段，API 可能会变动。
- **推荐使用**：**谨慎使用**。适合在运动设计或虚拟制作的前沿项目中进行原型开发和功能探索。由于其是 Beta 状态且较为新颖，不建议在需要长期稳定性的生产环境中直接依赖。应持续关注其后续版本更新和 API 变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SceneState)
- [官方文档]()（暂无）
- [测试用例]()（未在提供路径中发现标准测试文件）