# Interchange Tests

> Plugin for Interchange automation tests.

| 属性 | 值 |
|---|---|
| 中文名 | 交换测试 |
| 分类 | Testing |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeTestEditor` (Runtime), `InterchangeTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-02-20 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/InterchangeTests) | |

## 用途

这是一个专为 **Interchange 资产交换管线** 设计的自动化测试插件。它的核心作用不是向最终用户提供功能，而是作为 Epic 内部及开发者验证 Interchange 导入、导出及处理流程正确性的基础设施。通过该框架编写的测试用例，可以确保各种格式的资产（如静态网格、骨骼网格）在通过 Interchange 管线处理时行为符合预期，是保障引擎资产工作流稳定性的重要工具。

## 使用场景

- **引擎开发者**：在修改 Interchange 核心代码或导入器/导出器后，运行此插件内的测试以验证改动未引入回归问题。
- **大型项目团队**：为项目自定义的 Interchange 节点或处理逻辑编写自动化测试，确保资产流水线的长期可靠性。
- **插件/格式开发者**：在开发新的资产格式支持（如新的 FBX 版本或自定义格式）时，基于此框架验证导入/导出功能。

## 蓝图用法

此插件为纯测试框架，不提供可公开使用的 `BlueprintCallable` 节点或 `BlueprintReadWrite` 属性。其功能完全通过 C++ 自动化测试框架实现。

## C++ 用法

该插件的使用方式是基于其提供的测试基类和辅助工具，编写新的自动化测试用例。

### 头文件引入

```cpp
#include "InterchangeTestEditor.h" // 引入编辑器测试相关工具
#include "InterchangeTests.h"       // 引入核心测试框架和辅助函数
```

### 基本用法

典型用法是继承自插件提供的测试基类，并实现测试逻辑。

```cpp
// 示例：一个简单的资产导入测试 (概念性代码)
#include "Misc/AutomationTest.h"
#include "InterchangeTests.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FMyImportTest,
    "Project.Interchange.Import.StaticMesh",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter
)

bool FMyImportTest::RunTest(const FString& Parameters)
{
    // 使用 InterchangeTests 模块提供的辅助函数来设置测试环境
    // 例如：创建临时工作区、加载测试资产源文件
    FString TestAssetPath = TEXT("/Game/Tests/SampleMesh.fbx");
    
    // 执行 Interchange 导入流程
    // ... 具体的导入调用代码 ...
    
    // 验证导入结果
    UStaticMesh* ImportedMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Tests/ImportedMesh"));
    TestNotNull(TEXT("Imported mesh should exist"), ImportedMesh);
    
    // 进行更详细的检查（顶点数、材质槽等）
    // ...
    
    return true;
}
```

### 进阶用法

`InterchangeTestEditor` 模块可能提供更高级的编辑器集成测试工具，例如模拟整个编辑器内的导入对话框交互，或批量测试资产库。这些测试通常用于覆盖用户界面和更复杂的交互流程。

## Demo 示例

由于这是一个测试框架，其 “示例” 就是插件自身源码中已有的测试用例。开发者应参考 `Source/InterchangeTests/` 目录下的 `*.cpp` 文件，学习如何为不同类型的资产和流程编写测试。

## 模块依赖

要使用此测试框架编写新的测试，你的模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `InterchangeTests` | 核心测试框架、基类和通用测试辅助函数 |
| `InterchangeTestEditor` | 编辑器环境下的高级测试工具和流程 |
| `AutomationTest` | 提供 `IMPLEMENT_SIMPLE_AUTOMATION_TEST` 等自动化测试基础设施 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏至新接口。 |
| 2026-04-06 | `a3591f26` | [ContentBrowser] New Add Menu Interchange Menu | 为内容浏览器添加了新的Interchange菜单。 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introd | 废弃了旧的对象遍历函数，引入新接口。 |
| 2026-03-18 | `44060456` | Interchange - Added support for import containing both SM and SKM at the same time. | Interchange新增同时导入静态网格和骨骼网格的支持。 |
| 2026-03-04 | `7ceb4698` | Interchange - New Skeletal Mesh Combine Options | Interchange新增了骨骼网格合并选项。 |

### 维护评价

- **活跃维护**：从提交记录看，插件近期（2026年3-4月）仍有频繁更新，主要是功能增强和API迭代。
- **实验性状态**：`IsBetaVersion=true` 表明该插件处于Beta阶段，API和功能可能发生变化。
- **推荐用途**：作为**内部测试和开发验证工具**非常合格。虽然标记为Beta，但鉴于Epic对其Interchange管线的重视，此测试框架会持续维护。不建议在最终产品中直接依赖其实验性API，但可放心使用其测试用例来验证自定义Interchange流程。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/InterchangeTests)
- 测试用例位于插件内部的 `Source/InterchangeTests/` 目录下。