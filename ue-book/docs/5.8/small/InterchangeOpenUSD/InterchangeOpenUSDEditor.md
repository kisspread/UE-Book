# Interchange OpenUSD

> Allows translation of OpenUSD files via the Interchange framework

| 属性 | 值 |
|---|---|
| 中文名 | Interchange USD 导入 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（翻译器设置资产、蓝图函数库） |
| 模块 | `InterchangeOpenUSDEditor` (Runtime), `InterchangeOpenUSDImport` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | unknown |
| 年龄标签 | 🆕（约 N 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Extensions/OpenUSD) | |

## 用途

该插件为虚幻引擎的 **Interchange 框架** 提供了导入 **OpenUSD** (Universal Scene Description) 文件格式的支持。USD 是 Pixar 开发的开源 3D 场景描述格式，在影视和视觉特效行业广泛使用，用于交换复杂的场景、资产、材质和动画数据。

InterchangeOpenUSD 插件的主要作用是作为 USD 文件和虚幻引擎资产（如静态网格体、骨骼网格体、材质、纹理等）之间的 **翻译器 (Translator)**。它解析 USD 文件的层级结构，并将其中的数据映射为虚幻引擎可理解的资产和组件，使得用户可以通过统一的“拖放导入”或“资产导入”工作流将 USD 资产引入引擎。

## 使用场景

- **电影与视效资产导入**：当你从 Maya、Houdini 等支持 USD 的 DCC 工具导出场景或资产，并希望将其导入到虚幻引擎中时。
- **大型场景与资产库管理**：USD 适合描述复杂、大型的场景层级和资产变体。此插件允许你将这些复杂的 USD “舞台 (Stage)” 或单个“对象 (Prim)” 作为资产或子资产导入。
- **材质与几何体交换**：需要导入 USD 中定义的材质（可能基于 MaterialX）以及对应的几何体数据时。
- **可控的导入流程**：当你需要对 USD 的导入过程进行精细控制，例如指定哪些“模式处理器 (Schema Handler)”生效、以及它们的优先级顺序时。

## 蓝图用法

该插件主要通过提供设置对象和蓝图函数库来扩展 Interchange 的 USD 导入流程。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Default Schema Handler Entries` | 获取通过 C++ 注册的默认 USD 模式处理器列表。返回的 `FSchemaHandlerEntry` 数组可被修改，并用于覆盖翻译器的默认处理器顺序。 | `UInterchangeUsdTranslatorBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **获取与修改处理器顺序**：
    *   在蓝图中，调用 `Get Default Schema Handler Entries` 节点。
    *   节点将返回一个 `FSchemaHandlerEntry` 结构体的数组。每个条目代表一个处理特定 USD 模式（如网格体、材质、灯光等）的处理器。
    *   你可以使用数组操作节点（如过滤、排序）来调整这个列表的顺序。靠前的处理器在导入时拥有更高的优先级。
2.  **应用自定义顺序**：
    *   你需要获取 `UInterchangeUsdTranslatorSettings` 的 **类默认对象 (CDO)**。
    *   将修改后的处理器数组设置到该 CDO 的 `CustomHandlerEntries` 属性中。
    *   此设置会影响后续所有使用此翻译器的 USD 导入操作。

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeUsdTranslatorBlueprintLibrary.h"
```

### 基本用法

通过蓝图函数库获取并查看默认的处理器注册列表。

```cpp
// 获取默认的 USD 模式处理器列表
TArray<FSchemaHandlerEntry> DefaultEntries = UInterchangeUsdTranslatorBlueprintLibrary::GetDefaultSchemaHandlerEntries();

// 遍历并查看
for (const FSchemaHandlerEntry& Entry : DefaultEntries)
{
    UE_LOG(LogTemp, Log, TEXT("Handler: %s, Priority: %d"), *Entry.HandlerClassName.ToString(), Entry.Priority);
}
```

### 进阶用法

在 C++ 中动态调整处理器顺序，这需要访问翻译器设置对象。

```cpp
#include "InterchangeUsdTranslatorSettings.h"

void CustomizeUsdImportPriority()
{
    // 1. 获取翻译器设置的类默认对象 (CDO)
    UInterchangeUsdTranslatorSettings* Settings = GetMutableDefault<UInterchangeUsdTranslatorSettings>();

    // 2. 获取默认处理器列表
    TArray<FSchemaHandlerEntry> NewOrder = UInterchangeUsdTranslatorBlueprintLibrary::GetDefaultSchemaHandlerEntries();

    // 3. 进行自定义排序或修改（例如，将某个处理器的优先级提前）
    // ... 对 NewOrder 数组进行操作 ...

    // 4. 将自定义顺序应用到设置中
    Settings->CustomHandlerEntries = NewOrder;

    // 现在，后续的 USD 导入将使用此自定义顺序
}
```

## Demo 示例

一个简单的示例，演示如何在 C++ 中获取并修改 USD 处理器顺序。

```cpp
// UsdImportCustomizer.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "UsdImportCustomizer.generated.h"

UCLASS()
class UUsdImportCustomizer : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "USD|Import")
    void ApplyCustomHandlerOrder();
};

// UsdImportCustomizer.cpp
#include "UsdImportCustomizer.h"
#include "InterchangeUsdTranslatorBlueprintLibrary.h"
#include "InterchangeUsdTranslatorSettings.h"

void UUsdImportCustomizer::ApplyCustomHandlerOrder()
{
    // 获取默认处理器列表
    TArray<FSchemaHandlerEntry> HandlerEntries = UInterchangeUsdTranslatorBlueprintLibrary::GetDefaultSchemaHandlerEntries();

    // 示例：将列表反转，从而逆转处理器的默认优先级
    Algo::Reverse(HandlerEntries);

    // 应用到翻译器设置
    UInterchangeUsdTranslatorSettings* TranslatorSettings = GetMutableDefault<UInterchangeUsdTranslatorSettings>();
    if (TranslatorSettings)
    {
        TranslatorSettings->CustomHandlerEntries = HandlerEntries;
        UE_LOG(LogTemp, Log, TEXT("Applied custom USD handler order with %d entries."), HandlerEntries.Num());
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | Interchange 框架的核心模块，提供翻译器基础接口和资产导入流程 |
| `USDClasses` | 提供 USD 核心数据类型（如 `FSchemaHandlerEntry`, `FUsdStage` 等）的定义 |
| `UnrealUSDWrapper` | 封装了 Pixar USD 库的低层绑定 |

*注：插件本身依赖多个 Epic 内部模块，如 `Slate`, `SlateCore`, `UMG` 用于编辑器 UI，`Core`, `CoreUObject`, `Engine` 等基础模块在此未列出。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-25 | `61d0e791` | USD Pregen: Implement tracking of Skeleton and PhysicsAssets | 实现 USD 预生成中对骨架和物理资产的追踪。 |
| 2026-05-22 | `e55b6ad4` | USD Pregen: Fix handling of USDZ files. | 修复对 USDZ 文件（USD 的打包格式）的处理问题。 |
| 2026-05-19 | `fd496b57` | USD Pregen: Properly tag nodes produced by MaterialX translator with corresponding prim path so that | 修复 MaterialX 翻译器生成的节点，使其正确标记对应的 USD Prim 路径。 |
| 2026-05-14 | `561d9c2d` | USD Pregen: Fix materials inside instances not being deduplicated; | 修复 USD 实例内材质未被去重的问题。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数时产生警告的代码。 |

### 维护评价

该插件**正处于非常活跃的开发与维护中**。从近期（2026年5月）的提交历史来看，几乎每天都有更新，内容聚焦于 **“USD Pregen”（USD 预生成）** 功能的改进和缺陷修复，涉及材质处理、实例去重、特定资产（骨架、物理资产）的跟踪以及文件格式兼容性（USDZ）。这些工作表明插件正在从实验性功能向更稳定、更完整的状态演进。

由于 `.uplugin` 明确标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，它仍然属于**实验性功能**。这意味着其 API 和行为在未来版本中可能发生破坏性变更。不建议在需要长期稳定性的生产核心流程中直接依赖此插件，但非常适合用于探索、评估或非关键的导入工作流。

**推荐使用**：适合希望尝试最新 USD 导入技术、并愿意跟进其快速发展的开发者。对于生产项目，建议密切关注其更新日志并做好应对变更的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Extensions/OpenUSD)
- [官方文档]()  (无)