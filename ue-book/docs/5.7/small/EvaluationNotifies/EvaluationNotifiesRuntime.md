# Evaluation Notifies

> A system for animation notifies which have animation evaluation time code.

| 属性 | 值 |
|---|---|
| 中文名 | 评估通知 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `EvaluationNotifiesRuntime` (Runtime), `EvaluationNotifiesEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EvaluationNotifies) | |

## 用途

传统动画通知（`UAnimNotify` / `UAnimNotifyState`）仅在动画播放的特定时间点触发事件，无法在通知持续期间动态干预骨骼变形或根骨运动。本插件提供**评估通知**（Evaluation Notifies）框架，允许开发者注册自定义的评估时处理器，在动画评估循环中实时计算并修改骨骼位置、旋转以及根运动，实现更精细的动画控制。

插件解决了以下问题：
- 动画播放过程中的实时对齐（如角色转向、脚部着地调整）
- 根据动画根运动动态调整目标变换（如路径弯曲、方向对齐）
- 在通知时间段内平滑混合 IK 效果（如两骨 IK）
- 与 AnimNext 动画系统深度集成，支持基于任务图的评估管线

## 使用场景

- **角色移动转向**：当角色播放转向动画时，使用 `Alignment` 通知根据实际移动方向动态弯曲动画轨迹。
- **脚部着地调整**：利用 `AlignToGround` 通知将脚部骨骼对齐到地面高度，避免悬空或穿透。
- **动态 IK**：在角色拿取物品或触墙时，使用 `TwoBoneIK` 通知调整手肘/膝盖位置。
- **动画蓝图高级控制**：在动画蓝图中使用 `FAnimNode_EvaluationNotifies` 节点，为已有动画序列注入自定义评估逻辑。
- **人工智能动画同步**：配合 UAF（Unreal Animation Framework）和 RigVM，实现复杂动画状态机中的精确变形。

## 蓝图用法

插件主要暴露了两类可蓝图使用的元素：**动画通知状态类**（继承自 `UAnimNotifyState`）和**动画蓝图节点**（`FAnimNode_EvaluationNotifies`）。

### 动画通知状态

这些类可以拖放到动画序列的通知轨道中，并在持续时间内自动驱动评估逻辑。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Alignment`（预设） | 通用对齐通知，可配置平移/旋转弯曲曲线和转向平滑 | `UNotifyState_AlignmentBase` |
| `AlignToGround`（预设） | 将指定骨骼动态对齐到地面，基于根运动高度调整 | `UE::UAF::FEvaluationNotify_AlignToGroundInstance` |
| `TwoBone IK`（预设） | 两骨 IK 通知，支持目标位置、拉伸和混合时间 | `UNotifyState_TwoBoneIK` |

**使用示例**（以 TwoBone IK 为例）：
1. 在动画序列的时间轴上添加 `Two Bone IK` 通知状态。
2. 设置 `IK Bone`（例如左手腕），`Effector Location`（世界空间目标位置），并调整 `Blend In Time` / `Blend Out Time`。
3. 运行时通知激活期间，骨骼链将自动向目标位置插值，并在通知结束后恢复原状。

### 动画蓝图节点

在动画蓝图中添加 `AnimNode_EvaluationNotifies` 节点（作为控制节点），用于将评估通知逻辑附加到骨架控制管道。

**核心属性**（蓝图可读写）：
- `Current Anim Asset`：当前播放的动画资产，用于提取根运动数据。
- `Current Anim Asset Time`：当前播放时间（秒）。
- `Current Anim Asset Mirrored`：是否镜像动画。
- `Mirror Data Table`：镜像所需的数据表。
- `Named Transforms`：命名变换映射，供通知实例访问外部骨骼空间。

**连接方式**：
1. 在动画蓝图事件图或 `Update Animation` 事件中，将当前动画资产和时间赋值给该节点的输入端。
2. 将节点输出连接到 `Enable Skeletal Control` 或直接作为 `Output Pose`。

## C++ 用法

### 头文件引入

```cpp
#include "EvaluationNotifies/AnimNode_EvaluationNotifies.h"
#include "EvaluationNotifies/AnimNotifyState_Alignment.h"
#include "EvaluationNotifies/AnimNotifyState_TwoBoneIK.h"
```

### 基本用法

**注册自定义评估通知处理器**（类似 `UAnimNotifyState` 但具有评估逻辑）：

```cpp
// 1. 定义评估实例结构体（继承自 FEvaluationNotifyInstance）
struct FMyCustomNotifyInstance : public FEvaluationNotifyInstance
{
    virtual void Start(const UAnimSequenceBase* AnimationAsset) override
    {
        // 通知开始的初始化逻辑
    }

    virtual void Update(const UAnimSequenceBase* AnimationAsset, float CurrentTime, float DeltaTime, bool bIsMirrored,
        const UMirrorDataTable* MirrorDataTable, FTransform& RootBoneTransform,
        const TMap<FName, FTransform>& NamedTransforms, FComponentSpacePoseContext& Output,
        TArray<FBoneTransform>& OutBoneTransforms) override
    {
        // 每帧更新骨骼变换，可修改 OutBoneTransforms
    }

    virtual void End() override
    {
        // 通知结束的清理
    }
};

// 2. 注册处理器（通常在模块启动时）
FAnimNode_EvaluationNotifies::RegisterEvaluationHandler(
    UMyCustomNotifyState::StaticClass(),          // 你的 UAnimNotifyState 子类
    FMyCustomNotifyInstance::StaticStruct()       // 对应的评估实例结构
);
```

**在动画蓝图中使用自定义节点**：

```cpp
// 创建 FAnimNode_EvaluationNotifies 子类或直接使用
FAnimNode_EvaluationNotifies* EvalNode = NewObject<FAnimNode_EvaluationNotifies>();
EvalNode->CurrentAnimAsset = MyAnimationAsset;
EvalNode->CurrentAnimAssetTime = 0.5f;
```

### 进阶用法

**利用 Alignment 通知进行动态转向**：

```cpp
// 假设已有角色动画组件和 UNotifyState_AlignmentBase 通知
// 在动画评估循环中，Alignment 通知会自动根据根运动曲线计算目标方向

// 可通过子类化 FEvaluationNotify_AlignmentInstance 自定义目标获取逻辑
struct FMyAlignmentInstance : public FEvaluationNotify_AlignmentInstance
{
    virtual bool GetTargetTransform(UE::UAF::FEvaluationNotifiesTrait::FInstanceData& TraitInstanceData,
        FTransform& TargetTransform) override
    {
        // 返回自定义目标（例如从导航系统获取）
        TargetTransform = FTransform(FRotator(0, DesiredYaw, 0), GroundLocation);
        return true;
    }
};
```

**与 AnimNext 集成**（使用 `FEvaluationNotifiesTrait`）：

```cpp
// 在 AnimNext 任务图中，通过 trait 注册评估处理器
UE::UAF::FEvaluationNotifiesTrait::RegisterEvaluationHandler(
    UMyCustomNotifyState::StaticClass(),
    FMyCustomNotifyInstance::StaticStruct()
);
// 然后在动画评估时，trait 会自动解析通知并分发到对应实例
```

## Demo 示例

以下是一个最小化 C++ 示例，展示如何在自定义动画通知状态中使用评估通知框架来调整脚部旋转。

**MyFootRotateNotifyState.h**：

```cpp
#pragma once
#include "EvaluationNotifies/AnimNode_EvaluationNotifies.h"
#include "MyFootRotateNotifyState.generated.h"

UCLASS(BlueprintType)
class UNotifyState_FootRotate : public UAnimNotifyState
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, Category = Settings)
    FName FootBoneName = "foot_l";

    UPROPERTY(EditAnywhere, Category = Settings)
    float TargetPitch = 0.0f;
};

USTRUCT()
struct FFootRotateNotifyInstance : public FEvaluationNotifyInstance
{
    GENERATED_BODY()
    virtual void Update(const UAnimSequenceBase* AnimationAsset, float CurrentTime, float DeltaTime,
        bool bIsMirrored, const UMirrorDataTable* MirrorDataTable, FTransform& RootBoneTransform,
        const TMap<FName, FTransform>& NamedTransforms, FComponentSpacePoseContext& Output,
        TArray<FBoneTransform>& OutBoneTransforms) override
    {
        // 查找脚部骨骼索引
        int32 FootIndex = Output.Pose.GetPose().GetBoneContainer().GetPoseBoneIndexForBoneName(FootBoneName);
        if (FootIndex == INDEX_NONE) return;

        // 修改脚部旋转
        FTransform FootTransform = Output.Pose.GetComponentSpaceTransform(FootIndex);
        FootTransform.SetRotation(FRotator(TargetPitch, 0, 0).Quaternion());
        OutBoneTransforms.Add(FBoneTransform(FootIndex, FootTransform));
    }

    FName FootBoneName;
    float TargetPitch;
};
```

**MyModule.cpp**（模块启动注册）：

```cpp
#include "MyFootRotateNotifyState.h"
#include "Animation/AnimInstance.h"

void FMyModule::StartupModule()
{
    FAnimNode_EvaluationNotifies::RegisterEvaluationHandler(
        UNotifyState_FootRotate::StaticClass(),
        FFootRotateNotifyInstance::StaticStruct()
    );
}
```

然后在动画序列中添加 `FootRotate` 通知状态，并设置脚骨名称和目标俯仰角。运行时通知期间脚部将被强制旋转。

## 模块依赖

由于插件依赖于 UAF、RigVM 等高级框架，以下是其独特依赖（省略了核心引擎模块）：

| 模块 | 用途 |
|---|---|
| `AnimationWarping` | 提供动画弯曲曲线和根运动提取工具 |
| `RigVM` | 用于与动画控制任务图集成 |
| `UAF` | Unreal Animation Framework，提供动画评估管线和 trait 系统 |
| `UAFAnimGraph` | UAF 的动画蓝图扩展，支持可视化的通知配置 |
| `StructUtils` | 用于 `InstancedStruct` 和动态数据结构 |

若只使用基本评估通知节点（不使用 AnimNext trait），则最低依赖为 `AnimationWarping` 和 `StructUtils`。

## 维护状态

### 近期更新

- 2025-06-26 effdabd2 UAF: Moved/renamed AnimNext and AnimNextAnimGraph plugins
- 2025-06-25 bdc91c59 UAF: Namespace renamed
- 2025-06-10 57979323 AnimNext: Pass-by-ref runtime refactor
- 2025-05-26 4aabc348 Alignment bug fixes
- 2025-05-02 e63e0195 Add options for flattening alignment transforms

### 维护评价

- **创建时间**：2025-05-02，至今约 5 个月，属于非常新的插件。
- **更新频率**：近 4 个月有多次提交，但多为 UAF 重构或重命名，功能性更新较少（仅 5 月有一次对齐修复和一次功能添加）。
- **活跃度**：目前可见更新停止在 6 月底，距今约 4 个月未刷新。考虑到插件被标记为**实验性**，可能处于早期开发阶段，后续可能会随 UAF 框架演化而变化。
- **已知限制**：插件的类结构依赖 UAF 和 RigVM 内部接口，API 不稳定；`IsExperimentalVersion=true` 表明不建议用于生产环境。
- **推荐情况**：仅推荐在 UAF 相关试验性项目或研发原型中使用。生产项目请等待其稳定或使用标准动画通知组合实现。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EvaluationNotifies)
- [官方文档]（暂无，插件太新）
- [测试用例]（未在源码中发现独立测试目录）