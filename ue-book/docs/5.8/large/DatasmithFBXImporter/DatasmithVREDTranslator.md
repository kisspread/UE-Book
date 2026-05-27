# Datasmith FBX Importer

> Adds support for importing content from DeltaGen and VRED into Unreal Engine（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | VRED FBX 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithVREDTranslator` (Editor), `DatasmithDeltaGenTranslator` (Editor), `DatasmithFBXTranslator` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithFBXImporter) | |

## 用途

此插件的核心功能是为 **VRED** 软件（一款用于汽车、产品设计可视化的专业工具）导出的 FBX 文件提供专门的翻译器。它不只是简单的 FBX 导入，而是能够解析 VRED 特有的辅助数据文件（如 `.mats` 材质文件、`.var` 变体文件、`.lights` 灯光文件、`.clips` 动画剪辑文件），并将这些数据与基础 FBX 模型一起，完整地转换为虚幻引擎的 Datasmith 场景。这使得设计师在 VRED 中创建的复杂场景、材质变体、动画序列和灯光设置能够无损地迁移到 UE 中，主要用于设计评审和可视化预览。

## 使用场景

- 你是一个汽车设计师，在 **VRED** 中创建了车辆的渲染场景，包含多种颜色、材质变体以及轮毂、车门等部件的开合动画，希望在虚幻引擎中进行实时交互式评审。
- 你的工作流涉及从 VRED 导出包含 `.fbx`、`.var`、`.clips` 等多个文件的完整数据包，你需要将它们一次性正确导入 UE。
- 你需要在 UE 中保留并使用 VRED 项目中的“变体集”（Variant Sets）和“动画剪辑”（Animation Clips），以便在运行时或编辑器中切换模型状态和播放动画。

**注意**：此插件默认未启用 (`EnabledByDefault: false`)。要使用它，需要在 UE 编辑器中手动启用 `DatasmithFBXImporter` 插件。

## 蓝图用法

此插件主要作为编辑器数据导入工具，其蓝图暴露的节点主要集中在导入选项的配置上，允许在导入前设置特定参数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `bImportMats` | 布尔属性，控制是否导入 VRED 的 `.mats` 材质文件以获得更准确的材质表现。 | `UDatasmithVREDImportOptions` |
| `bImportVar` | 布尔属性，控制是否导入 VRED 的 `.var` 变体文件。 | `UDatasmithVREDImportOptions` |
| `bImportLightInfo` | 布尔属性，控制是否导入 VRED 的 `.lights` 灯光附加信息文件。 | `UDatasmithVREDImportOptions` |
| `bImportClipInfo` | 布尔属性，控制是否导入 VRED 的 `.clips` 动画剪辑文件。 | `UDatasmithVREDImportOptions` |
| `bCleanVar` | 布尔属性，控制是否清理导入的变体（移除空变体集和无效选项）。 | `UDatasmithVREDImportOptions` |
| `ResetPaths` | 函数，根据给定的 FBX 文件名重置所有辅助文件（mats, var, lights, clips）的搜索路径。 | `UDatasmithVREDImportOptions` |

### 使用示例（蓝图描述）

在导入 VRED FBX 文件前，可以通过蓝图获取并修改 `UDatasmithVREDImportOptions` 对象。
1.  使用 “Get Datasmith Import Options” 节点或类似方法获取导入选项对象。
2.  通过 “Set (by name)” 节点，将 `bImportMats`、`bImportVar` 等属性设置为 `true`。
3.  如果不想使用默认的文件查找逻辑，可以手动设置 `MatsPath`、`VarPath` 等 `FFilePath` 属性，指向正确的辅助文件路径。
4.  将配置好的选项对象传递给导入函数。

## C++ 用法

### 头文件引入

```cpp
#include "DatasmithVREDTranslatorModule.h"
// 如果需要操作导入选项
#include "DatasmithVREDImportOptions.h"
```

### 基本用法

此插件主要通过 Datasmith 框架的 `IDatasmithTranslator` 接口工作。开发者通常不直接调用，而是通过 DatasmithImporter 模块触发。了解其内部结构有助于调试和扩展。

**检查模块是否可用**
```cpp
// 来源：Public/DatasmithVREDTranslatorModule.h
if (IDatasmithVREDTranslatorModule::IsAvailable())
{
    // VRED 翻译器模块已加载，可以执行 VRED 相关操作
    IDatasmithVREDTranslatorModule& VREDModule = IDatasmithVREDTranslatorModule::Get();
    // ... 进一步操作
}
```

**了解核心导入类**
`FDatasmithVREDImporter` 是执行实际导入逻辑的类。
```cpp
// 来源：Private/DatasmithVREDImporter.h
// 创建一个 VRED 导入器实例
TSharedRef<IDatasmithScene> Scene = MakeShared<FDatasmithScene>();
UDatasmithVREDImportOptions* Options = ... // 获取导入选项
FDatasmithVREDImporter Importer(Scene, Options);

// 打开并解析 VRED 导出的 FBX 文件
if (Importer.OpenFile(TEXT("C:/MyVREDExport/scene.fbx")))
{
    // 将解析的数据发送到 Datasmith 场景
    Importer.SendSceneToDatasmith();
    // 完成后清理资源
    Importer.UnloadScene();
}
```

### 进阶用法

**理解 VRED 变体数据结构**
插件定义了一系列结构体来映射 VRED 的变体系统，这些在蓝图中也可用。
```cpp
// 来源：Private/DatasmithVREDImportData.h
FVREDCppVariant Variant;
Variant.Name = TEXT("Wheel_Style_A");
Variant.Type = EVREDCppVariantType::Geometry; // 这是一个几何变体
Variant.Geometry.TargetNodes = { TEXT("Wheel_Front_L"), TEXT("Wheel_Front_R") }; // 影响的节点
Variant.Geometry.Options.Add({TEXT("Option1"), {TEXT("MeshA1")}, {TEXT("MeshA2")}}); // 具体的显示/隐藏选项
// ... 这样的 Variant 结构可以被 FVREDVariantConverter 转换为 IDatasmithLevelVariantSetsElement
```

**处理动画剪辑**
`FDatasmithVREDClipProcessor` 负责处理 VRED 独特的嵌套动画剪辑延迟问题，使其符合 Sequencer 的工作方式。
```cpp
// 来源：Private/DatasmithVREDClipProcessor.h
TArray<FDatasmithFBXSceneAnimClip> ParsedClips = ...; // 从 .clips 文件解析出的原始数据
TArray<FDatasmithFBXSceneAnimNode> AnimNodes = ...;
FDatasmithVREDClipProcessor ClipProcessor(ParsedClips, AnimNodes);
ClipProcessor.Process(); // 处理剪辑延迟和翻转等问题，使其适用于 UE
```

## Demo 示例

一个最小化的使用 `FDatasmithVREDImporter` 的示例，演示如何将 VRED 数据解析到 Datasmith 场景。

**MyVREDImportHelper.h**
```cpp
#pragma once
#include "CoreMinimal.h"

class IDatasmithScene;
class UDatasmithVREDImportOptions;

class FMyVREDImportHelper
{
public:
    static bool ImportVREDScene(const FString& FBXFilePath, UDatasmithVREDImportOptions* Options, TSharedRef<IDatasmithScene>& OutScene);
};
```

**MyVREDImportHelper.cpp**
```cpp
#include "MyVREDImportHelper.h"
#include "DatasmithVREDImporter.h"

bool FMyVREDImportHelper::ImportVREDScene(const FString& FBXFilePath, UDatasmithVREDImportOptions* Options, TSharedRef<IDatasmithScene>& OutScene)
{
    if (!Options)
    {
        return false;
    }

    // 创建 VRED 导入器
    FDatasmithVREDImporter Importer(OutScene, Options);

    // 第一步：打开并解析 FBX 文件及其关联的辅助文件
    if (!Importer.OpenFile(FBXFilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open VRED FBX file: %s"), *FBXFilePath);
        return false;
    }

    // 第二步：将解析的数据转换为 Datasmith 场景元素
    if (!Importer.SendSceneToDatasmith())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to send VRED scene to Datasmith."));
        Importer.UnloadScene();
        return false;
    }

    // 第三步：清理临时数据
    Importer.UnloadScene();
    UE_LOG(LogTemp, Log, TEXT("Successfully imported VRED scene: %s"), *FBXFilePath);
    return true;
}
```

## 模块依赖

从 `DatasmithVREDTranslator.Build.cs` 分析，使用者（或本插件内部）需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `DatasmithFBX` | 核心依赖。提供 FBX 文件解析的基础结构和数据容器（如 `FDatasmithFBXScene`, `FDatasmithFBXSceneNode`）。 |
| `DatasmithImporter` | 提供 Datasmith 导入框架、`IDatasmithTranslator` 接口和场景构建能力。 |
| `DatasmithContent` | 提供 Datasmith 在运行时所需的内容资产类型和接口。 |

**其他未列出的依赖**（如 `Core`, `Engine`, `Slate` 等）均为 UE 基础模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数时产生的编译警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏 `UE_LOG` 迁移为新的 `UE_LOGF` 宏。 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复不可达代码错误。 |
| 2025-03-13 | `b059f7b4` | Fix trivial unreachable code warnings. | 修复琐碎的不可达代码警告。 |
| 2024-10-02 | `0a14cf0e` | Update VRED python exporter to support API changes in VRED | 更新 VRED Python 导出器脚本以支持 VRED 的 API 变更。 |

### 维护评价

- **创建时间**：该插件于 2019 年 10 月创建，已有约 6 年历史。
- **近期更新频率**：近一年内有多次提交，但集中在**代码质量维护**（修复编译警告、错误）和**日志系统迁移**上。最后一次**功能性更新**（更新导出器脚本支持新版 VRED）距今已超过 1.5 年。
- **活跃度**：处于**维护不活跃**状态。虽然代码库仍在随引擎版本进行基础维护，但针对新功能或兼容性新版本 VRED 的更新非常缓慢。
- **已知问题/限制**：
    1.  **默认未启用**：需要手动启用，表明 Epic 可能将其视为专业或特定场景工具。
    2.  **版本依赖**：对 VRED 软件版本有一定依赖（从 `.mats`, `.var` 等文件格式可知），更新滞后可能影响与新版 VRED 的兼容性。
- **推荐使用**：**仅推荐给有明确 VRED 数据导入需求的用户**。对于其他 FBX 导入，应使用引擎内置的标准 FBX 导入器或更通用的 Datasmith 导入器。使用前请确认您的 VRED 版本与此插件兼容。

**⚠️ 警告**：超过 1.5 年没有针对核心功能（如新版 VRED 支持、Datasmith API 更新）的实质性提交，长期兼容性和支持前景存在不确定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithFBXImporter)
- [官方文档]() (此插件无独立官方文档，参考 [Datasmith 官方文档](https://docs.unrealengine.com/en-US/datasmith/))
- [测试用例]() (在提供的源码信息中未找到明确的测试用例路径)