# Datasmith FBX Importer

> Adds support for importing content from DeltaGen and VRED into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | DatasmithFBX导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithVREDTranslator` (Editor), `DatasmithDeltaGenTranslator` (Editor), `DatasmithFBXTranslator` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithFBXImporter) | |

## 用途

本插件为 Unreal Engine 提供从专业工业可视化软件 **Dassault Systèmes DeltaGen** 和 **PI VRED** 导入 3D 场景的能力。它并非一个通用的 FBX 导入器，而是专为解析这些特定软件导出的、包含丰富元数据（如材质参数、动画片段、变体配置、灯光信息）的 FBX 文件而设计。它通过读取随 FBX 文件一同导出的辅助文件（`.mats`, `.var`, `.clips`, `.lights`），能更准确地还原原始场景中的材质、产品变体、动画序列和灯光设置，确保导入的资产在功能上更接近源软件中的设计，主要用于汽车设计、工业可视化等需要高保真度工作流的领域。

## 使用场景

- **汽车行业设计评审**：设计师在 VRED 或 DeltaGen 中完成汽车内外饰的可视化方案后，需要将其完整导入 UE 进行实时渲染、交互式演示或虚拟展厅搭建，此时需要保留所有的材质变体、部件替换逻辑和灯光设置。
- **工业产品可视化**：产品设计师使用 DeltaGen 创建了包含复杂动画和部件拆解的产品展示，希望导入 UE 后继续使用这些动画序列。
- **项目需要导入 VRED/DeltaGen 的完整场景资产**，而不仅仅是基础的几何体和贴图。

## 蓝图用法

本插件主要提供导入器功能，其配置选项通过蓝图可访问的 `UDatasmithVREDImportOptions` 和 `UDatasmithDeltaGenImportOptions` 类暴露。用户可以在项目设置或导入对话框中调整这些选项，而不是在运行时通过蓝图节点调用。

### 核心节点（导入配置）

此表列出的部分蓝图属性允许用户在导入前配置 VRED 或 DeltaGen 文件的处理方式。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `bImportMats` | 是否导入与 FBX 文件同名的 `.mats` 材质文件，以更准确地还原材质参数 | `UDatasmithVREDImportOptions` |
| `bImportVar` | 是否导入与 FBX 文件同名的 `.var` 变体文件，用于创建产品配置器 | `UDatasmithVREDImportOptions` |
| `bImportClipInfo` | 是否导入与 FBX 文件同名的 `.clips` 动画片段文件 | `UDatasmithVREDImportOptions` |
| `bImportLightInfo` | 是否导入与 FBX 文件同名的 `.lights` 灯光补充信息文件 | `UDatasmithVREDImportOptions` |
| `bCleanVar` | 是否在导入时清理变体文件中无效或空的选项 | `UDatasmithVREDImportOptions` |

### 使用示例（蓝图描述）

配置导入选项通常在编辑器导入对话框中完成，而非在蓝图图表中。然而，你可以通过以下步骤在蓝图或编辑器工具脚本中访问和设置这些选项：

1.  使用 `Get Datasmith VRED Import Options` 或类似节点获取当前导入选项对象。
2.  通过返回的选项对象，访问并设置上述 `bImportMats`、`bImportVar` 等布尔属性。
3.  将配置好的选项对象传递给 `Datasmith Import Scene` 等节点以执行导入。

## C++ 用法

主要的 C++ 用法涉及实例化和使用 `FDatasmithVREDImporter` 类来加载和处理场景。

### 头文件引入

```cpp
#include "DatasmithVREDImporter.h"
#include "DatasmithVREDImportOptions.h"
```

### 基本用法

根据 `FDatasmithVREDImporter` 的接口设计，基本的导入流程如下：（来源：`Private/DatasmithVREDImporter.h` 及相关翻译器实现）

```cpp
// 1. 准备 Datasmith 场景输出和导入选项
TSharedRef<IDatasmithScene> OutScene = FDatasmithSceneFactory::CreateScene(TEXT("ImportedVREDScene"));
UDatasmithVREDImportOptions* ImportOptions = GetMutableDefault<UDatasmithVREDImportOptions>();

// 2. 创建导入器实例
FDatasmithVREDImporter Importer(OutScene, ImportOptions);

// 3. 打开 VRED 导出的 FBX 文件 (会自动查找并解析关联的辅助文件)
const FString FBXFilePath = TEXT("/Path/To/Your/Model.fbx");
if (Importer.OpenFile(FBXFilePath))
{
    // 4. 将解析后的场景数据转换并发送到 Datasmith 场景
    Importer.SendSceneToDatasmith();

    // 5. 使用 OutScene 进行后续处理，例如将其应用到关卡或导出为 .udatasmith 文件
    // ...
}

// 6. 清理
Importer.UnloadScene();
```

### 进阶用法

`FDatasmithVREDImporter` 的 `OpenFile` 方法内部会调用 `ParseFbxFile` 和 `ParseAuxFiles`。你也可以单独解析某个辅助文件用于调试或特定处理，这需要使用 `FDatasmithVREDAuxFiles` 命名空间下的函数：（来源：`Private/DatasmithVREDImporterAuxFiles.h`）

```cpp
#include "DatasmithVREDImporterAuxFiles.h"

// 单独解析 .mats 文件
FString MatsFilePath = TEXT("/Path/To/Your/Model.mats");
FDatasmithVREDImportMatsResult MatsResult = FDatasmithVREDAuxFiles::ParseMatsFile(MatsFilePath);
// MatsResult.Mats 包含了从 .mats 文件解析出的材质信息数组

// 单独解析 .var 文件
FString VarFilePath = TEXT("/Path/To/Your/Model.var");
FDatasmithVREDImportVariantsResult VarResult = FDatasmithVREDAuxFiles::ParseVarFile(VarFilePath);
// VarResult.VariantSwitches 包含了从 .var 文件解析出的变体数据

// 单独解析 .clips 文件
FString ClipsFilePath = TEXT("/Path/To/Your/Model.clips");
FDatasmithVREDImportClipsResult ClipsResult = FDatasmithVREDAuxFiles::ParseClipsFile(ClipsFilePath);
// ClipsResult.AnimClips 包含了动画片段信息
```

## Demo 示例

一个完整的最小示例，展示如何在 C++ 中配置并使用导入器：（来源：综合 `FDatasmithVREDImporter` 和 `UDatasmithVREDImportOptions` 的接口）

```cpp
// VREDImportDemo.h
#pragma once

#include "CoreMinimal.h"

class UVREDImportDemo
{
public:
    static void ImportVREDScene(const FString& FBXFilePath, bool bImportMaterials, bool bImportVariants);
};

// VREDImportDemo.cpp
#include "VREDImportDemo.h"
#include "DatasmithVREDImporter.h"
#include "DatasmithVREDImportOptions.h"
#include "DatasmithSceneFactory.h"

void UVREDImportDemo::ImportVREDScene(const FString& FBXFilePath, bool bImportMaterials, bool bImportVariants)
{
    // 创建输出场景
    TSharedRef<IDatasmithScene> Scene = FDatasmithSceneFactory::CreateScene(FName(*FPaths::GetBaseFilename(FBXFilePath)));

    // 配置导入选项
    UDatasmithVREDImportOptions* Options = NewObject<UDatasmithVREDImportOptions>();
    Options->bImportMats = bImportMaterials;
    Options->bImportVar = bImportVariants;
    Options->ResetPaths(FBXFilePath, false); // 重置路径查找辅助文件

    // 初始化并执行导入
    FDatasmithVREDImporter Importer(Scene, Options);
    if (Importer.OpenFile(FBXFilePath))
    {
        Importer.SendSceneToDatasmith();
        UE_LOG(LogTemp, Log, TEXT("VRED Scene imported successfully into Datasmith scene: %s"), *Scene->GetName());
        // 此处可以将 `Scene` 传递给 Datasmith 导入器进行实际资产创建
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open VRED file: %s"), *FBXFilePath);
    }

    Importer.UnloadScene();
}
```

## 模块依赖

根据 Datasmith 插件的通用架构，此插件依赖于 Datasmith 核心模块和 FBX 处理模块。

| 模块 | 用途 |
|---|---|
| `DatasmithImporter` | Datasmith 核心导入框架和接口 |
| `DatasmithContent` | Datasmith 内容类型（如资产、材质元素）的定义 |
| `DatasmithCore` | Datasmith 核心库，提供场景、元素等基础结构（通过 DatasmithImporter 间接依赖） |
| `FBX` / `UnrealEd` 中的 FBX 功能 | 解析 FBX 文件格式 |
| `DatasmithFBXTranslator` | 本插件内部的基础 FBX 翻译器模块，为 DeltaGen 和 VRED 翻译器提供基础 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下 double 常量截断为 float 的警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版 UE_LOG 宏迁移为新版 UE_LOGF。 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复不可达代码错误。 |
| 2025-03-13 | `b059f7b4` | Fix trivial unreachable code warnings. | 修复琐碎的不可达代码警告。 |
| 2024-10-02 | `0a14cf0e` | Update VRED python exporter to support API changes in VRED | 更新 VRED Python 导出器以支持 VRED 的 API 变更。 |

### 维护评价

- **创建时间**：2019年创建，属于较早期的 Datasmith 家族成员。
- **最近更新频率和内容**：最近的提交（2024年至2026年）主要是代码清理、警告修复和日志系统迁移，没有发现新功能开发或重大改进。最后一次涉及功能性的更新是2024年10月，为适配 VRED 软件的 API 变化而更新了 Python 导出器。
- **是否还在活跃维护**：维护活动已显著放缓，近期提交多为技术债务清理而非功能迭代。**已超过1年没有实质性功能更新。**
- **是否有已知问题或限制**：默认禁用 (`EnabledByDefault=false`)，表明它可能被视为特定工作流或实验性功能，非核心组件。其功能强依赖于源软件（VRED/DeltaGen）的导出格式。
- **是否推荐使用**：**如果你的工作流确实需要从 VRED 或 DeltaGen 导入带有复杂元数据（材质、变体、动画）的场景，此插件是官方提供的必需工具。** 但需注意，其更新频率较低，未来可能面临与新版 UE 或源软件不兼容的风险。对于简单的 FBX 导入，应使用 UE 自带的 FBX 导入器。

**⚠️ 警告：该插件超过一年没有功能性更新，维护可能不活跃。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithFBXImporter)
- [官方文档]() （.uplugin 中未提供）
- [测试用例]() （提供的信息中未明确指向测试文件路径）