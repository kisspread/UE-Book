# IK Rig

> （照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 逆向运动绑定 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、数据资产、图表资产） |
| 模块 | `IKRig` (Runtime), `IKRigDeveloper` (Runtime), `IKRigEditor` (Runtime), `IKRigUAF` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-11-25 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/IKRig) | |

## 用途
IKRig 是 UE5 中用于定义、构建和求解逆向运动学 (IK) 链条的核心动画系统。它解决的主要问题是将复杂、可定制的 IK 解算器集成到动画蓝图中，用于动画重定向 (Retargeting) 和角色姿势控制。它超越了简单的 Two Bone IK，允许你在一个数据资产 (`UIKRigDefinition`) 中配置完整的骨架映射、IK 链条、目标和约束，并生成一个可在动画蓝图中使用的 AnimGraph 节点 (`AnimNode_IKRig`)。这使得为不同骨架的角色创建共享的、可移植的 IK 逻辑变得高效，是 UE5 高级动画管线的关键组件。

## 使用场景
- **动画重定向**：将一个角色的动画资产转换到另一个骨骼比例或拓扑结构完全不同的角色上使用。
- **角色动画 IK 解算**：例如，为攀爬、游泳或与环境交互的角色手/脚添加 IK，确保肢体始终正确贴地或抓住物体。
- **程序化动画 (Procedural Animation)**：在运行时根据游戏逻辑（如地形坡度、武器后坐力）动态调整角色的根骨骼或肢体位置。
- **混合 IK 与 FK**：在动画蓝图中混合基于物理的动画、手动动画和 IK 解算的结果。

## 蓝图用法
IKRig 的主要蓝图使用方式是在动画蓝图的 AnimGraph 中使用 `IK Rig` 节点。详细的 API 请参阅各子模块文档。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IK Rig` (AnimGraph Node) | 在动画图表中求解指定 `UIKRigDefinition` 中定义的 IK 设置。 | `UAnimGraphNode_IKRig` |
| `Set IK Rig Definition` | 在运行时设置 `AnimNode_IKRig` 节点使用的 `UIKRigDefinition` 数据资产。 | `UAnimInstance` |
| `Set IK Rig Goal Transform` | 在运行时设置特定 IK 目标（如“左手”）的世界空间变换。 | `UAnimInstance` |

### 使用示例（蓝图描述）
1.  创建一个 `UIKRigDefinition` 资产，在其中定义源和目标骨架，并设置 IK 链条。
2.  在动画蓝图的 AnimGraph 中，添加一个 `IK Rig` 节点，并将其连接到动画状态机的输出。
3.  在节点的细节面板中，指定上一步创建的 `UIKRigDefinition` 资产。
4.  （可选）通过暴露的 Pin 或在 `Event Blueprint Update Animation` 中使用 `Set IK Rig Goal Transform` 等函数，动态控制目标位置。

## C++ 用法
C++ 使用侧重于引擎内部扩展和底层数据操作。

### 头文件引入
```cpp
#include "IKRigDefinition.h"
#include "AnimNode_IKRig.h"
```

### 基本用法
获取和配置 IKRig 数据资产。
```cpp
// 从内容浏览器加载一个已有的 IKRigDefinition 资产
UIKRigDefinition* IKRigDef = LoadObject<UIKRigDefinition>(nullptr, TEXT("/Game/Animation/MyCharacterIKRig"));

// 获取其根骨骼设置
if (IKRigDef && IKRigDef->GetRootBone())
{
    const FName RootBoneName = IKRigDef->GetRootBone()->BoneName;
    // ...
}
```
*来源参考: `Engine/Plugins/Animation/IKRig/Source/IKRig/Private/Retargeter/IKRetargeter.cpp`*

## Demo 示例
一个最小化的动画蓝图设置，用于在运行时应用 IKRig。
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
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IK")
    UIKRigDefinition* CharacterIKRig;

    UPROPERTY(BlueprintReadWrite, Category = "IK")
    FTransform LeftHandGoalTransform;
};
```
*在 AnimGraph 中放置 `IK Rig` 节点，并将其 `Definition` 属性绑定到 `CharacterIKRig` 变量。*

## 模块依赖
你的模块需要依赖以下模块才能使用 IKRig：
| 模块 | 用途 |
|---|---|
| `IKRig` | 核心运行时模块，包含数据资产、解算器和 AnimNode。 |
| `AnimationCore` | 提供动画核心数学和基础类型。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `d96c8edf` | Fix root motion trajectory visualization in IK Retarget editor | 修复了 IK 重定向编辑器中根运动轨迹的可视化问题。 |
| 2026-05-12 | `b9da6b61` | [IK Retargeter] Fix curve-bound override values having no effect on exported batch retarget animation | 修复了 IK 重定向器中曲线覆盖值对批量导出的重定向动画无效的问题。 |
| 2026-05-12 | `553f4a7e` | [IK Retargeter] Fix pre-5.6 RTG assets having all ops enabled in 5.8: narrow PostLoad version guard | 修复了 5.6 之前的重定向器资产在 5.8 中所有操作默认启用的兼容性问题。 |
| 2026-05-12 | `0171c6fd` | [IK Retargeter] Fix null deref crashes in GenerateAssetLists: guard GC'd weak ptrs, uncompiled bluep | 修复了生成资产列表时空指针崩溃的问题。 |
| 2026-05-12 | `f8c7fc88` | [IK Retargeter] Fix active-by-default Override Sets not applied when exporting animations through th | 修复了通过导出管线导出动画时，默认激活的覆盖集未被应用的问题。 |

### 维护评价
IKRig 是 UE5 动画系统的**核心且活跃维护**的组件。从近期提交记录看，主要围绕其**动画重定向 (Retargeting)** 子系统 `IKRetargeter` 进行密集的 bug 修复和优化，表明该功能仍在持续完善和打磨。插件创建于 2020 年，已有近 6 年历史，但依然得到 Epic Games 的高频更新，无废弃迹象。它为高级角色动画提供了强大而灵活的工具链，**强烈推荐**在中大型项目中使用。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/IKRig)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/IKRig/Tests)