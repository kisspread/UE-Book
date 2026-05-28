# USD Importer MDL integration

> Allows importing USD files that reference MDL files, via the USD Stage Actor and USD import

| 属性 | 值 |
|---|---|
| 中文名 | USD导入MDL集成 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `USDImporterMDL` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporterMDL) | |

## 用途

此插件为 UE5 的 USD 导入流程添加了对 **MDL (Material Definition Language)** 材质的支持。它的核心功能是充当 USD 资产与 Unreal 材质系统之间的“翻译器”。当导入一个包含 MDL 材质引用或定义的 USD 文件时，此插件中的专用翻译器 `FMdlUsdShadeMaterialTranslator` 会介入工作，将 USD 中描述的 MDL 材质信息（例如，通过 UsdShadeMaterial 和 UsdShadeShader 定义的材质图）解析并转换为 Unreal Engine 内部可识别的材质资产（UMaterialInterface）。这样，通过 USD Stage Actor 或标准 USD 导入流程引入的 3D 模型就能自动获得正确的材质表现。

该插件被设计为一个可独立启用/禁用的模块，它依赖并扩展了 `USDImporter` 和 `MDLImporter` 插件的功能。将其分离出来有助于模块化管理，并且允许用户根据项目需求选择性启用 MDL 支持。

## 使用场景

- 你在进行**建筑可视化（ArchViz）** 或**工业设计（如汽车、消费品）** 项目，需要导入由其他 DCC 工具（如 Omniverse, 3ds Max with V-Ray, Maya）导出的、包含 MDL 材质的 USD 文件。
- 你的美术或技术团队使用 **MDL 作为统一的材质描述语言**，并需要将这些资产无损地整合到 Unreal 项目中。
- 你希望利用 **USD Stage Actor** 进行非破坏性场景搭建，并需要场景中的资产能正确显示其原始的 MDL 材质。

## 蓝图用法

该插件主要在编辑器后台的 USD 导入流程中自动工作，**不直接暴露任何可供蓝图调用的函数或节点**。其作用通过标准的 USD 导入（Import）或 USD Stage Actor 的 Stage 来体现。当用户导入或更新一个引用了 MDL 材质的 USD 文件时，插件会自动触发材质转换。

## C++ 用法

### 头文件引入

该插件的核心类是 `FMdlUsdShadeMaterialTranslator`。你需要包含其头文件来与之交互或进行扩展。

```cpp
#include "MDLUSDShadeMaterialTranslator.h"
```

### 基本用法

`FMdlUsdShadeMaterialTranslator` 是一个 USD Shading 材质的翻译器。在 USD 导入流程中，系统会根据 USD 文件中的材质 schema 类型选择对应的翻译器。你通常不需要直接实例化或调用它，但可以了解其工作方式。

**来源文件:** `Engine/Plugins/Importers/USDImporterMDL/Source/USDImporterMDL/Public/MDLUSDShadeMaterialTranslator.h`

```cpp
// 此类继承自 MaterialX 翻译器，专注于处理 MDL 相关的材质数据
class FMdlUsdShadeMaterialTranslator : public FMaterialXUsdShadeMaterialTranslator
{
    using Super = FMaterialXUsdShadeMaterialTranslator;

public:
    // 使用父类的构造函数
    using FMaterialXUsdShadeMaterialTranslator::FMaterialXUsdShadeMaterialTranslator;

    // 核心方法：负责创建 UE 的材质资产。此插件在此方法中实现了 MDL 到 UE 材质的转换逻辑。
    virtual void CreateAssets() override;
};
```

### 进阶用法

1.  **日志记录**：插件定义了自己的日志分类 `LogUsdMdl`，用于输出与 MDL 材质翻译相关的调试信息。你可以在代码中使用它。
    **来源文件:** `Engine/Plugins/Importers/USDImporterMDL/Source/USDImporterMDL/Public/MDLUSDLog.h`

    ```cpp
    #include "MDLUSDLog.h"
    
    void SomeFunction()
    {
        UE_LOG(LogUsdMdl, Log, TEXT("Starting MDL material translation for asset: %s"), *AssetName);
    }
    ```

2.  **检查 USD SDK 状态**：根据最近的代码提交，存在一个集中式的函数来检查 USD SDK 是否在 Unreal 中启用。虽然此函数不在本插件内，但理解其存在有助于调试导入问题。相关的代码清理（删除5.5版本前已废弃的代码）也表明导入流程在不断优化。

## Demo 示例

由于这是一个内部翻译器插件，没有独立的运行时组件，因此没有可单独编译运行的最小示例。其功能通过标准的 UE5 USD 导入工作流进行验证和使用。

## 模块依赖

你的模块如果需要在代码层面与 USD/MDL 导入系统深度集成，可能需要依赖以下模块。请注意，该插件本身依赖于 `USDCore`、`USDImporter` 和 `MDLImporter` 这三个插件。

| 模块 | 用途 |
|---|---|
| `USDImporter` | 核心的 USD 导入框架，提供基础的翻译器接口和导入流程。 |
| `MDLImporter` | 提供底层的 MDL SDK 集成和材质解析功能。 |
| `USDClasses` | 提供 USD 相关的 UObject 类和数据结构。 |
| `MaterialX` | 用于处理 MaterialX 相关的数据，本插件的翻译器继承自此系统的翻译器。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏迁移至新的 UE_LOGF 宏。 |
| 2026-01-22 | `6bfebf62` | USD: Delete code that was deprecated up to and including in 5.5. | 清理掉在5.5及之前版本就已废弃的代码。 |
| 2026-01-09 | `49c11077` | [UObject] | 未提供具体信息，可能为通用引擎更新或重构。 |
| 2025-10-24 | `19dfa25d` | USD: Centralized and exposed a single function to check if the USD SDK is enabled in UnrealUSDWrapper. | 在底层包装器中集中并暴露了一个函数，用于检查USD SDK是否启用。 |
| 2025-10-17 | `b322ef48` | [Backout] - CL47041219 | 回滚了编号为CL47041219的变更。 |

### 维护评价

该插件**创建于 2025 年 3 月，年龄约 1 年**，目前仍处于 **Beta 测试阶段**，且默认未启用。从 Git 提交历史看，它在 2026 年初仍收到更新，包括代码清理和日志系统迁移，表明其作为 USD 工作流的一部分仍在**积极维护**中。最后一次功能性相关的提交（集中 USD SDK 检查函数）是 2025 年 10 月，之后主要是维护性更新。

**总结**：这是一个**功能明确、仍在活跃维护的 Beta 版本插件**。它解决了 USD 与 MDL 集成的一个具体需求。对于需要 MDL 支持的用户，建议启用并测试，但需留意其 Beta 状态可能带来的不稳定风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporterMDL)
- 官方文档：无
- 测试用例：未发现公开的专用测试文件。