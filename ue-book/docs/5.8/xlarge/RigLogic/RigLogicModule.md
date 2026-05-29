# RigLogic Plugin

> RigLogic Plugin for Facial Animation

| 属性 | 值 |
|---|---|
| 中文名 | RigLogic 面部动画插件 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（DNA资产，动画节点，工具类） |
| 模块 | `RigLogicLib` (Runtime), `RigLogicModule` (Runtime), `RigLogicLibTest` (Runtime), `RigLogicEditor` (Runtime), `RigLogicDeveloper` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-07-20 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/RigLogic) | |

## 用途

RigLogic 插件是 Epic Games 为驱动 MetaHuman 高保真面部动画而开发的核心系统。它不仅仅是一个动画节点，而是一套完整的面部动画解决方案。

**核心功能**：该插件的核心是一个名为 RigLogic 的运行时引擎，它能够读取一种名为 DNA（Digital Native Art）的专有动画数据格式。DNA 文件包含了完整的面部拓扑、骨骼绑定、混合形状、皮肤权重以及复杂的控制逻辑（包括传统变形、基于物理的 RBF 求解器和机器学习行为）。RigLogic 引擎通过输入一组简单的控制值（如 GUI 滑块值），利用 DNA 中存储的数学模型和权重，计算出最终的面部骨骼变换、混合形状权重和动画映射值，从而驱动角色面部做出极其细腻的表情。

**为什么存在**：传统的面部动画管线通常依赖于大量美术手动调整的混合形状和骨骼权重，难以保证跨角色的一致性，且性能开销大。RigLogic 通过将复杂的面部动画逻辑数据化（DNA 文件），并提供一个高性能、支持多线程和 SIMD 指令加速的计算引擎，解决了以下问题：
1.  **标准化**：为 MetaHuman 角色提供统一的、基于科学的面部动画逻辑。
2.  **高性能**：支持 SSE、AVX、NEON 等向量指令集，并可在运行时切换计算后端（标量/向量）。
3.  **可扩展性**：支持机器学习驱动的面部动画（ML Controls）。
4.  **工作流集成**：作为 Unreal Engine 动画蓝图和 Control Rig 的核心节点，无缝融入现有管线。

## 使用场景

-   **MetaHuman 角色驱动**：当你使用 MetaHuman Creator 创建角色并将其导入 UE5 后，该插件的动画节点（`AnimNode_RigLogic`）会自动用于驱动角色的面部动画。
-   **自定义 DNA 角色**：如果你使用 iClone、Character Creator 或其他支持 DNA 导出流程的 DCC 工具创建了数字人角色，可以将 DNA 文件导入 UE，并使用此插件进行驱动。
-   **需要高性能面部动画**：项目对大量角色同时进行面部动画有严格的性能要求，需要利用 SIMD 指令集优化计算。
-   **控制驱动的精细面部动画**：希望通过少量输入控件（如表情面板上的滑块）来驱动大量、高精度的面部变形。
-   **研究或集成 ML 面部动画**：需要利用或实验基于神经网络（ML Controls）的先进面部动画技术。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RigLogic` | RigLogic 控制单元（Control Rig），是驱动面部动画的核心节点 | `FRigUnit_RigLogic` |
| `SetDNAReader` | 为 DNA 资产或 Skeletal Mesh 设置 DNA 读取器 | `UDNAAsset`, `UDNA` |
| `GetDNAReader` | 从 DNA 资产或 Skeletal Mesh 获取 DNA 读取器 | `UDNAAsset`, `UDNA` |
| `RestoreLegacyUEMHCCompatibility` | 将 DNA 数据转换回 Maya 坐标空间，兼容旧版工作流 | `UDNAAsset`, `UDNA` |
| `CreateMapForUpdatingNeutralMesh` | 创建用于从 DNA 更新 Skeletal Mesh 中性姿态的映射 | `USkelMeshDNAUtils` |
| `UpdateJoints` | 使用 DNA 数据更新 Skeletal Mesh 的关节位置 | `USkelMeshDNAUtils` |
| `UpdateBaseMesh` | 使用 DNA 数据更新 Skeletal Mesh 的基础顶点位置 | `USkelMeshDNAUtils` |
| `UpdateMorphTargets` | 使用 DNA 数据更新 Skeletal Mesh 的 Morph Targets | `USkelMeshDNAUtils` |
| `UpdateSkinWeights` | 使用 DNA 数据更新 Skeletal Mesh 的蒙皮权重 | `USkelMeshDNAUtils` |

### 使用示例（蓝图描述）

在动画蓝图中，`FAnimNode_RigLogic` 通常作为最终或中间节点。你需要将一个基础动画序列（或姿态）连接到它的 `AnimSequence` 输入引脚。该节点会读取附加在 Skeletal Mesh Component 上的 DNA 数据，并使用其中的逻辑将动画曲线中的输入值（例如 “CTRL_expressions_Happy”）转换为面部骨骼的旋转/位移、Morph Target 权重等输出，最终驱动模型。

**配置 DNA 资产**：
1.  选择你的 Skeletal Mesh。
2.  在其 Asset User Data 中，确保存在 `UDNAAsset` 或 `UDNA` 类型的资产。
3.  选中该 DNA 资产，在 Details 面板中可以配置 `RigLogicConfiguration`，例如选择计算后端（`CalculationType`：向量化/SIMD 或标量）、启用/禁用特定计算通道（如机器学习行为 `LoadMachineLearnedBehavior`）、设置裁剪阈值等。

## C++ 用法

### 头文件引入

```cpp
// 核心 RigLogic 引擎
#include "RigLogicModule.h"

// DNA 数据读写
#include "DNAReader.h"
#include "DNAUtils.h"

// Skeletal Mesh 更新工具
#include "SkelMeshDNAUtils.h"

// 动画节点
#include "AnimNode_RigLogic.h"
```

### 基本用法

从 DNA 文件加载并创建一个 RigLogic 实例。

```cpp
// 来自 `DNAUtils.h` 和 `RigLogic.h`
#include "DNAUtils.h"
#include "RigLogic.h"

// 1. 从文件加载 DNA 读取器
TSharedPtr<IDNAReader> DNAReader = LoadDNAFromFile(TEXT("/Game/Characters/DNA/MyMetaHuman.dna"));
if (DNAReader.IsValid())
{
    // 2. 创建 RigLogic 配置
    FRigLogicConfiguration Config;
    Config.CalculationTypePerPlatform = FPerPlatformERigLogicCalculationType(ERigLogicCalculationType::AnyVector);
    Config.LoadMachineLearnedBehavior = true; // 启用 ML 计算

    // 3. 创建 RigLogic 核心实例（无状态，可被多个角色实例共享）
    TSharedPtr<FRigLogic> SharedRigLogic = MakeShared<FRigLogic>(DNAReader.Get(), Config);

    // 4. 为某个特定角色创建 RigInstance（包含该角色的输入/输出缓冲区）
    FRigInstance CharacterInstance(SharedRigLogic.Get());

    // 5. 设置输入控制值 (例如，微笑值为 1.0)
    uint16 SmileControlIndex = 0; // 需要通过名称查找或从配置中获取索引
    CharacterInstance.SetGUIControl(SmileControlIndex, 1.0f);

    // 6. 执行一次完整的计算循环
    //    计算顺序: GUI -> Raw -> (RBF) -> (ML) -> PSD -> Joints/BlendShapes/AnimatedMaps
    SharedRigLogic->Calculate(&CharacterInstance);

    // 7. 读取计算结果
    TArrayView<const float> JointOutputs = CharacterInstance.GetJointOutputs();
    TArrayView<const float> BlendShapeOutputs = CharacterInstance.GetBlendShapeOutputs();
    // ... 将结果应用到骨骼组件
}
```

### 进阶用法

在 `AnimNode_RigLogic` 内部，计算被分解为多个阶段，可以精细控制。

```cpp
// 来自 `RigLogic.h`， AnimNode_RigLogic 内部计算流程的抽象
void FAnimNode_RigLogic::CalculateRigLogic()
{
    // 假设 LocalRigRuntimeContext 已初始化并包含有效的 FRigLogic 和 FRigInstance
    FRigLogic* RigLogic = LocalRigRuntimeContext->RigLogic.Get();
    FRigInstance* RigInstance = LocalRigRuntimeContext->RigInstance.Get();

    // 1. 将动画蓝图中的输入曲线映射到 RigLogic 的 Raw Controls
    // UpdateRawControls(InputContext);

    // 2. 将 GUI Controls 映射到 Raw Controls (如果需要)
    // RigLogic->MapGUIToRawControls(RigInstance);

    // 3. 计算机器学习驱动的控制值 (如果 DNA 中包含且配置启用)
    if (RigLogic->GetConfiguration().LoadMachineLearnedBehavior)
    {
        RigLogic->CalculateMLControls(RigInstance);
    }

    // 4. 计算 RBF 求解器的输出
    if (RigLogic->GetConfiguration().LoadRBFBehavior)
    {
        RigLogic->CalculateRBFControls(RigInstance);
    }

    // 5. 计算 PSD 控制值
    RigLogic->CalculatePSDControls(RigInstance);

    // 6. 计算最终的骨骼变形、混合形状等
    RigLogic->CalculateJoints(RigInstance);
    RigLogic->CalculateBlendShapes(RigInstance);
    RigLogic->CalculateAnimatedMaps(RigInstance);
}
```

## Demo 示例

一个最小化的 C++ 示例，演示如何创建 RigInstance 并执行一次计算。

**头文件 (MyRigLogicComponent.h)**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "RigInstance.h"
#include "SharedRigRuntimeContext.h"
#include "MyRigLogicComponent.generated.h"

class UMyRigLogicComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyRigLogicComponent();

    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

    // 设置要使用的 DNA 资产（蓝图可调用）
    UFUNCTION(BlueprintCallable, Category = "RigLogic")
    void SetDNA(class UDNA* InDNAAsset);

    // 设置一个简单的 GUI 控制值（蓝图可调用）
    UFUNCTION(BlueprintCallable, Category = "RigLogic")
    void SetControlValue(uint16 ControlIndex, float Value);

private:
    // RigLogic 运行时上下文（包含共享的 RigLogic 引擎）
    TSharedPtr<FSharedRigRuntimeContext> RigRuntimeContext;

    // 用于当前角色的 Rig 实例
    TUniquePtr<FRigInstance> RigInstance;

    // 引用的 DNA 资产
    UPROPERTY(Transient)
    class UDNA* DNAAsset;
};
```

**源文件 (MyRigLogicComponent.cpp)**
```cpp
#include "MyRigLogicComponent.h"
#include "DNA.h"
#include "RigLogic.h"
#include "DNAReader.h"

UMyRigLogicComponent::UMyRigLogicComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
}

void UMyRigLogicComponent::BeginPlay()
{
    Super::BeginPlay();
    if (DNAAsset)
    {
        SetDNA(DNAAsset);
    }
}

void UMyRigLogicComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
    if (RigRuntimeContext.IsValid() && RigInstance.IsValid())
    {
        // 在这里，通常会从动画蓝图获取输入曲线并设置到 RigInstance 的 GUI/Raw Controls
        // 本例假设控制值已通过 SetControlValue 设置。

        // 执行完整的计算
        RigRuntimeContext->RigLogic->Calculate(RigInstance.Get());

        // 从这里可以读取输出 (GetJointOutputs, GetBlendShapeOutputs等)
        // 并应用到骨骼网格体组件上。
        // 例如: 对于每个输出的骨骼变换，更新对应的骨骼。
    }
}

void UMyRigLogicComponent::SetDNA(UDNA* InDNAAsset)
{
    DNAAsset = InDNAAsset;
    if (DNAAsset)
    {
        // 从 DNA 资产获取其内部共享的 RigRuntimeContext
        RigRuntimeContext = DNAAsset->GetRigRuntimeContext();
        if (RigRuntimeContext.IsValid())
        {
            // 为当前组件创建一个新的 RigInstance
            RigInstance = MakeUnique<FRigInstance>(RigRuntimeContext->RigLogic.Get());
            // 可选：设置初始 LOD
            RigInstance->SetLOD(0);
        }
    }
    else
    {
        RigRuntimeContext.Reset();
        RigInstance.Reset();
    }
}

void UMyRigLogicComponent::SetControlValue(uint16 ControlIndex, float Value)
{
    if (RigInstance.IsValid())
    {
        RigInstance->SetGUIControl(ControlIndex, Value);
    }
}
```

## 模块依赖

要使用此插件，你的模块需要依赖以下模块（除了标准的 Core, Engine, Slate 等）：

| 模块 | 用途 |
|---|---|
| `RigLogicModule` | RigLogic 的 UE 集成模块，包含动画节点、DNA 资产、工具函数等。**这是你通常需要依赖的主要模块**。 |
| `RigLogicLib` | RigLogic 引擎的纯 C++ 库，负责核心数学计算。`RigLogicModule` 已经依赖它，通常你不需要直接依赖。 |
| `SkeletalMeshUtilitiesCommon` | 用于 Skeletal Mesh 的通用操作和更新。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `de0806c7` | Fix RigLogic NaN output from TwistSwing/RBF when ControlAttributeCurves overwrites driver-joint quat | 修复当 ControlAttributeCurves 覆盖驱动关节四元数时，TwistSwing/RBF 计算可能产生 NaN 的问题 |
| 2026-05-13 | `52da7ee0` | Fix quaternion joints evaluator test in case no rotation support is compiled in for the zyx sequence | 修复当未编译 ZYX 旋转序列支持时，四元数关节评估器测试失败的问题 |
| 2026-05-13 | `27f94d1b` | Fix RigLogic ML Joints initialization of rotation adapter in the absence of coordinate system conver | 修复在坐标系统转换未启用时，ML Joints 的旋转适配器初始化错误 |
| 2026-05-13 | `4b5d4e7d` | Notify dependent AnimNode_RigLogic instances when RigRuntimeContext is reinitialized due to config c | 当 RigRuntimeContext 因配置更改而重新初始化时，通知所有依赖的 AnimNode_RigLogic 实例 |
| 2026-05-12 | `9006d42c` | Implement identical integration tests for all three RigLogic runtime integrations, AnimNode RigLogic | 为所有三种 RigLogic 运行时集成（AnimNode RigLogic...）实现相同的集成测试 |

### 维护评价

**维护状态：活跃维护**

RigLogic 是 MetaHuman 项目的核心依赖，由 Epic Games 官方维护。从 Git 历史看，最近一次更新发生在几天前（2026-05-26），且内容集中在 **Bug 修复和稳定性改进** 上，没有出现功能移除或废弃标记。这表明插件仍在被积极使用和改进，特别是为了确保与 MetaHuman 工作流的兼容性和运行时稳定性。

**推荐程度：强烈推荐（用于 MetaHuman 相关工作流）**
如果你需要驱动 MetaHuman 角色的面部动画，或者需要集成基于 DNA 的面部动画工作流，这个插件是**必需品**。对于其他类型的动画，这个插件并不适用。它的 API 相对复杂，但官方提供了清晰的集成示例（如 `AnimNode_RigLogic` 和 `FRigUnit_RigLogic`），跟随 MetaHuman 文档和示例项目是最佳的学习途径。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/RigLogic)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/riglogic-plugin-in-unreal-engine/)（MetaHuman 相关文档通常涵盖此插件）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/RigLogic/Source/RigLogicLibTest)