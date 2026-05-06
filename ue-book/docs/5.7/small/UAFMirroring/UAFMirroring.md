# UAF Mirroring

> Keyframe mirroring for UAF

| 属性 | 值 |
|---|---|
| 中文名 | UAF 镜像 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFMirroring` (Runtime), `UAFMirroringUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFMirroring) | |

---

## 用途

UAF Mirroring 是 [Unreal Animation Framework (UAF)](https://docs.unrealengine.com/5.3/AnimationFramework/) 的一个实验性插件，为 UAF 的关键帧动画提供镜像能力。它可以对输入的关键帧数据（骨骼变换、动画曲线、属性）进行镜像处理，常用于制作对称动画（如跑步、攻击动作的左右互换）、或对同一主控动画的左右侧应用相反的效果。

该插件通过 **Trait** 系统集成到 UAF 动画图中，提供两种 trait 类型：
- **Mirroring Trait**（主镜像）：直接镜像输入节点的输出。
- **Additive Mirroring Trait**（附加镜像）：仅镜像父级 trait 的输出，适合在叠加层（如混合空间或层叠动画）中使用。

---

## 使用场景

- 你在使用 **UAF** 制作角色动画，需要快速生成左右对称的关键帧（例如将右手挥舞剑的动画镜像为左手）。  
- 你需要对已有动画数据进行单轴镜像（X、Y、Z 轴），而不复制整个动画资源。  
- 你希望在动画图运行期间动态切换镜像状态（例如根据角色装备的武器）。  

---

## 蓝图用法

该插件不提供直接的蓝图可调用函数，而是通过 **UAF 动画图** 中的 Trait 节点暴露配置。在 UAF 动画图中，你可以添加以下两个 Trait：

- **Mirroring**（`FMirroringTraitSharedData`）  
- **Mirroring（Additive）**（`FMirroringAdditiveTraitSharedData`）

每个 Trait 都包含两个可编辑的结构体：

### 1. 镜像设置参数（`FUAFMirroringTraitSetupParams`）

| 属性 | 类型 | 描述 |
|---|---|---|
| `Mirror` | bool | 是否启用镜像 |
| `Mirror Data Table` | UMirrorDataTable | 定义骨骼镜像映射和镜像轴的数据表 |

### 2. 镜像应用于通道（`FUAFMirroringTraitApplyToParams`）

| 属性 | 类型 | 描述 |
|---|---|---|
| `Bones` | bool | 是否镜像骨骼变换 |
| `Curves` | bool | 是否镜像动画曲线 |
| `Attributes` | bool | 是否镜像自定义属性 |

**使用示例（蓝图文字描述）**：
1. 打开 UAF 动画图，添加一个 **Mirroring** Trait 节点。
2. 将 Trait 的 `Input` 引脚连接到要镜像的动画节点（如播放动画的节点）。
3. 在 Details 面板中，展开 **Setup** 部分，勾选 `Mirror`，并指定一个 `Mirror Data Table`（需提前创建，包含骨骼名称对和镜像轴）。
4. 在 **Apply To** 部分，选择需要镜像的通道（通常全部勾选）。
5. 编译后，该 trait 的输出即为镜像后的关键帧数据。

---

## C++ 用法

### 头文件引入

```cpp
#include "Mirroring/Mirroring.h"
```

### 基本用法

使用 `UE::UAF::MirrorPose` 直接对 `FLODPose` 进行镜像（需要 `UMirrorDataTable` 资源）：

```cpp
#include "Mirroring/Mirroring.h"
#include "Animation/MirrorDataTable.h"

void MyAnimNode::MirrorCurrentPose(FLODPose& Pose, UMirrorDataTable* MirrorTable)
{
    if (MirrorTable)
    {
        UE::UAF::MirrorPose(Pose, *MirrorTable);
    }
}
```

*来源：`Engine/Plugins/Experimental/UAF/UAFMirroring/Private/Mirroring.h`，第 81-88 行*

---

### 进阶用法

如果需要高性能的反复镜像（例如每帧调用），建议预计算镜像映射和参考姿态数据，避免重复从数据表查询：

```cpp
#include "Mirroring/Mirroring.h"
#include "Animation/MirrorDataTable.h"

// 在初始化时构建缓存
void MyAnimNode::BuildMirrorCache(const FReferencePose& RefPose, const UMirrorDataTable* MirrorTable)
{
    const int32 NumBones = UE::UAF::GetNumOfBonesForMirrorData(RefPose);
    MirrorMap.SetNum(NumBones);
    RefPoseRotations.SetNum(NumBones);
    RefPoseCorrections.SetNum(NumBones);

    // 1. 从数据表构建骨骼索引映射
    UE::UAF::BuildMeshBoneIndexMirrorMap(RefPose, *MirrorTable, MirrorMap);

    // 2. 构建参考姿态旋转（网格空间）
    UE::UAF::BuildReferencePoseMirrorData(RefPose, MirrorTable->MirrorAxis, MirrorMap, RefPoseRotations, RefPoseCorrections);
}

// 每帧调用快速镜像
void MyAnimNode::FastMirrorPose(FLODPose& Pose)
{
    UE::UAF::MirrorPose(Pose, MirrorAxis, MirrorMap, RefPoseRotations, RefPoseCorrections);
}
```

*来源：`Engine/Plugins/Experimental/UAF/UAFMirroring/Private/Mirroring.h`*

---

## Demo 示例

以下是一个最小化的 C++ 类，演示如何在自定义 UAF 动画节点中使用镜像（结合 UAF 框架，但省略了骨架代码）：

**MyMirrorAnimNode.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimNodeBase.h"
#include "Mirroring/Mirroring.h"
#include "Animation/MirrorDataTable.h"
#include "MyMirrorAnimNode.generated.h"

USTRUCT(BlueprintType)
struct FMyMirrorAnimNode : public FAnimNode_Base
{
    GENERATED_BODY()

    // 输入引脚
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = Links)
    FPoseLink SourcePose;

    // 镜像数据表
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = Settings)
    TObjectPtr<UMirrorDataTable> MirrorTable;

    // 缓存（仅在编辑器或运行时初始化）
    TArray<FBoneIndexType> MirrorMap;
    TArray<FQuat> RefPoseRotations;
    TArray<FQuat> RefPoseCorrections;
    bool bCacheValid = false;

    virtual void Evaluate_AnyThread(FPoseContext& Output) override;
};
```

**MyMirrorAnimNode.cpp**
```cpp
#include "MyMirrorAnimNode.h"

void FMyMirrorAnimNode::Evaluate_AnyThread(FPoseContext& Output)
{
    // 先计算源姿势
    FPoseContext SourceContext(Output);
    SourcePose.Evaluate(SourceContext);

    // 如果设置了数据表，执行镜像
    if (MirrorTable && bCacheValid)
    {
        FLODPose LODPose = SourceContext.Pose; // 临时转换（实际需处理 LOD）
        // 若缓存有效，使用缓存快速镜像
        UE::UAF::MirrorPose(LODPose, MirrorTable->MirrorAxis, MirrorMap, RefPoseRotations, RefPoseCorrections);
        Output.Pose = LODPose;
    }
    else
    {
        // 无镜像，直接传递
        Output = SourceContext;
    }
}
```

（注意：实际 UAF 节点需继承 `FAnimNextBaseNode` 并正确实现 Trait 接口，此处仅为示意。）

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UAF` | 核心动画框架，提供 Trait 系统、关键帧管道等 |
| `UAFAnimGraph` | 动画图编辑支持，用于在动画蓝图中配置 Trait |

**省略常见依赖**：`Core`, `CoreUObject`, `Engine`, `Slate`, `SlateCore`, `UMG`, `InputCore` 等标准模块。

---

## 维护状态

### 近期更新

| 日期 | Commit Hash | 说明 |
|---|---|---|
| 2025-08-20 | `da73fa04` | 修复当跳过镜像骨骼或属性时，完全中止镜像任务的问题 |
| 2025-08-20 | `c983bdd2` | UAF Mirroring 改进（未提供详情） |
| 2025-08-18 | `e8a6162f` | UAF 镜像支持的首次提交 |

### 维护评价

- 该插件创建于 **2025-08-18**，属于非常新的实验性功能。
- 最近更新为 **2025-08-20**，有实质性 bug 修复和功能改进。
- 开发处于早期阶段，可能存在较多未知问题，API 可能在未来版本中发生变化。
- 由于是实验性插件，默认未启用，需在项目插件中手动开启。
- **建议**: 仅用于评估和测试，不建议直接用于生产项目。如果确实需要镜像功能，可考虑使用传统的 `UMirrorDataTable` + `ANIMBP` 手动实现，或等待该插件稳定。

---

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFMirroring)
- [官方文档](https://docs.unrealengine.com/)（该插件暂无独立文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFMirroring/Tests)（若存在）