# Animation Warping

> Framework for animation and pose warping. This plugin includes Stride, Orientation, and Slope Warping alongside the Root Motion Delta animation attribute.

| 属性 | 值 |
|---|---|
| 中文名 | 动画扭曲 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画蓝图资产、动画节点） |
| 模块 | `AnimationWarpingRuntime` (Runtime), `AnimationWarpingEditor` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2021-12-04 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/AnimationWarping) | |

## 用途

AnimationWarping 插件提供了一个高级动画扭曲（Warping）框架，其核心目的是在运行时动态调整角色的骨骼姿势，以适应不同的移动速度、方向和地形坡度。它主要解决以下问题：

1.  **步幅扭曲（Stride Warping）**：根据角色的移动速度，动态拉伸或压缩腿部动画的步幅，避免在快速移动时出现滑步（Foot Sliding），或在慢速移动时步伐不自然。
2.  **方向扭曲（Orientation Warping）**：当角色的移动方向与其身体朝向（上半身）不一致时，自动旋转下半身和腿部以适应移动方向，常用于实现平滑的转身和侧移动画。
3.  **斜率扭曲（Slope Warping）**：根据地面坡度调整角色姿势，例如上坡时身体前倾，下坡时身体后仰，使动画与地形自然贴合。

它通过分析角色的根运动（Root Motion）增量（`FAnimNode_RootMotionDelta`）并驱动一系列扭曲动画节点来实现这些效果，是制作高品质、响应迅速角色动画的关键技术。

## 使用场景

-   **开放世界游戏**：角色在复杂地形上跑动时，使用斜率扭曲让身体自然适应上下坡，使用步幅扭曲确保步伐与速度匹配。
-   **竞技或动作游戏**：角色需要快速转向或侧移时，使用方向扭曲平滑过渡下半身朝向，避免生硬的转身动作。
-   **动画蓝图高级混合**：作为动画蓝图中的一个节点，与其它动画层（如上半身瞄准、下半身移动）结合使用，实现高度动态和自适应的角色动画。

## 蓝图用法

AnimationWarping 主要通过在动画蓝图中添加和配置专门的动画节点来使用。以下是在动画蓝图中可能使用到的核心节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Stride Warping` | 根据移动速度扭曲腿部动画步幅。 | `FAnimNode_StrideWarping` |
| `Orientation Warping` | 根据移动方向扭曲下半身朝向。 | `FAnimNode_OrientationWarping` |
| `Slope Warping` | 根据地面坡度扭曲角色姿势。 | (可视为 `FAnimNode_OrientationWarping` 的一种应用模式) |

### 使用示例（蓝图描述）

1.  **配置步幅扭曲**：
    *   在动画蓝图的 `AnimGraph` 中添加一个 `Stride Warping` 节点。
    *   在节点的细节面板中，设置 `PelvisBone`（骨盆骨骼，如 `pelvis`）和 `IKFootRootBone`（IK脚部根节点，如 `ik_foot_root`）。
    *   添加 `Foot Definitions`，为每只脚定义其 `IKFootBone`（IK脚部骨骼）、`FKFootBone`（FK脚部骨骼）和 `ThighBone`（大腿骨骼）。
    *   将角色的速度向量（来自 `CharacterMovement` 组件）连接到节点的输入引脚。
    *   将该节点的输出连接到 `Output Pose` 节点。

2.  **配置方向扭曲**：
    *   在动画蓝图中添加一个 `Orientation Warping` 节点。
    *   设置 `IKFootRootBone` 和 `IKFootBones`（IK脚部骨骼数组）。
    *   设置 `Orientation Angle`（扭曲角度，通常由移动方向与身体朝向的差值计算得出）。
    *   将该节点串联在移动动画节点之后，或与其它扭曲节点组合使用。

**注意**：具体实现可能涉及使用 `Animation Modifier Library` 中的动画修改器来预先处理动画资产，以包含扭曲所需的数据。

## C++ 用法

主要通过实例化和配置动画节点（`FAnimNode_*`）在 C++ 动画实例或自定义动画图节点中使用。

### 头文件引入

```cpp
#include "Animation/AnimNode_StrideWarping.h"
#include "Animation/AnimNode_OrientationWarping.h"
// 可能还需要根运动增量节点
#include "Animation/AnimNode_RootMotionDelta.h"
```

### 基本用法

以下示例展示了如何在测试环境中配置和求值一个 `StrideWarping` 节点（基于 `Tests/Private/AnimationWarpingTestFixture.h` 的测试模式）：

```cpp
// 来源: Tests/Private/AnimationWarpingTestFixture.h - ConfigureStrideWarping
// 创建并配置一个步幅扭曲节点
FAnimNode_StrideWarping StrideWarpingNode;
// 设置必要的骨骼引用
StrideWarpingNode.PelvisBone.BoneName = TEXT("pelvis");
StrideWarpingNode.IKFootRootBone.BoneName = TEXT("ik_foot_root");
// 设置扭曲模式为手动（由外部输入驱动）
StrideWarpingNode.Mode = EWarpingEvaluationMode::Manual;
// 启用根据地面法线调整步幅方向
StrideWarpingNode.bOrientStrideDirectionUsingFloorNormal = true;
// 添加脚部定义
FStrideWarpingFootDefinition FootDefLeft;
FootDefLeft.IKFootBone.BoneName = TEXT("ik_foot_l");
FootDefLeft.FKFootBone.BoneName = TEXT("foot_l");
FootDefLeft.ThighBone.BoneName = TEXT("thigh_l");
StrideWarpingNode.FootDefinitions.Add(FootDefLeft);
// ... 为右脚添加类似定义
```

### 进阶用法

在自定义动画图节点中，你可能需要结合 `FAnimInstanceProxy` 来管理动画更新和求值流程。

```cpp
// 模拟一个简单的动画实例代理和求值上下文
// 来源: Tests/Private/AnimationWarpingTestFixture.h - FAnimWarpingFixture
class FMyAnimInstanceProxy : public FAnimInstanceProxy
{
    // ... 代理实现
};

// 初始化节点
FAnimationInitializeContext InitContext(&AnimInstanceProxy);
StrideWarpingNode.Initialize_AnyThread(InitContext);

// 缓存骨骼
FAnimationCacheBonesContext CacheContext(&AnimInstanceProxy);
StrideWarpingNode.CacheBones_AnyThread(CacheContext);

// 更新节点（传入 DeltaTime）
FAnimationUpdateContext UpdateContext(&AnimInstanceProxy, DeltaTime);
StrideWarpingNode.UpdateInternal(UpdateContext);

// 求值节点，获取输出的骨骼变换
FComponentSpacePoseContext CSPoseContext(&AnimInstanceProxy);
TArray<FBoneTransform> OutBoneTransforms;
// ... 初始化 CSPoseContext 为参考姿势
StrideWarpingNode.EvaluateSkeletalControl_AnyThread(CSPoseContext, OutBoneTransforms);
// OutBoneTransforms 中现在包含了经过扭曲处理的骨骼变换数据
```

## Demo 示例

一个在控制台单元测试中验证步幅扭曲节点基本功能的最小示例。它展示了如何设置一个临时骨骼、配置节点并执行求值。

```cpp
// Header: (假设文件名为 StrideWarpingDemo.h)
#pragma once
#include "CoreMinimal.h"
#include "Animation/AnimNode_StrideWarping.h"
// ... 其他必要头文件

class FStrideWarpingDemo
{
public:
    // 创建一个简单的测试骨架
    static USkeleton* CreateSimpleSkeleton();
    // 运行一个步幅扭曲的基本求值测试
    static bool RunBasicStrideWarpingTest();
};
```

```cpp
// Source: (假设文件名为 StrideWarpingDemo.cpp)
#include "StrideWarpingDemo.h"
#include "Animation/AnimInstanceProxy.h"

USkeleton* FStrideWarpingDemo::CreateSimpleSkeleton()
{
    // 实现类似测试 Fixture 中的 MakeTestSkeleton，创建一个包含 pelvis, thigh_l 等骨骼的简单骨架。
    // ... (参考测试夹具代码)
    return Skeleton;
}

bool FStrideWarpingDemo::RunBasicStrideWarpingTest()
{
    USkeleton* Skeleton = CreateSimpleSkeleton();
    if (!Skeleton) return false;

    // 设置动画代理和所需骨骼
    FAnimInstanceProxy Proxy;
    TArray<FBoneIndexType> RequiredBones;
    for (int32 Idx = 0; Idx < Skeleton->GetReferenceSkeleton().GetNum(); ++Idx)
    {
        RequiredBones.Add(Idx);
    }
    const UE::Anim::FCurveFilterSettings FilterSettings(UE::Anim::ECurveFilterMode::DisallowAll);
    Proxy.GetRequiredBones().InitializeTo(RequiredBones, FilterSettings, *Skeleton);

    // 创建并配置扭曲节点
    FAnimNode_StrideWarping Node;
    Node.PelvisBone.BoneName = TEXT("pelvis");
    Node.IKFootRootBone.BoneName = TEXT("ik_foot_root");
    Node.Mode = EWarpingEvaluationMode::Manual;
    // ... (配置 FootDefinitions)

    // 初始化、更新、求值
    FAnimationInitializeContext InitCtx(&Proxy);
    Node.Initialize_AnyThread(InitCtx);
    FAnimationCacheBonesContext CacheCtx(&Proxy);
    Node.CacheBones_AnyThread(CacheCtx);
    FAnimationUpdateContext UpdateCtx(&Proxy, 1.f/30.f); // 假设 30fps
    Node.UpdateInternal(UpdateCtx);

    FComponentSpacePoseContext EvalCtx(&Proxy);
    EvalCtx.ResetToRefPose(); // 使用参考姿势作为输入
    TArray<FBoneTransform> OutTransforms;
    Node.EvaluateSkeletalControl_AnyThread(EvalCtx, OutTransforms);

    // 检查输出是否有效（不含 NaN）
    for (const FBoneTransform& BT : OutTransforms)
    {
        if (BT.Transform.ContainsNaN())
        {
            return false;
        }
    }
    return true;
}
```

## 模块依赖

要使用 AnimationWarping 插件的功能，你的模块（通常是游戏模块或动画模块）需要在 `.Build.cs` 文件中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `AnimationWarpingRuntime` | 包含核心的扭曲动画节点（如 `FAnimNode_StrideWarping`）和相关数据结构。这是必须依赖的模块。 |
| `AnimationModifierLibrary` | （可选）如果使用该插件提供的动画修改器（Animation Modifiers）来预处理动画资产以支持扭曲，则需要依赖此模块。 |

**注意**：无需显式依赖 `AnimationWarpingEditor`，它是编辑器工具，不影响运行时功能。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `42c8bcfa` | Fix tooltip on ABP steering node | 修复动画蓝图中转向节点的工具提示信息。 |
| 2026-04-24 | `afab60f0` | UE-363190 - Replace crash-assert NaN guards with UE_LOGF + safe-default in StrideWarping and Orienta | 修复步幅扭曲和方向扭曲中的崩溃问题，将 NaN 断言替换为日志和安全默认值。 |
| 2026-04-24 | `42548e51` | Fix non-unity build: forward-declare UAnimationAsset in anim node headers | 修复非统一编译下的编译错误，在动画节点头文件中前向声明 `UAnimationAsset`。 |
| 2026-04-23 | `23ccd2bd` | Add Anim Node Functions to support applying a delta to the offset root bone's internal simulated tra | 新增动画节点函数，支持对偏移根骨骼的内部模拟变换应用增量。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的日志宏 `UE_LOG` 迁移到新宏 `UE_LOGF`。 |

### 维护评价

-   **创建时间**：2021年12月从 Experimental 迁移至 Beta，目前标记为非实验性，是成熟的动画功能模块。
-   **维护频率**：最近（2026年4月）有多次提交，包括功能增强、Bug 修复和代码现代化（日志迁移），表明该插件处于**活跃维护**状态。
-   **已知问题**：近期的更新修复了与 NaN 值相关的崩溃问题，说明之前版本可能存在相关稳定性风险，但现已解决。
-   **推荐使用**：**推荐使用**。AnimationWarping 是UE5提供的官方高质量动画扭曲解决方案，适用于对角色动画真实性有较高要求的项目。由于最近的维护集中在稳定性和功能完善上，可以放心集成。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/AnimationWarping)
-   [官方文档](https://docs.unrealengine.com/5.0/en-US/animation-warping-in-unreal-engine/)（请在 Epic 官方文档站搜索 “Animation Warping” 获取最新信息）
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/AnimationWarping/Tests)