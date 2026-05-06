# AI Behaviors

> Encapsulated fire-and-forget behaviors for AI agents

| 属性 | 值 |
|---|---|
| 中文名 | AI 行为系统 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayBehaviorsModule` (Runtime), `GameplayBehaviorsModule` (UncookedOnly), `GameplayBehaviorsEditorModule` (Editor), `GameplayBehaviorsTestSuite` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GameplayBehaviors) | |

## 用途

GameplayBehaviors 提供了轻量级、即发即弃（fire-and-forget）的行为封装机制，专为 AI Agent 设计。它借鉴了 GameplayAbilities 的“能力-效果-任务”架构，但更简化，无需复杂的 GameplayEffect 和 Ability 系统负担。行为实例由 `UGameplayBehavior` 表示，通过 `UGameplayBehaviorConfig` 配置，可与 BehaviorTree 任务（BTTask）深度集成。

该插件解决了 AI 行为开发中的两个痛点：
1. **行为复用**：将常见行为（如跳跃、翻滚、投掷）封装为独立资源，可在多个黑板任务中共享。
2. **即用即弃**：行为执行完毕后自动销毁，无需手动管理生命周期，特别适合与 GameplayAbilities 配合，执行短促的动画驱动操作。

## 使用场景

- 需要执行一次性的动画/物理行为（如“躲避”“攀爬”），且不想引入 GameplayAbilities 的完整开销时。
- 希望在 BehaviorTree 的 Task 节点中，通过简单的配置触发带有参数的行为（例如指定行为配置资产 `UGameplayBehaviorConfig`）。
- 构建轻量级的“行为库”，在多个 AI 控制器之间共享预定义行为模板。

## 蓝图用法

> **注意**：本插件的主要运行时模块 `GameplayBehaviorsModule` 未提供蓝图可调用函数。测试模块 `GameplayBehaviorsTestSuite` 不向蓝图暴露节点。以下内容基于常见模式推断，实际 API 请参考插件源代码。

如果需在蓝图中触发行为，通常通过自定义 BTTask 节点内部调用 C++ API，或在 AI Controller 中通过 `TriggerGameplayBehavior` 函数（由 `UGameplayBehaviorConfig` 提供）。具体蓝图节点需查看源码中 `UFUNCTION(BlueprintCallable)` 标记。

### 核心节点（推测）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `TriggerGameplayBehavior` | 触发一个由配置资产定义的行为 | `UGameplayBehaviorConfig` |
| `OnBehaviorFinished` | 行为完成时触发的自定义事件 | `UGameplayBehavior` |

（因缺少具体源码，以上为基于架构的合理推断，实际节点可能不同。）

## C++ 用法

本模块为测试套件（`GameplayBehaviorsTestSuite`），主要用于自动化测试 `GameplayBehaviorsModule` 的功能。开发者可参考其测试代码编写自定义行为。

### 头文件引入

```cpp
#include "GameplayBehaviorsTestSuiteModule.h"
```

### 基本用法

测试套件通过自动化测试宏（`IMPLEMENT_SIMPLE_AUTOMATION_TEST`）对行为系统进行验证。以下示例来自测试模块目录（`Source/GameplayBehaviorsTestSuite`）：

```cpp
// 文件路径: Engine/Plugins/Experimental/GameplayBehaviors/Source/GameplayBehaviorsTestSuite/Private/Tests/BehaviorTest.cpp
// （假设存在，实际需查看仓库）

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGameplayBehaviorBasicTest, "GameplayBehaviors.BasicExecution",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FGameplayBehaviorBasicTest::RunTest(const FString& Parameters)
{
    // 1. 创建行为配置资产（UObject）
    UGameplayBehaviorConfig* Config = NewObject<UGameplayBehaviorConfig>();
    // 2. 触发行为
    UGameplayBehavior* Behavior = Config->TriggerBehavior(/* agent */ GetWorld()->GetFirstPlayerController());
    // 3. 等待执行完成（通常通过Tick或回调）
    TestNotNull("Behavior should be created", Behavior);
    return true;
}
```

**注意**：上述代码为示意，具体 `UGameplayBehaviorConfig`、`UGameplayBehavior` 的实际接口需查阅 `GameplayBehaviorsModule` 的公共头文件。

### 进阶用法

测试套件中可能包含多个测试用例，覆盖：
- 行为正常执行和生命周期回调
- 行为配置参数传递（如浮点、向量、对象引用）
- 行为与行为树的集成（通过 `BTTask_SetKeyValueX` 等任务）

从 Git 历史看，2024-09-27 的提交 `Create BTTask_SetKeyValueX for all blackboard key type` 可能新增了一批 BTTask，用于在黑板上设置各种键值类型，推测这些任务可搭配 `GameplayBehavior` 使用。

## Demo 示例

由于仅提供测试模块头文件，以下给出一个最小化 C++ 示例，展示如何注册并运行一个测试（需在自定义编辑器模块或关卡加载时运行）。

**头文件 DemoTest.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Misc/AutomationTest.h"

// 引入测试套件模块（仅作为示例，实际测试应放入独立的测试模块）
IMPLEMENT_COMPLEX_AUTOMATION_TEST(FGameplayBehaviorTestExample, "GameplayBehaviors.ExampleTest",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
```

**源代码 DemoTest.cpp**

```cpp
#include "DemoTest.h"
#include "GameplayBehaviorsTestSuiteModule.h"
#include "GameplayBehaviorConfig.h" // 假设存在

bool FGameplayBehaviorTestExample::RunTest(const FString& Parameters)
{
    // 简化测试：检查插件模块是否加载
    if (!IGameplayBehaviorsTestSuiteModule::IsAvailable())
    {
        AddError("GameplayBehaviorsTestSuite module not loaded");
        return false;
    }

    // 创建测试世界（需使用 AutomationEditorCommon 工具，此处省略）
    // 典型流程：创建 UGameplayBehaviorConfig → 调用 TriggerBehavior → 确认行为对象非空
    return true;
}
```

**模块依赖**：测试代码依赖 `GameplayBehaviorsModule` 和 `GameplayBehaviorsTestSuite`，但示例仅演示模块可用性检查，无需额外依赖。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayAbilities` | 行为系统可与 GameplayAbility 协同工作，提供技能相关行为 |
| `AIModule` | 集成行为树（BTTask）和黑板 |

其余为标准 Engine 依赖（Core、CoreUObject、Engine、Slate 等），不逐一列出。

## 维护状态

### 近期更新

- 2025-06-26 `ec900998` — 添加 UE_INLINE_GENERATED_CPP_BY_NAME 到对应 .gen.cpp 文件的源文件中
- 2025-04-23 `93a13080` — 使用 LyraGame 构建目标转换文件，添加 DLL 存储到方法/静态变量
- 2025-01-16 `4a9936fa` — [BehaviorTree] 将对黑板资源的 ensure 替换为错误报告，因为这是可能的可恢复情况
- 2024-11-10 `66e9bb39` — 移除所有 `#if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2` 作用域
- 2024-09-27 `58cf817b` — 创建所有黑板键类型的 BTTask_SetKeyValueX

### 维护评价

- **创建时间**：2024年9月（约1年前）
- **近期更新**：持续有代码规范改进和行为树兼容性修复，最近一次在2025年6月，属于活跃维护
- **活跃度**：半年内有实质性更新（编译修复、API 调整），功能稳定
- **已知限制**：插件标注为实验性（`IsBetaVersion=true`），API 可能发生变化；当前仅提供了测试套件头文件，运行时模块的详细文档尚需完善
- **推荐使用**：适合早期集成和尝试，生产环境建议跟踪后续正式版本；由于默认禁用，需手动在项目设置中启用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GameplayBehaviors)
- [官方文档](https://docs.unrealengine.com/)（插件无独立文档页，可参考官方的“AI Behaviors”开发指南）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GameplayBehaviors/Source/GameplayBehaviorsTestSuite/Private/Tests)（假设存在，实际需确认仓库结构）