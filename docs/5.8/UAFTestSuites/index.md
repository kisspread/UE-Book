# UAF Tests

> UAF Automated Tests

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资产、蓝图、动画数据） |
| 模块 | `UAFAnimGraphTestSuite` (Runtime), `UAFAnimNodeTestData` (Runtime), `UAFCQTestSuite` (Runtime), `UAFTestSuite` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-30 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites) | |

## 用途

本插件是 Unreal Animation Framework (UAF) 系统的官方自动化测试套件。它并非面向最终用户的功能插件，而是用于验证 UAF 核心功能（如动画图求值、动画节点逻辑、CQ 系统）的正确性、稳定性和性能。插件的存在是为了保障 UAF 系统的质量，是 UAF 开发和维护流程中的关键组成部分。

## 使用场景

- **UAF 核心开发者**：在修改动画图、动画节点或 CQ 系统后，运行此测试套件以确保没有引入回归错误。
- **引擎集成测试**：在引擎构建或持续集成 (CI) 流程中，作为质量门禁的一部分，自动验证 UAF 模块的健康状况。
- **学习 UAF 内部机制**：通过阅读测试用例，可以了解 UAF 各个子系统的预期行为和边界情况。

## 蓝图用法

本插件主要提供自动化测试功能，不包含面向游戏逻辑的公开蓝图 API。其测试资产（如测试动画蓝图、测试数据资产）可在编辑器中查看和调试，但通常不直接用于游戏运行时。

## C++ 用法

本插件的核心是编写和组织自动化测试用例。开发者可以通过继承或参考其中的测试类来为自己的 UAF 相关功能编写测试。

### 头文件引入

```cpp
// 引入测试框架基础
#include "Misc/AutomationTest.h"
// 引入UAF测试基类（如果存在）
#include "UAFTestSuite.h"
```

### 基本用法

测试用例通常使用 `IMPLEMENT_SIMPLE_AUTOMATION_TEST` 宏定义，并遵循 BDD (Given-When-Then) 风格组织。

```cpp
// 示例：一个简单的动画节点功能测试
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FMyAnimNodeTest,
    "UAF.AnimNodes.MyNode.BasicFunctionality",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FMyAnimNodeTest::RunTest(const FString& Parameters)
{
    // Given: 准备测试环境和数据
    UWorld* World = UWorld::CreateWorld(EWorldType::Game, false);
    // ... 创建测试用的动画蓝图实例等

    // When: 执行被测试的操作
    // ... 模拟动画节点的求值过程

    // Then: 验证结果
    TestEqual(TEXT("节点输出值应为预期值"), ActualValue, ExpectedValue);

    // 清理
    World->DestroyWorld(false);
    return true;
}
```

### 进阶用法

更复杂的测试可能涉及多个模块的协作，例如测试动画图与 CQ 系统的交互。这通常需要组合使用 `UAFAnimNodeTestData` 模块提供的数据资产和 `UAFCQTestSuite` 中的测试框架。

## Demo 示例

本插件本身即为一系列可运行的示例。要查看或运行测试：
1.  在编辑器中启用 `UAFTestSuites` 插件。
2.  打开“会话前端” (Session Frontend) 窗口，切换到“自动化” (Automation) 选项卡。
3.  在测试列表中查找以 `UAF.` 开头的测试项，例如 `UAF.AnimGraph` 或 `UAF.CQ`。
4.  选择并运行这些测试，观察结果。

## 模块依赖

本插件的模块主要依赖于 UAF 核心模块和测试框架。由于是测试套件，其依赖关系反映了被测系统（UAF）的依赖。

| 模块 | 用途 |
|---|---|
| `UAF` | 被测试的核心动画框架模块 |
| `UAFAnimGraph` | 被测试的动画图相关功能 |
| `UAFAnimNodes` | 被测试的动画节点库 |
| `UAFCQ` | 被测试的 CQ (Control Rig Query?) 系统 |
| `ControlRig` | CQ 系统可能依赖的底层控制 rig 框架 |

## 维护状态

### 近期更新

- 2026-04-14 `12eb7efc` 修复 FBindableXxx 在与 UAF 特性一同使用时的绑定序列化问题。
- 2026-04-14 `35e60df1` 将 UE_LOG 迁移至 UE_LOGF。
- 2026-04-10 `797a6da6` 将 GetComponent 重命名为 GetOrAddComponent 以更准确地反映其功能。
- 2026-04-06 `4ba19be0` 为 FBindableValue 添加函数绑定支持。
- 2026-03-30 `0df5eb4c` 添加 FBindableTransform 用于绑定 FTransform 值（相比使用 FBindableStruct 包装 FTransform，其开销更低）。

### 维护评价

该插件处于**活跃维护**状态。在约两周的时间内有五次提交，频率较高，且内容集中于功能增强（如新增绑定类型、函数绑定支持）和问题修复，表明开发团队正在积极完善其核心功能。从提交内容看，插件正从基础功能向更稳定、更完善的API演进。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites/Source) (各模块的 `Tests` 目录)