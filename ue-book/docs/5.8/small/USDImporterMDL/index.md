# USD Importer MDL integration

> Allows importing USD files that reference MDL files, via the USD Stage Actor and USD import

| 属性 | 值 |
|---|---|
| 中文名 | USD MDL材质导入 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `USDImporterMDL` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporterMDL) | |

## 用途

该插件是主 USD 导入插件 (`USDImporter`) 和 MDL 材质导入插件 (`MDLImporter`) 之间的桥梁。它存在的主要目的是将 MDL（Material Definition Language）材质的翻译逻辑从核心 USD 导入功能中分离出来，使其成为一个独立的、可选的模块。

**解决的问题**：
当导入的 USD 文件内部引用了 MDL 材质定义时，UE 需要能够理解并转换这些材质。此插件提供了 `FMdlUsdShadeMaterialTranslator`，该类扩展了基础的 `FMaterialXUsdShadeMaterialTranslator`，专门用于处理 MDL 材质到 UE 材质系统的转换。通过将它独立成插件，实现了：
1.  **模块化**：用户可以根据需要启用或禁用 MDL 支持，而不影响核心的 USD 导入功能。
2.  **关注点分离**：将特定于 MDL 的代码与通用的 USD 处理逻辑解耦，便于维护和扩展。
3.  **按需加载**：仅当项目需要 MDL 材质支持时才加载此插件，有助于减少编辑器的初始内存占用。

## 使用场景

-   **场景一**：你正在从支持 MDL 材质的 3D 软件（如 Omniverse）导出 USD 文件，并将其导入到 Unreal Engine 中。你需要确保 USD 文件中引用的 MDL 材质被正确解析和转换，以便在 UE 中正确显示。
-   **场景二**：你的团队正在进行项目迁移或资产整合，资产管线中大量使用了基于 MDL 的材质库。你需要通过 USD Stage Actor 或资产导入流程将这些资产无缝带入 UE。
-   **场景三**：你正在开发一个自定义的 USD 工作流，并且需要确保 MDL 材质翻译环节是可插拔和可配置的。

## 蓝图用法

此插件主要提供底层的 C++ 翻译器类，并未公开额外的 `BlueprintCallable` 节点。其功能在以下情况下自动生效：

-   当通过 **USD Stage Actor** 加载一个引用了 MDL 材质的 USD 文件时。
-   当使用 **UE 的标准资产导入** 功能（例如拖拽 .usd 文件到 Content Browser）导入包含 MDL 材质引用的 USD 文件时。

你无需在蓝图中主动调用任何函数，只要插件被正确启用，材质转换就会在后台自动完成。

## C++ 用法

此插件的核心是一个材质翻译器类，它扩展了 USD 导入流程中的材质处理管线。

### 头文件引入

```cpp
// 包含 MDL 翻译器的头文件
#include "MDLUSDShadeMaterialTranslator.h"

// 包含基础材质翻译器（通常在父类中使用）
#include "USDMaterialTranslator.h" // 路径可能因版本而异，来自 USDImporter 模块
```

### 基本用法

该插件的类 `FMdlUsdShadeMaterialTranslator` 主要通过继承被自动集成到翻译管线中。它的存在就是一种“用法”。

作为开发者，你通常**不需要直接实例化**这个类。USD 导入框架会在遇到 MDL 材质时，根据已注册的翻译器，自动使用 `FMdlUsdShadeMaterialTranslator` 来处理。

如果你需要自定义 MDL 材质的导入行为（例如，对特定类型的 MDL 节点应用特殊处理），你可能会创建一个继承自此翻译器的子类，并注册它。但这是高级用法。

### 进阶用法：自定义翻译器

虽然插件本身不提供注册接口，但你可以参考其模式，创建自己的材质翻译器来处理其他类型的材质定义。核心思路是：

```cpp
// 假设你创建了一个自定义的材质翻译器
class FMyCustomMaterialTranslator : public FMaterialXUsdShadeMaterialTranslator
{
public:
    using FMaterialXUsdShadeMaterialTranslator::FMaterialXUsdShadeMaterialTranslator;

    // 重写 CreateAssets 方法来实现自定义逻辑
    virtual void CreateAssets() override
    {
        // 1. 检查材质输入是否匹配你的条件
        if (bShouldHandleThisMaterial)
        {
            // 2. 执行你自定义的材质创建或转换逻辑
            CreateMySpecialMaterial();
        }
        else
        {
            // 3. 如果不处理，调用父类的默认逻辑
            Super::CreateAssets();
        }
    }
};

// 在适当的时机（例如模块启动时）注册你的翻译器
// 具体的注册方式取决于 UE 版本和 USD 导入框架的接口
// 通常类似于：FUSDTranslationManager::Get()->RegisterMaterialTranslator<FMyCustomMaterialTranslator>();
```

`FMdlUsdShadeMaterialTranslator` 就是 Epic 官方实现的一个这样的“自定义”翻译器。

## Demo 示例

以下是一个可编译的最小示例，展示了如何创建一个继承自 `FMdlUsdShadeMaterialTranslator` 的子类，以在其基础上添加自定义日志。这个例子说明了如何扩展此插件的功能。

**MyCustomMdlTranslator.h**
```cpp
// MyCustomMdlTranslator.h
#pragma once

#include "MDLUSDShadeMaterialTranslator.h"

class FMyCustomMdlTranslator : public FMdlUsdShadeMaterialTranslator
{
    using Super = FMdlUsdShadeMaterialTranslator;

public:
    using Super::Super; // 继承构造函数

    virtual void CreateAssets() override;
};
```

**MyCustomMdlTranslator.cpp**
```cpp
// MyCustomMdlTranslator.cpp
#include "MyCustomMdlTranslator.h"

#include "MDLUSDLog.h" // 使用本插件定义的日志类别

void FMyCustomMdlTranslator::CreateAssets()
{
    UE_LOG(LogUsdMdl, Log, TEXT("Custom MDL Translator: Starting asset creation for MaterialX graph with %d nodes."), /* 从某处获取节点数 */ 0);

    // 调用父类（MDL翻译器）的实现，完成实际的MDL材质转换
    Super::CreateAssets();

    UE_LOG(LogUsdMdl, Log, TEXT("Custom MDL Translator: Finished asset creation."));
}
```

**说明**：
-   这个自定义翻译器首先输出一条带时间戳的日志。
-   然后调用父类 `FMdlUsdShadeMaterialTranslator::CreateAssets()` 来执行 MDL 材质转换的核心逻辑。
-   最后再输出一条完成日志。
-   **注意**：要让这个自定义翻译器生效，你需要在某个合适的地方（例如，在你的项目模块或另一个插件中）向 USD 翻译管理器注册它，这超出了本插件本身的范围。

## 模块依赖

要使用此插件，你的项目需要依赖以下插件和模块：

| 依赖 | 用途 |
|---|---|
| `USDCore` | 提供 USD SDK 的基础封装和运行时。 |
| `USDImporter` | 提供核心的 USD 资产导入功能和基础的材质翻译框架。 |
| `MDLImporter` | 提供 MDL 材质解析、编译和 UE 材质生成的核心功能。 |

此插件 (`USDImporterMDL`) 本身是一个 `Editor` 模块，这意味着它主要在编辑器环境下工作（用于导入资产）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 `UE_LOG` 宏迁移到新的 `UE_LOGF` 宏，属于日志系统现代化更新。 |
| 2026-01-22 | `6bfebf62` | USD: Delete code that was deprecated up to and including in 5.5. | 清理了在 UE 5.5 版本之前就已弃用的代码，保持代码库整洁。 |
| 2026-01-09 | `49c11077` | [UObject] | 通用的 UObject 相关改动，可能涉及序列化或反射系统调整。 |
| 2025-10-24 | `19dfa25d` | USD: Centralized and exposed a single function to check if the USD SDK is enabled in UnrealUSDWrappe | 重构了 USD SDK 的可用性检查，将其集中并暴露为一个统一的函数，提高了代码可维护性。 |
| 2025-10-17 | `b322ef48` | [Backout] - CL47041219 | 回滚了之前的某个改动（CL47041219），可能因为引入了问题。 |

### 维护评价

-   **活跃度**：该插件仍在维护中，最近的更新发生在 2026 年 4 月。更新内容主要为代码现代化和清理，属于常规维护，而非重大功能变更。
-   **状态**：`.uplugin` 明确标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`，这表明它被视为**实验性功能**。Epic 可能还在评估其稳定性和 API 设计。
-   **风险**：作为实验性插件，其 API 和行为在未来版本中可能会发生不兼容的改变。
-   **推荐**：**谨慎使用**。如果你的项目**必须**导入包含 MDL 材质的 USD 文件，并且没有其他替代方案，那么可以启用此插件。但需要意识到它是测试性的，并在 UE 版本升级时密切关注其变更日志。对于不涉及 MDL 材质的 USD 工作流，则无需启用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporterMDL)
-   官方文档：暂无
-   测试用例：暂无