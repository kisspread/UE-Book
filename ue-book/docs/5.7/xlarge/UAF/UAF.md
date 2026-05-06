# Unreal Animation Framework (UAF)

> Framework for defining functional data flow for animation systems

| 属性 | 值 |
|---|---|
| 中文名 | 动画框架 (UAF) |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画蓝图资产、模块系统、RigVM 图、参数定义） |
| 模块 | `UAF` (Runtime), `UAFEditor` (Runtime), `UAFTestSuite` (Runtime), `UAFUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-25 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAF) | |

## 用途

UAF（虚幻动画框架）是一个基于 **RigVM** 和 **事件驱动** 的模块化动画数据流框架。它允许开发者以**功能性数据流**的方式定义动画系统的行为，而无需编写传统的动画蓝图或状态机。

该框架的核心思路是将动画逻辑拆解为独立的**模块（Module）**，每个模块包含若干**事件（Event）**，事件内部通过 RigVM 图表执行计算，并支持**参数（Parameter）** 的显式输入/输出绑定。模块之间通过**依赖关系**（前置/后置）进行排序，从而构建出完整的动画更新管线。

主要特性：
- **模块化结构**：每个 `UAnimNextModule` 是一个自包含的动画单元，包含所需的组件、变量和事件图。
- **事件驱动执行**：模块内的事件（如 `BeginExecution`、`PostPhysics`）按依赖顺序在指定线程（Game Thread 或 Worker Thread）上执行。
- **RigVM 集成**：事件图使用 RigVM 节点，支持自定义 RigVM 分发器（如参数读写、对象定位器解析）。
- **参数系统**：通过 `UAnimNextParam` 等类型定义强类型参数，支持在模块之间、蓝图和 C++ 之间传递数据。
- **Trait 系统**：基于 `FRigVMTrait` 的扩展，允许将变量、组件等暴露为可编程引脚。
- **模块实例组件**：通过 `FUAFModuleInstanceComponent` 派生类（如 `FAnimNextSkeletalMeshComponentReferenceComponent`）自动获取外部游戏对象引用。

## 使用场景

- 你需要为角色设计一套**可重用的、数据驱动的动画系统**，代替传统的动画蓝图状态机。
- 你希望将动画逻辑拆解为**独立的模块**，并精确控制每个模块的执行顺序和线程（Game Thread / Worker Thread）。
- 你需要在动画系统中**动态绑定外部游戏对象**（如 Actor 组件、骨骼网格体组件）的数据。
- 你正在进行**实验性动画技术**的研究，需要一个灵活、可编程的控制框架。

## 蓝图用法

UAF 插件主要面向 C++ 开发者，但在编辑器模式下，用户可以通过 **RigVM 图表**（通过模块编辑器）进行可视化的蓝图式编程。以下为通过 C++ 暴露给蓝图的关键 API。

### 核心节点（蓝图可调用函数）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `QueueInputTraitEvent` | 将一个输入 Trait 事件加入队列，在下次图更新时处理 | `UAnimNextWorldSubsystem` |
| `QueueOutputTraitEvent` | 将一个输出 Trait 事件加入队列，在本次调度末尾处理 | `UAnimNextWorldSubsystem` |
| `ShowDebugDrawing` | 启用/禁用该模块实例的调试绘制 | `UAnimNextModuleInstance` |
| `GetModule` | 获取该实例对应的 `UAnimNextModule` 资产 | `UAnimNextModuleInstance` |
| `FindFirstUserTickFunction` | 查找第一个用户定义的事件 TickFunction | `UAnimNextModuleInstance` |

### 使用示例（蓝图描述）

1. **创建模块实例**（通过 World Subsystem）：
   - 在 Game Mode 或 Player Controller 中，获取 `UAnimNextWorldSubsystem`。
   - 调用 `CreateModuleInstance`（需指定 `UAnimNextModule` 资产和绑定对象）。
   - 子系统会分配一个 `FAnimNextModuleInstance` 并开始调度事件。

2. **向模块发送游戏事件**：
   - 在玩家输入或碰撞触发时，获取 `UAnimNextWorldSubsystem` 实例。
   - 调用 `QueueInputTraitEvent`，传入一个 `FAnimNextTraitEventPtr`（Traits 事件的智能指针）。
   - 模块在下一个 Tick 时处理该事件。

3. **启用调试绘制**：
   - 从模块实例（通过 `FAnimNextModuleInstance` 的 `ShowDebugDrawing(true)`）启用。
   - 在视口中查看 RigVM 绘制的调试线条。

## C++ 用法

### 头文件引入

```cpp
#include "Component/AnimNextWorldSubsystem.h"
#include "Module/AnimNextModuleInstance.h"
#include "Module/AnimNextModule.h"
```

### 基本用法

以下代码演示了如何获取 World Subsystem、创建模块实例、并触发事件（来自 `AnimNextWorldSubsystem.h` 和测试用例）：

```cpp
// 假设你已经有一个 UAnimNextModule 资产（通过 LoadObject 或引用）
UAnimNextModule* MyModule = LoadObject<UAnimNextModule>(nullptr, TEXT("/Game/MyModule.MyModule"));

// 获取 World Subsystem
UWorld* World = GetWorld();
UAnimNextWorldSubsystem* Subsystem = UAnimNextWorldSubsystem::Get(World);
if (Subsystem)
{
    // 创建模块实例，绑定到某个 Actor
    UE::UAF::FModulePendingAction* Action = Subsystem->CreateModuleInstance(
        MyModule,
        MyActor,
        EAnimNextModuleInitMethod::Immediate  // 或 Delayed
    );

    // 创建一个输入 Trait 事件（假设有自定义事件类型）
    TSharedPtr<FAnimNextTraitEvent> InputEvent = MakeShared<FAnimNextTraitEvent>(/* ... */);
    Subsystem->QueueInputTraitEvent(InputEvent);
}
```

**来源**：`Component/AnimNextWorldSubsystem.h`、`Module/AnimNextModuleInstance.h`

### 进阶用法：自定义模块实例组件

模块实例组件（继承 `FUAFModuleInstanceComponent`）允许在模块初始化时自动绑定游戏对象。以下示例展示了如何创建一个引用骨骼网格体组件的组件：

```cpp
// 定义组件结构体（需 USTRUCT）
USTRUCT()
struct FMySkeletalMeshComponent : public FAnimNextSkeletalMeshComponentReferenceComponent
{
    GENERATED_BODY()

    FMySkeletalMeshComponent()
    {
        ComponentType = USkeletalMeshComponent::StaticClass();
    }

    // 可添加自定义数据
    UPROPERTY()
    float MyCustomScale = 1.0f;
};

// 在模块中注册该组件（通过 UAnimNextModule 的 RequiredComponents）
// 通常由编辑器处理，但也可在代码中动态添加
```

```cpp
// 在模块实例的 Tick 函数中访问该组件
void ExecuteMyEvent(const FAnimNextExecuteContext& Context)
{
    const FAnimNextModuleContextData& ContextData = Context.GetContextData<FAnimNextModuleContextData>();
    FAnimNextModuleInstance& Instance = ContextData.GetModuleInstance();

    // 获取组件实例（假设组件名为 "SkeletalMeshRef"）
    const FMySkeletalMeshComponent* Component = Instance.FindComponent<FMySkeletalMeshComponent>(TEXT("SkeletalMeshRef"));
    if (Component)
    {
        USkeletalMeshComponent* SkelMesh = Component->GetComponent();
        if (SkelMesh)
        {
            // 使用骨骼网格体
            SkelMesh->SetRelativeScale3D(FVector(Component->MyCustomScale));
        }
    }
}
```

**用法说明**：模块实例组件使得模块可以直接访问外观对象，无需手动注册 Tick 依赖关系。

### 参数系统

UAF 提供了一套基于 `FAnimNextParamType` 和 `RigVMDispatch` 的参数传递机制。以下是一个获取/设置参数的 RigVM 分发器示例：

```cpp
// 获取参数
void FRigVMDispatch_GetParameter::Execute(FRigVMExtendedExecuteContext& InContext, FRigVMMemoryHandleArray Handles, FRigVMPredicateBranchArray RigVMBranches)
{
    // 从 Handle 中取出参数 ID 和类型
    // 从模块实例的变量存储中获取值
    // ... 参考测试用例
}

// 设置参数
void FRigVMDispatch_SetLayerParameter::Execute(FRigVMExtendedExecuteContext& InContext, FRigVMMemoryHandleArray Handles, FRigVMPredicateBranchArray RigVMBranches)
{
    // 类似原理，但执行写入
}
```

这些分发器通常由编译器自动插入到事件图中，用户无需直接调用。

## Demo 示例

以下是一个最小的可编译示例，演示如何在 GameMode 中创建并使用 UAF 模块实例。

**ModuleDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "ModuleDemo.generated.h"

UCLASS()
class AModuleDemoGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    AModuleDemoGameMode();

    virtual void BeginPlay() override;

    virtual void Tick(float DeltaTime) override;

private:
    class UAnimNextWorldSubsystem* Subsystem = nullptr;
    class UAnimNextModule* MyModuleAsset = nullptr;
    UE::UAF::FModuleHandle ModuleHandle;
};
```

**ModuleDemo.cpp**
```cpp
#include "ModuleDemo.h"
#include "Component/AnimNextWorldSubsystem.h"
#include "Module/AnimNextModule.h"
#include "Module/AnimNextModuleInstance.h"

AModuleDemoGameMode::AModuleDemoGameMode()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AModuleDemoGameMode::BeginPlay()
{
    Super::BeginPlay();

    UWorld* World = GetWorld();
    if (!World) return;

    Subsystem = UAnimNextWorldSubsystem::Get(World);
    if (!Subsystem) return;

    // 加载模块资产（路径根据实际情况修改）
    MyModuleAsset = LoadObject<UAnimNextModule>(nullptr, TEXT("/Game/AnimNext/MyModule.MyModule"));
    if (!MyModuleAsset) return;

    // 创建模块实例，绑定到 GameMode 自身
    ModuleHandle = Subsystem->CreateModuleInstance(
        MyModuleAsset,
        this,
        EAnimNextModuleInitMethod::Immediate
    ).ModuleHandle;
}

void AModuleDemoGameMode::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (Subsystem && ModuleHandle.IsValid())
    {
        // 每帧向模块发送一个简单事件（仅示例）
        TSharedPtr<UE::UAF::FAnimNextTraitEvent> TickEvent = MakeShared<UE::UAF::FAnimNextTraitEvent>(/* 合适的构造 */);
        Subsystem->QueueInputTraitEvent(TickEvent);
    }
}
```

## 模块依赖

使用 `UAF` Runtime 模块时，你的模块需要添加以下依赖到 `Build.cs`：

| 模块 | 用途 |
|---|---|
| `LiveCoding` | 仅在开发阶段用于热重载，生产环境可忽略 |

除此之外，`UAF` 内部还依赖了 RigVM、UniversalObjectLocator 等，但这些已通过 UAF 自身提供，使用者无需额外引用。若需使用编辑器功能（如 UAFEditor 模块），还需依赖 `UnrealEd` 等（属于标准编辑器依赖，此处省略）。

**注意**：`UAFEditor` 和 `UAFTestSuite` 模块不会被运行时库直接引用，仅在编辑器或测试环境下使用。

## 维护状态

### 近期更新

- 2025-10-02 ef1c8b5 Fix double binding to IsEnabled
- 2025-10-02 f75459b Fix crash from selecting non-Actor derived blueprint to modify in UAF asset wizard
- 2025-10-01 6f23619 Moved UEdGraphSchema asset reference filtering for drag and drop operations to their various impleme
- 2025-09-30 737f1f4 Crash fixes for LODPose
- 2025-09-25 2f8943c Honor `ShrinkByDefault` in various existing array classes.

### 维护评价

该插件创建于 **2025年9月25日**，属于全新开发的实验性插件。从其 Git 日志可以看出，插件正处于 **活跃开发阶段**，几乎每天都有热修复和功能改进（包括崩溃修复、绑定逻辑修复、编辑器过滤优化等）。虽然 `IsExperimentalVersion=true`，但代码质量高、架构清晰，适合用于**学习和实验**，也适合作为构建自定义动画框架的基础。

**局限性**：
- 仍处于实验阶段，API 可能会发生较大变化。
- 当前依赖 `LiveCoding` 模块（仅在开发构建中可用），发布版本可能需要额外配置。
- 缺乏正式文档和示例项目，上手成本较高。

**建议**：如果项目处于早期研发阶段，且需要高度定制化的动画系统，推荐试用此插件。生产项目中请谨慎使用，并关注后续版本更新。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAF)
- [官方文档]（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAF/Source/UAFTestSuite)