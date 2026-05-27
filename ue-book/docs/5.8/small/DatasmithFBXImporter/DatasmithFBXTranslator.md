# Datasmith FBX Importer

> Adds support for importing content from DeltaGen and VRED into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | Datasmith FBX 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithVREDTranslator` (Editor), `DatasmithDeltaGenTranslator` (Editor), `DatasmithFBXTranslator` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithFBXImporter) | |

## 用途

该插件是 Datasmith 生态系统的一部分，专门用于解析和导入来自特定工业设计及可视化软件（主要是 DeltaGen 和 VRED）导出的 FBX 文件。它不仅仅是简单的 FBX 导入器，其核心价值在于理解并转换这些软件特有的 FBX 结构，包括复杂的动画系统、材质参数（如三平面投影、VRED 的重复模式）、场景层级以及软件自定义的元数据（如切换对象、材质切换等），最终将其转换为 Unreal Engine 可用的 Datasmith 场景元素。这解决了从专业汽车设计、产品可视化等工作流中将复杂、动画化的设计数据无缝迁移到 UE 的难题。

## 使用场景

- **汽车/工业设计可视化**：设计师在 DeltaGen 或 VRED 中完成带有多状态动画（如车门开合、零件切换）和材质的汽车模型，需要将其导入 UE 进行实时渲染或虚拟评审。
- **动画资产迁移**：需要将在 VRED 中制作的复杂、基于关键帧的物体动画（如爆炸视图、装配过程）准确导入 UE。
- **材质参数保真导入**：希望保留 VRED 中定义的特殊材质属性（如精确的纹理投影方式、重复模式），而不仅仅是基础的颜色和贴图。
- **批量场景优化**：导入后的场景包含大量冗余节点（如辅助几何体、灯光目标点），需要工具自动清理和优化层级结构。

## 蓝图用法

该插件主要作为编辑器工具运行，直接的蓝图节点较少。主要的交互点在于配置导入选项。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `TextureDirs` | (属性) 指定在导入过程中搜索纹理文件的文件夹路径列表。当 FBX 文件中引用的纹理路径失效时，Datasmith 会在这些目录中查找。 | `UDatasmithFBXImportOptions` |

### 使用示例（蓝图描述）

在导入 Datasmith 场景或触发自动重新导入时，可以在“导入选项”面板中找到“Datasmith FBX 导入选项”。在这里，你可以向 `TextureDirs` 数组中添加多个目录路径，以确保材质所需的纹理文件能够被正确找到。

## C++ 用法

### 头文件引入

```cpp
#include "DatasmithFBXTranslatorModule.h"
#include "DatasmithFBXFileImporter.h"
#include "DatasmithFBXSceneProcessor.h"
#include "DatasmithFBXImporter.h"
#include "DatasmithFBXImportOptions.h"
```

### 基本用法

该插件的核心是内部处理流程，通常由 Datasmith 导入框架调用。以下示例展示了如何访问其公共模块接口并确认模块加载状态。

```cpp
// 检查 DatasmithFBXTranslator 模块是否加载
if (IDatasmithFBXTranslatorModule::IsAvailable())
{
    // 获取模块引用
    IDatasmithFBXTranslatorModule& FBXTranslatorModule = IDatasmithFBXTranslatorModule::Get();
    UE_LOG(LogTemp, Log, TEXT("DatasmithFBXTranslator 模块已加载。"));
}
```

### 进阶用法

以下示例展示了如何模拟插件内部工作流的核心阶段：导入、处理和转换。这有助于理解插件架构，但通常不需要用户直接调用。

```cpp
// 假设已有一个 FbxScene* 从 FBX SDK 获取
FbxScene* MyFbxScene = /* ... */;
// 创建配置选项
const UDatasmithFBXImportOptions* ImportOptions = GetDefault<UDatasmithFBXImportOptions>();
const FDatasmithImportBaseOptions* BaseOptions = /* ... */;

// 1. 创建中间场景表示
FDatasmithFBXScene IntermediateScene;

// 2. 使用文件导入器将 FBX 数据填充到中间场景
FDatasmithFBXFileImporter FileImporter(MyFbxScene, &IntermediateScene, ImportOptions, BaseOptions);
FileImporter.ImportScene();

// 3. 对中间场景进行优化和处理（例如去除冗余节点）
FDatasmithFBXSceneProcessor SceneProcessor(&IntermediateScene);
SceneProcessor.FindDuplicatedMaterials();
SceneProcessor.RemoveEmptyNodes();
SceneProcessor.SimplifyNodeHierarchy();

// 4. (概念性) 将处理后的中间场景转换为最终的 Datasmith 元素
// 这部分通常由更上层的 VRED/DeltaGen 转换器完成。
// FDatasmithFBXImporter DatasmithImporter;
// TSharedRef<IDatasmithScene> FinalScene = IDatasmithScene::Create();
// DatasmithImporter.BuildAssetMaps(FinalScene, /*...*/);
```

## Demo 示例

以下示例展示了一个最小化的类，演示了如何在自己的导入器或处理程序中集成 DatasmithFBXTranslator 模块的功能。

```cpp
// MyCustomFBXProcessor.h
#pragma once

#include "CoreMinimal.h"
#include "DatasmithFBXScene.h" // 包含中间场景的数据结构

class FMyCustomFBXProcessor
{
public:
    // 模拟从FBX文件加载并处理数据
    void ProcessLoadedFBXData(FDatasmithFBXScene& InOutScene);
};
```

```cpp
// MyCustomFBXProcessor.cpp
#include "MyCustomFBXProcessor.h"
#include "DatasmithFBXSceneProcessor.h" // 使用场景处理器

void FMyCustomFBXProcessor::ProcessLoadedFBXData(FDatasmithFBXScene& InOutScene)
{
    // 使用插件提供的处理器来优化场景
    FDatasmithFBXSceneProcessor Processor(&InOutScene);
    
    // 移除无用的灯光映射节点
    Processor.RemoveLightMapNodes();
    
    // 移除不可见节点
    Processor.RemoveInvisibleNodes();
    
    // 压缩节点层级
    Processor.SimplifyNodeHierarchy();
    
    // 修复无效的网格体名称
    Processor.FixMeshNames();
    
    UE_LOG(LogTemp, Log, TEXT("场景优化完成。剩余节点数: %d"), InOutScene.GetAllNodes().Num());
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DatasmithCore` | Datasmith 的核心数据结构和接口。 |
| `DatasmithContent` | Datasmith 内容资产类型。 |
| `DatasmithImporter` | Datasmith 导入框架，本插件为其提供 FBX 格式的支持。 |
| `FBX` (第三方) | 提供 FBX SDK 进行 FBX 文件解析。 |
| `MeshDescription` | 用于表示和操作网格体几何数据。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下 double 常量截断为 float 的警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF。 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复不可达代码错误。 |
| 2025-03-13 | `b059f7b4` | Fix trivial unreachable code warnings. | 修复琐碎的不可达代码警告。 |
| 2024-10-02 | `0a14cf0e` | Update VRED python exporter to support API changes in VRED | 更新 VRED Python 导出器以支持 VRED 的 API 变更。 |

### 维护评价

该插件创建于 2019 年，拥有约 6 年历史。从近期提交记录看，最后几次更新集中在 2024 年 10 月之后，但内容主要是编译警告修复、日志系统迁移和代码清理等维护性工作，**没有新增实质性功能**。这表明该插件可能已进入稳定维护期，没有重大的功能开发计划。插件默认未启用（`EnabledByDefault=false`），属于编辑器专用工具。鉴于其为特定行业工作流（DeltaGen/VRED）提供支持，且依赖的外部软件（FBX SDK、特定设计软件）API 可能变化，使用者需注意版本兼容性。对于需要从这些特定软件导入数据的用户，它仍是必要工具；对于一般 FBX 导入需求，UE 内置的 FBX 导入器可能更常用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithFBXImporter)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/datasmith-import-process-in-unreal-engine/) (Datasmith 整体文档)