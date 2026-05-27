# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器界面） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

USD Importer 插件为 Unreal Engine 提供了对 OpenUSD (Universal Scene Description) 格式的全面支持。它不仅仅是一个简单的文件导入器，而是一个完整的 USD 工作流集成套件。该插件解决的核心问题是：如何在 UE 中无缝地查看、编辑、导入和导出复杂的 USD 场景，实现与 Maya、Houdini 等 DCC 工具的非破坏性资产交换和场景协作。

插件通过多个模块协同工作，实现了 USD Stage（舞台）的实时加载与编辑、属性查看与修改、图层管理、变体（Variant）选择、Prim（场景图元）树状结构展示、几何体缓存集成以及最终导入为 UE 原生资产等功能。

## 使用场景

- **影视/动画资产管线**：你需要从 Maya 等软件导入包含复杂材质、动画、变体和图层结构的 USD 资产到 UE 中进行实时渲染或虚拟制片。
- **场景协作**：美术师在 Houdini 中构建程序化 USD 场景，你需要将其无缝链接到 UE 关卡中，并支持在 UE 侧进行部分属性的实时调整。
- **资产审查**：你需要检查一个 USD 文件的内部结构（Prim 层次、属性、参考关系、变体等），而无需依赖外部 DCC 工具。
- **非破坏性编辑**：你希望对导入的 USD 资产进行修改（如调整材质参数、切换变体），但同时保留原始 USD 文件结构，以便后续在 DCC 中继续迭代。
- **几何缓存导入**：你需要将 USD 格式的动画几何缓存（如布料、流体模拟结果）导入 UE 并用于实时播放。

## 蓝图用法

该插件的核心功能主要体现在编辑器 UI 和 C++ API 上，蓝图可直接调用的函数较少。其工作流主要通过 `USDStageEditor` 模块提供的专用编辑器面板和工具栏按钮来完成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （编辑器内操作） | 在 USD Stage 面板中右键点击 Prim 或图层可执行各种操作 | N/A |

### 使用示例（蓝图描述）

由于主要的用户交互发生在专用的编辑器面板中，典型的蓝图使用场景是通过 `USDStageActor` 在场景中引用一个 USD Stage，并通过编辑器 UI 进行操作。在蓝图中，你可能会：
1.  在场景中放置一个 `USDStageActor`。
2.  在其属性面板中指定一个 `.usd` 或 `.usda` 文件路径。
3.  运行游戏或在编辑器中，`USDStageActor` 将根据 USD 文件的内容生成对应的 UE Actor。
4.  通过点击 `USDStageActor` 打开关联的 **USD Stage Editor** 面板，进行 Prim 浏览、属性编辑、变体切换、图层管理等操作。
5.  最终，可以通过面板的“导入”按钮，将当前 USD Stage 的状态转换为 UE 原生资产（如 StaticMesh、Material）并保存到内容浏览器中。

## C++ 用法

该插件的 C++ API 主要封装在 `USDClasses`, `UsdUtils` 等模块中，用于程序化地操作 USD 数据。`USDStageEditorViewModels` 模块提供了编辑器 UI 的视图模型。

### 头文件引入

```cpp
#include "UsdWrappers/UsdStage.h"
#include "UsdWrappers/UsdPrim.h"
#include "UsdWrappers/SdfLayer.h"
#include "UsdUtils/UsdStageViewModel.h" // 或其他需要的视图模型头文件
```

### 基本用法

以下示例展示了如何使用 `FUsdStageViewModel` 来程序化地打开和操作一个 USD Stage。(*来源：推断自 `USDStageViewModel.h` 接口*)

```cpp
// 创建一个 USDStageViewModel 实例（通常由编辑器模块管理，此处仅为演示逻辑）
FUsdStageViewModel StageViewModel;

// 假设已有一个有效的 AUsdStageActor 指针
StageViewModel.UsdStageActor = SomeUsdStageActor;

// 打开一个新的 USD 文件
StageViewModel.OpenStage(TEXT("/Game/Assets/MyScene.usd"));

// 设置所有 Prim 的加载规则为“全部加载”
StageViewModel.SetLoadAllRule();

// 程序化地将当前 Stage 状态导入到指定内容目录
FString TargetFolder = TEXT("/Game/ImportedAssets");
UUsdStageImportOptions* ImportOptions = nullptr; // 可以配置导入选项
StageViewModel.ImportStage(*TargetFolder, ImportOptions);
```

### 进阶用法

结合多个视图模型可以进行更精细的操作。例如，遍历 Prim 树并修改属性：

```cpp
// 获取根 Prim 的视图模型（假设已通过某种方式获得 FUsdPrimViewModel 实例）
FUsdPrimViewModel RootPrimViewModel = ...;

// 遍历子 Prim
for (const FUsdPrimViewModelRef& ChildPrim : RootPrimViewModel.UpdateChildren())
{
    // 检查此 Prim 是否有 Payload
    if (ChildPrim->HasPayload() && !ChildPrim->IsLoaded())
    {
        // 尝试加载 Payload
        ChildPrim->TogglePayload();
    }
    
    // 切换 Prim 的可见性
    ChildPrim->ToggleVisibility();
    
    // 为 Prim 应用一个 Schema (例如，为 Mesh 增加一个自定义的 Schema)
    if (ChildPrim->CanApplySchema(FName("MyCustomAPI")))
    {
        ChildPrim->ApplySchema(FName("MyCustomAPI"));
    }
}

// 刷新 Prim 的数据以反映最新状态
RootPrimViewModel.RefreshData(true); // true 表示同时刷新子节点
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何使用 `FUsdObjectFieldsViewModel` 来读取一个 USD Prim 的属性。

**MyUSDFieldReader.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "USDObjectFieldViewModel.h"

class FMyUSDFieldReader
{
public:
    void ReadPrimAttributes(const UE::FUsdStageWeak& Stage, const TCHAR* PrimPath);

private:
    FUsdObjectFieldsViewModel FieldsViewModel;
};
```

**MyUSDFieldReader.cpp**
```cpp
#include "MyUSDFieldReader.h"

void FMyUSDFieldReader::ReadPrimAttributes(const UE::FUsdStageWeak& Stage, const TCHAR* PrimPath)
{
    // 使用视图模型刷新指定 Prim 的属性数据
    FieldsViewModel.Refresh(Stage, PrimPath, UsdTimeCode::Default()); // UsdTimeCode::Default() 通常对应时码 0
    
    // 遍历所有属性字段
    for (const TSharedPtr<FUsdObjectFieldViewModel>& FieldPtr : FieldsViewModel.Fields)
    {
        if (FieldPtr)
        {
            UE_LOG(LogTemp, Log, TEXT("Field: %s, Type: %d, Value: %s"),
                *FieldPtr->Label,
                static_cast<int32>(FieldPtr->Type),
                *FieldPtr->Value.Get<FString>()); // 注意：实际获取值的方式需根据 UsdUtils::FConvertedVtValue 类型
        }
    }
}
```

## 模块依赖

USDImporter 插件由多个模块组成，它们之间相互依赖，并共同依赖于 USD 核心库。要使用该插件，你的项目通常需要依赖以下模块（除了标准 Core/Engine 模块外）：

| 模块 | 用途 |
|---|---|
| `USDClasses` | 定义 USD 相关的 UObject 和基本数据结构 |
| `UsdUtils` | 提供 USD 数据类型的转换工具和通用功能函数 |
| `USDSchemas` | 定义 USD Prim 的类型映射规则（Schema） |
| `USDStage` | 管理 `AUsdStageActor` 和 USD Stage 的运行时表示 |
| `USDImporter` | 处理 USD 文件内容的解析和到 UE 资产的转换逻辑 |
| `GeometryCacheUSD` | 将 USD 内容导入为 UE 的几何缓存资产 |

**注意**：以上模块的 `Build.cs` 中会包含对第三方 USD 库（如 `USDLib`, `USDKit`）的依赖。在启用插件时，需确保项目已正确配置这些第三方库。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数产生警告的代码。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | USD: 新增支持分配与蓝图无关的控制绑定。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va | USD: 解决了 USD 更新到 26.03 版本导致 LOD 变化时 AnimQuery 内部引用失效的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了格式说明符与参数位数不匹配（32位/64位）的问题。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | USD: 烘焙曝光动画轨道的所有帧。 |

### 维护评价

USD Importer 插件由 Epic Games 官方维护，是一个**活跃且持续更新**的项目。
- **创建时间**：2018年11月，已有约7年历史。
- **最近更新**：最近一次更新在2026年5月，且过去一个月内有多次功能提交和错误修复，涵盖动画、绑定、浮点精度和LOD等核心功能。
- **维护状态**：**活跃维护中**。Commit 记录显示其仍在积极开发新功能（如控制绑定支持）和修复底层问题。
- **已知问题/限制**：插件标记为 `IsBetaVersion` 且 `EnabledByDefault` 为 `false`，表明它可能尚未达到完全稳定的生产就绪状态，可能存在一些边缘情况的缺陷或不完整的功能。
- **推荐**：**强烈推荐**给任何需要与 USD 工作流集成的 UE 项目。尽管标记为测试版，但其功能已相当成熟，是 Epic 官方推荐的 USD 集成方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/working-with-usd-in-unreal-engine/) (Epic 官方 USD 工作流文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests)