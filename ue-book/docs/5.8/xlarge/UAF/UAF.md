# Unreal Animation Framework (UAF)

> Framework for defining functional data flow for animation systems（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 虚幻动画框架 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `UAF` (Runtime), `UAFEditor` (Runtime), `UAFTestData` (Runtime), `UAFUncookedOnly` (Runtime), `UAFTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-26 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF) | |

> ⚠️ 本插件默认未启用，需在插件管理器中手动启用。且标记为实验性（IsExperimentalVersion），API 可能在未来版本中发生破坏性变更。

---

## 文档结构

本文档为 xlarge 级插件的汇总索引页。UAF 源码规模超过 600 个文件，按功能划分为以下子模块文档：

| 子模块文档 | 说明 |
|---|---|
| [Module-System.md](Module-System.md) | UAF 系统核心：`UUAFSystem`、`FAnimNextModuleInstance`、`UUAFComponent`、事件系统、Tick 函数、任务队列 |
| [DataRegistry.md](DataRegistry.md) | 数据注册表：`FDataRegistry`、引用姿势管理、`FDataHandle` 引用计数内存 |
| [ValueRuntime.md](ValueRuntime.md) | 值运行时：`FValueBundle`/`FPoseValueBundle`、`FBoundValueMap`/`FUnboundValueMap`、属性集与映射 |
| [Transformers.md](Transformers.md) | 值变换器：Additive Space、自定义变换器注册、`FValueTransformerList` |
| [Variables-Types.md](Variables-Types.md) | 变量与类型系统：`FAnimNextParamType`、`FBindableValueBase` 系列、`FUAFAssetInstance`、`FUAFInstanceVariableData` |
| [Pose-Retargeting.md](Pose-Retargeting.md) | 姿势与重定向：`FLODPose`、`FTransformArray`、`FGenerationTools`、`FRetargetingTools` |
| [RigVM-Integration.md](RigVM-Integration.md) | RigVM 集成：`UUAFRigVMAsset`、RigUnit 节点、`FRigVMRuntimeDataRegistry` |

---

## 用途

UAF（Unreal Animation Framework，前身为 AnimNext）是 Epic 开发的下一代动画系统框架。它提供了一种**基于数据流的函数式动画管线**，取代传统 AnimGraph 的节点评估模型。

核心设计理念：
1. **模块化系统**：动画逻辑封装在 `UUAFSystem` 资产中，通过 `UUAFComponent` 挂载到 Actor
2. **事件驱动执行**：使用 RigVM 脚本定义事件（Initialize、PrePhysics、PostPhysics 等），在不同 Tick Group 中执行
3. **数据驱动变量**：通过 `FAnimNextParamType` 和 `FAnimNextVariableReference` 实现强类型变量系统，支持蓝图绑定
4. **值运行时（Value Runtime）**：新型属性数据容器，支持 Bound Map（属性集绑定）和 Unbound Map（名称映射）两种模式
5. **可组合变换器**：变换器（Transformer）机制用于处理加法动画、混合、重定向等操作
6. **引用计数数据管理**：`FDataRegistry` 和 `FDataHandle` 提供全局动画数据存储，带引用计数生命周期管理

## 使用场景

- 你需要构建一个**模块化、数据驱动的动画系统**，而不是传统 AnimGraph → 用 UAF
- 你需要自定义**动画事件的执行时序**（如物理更新前后精确控制）→ 用 UAF 的事件系统
- 你需要**高效管理大量动画属性数据**（骨骼变换、曲线、浮点值等）→ 用 Value Runtime
- 你需要**跨骨骼拓扑的动画重定向** → 用 `FRetargetingTools`
- 你需要将**动画逻辑从蓝图迁移到 RigVM 脚本**以获得更好的性能 → 用 UAF

## 蓝图用法

### 核心组件：UUAFComponent

`UUAFComponent` 是将 UAF 系统挂载到 Actor 的核心组件。继承自 `UActorComponent`。

#### 变量操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Variable` (by reference) | 设置系统变量的值，使用变量引用 | `UUAFComponent` |
| `Get Variable` (by reference) | 获取系统变量的值，使用变量引用 | `UUAFComponent` |
| `Set Input Binding` | 将另一个组件的输出绑定到系统变量 | `UUAFComponent` |

#### 调度依赖

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Component Prerequisite` | 添加组件的 Tick 前置依赖（组件先于事件执行） | `UUAFComponent` |
| `Add Component Subsequent` | 添加组件的 Tick 后续依赖（组件后于事件执行） | `UUAFComponent` |
| `Remove Component Prerequisite` | 移除前置依赖 | `UUAFComponent` |
| `Remove Component Subsequent` | 移除后续依赖 | `UUAFComponent` |
| `Add Module Event Prerequisite` | 添加 UAF 系统事件之间的前置依赖 | `UUAFComponent` |
| `Add Module Event Subsequent` | 添加 UAF 系统事件之间的后续依赖 | `UUAFComponent` |
| `Remove Module Event Prerequisite` | 移除系统事件前置依赖 | `UUAFComponent` |
| `Remove Module Event Subsequent` | 移除系统事件后续依赖 | `UUAFComponent` |

#### 系统查询

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get System Reference` | 获取系统实例的弱引用 | `UUAFComponent` |
| `Show Debug Drawing` | 启用/禁用调试绘制 | `UUAFComponent` |

### 使用示例（蓝图描述）

**基本设置：**
1. 在 Actor 上添加 `UUAFComponent`
2. 在组件的 `Animation` 分类中设置 `AssetData` 属性，选择一个 `UUAFSystem` 资产
3. 如需动画输出，在 `Output` 分类中指定 `OutputComponent`（通常是 `SkeletalMeshComponent`）
4. 在 `Input` 分类中添加 `Inputs` 数组，将其他 UAF 组件的输出映射到当前系统变量

**变量驱动动画：**
- 使用 `Set Variable`（by reference）节点，传入 `FAnimNextVariableReference` 和值来动态控制动画参数
- 使用 `Get Variable`（by reference）节点读取当前运行时变量值

**执行顺序控制：**
- 使用 `Add Component Prerequisite` 让某个组件在 UAF 系统的特定事件之前 Tick
- 例如：让 Character Movement Component 在 UAF 的 `PrePhysics` 事件之前执行

---

## C++ 用法

### 头文件引入

```cpp
#include "Component/AnimNextComponent.h"
#include "Module/AnimNextModule.h"
#include "Module/ModuleTaskContext.h"
#include "Module/SystemReference.h"
#include "DataRegistry.h"
#include "DataRegistryTypes.h"
```

### 基本用法：访问系统变量

通过 `UUAFComponent` 的 C++ 接口设置和获取变量：

```cpp
#include "Component/AnimNextComponent.h"

// 假设已有 UUAFComponent* AnimNextComponent 和 FAnimNextVariableReference VariableRef

// 设置变量（模板方式，类型安全）
float NewSpeed = 300.0f;
AnimNextComponent->SetVariable(VariableRef, NewSpeed);

// 获取变量
float OutSpeed = 0.0f;
if (AnimNextComponent->GetVariable(VariableRef, OutSpeed))
{
    // 使用 OutSpeed
}

// 零拷贝写入（适用于大型数据结构）
AnimNextComponent->WriteVariable<FTransform>(VariableRef, [](FTransform& OutTransform)
{
    OutTransform = FTransform(FRotator(0, 90, 0), FVector(100, 0, 0));
});
```

来源：`Public/Component/AnimNextComponent.h` — `SetVariable<T>`, `GetVariable<T>`, `WriteVariable<T>`

### 基本用法：数据注册表

`FDataRegistry` 是全局单例，用于管理动画数据的引用计数生命周期：

```cpp
#include "DataRegistry.h"
#include "DataRegistryTypes.h"

// 获取全局注册表
UE::UAF::FDataRegistry* Registry = UE::UAF::FDataRegistry::Get();

// 注册引用姿势（骨骼网格体）
UE::UAF::FDataHandle RefPoseHandle = Registry->GetOrGenerateReferencePose(MySkeletalMesh);

// 分配自定义数据
FDataHandle CustomData = Registry->AllocateData<FTransform>(NumBones, FTransform::Identity);
TArrayView<FTransform> Transforms = CustomData.AsArrayView<FTransform>();

// 注册命名数据
Registry->RegisterData(FName("MyCustomPose"), CustomData);

// 稍后获取
FDataHandle Retrieved = Registry->GetRegisteredData(FName("MyCustomPose"));
```

来源：`Public/DataRegistry.h`

### 基本用法：执行任务队列

通过 `QueueTask` 在模块执行的特定事件点注入自定义逻辑：

```cpp
#include "Component/AnimNextComponent.h"
#include "Module/ModuleTaskContext.h"

// 在 PrePhysics 事件之前注入任务
AnimNextComponent->QueueTask(
    FName("PrePhysics"),
    [MyData](const UE::UAF::FModuleTaskContext& Context)
    {
        // 在此访问模块实例、组件、变量等
        // MyData 捕获的外部数据
    },
    UE::UAF::ETaskRunLocation::Before
);

// 在系统执行前注入任务（第一个用户事件之前）
AnimNextComponent->QueueTask(
    FName(),
    [](const UE::UAF::FModuleTaskContext& Context)
    {
        // 初始化逻辑
    },
    UE::UAF::ETaskRunLocation::Before
);
```

来源：`Internal/Module/AnimNextModuleInstance.h` — `QueueTask`, `Public/Module/ModuleTaskContext.h`

### 进阶用法：Value Bundle 操作

`FPoseValueBundle` 提供对动画姿势数据的高层访问：

```cpp
#include "UAF/ValueRuntime/PoseValueBundle.h"
#include "UAF/ValueRuntime/BoundValueMap.h"

// 假设有一个 FPoseValueBundle* PoseBundle

// 查找骨骼变换映射
TBoundValueMap<FBoneTransformAnimationAttribute>* BoneTransforms = PoseBundle->FindBoneTransforms();
if (BoneTransforms)
{
    // 按索引访问
    FTransform CurrentTransform = (*BoneTransforms)[BoneIndex].Value;

    // 修改
    (*BoneTransforms)[BoneIndex].Value = NewTransform;

    // 按名称查找
    FAttributeTypedSetPtr TypedSet = BoneTransforms->GetTypedSet();
    FAttributeSetIndex HeadIndex = TypedSet->FindIndex(FName("head"));
    if (HeadIndex.IsValid())
    {
        FTransform HeadTransform = (*BoneTransforms)[HeadIndex].Value;
    }
}

// 查找浮点曲线映射（Morph Targets、控制曲线等）
TBoundValueMap<FFloatAnimationAttribute>* FloatCurves = PoseBundle->FindFloatCurves();
if (FloatCurves)
{
    FAttributeTypedSetPtr FloatTypedSet = FloatCurves->GetTypedSet();
    FAttributeSetIndex Index = FloatTypedSet->FindIndex(FName("smile_left"));
    if (Index.IsValid())
    {
        (*FloatCurves)[Index].Value = 0.75f;
    }
}
```

来源：`Public/UAF/ValueRuntime/PoseValueBundle.h`

### 进阶用法：加法动画空间变换器

```cpp
#include "UAF/ValueRuntime/Transformers/AdditiveSpace.h"

// 创建加法空间姿势
UE::UAF::Transformers::FMakeAdditiveSpace::Apply(
    TransformerMap,  // FValueTransformerMapPtr
    BaseBundle,      // const FValueBundle& 基础姿势
    InputBundle,     // const FValueBundle& 输入姿势
    AdditiveOutput   // FValueBundle& 输出（输入 - 基础）
);

// 应用加法姿势（带权重）
UE::UAF::Transformers::FApplyAdditiveSpace::Apply(
    TransformerMap,
    BaseBundle,       // 基础姿势
    AdditiveBundle,   // 加法姿势
    0.5f,             // 混合权重
    OutputBundle      // 输出：Base + Lerp(Identity, Additive, Weight)
);

// 带逐骨骼权重的应用
UE::UAF::Transformers::FApplyAdditiveSpace::Apply(
    TransformerMap,
    BaseBundle,
    AdditiveBundle,
    PerValueWeights,  // FValueBundle，每骨骼权重
    0.5f,             // 默认权重
    OutputBundle
);
```

来源：`Public/UAF/ValueRuntime/Transformers/AdditiveSpace.h`

---

## Demo 示例

### 最小 UAF 系统组件使用

```cpp
// MyAnimActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Component/AnimNextComponent.h"
#include "MyAnimActor.generated.h"

UCLASS()
class AMyAnimActor : public AActor
{
    GENERATED_BODY()

public:
    AMyAnimActor();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

protected:
    // UAF 系统组件
    UPROPERTY(VisibleAnywhere, Category = "Animation")
    TObjectPtr<UUAFComponent> AnimComponent;

    // 可视化组件
    UPROPERTY(VisibleAnywhere, Category = "Mesh")
    TObjectPtr<USkeletalMeshComponent> MeshComponent;
};
```

```cpp
// MyAnimActor.cpp
#include "MyAnimActor.h"
#include "Component/AnimNextComponent.h"

AMyAnimActor::AMyAnimActor()
{
    PrimaryActorTick.bCanEverTick = true;

    MeshComponent = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("Mesh"));
    RootComponent = MeshComponent;

    AnimComponent = CreateDefaultSubobject<UUAFComponent>(TEXT("Anim"));
    AnimComponent->SetupAttachment(MeshComponent);
}

void AMyAnimActor::BeginPlay()
{
    Super::BeginPlay();

    // 获取系统引用（可用于后续操作）
    FUAFWeakSystemReference SystemRef = AnimComponent->GetSystemReference();
}

void AMyAnimActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
}
```

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveCoding` | 编辑器中的实时代码重编译支持 |

无其他特殊依赖（仅标准 Core/Engine/Slate/RigVM 等）。UAF 内部模块（如 `UAFEditor`、`UAFUncookedOnly`、`UAFTestData`）之间有互相依赖，但对外部使用者透明。

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `eeaff753` | UAF: Introduce optional tick dependency between the UAF Component targeting a ACharacters mesh compo | 新增 UAF 组件与角色移动组件之间的可选 Tick 依赖关系 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复跨编译器（MSVC/Clang）函数类型转换警告的可移植性 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复作用域枚举在格式化函数中导致乱码输出的问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配问题 |
| 2026-04-24 | `523ac953` | Fix incorrect quaternion attribute type usage | 修复四元数属性类型使用错误 |

### 维护评价

**活跃维护** ✅

- **创建时间**：2025-06-26（约 1 年前）
- **最近更新**：2026-05-12，持续活跃开发中
- **更新频率**：近期（2026-04~05）有多次实质性功能更新和 bug 修复
- **来源**：从 AnimNext 插件重命名/迁移而来（2025-06-26 首次提交信息："Moved/renamed AnimNext and AnimNextAnimGraph plugins"），因此底层代码历史更长
- **状态**：标记为实验性（IsExperimentalVersion），API 仍在演进中
- **推荐**：适合进行前瞻性的动画系统研究和原型开发。不建议在生产环境的稳定版本中直接使用，因为 API 可能发生破坏性变更。如果要用于生产，建议在引擎版本锁定后开始集成

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF)
- 官方文档（暂无）