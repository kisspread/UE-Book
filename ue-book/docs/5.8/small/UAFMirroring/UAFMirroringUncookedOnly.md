# UAF Mirroring

> Keyframe mirroring for UAF

| 属性 | 值 |
|---|---|
| 中文名 | UAF 镜像工具 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFMirroring` (Runtime), `UAFMirroringUncookedOnly` (Runtime), `UAFMirroringTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-18 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMirroring) | |

## 用途

此插件是 UAF (Unified Animation Framework) 的扩展模块，专门用于实现动画关键帧的镜像功能。它解决了在 UAF 动画系统中高效、准确地创建镜像动画片段（如左右对称的行走、跑步循环）的问题。通过提供镜像特性（Trait）、辅助方法和蓝图图节点，该插件让动画师和开发者能够以数据驱动的方式（通过数据表）快速定义和应用镜像规则，从而避免手动逐帧调整对称动画，极大地提高了动画资产制作的效率。

## 使用场景

- **动画资产快速创建**：你正在使用 UAF 制作一个需要大量左右对称动画（如行走、攻击、受击）的游戏角色。使用此插件可以将一个方向的动画片段（如“向左行走”）通过镜像数据表，快速生成其对应的镜像片段（“向右行走”），无需手动调整。
- **程序化动画修正**：在程序化动画或动画蓝图中，需要实时或根据状态翻转角色的某些动画表现。通过 `MirrorPose` 函数和预设的镜像数据表，可以在运行时动态调整动画输出。

## 蓝图用法

该插件主要提供了一个 UAF 图节点模板，用于在蓝图或 UAF 图编辑器中进行可视化操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Mirror` | 一个 UAF 图节点模板，使用指定的镜像数据表来镜像输入姿态。 | `UUAFGraphNodeTemplate_Mirror` |

### 使用示例（蓝图描述）

1.  在 UAF 图编辑器或支持 UAF 的蓝图编辑器中，右键搜索并添加 **“Mirror”** 节点。
2.  从资产浏览器中，将一个 `UMirrorDataTable` 资产**拖放**到该节点上，节点会自动配置并更新标题为“Mirror using [数据表名称]”。
3.  将该节点的输入引脚连接到需要被镜像的动画姿态源。
4.  将该节点的输出引脚连接到后续的动画处理节点或最终输出。

## C++ 用法

### 头文件引入

```cpp
#include "Traits/MirroringTrait.h"
```

### 基本用法

以下示例展示了如何在 C++ 中使用镜像特性数据，以及如何调用辅助函数来镜像一个动画姿态。

```cpp
#include "Traits/MirroringTrait.h"
#include "Animation/MirrorDataTable.h"

// 假设你有一个有效的 FMirroringTraitData 和动画片段
void MirrorAnimationSample(UE::UAF::FMirroringTraitData& TraitData, const FAnimSequence& SourceAnim)
{
    // 1. (可选) 通过代码或蓝图设置镜像数据表
    UMirrorDataTable* MirrorTable = LoadObject<UMirrorDataTable>(nullptr, TEXT("/Game/Data/DT_CharacterMirror"));
    TraitData.Setup.MirrorDataTable = MirrorTable;

    // 2. 使用 TraitData 中的逻辑来镜像动画数据
    // 通常在 Trait 的 Apply 或 Evaluate 方法内部调用辅助函数
    // 例如，Trait 内部可能会调用：
    // UE::UAF::Mirroring::MirrorPose(PoseToMirror, TraitData.CachedMirrorData, MirrorMode);
}
```

### 进阶用法

该插件的核心逻辑封装在 `UAFMirroring` 模块中。在实现自定义的 UAF 特性（Trait）时，可以继承或组合其提供的基类，以实现自定义的镜像逻辑。更复杂的用法通常涉及：
1.  创建自定义的镜像数据表（`UMirrorDataTable`），定义骨骼名称、曲线名称和元数据的映射关系。
2.  在 UAF 特性图中使用提供的 `Mirror` 模板节点。
3.  在 C++ 中直接操作 `FMirroringTraitSetupParams` 和 `FMirroringTraitApplyParams` 来精细化控制镜像过程。

## Demo 示例

以下是一个最小示例，演示如何在 C++ 中创建一个使用镜像特性（Trait）的 UAF 评估器。

**MyMirrorEvaluator.h**
```cpp
#pragma once
#include "UAFEvaluator.h"
#include "Traits/MirroringTrait.h" // 包含镜像特性头文件

UCLASS()
class UMyMirrorEvaluator : public UUAFEvaluator
{
    GENERATED_BODY()

public:
    virtual void Initialize(const FAnimationUpdateContext& Context) override;

private:
    // 包含一个镜像特性数据实例
    UE::UAF::FMirroringTraitData MirrorTraitData;
};
```

**MyMirrorEvaluator.cpp**
```cpp
#include "MyMirrorEvaluator.h"
#include "Animation/MirrorDataTable.h"

void UMyMirrorEvaluator::Initialize(const FAnimationUpdateContext& Context)
{
    Super::Initialize(Context);

    // 加载或获取镜像数据表
    UMirrorDataTable* MyMirrorTable = LoadObject<UMirrorDataTable>(nullptr, TEXT("/Game/Data/DT_PlayerMirror"));
    if (MyMirrorTable)
    {
        // 配置特性数据
        MirrorTraitData.Setup.MirrorDataTable = MyMirrorTable;

        // 在此处，你会将 MirrorTraitData 添加到你的特性列表或直接用于评估。
        // 具体的添加方式取决于你的 UAF 评估器设计和 Trait 执行管线。
        // AddTrait(MakeShared<UE::UAF::FMirroringTrait>(MirrorTraitData));
    }
}
```

## 模块依赖

此插件依赖于其他 UAF 相关插件，且在插件的 `.uplugin` 文件中声明了依赖。

| 插件/模块 | 用途 |
|---|---|
| `UAF` | 核心 UAF 框架，提供基础类型、评估器和特性系统。 |
| `UAFAnimGraph` | UAF 的动画图编辑器集成，提供图节点模板等功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF。 |
| 2026-03-10 | `24473b8e` | Fix direct reads of latent SharedData properties in UAF traits | 修复 UAF 特性中延迟读取 SharedData 属性的直接访问问题。 |
| 2026-02-17 | `baf983b4` | [SubmitTool - UAF] Add validators to build and run LowLevelTests for UAF plugins | 为 UAF 插件添加构建验证器并运行底层测试。 |
| 2026-01-23 | `81bd488d` | UAF fix some incorrect comparison of invalid bone indicies, where 16bit was upcast to 32bit and comp | 修复 UAF 中无效骨骼索引的比较错误，涉及 16 位到 32 位的上行转换和比较。 |
| 2026-01-23 | `9735f798` | UAF: Fix rename/move issues | 修复 UAF 中的重命名和移动问题。 |

### 维护评价

- **创建时间**：2025 年 8 月，作为 UAF 的实验性扩展，历史约 1 年。
- **更新频率**：自创建以来，最近一次更新在 2026 年 4 月，期间有多次维护性更新。
- **维护内容**：近期的提交主要是**修复bug**（如骨骼索引比较、属性访问）和**基础设施改进**（日志迁移、测试验证），尚未看到重大的新功能添加。
- **稳定性**：插件本身标记为 `IsExperimentalVersion=true`，并且其依赖的 `UAF` 和 `UAFAnimGraph` 也处于实验阶段。这意味着 API 和功能可能会发生不兼容的更改。
- **推荐度**：**适合早期评估和内部实验**。不建议在需要长期稳定维护的生产项目中使用。如果你的项目已经深度集成了实验性 UAF 框架，并且有迫切的镜像动画需求，可以谨慎使用，并做好应对未来 API 变更的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMirroring)
- [官方文档](https://epicgames.com) （暂无专属文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFMirroring/Tests)