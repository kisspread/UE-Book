# UAF Warping

> Framework for animation and pose warping for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF 动画扭曲 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFWarping` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFWarping) | |

## 用途

UAFWarping 是一个为 UAF (Universal Animation Framework) 设计的实验性动画扭曲框架。它提供了一套工具和节点，用于在运行时根据目标位置、旋转或其它条件，对动画姿态（Pose）或根骨骼运动（Root Motion）进行动态调整（扭曲）。

该插件解决的核心问题是：如何让角色动画更智能、更动态地适应游戏世界中的目标。例如，当角色需要将手精确地伸向一个抓取点，或者需要调整步伐以准确到达某个落脚点时，传统的固定动画播放无法满足需求。UAFWarping 通过程序化的方式调整动画数据，使最终的姿态符合游戏逻辑的目标，从而提升交互的真实感和精确度。

它依赖于 UAF 核心插件及相关的动画图、动画节点插件，作为 UAF 生态系统中处理“动画目标导向”行为的一部分。

## 使用场景

- 你在制作一个需要角色与物体进行精确交互的游戏（如攀爬、抓取、开关门）→ 用 UAFWarping 动态调整手臂或身体姿态，使手能够对准目标点。
- 你的游戏有复杂的移动系统，要求角色的脚步必须精确落在地面上的特定位置（如平台跳跃、走钢丝）→ 用 UAFWarping 扭曲根骨骼运动，使落地动画与目标位置匹配。
- 你正在实现一个瞄准系统，希望角色的上半身能根据瞄准目标的方向进行实时姿态调整 → 用 UAFWarping 结合 IK 来驱动瞄准姿态。

## 蓝图用法

基于最近的代码提交，该插件提供了动画图节点用于在动画蓝图中实现扭曲逻辑。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `WarpToTarget` | 一个动画节点，用于将当前姿态扭曲以匹配目标位置/旋转。 | 可能为 `UK2Node_WarpToTarget` 或类似动画节点 |

### 使用示例（蓝图描述）

1.  **创建扭曲节点**: 在动画蓝图的动画图（AnimGraph）中，右键搜索 “Warp to Target” 并添加该节点。
2.  **连接输入**:
    *   将前一个动画状态或姿势节点的输出连接到 `WarpToTarget` 节点的 `Source Pose` 输入。
    *   通过蓝图逻辑计算或获取目标变换（Transform），将其连接到 `Target Transform` 输入。这个目标可以是世界空间中的一个点，或者是另一个骨骼的位置。
3.  **配置参数**:
    *   设置扭曲的强度 (`Alpha`)，控制从源姿态到目标姿态的混合程度。
    *   可能需要指定受扭曲影响的骨骼链（例如，仅影响从脊柱到手掌的骨骼）。
4.  **连接输出**: 将 `WarpToTarget` 节点的输出连接到动画图的最终姿态输出或后续的动画节点。

## C++ 用法

### 头文件引入

```cpp
#include "UAFWarpingModule.h" // 假设的模块头文件
```

### 基本用法

以下示例基于测试用例 (`UAFWarpingTests`) 的常见模式，展示了如何设置和使用一个扭曲操作（AnimOp）。

```cpp
// (示例，基于测试模式推断)
#include "UAFWarping/UAFAnimOp_WarpToTarget.h" // 假设的操作类头文件
#include "RigVMCore/RigVMMemory.h"

// 在某个测试或函数中
void Example_UseWarpToTargetAnimOp()
{
    // 1. 创建扭曲操作实例
    UUAFAnimOp_WarpToTarget* WarpOp = NewObject<UUAFAnimOp_WarpToTarget>();

    // 2. 设置目标数据 (例如，一个目标变换)
    FTransform TargetTransform(FRotator(0, 45, 0), FVector(100, 50, 0), FVector::OneVector);
    WarpOp->SetTargetTransform(TargetTransform);

    // 3. 准备一个内存存储和输入数据束 (Value Bundle) 用于评估
    FRigVMMemoryContainer Memory;
    // ... 初始化内存，加载当前动画数据 ...

    // 4. 评估扭曲操作，得到扭曲后的动画数据
    // WarpOp->Evaluate(/* context, input data bundle */);
    // 扭曲后的结果会输出到指定的输出数据束中。

    // 5. (可选) 清理
    WarpOp->MarkPendingKill();
}
```

### 进阶用法

结合动画图（AnimGraph）和 RigVM，在更复杂的逻辑中集成扭曲操作。这通常由引擎内部的动画图节点完成，但了解底层 API 有助于自定义。

```cpp
// (概念性示例)
// 在一个自定义的 AnimNode 中，可能会这样使用：
void FMyAnimNode::Evaluate_AnyThread(FPoseContext& Output)
{
    // ... 获取其他逻辑计算的 TargetTransform ...
    // ... 获取当前的输入姿势 ...

    // 调用扭曲操作来转换输入姿势
    // 假设存在一个工具函数或操作类来执行核心扭曲计算
    FPoseValueBundle SourcePoseBundle = /* 从输出上下文转换而来 */;
    FPoseValueBundle TargetPoseBundle = UUAFWarpingUtils::WarpPoseToTarget(
        SourcePoseBundle,
        TargetTransform,
        WarpAlpha,
        AffectedBones);

    // 将扭曲后的姿势写回输出
    // Output.Pose = TargetPoseBundle.ConvertToPose();
}
```

## Demo 示例

以下是一个简化、概念性的 C++ 类，演示了如何创建一个基本的扭曲操作。

```cpp
// MyCustomWarpOp.h
#pragma once
#include "UAFWarping/UAFAnimOpBase.h" // 假设的基础操作类
#include "MyCustomWarpOp.generated.h"

UCLASS()
class UMyCustomWarpOp : public UUAFAnimOpBase
{
    GENERATED_BODY()

public:
    // 设置扭曲的目标位置
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Warp")
    FVector TargetLocation;

    // 执行扭曲评估的核心函数 (示例)
    virtual void Evaluate(const FUAFAnimOpContext& Context, const FPoseValueBundle& Input, FPoseValueBundle& Output) override
    {
        // 1. 将输入数据包（包含骨骼位置等）复制到输出
        Output = Input;

        // 2. 执行简单的扭曲逻辑 (例如，仅移动根骨骼)
        // 这是一个极度简化的示意，真实实现会涉及复杂的骨骼链IK计算
        if (Output.Bones.Num() > 0)
        {
            // 假设第一个骨骼是根骨骼
            FTransform& RootTransform = Output.Bones[0].Transform;
            // 将根骨骼位置向目标位置移动一小步
            RootTransform.SetLocation(FMath::VInterpTo(RootTransform.GetLocation(), TargetLocation, Context.DeltaTime, 5.0f));
        }
    }
};
```

```cpp
// MyCustomWarpOp.cpp
#include "MyCustomWarpOp.h"

// 实现为空，逻辑主要在 Evaluate 虚函数中
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UAF` | UAF 核心框架，提供基础动画数据类型和操作接口。 |
| `UAFAnimGraph` | 提供动画图（AnimGraph）相关节点和编辑器集成。 |
| `UAFAnimNode` | 提供具体的动画节点（AnimNode）实现。 |
| `RigVM` | 虚拟机系统，用于驱动基于节点的动画逻辑和评估。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `b604d5ca` | Handle empty value bundle in modifier AnimOps | 修复了修改型动画操作对空数据包的处理 |
| 2026-04-14 | `7b3fe3c2` | Use FPoseValueBundle in AnimOp value bundle evaluator | 将 AnimOp 的值束评估器统一使用 FPoseValueBundle 类型 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版日志宏 UE_LOG 迁移为新的 UE_LOGF 格式 |
| 2026-04-09 | `153328f9` | UAFWarping - WarpToTargetNode | 实现或更新了核心的“扭曲到目标”动画节点 |
| 2026-04-06 | `0b5bc2d3` | UAFWarping - small code cleanup | 代码清理和小幅优化 |

### 维护评价

UAFWarping 是一个非常新的实验性插件，创建于 2025 年年中。从最近的提交记录（2026年4月）来看，它正处于**活跃开发**阶段。近期的更新集中在核心功能（WarpToTargetNode）的实现、API 统一（使用 FPoseValueBundle）以及代码健壮性提升（处理空数据包、日志迁移）。

**优点**：
- 作为 UAF 生态的一部分，与 Epic 官方的动画框架深度集成。
- 最近更新频繁，表明该功能正在被积极实现和完善。

**风险与限制**：
- **实验性状态**：位于 `Experimental` 目录下，且 `IsExperimentalVersion: true`，`EnabledByDefault: false`。API 和功能在未来版本中可能会发生重大变更，不建议在稳定的生产项目中作为核心依赖。
- **文档缺失**：没有官方文档链接，学习曲线较陡，需依赖源码和测试用例。
- **依赖关系复杂**：强依赖于 UAF、RigVM 等一系列插件，增加了项目复杂度。

**结论**：如果你正在跟进或学习 Epic 的最新动画技术栈（UAF），这是一个值得关注和实验的模块。但对于追求稳定性的项目，建议观望其离开实验阶段，或准备应对其 API 变更带来的维护成本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFWarping)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFWarping/Tests)