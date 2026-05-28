# UAF Anim Graph

> Framework for defining animation graphs.

| 属性 | 值 |
|---|---|
| 中文名 | UAF 动画图 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画图资产，测试资源） |
| 模块 | `UAFAnimGraph` (Runtime), `UAFAnimGraphEditor` (Editor), `UAFAnimGraphUncookedOnly` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-26 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFAnimGraph) | |

## 用途

UAFAnimGraph 是一个基于**Trait（特质）** 的高级动画图框架。它旨在为 Unreal Engine 提供一个模块化、高性能的动画逻辑定义和执行系统。该插件的核心并非简单的动画状态机，而是一个完整的“可编程动画图”运行时和工具链。

该框架解决了以下问题：
1.  **模块化动画逻辑**：通过`FTrait`及其栈结构，允许将动画行为（如播放、混合、更新逻辑、评估）封装成独立、可组合的单元。
2.  **图与实例分离**：定义静态的`UUAFAnimGraph`资产，运行时创建`FAnimNextGraphInstance`实例，支持高效的多实例管理和热重载。
3.  **高级混合与状态管理**：内置`BlendStack`、`PlayAnimSlot`、`InjectionSite`等Trait，为复杂的动画状态机、Montage、动画注入（Injection）提供了核心支持。
4.  **高性能评估**：通过`FEvaluationVM`（评估虚拟机）和`FEvaluationProgram`，将动画图编译为高效的线性执行程序，减少运行时开销。
5.  **可扩展的接口系统**：使用`ITraitInterface`定义清晰的接口（如`IUpdate`, `IEvaluate`, `IHierarchy`），便于扩展和定制动画行为。

其存在意义在于为需要极高灵活性和性能的动画系统（如大型角色动画、复杂的AI行为动画）提供一个比传统AnimGraph蓝图更底层、更可控的解决方案。

## 使用场景

-   **你正在开发一款3A级动作或RPG游戏，需要复杂的角色动画状态机和Montage系统** → 使用 UAFAnimGraph 构建基于 Trait 的动画图，利用 `BlendStack` 和 `MontageTrait` 管理动画过渡。
-   **你的游戏有动态注入动画的需求（例如，在特定部位实时叠加受伤动画或技能动画）** → 使用 `InjectionSiteTrait` 和 `FInjectionUtils` 来实现动画注入和拔出。
-   **你需要构建一个可高度定制、数据驱动的动画评估管线** → 使用 `IEvaluate` 接口和 `FEvaluationVM` 来定义自定义的动画计算逻辑。
-   **你希望将动画逻辑与动画资产（如UAnimSequence）解耦，实现更灵活的资产驱动** → 利用 `FAnimNextFactoryParams` 和 `FAnimNextSimpleAnimGraphBuilder` 在运行时动态组装和配置动画图。

## 蓝图用法

该插件主要提供底层 C++ API，蓝图暴露有限。核心蓝图功能集中在动画注入操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Is Slot Active` | 检查指定槽位（Slot）当前是否有动画蒙太奇活跃播放。 | `UUAFInjectionLibrary` |
| `Play Anim` | 通过组件向指定的注入点播放一个动画序列。 | `UUAFInjectionLibrary` |

### 使用示例（蓝图描述）

1.  **检查蒙太奇状态**：在蓝图中，你可以获取一个 `UUAFComponent` 的引用，然后调用 `Is Slot Active` 函数，传入一个槽位名称（例如 “UpperBody”），该函数会返回一个布尔值，表示该槽位是否正被蒙太奇占用。
2.  **触发动画注入**：要通过蓝图触发一次动画注入，你需要先获取系统的弱引用（`FUAFWeakSystemReference`）。然后调用 `UUAFInjectionLibrary::PlayAnim` 函数，传入该系统引用、目标注入点名称、要播放的 `UAnimSequence` 资产以及混合设置。函数会返回一个 `FInjectionRequestPtr`，用于跟踪请求状态或取消它。

## C++ 用法

### 头文件引入

```cpp
// 引入注入工具类
#include "Injection/InjectionUtils.h"

// 引入图实例和动画图资产
#include "Graph/AnimNextGraphInstance.h"
#include "Graph/AnimNextAnimationGraph.h"

// 引入工厂参数（用于运行时构建图）
#include "Factory/AnimNextFactoryParams.h"
```

### 基本用法：使用工厂参数创建并播放一个简单的动画图实例

以下代码展示了如何使用 `FAnimNextFactoryParams` 在运行时构建一个包含序列播放器 Trait 的动画图，并分配一个实例。
（来源：基于 `FAnimNextFactoryParams` 和 `FAnimNextSimpleAnimGraphBuilder` 的用法模式推断）

```cpp
// 假设你有一个 UUAFComponent* 或者 UObject* InHost 作为系统宿主
// 假设你有一个 UAnimSequence* InSequenceToPlay

// 1. 创建工厂参数对象
UE::UAF::FAnimNextFactoryParams FactoryParams;

// 2. 向参数中添加一个序列播放器 Trait（例如，使用一个名为FAnimNextSequencePlayerTrait的Trait）
//    ‘0’ 代表堆栈索引， ‘UE::UAF::ETraitVariableMapping::All’ 表示该Trait的公共变量将暴露
FactoryParams.AddTraitStruct<FAnimNextSequencePlayerTraitSharedData>(UE::UAF::ETraitVariableMapping::All, 0);

// 3. 访问刚才添加的 Trait 结构体，并设置动画序列
FactoryParams.AccessTraitStruct<FAnimNextSequencePlayerTraitSharedData>(0, [&](FAnimNextSequencePlayerTraitSharedData& Data)
{
    Data.AnimSequence = InSequenceToPlay;
    Data.Loop = true;
});

// 4. （可选）添加一个变量映射，使外部可以控制播放速率
// FactoryParams.AddVariableMappingToAll(FAnimNextVariableReference(TEXT("PlayRate")), FName(TEXT("PlayRate")));

// 5. 使用工厂参数分配一个图实例
//    注意：你需要一个有效的 UUAFAnimGraph 资产作为模板，或者让系统使用默认逻辑。
TSharedPtr<FAnimNextGraphInstance> GraphInstance = MyAnimGraph->AllocateInstance(UE::UAF::FGraphAllocationParams(), MoveTemp(FactoryParams));

// 6. 启动图的更新和评估
//    通常，图实例会被集成到一个模块实例或组件中，由系统驱动更新。
//    如果手动驱动，你需要在合适的地方（如 Tick）调用其更新和评估逻辑。
```

### 进阶用法：通过 `FInjectionUtils` 播放动画注入

以下代码展示了如何通过注入系统播放一个动画序列到指定的注入点。
（来源：`FInjectionUtils::PlayAnim` 函数签名）

```cpp
// 假设 InHost 是拥有动画系统的 UObject (例如 UUAFComponent)
// 假设 InSystemReference 是有效的系统弱引用
// 假设 InTargetSite 是注入点名称 (FName)
// 假设 InAnimSequence 是要播放的动画序列
// 假设 InBlendInSettings 和 InBlendOutSettings 是混合设置

// 创建并发送注入请求
FInjectionRequestPtr Request = UE::UAF::FInjectionUtils::PlayAnimHandle(
    InHost,
    InSystemReference,
    InTargetSite, // 例如 FName(“UpperBody”)
    InAnimSequence,
    UE::UAF::FPlayAnimArgs(), // 使用默认播放参数
    InBlendInSettings,
    InBlendOutSettings,
    UE::UAF::FInjectionLifetimeEvents() // 可以设置生命周期回调
);

if (Request.IsValid())
{
    // 注入请求已成功发送
    // 你可以存储 Request 以供后续查询状态或取消 (Uninject)
    // Request->GetStatus() 可以检查播放状态
    // Request->QueueTask(...) 可以在实例上设置变量
}
else
{
    // 注入失败
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何定义一个简单的自定义 Trait 和一个使用它的动画图。

### 自定义 Trait 定义 (MySimpleTrait.h)

```cpp
#pragma once

#include "TraitCore/Trait.h"

// 一个简单的 Trait，它在更新时输出日志
USTRUCT(meta = (DisplayName = “Simple Log Trait”))
struct FMySimpleTraitSharedData : public FAnimNextTraitSharedData
{
    GENERATED_BODY()

    // 共享数据：一个用于输出的日志消息
    UPROPERTY(EditAnywhere, Category = “Debug”)
    FString LogMessage = TEXT(“Trait Updated!”);
};

namespace UE::UAF
{
    struct FMySimpleTrait : FBaseTrait, IUpdate
    {
        DECLARE_ANIM_TRAIT(FMySimpleTrait, FBaseTrait)

        using FSharedData = FMySimpleTraitSharedData;

        struct FInstanceData : FTrait::FInstanceData
        {
            void Construct(const FExecutionContext& Context, const FTraitBinding& Binding)
            {
                UE_LOG(LogTemp, Log, TEXT(“MySimpleTrait Constructed.”));
            }
            void Destruct(const FExecutionContext& Context, const FTraitBinding& Binding)
            {
                UE_LOG(LogTemp, Log, TEXT(“MySimpleTrait Destructed.”));
            }
        };

        // IUpdate 接口实现
        virtual void PreUpdate(FUpdateTraversalContext& Context, const TTraitBinding<IUpdate>& Binding, const FTraitUpdateState& TraitState) const override
        {
            const FSharedData* SharedData = Binding.GetSharedData<FSharedData>();
            if (SharedData)
            {
                UE_LOG(LogTemp, Log, TEXT(“%s”), *SharedData->LogMessage);
            }
        }
    };
}

// 在 .cpp 文件中实现 GENERATE_ANIM_TRAIT_IMPLEMENTATION
// ... (GENERATE_ANIM_TRAIT_IMPLEMENTATION(FMySimpleTrait, ...) )
```

### 使用 Trait 构建图并分配实例 (示例使用)

```cpp
#include “Factory/AnimNextFactoryParams.h”
#include “MySimpleTrait.h” // 包含上面定义的Trait

// 在某个函数中
{
    // 1. 使用工厂参数构建图
    UE::UAF::FAnimNextFactoryParams Params;
    // 添加我们的自定义 Trait 到堆栈 0
    Params.AddTraitStruct<FMySimpleTraitSharedData>(UE::UAF::ETraitVariableMapping::All, 0);
    // 访问它以设置消息
    Params.AccessTraitStruct<FMySimpleTraitSharedData>(0, [](FMySimpleTraitSharedData& Data)
    {
        Data.LogMessage = TEXT(“Hello from Runtime Built Graph!”);
    });

    // 2. 从模板动画图资产分配实例（假设 TemplateGraph 是一个有效的 UUAFAnimGraph 资产指针）
    //    注意：实际使用时，你需要一个已编译的动画图资产作为模板，其中包含至少一个节点引用了我们的 Trait。
    //    或者，你需要通过更底层的接口注册 Trait 并构建图数据。这个示例简化了步骤。
    TSharedPtr<FAnimNextGraphInstance> Instance = TemplateGraph->AllocateInstance(UE::UAF::FGraphAllocationParams(), MoveTemp(Params));

    // 3. 通常，实例会被附加到一个模块实例或系统中进行驱动。
    //    当系统更新时，我们的 Trait 的 `PreUpdate` 将会被调用，并输出我们设置的日志消息。
}
```

## 模块依赖

要使用 `UAFAnimGraph` 插件，你的模块需要依赖以下核心模块（已在插件内部处理，但了解它们有助于调试）：

| 模块 | 用途 |
|---|---|
| `UAF` | 核心 UAF 框架，提供模块、组件、系统实例等基础架构。 |
| `RigVM` | RigVM 运行时，用于动画图中潜力销钉（Latent Pins）的执行。 |
| `AnimGraphRuntime` | 传统的动画图运行时，可能用于集成旧版动画节点。 |
| `PropertyEditor` | 编辑器属性自定义（仅编辑器模块依赖）。 |
| `ToolMenus`, `LevelEditor` | 编辑器工具和菜单集成（仅编辑器模块依赖）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `43658976` | Sequencer: Anim Mixer: Fix crash when scrubbing a level sequence after changing a Mix Layer transiti | 修复序列器动画混合器中，更改混合层过渡后拖动时间轴导致的崩溃问题。 |
| 2026-05-12 | `61c7c092` | [UEMHC] - Fix Geometry Export crash and material issues on re-export | 修复几何体导出崩溃以及重新导出时的材质问题。 |
| 2026-05-12 | `14c22336` | UAF: Add tick order dependecy between the UAF Montage Tick and CMC Tick to ensure the movement compo | 为UAF蒙太奇Tick和CMC Tick添加时序依赖，确保移动组件正常工作。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复32位和64位格式说明符不匹配的问题。 |
| 2026-04-22 | `287203b9` | UE 5.8 Animation deprecation clean up (CL 9/10): UAF | UE 5.8动画废弃代码清理（第9/10部分）：UAF。 |

### 维护评价

- **创建时间**：2025年6月创建，非常年轻。
- **最近更新频率**：非常活跃。最近一次更新（`43658976`）在2026年5月，且提交内容显示该插件仍在积极集成到 UE 5.8 的动画系统中（如动画混合器、序列器）。
- **维护状态**：**活跃维护中**。提交历史显示 Epic 内部团队仍在使用和改进此插件，修复崩溃、性能问题和进行引擎版本升级适配。
- **已知问题/限制**：该插件标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，表明它仍处于实验阶段，API和功能可能在未来版本中发生变化。其复杂性也意味着学习曲线较陡。
- **推荐使用**：**适用于愿意探索前沿技术、且对动画系统有深度定制需求的高级开发者或团队**。对于生产项目，需谨慎评估其稳定性和长期支持承诺。它代表了 UE 动画系统未来的一个可能方向。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFAnimGraph)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFAnimGraph/Tests)