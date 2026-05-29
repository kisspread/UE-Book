# UAF Anim Graph

> Framework for defining animation graphs.

| 属性 | 值 |
|---|---|
| 中文名 | 动画图框架 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画图资产、蓝图节点模板、编辑器工具） |
| 模块 | `UAFAnimGraph` (Runtime), `UAFAnimGraphEditor` (Editor), `UAFAnimGraphUncookedOnly` (UncookedOnly), `UAFAnimGraphTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-26 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFAnimGraph) | |

## 用途

UAFAnimGraph 是一个基于 **RigVM** 构建的动画图定义框架，用于在 UE5 中以节点图的方式创建和编辑动画逻辑。它从 Epic 内部的 **AnimNext** 项目演变而来（原名 AnimNextAnimGraph），是 UAF（Unified Animation Framework）动画系统的核心组件之一。

该插件解决的核心问题是：**如何为动画状态机和动画混合逻辑提供一套可视化、可扩展的图编辑框架**。与传统 AnimGraph 不同，UAFAnimGraph 基于 RigVM 虚拟机，支持：

- **Trait 系统**：每个动画图节点本质上是一个 Trait Stack（特性栈），可以叠加多个 Trait（如序列播放器、混合空间播放器、混合器等）来组合动画行为
- **节点模板机制**：通过 `UUAFGraphNodeTemplate` 定义节点的外观、行为和交互逻辑（拖放资产、变量绑定等）
- **图嵌套与注入**：支持 Inline SubGraph（内联子图）和 Injection Site（注入点），实现动画图的模块化组合
- **与 AnimBlueprint 集成**：通过 `UAnimGraphNode_AnimNextGraph` 将 UAF 动画图嵌入传统 AnimBlueprint 工作流

## 使用场景

- 你在开发复杂的角色动画系统，需要可视化编辑动画混合逻辑 → 用 UAFAnimGraph 构建动画图
- 你需要将动画图作为可复用资产，支持在多个角色间共享 → 用 UAFAnimGraph 创建独立的动画图资产
- 你想使用 Trait 系统（序列播放器、混合空间、混合器等）组合动画行为 → 通过模板节点在动画图中搭建
- 你需要在运行时动态注入外部动画逻辑 → 使用 Injection Site 节点和蓝图注入回调
- 你的团队需要比传统 AnimGraph 更灵活的动画编辑工具 → UAFAnimGraph 基于 RigVM 提供更强大的图编辑能力

## 蓝图用法

> ⚠️ 此插件标记为实验性（IsExperimentalVersion=true），且默认未启用（EnabledByDefault=false）。使用前需手动在项目设置中启用。

### 核心节点

#### 动画图资产操作（UAnimNextAnimationGraphLibrary）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddAnimationGraph` | 向 UAF 动画图资产中添加新的动画图入口 | `UAnimNextAnimationGraphLibrary` |

#### 控制器操作（UAnimNextController）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddTraitStruct` | 向 Trait Stack 节点添加一个新 Trait（使用结构体实例） | `UAnimNextController` |
| `AddTraitByName` | 通过 Trait 类型名称向节点添加 Trait | `UAnimNextController` |
| `RemoveTraitByName` | 通过 Trait 实例名称从节点移除 Trait | `UAnimNextController` |
| `SwapTraitByName` | 用新 Trait 替换现有 Trait | `UAnimNextController` |
| `SetTraitPinIndex` | 移动 Trait 在栈中的位置（改变执行顺序） | `UAnimNextController` |

#### 注入回调（蓝图异步节点）

| 节点 | 说明 | 所在类 |
|---|---|---|
| AnimNext Injection | 异步注入动画逻辑到动画图的注入点 | `UK2Node_AnimNextInjection` |
| Injection Set Variable | 在注入回调中设置变量 | `UK2Node_InjectionCallbackProxySetVariable` |
| AnimNext Play Anim | 蓝图中播放 UAF 动画 | `UK2Node_AnimNextPlayAnim` |

### 使用示例（蓝图描述）

**在蓝图中播放 UAF 动画图：**
1. 在角色蓝图中添加 AnimNext 组件
2. 使用 `Play Anim` 异步节点指定要播放的 UAF 动画图资产
3. 通过 Completed 输出引脚监听播放完成事件

**通过蓝图向动画图注入逻辑：**
1. 在动画图编辑器中放置 Injection Site 节点
2. 在蓝图中使用 `AnimNext Injection` 异步节点连接到对应的注入点
3. 通过 `Set Variable` 节点动态修改注入逻辑中的变量值

## C++ 用法

### 头文件引入

```cpp
// 核心模块
#include "UAFAnimGraph.h"

// 编辑器数据（仅编辑器/UncookedOnly）
#include "Graph/AnimNextAnimationGraph_EditorData.h"

// 控制器扩展
#include "AnimNextController.h"

// 节点模板
#include "Templates/UAFGraphNodeTemplate.h"

// 动画图入口
#include "Entries/AnimNextAnimationGraphEntry.h"
```

### 基本用法

**创建动画图入口并设置简单动画图：**

```cpp
// 来源: Internal/Graph/AnimGraphUncookedOnlyUtils.h
// 需要引用模块: UAFAnimGraphUncookedOnly

#include "AnimGraphUncookedOnlyUtils.h"
#include "Graph/AnimNextAnimationGraph_EditorData.h"

// 获取动画图资产的编辑器数据
UUAFAnimGraph_EditorData* EditorData = /* ... */;

// 使用控制器添加动画图入口
UAnimNextAnimationGraphEntry* Entry = UAnimNextAnimationGraphLibrary::AddAnimationGraph(
    InAsset, 
    TEXT("DefaultGraph"), 
    true,  // bSetupUndoRedo
    false  // bPrintPythonCommand
);

// 使用工具函数快速设置一个基础动画图
UE::UAF::UncookedOnly::FAnimGraphUtils::SetupAnimGraph(
    Entry->GetEntryName(),
    Controller,
    true   // bSetupUndoRedo
);
```

*来源: `Internal/Graph/AnimGraphUncookedOnlyUtils.h`, `Internal/Graph/AnimNextAnimationGraph_EditorData.h`*

### 进阶用法

**通过控制器操作 Trait Stack：**

```cpp
#include "AnimNextController.h"

// 获取控制器
UAnimNextController* Controller = /* ... */;

// 向 Trait Stack 添加一个序列播放器 Trait
FName TraitInstanceName = Controller->AddTraitByName(
    TEXT("MyTraitStackNode"),      // 节点名称
    TEXT("SequencePlayerTrait"),   // Trait 类型名
    0,                              // Pin 索引
    TEXT(""),                       // 默认值
    true,                           // bSetupUndoRedo
    false                           // bPrintPythonCommand
);

// 更换 Trait 类型
FName NewTraitInstanceName = Controller->SwapTraitByName(
    TEXT("MyTraitStackNode"),
    TraitInstanceName,
    0,
    TEXT("BlendSpacePlayerTrait")
);

// 调整 Trait 执行顺序
Controller->SetTraitPinIndex(
    TEXT("MyTraitStackNode"),
    NewTraitInstanceName,
    1  // 移动到索引 1
);

// 移除 Trait
Controller->RemoveTraitByName(
    TEXT("MyTraitStackNode"),
    NewTraitInstanceName
);
```

*来源: `Internal/AnimNextController.h`*

**自定义节点模板（创建新的动画图节点类型）：**

```cpp
#include "Templates/UAFGraphNodeTemplate.h"

UCLASS()
class UMyGraphNodeTemplate_CustomBlend : public UUAFGraphNodeTemplate
{
    GENERATED_BODY()

    UMyGraphNodeTemplate_CustomBlend()
    {
        Title = LOCTEXT("CustomBlendTitle", "Custom Blend");
        TooltipText = LOCTEXT("CustomBlendTooltip", "Custom blend node");
        Category = LOCTEXT("CustomBlendCategory", "UAF");
        MenuDescription = LOCTEXT("CustomBlendMenuDesc", "Custom Blend");
        Color = UE::UAF::UncookedOnly::FGraphNodeColors::Blends;
        
        // 定义此节点使用的 Trait
        Traits =
        {
            TInstancedStruct<FMyCustomBlendTraitSharedData>::Make(),
            TInstancedStruct<FAnimNextBlendSmootherTraitSharedData>::Make()
        };
        
        // 配置引脚布局
        SetCategoryForPinsInLayout(
            {
                GET_PIN_PATH_STRING_CHECKED(FMyCustomBlendTraitSharedData, InputA),
                GET_PIN_PATH_STRING_CHECKED(FMyCustomBlendTraitSharedData, InputB),
                GET_PIN_PATH_STRING_CHECKED(FMyCustomBlendTraitSharedData, Alpha),
            },
            FRigVMPinCategory::GetDefaultCategoryName(),
            NodeLayout,
            true);
    }

    virtual void HandleAssetDropped_Implementation(
        UAnimNextController* Controller, 
        URigVMUnitNode* Node, 
        UObject* Asset) const override
    {
        Super::HandleAssetDropped_Implementation(Controller, Node, Asset);
        // 自定义拖放资产处理逻辑
    }
};
```

*来源: `Private/Templates/UAFGraphNodeTemplate_BlendByBool.h`, `Public/Templates/UAFGraphNodeTemplate.h`*

## Demo 示例

**创建一个带有序列播放器节点的最小动画图：**

```cpp
// MyAnimGraphBuilder.h
#pragma once

#include "CoreMinimal.h"
#include "AnimNextController.h"
#include "Entries/AnimNextAnimationGraphEntry.h"

class FMyAnimGraphBuilder
{
public:
    /** 创建一个包含序列播放器节点的动画图 */
    static UAnimNextAnimationGraphEntry* BuildSimpleAnimGraph(UUAFAnimGraph* InAsset)
    {
        // 1. 添加动画图入口
        UAnimNextAnimationGraphEntry* Entry = UAnimNextAnimationGraphLibrary::AddAnimationGraph(
            InAsset, TEXT("SimpleGraph"), true, false);
        
        if (!Entry)
        {
            return nullptr;
        }
        
        // 2. 通过 UncookedOnly 工具函数设置基础图结构
        UE::UAF::UncookedOnly::FAnimGraphUtils::SetupAnimGraph(
            Entry->GetEntryName(), InAsset->GetEditorData()->GetController());
        
        return Entry;
    }
    
    /** 检查节点是否为 Trait Stack */
    static bool IsTraitStack(const URigVMNode* Node)
    {
        return UE::UAF::UncookedOnly::FAnimGraphUtils::IsTraitStackNode(Node);
    }
};
```

```cpp
// MyAnimGraphBuilder.cpp
#include "MyAnimGraphBuilder.h"
#include "AnimGraphUncookedOnlyUtils.h"
```

## 模块依赖

### 插件依赖

| 插件 | 用途 |
|---|---|
| `UAF` | 统一动画框架基础插件，提供核心动画 Trait 系统和运行时 |
| `RigVM` | RigVM 虚拟机，提供动画图的节点执行引擎和编辑器图框架 |

### 模块依赖（UAFAnimGraphUncookedOnly）

| 模块 | 用途 |
|---|---|
| `UAF` | UAF 核心运行时模块 |
| `UAFAnimGraph` | 动画图运行时模块 |
| `AnimNextEditor` | AnimNext 编辑器基础工具 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `43658976` | Sequencer: Anim Mixer: Fix crash when scrubbing a level sequence after changing a Mix Layer transiti | 修复 Sequencer 动画混合器在切换 Mix Layer 后拖动时间轴时的崩溃 |
| 2026-05-12 | `61c7c092` | [UEMHC] - Fix Geometry Export crash and material issues on re-export | 修复几何体导出崩溃和重新导出时的材质问题 |
| 2026-05-12 | `14c22336` | UAF: Add tick order dependency between the UAF Montage Tick and CMC Tick to ensure the movement compo | 添加 UAF Montage Tick 与 CMC Tick 之间的执行顺序依赖 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32 位/64 位格式说明符不匹配问题 |
| 2026-04-22 | `287203b9` | UE 5.8 Animation deprecation clean up (CL 9/10): UAF | UE 5.8 动画系统废弃代码清理（UAF 部分） |

### 维护评价

- **状态**：🟢 **活跃维护中**
- **创建时间**：2025-06-26（约 1 年前），从内部 AnimNext 项目迁移而来
- **更新频率**：最近一个月有 5 次更新，包含功能修复、兼容性更新和代码清理
- **实验性标记**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，目前仍处于实验阶段
- **废弃警告**：最近一次更新（2026-04-22）涉及 UE 5.8 的废弃代码清理，表明 API 可能会有变动
- **推荐使用**：此插件为 Epic 官方的下一代动画图框架，API 尚不稳定，适合研究和实验性项目使用。生产环境建议等待其脱离实验阶段。依赖 `UAF` 和 `RigVM` 两个基础插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFAnimGraph)
- 官方文档（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFAnimGraph/Tests/UAFAnimGraphTests)