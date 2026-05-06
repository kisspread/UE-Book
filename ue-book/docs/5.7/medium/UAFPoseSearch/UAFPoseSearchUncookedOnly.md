# UAF Pose Search

> Pose Search integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF姿势搜索 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFPoseSearch` (Runtime), `UAFPoseSearchUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-20 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFPoseSearch) | |

## 用途

本插件是 **UAF（Universal Animation Framework）** 对 Unreal Engine 原生 **PoseSearch** 系统的集成模块。它提供了一个动画蓝图图形节点 `Motion Matching`，允许用户在 UAF 框架内直接使用姿势搜索数据库（`UPoseSearchDatabase`）进行运动匹配。该节点内部组合了混合堆栈（BlendStack）、混合平滑（BlendSmoother）、历史轨迹收集（HistoryCollector）以及运动匹配特质（MotionMatchingTrait），使得开发者能够以拖拽和连接的方式快速搭建高质量的运动匹配动画流程，无需编写复杂 C++ 代码。

**解决问题**：传统动画蓝图难以高效实现实时数据库驱动的运动匹配；UAF 提供了统一的特质（Trait）系统，而本插件将 PoseSearch 数据库无缝嵌入该系统中，让动画师和程序员能在同一框架下工作。

## 使用场景

- 你正在使用 UAF 框架构建角色动画系统，需要加入由姿势搜索数据库驱动的运动匹配（例如角色根据行走速度、方向自动选择最匹配的跑步动画）。
- 你需要为角色添加自然、反应灵敏的过渡动画，且希望利用 UE5 的 PoseSearch 数据库进行离线预处理和实时查询。
- 在动画蓝图中，你希望将运动匹配节点与混合堆栈、历史轨迹等能力组合成一个独立的装配（Rig）模块。

## 蓝图用法

本模块主要提供的是**动画蓝图图形节点**（继承自 `UUAFGraphNodeTemplate`），属于编辑器时装配节点，并不直接暴露为蓝图可调用函数。但该节点可在 UAF 的动画图表中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Motion Matching` | 对指定姿势搜索数据库执行运动匹配，并收集局部历史轨迹，同时处理混合堆栈和混合平滑。 | `UUAFGraphNodeTemplate_MotionMatching` |

#### 节点使用示例（蓝图图形描述）

1. 在 UAF 动画图表中右键，从 `UAF` 分类中创建 `Motion Matching` 节点。
2. 将 `PoseSearchDatabase` 资产拖拽到节点上（节点接受拖放），或通过节点的 `Databases` 引脚连接一个数据库数组。
3. 连接 `Trajectory` 输入（来自历史收集器），提供当前角色轨迹。
4. 节点的输出引脚可用于后续动画混合或直接驱动最终姿势。

## C++ 用法

### 头文件引入

```cpp
#include "UAFGraphNodeTemplate_MotionMatching.h"
```

### 基本用法

以下示例展示了如何在自定义 UAF 图形模板中创建一个 `MotionMatching` 节点并设置其属性。该代码片段来自本插件模块的构造函数实现。

**来源文件**：`Engine/Plugins/Experimental/UAF/UAFPoseSearch/Source/UAFPoseSearchUncookedOnly/Private/UAFGraphNodeTemplate_MotionMatching.h`

```cpp
UUAFGraphNodeTemplate_MotionMatching::UUAFGraphNodeTemplate_MotionMatching()
{
    Title = LOCTEXT("MotionMatchingTitle", "Motion Matching");
    TooltipText = LOCTEXT("MotionMatchingTooltip", "Performs motion matching on a pose search database with local history collection");
    Category = LOCTEXT("MotionMatchingCategory", "UAF");

    // 使用 PoseSearch 数据库的图标颜色作为节点颜色
    Color = FLinearColor(FColor(29, 96, 125)); // From UE::PoseSearch::GetAssetColor();

    // 注册拖拽资产类型，允许直接将 UPoseSearchDatabase 拖放到节点上
    DragDropAssetTypes.Add(UPoseSearchDatabase::StaticClass());

    // 配置内部使用的特质（Traits），自动组合混合堆栈、平滑、运动匹配和历史收集
    Traits =
    {
        TInstancedStruct<FAnimNextBlendStackCoreTraitSharedData>::Make(),
        TInstancedStruct<FAnimNextBlendSmootherCoreTraitSharedData>::Make(),
        TInstancedStruct<FMotionMatchingTraitSharedData>::Make(),
        TInstancedStruct<FAnimNextHistoryCollectorTraitSharedData>::Make()
    };

    // 设置引脚布局：将 Databases 和 Trajectory 引脚放到默认分类下
    SetCategoryForPinsInLayout(
        {
            GET_PIN_PATH_STRING_CHECKED(FMotionMatchingTraitSharedData, Databases),
            GET_PIN_PATH_STRING_CHECKED(FAnimNextHistoryCollectorTraitSharedData, Trajectory),
        },
        FRigVMPinCategory::GetDefaultCategoryName(),
        NodeLayout,
        true);
}
```

### 进阶用法

在 UAF 框架中，开发者可以继承 `UUAFGraphNodeTemplate` 并自定义特质组合。例如，你可以创建一个派生节点，添加额外的混合层或修改姿态搜索数据库的查询参数（如 `FMotionMatchingTraitSharedData` 中的可编辑属性）。

以下是对 `FMotionMatchingTraitSharedData` 的假设扩展（实际属性需查看 UAF 相关头文件）：

```cpp
// 假设在 MotionMatchingTraitData.h 中
USTRUCT(BlueprintType)
struct FMotionMatchingTraitSharedData : public FAnimNextTraitSharedData
{
    GENERATED_BODY()

    // 关联的姿势搜索数据库数组（UAF 中可能使用 TArray<TObjectPtr<UPoseSearchDatabase>>）
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Motion Matching")
    TArray<TObjectPtr<UPoseSearchDatabase>> Databases;

    // 搜索参数：搜索半径
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Motion Matching")
    float SearchRadius = 100.0f;
};
```

你可以在 C++ 中直接创建该节点的实例，并在 UAF 图装配中编译执行。

## Demo 示例

> 注意：由于本插件属于编辑器模块，完整的最小示例需要配合 UAF 框架的图装配系统。以下提供一个简单的 UAF 图节点子类。

```cpp
// MyCustomMotionMatchNode.h
#pragma once

#include "UAFGraphNodeTemplate_MotionMatching.h"
#include "MyCustomMotionMatchNode.generated.h"

UCLASS()
class UMyCustomMotionMatchNode : public UUAFGraphNodeTemplate_MotionMatching
{
    GENERATED_BODY()

public:
    UMyCustomMotionMatchNode()
    {
        // 修改标题和说明
        Title = LOCTEXT("CustomMMTitle", "Custom MM");
        TooltipText = LOCTEXT("CustomMMTooltip", "A customized motion matching node with extended search");
        
        // 可以添加额外的特质或修改现有特质属性
        // 例如，强制使用更大的搜索半径
        // 需通过 Traits 数组修改 TInstancedStruct 内部数据
    }
};
```

```cpp
// MyCustomMotionMatchNode.cpp
#include "MyCustomMotionMatchNode.h"
```

注册到 UAF 的节点工厂即可在动画蓝图图表中使用。

## 模块依赖

> 以下依赖基于公共头文件推断，实际请以插件 `Build.cs` 为准。

| 模块 | 用途 |
|---|---|
| `UAF` | 提供 UUAFGraphNodeTemplate 基类和特质（Trait）系统 |
| `PoseSearch` | 提供姿势搜索数据库和核心算法 |
| `AnimGraph` | 提供用于动画蓝图图形的基础设施 |
| `AnimGraphRuntime` | 提供动画蓝图运行时节点支持 |
| `AnimNext`（UAF 内部） | 提供混合堆栈、平滑、历史收集等特质数据定义 |

> **常见依赖省略**：Core, CoreUObject, Engine, Slate, SlateCore, UMG, InputCore, UnrealEd, PropertyEditor 等未列出。

## 维护状态

### 近期更新

- 2025-10-03 `ff6147e` — Updated UAF Trajectory functions to have an execution pin.
- 2025-10-03 `61a8ba0` — Added UAF GenerateTrajectory version for CharacterMovementComponent.
- 2025-10-01 `604a771` — PoseSearch - fix for MM trait timeline and MM node interaction blendstack synchronizations
- 2025-09-04 `d443289` — PoseSearch
- 2025-08-20 `6cd8938` — PoseSearch - making FPoseSearchColumn::InterruptMode pinnable

### 维护评价

该插件非常年轻（2025年8月创建），更新频率高（几乎每周都有提交），且涉及功能修复和新增接口（轨迹执行引脚、生成轨迹函数）。当前处于积极开发阶段，但标记为实验性，API 可能发生变动。建议在原型阶段使用，紧跟前瞻版本更新。

**综合评价**：活跃维护，适合实验和前沿项目，但需注意稳定性风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFPoseSearch)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/pose-search-in-unreal-engine/)（PoseSearch 通用文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFPoseSearch/Tests)（如存在；本插件 UnrealEngine 主仓库中测试用例路径未知）