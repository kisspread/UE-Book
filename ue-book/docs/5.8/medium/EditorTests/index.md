# Editor Tests

> 

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器测试 |
| 分类 | Testing |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资产） |
| 模块 | `EditorTests` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2016-09-21 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/EditorTests) | |

## 用途

`EditorTests` 插件是一个为 Unreal Engine 编辑器功能提供自动化测试框架和工具集的插件。它包含一组蓝图函数库，用于测试编辑器中的特定功能，如网格体合并、材质烘焙、蓝图控件编辑等。其核心目的是为引擎开发者（主要是 Epic Games 内部）提供一套编写、运行和验证编辑器功能正确性的自动化测试用例。它不是一个面向最终用户的功能性插件，而是一个**开发者工具**，用于确保引擎编辑器的稳定性与功能回归测试。

## 使用场景

- 你正在开发或维护引擎编辑器的功能，需要为新功能或修复编写回归测试。
- 你需要验证编辑器 UI 工具（如蓝图控件设计器）在交互后的状态是否正确。
- 你需要自动化测试复杂的资产处理流程，例如网格体合并与材质烘焙。
- 你是引擎贡献者，需要确保代码更改没有破坏现有的编辑器功能。

## 蓝图用法

插件提供的蓝图节点主要集中在 `UEditorTestsUtilityLibrary` 和 `UEditorUtilityTest` 类中，用于构建测试逻辑。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BakeMaterialsForComponent` | 为指定的静态网格组件烘焙材质（原地操作）。 | `UEditorTestsUtilityLibrary` |
| `MergeStaticMeshComponents` | 将一组静态网格组件合并，并根据设置烘焙出图集材质。 | `UEditorTestsUtilityLibrary` |
| `CreateProxyMesh` | 为一组静态网格组件创建代理网格体（简化网格）。 | `UEditorTestsUtilityLibrary` |
| `GetChildEditorWidgetByName` | 在控件蓝图中，通过名称查找一个子控件，用于测试控件编辑。 | `UEditorTestsUtilityLibrary` |
| `SetEditorWidgetNavigationRule` | 设置控件的导航规则。 | `UEditorTestsUtilityLibrary` |
| `GetEditorWidgetNavigationRule` | 获取控件的导航规则。 | `UEditorTestsUtilityLibrary` |
| `Run` | 启动一个 `EditorUtilityTest` 的执行流程。 | `UEditorUtilityTest` |
| `PrepareTest` | 测试准备阶段的事件实现点（蓝图可覆盖）。 | `UEditorUtilityTest` |
| `FinishPrepareTest` | 通知测试框架准备工作完成，可以开始运行。 | `UEditorUtilityTest` |
| `StartTest` | 测试运行阶段的事件实现点（蓝图可覆盖）。 | `UEditorUtilityTest` |
| `FinishTest` | 通知测试框架测试运行结束，并报告结果。 | `UEditorUtilityTest` |
| `AddError` / `AddWarning` / `AddInfo` | 向测试日志中添加不同级别的信息。 | `UEditorUtilityTest` |
| `ExpectTrue` / `ExpectFalse` | 断言检查，条件失败则记录错误。 | `UEditorUtilityTest` |
| `GetState` / `IsRunning` | 获取测试的当前状态。 | `UEditorUtilityTest` |

### 使用示例（蓝图描述）

要创建一个编辑器功能测试：
1.  创建一个新的蓝图类，父类选择 `EditorUtilityTest`。
2.  在 `PrepareTest` 事件中，设置测试初始状态（如加载关卡、生成测试对象）。
3.  在事件结束时调用 `FinishPrepareTest` 节点。
4.  在 `StartTest` 事件中，执行具体的测试逻辑。
5.  在测试逻辑中，使用 `GetChildEditorWidgetByName` 获取一个按钮控件，然后使用其他编辑器工具库节点模拟操作或检查状态。
6.  使用 `ExpectTrue` 等节点来验证结果。
7.  测试完成后，调用 `FinishTest` 节点并传入结果（如 `EEditorUtilityTestResult::Succeeded`）。
8.  在自动化测试管理器中运行这个蓝图类对应的测试项。

## C++ 用法

### 头文件引入

```cpp
#include "EditorTestsUtilityLibrary.h"
#include "EditorUtilityTest.h"
```

### 基本用法

以下是一个基于 `UEditorUtilityTest` 创建简单测试类的示例。
*来源参考：`Source/EditorTests/Classes/EditorUtilityTest.h`*

```cpp
UCLASS()
class UMyEditorTest : public UEditorUtilityTest
{
    GENERATED_BODY()

protected:
    virtual void PrepareTest() override
    {
        // 测试准备工作
        UE_LOG(LogTemp, Log, TEXT("MyTest: Preparing..."));
        // 必须调用以通知框架准备完成
        FinishPrepareTest();
    }

    virtual void StartTest() override
    {
        UE_LOG(LogTemp, Log, TEXT("MyTest: Running..."));
        // 这里执行测试逻辑，例如使用编辑器工具函数
        UStaticMeshComponent* TestComp = /* 获取或创建一个测试组件 */;
        UEditorTestsUtilityLibrary::BakeMaterialsForComponent(TestComp, nullptr, nullptr);

        // 检查结果并报告
        if (/* 测试通过 */)
        {
            FinishTest(EEditorUtilityTestResult::Succeeded, TEXT("Bake succeeded."));
        }
        else
        {
            AddError(TEXT("Bake failed unexpectedly."));
            FinishTest(EEditorUtilityTestResult::Failed, TEXT("Bake failed."));
        }
    }
};
```

### 进阶用法

组合使用工具库函数进行更复杂的测试。
*来源参考：`Source/EditorTests/Public/EditorTestsUtilityLibrary.h`*

```cpp
void UMyAdvancedTest::StartTest()
{
    // 假设有一组静态网格组件
    TArray<UStaticMeshComponent*> ComponentsToMerge = /* 获取测试组件数组 */;

    // 配置合并设置
    FMeshMergingSettings MergeSettings;
    /* 配置 MergeSettings ... */

    // 执行合并操作
    TArray<int32> LODIndices;
    UEditorTestsUtilityLibrary::MergeStaticMeshComponents(ComponentsToMerge, MergeSettings, false, LODIndices);

    // 验证LOD索引是否符合预期
    if (LODIndices.Num() > 0 && /* 其他条件 */)
    {
        FinishTest(EEditorUtilityTestResult::Succeeded, TEXT("Merge operation completed as expected."));
    }
    else
    {
        AddError(FString::Printf(TEXT("LOD Indices count: %d"), LODIndices.Num()));
        FinishTest(EEditorUtilityTestResult::Failed, TEXT("Merge produced unexpected results."));
    }
}
```

## Demo 示例

一个最小的、可编译的 `EditorUtilityTest` 派生类。

**MySimpleTest.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "EditorUtilityTest.h"
#include "MySimpleTest.generated.h"

UCLASS()
class UMySimpleTest : public UEditorUtilityTest
{
    GENERATED_BODY()

public:
    UMySimpleTest();

protected:
    virtual void PrepareTest() override;
    virtual void StartTest() override;
};
```

**MySimpleTest.cpp**
```cpp
#include "MySimpleTest.h"
#include "EditorTestsUtilityLibrary.h"

UMySimpleTest::UMySimpleTest()
{
    Owner = TEXT("MyTeam");
    Description = TEXT("A simple demo test to verify the framework works.");
    TimeLimit = 30.0f;
}

void UMySimpleTest::PrepareTest()
{
    // 模拟一些准备工作，例如获取引用
    UE_LOG(LogTemp, Log, TEXT("MySimpleTest: PrepareTest called."));
    FinishPrepareTest();
}

void UMySimpleTest::StartTest()
{
    UE_LOG(LogTemp, Log, TEXT("MySimpleTest: StartTest called."));
    AddInfo(TEXT("Test is running..."));

    // 简单的逻辑断言
    const bool bSimpleCondition = (2 + 2 == 4);
    ExpectTrue(bSimpleCondition, TEXT("Basic math should hold true."));

    // 测试总是通过
    FinishTest(EEditorUtilityTestResult::Succeeded, TEXT("Demo test completed successfully."));
}
```

## 模块依赖

从 `EditorTests.Build.cs` 分析，使用者（编译时）需要依赖以下**特定**模块：

| 模块 | 用途 |
|---|---|
| `MeshMergeUtilities` | 提供网格体合并的核心工具函数。 |
| `MeshMerging` | 网格体合并功能的相关模块。 |
| `LevelEditor` | 访问关卡编辑器特定功能，常用于测试场景。 |
| `EditorScriptingUtilities` | 提供编辑器脚本和自动化相关的实用函数。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量转换为浮点数时产生警告的代码。 |
| 2026-05-12 | `847aba44` | Add support for JSON schema generation from fixed sized array properties. | 为固定大小数组属性添加了 JSON 模式生成支持。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移到 UE_LOGF。 |

### 维护评价

该插件创建于 2016 年，历史悠久。从 Git 历史看，它持续有更新，最新的提交记录在 2026 年 5 月，表明它仍在**活跃维护**中。这些更新主要是编译修复、代码清理和跟随引擎核心功能（如 JSON 工具）的演进。作为 Epic Games 内部维护的编辑器测试框架，它是引擎开发流程中不可或缺的一部分，稳定可靠。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/EditorTests)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/EditorTests/Source/EditorTests/Private/UnrealEd)