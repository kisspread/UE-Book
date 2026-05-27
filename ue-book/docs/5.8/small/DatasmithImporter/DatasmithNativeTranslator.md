# Datasmith Importer

> Importer for Datasmith files.

| 属性 | 值 |
|---|---|
| 中文名 | 数据石导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithImporter` (Runtime), `DatasmithTranslator` (Runtime), `DatasmithNativeTranslator` (Runtime), `DatasmithExternalSource` (Runtime), `ExternalSource` (Runtime), `DirectLinkExtension` (Runtime), `DirectLinkExtensionEditor` (Runtime), `DirectLinkTest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter) | |

## 用途

Datasmith 是 Epic Games 面向建筑、工程、制造（AEC/MFG）行业推出的数据交换方案。本插件负责将 `.udatasmith` 格式文件以及通过 DirectLink 实时同步的场景数据导入 Unreal Engine。

核心解决的问题是：**将 CAD/BIM/DCC 软件（如 3ds Max、Revit、SketchUp、CATIA 等）的复杂工程场景高效、高保真地转换为 UE 可用资产**，包括几何体、材质、光照、层次结构、动画序列等。相较于标准 FBX 导入，Datasmith 能保留更多工程级元数据和场景层次。

当前文档聚焦的 `DatasmithNativeTranslator` 模块是 Datasmith 原生 `.udatasmith` 文件格式的解析器，负责读取 Datasmith 专有二进制格式并转换为引擎内部的 `IDatasmithScene` 表示。

**注意**：本插件默认未启用（`EnabledByDefault=false`），需要在编辑器插件设置中手动启用，或在项目 `.uproject` 中显式声明。

## 使用场景

- 你从 **3ds Max** 通过 Datasmith Exporter 导出了建筑可视化场景 → 用 Datasmith Importer 导入 UE
- 你从 **Revit / SketchUp / CATIA / SolidWorks** 等 CAD/BIM 工具导出了工程模型 → 用 Datasmith Importer 保持材质和层次结构
- 你需要通过 **DirectLink** 实时同步 DCC 工具中的场景变更 → 用 DirectLinkExtension 模块
- 你需要从外部数据源（HTTP、文件系统等）加载 Datasmith 场景 → 用 ExternalSource 模块

## 蓝图用法

`DatasmithNativeTranslator` 模块本身不暴露 `BlueprintCallable` 函数——它是作为引擎内部翻译层运作的。蓝图层面的 Datasmith 导入操作通常通过编辑器菜单（`File > Import Into Level`）触发，或通过 `UDatasmithStaticMeshImportFactory` 等工厂类自动调度。

与蓝图交互的核心入口位于 `DatasmithImporter` 模块（非当前模块），此处仅列出翻译层的接口概念：

### 核心接口

| 接口方法 | 说明 | 所在类 |
|---|---|---|
| `Initialize` | 声明翻译器能力（支持的元素类型） | `FDatasmithNativeTranslator` |
| `LoadScene` | 读取 `.udatasmith` 文件并填充 `IDatasmithScene` | `FDatasmithNativeTranslator` |
| `LoadStaticMesh` | 按需加载特定网格体的几何数据 | `FDatasmithNativeTranslator` |
| `LoadLevelSequence` | 加载关卡序列动画数据 | `FDatasmithNativeTranslator` |
| `LoadCloth` | ⚠️ 已废弃（UE 5.5），布料导入不再支持 | `FDatasmithNativeTranslator` |

### 使用示例

Datasmith 的导入流程由引擎调度器自动管理，典型调用链为：

1. 用户选择 `.udatasmith` 文件导入
2. 引擎创建 `FDatasmithNativeTranslator` 实例
3. 调用 `Initialize()` 获取能力描述
4. 调用 `LoadScene()` 加载场景结构
5. 对场景中的每个网格体元素按需调用 `LoadStaticMesh()`
6. 对场景中的每个序列元素按需调用 `LoadLevelSequence()`

## C++ 用法

### 头文件引入

```cpp
#include "DatasmithNativeTranslator.h"
#include "DatasmithNativeTranslatorModule.h"
```

### 基本用法

通过翻译器接口加载 Datasmith 原生文件场景：

```cpp
// 包含必要的头文件
#include "DatasmithNativeTranslator.h"
#include "DatasmithSceneFactory.h"
#include "IDatasmithSceneElements.h"

// 创建翻译器实例
TSharedRef<FDatasmithNativeTranslator> Translator = MakeShared<FDatasmithNativeTranslator>();

// 声明能力
FDatasmithTranslatorCapabilities Capabilities;
Translator->Initialize(Capabilities);

// 创建输出场景
TSharedRef<IDatasmithScene> Scene = FDatasmithSceneFactory::CreateScene(TEXT("MyScene"));

// 加载场景结构
const FString FilePath = TEXT("/path/to/scene.udatasmith");
bool bSuccess = Translator->LoadScene(Scene);
```

### 按需加载网格体

```cpp
// 从已加载的场景中获取网格体元素
TSharedPtr<IDatasmithMeshElement> MeshElement = /* 从 Scene 中遍历获取 */;

if (MeshElement.IsValid())
{
    FDatasmithMeshElementPayload MeshPayload;
    bool bLoaded = Translator->LoadStaticMesh(MeshElement.ToSharedRef(), MeshPayload);

    if (bLoaded)
    {
        // MeshPayload 包含几何体数据，可用于创建 UStaticMesh
    }
}
```

### 文件路径解析

`FDatasmithNativeTranslator` 提供两个静态工具方法用于解析资源路径：

```cpp
// 解析单个文件路径（在给定的资源搜索路径列表中查找）
FString ResolvedPath = FDatasmithNativeTranslator::ResolveFilePath(
    TEXT("Textures/wood_diffuse.png"),
    { TEXT("/Game/Assets/Imported/"), TEXT("D:/Project/Assets/") }
);

// 批量解析场景中所有文件引用
TArray<FString> ResourcePaths = { TEXT("/Game/Imported/") };
FDatasmithNativeTranslator::ResolveSceneFilePaths(Scene, ResourcePaths);
```

## Demo 示例

以下演示如何在编辑器工具中使用 `DatasmithNativeTranslator` 加载场景：

```cpp
// DatasmithLoaderExample.h
#pragma once

#include "CoreMinimal.h"

class IDatasmithScene;

class FDatasmithLoaderExample
{
public:
    /** 加载指定的 .udatasmith 文件并返回场景 */
    static TSharedPtr<IDatasmithScene> LoadDatasmithFile(const FString& FilePath);

    /** 列出场景中的所有网格体元素 */
    static void ListMeshElements(TSharedRef<IDatasmithScene> Scene);
};
```

```cpp
// DatasmithLoaderExample.cpp
#include "DatasmithLoaderExample.h"

#include "DatasmithNativeTranslator.h"
#include "DatasmithNativeTranslatorModule.h"
#include "DatasmithSceneFactory.h"
#include "IDatasmithSceneElements.h"

TSharedPtr<IDatasmithScene> FDatasmithLoaderExample::LoadDatasmithFile(const FString& FilePath)
{
    // 检查翻译器模块是否可用
    if (!FDatasmithNativeTranslatorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("DatasmithNativeTranslator module is not loaded."));
        return nullptr;
    }

    // 创建翻译器
    TSharedRef<FDatasmithNativeTranslator> Translator = MakeShared<FDatasmithNativeTranslator>();

    // 初始化并获取能力描述
    FDatasmithTranslatorCapabilities Capabilities;
    Translator->Initialize(Capabilities);

    // 创建空场景并加载
    TSharedRef<IDatasmithScene> Scene = FDatasmithSceneFactory::CreateScene(TEXT("ImportedScene"));
    if (!Translator->LoadScene(Scene))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load Datasmith scene: %s"), *FilePath);
        return nullptr;
    }

    UE_LOG(LogTemp, Log, TEXT("Successfully loaded scene with %d children."), Scene->GetChildrenCount());
    return Scene;
}

void FDatasmithLoaderExample::ListMeshElements(TSharedRef<IDatasmithScene> Scene)
{
    for (int32 i = 0; i < Scene->GetChildrenCount(); ++i)
    {
        TSharedPtr<IDatasmithBaseElement> Child = Scene->GetChild(i);
        if (Child.IsValid() && Child->IsA(EDatasmithElementType::StaticMesh))
        {
            TSharedRef<IDatasmithMeshElement> Mesh =
                StaticCastSharedRef<IDatasmithMeshElement>(Child.ToSharedRef());

            UE_LOG(LogTemp, Log, TEXT("Mesh: %s, Source: %s"),
                *Mesh->GetName(), *Mesh->GetFile());
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DatasmithTranslator` | Datasmith 翻译器基础接口（`IDatasmithTranslator`） |
| `DatasmithCore` | Datasmith 核心数据模型（`IDatasmithScene`、元素类型定义） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 到 float 的截断警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移 UE_LOG 宏到新的 UE_LOGF 格式 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introd | 废弃旧版对象遍历 API，引入替代方案 |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 规范纹理属性修改，加入 PreEditChange/PostEditChange 包装 |
| 2026-03-05 | `1adb9f68` | New material translator work: | 新材质翻译器开发工作 |

### 维护评价

- **创建时间**：2019 年 10 月，随 UE4 Enterprise 分支从内部仓库迁移而来
- **维护状态**：**活跃维护中** —— 2026 年仍有持续的功能更新和代码清理，尤其在材质翻译器方面有新功能开发
- **活跃度**：每月至少 1-2 次有意义的提交，表明该模块仍处于积极开发状态
- **特殊说明**：
  - 插件默认未启用（`EnabledByDefault=false`），属于企业版功能，需要用户主动开启
  - UE 5.5 起废弃了实验性布料（Cloth）导入功能
  - 该插件与 Datasmith CAD 导入器（`Engine/Plugins/Enterprise/CadImporter`）配合使用，覆盖完整的 CAD/BIM 数据管线
- **推荐使用**：✅ 强烈推荐 —— 对于建筑可视化、工业数字孪生、制造业产品可视化等场景，Datasmith 是 Epic 官方推荐的数据交换方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter/Source/DirectLinkTest)