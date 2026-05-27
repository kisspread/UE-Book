# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 工作流集成 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（USD模式、阶段管理UI、导出功能） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

该插件为 Unreal Engine 提供了完整的 USD（通用场景描述）工作流支持。它解决的核心问题是将 USD 这一开放标准的3D资产格式与UE引擎进行深度集成，其功能远超简单的“导入”。插件包含一套完整的模块体系，覆盖了从USD文件解析、场景阶段（Stage）管理、Prim（基本对象）与属性的可视化编辑、图层（Layer）管理、变体（Variant）选择，到最终将场景烘焙导入引擎的全过程。它实质上是一个基于USD构建的轻量级、非破坏性的场景编辑和管理环境。

## 使用场景

- 你正在参与一个大型影视、动画或视觉特效项目，项目流水线以 USD 为核心。
- 你需要在一个场景中整合来自不同部门（模型、动画、灯光）的 USD 文件，并进行非破坏性的实时编辑和预览。
- 你需要管理复杂的USD图层（Sublayer）、引用（Reference）和载荷（Payload），并在UE中实时切换和调试。
- 你需要将复杂的、包含丰富元数据的USD资产最终“烘焙”并导入为UE原生资产（如StaticMesh， SkeletalMesh）。
- 你需要将UE场景或资产导出为USD格式，以供其他DCC工具使用。

## 蓝图用法

本插件提供了丰富的编辑器端 ViewModel 来支撑 UI 交互，部分核心操作也暴露给了蓝图。

### 核心节点

由于插件规模巨大，以下仅列出当前模块 `USDStageEditorViewModels` 中与蓝图/交互相关的核心ViewModel及其功能：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ToggleVisibility` | 切换某个 Prim（对象）在USD场景中的可见性。 | `FUsdPrimViewModel` |
| `TogglePayload` | 切换某个 Prim 的 Payload（载荷）的加载状态。 | `FUsdPrimViewModel` |
| `ApplySchema` | 为某个 Prim 应用指定的 USD Schema。 | `FUsdPrimViewModel` |
| `RemoveSchema` | 移除某个 Prim 上指定的 USD Schema。 | `FUsdPrimViewModel` |
| `SetAttributeValue` | 设置某个 USD 属性的值（通过ViewModel）。 | `FUsdObjectFieldViewModel` |
| `Refresh` | 刷新指定 USD 对象的所有字段（元数据、属性、关系）数据。 | `FUsdObjectFieldsViewModel` |
| `ToggleMuteLayer` | 切换某个 USD 图层（Layer）的静音状态。 | `FUsdLayerViewModel` |
| `EditLayer` | 将某个图层设置为当前编辑目标（Edit Target）。 | `FUsdLayerViewModel` |
| `AddSubLayer` | 为当前图层添加一个新的子图层。 | `FUsdLayerViewModel` |
| `Reload` | 重新加载某个 USD 图层。 | `FUsdLayerViewModel` |
| `SetVariantSelection` | 为某个 Variant Set 设置当前选中的变体。 | `FUsdVariantSetViewModel` |
| `RemoveReference` | 移除某个 Prim 上的引用或载荷。 | `FUsdReferencesViewModel` |
| `ImportStage` | 将当前打开的 USD 阶段导入到UE内容浏览器。 | `FUsdStageViewModel` |
| `SaveStage` | 保存当前USD阶段。 | `FUsdStageViewModel` |

### 使用示例（蓝图描述）

蓝图交互通常通过 `USDStageEditor` 模块提供的 Slate UI 或自定义编辑器工具包进行，而非直接通过蓝图图表。典型流程是：在自定义编辑器工具中创建 `FUsdStageViewModel` 来管理阶段；为树状视图创建 `FUsdPrimViewModel` 的列表作为数据源；当用户在列表中选择一个 Prim 时，使用 `FUsdObjectFieldsViewModel` 加载并显示其字段，并使用 `FUsdVariantSetsViewModel` 加载其变体集。UI控件（如按钮、下拉框）通过委托或直接调用对应ViewModel的函数（如 `ToggleVisibility`， `SetVariantSelection`）来响应用户操作。

## C++ 用法

### 头文件引入

```cpp
#include "USDStageViewModel.h"
#include "USDPrimViewModel.h"
#include "USDObjectFieldViewModel.h"
// ... 根据需要引入其他 ViewModel 头文件
```

### 庺本用法

**操作USD阶段**

```cpp
// 来源: 推断自 USDStageViewModel.h
// 创建一个阶段视图模型
FUsdStageViewModel StageViewModel;

// 打开一个USD文件
StageViewModel.OpenStage(TEXT("C:/Path/To/Scene.usda"));

// 导入阶段到UE内容浏览器
StageViewModel.ImportStage(TEXT("/Game/ImportedScenes"), ImportOptionsObject);

// 保存阶段
StageViewModel.SaveStage();

// 关闭阶段
StageViewModel.CloseStage();
```

**查询和操作Prim视图模型**

```cpp
// 来源: 推断自 USDPrimViewModel.h
// 假设 UsdStage 是一个有效的 FUsdStageWeak
UE::FUsdPrim RootPrim = UsdStage->GetPseudoRoot();
FUsdPrimViewModel PrimViewModel(nullptr, UsdStage, RootPrim);

// 获取数据模型
TSharedRef<FUsdPrimModel> Data = PrimViewModel.RowData;
FText PrimName = Data->GetName();

// 切换可见性
PrimViewModel.ToggleVisibility();

// 检查是否可以应用某个Schema
FName SchemaName = TEXT("MaterialBindingAPI");
if (PrimViewModel.CanApplySchema(SchemaName))
{
    PrimViewModel.ApplySchema(SchemaName);
}
```

**读写属性字段**

```cpp
// 来源: 推断自 USDObjectFieldViewModel.h
FUsdObjectFieldsViewModel FieldsViewModel;
FieldsViewModel.Refresh(UsdStage, PrimPath, UsdTimeCode::Default());

// 遍历所有字段
for (const auto& FieldPtr : FieldsViewModel.Fields)
{
    EObjectFieldType FieldType = FieldPtr->Type;
    FString FieldName = FieldPtr->Label;
    // ... 显示或处理字段
}

// 设置一个特定属性的值
FConvertedVtValue NewValue;
NewValue.Set<FString>(TEXT("NewMaterial"));
FieldsViewModel.SetFieldValue(TEXT("material:binding"), NewValue);
```

### 进阶用法

组合多个 ViewModel 实现一个简单的编辑器面板交互逻辑：

```cpp
// 来源: 推断自多个 ViewModel 头文件的组合用法
class FMyUsdPanel
{
public:
    void OnPrimSelected(FUsdPrimViewModelRef SelectedPrim)
    {
        // 1. 更新属性面板
        FieldsViewModel_.Refresh(
            SelectedPrim->UsdStage,
            SelectedPrim->UsdPrim.GetPath().GetText(),
            UsdTimeCode::Default()
        );
        
        // 2. 更新变体集面板
        VariantSetsViewModel_.UpdateVariantSets(
            SelectedPrim->UsdStage,
            SelectedPrim->UsdPrim.GetPath().GetText()
        );
        
        // 3. 更新引用/载荷面板
        ReferencesViewModel_.UpdateReferences(
            SelectedPrim->UsdStage,
            *SelectedPrim->UsdPrim.GetPath().GetText()
        );
    }
    
private:
    FUsdObjectFieldsViewModel FieldsViewModel_;
    FUsdVariantSetsViewModel VariantSetsViewModel_;
    FUsdReferencesViewModel ReferencesViewModel_;
};
```

## Demo 示例

以下是一个控制台应用程序风格的示例，展示如何利用ViewModel层来加载USD文件并查询信息。此代码需要在一个支持模块依赖的上下文中运行（例如编辑器工具或自定义资产处理逻辑）。

**MyUsdDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "USDStageViewModel.h"
#include "USDPrimViewModel.h"
#include "USDObjectFieldViewModel.h"

class FMyUsdDemo
{
public:
    FMyUsdDemo();
    ~FMyUsdDemo();

    void Run(const FString& UsdFilePath);

private:
    void PrintPrimInfo(const FUsdPrimViewModel& Prim, int32 Depth = 0);
    void PrintFields(const FString& PrimPath);

    FUsdStageViewModel StageViewModel;
    TSharedPtr<FUsdObjectFieldsViewModel> FieldsViewModel;
    TWeakPtr<FUsdPrimViewModel> CurrentPrimViewModel;
};
```

**MyUsdDemo.cpp**
```cpp
#include "MyUsdDemo.h"
#include "USDStage.h"
#include "UsdWrappers/UsdStage.h"
#include "UsdWrappers/UsdPrim.h"

FMyUsdDemo::FMyUsdDemo()
    : FieldsViewModel(MakeShared<FUsdObjectFieldsViewModel>(nullptr))
{
}

FMyUsdDemo::~FMyUsdDemo()
{
    if (StageViewModel.UsdStageActor.IsValid())
    {
        StageViewModel.CloseStage();
    }
}

void FMyUsdDemo::Run(const FString& UsdFilePath)
{
    // 1. 打开 USD 阶段
    UE_LOG(LogTemp, Log, TEXT("Opening USD stage: %s"), *UsdFilePath);
    StageViewModel.OpenStage(*UsdFilePath);

    // 假设 UsdStageActor 已由 OpenStage 设置或通过其他方式获得
    if (!StageViewModel.UsdStageActor.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open stage or get stage actor."));
        return;
    }
    UE::FUsdStageWeak UsdStage = StageViewModel.UsdStageActor->GetStage();

    // 2. 创建根节点视图模型并递归打印信息
    UE::FUsdPrim RootPrim = UsdStage->GetPseudoRoot();
    FUsdPrimViewModel RootPrimViewModel(nullptr, UsdStage, RootPrim);
    PrintPrimInfo(RootPrimViewModel, 0);

    // 3. 打印某个特定Prim的字段（假设路径为 “/Root/SomePrim”）
    PrintFields(TEXT("/Root/SomePrim"));

    // 4. 导入阶段（可选）
    // StageViewModel.ImportStage(TEXT("/Game/DemoImport"));
}

void FMyUsdDemo::PrintPrimInfo(const FUsdPrimViewModel& Prim, int32 Depth)
{
    FString Indent = FString::ChrN(Depth * 2, ' ');
    FText PrimName = Prim.RowData->GetName();
    FText PrimType = Prim.RowData->GetType();
    UE_LOG(LogTemp, Log, TEXT("%s- %s (%s) [Visible: %s, HasPayload: %s]"),
        *Indent,
        *PrimName.ToString(),
        *PrimType.ToString(),
        Prim.RowData->IsVisible() ? TEXT("Yes") : TEXT("No"),
        Prim.RowData->HasPayload() ? TEXT("Yes") : TEXT("No")
    );

    // 递归打印子项
    TArray<FUsdPrimViewModelRef>& Children = const_cast<FUsdPrimViewModel&>(Prim).UpdateChildren();
    for (const auto& Child : Children)
    {
        PrintPrimInfo(*Child, Depth + 1);
    }
}

void FMyUsdDemo::PrintFields(const FString& PrimPath)
{
    UE_LOG(LogTemp, Log, TEXT("=== Fields for Prim: %s ==="), *PrimPath);

    if (!StageViewModel.UsdStageActor.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("No active stage to query fields from."));
        return;
    }

    UE::FUsdStageWeak UsdStage = StageViewModel.UsdStageActor->GetStage();
    FieldsViewModel->Refresh(UsdStage, *PrimPath, UsdTimeCode::Default());

    for (const auto& Field : FieldsViewModel->Fields)
    {
        UE_LOG(LogTemp, Log, TEXT("  [%s] %s: %s"),
            Field->Type == EObjectFieldType::Metadata ? TEXT("Metadata") :
            Field->Type == EObjectFieldType::Attribute ? TEXT("Attribute") :
            TEXT("Relationship"),
            *Field->Label,
            *Field->Value.GetValueString()
        );
    }
}
```

## 模块依赖

根据 `USDImporter` 各模块的常见依赖关系推断，使用其核心功能通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `USDStage` | 提供 USD 阶段管理和核心 Actor 类 (`AUsdStageActor`)。 |
| `USDSchemas` | 提供 USD Schema 相关的类型和工具。 |
| `USDExporter` | 提供将 UE 资产导出为 USD 的功能。 |
| `USDClasses` / `USDClassesEditor` | 提供 USD 相关的基础类和编辑器扩展类。 |
| `UsdUtils` (USDUtilities) | 提供 USD 与 UE 之间数据转换的核心工具函数。 |
| `SlateCore`, `UMG` | 用于构建 USD 编辑器 UI。 |

*注：由于本插件是 Epic 的内部项目，其具体的 `Build.cs` 依赖未公开。实际开发中，如果以本插件为基础开发编辑器工具，需参考官方示例或插件内模块的依赖关系进行配置。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数的警告。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | USD：添加了对分配独立于蓝图的控制绑定的支持。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va... | USD：解决了USD 26.03更新导致的、与LOD变体相关的AnimQuery内部引用失效问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了格式化字符串中32位与64位格式说明符不匹配的问题。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | USD：烘焙了曝光动画轨道的所有帧。 |

### 维护评价

- **活跃维护**：尽管插件创建于2018年，但从近期的 Git 历史（2026年）看，它仍在接受**频繁且实质性的更新**。近期的提交涵盖了新功能添加（如独立控制绑定）、重要的兼容性修复（与新版USD库的适配）、动画系统优化以及代码质量改进。
- **实验性状态**：插件在 `.uplugin` 中明确标记为 `IsBetaVersion: true`，表明其API和功能可能在未来版本中发生变化。
- **项目重要性**：作为 Epic Games 官方维护的、连接开源USD生态与UE引擎的官方桥梁，该插件具有极高的战略重要性，预计将持续得到长期投入。
- **推荐使用**：对于需要基于USD进行工作流开发或集成的项目，尽管其为实验性状态，但鉴于其官方维护、功能全面且持续更新，是目前最可靠和强大的选择。用户应做好应对未来API变动的心理准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [官方文档]() (待补充)
- [测试用例]() (路径待在源码库中搜索确认)