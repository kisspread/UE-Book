# RigLogic for UAF

> RigLogic for UAF

| 属性 | 值 |
|---|---|
| 中文名 | 面部动画UAF集成 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RigLogicUAF` (Runtime), `RigLogicUAFUncookedOnly` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-26 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RigLogicUAF) | |

## 用途

RigLogicUAF 是 Epic Games 在 UE5 的 UAF (Unified Animation Framework) 框架下对 RigLogic 技术的集成实现。RigLogic 本身是一种用于驱动基于 DNA 数据（如 MetaHuman 使用的面部动画数据）的程序化动画的运行时引擎。

该插件的核心作用是**将 RigLogic 的程序化面部动画驱动能力，以 Trait（特征）的形式接入 UAF 动画图系统**。它解决了在 UAF 的模块化、可组合的动画图环境中，如何高效、标准化地执行基于 DNA 资产的面部表情、口型同步和眼部运动等计算的问题。它接收来自 UAF 图的输入姿势（Pose）和曲线（Curves），通过 RigLogic 计算后，输出修改后的姿势和变形（BlendShape）曲线。

## 使用场景

- 你的项目使用 MetaHuman 或其他基于 DNA 管道创建的数字人角色，且希望在下一代 UAF 动画系统中驱动其面部动画。
- 你需要在 UAF 动画图中程序化地、实时地驱动基于 RigLogic 资产（如 `.dna` 文件）的复杂面部变形。
- 你的动画系统需要高 LOD 优化的面部动画方案，该插件支持通过 LOD 阈值来控制面部动画计算的细节层级。

## 蓝图用法

该插件主要通过 UAF 的节点图系统（AnimGraph）使用，而非传统的蓝图节点。其主要交互方式是通过 `RigLogic` 节点模板。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RigLogic` | UAF 动画图节点模板，代表 RigLogic 计算特征。 | `FRigLogicTrait` (Trait) |

### 使用示例（蓝图描述）

在 UAF 动画图编辑器中：
1. 从节点列表中拖入 **`RigLogic`** 节点。
2. 该节点会暴露一个 **输入引脚**，用于接收上游动画节点输出的骨骼姿势和动画曲线。
3. 在节点的细节面板中，可以设置 **`LODThreshold`** 属性，以控制在不同 LOD 级别下是否启用面部动画计算。
4. 该节点的 **输出** 是经过 RigLogic 处理后的修改姿势和曲线，可以连接到后续的动画节点或最终输出节点。

## C++ 用法

### 头文件引入

```cpp
#include "RigLogicUAF/RigLogicTrait.h"
#include "RigLogicUAF/RigLogicTask.h"
```

### 基本用法

核心在于理解和实例化 `FRigLogicTrait` 及其相关数据。以下示例展示了 Trait 数据结构的基本构成。

（来源：`Engine/Plugins/Experimental/RigLogicUAF/Source/RigLogicUAF/Public/RigLogicTrait.h`）

```cpp
// RigLogic Trait 的共享数据，在动画图实例之间共享。
USTRUCT(meta = (DisplayName = "RigLogic"))
struct FUAFRigLogicTraitSharedData : public FAnimNextTraitSharedData
{
    GENERATED_BODY()

    // 输入 Trait 句柄，用于接收上游姿势和曲线。
    UPROPERTY()
    FAnimNextTraitHandle Input;

    // LOD 阈值，控制面部动画计算的最高 LOD 级别。
    UPROPERTY(EditAnywhere, Category = RigLogic)
    int32 LODThreshold = INDEX_NONE;
};

// RigLogic Trait 的实例数据，每个动画图实例拥有独立的一份。
namespace UE::UAF
{
    struct FRigLogicTrait : FBaseTrait, IEvaluate, IUpdate, IUpdateTraversal, IHierarchy
    {
        // ... 省略宏声明 ...

        struct FInstanceData : FTrait::FInstanceData
        {
            /** 输入节点，用于接收输入姿势和面部表情曲线。 */
            FTraitPtr Input;

            /** 独占的 RigLogic 运行时实例。 */
            TUniquePtr<FRigInstance> RigInstance;
        };

        // 关键接口实现：在后评估阶段执行 RigLogic 计算。
        virtual void PostEvaluate(FEvaluateTraversalContext& Context, const TTraitBinding<IEvaluate>& Binding) const override;
    };
}
```

### 进阶用法

`RigLogicInstanceData` 管理了骨骼映射等静态数据，而 `RigLogicTask` 负责实际执行计算逻辑。开发者通常不直接与这些类交互，它们由 `FRigLogicTrait` 内部管理。如果需要进行深度集成或调试，可以关注以下结构：

（来源：`Engine/Plugins/Experimental/RigLogicUAF/Source/RigLogicUAF/Public/RigLogicInstanceData.h`）

```cpp
// 骨骼索引映射结构
struct FRigLogicBoneMapping
{
    uint16 RigLogicJointIndex; // RigLogic 内部骨骼索引
    int32 PoseBoneIndex;       // 当前 LOD 下的姿势骨骼索引
};

// 实例数据管理类，缓存了骨骼映射等信息
struct FRigLogicInstanceData
{
    // 缓存的 DNA 运行时上下文和索引映射
    TSharedPtr<FSharedRigRuntimeContext> CachedRigRuntimeContext;
    TSharedPtr<FDNAIndexMapping> CachedDNAIndexMapping;

    // 每个 LOD 级别的骨骼索引映射表
    TArray<TArray<FRigLogicBoneMapping>> RigLogicToSkeletonBoneIndexMappingPerLOD;

    // 初始化函数，基于参考姿势构建映射
    void Init(const UE::UAF::FReferencePose* ReferencePose);
};
```

## Demo 示例

以下示例展示如何创建一个继承自 `FRigLogicTrait` 的最小自定义 Trait，演示其生命周期接口的基本使用。

### MyRigLogicTrait.h
```cpp
// MyRigLogicTrait.h
#pragma once
#include "RigLogicUAF/RigLogicTrait.h"

namespace UE::UAF
{
    struct FMyRigLogicTrait : FRigLogicTrait
    {
        DECLARE_ANIM_TRAIT(FMyRigLogicTrait, FRigLogicTrait)

        using FSharedData = FUAFRigLogicTraitSharedData;

        struct FInstanceData : FRigLogicTrait::FInstanceData
        {
            // 可添加自定义实例数据
        };

        // 覆盖评估函数，可在此添加自定义逻辑
        virtual void PostEvaluate(FEvaluateTraversalContext& Context, const TTraitBinding<IEvaluate>& Binding) const override;
    };
}
```

### MyRigLogicTrait.cpp
```cpp
// MyRigLogicTrait.cpp
#include "MyRigLogicTrait.h"

namespace UE::UAF
{
    IMPLEMENT_ANIM_TRAIT(FMyRigLogicTrait, FRigLogicTrait)

    void FMyRigLogicTrait::PostEvaluate(FEvaluateTraversalContext& Context, const TTraitBinding<IEvaluate>& Binding) const
    {
        // 1. 获取 Trait 和实例数据
        const FSharedData& SharedData = Binding.GetSharedData<FSharedData>();
        FInstanceData& InstanceData = Binding.GetInstanceData<FInstanceData>();

        // 2. 调用父类（FRigLogicTrait）的 PostEvaluate，执行核心 RigLogic 计算
        FRigLogicTrait::PostEvaluate(Context, Binding);

        // 3. （可选）添加自定义的后处理逻辑，例如记录日志
        // UE_LOG(LogRigLogicUAF, Verbose, TEXT("MyRigLogicTrait PostEvaluate Executed."));
    }
} // namespace UE::UAF
```

## 模块依赖

从代码结构和插件依赖推断，使用此插件需要依赖以下模块（除 Core, CoreUObject, Engine 等常见依赖外）：

| 模块 | 用途 |
|---|---|
| `RigLogic` | RigLogic 核心运行时库，提供 `FRigInstance` 等基础类。 |
| `UAF` | 统一动画框架核心，提供 Trait 系统、动画图等基础设施。 |
| `UAFAnimGraph` | UAF 的动画图编辑器和相关支持。 |
| `RigLogicUAF` | 本插件的运行时模块，提供 Trait、Task 和实例数据类。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `de315afa` | Fix compile error for RigLogicUAF test module | 修复 RigLogicUAF 测试模块的编译错误 |
| 2026-05-12 | `9006d42c` | Implement identical integration tests for all three RigLogic runtime integrations, AnimNode RigLogic | 为所有三个 RigLogic 运行时集成实现统一的集成测试 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 64 位系统下格式说明符与参数位数不匹配的问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移到 UE_LOGF |
| 2026-03-18 | `d5252a70` | RigLogicUAF: Support new UDNAAssetUserData in addition to legacy UDNAAsset | RigLogicUAF：在原有 UDNAAsset 支持基础上，新增对 UDNAAssetUserData 的支持 |

### 维护评价

该插件**处于活跃开发中**。创建于 2025 年 8 月，历史不到 1 年，属于非常新的插件。从 git 历史看，它在 2026 年 3 月至 5 月期间有多次实质性更新，包括功能增强（支持新的资产类型）、缺陷修复、测试完善和代码现代化迁移。这表明该插件是 Epic Games 正在积极迭代和测试的实验性功能，旨在为 UAF 框架提供标准化的 DNA/RigLogic 动画支持。

**注意**：这是一个 `IsExperimentalVersion = true` 的实验性插件，其 API 和功能在未来版本中可能发生重大变化，不建议在正式生产项目中作为核心功能依赖，但非常适合用于学习、研究和原型开发。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RigLogicUAF)
- [官方文档]()（暂无）
- [测试用例]()（根据 git 历史，测试模块存在，但具体路径需查看源码确认）