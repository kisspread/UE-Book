# Motion Design Scene State

> （Description 为空）

| 属性 | 值 |
|---|---|
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、图表资产） |
| 模块 | `SceneState` (Runtime), `SceneStateBinding` (Runtime), `SceneStateBlueprint` (Runtime), `SceneStateBlueprintEditor` (Runtime), `SceneStateEditor` (Runtime), `SceneStateEvent` (Runtime), `SceneStateEventEditor` (Runtime), `SceneStateEventGraph` (Runtime), `SceneStateGameplay` (Runtime), `SceneStateGameplayEditor` (Runtime), `SceneStateMachineEditor` (Runtime), `SceneStateMachineGraph` (Runtime), `SceneStateTasks` (Runtime), `SceneStateTransitionGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneState) | |

## 用途

SceneState 是一个面向虚拟制片（Virtual Production）和动态设计（Motion Design）的**场景状态机系统**。它提供了一套完整的状态机框架，用于管理场景中对象的状态转换、属性绑定、事件响应和任务执行。

核心解决的问题：
- **场景状态管理**：通过可视化状态机图表管理复杂场景的状态流转（如灯光切换、材质变化、动画触发等）
- **属性绑定**：将源属性自动绑定到目标属性，实现数据驱动的场景控制
- **事件驱动**：支持事件触发状态转换和任务执行
- **任务系统**：在状态中执行具体的场景操作任务
- **蓝图集成**：允许通过蓝图定义自定义任务和参数

该插件本质上是一个**场景编排引擎**，让设计师可以通过可视化图表定义"当场景处于某个状态时，执行哪些操作，满足什么条件时切换到下一个状态"。

## 使用场景

- 你在做虚拟制片项目，需要管理灯光、材质、动画等多个元素的状态切换 → 用 SceneState
- 你需要一个可视化的状态机来编排复杂的场景序列 → 用 SceneState 的状态机图表
- 你需要将场景中不同对象的属性相互绑定（如将一个参数同时驱动多个材质参数）→ 用 SceneState 的属性绑定系统
- 你需要在特定状态转换时触发自定义逻辑 → 用 SceneState 的事件系统和任务系统

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BuildFromPinType` | 根据蓝图引脚类型构建属性引用实例 | `FSceneStateBlueprintPropertyReference` |
| `GetReferenceType` | 获取属性引用的类型（Bool/Int/Float/Struct/Object 等） | `FSceneStateBlueprintPropertyReference` |
| `IsReferenceToArray` | 判断引用是否指向数组 | `FSceneStateBlueprintPropertyReference` |
| `GetTypeObject` | 获取引用的 ScriptStruct、Class 或 Enum 对象 | `FSceneStateBlueprintPropertyReference` |

### 属性引用类型

`FSceneStateBlueprintPropertyReference` 支持以下引用类型：

| 类型 | 说明 |
|---|---|
| `Bool` | 布尔值引用 |
| `Byte` | 字节引用 |
| `Int32` / `Int64` | 整数引用 |
| `Float` / `Double` | 浮点数引用 |
| `Name` / `String` / `Text` | 字符串类型引用 |
| `Enum` | 枚举引用 |
| `Struct` | 结构体引用 |
| `Object` / `SoftObject` | 对象引用 |
| `Class` / `SoftClass` | 类引用 |

### 使用示例（蓝图描述）

1. **创建属性引用**：在蓝图任务中，使用 `FSceneStateBlueprintPropertyReference` 变量，通过编辑器下拉菜单选择引用类型（如 Float），然后在属性绑定面板中将其绑定到场景中某个对象的具体属性
2. **绑定属性**：在状态机编辑器中，将源数据（如根参数）的属性路径拖拽到目标任务的属性上，系统自动创建绑定关系
3. **数组引用**：设置 `bIsReferenceToArray = true` 可以引用整个数组，而非单个元素

## C++ 用法

### 头文件引入

```cpp
#include "SceneStateBindingCollection.h"
#include "SceneStateBinding.h"
#include "SceneStateBindingDesc.h"
#include "SceneStatePropertyReference.h"
#include "SceneStateBlueprintPropertyReference.h"
#include "SceneStateBindingUtils.h"
```

### 基本用法

```cpp
// 来源: SceneStateBinding/Public/SceneStateBindingDataHandle.h

// 创建数据句柄，指向不同类型的数据源
FSceneStateBindingDataHandle RootHandle(ESceneStateDataType::Root);
FSceneStateBindingDataHandle TaskHandle(ESceneStateDataType::Task, /*DataIndex=*/0);
FSceneStateBindingDataHandle EventHandlerHandle(ESceneStateDataType::EventHandler, /*DataIndex=*/1);
FSceneStateBindingDataHandle StateMachineHandle(ESceneStateDataType::StateMachine, /*DataIndex=*/0, /*SubIndex=*/2);

// 检查句柄有效性
if (TaskHandle.IsValid())
{
    ESceneStateDataType DataType = static_cast<ESceneStateDataType>(TaskHandle.GetDataType());
    uint16 DataIndex = TaskHandle.GetDataIndex();
    uint16 DataSubIndex = TaskHandle.GetDataSubIndex();
}
```

### 属性引用用法

```cpp
// 来源: SceneStateBinding/Public/SceneStatePropertyReference.h

// 属性引用允许绑定系统以引用方式（而非拷贝）处理属性
FSceneStatePropertyReference PropRef;
if (PropRef.IsValidIndex())
{
    // 引用有效，可以通过绑定集合和执行上下文获取实际属性数据
    // ReferenceIndex 同时指向 Reference 和 Resolved Reference
}

// 蓝图属性引用（带类型信息）
// 来源: SceneStateBinding/Public/SceneStateBlueprintPropertyReference.h
FSceneStateBlueprintPropertyReference BlueprintRef;
ESceneStatePropertyReferenceType RefType = BlueprintRef.GetReferenceType();
bool bIsArray = BlueprintRef.IsReferenceToArray();
UObject* TypeObj = BlueprintRef.GetTypeObject();
```

### 绑定集合作用法

```cpp
// 来源: SceneStateBinding/Public/SceneStateBindingCollection.h

// 获取绑定集合（通过 ISceneStateBindingCollectionOwner 接口）
ISceneStateBindingCollectionOwner* Owner = /* ... */;
FSceneStateBindingCollection& BindingCollection = Owner->GetBindingCollection();

// 遍历所有绑定
BindingCollection.ForEachBinding([](const FPropertyBindingBinding& Binding)
{
    // 处理每个绑定
});

// 查找绑定描述
FSceneStateBindingDataHandle DataHandle(ESceneStateDataType::Task, 0);
const FSceneStateBindingDesc* Desc = BindingCollection.FindBindingDesc(DataHandle);

// 解析属性引用
FSceneStatePropertyReference PropRef;
const FSceneStateBindingResolvedReference* ResolvedRef = BindingCollection.FindResolvedReference(PropRef);
```

### 进阶用法

```cpp
// 来源: SceneStateBinding/Public/SceneStateBindingUtils.h

// 编辑器下：处理结构体 ID 变更时更新绑定
#if WITH_EDITOR
UE::SceneState::HandleStructIdChanged(*MyObject, OldStructId, NewStructId);
#endif

// 修补绑定集合中失效的结构体（属性包、用户定义结构体等）
UE::SceneState::FPatchBindingParams PatchParams;
PatchParams.BindingCollection = BindingCollection;
PatchParams.FindDataStructFunctor = [](const FSceneStateBindingDataHandle& Handle) -> const UStruct*
{
    // 根据句柄查找对应的 UStruct
    return nullptr;
};
UE::SceneState::PatchBindingCollection(PatchParams);

// 来源: SceneStateBinding/Public/SceneStateBindingCollectionOwner.h
// 实现绑定集合所有者接口
class UMySceneStateObject : public UObject, public ISceneStateBindingCollectionOwner
{
    // 实现 GetBindingCollection()
    virtual FSceneStateBindingCollection& GetBindingCollection() override;
    virtual const FSceneStateBindingCollection& GetBindingCollection() const override;

#if WITH_EDITOR
    // 实现可绑定函数遍历
    virtual bool ForEachBindableFunction(
        TFunctionRef<bool(const FSceneStateBindingDesc&, const UE::SceneState::FBindingFunctionInfo&)> InFunc) const override;
#endif
};
```

## Demo 示例

```cpp
// MySceneStateTask.h
#pragma once

#include "SceneStatePropertyReference.h"
#include "UObject/Object.h"
#include "MySceneStateTask.generated.h"

UCLASS()
class UMySceneStateTask : public UObject
{
    GENERATED_BODY()

public:
    // 属性引用：允许在编辑器中绑定到场景中的任意 Float 属性
    // RefType 元数据指定引用的属性类型
    UPROPERTY(EditAnywhere, Category="Scene State", meta=(RefType="float"))
    FSceneStatePropertyReference FloatPropertyRef;

    // 蓝图属性引用：可在蓝图中使用，带完整类型信息
    UPROPERTY(EditAnywhere, Category="Scene State", BlueprintReadWrite)
    FSceneStateBlueprintPropertyReference BlueprintRef;

    // 执行任务
    UFUNCTION(BlueprintCallable, Category="Scene State")
    void ExecuteTask()
    {
        if (FloatPropertyRef.IsValidIndex())
        {
            // 通过绑定集合解析引用并获取实际数据
            // 实际使用需要配合 FSceneStateBindingCollection 和执行上下文
        }
    }
};
```

```cpp
// MySceneStateTask.cpp
#include "MySceneStateTask.h"
#include "SceneStateBindingCollection.h"
#include "SceneStateBindingUtils.h"

void UMySceneStateTask::ExecuteTask()
{
    // 在实际场景状态系统中，任务的执行由状态机框架驱动
    // 属性引用的解析通过 FSceneStateBindingCollection::ResolveProperty 完成
    // 这里展示的是任务定义的基本结构
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PropertyBinding` | 属性绑定基础框架（FPropertyBindingBinding、FPropertyBindingBindingCollection 等基类） |
| `StructUtils` | 结构体工具（FInstancedStruct、FStructView 等） |

## 维护状态

### 近期更新

```
- d53130edebd0 Motion Design Scene State: added actor reference for the spawned actor to be useable outside its task
- 9d2e4cc30738 Motion Design Scene State: fixed issue where copying tasks/etc would not copy over the function values (only type).
- 0a35bd340336 Motion Design Scene State: fixed issue where state machine parameters, etc would not appear in the property binding menu for functions. Additionally fixed an issue where binding extensions were not allocating function instances in execution.
```

### 维护评价

**⚠️ 实验性/Beta 插件，谨慎使用**

- **创建时间**：2025-04-22，非常新的插件（不到 1 年）
- **维护状态**：活跃开发中，近期有多次功能性更新和 bug 修复
- **代码规模**：701 个源文件，14 个模块，架构复杂且完整
- **已知限制**：
  - 标记为 Beta（`IsBetaVersion: true`），API 可能发生破坏性变更
  - 默认未启用（`Installed: false`），需手动在插件设置中启用
  - 属于 Experimental 分类，尚未正式发布
- **推荐程度**：适合在虚拟制片/动态设计项目中**试用和评估**，但不建议在生产环境中作为核心依赖。关注后续版本的稳定性改进。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneState)
- 官方文档（暂无）