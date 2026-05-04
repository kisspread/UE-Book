# State Tree

> General purpose hierarchical state machine

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、Schema 模板） |
| 模块 | `StateTreeModule` (Runtime), `StateTreeEditorModule` (Runtime), `StateTreeDeveloper` (Runtime), `StateTreeTestSuite` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/StateTree) | |

---

## 用途

StateTree 是 UE5 中的**通用分层状态机系统**，用于替代和补充传统的行为树（Behavior Tree）与有限状态机（FSM）。它解决的核心问题是：**在复杂的游戏逻辑中，需要一种既能表达层级结构、又能支持事件驱动转换、还能进行属性绑定和数据流的状态管理方案**。

与行为树相比，StateTree 的关键差异在于：

- **状态导向而非任务导向**：以"状态"为核心组织单位，每个状态可包含多个任务（Task）、评估器（Evaluator）和条件（Condition）
- **原生属性绑定**：内置编译期属性绑定系统，节点间数据流动无需手动编写胶水代码
- **Schema 可扩展**：通过 `UStateTreeSchema` 定义不同类型状态树的约束（如 AI 行为、动画状态、游戏流程）
- **分层结构**：支持子树（SubTree）和状态嵌套，适合表达复杂的游戏逻辑层级
- **事件驱动转换**：基于 GameplayTag 的事件系统驱动状态转换，支持条件表达式组合

StateTree 默认未启用（`EnabledByDefault=false`），需要在项目设置中手动启用。

## 使用场景

- 你需要为 AI 角色构建复杂的行为逻辑，且行为树不够灵活 → 用 StateTree
- 你需要一个可视化的状态机编辑器来管理游戏流程（如关卡流程、UI 状态） → 用 StateTree
- 你需要节点间自动数据绑定，避免手动传递参数 → 用 StateTree 的属性绑定系统
- 你需要基于事件（GameplayTag）驱动的状态转换 → 用 StateTree 的事件系统
- 你需要可扩展的状态机框架，不同类型的状态树有不同约束 → 用 StateTree 的 Schema 系统

## 蓝图用法

StateTree 的运行时 API 主要在 `StateTreeModule` 中。编辑器模块提供资产创建和编译功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CompileStateTree` | 编译指定的 StateTree 资产 | `UStateTreeEditingSubsystem` |
| `ValidateStateTree` | 验证并修复 StateTree 资产的 Schema 约束 | `UStateTreeEditingSubsystem` |
| `CalculateStateTreeHash` | 计算 StateTree 编辑数据的哈希值 | `UStateTreeEditingSubsystem` |
| `FindOrAddViewModel` | 获取或创建 StateTree 的编辑器视图模型 | `UStateTreeEditingSubsystem` |

### 使用示例（蓝图描述）

StateTree 资产的使用通常通过以下流程：

1. **创建资产**：在 Content Browser 中右键 → Artificial Intelligence → State Tree，选择 Schema 类型
2. **编辑状态**：在 StateTree 编辑器中添加状态（State），每个状态可挂载任务（Task）、条件（Condition）、评估器（Evaluator）
3. **配置转换**：在状态之间添加转换（Transition），设置触发条件和目标状态
4. **属性绑定**：通过绑定面板将一个节点的输出属性连接到另一个节点的输入属性
5. **编译**：点击编译按钮，编辑器数据被烘焙为运行时格式

## C++ 用法

### 头文件引入

```cpp
// 编辑器模块（资产编译、编辑）
#include "StateTreeEditorModule.h"
#include "StateTreeCompiler.h"
#include "StateTreeCompilerManager.h"
#include "StateTreeEditingSubsystem.h"

// 运行时模块（状态树实例执行）
#include "StateTree.h"
```

### 基本用法：编译 StateTree 资产

从 `StateTreeCompilerManager.h` 和 `StateTreeEditingSubsystem.h` 提取的编译用法：

```cpp
#include "StateTreeCompilerManager.h"
#include "StateTreeEditingSubsystem.h"
#include "StateTreeCompilerLog.h"

// 方式一：通过 CompilerManager 同步编译
UStateTree* MyStateTree = /* 获取或创建 StateTree 资产 */;
bool bSuccess = UE::StateTree::Compiler::FCompilerManager::CompileSynchronously(MyStateTree);

// 方式二：带日志的编译
FStateTreeCompilerLog Log;
bool bSuccess = UE::StateTree::Compiler::FCompilerManager::CompileSynchronously(MyStateTree, Log);
if (!bSuccess)
{
    // 处理编译错误，Log 中包含详细错误信息
    TArray<TSharedRef<FTokenizedMessage>> Messages = Log.ToTokenizedMessages();
}

// 方式三：通过编辑器子系统编译
FStateTreeCompilerLog Log;
bool bSuccess = UStateTreeEditingSubsystem::CompileStateTree(MyStateTree, Log);
```

### 基本用法：验证 StateTree

```cpp
#include "StateTreeEditingSubsystem.h"

// 验证并修复 StateTree 的 Schema 约束
UStateTree* MyStateTree = /* 获取 StateTree 资产 */;
UStateTreeEditingSubsystem::ValidateStateTree(MyStateTree);
```

### 进阶用法：自定义 Schema 和编辑器扩展

StateTree 支持通过 Schema 系统自定义不同类型状态树的行为：

```cpp
#include "StateTreeEditorSchema.h"
#include "StateTreeEditorData.h"
#include "StateTreeEditorModule.h"

// 自定义 Schema：限制状态树的编辑行为
UCLASS()
class UMyGameplaySchema : public UStateTreeEditorSchema
{
    GENERATED_BODY()
public:
    // 禁止添加扩展
    virtual bool AllowExtensions() const override { return false; }
    
    // 自定义编译后处理
    virtual bool HandlePostInternalCompile(
        const UE::StateTree::Compiler::FPostInternalContext& Context) override
    {
        // 在编译成功后执行自定义逻辑
        return true;
    }
    
    // 自定义验证逻辑
    virtual void Validate(TNotNull<UStateTree*> StateTree) override
    {
        Super::Validate(StateTree);
        // 添加自定义验证规则
    }
};

// 注册自定义编辑器数据类型
FStateTreeEditorModule& EditorModule = FStateTreeEditorModule::GetModule();
EditorModule.RegisterEditorDataClass(UMySchema::StaticClass(), UMyEditorData::StaticClass());
EditorModule.RegisterEditorSchemaClass(UMySchema::StaticClass(), UMyEditorSchema::StaticClass());
```

### 进阶用法：编辑器数据扩展

```cpp
#include "StateTreeEditorDataExtension.h"

// 自定义编辑器数据扩展，在编译后执行额外处理
UCLASS()
class UMyStateTreeExtension : public UStateTreeEditorDataExtension
{
    GENERATED_BODY()
public:
    virtual bool HandlePostInternalCompile(
        const UE::StateTree::Compiler::FPostInternalContext& Context) override
    {
        // 编译成功后的自定义处理
        return true;
    }
    
    virtual void CustomizeDetails(
        TNonNullPtr<UStateTreeState> State,
        IDetailLayoutBuilder& DetailBuilder) override
    {
        // 自定义状态的细节面板
    }
};
```

### 进阶用法：监听编译事件

```cpp
#include "StateTreeEditorModule.h"

// 监听所有 StateTree 资产的编译完成事件
FStateTreeEditorModule& EditorModule = FStateTreeEditorModule::GetModule();
EditorModule.OnPostInternalCompile().AddLambda(
    [](const UE::StateTree::Compiler::FPostInternalContext& Context)
    {
        const UStateTree* StateTree = Context.GetStateTree();
        // 对编译完成的 StateTree 执行自定义逻辑
    });
```

## Demo 示例

### 自定义 StateTree 编辑器宿主

```cpp
// MyStateTreeEditorHost.h
#pragma once

#include "IStateTreeEditorHost.h"
#include "StateTree.h"

class FMyStateTreeEditorHost : public IStateTreeEditorHost
{
public:
    FMyStateTreeEditorHost(UStateTree* InStateTree)
        : StateTree(InStateTree) {}

    virtual FName GetCompilerLogName() const override { return TEXT("MyStateTreeCompiler"); }
    virtual FName GetCompilerTabName() const override { return TEXT("MyStateTreeCompilerTab"); }
    virtual bool ShouldShowCompileButton() const override { return true; }
    virtual bool CanToolkitSpawnWorkspaceTab() const override { return true; }
    virtual UStateTree* GetStateTree() const override { return StateTree; }
    virtual FSimpleMulticastDelegate& OnStateTreeChanged() override { return StateTreeChangedDelegate; }
    virtual TSharedPtr<IDetailsView> GetAssetDetailsView() override { return nullptr; }
    virtual TSharedPtr<IDetailsView> GetDetailsView() override { return nullptr; }
    virtual TSharedPtr<UE::StateTreeEditor::FWorkspaceTabHost> GetTabHost() const override { return nullptr; }

private:
    UStateTree* StateTree;
    FSimpleMulticastDelegate StateTreeChangedDelegate;
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PropertyBinding` | 属性绑定框架，StateTree 节点间数据流的核心依赖 |
| `GameplayTags` | 事件系统的 GameplayTag 支持 |
| `StructUtils` | FInstancedStruct 等动态结构体工具 |
| `StateTreeModule` | 运行时状态树执行引擎（编辑器模块依赖） |
| `EditorFramework` | 编辑器框架（测试套件依赖） |
| `UnrealEd` | 编辑器工具（测试套件依赖） |

## 维护状态

### 近期更新

```
- 4cf1fcbba5b3 [State Tree] fixed crash when paste a binding to context data
- 1c99e02fa85a [StateTreeDebugger] Prevent StateTreeDebugger from auto-recording on PIE start when not using the legacy mode. Users should rely on the RewindDebugger option.
- f4d53f0d55f0 [State Tree] fixed Delegate Listener cannot bind to nested Delegate Dispatcher because a false CanAcceptPropertyOrChildren will stop traversing any child properties
```

### 维护评价

**活跃维护** ⭐⭐⭐⭐

- **创建时间**：2021 年 9 月，约 4 年历史，属于较新的系统
- **更新频率**：持续有功能性更新和 Bug 修复，近期修复了属性绑定粘贴崩溃、委托监听器嵌套绑定、调试器自动录制等问题
- **活跃度**：作为 UE5 核心 AI/游戏逻辑系统，由 Epic 官方团队持续维护
- **版本状态**：Version 0.1，尚未标记为 1.0 正式版，但已在 Lyra 等官方示例项目中广泛使用
- **已知限制**：默认未启用（`EnabledByDefault=false`），需要手动在项目设置中启用；部分功能标记为 Experimental（如 `bRetainNodePropertyValues`）
- **推荐程度**：强烈推荐用于新项目。StateTree 是 Epic 推荐的下一代 AI/状态管理方案，正在逐步替代行为树。虽然版本号仍为 0.1，但功能已相当成熟，且有持续的官方支持

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/StateTree)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/StateTree/Source/StateTreeTestSuite)