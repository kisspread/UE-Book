# NNE Model Tests

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
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNE/NNEModelTests) | |

## 用途

NNEModelTests 是 NNE（Neural Network Engine，神经网络引擎）的**测试基础设施插件**。它解决的核心问题是：如何在 UE5 的自动化测试框架中，系统性地验证不同 NNE 运行时（Runtime）对神经网络模型的推理正确性。

具体来说，这个插件提供了一套从 JSON 配置文件导入测试用例的机制，每个测试用例包含：
- 模型文件路径
- 输入张量的形状和数据类型
- 期望输出
- 多个运行时环境配置（接口类型、运行时名称、误差容忍度）
- 平台/硬件需求（如 NPU、NNE Shader 支持）

插件会根据当前运行环境自动过滤不适用的测试，然后在所有可用的 NNE 运行时上执行模型推理并验证结果。这是 NNE 引擎质量保证的核心组件。

## 使用场景

- 你是 NNE 运行时开发者 → 用此插件验证你的运行时实现对标准模型的推理正确性
- 你在开发自定义神经网络推理后端 → 用此插件进行回归测试，确保不同版本间行为一致
- 你需要在 CI/CD 中自动化测试 NNE 模型推理 → 用此插件的 `RunModelTests` 接口集成到测试流水线
- 你需要跨平台验证模型推理（CPU/GPU/NPU）→ 用此插件的平台过滤和多运行时支持

## 蓝图用法

此插件主要面向 C++ 自动化测试场景，蓝图暴露的 API 较少。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `InitializeFromFile` | 从 JSON 文件加载测试配置 | `UNNEModelTests` |
| `GetFilteredModelTestParameters` | 获取过滤后的测试参数列表 | `UNNEModelTests` |
| `InitializeFromFile` | 从文件加载测试数据（对齐内存） | `UNNEModelTestData` |
| `GetData` | 获取已加载的测试数据 | `UNNEModelTestData` |

### 使用示例（蓝图描述）

由于此插件主要用于自动化测试框架，典型使用方式是在 C++ 测试代码中调用。蓝图中可使用 `UNNEModelTests` 和 `UNNEModelTestData` 对象加载测试配置和数据，但实际测试执行逻辑通常在自动化测试宏中完成。

## C++ 用法

### 头文件引入

```cpp
#include "NNEModelTests.h"
#include "NNEModelTestsModule.h"
```

### 基本用法

加载并运行模型测试：

```cpp
// 获取 NNEModelTests 模块
FNNEModelTestsModule& Module = FModuleManager::GetModuleChecked<FNNEModelTestsModule>("NNEModelTests");

// 运行所有已加载的模型测试
int32 NumSuccesses = 0;
int32 NumSkipped = 0;
int32 Total = 0;
Module.RunModelTests(NumSuccesses, NumSkipped, Total);

// 检查结果
UE_LOG(LogNNEModelTests, Log, TEXT("Tests: %d passed, %d skipped, %d total"), NumSuccesses, NumSkipped, Total);
```

### 进阶用法

手动加载测试配置并过滤特定运行时：

```cpp
// 创建测试对象
UNNEModelTests* ModelTests = NewObject<UNNEModelTests>();

// 准备额外文件映射和运行时过滤器
TMap<FString, TArray<FString>> AdditionalFiles;
TMap<FString, TSet<FString>> RuntimeFilters;

// 从 JSON 文件初始化
FString TestConfigPath = TEXT("/Game/Tests/MyModelTest.json");
bool bSuccess = ModelTests->InitializeFromFile(TestConfigPath, AdditionalFiles, RuntimeFilters);

if (bSuccess)
{
    // 获取过滤后的测试参数
    TArray<UE::NNEModelTests::FModelTestParameters> TestParameters;
    ModelTests->GetFilteredModelTestParameters(TestParameters);

    // 遍历测试参数
    for (const auto& Params : TestParameters)
    {
        UE_LOG(LogNNEModelTests, Log, TEXT("Test: %s, Model: %s"), *Params.TestName, *Params.ModelPath);

        for (const auto& Input : Params.Inputs)
        {
            UE_LOG(LogNNEModelTests, Log, TEXT("  Input: Path=%s, Type=%s"), *Input.Path, *Input.Type);
        }

        for (const auto& Runtime : Params.Runtimes)
        {
            UE_LOG(LogNNEModelTests, Log, TEXT("  Runtime: %s (Interface: %s, AbsErr: %f, RelErr: %f)"),
                *Runtime.RuntimeName, *Runtime.Interface, Runtime.AbsoluteError, Runtime.RelativeError);
        }
    }
}
```

加载测试数据文件：

```cpp
UNNEModelTestData* TestData = NewObject<UNNEModelTestData>();
FString DataFilePath = TEXT("/Game/Tests/InputData.bin");

if (TestData->InitializeFromFile(DataFilePath))
{
    TConstArrayView64<uint8> Data = TestData->GetData();
    UE_LOG(LogNNEModelTests, Log, TEXT("Loaded %llu bytes of test data"), Data.Num());
}
```

## Demo 示例

### NNEModelTestRunner.h

```cpp
#pragma once

#include "CoreMinimal.h"

class FNNEModelTestRunner
{
public:
    /** 加载指定目录下的所有模型测试并执行 */
    static bool RunAllTestsInDirectory(const FString& Directory);

    /** 执行单个测试配置文件 */
    static bool RunTestFromFile(const FString& ConfigFilePath);

private:
    static void LogTestResults(int32 NumSuccesses, int32 NumSkipped, int32 Total);
};
```

### NNEModelTestRunner.cpp

```cpp
#include "NNEModelTestRunner.h"
#include "NNEModelTests.h"
#include "NNEModelTestsModule.h"
#include "Modules/ModuleManager.h"

bool FNNEModelTestRunner::RunAllTestsInDirectory(const FString& Directory)
{
    FNNEModelTestsModule* Module = FModuleManager::GetModulePtr<FNNEModelTestsModule>("NNEModelTests");
    if (!Module)
    {
        UE_LOG(LogTemp, Error, TEXT("NNEModelTests module not loaded"));
        return false;
    }

    int32 NumSuccesses = 0;
    int32 NumSkipped = 0;
    int32 Total = 0;

    Module->RunModelTests(NumSuccesses, NumSkipped, Total);
    LogTestResults(NumSuccesses, NumSkipped, Total);

    return NumSuccesses == Total - NumSkipped;
}

bool FNNEModelTestRunner::RunTestFromFile(const FString& ConfigFilePath)
{
    UNNEModelTests* ModelTests = NewObject<UNNEModelTests>();
    TMap<FString, TArray<FString>> AdditionalFiles;
    TMap<FString, TSet<FString>> RuntimeFilters;

    if (!ModelTests->InitializeFromFile(ConfigFilePath, AdditionalFiles, RuntimeFilters))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load test config: %s"), *ConfigFilePath);
        return false;
    }

    TArray<UE::NNEModelTests::FModelTestParameters> TestParameters;
    if (!ModelTests->GetFilteredModelTestParameters(TestParameters))
    {
        UE_LOG(LogTemp, Warning, TEXT("No valid test parameters after filtering"));
        return false;
    }

    UE_LOG(LogTemp, Log, TEXT("Loaded %d test configurations"), TestParameters.Num());
    return true;
}

void FNNEModelTestRunner::LogTestResults(int32 NumSuccesses, int32 NumSkipped, int32 Total)
{
    UE_LOG(LogTemp, Log, TEXT("NNE Model Tests: %d/%d passed, %d skipped"),
        NumSuccesses, Total, NumSkipped);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NNE` | NNE 核心引擎模块，提供神经网络推理接口 |
| `Json` | JSON 序列化支持，用于解析测试配置文件 |

## 维护状态

### 近期更新

- 2026-04-14 `35e60df1` Migrate UE_LOG to UE_LOGF.
- 2026-03-30 `6ab5ee4d` [NNE] NNEModelTests to experimental.

### 维护评价

- **实验性状态**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，表明此插件仍在积极开发中
- **创建时间**：2026-03-30，非常新的插件
- **代码质量**：结构清晰，JSON 序列化使用 UE 标准宏，内存对齐处理专业
- **功能完整性**：提供完整的测试生命周期管理（加载、过滤、执行）
- **推荐使用**：适合 NNE 运行时开发者和需要自动化测试神经网络推理的项目，但需注意实验性状态可能带来 API 变更

⚠️ **注意**：此插件为实验性功能，API 可能在未来版本中发生变化。建议在生产环境中谨慎使用，并关注官方更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNE/NNEModelTests)
- [官方文档](https://dev.epicgames.com/community/learning/courses/e7w/unreal-engine-neural-network-engine-nne)
- [支持论坛](https://forums.unrealengine.com/t/course-neural-network-engine-nne/1162628)