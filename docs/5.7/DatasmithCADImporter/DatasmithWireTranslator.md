# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithWireTranslator` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

`DatasmithWireTranslator` 是 `DatasmithCADImporter` 插件中的一个核心模块，专门负责将 Autodesk Alias Studio 的 `.wire` 格式文件导入到 Unreal Engine 中。它通过实现 `IWireInterface` 接口，封装了与 Alias OpenModel SDK 的交互逻辑，将 Alias 的曲面、线框和图层数据转换为 UE 可用的网格（Mesh）和场景（Scene）元素。该模块解决了工业设计软件（如汽车A级曲面设计）与游戏引擎之间高精度CAD数据转换的难题，使得设计师可以直接在UE中查看和评审复杂的Alias模型。

## 使用场景

- 你是汽车设计师，使用 Alias Studio 进行外观A级曲面设计，需要将 `.wire` 模型导入 UE 进行实时可视化、材质评审或制作交互式配置器。
- 你需要将 Alias 的复杂曲面模型转换为 UE 的静态网格体，用于建筑可视化、产品展示或虚拟现实（VR）评审。
- 你的工作流程依赖 Datasmith 进行数据转换，并且需要处理来自 Alias 的特定数据结构（如图层、组）。

## 蓝图用法

该模块主要通过 Datasmith 的通用导入流程工作，其核心接口 `IWireInterface` 是 C++ 层面的。蓝图层面主要通过 `FWireSettings` 结构体来配置导入选项。

### 核心配置结构体

| 属性 | 说明 | 所在类 |
|---|---|---|
| `bUseLayerAsActor` | 是否将 Alias 文件中的图层（Layer）映射为场景大纲中的顶级 Actor。默认为 `true`。 | `FWireSettings` |
| `bMergeGeometryByGroup` | 是否将同一组（Group）下的所有几何节点合并为一个网格体。默认为 `true`。 | `FWireSettings` |

### 使用示例（蓝图描述）

在 Datasmith 导入流程中，当选择导入 `.wire` 文件时，导入对话框会显示由 `FWireSettings` 定义的选项。你可以在导入前勾选或取消勾选“Use Layer As Actor”和“Merge Geometry By Group”来控制导入结果的结构。这些选项会影响最终生成的 Actor 层次和网格体数量。

## C++ 用法

### 头文件引入

```cpp
#include "IWireInterface.h"
```

### 基本用法

该模块的核心是 `IWireInterface` 接口。通常，你不会直接实例化它，而是通过 `DatasmithCADTranslator` 模块提供的工厂方法来获取。以下代码展示了接口的基本使用流程。

```cpp
// 来源: 基于 IWireInterface.h 接口设计推断
#include "IWireInterface.h"

void ImportWireFile(const FString& WireFilePath)
{
    // 1. 通过工厂函数创建 WireInterface 实例 (通常由更高层的 Translator 管理)
    // TSharedPtr<IWireInterface> WireInterface = FWireInterfaceFactory::Create();
    // 注意：实际创建方式取决于插件内部注册机制，此处为示意。

    // 2. 初始化接口，传入文件路径
    if (WireInterface && WireInterface->Initialize(*WireFilePath))
    {
        // 3. 配置导入选项
        FWireSettings Settings;
        Settings.bUseLayerAsActor = true;
        Settings.bMergeGeometryByGroup = false; // 不合并组内几何体
        WireInterface->SetImportSettings(Settings);

        // 4. 设置输出路径（用于缓存中间数据）
        WireInterface->SetOutputPath(FPaths::ProjectSavedDir() / TEXT("WireImportCache"));

        // 5. 创建一个空的 Datasmith 场景并加载数据
        TSharedPtr<IDatasmithScene> Scene = FDatasmithSceneFactory::CreateScene(TEXT("WireImportScene"));
        if (WireInterface->Load(Scene))
        {
            // 场景加载成功，现在可以将 Scene 传递给 Datasmith 的后续处理流程
            // 例如，将其转换为 UE 的 Actor 和资产
        }
    }
}
```

### 进阶用法：加载单个网格体

除了加载整个场景，接口也支持按需加载单个网格体元素。这在需要精细控制或处理大型文件时很有用。

```cpp
// 来源: 基于 IWireInterface.h 接口设计推断
void LoadSingleMeshFromWire(TSharedPtr<IWireInterface> WireInterface, const TSharedPtr<IDatasmithMeshElement>& MeshElement)
{
    if (!WireInterface || !MeshElement.IsValid())
    {
        return;
    }

    FDatasmithMeshElementPayload MeshPayload;
    FDatasmithTessellationOptions TessOptions; // 可以从 FWireSettings 继承或单独设置

    // 调用 LoadStaticMesh 来获取指定网格元素的几何数据
    if (WireInterface->LoadStaticMesh(MeshElement, MeshPayload, TessOptions))
    {
        // MeshPayload 现在包含了该网格的顶点、索引等数据
        // 可以用这些数据创建 UStaticMesh 或进行其他处理
    }
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示了如何使用 `IWireInterface` 接口来加载一个 Alias `.wire` 文件。

**MyWireImporter.h**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"

class IWireInterface;
class IDatasmithScene;

class FMyWireImporter
{
public:
    FMyWireImporter();
    ~FMyWireImporter();

    /** 导入指定的 .wire 文件到一个新的 Datasmith 场景中 */
    bool ImportWireFile(const FString& FilePath);

    /** 获取导入后的场景（如果成功） */
    TSharedPtr<IDatasmithScene> GetImportedScene() const;

private:
    TSharedPtr<IWireInterface> WireInterface;
    TSharedPtr<IDatasmithScene> ImportedScene;
};
```

**MyWireImporter.cpp**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#include "MyWireImporter.h"
#include "IWireInterface.h"
#include "DatasmithSceneFactory.h" // 假设的工厂头文件

FMyWireImporter::FMyWireImporter()
{
    // 注意：实际的创建方式可能需要通过模块接口或工厂函数。
    // 此处为简化示例，假设可以直接构造。
    // WireInterface = MakeShared<FWireInterfaceImpl>();
}

FMyWireImporter::~FMyWireImporter()
{
}

bool FMyWireImporter::ImportWireFile(const FString& FilePath)
{
    if (!WireInterface.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("WireInterface is not initialized."));
        return false;
    }

    // 步骤 1: 初始化
    if (!WireInterface->Initialize(*FilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize WireInterface for file: %s"), *FilePath);
        return false;
    }

    // 步骤 2: 配置设置
    FWireSettings Settings;
    Settings.bUseLayerAsActor = true;
    Settings.bMergeGeometryByGroup = true;
    WireInterface->SetImportSettings(Settings);

    // 步骤 3: 设置输出缓存路径
    FString CachePath = FPaths::Combine(FPaths::ProjectSavedDir(), TEXT("WireCache"), FPaths::GetBaseFilename(FilePath));
    WireInterface->SetOutputPath(CachePath);

    // 步骤 4: 创建目标场景并加载
    ImportedScene = FDatasmithSceneFactory::CreateScene(*FPaths::GetBaseFilename(FilePath));
    if (!WireInterface->Load(ImportedScene))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load wire file into scene."));
        ImportedScene.Reset();
        return false;
    }

    UE_LOG(LogTemp, Log, TEXT("Successfully imported wire file: %s"), *FilePath);
    return true;
}

TSharedPtr<IDatasmithScene> FMyWireImporter::GetImportedScene() const
{
    return ImportedScene;
}
```

## 模块依赖

该模块是 DatasmithCADImporter 插件的一部分，其依赖关系主要在插件内部。

| 模块 | 用途 |
|---|---|
| `CADInterfaces` | 提供与 CAD 内核（如 TechSoft）交互的底层接口和数据结构。 |
| `CADLibrary` | 提供 CAD 数据处理的通用工具库。 |
| `DatasmithCore` | Datasmith 的核心运行时模块，提供场景、元素等基础类型。 |
| `DatasmithRuntime` | Datasmith 的运行时导入和转换逻辑。 |

## 维护状态

### 近期更新

- e22549c2792a Added support for users having AliasStudio 2024.1 and/or 2025.0 installed Removed CVar ds.CADTranslator.Alias.LayersAsActors. A new option has been added to allow users to select that feature from the translator's import dialog Removed CVar ds.CADTranslator.Alias.SewByMaterial. Revisited management of memory allocated by the OpenModel SDK - WIP
  *解读：添加了对新版 Alias 的支持，并将一些控制台变量（CVar）迁移为导入对话框中的用户选项，同时改进了内存管理。*
- 35f0a31b2c17 Addressed miscellaneous crashes: - Clean up the logic in FTopologicalFace::UpdateBBox and remove potential crashes - Modified logic in UE::CADKernel::FindLoopIntersectionsWithIso to only return unique intersection values - Fixed TCurveSamplerAbstract::RunSampling to immediately return if there is no segment to sample - Fixed issue with import of multiple files in Datasmith: The UnloadScene of the translator was not called until all the sources were imported. This was not correct for translators which use SDK with global settings, i.e. OpenModel. - Fixed FAliasModelToCADKernelConverter::AddFace to only add a Face if it has at least one loop. - Made sure debug 'ensure' were not hit in regular builds
  *解读：修复了多个可能导致崩溃的边界情况，改进了多文件导入的流程，并确保了发布版本的稳定性。*
- 184e765d9f5e Temporarily disabled all processing related to thin faces or zones.
  *解读：暂时禁用了与薄面或区域相关的处理，可能是因为存在未解决的稳定性或正确性问题。*

### 维护评价

该模块仍在**活跃维护**中。最近的提交（2025年）显示 Epic 正在持续更新其对新版 Alias 软件的支持，并积极修复已知的崩溃和稳定性问题。虽然有一个功能（薄面处理）被暂时禁用，但这表明团队正在谨慎地处理复杂问题。作为 Datasmith 企业级功能的一部分，它得到了持续的关注。**推荐使用**，但需注意其依赖于特定的 Alias OpenModel SDK，并且某些高级功能（如薄面处理）可能暂时不可用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter/Source/DatasmithWireTranslator)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests)