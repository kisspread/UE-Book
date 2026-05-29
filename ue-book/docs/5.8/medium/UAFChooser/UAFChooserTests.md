# UAF Chooser

> Chooser integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF选择器集成 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFChooser` (Runtime), `UAFChooserEditor` (Runtime), `UAFChooserUncookedOnly` (Runtime), `UAFChooserTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFChooser) | |

## 用途

UAFChooser 插件为 Unreal Animation Framework (UAF) 提供了与 Chooser 表集成的能力。Chooser 是一个强大的数据驱动的选择器系统，用于根据输入条件查找和选择结果。该插件的目的在于让开发者能够在 UAF 的动画流程（如动画蓝图、AnimNode）中，直接使用 Chooser 表来驱动动画混合、选择动画资产或控制动画逻辑，从而实现更灵活、数据驱动且易于配置的动画决策系统。

## 使用场景

- 你在使用 UAF 构建动画系统，并希望根据角色状态（如生命值、装备、战斗状态）动态选择不同的动画混合树或动画资产。
- 你需要实现一套复杂的、非线性的动画逻辑（如多段攻击的连招、根据环境互动的不同反应），并希望通过表格化数据而非硬编码来管理和扩展。
- 你已经在项目中使用了 Chooser 表来管理游戏逻辑（如物品选择、对话分支），并希望将同样的数据驱动方式引入动画领域。

## 蓝图用法

根据模块类型和集成目的，主要的蓝图用法通常集中在 AnimNode 或 AnimInstance 上。
（注：以下节点基于通用集成模式推断，具体节点名需查看 `UAFChooser` 模块的公共头文件）

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （集成于 AnimNode） | 在 UAF 动画节点图中，提供基于 Chooser 表的选择逻辑。例如，一个“Chooser Blend”节点，其输入参数（如枚举、布尔值）会连接到 Chooser 表，输出对应的动画结果。 | 可能存在于 `UAnimNode_*` 相关类中 |

### 使用示例（蓝图描述）

1.  在动画蓝图的 AnimGraph 中，添加一个由 `UAFChooser` 提供的自定义 AnimNode，例如 “Chooser Select”。
2.  将该节点的“选择条件”输入引脚（如一个名为 `SelectorKey` 的枚举变量）连接到角色状态或游戏逻辑的枚举输出。
3.  在节点细节面板或外部资源中，指定一个 Chooser 表资产。该表定义了当 `SelectorKey` 为不同值时，应该选择哪个动画子图或动画资产。
4.  将该节点的输出连接到后续的动画逻辑或最终动画姿势。

## C++ 用法

（注：由于未提供具体的 `.h/.cpp` 文件内容，以下为基于测试模块 `UAFChooserTests` 存在的通用指导）

### 头文件引入

```cpp
#include "UAFChooser.h" // 或更具体的集成头文件
```

### 基本用法

测试是了解插件用法的最佳途径。请查看 `Tests/` 目录下的用例。
```cpp
// 伪代码示例：假设测试用例中展示了如何创建一个使用 Chooser 的 UAF AnimNode
// 来源: 可能位于 Engine/Plugins/Experimental/UAF/UAFChooser/Tests/UAFChooserTests/

// 1. 包含测试框架和插件头文件
#include "Misc/AutomationTest.h"
#include "UAFChooser.h" // 假设的主头文件

// 2. 定义测试
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FUAFChooserTest, "UAF.Chooser.Integration", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FUAFChooserTest::RunTest(const FString& Parameters)
{
    GIVEN("A Chooser table and a UAF AnimNode expecting input")
    {
        // 3. 设置测试环境，创建 Chooser 表、UAF 上下文等
        // ... 代码 ...

        WHEN("The Chooser is queried with specific input")
        {
            // 4. 执行插件提供的查询/评估函数
            // ... 调用 UAFChooser 提供的 API，获取结果 ...

            THEN("It should return the correct animation asset or blend logic")
            {
                // 5. 验证结果是否符合 Chooser 表中的预期
                // TestEqual("Selected animation is Idle", SelectedAnim, ExpectedIdleAnim);
            }
        }
    }
    return true;
}
```

### 进阶用法

结合多个测试用例，可以了解更复杂的集成，例如：
- 如何动态更新 Chooser 表的输入上下文。
- 如何处理 Chooser 表的异步加载。
- 如何将 Chooser 的输出用于驱动动画状态机或混合树。

## Demo 示例

一个基于测试用例推测的最小 C++ 集成示例。注意：此示例为示意性代码，具体类名和方法需以实际源码为准。

```cpp
// MyAnimNodeChooser.h
#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimNodeBase.h"
#include "UAFChooserInterface.h" // 假设的接口头文件

USTRUCT(BlueprintInternalUseOnly)
struct FAnimNode_MyChooserNode : public FAnimNode_Base
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = "Chooser")
    FChooserTableSelector ChooserSelector; // 可能在 UAFChooser 中定义的 Chooser 选择器结构

    // ... 其他 UAF 动画节点所需的输入输出 ...

    // FAnimNode_Base interface
    virtual void Initialize_AnyThread(const FAnimationInitializeContext& Context) override;
    virtual void Evaluate_AnyThread(FPoseContext& Output) override;
    // End of FAnimNode_Base interface
};

// MyAnimNodeChooser.cpp
#include "MyAnimNodeChooser.h"
#include "UAFChooserSubsystem.h" // 假设的子系统，用于查询 Chooser

void FAnimNode_MyChooserNode::Initialize_AnyThread(const FAnimationInitializeContext& Context)
{
    // 初始化 Chooser 相关资源
    // ...
}

void FAnimNode_MyChooserNode::Evaluate_AnyThread(FPoseContext& Output)
{
    // 1. 准备输入上下文（例如，当前角色状态）
    FChooserEvaluationContext EvalContext;
    // ... 填充 EvalContext ...

    // 2. 使用 UAF Chooser 集成进行查询
    UUAFChooserSubsystem* ChooserSubsystem = Context.GetAnimInstance()->GetWorld()->GetSubsystem<UUAFChooserSubsystem>();
    if (ChooserSubsystem)
    {
        // 3. 根据 Chooser 表的结果，决定后续的动画评估逻辑
        // FChooserEvaluationResult Result = ChooserSubsystem->EvaluateChooser(ChooserSelector, EvalContext);
        // ... 使用 Result (如选择一个子 AnimNode 进行评估) ...
    }

    // ... 最终输出动画姿势 ...
}
```

## 模块依赖

从 `Build.cs` 文件和插件性质推断。要使用 `UAFChooser`，你的模块（特别是编辑器或测试模块）通常需要依赖以下插件或模块：

| 模块 | 用途 |
|---|---|
| `UAF` | 核心 UAF 动画框架插件，提供基础 AnimNode 和系统 |
| `Chooser` | 提供核心的 Chooser 表数据结构和查询逻辑 |
| `GameplayTags` | 如果 Chooser 的选择条件基于 GameplayTag，则需要此模块 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-01 | `720e7f98` | Add modifier anim node data base class for anim nodes with a single child | 为单子节点动画节点添加了修饰符基类，完善了动画节点体系。 |
| 2026-03-19 | `910301d3` | UAF Anim Node rewind debugger track | 新增 UAF 动画节点的倒退调试器跟踪功能，增强调试能力。 |
| 2026-03-11 | `bda4ef8e` | Add debug update counter to UAF anim node to enforce invariants | 为 UAF 动画节点添加调试更新计数器，用于确保逻辑不变性。 |
| 2026-03-11 | `7da85466` | Implement AnimOp system for new UAF runtime | 实现了用于新 UAF 运行时的 AnimOp 系统，是核心架构的一部分。 |
| 2026-03-10 | `5a95823d` | AnimNodes Blend stack helper class to avoid too much code duplication (it can be used as either a b) | 添加了 AnimNodes 混合栈辅助类，减少代码重复，提升了开发效率。 |

### 维护评价

- **活跃维护**：插件创建于 2025 年 6 月，属于实验性插件（`IsExperimentalVersion=true`，默认禁用）。
- **近期更新频繁**：从 2026 年 3 月至 4 月有多次实质性提交，集中在动画节点基础类的完善、新运行时系统（AnimOp）的实现以及调试工具的增强，表明正在快速开发中。
- **核心开发中**：作为 UAF 和 Chooser 的集成桥梁，其更新紧密跟随这两个核心系统的演进。
- **推荐使用**：该插件处于实验性、快速迭代阶段。适合希望探索前沿动画系统、且能够接受 API 可能发生变化的开发者或技术预览项目。不建议用于追求稳定的生产环境。由于是新插件，社区知识和示例可能有限，需要参考 Epic 提供的测试用例进行学习。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFChooser)
- [官方文档]( ) （暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFChooser/Tests)