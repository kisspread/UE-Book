# NNEModelTests

> Infrastructure to import and add neural network model tests to automation tests that run on different NNE runtimes.

| 属性 | 值 |
|---|---|
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNEModelTests` (Runtime), `NNEModelTestsEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-30 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNE/NNEModelTests) | |

## 用途

NNEModelTests 是一个为 Unreal Engine 的神经网络引擎（NNE）提供测试基础设施的插件。它并非面向最终用户的功能插件，而是为 NNE 开发者和贡献者设计的工具。其核心目的是提供一套标准化的框架，用于导入神经网络模型，并将其作为自动化测试用例，在不同的 NNE 后端运行时（如 ONNX Runtime、TensorRT 等）上执行，以验证模型兼容性、推理正确性和性能基准。

## 使用场景

- **NNE 运行时开发者**：在开发或适配一个新的 NNE 后端（Runtime）时，使用此插件快速集成并运行一套标准的模型测试，确保新后端符合预期。
- **NNE 核心开发者**：在修改 NNE 核心框架或 API 后，运行此插件提供的测试套件，进行回归测试，确保改动没有破坏现有功能。
- **机器学习工程师**：在将训练好的模型集成到 UE 项目前，使用此框架验证模型在目标平台和运行时上的表现。

## 蓝图用法

此插件主要提供测试基础设施和编辑器工具，不包含面向游戏逻辑的公开蓝图节点。其功能主要通过自动化测试框架和编辑器操作来使用。

## C++ 用法

此插件的 API 主要服务于测试框架，而非最终用户的游戏逻辑。其核心用法体现在编写和组织自动化测试用例中。

### 头文件引入

```cpp
#include "NNEModelTests.h"
// 或
#include "NNEModelTestsEditor.h"
```

### 基本用法

该插件的核心是提供模型导入和测试用例注册的框架。开发者通常需要继承或使用其提供的基类来创建针对特定模型的测试。

```cpp
// 示例：定义一个继承自插件提供的测试基类的自定义测试
// 来源：基于插件结构推断的典型用法
class FMyModelTest : public FNNEModelTestBase
{
public:
    FMyModelTest() : FNNEModelTestBase(TEXT("MyModelTest")) {}

    virtual void GetTests(TArray<FString>& OutBeautifiedNames, TArray<FString>& OutTestCommands) const override
    {
        // 注册要测试的模型文件路径
        OutBeautifiedNames.Add(TEXT("MyModel.onnx"));
        OutTestCommands.Add(TEXT("Path/To/MyModel.onnx"));
    }

    virtual bool RunTest(const FString& Parameters) override
    {
        // 加载模型，创建推理实例，运行测试并验证结果
        // ... 具体测试逻辑
        return true;
    }
};
```

### 进阶用法

结合 `NNEModelTestsEditor` 模块，可以在编辑器中管理测试模型资产，并通过编辑器菜单或命令行触发测试套件的运行。

## Demo 示例

此插件本身即为测试框架，其“Demo”就是它所包含的测试用例。开发者应参考插件源码中已有的测试实现来学习如何为自己的模型编写测试。

## 模块依赖

从插件的性质推断，其模块必然依赖 NNE 核心模块。具体依赖需查看各模块的 `Build.cs` 文件。

| 模块 | 用途 |
|---|---|
| `NNE` | 神经网络引擎核心模块，提供模型加载、运行时抽象等基础功能。 |
| `NNEUtils` | NNE 工具模块，可能提供模型导入、数据转换等辅助功能。 |

## 维护状态

### 近期更新

- 2026-04-14 `35e60df1` 将UE_LOG迁移至UE_LOGF日志宏。
- 2026-03-30 `6ab5ee4d` 将NNEModelTests插件标记为实验性状态。

### 维护评价

该插件目前处于实验性阶段。近期提交均为维护性工作，表明开发团队仍在关注，但未进入积极的功能开发期。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNE/NNEModelTests)
- [官方文档](https://dev.epicgames.com/community/learning/courses/e7w/unreal-engine-neural-network-engine-nne)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNE/NNEModelTests/Tests)