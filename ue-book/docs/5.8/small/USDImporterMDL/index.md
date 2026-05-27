# USD Importer MDL Integration

> Allows importing USD files that reference MDL files, via the USD Stage Actor and USD import

| 属性 | 值 |
|---|---|
| 中文名 | USD-MDL 材质导入 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `USDImporterMDL` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporterMDL) | |

## 用途

该插件是 USD 管线中专门处理 **MDL（Material Definition Language）材质翻译** 的模块。它从 USDImporter 中拆分而来，提供一个独立可禁用的插件来处理引用了 MDL 文件的 USD 资产。

核心功能是将 USD Stage 中使用 MDL schema 定义的材质（`UsdShadeMaterial`）转换为 Unreal Engine 可用的材质资产。它通过继承 `FMaterialXUsdShadeMaterialTranslator`（MaterialX 的 USD 材质翻译器），实现了 MDL 特定的材质创建逻辑。

**为什么独立出来？** MDL 材质管线依赖 NVIDIA 的 MDL SDK，属于可选功能。将其从核心 USDImporter 中分离，允许用户在不需要 MDL 支持时完全禁用该模块，避免引入额外依赖。

## 使用场景

- 你有一个使用 NVIDIA Omniverse 或其他 DCC 工具导出的 USD 文件，其中材质使用 MDL 定义 → 通过 USD Stage Actor 或 USD 导入流程自动转换这些材质
- 你的项目不需要 MDL 材质支持 → 禁用此插件即可，不会影响标准 MaterialX 或其他 USD 材质的导入
- 你需要在 Unreal 中保持与 Omniverse 生态系统的材质一致性 → 启用此插件确保 MDL 材质正确翻译

## 蓝图用法

该插件没有暴露任何蓝图可调用的 API。它是一个纯粹的 **编辑器管道模块**，通过 USD 导入流程在后台自动工作：

- 当通过 **USD Stage Actor** 加载包含 MDL 引用的 USD 文件时，自动触发 MDL 材质翻译
- 当通过 **文件导入**（Import）导入 USD 文件时，自动参与材质处理

### 使用方式

1. 启用插件（默认禁用）：`Edit > Plugins > USD Importer MDL Integration`
2. 确保依赖插件已启用：`USD Core`、`USD Importer`、`MDL Importer`
3. 正常使用 USD Stage Actor 或 USD 导入功能，MDL 材质将被自动翻译

## C++ 用法

该插件不提供面向使用者的 C++ API。其内部类仅供 USD 导入管线内部调用。

### 核心类

```cpp
// 引入头文件
#include "MDLUSDShadeMaterialTranslator.h"

// MDL USD 材质翻译器
// 继承自 FMaterialXUsdShadeMaterialTranslator
// 仅在 USE_USD_SDK && WITH_EDITOR 条件下可用
class FMdlUsdShadeMaterialTranslator : public FMaterialXUsdShadeMaterialTranslator
{
    // 使用父类构造函数
    using FMaterialXUsdShadeMaterialTranslator::FMaterialXUsdShadeMaterialTranslator;

    // 重写材质资产创建逻辑，处理 MDL 特有的材质转换
    virtual void CreateAssets() override;
};
```

### 日志分类

```cpp
#include "MDLUSDLog.h"

// 使用 MDL 专用日志分类输出调试信息
UE_LOG(LogUsdMdl, Log, TEXT("MDL material translation started"));
```

## Demo 示例

该插件没有可独立运行的示例代码。其功能完全集成在 USD 导入管线中，使用方式见"蓝图用法"章节。

## 模块依赖

该插件依赖以下 UE 插件（需同时启用）：

| 插件 | 用途 |
|---|---|
| `USDCore` | 提供 USD SDK 封装和核心运行时 |
| `USDImporter` | 提供 USD 资产导入管线和材质翻译基类（`FMaterialXUsdShadeMaterialTranslator`） |
| `MDLImporter` | 提供 MDL SDK 集成和 MDL 材质资产处理 |

无特殊模块依赖（仅标准 Editor 模块）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至新格式 |
| 2026-01-22 | `6bfebf62` | USD: Delete code that was deprecated up to and including in 5.5. | 清理 5.5 之前的废弃代码 |
| 2026-01-09 | `49c11077` | [UObject] | UObject 相关框架更新 |
| 2025-10-24 | `19dfa25d` | USD: Centralized and exposed a single function to check if the USD SDK is enabled in UnrealUSDWrappe | 统一 USD SDK 启用状态检查函数 |
| 2025-10-17 | `b322ef48` | [Backout] - CL47041219 | 回退某个变更 |

### 维护评价

- **创建时间**: 2025 年 3 月，非常年轻的插件
- **标记为 Beta**（`IsBetaVersion: true`）且默认禁用，表明该功能仍在验证阶段
- 近期更新均为框架级维护（日志迁移、废弃代码清理），非功能性变更
- 作为 USD 管线的可选扩展模块，由 Epic 核心 USD 团队维护
- **建议**: 目前适合测试和评估，生产环境使用需关注 Beta 状态。如果你的项目不涉及 MDL 材质，无需启用此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporterMDL)
- [USD Importer（父插件）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [MDL Importer（MDL 材质核心）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/MDLImporter)