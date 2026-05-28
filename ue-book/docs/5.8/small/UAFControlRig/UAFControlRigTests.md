# UAF Control Rig

> Control Rig integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF 控制绑定 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFControlRig` (Runtime), `UAFControlRigEditor` (Runtime), `UAFControlRigTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFControlRig) | |

## 用途

该插件在 Unreal Animation Framework (UAF) 的动画层系统与 Control Rig 运行时之间建立桥接。它解决了在 UAF 动画层状态机或蒙太奇中直接嵌入和驱动 Control Rig 实例的需求，使得开发者可以将 Control Rig 的程序化动画控制逻辑与 UAF 的上层动画流程无缝结合。其存在价值在于允许在更高级的动画管理架构（UAF）中复用和集成底层的、灵活的骨骼控制逻辑（Control Rig）。

## 使用场景

- 你的项目使用 UAF 来管理复杂的动画状态机，但同时又需要在某些动画状态中混合由 Control Rig 驱动的程序化动画（如基于物理的武器摇摆、非对称 IK）。
- 你需要在 UAF 动画层中触发或停止一个 Control Rig 的逻辑，例如在角色进入“瞄准”状态时启动一个控制瞄准偏移的 Control Rig。

## 蓝图用法

通过搜索源码中的 `UFUNCTION(BlueprintCallable)`，可以找到以下核心蓝图节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetControlRigInstance` | 为当前 UAF 动画层实例设置一个要使用的 Control Rig 资产和初始变量 | `UUAFControlRigLayer` |
| `GetControlRigInstance` | 获取当前层正在使用的 Control Rig 实例对象 | `UUAFControlRigLayer` |
| `EvaluateControlRig` | 手动触发一次 Control Rig 的求值，通常在 `NativeUpdateAnimation` 中调用 | `UUAFControlRigLayer` |
| `FindOrAddControlRig` | 查找或创建一个指定类型的 Control Rig 实例，并与当前 UAF 层关联 | `UUAFControlRigLayer` |

### 使用示例（蓝图描述）

在你的 UAF 动画蓝图中，继承自 `UUAFControlRigLayer` 的层：
1. 在层的 `OnBecomeRelevant` 事件中，使用 `SetControlRig` 节点，选择一个 Control Rig 资产。
2. 在 `UpdateAnimation` 事件中，调用 `EvaluateControlRig` 节点来每帧更新 Control Rig 的逻辑。
3. 在 `OnCeaseRelevant` 事件中，可以手动清理或重置 Control Rig 实例。

## C++ 用法

### 头文件引入

```cpp
#include “UAFControlRigLayer.h“
#include “ControlRig.h“ // 依赖 ControlRig 模块
```

### 基本用法

以下代码演示如何在自定义的 UAF 动画层中初始化和使用 Control Rig。

```cpp
// 文件路径: Source/MyProject/MyAnimLayer.cpp (假设的测试用例灵感来源)
#include “MyAnimLayer.h“
#include “UAFControlRigLayer.h“
#include “ControlRig.h“
#include “Rigs/RigHierarchyController.h“

void UMyAnimLayer::OnBecomeRelevant(const FAnimUpdateContext& Context, const FAnimNodeReference& Node)
{
    Super::OnBecomeRelevant(Context, Node);

    // 获取或创建一个 Control Rig 实例
    UControlRig* ControlRig = FindOrAddControlRig(UMyControlRig::StaticClass());
    if (ControlRig)
    {
        // 初始化 Control Rig 的骨骼映射
        ControlRig->Initialize();
        // 设置一些初始变量
        ControlRig->SetVariableValue<FVector>(TEXT(“AimOffset“), FVector::ZeroVector);
    }
}

void UMyAnimLayer::NativeUpdateAnimation(const FAnimUpdateContext& Context, const FAnimNodeReference& Node, float DeltaSeconds)
{
    Super::NativeUpdateAnimation(Context, Node, DeltaSeconds);

    // 每帧驱动 Control Rig
    if (UControlRig* ControlRig = GetControlRigInstance())
    {
        // 更新变量
        ControlRig->SetVariableValue<FVector>(TEXT(“AimOffset“), CurrentAimOffset);
        // 触发求值
        EvaluateControlRig();
    }
}

void UMyAnimLayer::OnCeaseRelevant(const FAnimUpdateContext& Context, const FAnimNodeReference& Node)
{
    // 可在此清理 Control Rig 实例
    Super::OnCeaseRelevant(Context, Node);
}
```

### 进阶用法

结合 UAF 层的混合逻辑，在多个 Control Rig 之间进行混合或过渡。

```cpp
// 在需要切换Control Rig的层中
void USwitchingLayer::SwitchControlRig(TSubclassOf<UControlRig> NewRigClass)
{
    if (CurrentControlRig && CurrentControlRig->GetClass() != NewRigClass)
    {
        // 可以添加一个淡出/淡入的混合逻辑
        CurrentControlRig->SetExecuteState(ERigExecutionType::Stop);
        // ... 保存或迁移状态 ...

        UControlRig* NewRig = FindOrAddControlRig(NewRigClass);
        if (NewRig)
        {
            NewRig->SetExecuteState(ERigExecutionType::Execute);
            // 迁移需要的变量值
        }
    }
}
```

## Demo 示例

一个最小可编译的自定义 UAF 控制绑定层示例。

**头文件 (MyControlRigLayer.h)**
```cpp
#pragma once

#include “CoreMinimal.h“
#include “UAFControlRigLayer.h“
#include “MyControlRigLayer.generated.h“

UCLASS()
class MYPROJECT_API UMyControlRigLayer : public UUAFControlRigLayer
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = “Setup“)
    TSubclassOf<UControlRig> TargetControlRigClass;

    UPROPERTY(BlueprintReadWrite, Category = “State“)
    float DynamicAlpha;

protected:
    virtual void OnBecomeRelevant(const FAnimUpdateContext& Context, const FAnimNodeReference& Node) override;
    virtual void NativeUpdateAnimation(const FAnimUpdateContext& Context, const FAnimNodeReference& Node, float DeltaSeconds) override;
};
```

**源文件 (MyControlRigLayer.cpp)**
```cpp
#include “MyControlRigLayer.h“
#include “ControlRig.h“
#include “Animation/AnimInstanceProxy.h“

void UMyControlRigLayer::OnBecomeRelevant(const FAnimUpdateContext& Context, const FAnimNodeReference& Node)
{
    Super::OnBecomeRelevant(Context, Node);

    if (TargetControlRigClass)
    {
        // 查找或创建指定的 Control Rig
        UControlRig* Rig = FindOrAddControlRig(TargetControlRigClass);
        if (Rig)
        {
            // 初始化
            Rig->Initialize();
        }
    }
    DynamicAlpha = 1.0f;
}

void UMyControlRigLayer::NativeUpdateAnimation(const FAnimUpdateContext& Context, const FAnimNodeReference& Node, float DeltaSeconds)
{
    Super::NativeUpdateAnimation(Context, Node, DeltaSeconds);

    // 逻辑: 让 DynamicAlpha 随时间衰减
    DynamicAlpha = FMath::Max(0.0f, DynamicAlpha - (DeltaSeconds * 0.5f));

    if (UControlRig* Rig = GetControlRigInstance())
    {
        // 将计算好的Alpha值传递给Control Rig的某个变量
        Rig->SetVariableValue<float>(TEXT(“BlendAlpha“), DynamicAlpha);
        // 执行Control Rig
        EvaluateControlRig();
    }
}
```

## 模块依赖

从 `UAFControlRig.Build.cs` 和 `UAFControlRigEditor.Build.cs` 分析得出，使用此插件需要以下独特依赖：

| 模块 | 用途 |
|---|---|
| `ControlRig` | 提供核心的 Control Rig 运行时、蓝图资产和执行环境 |
| `AnimationCore` | 提供动画系统的底层核心类型和功能 |
| `AnimationGraph` | 提供动画图表相关的工具和类型，用于与 UAF 系统集成 |
| `UAF` | 作为父框架，提供动画层、状态机等上层架构 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将模块内日志输出宏统一迁移为新的 UE_LOGF 格式。 |
| 2026-03-03 | `fb006c07` | Control Rig: Fix ControlRigTrait not finding newer BP-independent rigs | 修复 ControlRigTrait 节点无法发现较新的、不依赖蓝图的 Control Rig 资产的问题。 |
| 2026-03-03 | `3757a39a` | [Backout] - CL51376416 | 回退了提交 CL51376416 中的改动。 |
| 2026-03-03 | `fc9640e7` | Control Rig: Fix ControlRigTrait not finding newer BP-independent rigs | 同 `fb006c07`，针对同一问题的再次修复提交。 |
| 2026-02-27 | `6f697f67` | Allow system and graph factory initializer callbacks to add custom variable references | 允许系统和图表工厂的初始化回调添加自定义变量引用，增强了初始化阶段的灵活性。 |

### 维护评价

该插件创建于 2025 年中，目前约有 1 年历史，且处于实验性阶段。从 Git 历史看，在 2026 年初（距今约 2-3 个月前）仍有活跃的功能性更新和 Bug 修复，特别是针对 Control Rig 资产发现逻辑的优化，表明它正在被积极开发和测试。最后一次更新是日志规范的迁移，属于代码质量维护。

**总结**：这是一个处于**活跃维护**状态的实验性插件。它正在解决 UAF 与 Control Rig 集成中的具体问题，并持续改进。但由于其`Experimental`标签和`EnabledByDefault=false`的设置，**不建议直接用于生产环境**，更适合在研究和原型开发阶段尝试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFControlRig)
- [官方文档](）(（.uplugin 中 DocsURL 为空）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFControlRig/Tests)