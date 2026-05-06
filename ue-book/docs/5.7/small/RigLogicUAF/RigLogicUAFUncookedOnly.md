# RigLogic for UAF

> RigLogic for UAF

| 属性 | 值 |
|---|---|
| 中文名 | UAF 面部 RigLogic 插件 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RigLogicUAF` (Runtime), `RigLogicUAFUncookedOnly` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-26 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RigLogicUAF) | |

## 用途

RigLogic for UAF 是 Epic 的 **RigLogic**（面部动画及身体矫正系统）与 **UAF（Unified Animation Framework）** 的集成插件。它允许在 UAF 动画蓝图环境中直接使用 RigLogic 进行面部动画驱动，并自动处理身体矫正。通过提供一个专门的 UAF 动画节点（`RigLogic`），开发者可以像使用其他 UAF 行为节点一样，将 RigLogic 的面部/身体变形能力无缝融入基于行为树的动画流程中。

该插件解决的核心问题：原有 RigLogic 需要独立配置和调用，无法直接与 UAF 的图形化编排系统结合。此集成简化了面部动画在下一代动画框架（UAF）内的使用。

## 使用场景

- 你在使用 **UAF（统一动画框架）** 构建角色动画系统，并希望加入 RigLogic 的面部/身体变形。
- 你需要在高保真面部动画（嘴唇同步、表情）的同时，通过 RigLogic 驱动的身体矫正（correctives）提升肢体表现。
- 你的动画蓝图使用 **UAF 行为节点** 进行状态编排，希望将 RigLogic 作为一个独立的“行为”集成到流程中。

## 蓝图用法

> 注意：此插件提供的节点是 **UAF 动画图节点**，可在 UAF 动画蓝图编辑器（Animation Blueprint using UAF）中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RigLogic` | 执行面部动画并驱动身体矫正。输入：Input Pose；输出：覆盖的关节变换和曲线（驱动 blendshape/animated map） | `UUAFGraphNodeTemplate_RigLogic` |

### 使用示例（蓝图描述）

1. 在 UAF 动画蓝图中，右键打开节点菜单，选择 `UAF` → `RigLogic`。
2. 将 `Input` 引脚连接到上游动画结果（如默认的 Locomotion 节点或混合结果）。
3. 将 `Enabled` 引脚（布尔）连接到一个控制开关，例如通过条件变量决定是否启用面部动画。
4. 将节点的输出（`Out Pose`）连接到最终的动画输出或后续融合节点。

## C++ 用法

### 头文件引入

```cpp
#include "UAFGraphNodeTemplate_RigLogic.h"   // 节点模板定义
#include "RigLogicTrait.h"                   // 运行时 trait 数据（位于 RigLogicUAF 模块）
#include "Traits/PassthroughBlendTrait.h"    // 混合 trait
```

### 基本用法

在自定义 UAF 行为构建器或手动创建节点时使用：

```cpp
// 创建 RigLogic 节点的模板实例并添加到 UAF 图
UUAFGraphNodeTemplate_RigLogic* RigLogicNode = NewObject<UUAFGraphNodeTemplate_RigLogic>();
NodeLayout = RigLogicNode->NodeLayout; // 获取布局信息
```

更常见的用法是直接通过 UAF 节点编辑器静态创建，无需手动编码。

### 进阶用法

若需要在运行时通过代码操控 trait 数据，可修改 `FUAFRigLogicTraitSharedData` 和 `FPassthroughBlendTraitSharedData` 实例：

```cpp
// 假设你已经持有一个 UUAFGraphNodeTemplate_RigLogic 节点
const TArray<TInstancedStruct<FUAFBehaviorTraitSharedData>>& Traits = RigLogicNode->Traits;

for (const auto& Trait : Traits)
{
    if (FUAFRigLogicTraitSharedData* RigLogicTrait = Trait.GetPtr<FUAFRigLogicTraitSharedData>())
    {
        // 修改输入姿势引用等（示例，具体属性取决于 FUAFRigLogicTraitSharedData 定义）
        RigLogicTrait->Input = EAnimAlphaInputType::Pose;
    }
}
```

## Demo 示例

以下是一个完整的 .h + .cpp 文件，演示如何创建一个简单的 UAF 动画蓝图并动态注入 RigLogic 节点（最小示例，实际使用需 UAF 环境）。

### RigLogicTest.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "UAFGraphNodeTemplate_RigLogic.h"
#include "RigLogicTest.generated.h"

UCLASS()
class URigLogicTestHelper : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION()
    void SetupRigLogicNode();
};
```

### RigLogicTest.cpp

```cpp
#include "RigLogicTest.h"
#include "Animation/UAFAnimationBlueprint.h" // 假设的 UAF 蓝图类
#include "Behavior/UAFBehavior.h"            // 假设的行为基类

void URigLogicTestHelper::SetupRigLogicNode()
{
    // 获取或创建 UAF 动画蓝图 UObject
    UUAFAnimationBlueprint* AnimBlueprint = NewObject<UUAFAnimationBlueprint>(GetTransientPackage());

    // 创建 RigLogic 节点模板
    UUAFGraphNodeTemplate_RigLogic* RigLogicNode = NewObject<UUAFGraphNodeTemplate_RigLogic>();
    RigLogicNode->Title = FText::FromString(TEXT("CustomRigLogic"));
    RigLogicNode->Category = FText::FromString(TEXT("UAF"));

    // 将节点添加到蓝图的行为列表（伪代码）
    // AnimBlueprint->AddBehaviorNode(RigLogicNode->CreateRuntimeNode());
    
    // 注意：此示例仅为概念验证，实际 UAF 节点创建涉及复杂图结构。
    // 真实环境中应使用 UAF 提供的编辑 API。
}
```

> 完整的可用示例需配合 UAF 运行时模块（如 `UAF`, `UAFAnimGraph`）的 API，此处仅展示基本思路。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RigLogic` | 底层 RigLogic 运行时库 |
| `UAF` | 统一动画框架运行时模块 |
| `UAFAnimGraph` | UAF 动画图编辑器支持 |

其他依赖均为标准 UE 模块（Core, Engine, Slate 等），此处不赘述。

## 维护状态

### 近期更新

- 2025-08-26 d6217680 初始提交：将 RigLogicAnimNext 迁移为 RigLogicUAF，并添加节点模板

### 维护评价

该插件创建于 2025 年 8 月，距今仅约 2 个月，属于**全新实验性插件**。目前仅有初始提交，后续维护频率未知。由于标记为 `IsExperimentalVersion=true`，且默认不启用，表明该集成仍处于早期开发阶段，可能存在 API 不稳定、功能缺失或与 UAF 未来版本不兼容的风险。建议在充分测试后用于非生产项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RigLogicUAF)
- [RigLogic 官方文档](https://docs.unrealengine.com/5.7/en-US/rig-logic-for-facial-animation-in-unreal-engine/)（独立 RigLogic 插件）
- [UAF 概述](https://docs.unrealengine.com/5.7/en-US/unified-animation-framework-in-unreal-engine/)