# IK Rig

> （.uplugin 中未提供描述，基于源码分析）为动画蓝图提供一套基于 IK 的、数据驱动的动画重定向与求解系统，支持从源骨骼向不同比例的目标骨骼重定向动画。

| 属性 | 值 |
|---|---|
| 中文名 | IK 重定向器 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、数据资产） |
| 模块 | `IKRig` (Runtime), `IKRigDeveloper` (Runtime), `IKRigEditor` (Runtime), `IKRigUAF` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-11-25 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/IKRig) | |

## 用途

IKRig 插件的核心目的是**解决动画重定向（Animation Retargeting）问题**，特别是处理角色骨骼比例差异（如人形角色间的体型差异）带来的动画适配问题。它提供了一套数据驱动的求解器系统，允许美术师通过编辑器可视化地定义源与目标骨架之间的对应关系（IK Rig）以及重定向规则（IK Retargeter），然后在运行时高效地执行重定向计算。与传统的基于名称的重定向不同，IKRig 利用 IK 求解来更精确地匹配肢体末端位置，从而获得更自然的结果。

该插件是 UE5 动画系统的重要组成部分，特别是与 **ControlRig** 和新的动画图系统（如 AnimNext、UAF - Unified Animation Framework）深度集成，允许在复杂的动画逻辑中嵌入 IK 重定向步骤。

## 使用场景

- **你正在开发一个角色扮演游戏（RPG）或动作游戏，需要将一套动作捕捉或预制动画应用到玩家自定义的不同体型角色上** → 使用 IKRig 创建目标角色的 IK Rig 定义，并配置 IK Retargeter 资产来驱动动画重定向。
- **你的游戏支持角色捏脸/换装系统，不同角色的骨架比例可能有显著差异** → 使用 IKRig 确保所有角色都能共享同一套动画资源库，且肢体末端（如手、脚）位置正确。
- **你需要在动画蓝图或动画图中，将动画数据从一个骨架（例如，一个高精度的动作捕捉骨骼）实时重定向到另一个更简化的游戏运行时骨架** → 使用 `FRigUnit_UAFIKRetargeter` 节点。
- **你想为程序化生成或实验性的动画系统（如 AnimNext）添加 IK 重定向能力** → 将 IKRig 的求解器集成到新的动画图节点中。

## 蓝图用法

### 核心资产

在编辑器中，主要通过创建和配置以下数据资产来工作：

| 资产类型 | 说明 |
|---|---|
| **IK Rig** (`UIKRigDefinition`) | 定义单个骨架的 IK 拓扑结构。你可以选择骨骼作为根节点、设置 IK 链、定义求解器（如 FABRIK, CCD, Full Body IK 等）。它是重定向的“蓝图”。 |
| **IK Retargeter** (`UIKRetargeter`) | 定义从源 IK Rig 到目标 IK Rig 的映射和求解设置。你可以设置重定向的根骨骼、链对应关系、调整全局和每个链的缩放/旋转/平移偏移，以及预览和烘焙结果。 |

### 核心节点（在动画图/UAF中）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IK Retargeter` | 在 AnimNext 或 UAF 动画图中执行 IK 重定向的核心节点。接受源姿态、目标参考姿态和 IK Retargeter 资产，输出重定向后的目标姿态。 | `FRigUnit_UAFIKRetargeter` |

### 使用示例（蓝图描述）

1.  **创建资产**：
    - 在内容浏览器右键 -> `Animation` -> `IK Rig`，为你的源骨架和目标骨架分别创建 `UIKRigDefinition` 资产。
    - 在 `UIKRigDefinition` 编辑器中，为角色的每条肢体（如左右腿、左右臂）创建 IK 链，并选择合适的求解器（通常是 FABRIK 或 CCD）。
2.  **配置重定向**：
    - 右键创建 `Animation` -> `IK Retargeter` 资产。
    - 在 `UIKRetargeter` 编辑器中，选择源 `IKRig` 和目标 `IKRig`。
    - 在“重定向根”面板中，设置根骨骼对应关系（如将源骨架的 `pelvis` 映射到目标骨架的 `pelvis`）。
    - 在“链映射”面板中，将源骨架的 IK 链（如 `LeftLeg`）与目标骨架的对应链进行匹配。可以调整偏移量来修正体型差异。
    - 在预览面板中，选择源动画，查看目标骨架的重定向效果，并实时调整参数。
3.  **运行时使用**：
    - 在 **动画蓝图** 中，你可以使用 `Retarget Pose From Mesh` 节点，指定源动画组件和 `IKRetargeter` 资产来执行重定向。
    - 在更先进的 **AnimNext 动画图** 中，你可以使用 `IK Retargeter` 节点（见上表），将源姿态和 `IKRetargeter` 资产作为输入，输出重定向后的姿态。

## C++ 用法

IKRig 的 C++ API 主要用于创建自定义求解器、扩展编辑器功能或在底层动画系统中集成重定向逻辑。普通项目通常通过蓝图和编辑器资产来使用它。

### 头文件引入

```cpp
#include "IKRig/IKRigDefinition.h"
#include "IKRetargeter/IKRetargeter.h"
```

### 基本用法（程序化创建/操作资产）

虽然通常通过编辑器创建资产，但你也可以在 C++ 中程序化地操作它们。以下是一个概念性示例，展示如何获取和使用一个已有的 `IKRetargeter` 资产。

```cpp
// 假设你已经通过资产路径加载了一个 IKRetargeter 资产
UIKRetargeter* RetargeterAsset = LoadObject<UIKRetargeter>(nullptr, TEXT("/Game/Animation/MyRetargeter"));

if (RetargeterAsset)
{
    // 获取其源 IK Rig 和目标 IK Rig
    UIKRigDefinition* SourceRig = RetargeterAsset->GetSourceIKRig();
    UIKRigDefinition* TargetRig = RetargeterAsset->GetTargetIKRig();
    
    // 在动画节点或处理器中，使用该资产配置 FIKRetargetProcessor
    // 具体集成方式取决于你的动画管线（是标准AnimBP还是自定义节点）
}
```

### 进阶用法（在自定义动画节点中集成）

参考 `FRigUnit_UAFIKRetargeter` 的实现，你可以在自己的自定义 `FRigUnit` 或动画节点中集成重定向功能。核心是创建并维护一个 `FIKRetargetProcessor` 实例。

```cpp
// 在你的自定义动画节点或Rig Unit的Execute函数中
#include "Retargeter/IKRetargetProcessor.h"

class FMyAnimationNode : public FAnimNode_Base
{
    // ... 省略其他成员 ...
    FIKRetargetProcessor RetargetProcessor;
    
    virtual void Initialize_AnyThread(const FAnimationInitializeContext& Context) override
    {
        // 用资产数据初始化处理器
        if (MyRetargeterAsset)
        {
            RetargetProcessor.Initialize(MyRetargeterAsset);
        }
    }
    
    virtual void Evaluate_AnyThread(FPoseContext& Output) override
    {
        // 1. 获取源姿态（可能是从另一个动画组件或节点来的）
        TArray<FTransform> SourcePose = ...; 

        // 2. 设置处理器输入
        RetargetProcessor.SetSourceMeshPose(SourcePose);

        // 3. 运行重定向
        RetargetProcessor.Run();

        // 4. 获取结果姿态并输出
        const TArray<FTransform>& TargetPose = RetargetProcessor.GetTargetMeshPose();
        // 将TargetPose转换为FPoseContext输出...
    }
};
```

**注意**：以上是高级用法示例。`FIKRetargetProcessor` 的 API 可能更复杂，需要处理姿态格式转换、LOD 适配等。建议仔细阅读 `IKRigUAF` 模块中 `FRigUnit_UAFIKRetargeter` 的源码作为参考。

## Demo 示例

由于这是一个大型的、面向工作流的插件，其核心价值在于编辑器工具链和资产。一个“最小可编译示例”无法体现其真正用法。最佳示例是：

1.  创建一个简单的第三人称模板项目。
2.  为 Manny 和 Quinn 骨架分别创建 `IK Rig` 资产。
3.  创建一个 `IK Retargeter` 资产，将 Manny 的动画重定向到 Quinn 上。
4.  在 Quinn 的动画蓝图中使用 `Retarget Pose From Mesh` 节点来驱动 Quinn 播放 Manny 的动画。

具体的蓝图连接和参数调整过程是学习本插件的关键。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ControlRig` | IKRig 的求解器系统基于 ControlRig 框架构建，并与之深度集成。 |
| `FullBodyIK` | 提供全身上下的 IK 求解器算法，是 IKRig 支持的核心求解器之一。 |
| `RigVM` | 底层的 Rig 虚拟机，用于执行控制逻辑和 IK 计算图。 |
| `SkeletalMeshDescription` | 用于在编辑器中与骨骼网格体数据交互。 |

**省略常见依赖**：Core, CoreUObject, Engine, Slate, SlateCore, UMG, InputCore, UnrealEd, EditorStyle, PropertyEditor, Projects, DeveloperSettings

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `d96c8edf` | Fix root motion trajectory visualization in IK Retarget editor | 修复 IK 重定向编辑器中根运动轨迹的可视化问题。 |
| 2026-05-12 | `b9da6b61` | [IK Retargeter] Fix curve-bound override values having no effect on exported batch retarget animation | 修复曲线绑定的重定向覆盖值在批量导出动画时无效的问题。 |
| 2026-05-12 | `553f4a7e` | [IK Retargeter] Fix pre-5.6 RTG assets having all ops enabled in 5.8: narrow PostLoad version guard | 修复从旧版本迁移的资产在 5.8 中意外启用所有操作的问题，通过更新版本检查逻辑解决。 |
| 2026-05-12 | `0171c6fd` | [IK Retargeter] Fix null deref crashes in GenerateAssetLists: guard GC'd weak ptrs, uncompiled bluep | 修复在生成资产列表时空指针崩溃的问题，加强了对弱指针和未编译蓝图的检查。 |
| 2026-05-12 | `f8c7fc88` | [IK Retargeter] Fix active-by-default Override Sets not applied when exporting animations through th | 修复默认激活的覆盖集在通过动画编辑器导出动画时未被应用的问题。 |

### 维护评价

- **活跃维护**：插件在 2026 年 5 月仍有密集的 bug 修复和功能完善提交，表明 Epic 仍在积极维护。
- **核心功能**：作为 UE5 动画重定向的核心解决方案，其稳定性至关重要。
- **已知问题**：从近期提交来看，主要修复了编辑器工作流、批量处理和版本迁移中的边界情况问题。
- **推荐使用**：**强烈推荐**。这是 Epic 官方提供的、功能强大且持续维护的动画重定向方案。对于需要跨骨架共享动画的项目，它是标准且推荐的工作流。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/IKRig)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/ik-rig-in-unreal-engine/) (UE5 文档中有相关章节)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/IKRig/Source/IKRig) (插件源码内含测试)