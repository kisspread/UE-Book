# AITestSuite

> Testing tools for artificial intelligence

| 属性 | 值 |
|---|---|
| 分类 | AI |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | AITestSuite (UncookedOnly), AITestSuiteEditor (Editor), MockAI (Runtime), MockGameplayTasks (Runtime), BehaviorTreeEditorTests (Editor), EQSQueryTestingPawnRuntime (Runtime) |
| 创建时间 | 2015-02-12 |
| 年龄标签 | 🏛️ 文物 (>10年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/AITestSuite) | |

## 用途

AITestSuite 是 Unreal Engine AI 系统的**自动化测试基础设施**。它不是一个面向最终用户的功能性插件，而是面向引擎开发者和需要对 AI 系统进行自动化验证的团队的**测试工具集**。

这个插件解决的核心问题是：**如何可靠地自动测试 Behavior Tree、EQS（Environment Query System）、AI Tasks、Blackboard 等 AI 子系统的正确性**。它提供了 Mock 对象（模拟对象）、测试用的 Pawn/Controller、以及一套基于 UE Automation Test 框架的测试用例。

简单来说：这个插件是 AI 系统的"单元测试+集成测试"工具箱。

## 使用场景

- **引擎开发者**：验证 Behavior Tree 节点执行流程、Decorator 条件判断、Service 调度等核心逻辑是否正确
- **AI 程序员**：为自定义 BT Task/Decorator/Service 编写自动化测试，确保重构后行为不变
- **QA 自动化**：通过 MockAI 和 MockGameplayTasks 构建可控的 AI 测试环境
- **EQS 开发**：测试 Environment Query 的查询逻辑，使用 EQSTestingPawn 在编辑器中可视化调试

**不适合的场景：**
- 如果你只是想在游戏中使用 AI，不需要这个插件——直接用 Engine 内置的 Behavior Tree 和 EQS 即可

## 蓝图用法

这个插件**没有暴露任何蓝图节点**。它是一个纯 C++ 测试框架插件，所有功能都通过自动化测试命令触发。

### 如何运行测试

在编辑器中通过以下方式运行 AI 测试：

1. **Session Frontend**：Window → Developer Tools → Session Frontend → Automation 标签页，筛选 `AITestSuite`
2. **命令行**：`UE5Editor-Cmd.exe ProjectName -ExecCmds="Automation RunTests AITestSuite" -Unattended -NullRHI -NoSound`
3. **控制台命令**：`Automation RunTests AITestSuite`（PIE 模式下）

## C++ 用法

### 核心概念：Mock 对象

AITestSuite 的核心是提供可控的 Mock 环境，避免真实 AI 系统的复杂性干扰测试。

#### MockAI（Runtime 模块）

提供以下测试替身：

| 类 | 用途 |
|---|---|
| `AMockAI_Character` | 带 `UBehaviorTreeComponent` + `UBlackboardComponent` 的测试用 Character |
| `AMockAI_Pawn` | 带 `UBehaviorTreeComponent` + `UBlackboardComponent` 的测试用 Pawn |
| `AMockAI_Controller` | 测试用 AIController，带有 BehaviorTreeComponent 和 BrainComponent 访问器 |
| `AMockAI_Hierarchical` | 支持层级 BT 的测试用 Character |

```cpp
// 在测试中创建 Mock AI Controller
UWorld* World = FAITestHelpers::GetWorld();
AMockAI_Controller* Controller = World->SpawnActor<AMockAI_Controller>();
Controller->RunBehaviorTree(MyTestBT);
```

#### MockGameplayTasks（Runtime 模块）

提供纯逻辑的测试用 Task：

| 类 | 用途 |
|---|---|
| `UMockGameplayTask` | 基础 Mock Task，支持 `ReadyForActivation()` |
| `UMockAbilityTask` | Mock AbilityTask |
| `UMockTaskOwner` | 模拟 Task Owner（`IGameplayTaskOwnerInterface`） |

#### BehaviorTreeEditorTests（Editor 模块）

测试 BT 节点查找和行为：

| 类 | 用途 |
|---|---|
| `FAITest_FindBTNode` | 在 BT 中查找特定类型的节点（按类/按名称） |

#### EQSQueryTestingPawnRuntime（Runtime 模块）

| 类 | 用途 |
|---|---|
| `AEQSQueryTestingPawn` | 可放置在场景中，在编辑器中运行 EQS 查询并可视化结果 |

### 编写 AI 测试用例

AITestSuite 使用 UE 标准的 `IMPLEMENT_SIMPLE_AUTOMATION_TEST` 宏定义测试：

```cpp
// 定义一个 AI 测试
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FMyAITest,
    "MyProject.AI.BehaviorTree.BasicExecution",
    EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::ProductFilter
)

bool FMyAITest::RunTest(const FString& Parameters)
{
    // 1. 创建测试世界
    UWorld* World = FAITestHelpers::GetWorld();
    
    // 2. 生成 Mock AI
    AMockAI_Controller* Controller = World->SpawnActor<AMockAI_Controller>();
    
    // 3. 加载并运行 Behavior Tree
    UBehaviorTree* BT = LoadObject<UBehaviorTree>(nullptr, TEXT("/Game/TestBT"));
    Controller->RunBehaviorTree(BT);
    
    // 4. 等待 BT tick 执行
    ADD_LATENT_AUTOMATION_TEST(FEngineWaitLatentCommand(1.0f));
    
    // 5. 验证结果
    TestEqual(TEXT("BT should have reached expected node"), 
              Controller->GetBrainComponent()->GetActiveNodeName(), 
              TEXT("ExpectedNode"));
    
    return true;
}
```

### 验证器（Validators）

AITestSuite 还包含一组自动运行的验证测试，确保常见 BT 模式正确工作：

| 测试 | 验证内容 |
|---|---|
| `BTTask_FindRandomLocation` | FindRandomLocation 任务能返回有效位置 |
| `BTService_OnBecomeRelevantReactivates` | Service 在条件变化时正确重新激活 |
| `BTDecorator_OnBecomeRelevant` | Decorator 在条件满足时正确触发 |
| `DecoratorTestRunBehaviorTreeSimple` | 基本 Decorator 流程 |
| `DecoratorTestRunBehaviorTreeObserverAborts` | Observer Abort 机制 |
| `DecoratorTestBlackboardObserver` | Blackboard 值变化时 Decorator 响应 |
| `AddRemoveBrainComponentRaceCondition` | BrainComponent 添加/移除的竞争条件 |
| `GenericStoreRawEntryInBlackboard` | Blackboard 通用存储 |

## 模块依赖

### AITestSuite (UncookedOnly)

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、容器、数学 |
| `CoreUObject` | UObject 系统、反射 |
| `Engine` | 引擎核心（World、Actor、Pawn 等） |
| `AIModule` | AI 核心模块（BT、Blackboard、AIController） |
| `GameplayTasks` | GameplayTask 框架 |
| `GameplayTags` | GameplayTag 系统 |
| `NavigationSystem` | 导航系统（AI 移动寻路） |

### MockAI (Runtime)

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `AIModule` | AI 核心 |
| `GameplayTasks` | GameplayTask |
| `NavigationSystem` | 导航系统 |

### MockGameplayTasks (Runtime)

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型 |
| `CoreUObject` | UObject 系统 |
| `GameplayTasks` | GameplayTask 框架 |

### AITestSuiteEditor (Editor)

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型 |
| `CoreUObject` | UObject 系统 |
| `AITestSuite` | 主测试模块 |
| `AIModule` | AI 核心 |
| `UnrealEd` | 编辑器功能 |
| `AssetTools` | 资产工具 |
| `AssetDefinition` | 资产定义 |
| `ToolMenus` | 工具菜单 |
| `EditorFramework` | 编辑器框架 |
| `Slate` | UI 框架 |
| `SlateCore` | Slate 核心 |
| `InputCore` | 输入系统 |
| `ToolWidgets` | 工具控件 |
| `GameplayAbilities` | Gameplay Ability 系统（用于 AbilityTask 测试） |

### BehaviorTreeEditorTests (Editor)

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `UnrealEd` | 编辑器功能 |
| `AITestSuite` | 主测试模块 |
| `AIModule` | AI 核心 |
| `GameplayTasks` | GameplayTask |

### EQSQueryTestingPawnRuntime (Runtime)

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `AIModule` | AI 核心 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-09-19 | `624732fc4389` | Implement latent test wait for true/ignore value for some mockai tests | 改进 MockAI 测试的延迟等待机制，支持等待特定条件而非固定时间 |
| 2025-09-19 | `776d1b7b38ea` | Modified the UT delay to be under a condition rather than a hardcoded value | 将 UT 延迟从硬编码改为条件驱动，提高测试可靠性 |
| 2024-12-12 | `282b1251412a` | Simplify IncludeWhatYouUse for AutomationTest, FEngineWaitLatentCommand | 清理 IWYU include，属于 UE5 IWYU 合规重构 |

### 维护评价

- **创建时间**: 2015 年 2 月（UE4 时代），已有 10+ 年历史，属于 UE AI 系统的原始基础设施
- **最近更新**: 2025 年 9 月有实质性改进（MockAI 测试框架增强），说明仍在积极维护
- **维护状态**: ✅ **活跃维护** — 作为 UE AI 系统的测试基石，随着 AI 模块的更新而同步维护
- **注意**: 此插件 **默认未启用**（`EnabledByDefault: false`），仅在需要运行 AI 自动化测试时才应启用
- **推荐使用**: 仅推荐给引擎开发者或需要深度自定义 AI 测试的团队。普通 AI 开发者不需要启用此插件

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/AITestSuite)
- 官方文档: 无专门文档（此为内部测试插件）
