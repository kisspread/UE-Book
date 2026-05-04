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

NNEModelTests 是 Unreal Engine 神经网络引擎（NNE）的**测试基础设施插件**。它解决的核心问题是：如何在 UE 的自动化测试框架中，系统性地导入和运行神经网络模型测试，并确保这些测试能在不同的 NNE 运行时后端上正确执行。

该插件本身不包含神经网络推理逻辑，而是提供：
- **模型文件导入工厂**：将 ONNX 等神经网络模型文件导入为 UE 资产
- **测试数据导入工厂**：将模型测试所需的输入/输出数据文件导入为资产
- **自动化测试基础设施**：为不同 NNE 运行时（如 ONNX Runtime、NNAPI 等）提供统一的测试框架

这是 NNE 插件生态中的质量保证组件，主要用于 Epic 内部 CI 和开发者验证 NNE 运行时的正确性。

## 使用场景

- 你正在开发或集成一个新的 NNE 运行时后端 → 用 NNEModelTests 验证你的运行时实现是否正确
- 你需要为 NNE 系统编写自动化回归测试 → 用此插件的测试基础设施
- 你需要在编辑器中导入神经网络模型文件用于测试 → 用 NNEModelTestsFactory
- 你需要导入模型的测试输入/输出数据（如 .npy 文件）→ 用 NNEModelTestsDataFactory

## 蓝图用法

本插件主要面向 C++ 自动化测试，不提供蓝图可调用的 API。两个工厂类（`UNNEModelTestsFactory` 和 `UNNEModelTestsDataFactory`）是编辑器工厂，通过拖拽文件到内容浏览器自动触发，无需蓝图调用。

## C++ 用法

### 头文件引入

```cpp
#include "NNEModelTestsFactory.h"
```

### 基本用法：模型文件导入工厂

`UNNEModelTestsFactory` 负责导入神经网络模型文件（如 `.onnx`），并支持重新导入（Reimport）。

```cpp
// 工厂自动注册，当用户将支持的模型文件拖入内容浏览器时自动触发
// FactoryCanImport() 判断文件扩展名是否支持
// FactoryCreateFile() 执行实际导入逻辑

// 重新导入支持：
// CanReimport() - 检查对象是否支持重新导入
// SetReimportPaths() - 设置重新导入的文件路径
// Reimport() - 执行重新导入
```

### 基本用法：测试数据导入工厂

`UNNEModelTestsDataFactory` 负责导入模型测试数据文件（如输入张量、期望输出张量等）。

```cpp
// 同样通过拖拽文件自动触发
// FactoryCanImport() 判断文件扩展名是否支持
// FactoryCreateFile() 将测试数据文件导入为 UE 资产
```

### 进阶用法：自定义测试运行时

NNEModelTests 的 Runtime 模块提供了测试基础设施，用于在不同 NNE 运行时上运行模型测试。典型的测试模式如下：

```cpp
// 测试模式：对每个注册的 NNE 运行时，导入模型并验证推理结果
// 1. 通过工厂导入模型资产
// 2. 通过工厂导入测试数据（输入/期望输出）
// 3. 在目标运行时上执行推理
// 4. 比较推理输出与期望输出
```

## Demo 示例

```cpp
// NNEModelTestsEditorModule.h
// 本插件的编辑器模块入口，注册工厂类

#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FNNEModelTestsEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// NNEModelTestsEditorModule.cpp
#include "NNEModelTestsEditorModule.h"

void FNNEModelTestsEditorModule::StartupModule()
{
    // 注册模型文件和测试数据的导入工厂
    // UFactory 子类通过 UCLASS() 宏自动注册到编辑器
}

void FNNEModelTestsEditorModule::ShutdownModule()
{
    // 清理资源
}

IMPLEMENT_MODULE(FNNEModelTestsEditorModule, NNEModelTestsEditor)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NNE` | 神经网络引擎核心模块，提供运行时抽象和模型管理 |
| `EditorReimportHandler` | 编辑器重新导入支持（NNEModelTestsEditor 模块） |

## 维护状态

### 近期更新

由于该插件创建日期较新（2026-03-30），且为实验性插件，暂无足够的 git 历史记录可供分析。

### 维护评价

- **实验性插件**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，表明此插件仍处于早期开发阶段
- **测试专用**：作为 NNE 生态的测试基础设施，主要服务于 Epic 内部开发和 CI 流程
- **依赖 NNE 主插件**：需要 NNE 核心插件才能正常工作
- **不建议生产使用**：此插件仅用于测试目的，不包含面向最终用户的推理功能
- **推荐使用场景**：仅在开发 NNE 运行时后端或需要验证 NNE 功能正确性时使用

⚠️ **注意**：此插件为实验性插件，API 和功能可能在后续版本中发生重大变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNE/NNEModelTests)
- [官方文档](https://dev.epicgames.com/community/learning/courses/e7w/unreal-engine-neural-network-engine-nne)
- [支持论坛](https://forums.unrealengine.com/t/course-neural-network-engine-nne/1162628)