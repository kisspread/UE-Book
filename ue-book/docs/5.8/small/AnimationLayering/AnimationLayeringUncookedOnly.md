# Animation Layering

> （Description 为空）

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AnimationLayering` (Runtime), `AnimationLayeringUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/AnimationLayering) | |

## 用途

AnimationLayering 是一个实验性动画插件，提供**基于骨骼蒙版（Bone Mask）的动画分层混合**能力。它解决的核心问题是：在动画蓝图中实现**按骨骼部位精细控制混合权重**，而非对整个骨骼网格体使用统一的混合比例。

具体功能包括：

- **骨骼蒙版混合（Bone Mask Blend）**：通过为每根骨骼定义独立的权重值，实现身体不同部位播放不同动画。例如：上半身播放射击动画，下半身播放跑步动画，过渡区域（脊柱）自动混合。
- **高级骨骼复制（Copy Bone Advanced）**：将源骨骼的变换以高级方式复制到目标骨骼，支持更精细的控制选项。
- **骨骼运动复制（Copy Bone Motion）**：专门用于复制骨骼的运动（位移/旋转），适用于需要将一个骨架的运动迁移到另一个骨架的场景。

该插件默认禁用且标记为实验性，说明 Epic 尚未将其作为稳定 API 推荐用于生产环境。

## 使用场景

- 你需要实现**上下半身分层动画**（如角色边跑边射击），且需要精确控制每根骨骼的混合权重 → 用 Bone Mask 节点
- 你需要将一个骨架的骨骼变换**高级复制**到另一个骨架，且需要比标准 CopyBone 更多的控制选项 → 用 Copy Bone Advanced 节点
- 你需要将骨骼的**运动（Motion）**从源复制到目标，而非完整的变换 → 用 Copy Bone Motion 节点

## 蓝图用法

该插件提供的所有节点均为**动画蓝图（Animation Blueprint）中的 AnimGraph 节点**，不是普通的蓝图函数节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Bone Mask` | 基于骨骼蒙版的多路混合节点，为每根骨骼定义独立混合权重 | `UAnimGraphNode_BoneMask` |
| `Copy Bone Advanced` | 高级骨骼变换复制，扩展自标准 CopyBone | `UAnimGraphNode_CopyBoneAdvanced` |
| `Copy Bone Motion` | 仅复制骨骼运动（位移/旋转），标记为实验性 | `UAnimGraphNode_CopyBoneMotion` |

### 使用示例（动画蓝图描述）

**骨骼蒙版混合示例**：

1. 打开动画蓝图，进入 AnimGraph 编辑器
2. 右键搜索 "Bone Mask"，添加 `Bone Mask` 节点
3. 该节点继承自 `BlendListBase`，可连接多个输入动画
4. 在 Details 面板中配置 `FAnimNode_BoneMask` 的骨骼权重映射
5. 为不同骨骼区域（如 spine_01、spine_02、upperarm_l 等）设置不同的混合权重
6. 连接输入动画：如 Input 0 连接跑步动画，Input 1 连接射击动画

**骨骼运动复制示例**：

1. 在 AnimGraph 中添加 "Copy Bone Motion" 节点
2. 配置源骨骼和目标骨骼名称
3. 该节点会将源骨骼的运动复制到目标骨骼

## C++ 用法

### 头文件引入

```cpp
// 运行时节点（动画逻辑）
#include "BoneMask/AnimNode_BoneMask.h"
#include "BoneControllers/AnimNode_CopyBoneAdvanced.h"
#include "BoneControllers/AnimNode_CopyBoneMotion.h"

// 编辑器图节点（仅编辑器/AnimGraph 使用）
#include "AnimGraph/AnimGraphNode_BoneMask.h"
#include "AnimGraph/AnimGraphNode_CopyBoneAdvanced.h"
#include "AnimGraph/AnimGraphNode_CopyBoneMotion.h"
```

### 基本用法

该插件主要通过动画蓝图的 AnimGraph 节点使用。在 C++ 中，你可以直接使用底层的 `FAnimNode_*` 结构体：

```cpp
// 在自定义 AnimInstance 或 AnimNode 中使用 BoneMask 节点
// FAnimNode_BoneMask 继承自 FAnimNode_BlendListBase
FAnimNode_BoneMask BoneMaskNode;
// 配置骨骼权重等属性后，在 Evaluate 中调用
BoneMaskNode.Evaluate_AnyThread(Output, Context);
```

### 进阶用法

`FBoneMaskEntryDetails` 提供了自定义属性面板，用于在编辑器中可视化编辑骨骼蒙版权重。如果你需要扩展骨骼蒙版的编辑界面，可以参考此自定义实现：

```cpp
// 自定义属性类型注册
// BoneMaskDetailCustomization.h 中的 FBoneMaskEntryDetails
// 实现了 IPropertyTypeCustomization 接口
class FBoneMaskEntryDetails : public IPropertyTypeCustomization
{
    static TSharedRef<IPropertyTypeCustomization> MakeInstance();
    virtual void CustomizeHeader(...) override;
    virtual void CustomizeChildren(...) override;
};
```

## Demo 示例

由于该插件主要通过动画蓝图的可视化节点使用，以下是一个最小的 C++ 自定义动画节点示例，展示如何在代码中集成骨骼蒙版：

```cpp
// MyAnimInstance.h
#pragma once

#include "Animation/AnimInstance.h"
#include "MyAnimInstance.generated.h"

UCLASS()
class UMyAnimInstance : public UAnimInstance
{
    GENERATED_BODY()

public:
    // 在动画蓝图中通过此变量控制骨骼蒙版的混合权重
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Layering")
    float UpperBodyWeight = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Layering")
    float LowerBodyWeight = 0.0f;
};
```

```cpp
// MyAnimInstance.cpp
#include "MyAnimInstance.h"

// 实际的骨骼蒙版配置在动画蓝图的 AnimGraph 中完成
// 通过 UPROPERTY 变量驱动混合权重
```

> **注意**：该插件的核心价值在于 AnimGraph 节点，建议直接在动画蓝图中使用，而非纯 C++ 集成。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AnimGraphRuntime` | 动画图运行时节点基类（FAnimNode_*） |
| `BlueprintGraph` | 动画蓝图图节点基类（UAnimGraphNode_*） |

## 维护状态

### 近期更新

由于该插件为实验性且创建时间较新，暂无可用的 git log 历史记录。

### 维护评价

- **实验性状态**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，明确标记为实验性功能
- **版本号**：0.1，处于早期开发阶段
- **稳定性风险**：实验性插件的 API 可能在后续版本中发生破坏性变更
- **推荐程度**：仅建议用于原型开发和功能探索，不建议在生产项目中依赖此插件

⚠️ **警告**：该插件为实验性功能，API 不稳定，可能在后续引擎版本中被移除或大幅修改。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/AnimationLayering)
- 官方文档：无
- 测试用例：未发现独立测试文件