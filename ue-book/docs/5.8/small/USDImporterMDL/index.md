# USD Importer MDL integration

> Allows importing USD files that reference MDL files, via the USD Stage Actor and USD import

| 属性 | 值 |
|---|---|
| 中文名 | USD MDL材质集成 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `USDImporterMDL` (Editor) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2025-03-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporterMDL) | |

## 用途

这个插件的核心功能是将 **MDL 材质** 在 **USD (Universal Scene Description)** 工作流中的集成能力进行**模块化和独立化**。它并非提供全新的导入功能，而是将原本集成在 `USDImporter` 插件中负责处理 MDL 材质的翻译逻辑抽取到一个独立的插件中。

其存在的价值在于：
1.  **模块化管理**：允许用户根据项目需求，单独启用或禁用 MDL 材质的导入支持。如果项目不使用 MDL 材质，禁用此插件可以减少潜在的加载开销和依赖。
2.  **代码解耦**：作为 `MDLImporter` 插件在 USD 工作流中的适配层，它实现了 `FMaterialXUsdShadeMaterialTranslator` 的特定子类 `FMdlUsdShadeMaterialTranslator`，专注于处理 USD 着色网络中与 MDL 相关的部分。
3.  **清理依赖**：将特定材质系统的逻辑从通用 USD 导入器中分离，使 `USDImporter` 本身更专注于通用的 USD 场景解析，符合单一职责原则。

## 使用场景

当你需要处理以下工作流时，应启用此插件：
- 你的项目需要导入包含 MDL 材质定义（`.mdl` 文件引用）的 USD 文件。
- 你使用的数字内容创作 (DCC) 工具（如 Houdini, Maya 等）导出了采用 MDL 材质标准的 USD 资产。
- 你希望利用 USD Stage Actor 在编辑器中动态加载并正确显示这些引用了 MDL 材质的 USD 资产。

如果你的项目不使用 MDL 材质系统，或使用的是其他材质标准（如 MaterialX、UsdPreviewSurface），则可以安全地禁用此插件。

## 蓝图用法

此插件主要作为编辑器后台功能运行，通过标准的 USD 导入流程（文件导入或 USD Stage Actor）自动激活。它**不直接暴露任何蓝图节点**。材质的转换是通过内部的 `FMdlUsdShadeMaterialTranslator` 自动处理的。

## C++ 用法

### 头文件引入

要使用或扩展此插件提供的翻译器，你需要引入相关头文件。

```cpp
#include "MDLUSDShadeMaterialTranslator.h"
```

### 基本用法

此插件的核心是 `FMdlUsdShadeMaterialTranslator` 类，它继承自 `FMaterialXUsdShadeMaterialTranslator`。其主要作用是重写 `CreateAssets()` 方法，为使用了 MDL 材质的 USD 着色网络创建对应的 Unreal 材质资产。

在代码中，你通常不会直接实例化这个类，它是由 USD 导入框架在需要时自动创建的。但如果你需要自定义 MDL 材质在 USD 中的导入行为，可以继承并覆盖它。

**示例：一个简化的自定义翻译器** (概念代码，非直接来自测试用例)
```cpp
// MyCustomMdlTranslator.h
#pragma once
#include "MDLUSDShadeMaterialTranslator.h"

class FMyCustomMdlTranslator : public FMdlUsdShadeMaterialTranslator
{
public:
    using FMdlUsdShadeMaterialTranslator::FMdlUsdShadeMaterialTranslator;

    // 重写创建资产的方法，添加自定义逻辑
    virtual void CreateAssets() override
    {
        // 调用父类或默认实现
        Super::CreateAssets();

        // 添加额外的自定义材质参数设置或后处理逻辑
        // ...
    }
};
```

### 进阶用法

插件通过 `LogUsdMdl` 日志分类输出调试信息，这对于排查 MDL 材质导入问题非常有用。你可以在代码中使用它。

**示例：添加日志输出**
```cpp
#include "MDLUSDLog.h"

void SomeFunction()
{
    UE_LOG(LogUsdMdl, Log, TEXT("MDL Material translation process started."));
    // ... 处理MDL材质
    UE_LOG(LogUsdMdl, Warning, TEXT("Unsupported MDL function encountered: %s"), *UnsupportedFunctionName);
}
```

## Demo 示例

以下是一个假设的、展示如何在此插件框架下工作的最小示例。请注意，实际使用时翻译器是被 USD 导入流程调用的。

**MyMDLHelper.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "MDLUSDShadeMaterialTranslator.h"

class FMyMDLHelper
{
public:
    // 模拟一个可能调用翻译器的流程
    static void ProcessMdlMaterialImport()
    {
        // 在实际USD导入中，UsdUtils 会根据材质类型创建合适的翻译器
        // 这里仅为演示目的
        FMyMDLHelper Helper;
        Helper.Translator->CreateAssets();
    }

private:
    // 持有一个翻译器实例 (实际生命周期由导入框架管理)
    TUniquePtr<FMdlUsdShadeMaterialTranslator> Translator;
};
```

**MyMDLHelper.cpp**
```cpp
#include "MyMDLHelper.h"
#include "MDLUSDLog.h"

// ... 其他包含

void FMyMDLHelper::ProcessMdlMaterialImport()
{
    UE_LOG(LogUsdMdl, Log, TEXT("Helper: Starting MDL material processing."));
    // 实际的 Translator 会在 USD 导入流程的适当阶段被初始化和调用
    if (Translator.IsValid())
    {
        Translator->CreateAssets();
    }
    else
    {
        UE_LOG(LogUsdMdl, Error, TEXT("Helper: Translator is not initialized."));
    }
}
```

## 模块依赖

要使用此插件的功能，你的模块（`Build.cs`）需要添加对以下模块的依赖。这些依赖主要来自其父插件 `USDImporter` 和 `MDLImporter`。

| 模块 | 用途 |
|---|---|
| `MDLImporter` | MDL 材质的核心导入和处理库，提供材质创建的基本能力。 |
| `USDImporter` | USD 文件解析和资产导入的主框架，本插件是其扩展。 |
| `USDCore` | USD 相关的基础类型和工具库。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏 UE_LOG 迁移为新的 UE_LOGF 宏，属于日志系统升级。 |
| 2026-01-22 | `6bfebf62` | USD: Delete code that was deprecated up to and including in 5.5. | 清理在 UE 5.5 及之前版本已标记为废弃的旧代码。 |
| 2026-01-09 | `49c11077` | [UObject] | 提交信息不完整，可能与 UObject 系统相关的内部调整有关。 |
| 2025-10-24 | `19dfa25d` | USD: Centralized and exposed a single function to check if the USD SDK is enabled in UnrealUSDWrapper. | 集中并公开了一个检查 USD SDK 是否启用的函数，优化了代码结构。 |
| 2025-10-17 | `b322ef48` | [Backout] - CL47041219 | 回滚了编号为 CL47041219 的更改。 |

### 维护评价

- **活跃度**：插件创建于 2025 年初，最近一次更新（日志迁移）在 2026 年 4 月，间隔约 6 个月。更新主要集中在**代码维护和清理**（如废弃代码删除、日志宏迁移），而非重大功能变更。这表明该插件功能已相对稳定，处于被动维护状态。
- **状态**：插件标记为 **实验性 (`IsBetaVersion: true`)** 且**默认不启用 (`EnabledByDefault: false`)**。这意味着 Epic 官方可能尚未将其视为完全稳定的生产级功能，用户需要自行评估风险并手动启用。
- **推荐度**：如果你的项目**确实需要**导入包含 MDL 材质的 USD 文件，那么**必须启用**此插件。否则，由于其模块化设计，不使用则无需启用。考虑到其创建时间较短且标记为实验性，在关键生产环境中使用前建议进行充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporterMDL)
- 官方文档（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporterMDL/Tests)（推测路径，根据UE惯例，Tests通常在插件目录下）