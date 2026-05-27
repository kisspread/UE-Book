# Datasmith FBX Importer

> Adds support for importing content from DeltaGen and VRED into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | Datasmith FBX 专业导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithVREDTranslator` (Editor), `DatasmithDeltaGenTranslator` (Editor), `DatasmithFBXTranslator` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithFBXImporter) | |

## 用途

此插件是 **Datasmith 框架的一个专用翻译器扩展**，其核心目的并非简单地导入通用 FBX 文件，而是**完整地解析并转化由特定工业设计软件（VRED 和 DeltaGen）导出的、附带丰富元数据的 FBX 及相关辅助文件**。普通 FBX 导入器无法处理这些软件特有的数据，如复杂的材质定义（.mats）、产品变体配置（.var）、灯光参数（.lights）和动画片段（.clips）。该插件解决了在 VRED/DeltaGen 到 UE5 的工作流中，关键设计意图和交互逻辑丢失的问题，实现了高保真的资产和场景转换。

## 使用场景

- 你是汽车设计师或产品可视化艺术家，使用 **VRED** 进行渲染和评审，需要将完整的汽车模型（包含变体、动画和精确材质）导入 UE5 进行实时渲染或虚拟评审。
- 你使用 **DeltaGen** 创建高质量的产品可视化场景，希望将场景及其复杂的材质关系无损地迁移到 UE5 的 Datasmith 工作流中。
- 你的工作流依赖于 VRED 导出的 FBX，但除了几何体，还需要导入其配套的 `.var`、`.mats`、`.clips` 等文件以保持资产完整性。

## 蓝图用法

该插件主要作为底层的 Datasmith 翻译器运行，不直接暴露大量蓝图节点。其交互主要通过标准的 Datasmith 导入界面进行。然而，它定义的一些数据结构（如变体选项）可以在蓝图中使用，用于数据处理或自定义逻辑。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EVREDCppVariantType` (枚举) | 定义了 VRED 变体的类型（相机、几何体、材质等） | `DatasmithVREDImportData` |
| `FVREDCppVariant` (结构体) | 表示一个完整的 VRED 变体，包含其类型和所有选项数据 | `DatasmithVREDImportData` |

### 使用示例（蓝图描述）

由于该插件是编辑器导入器，主要蓝图交互发生在导入管线内部。开发者可以在蓝图中创建一个 `FVREDCppVariant` 结构体数组，用于存储解析后的变体数据，但这通常由导入器在后台完成。

## C++ 用法

主要用法是作为 Datasmith 翻译器的内部实现。若需扩展或集成，可参考其提供的接口和类。

### 头文件引入

```cpp
#include "DatasmithVREDTranslatorModule.h"
#include "DatasmithVREDImporter.h"
```

### 基本用法

检查 VRED 翻译器模块是否可用，并获取其引用。

```cpp
// 检查模块状态
if (IDatasmithVREDTranslatorModule::IsAvailable())
{
    // 获取模块单例
    IDatasmithVREDTranslatorModule& VREDModule = IDatasmithVREDTranslatorModule::Get();
    // ... 可进行进一步操作，如注册自定义处理程序
}
```

### 进阶用法

直接使用 `FDatasmithVREDImporter` 类来控制导入过程。通常，`FDatasmithVREDTranslator` 会内部使用这个类。

```cpp
// 假设已有 Datasmith 场景对象和导入选项
TSharedRef<IDatasmithScene> MyScene = IDatasmithScene::Create();
UDatasmithVREDImportOptions* Options = GetMutableDefault<UDatasmithVREDImportOptions>();

// 创建 VRED 导入器实例
FDatasmithVREDImporter VREDImporter(MyScene, Options);

// 1. 打开并解析 VRED 导出的 FBX 文件及其关联文件
if (VREDImporter.OpenFile(TEXT("C:/Path/To/YourModel.fbx")))
{
    // 2. 将解析的场景数据转换并写入 Datasmith 场景
    if (VREDImporter.SendSceneToDatasmith())
    {
        // 此时 MyScene 已填充数据，可用于后续的 Unreal 场景创建
    }
}

// 3. 清理内部资源
VREDImporter.UnloadScene();
```

## Demo 示例

以下是一个在编辑器工具或自动化脚本中手动调用 VRED 导入器的最小示例。

**MyVREDImporter.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "DatasmithVREDImporter.h"

class UDatasmithVREDImportOptions;

class FMyVREDImportHelper
{
public:
    static bool ImportVREDScene(const FString& FBXPath, TSharedRef<IDatasmithScene>& OutScene);
};
```

**MyVREDImporter.cpp**
```cpp
#include "MyVREDImporter.h"
#include "DatasmithVREDImportOptions.h"
#include "DatasmithSceneFactory.h"

bool FMyVREDImportHelper::ImportVREDScene(const FString& FBXPath, TSharedRef<IDatasmithScene>& OutScene)
{
    // 使用默认或自定义的导入选项
    UDatasmithVREDImportOptions* Options = GetMutableDefault<UDatasmithVREDImportOptions>();
    
    FDatasmithVREDImporter Importer(OutScene, Options);
    
    if (Importer.OpenFile(FBXPath))
    {
        if (Importer.SendSceneToDatasmith())
        {
            Importer.UnloadScene();
            UE_LOG(LogTemp, Log, TEXT("成功导入 VRED 场景: %s"), *FBXPath);
            return true;
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("转换 Datasmith 场景失败: %s"), *FBXPath);
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("无法打开 VRED 文件: %s"), *FBXPath);
    }
    
    Importer.UnloadScene();
    return false;
}
```

## 模块依赖

此插件依赖于 Datasmith 核心插件和 FBX SDK，无需为你的模块添加额外的特殊依赖，除非你计划直接使用其内部数据结构。

| 模块 | 用途 |
|---|---|
| `DatasmithImporter` | 提供核心的 Datasmith 导入管线和翻译器接口 |
| `DatasmithContent` | 提供 Datasmith 资产类型（如材质实例） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数导致的编译器警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF，适配引擎更新。 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复“代码不可达”的编译错误。 |
| 2025-03-13 | `b059f7b4` | Fix trivial unreachable code warnings. | 修复简单的不可达代码警告。 |
| 2024-10-02 | `0a14cf0e` | Update VRED python exporter to support API changes in VRED | 更新VRED的Python导出器以支持VRED API变更。 |

### 维护评价

该插件创建于 2019 年，历史较长。从 git 日志看，**近两年的更新均为基础的编译兼容性修复和警告清理**（如迁移日志宏、修复浮点警告），**没有功能性增强或新特性引入**。这表明该插件目前处于**低活动度的维护状态**，可能已达到其设计目标的稳定阶段。作为一个服务于特定工业软件（VRED/DeltaGen）导入的 **Enterprise（企业）** 功能插件，其稳定性优先于新功能。对于目标用户（VRED/DeltaGen 用户）来说，它仍然是将资产导入 UE5 的关键且唯一途径，因此**推荐使用**，但用户应知晓其更新节奏缓慢，可能不会迅速支持新引擎版本中的前沿特性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithFBXImporter)
- [官方文档](https://docs.unrealengine.com)（请搜索 Datasmith 和 VRED/DeltaGen 导入相关文档）