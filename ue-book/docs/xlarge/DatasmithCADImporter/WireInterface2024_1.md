# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

DatasmithCADImporter 是一个企业级插件，其核心功能是将各种专业的 CAD（计算机辅助设计）文件格式（如 CATIA, NX, SolidWorks, Alias, Rhino 等）高效、准确地导入到 Unreal Engine 中。它不仅仅是一个简单的格式转换器，而是一个完整的处理管线，能够解析 CAD 文件中的复杂几何体（包括参数化曲面、B-Rep 实体）、材质、层级结构、元数据等信息，并将其转换为 UE 可用的静态网格体、材质和场景层级。

该插件解决了工业设计、建筑、工程和制造（AEC & MFG）领域专业人士将庞大的 CAD 设计数据引入实时 3D 环境（用于可视化、仿真、培训或销售配置）时面临的核心挑战：保持设计意图、处理超大规模装配体以及优化性能。它通过多进程处理（Dispatcher）和专门的几何内核（如 CADKernel）来应对这些挑战。

## 使用场景

- 你是一名汽车设计师，需要将 Alias 或 CATIA 设计的整车模型导入 UE，用于创建交互式配置器或虚拟展厅。
- 你是一名建筑师或工程师，需要将 Revit、ArchiCAD 或 SolidWorks 的建筑/机械模型导入 UE，进行施工流程模拟或设备维护培训。
- 你是一名产品设计师，需要将 Rhino 或 NX 的复杂曲面模型导入 UE，进行高质量的产品可视化渲染。
- 你需要处理包含成千上万个零件的大型装配体（如飞机、工厂），并希望利用 UE 的 Nanite 和 Lumen 技术进行实时渲染。

## 蓝图用法

该插件主要作为 Datasmith 导入管线的一部分工作，其核心功能通过 Datasmith 的导入界面和 C++ API 暴露。直接的蓝图节点较少，主要集中在控制导入过程和访问导入后的资产。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Import Datasmith Scene` | 通过 Datasmith 导入器导入 `.udatasmith` 文件，该文件可由 CAD 文件转换而来。 | `UDatasmithImportFactory` |
| `Get Imported Static Mesh` | 在导入完成后，通过资产路径获取导入的静态网格体资产。 | `UAssetRegistry` |

### 使用示例（蓝图描述）

1.  **触发导入**：在蓝图中，使用 `Import Datasmith Scene` 节点，指定一个由 DatasmithCADImporter 预先转换好的 `.udatasmith` 文件路径。该过程是异步的。
2.  **监听完成**：绑定 `OnImportCompleted` 委托，在导入完成后执行后续逻辑。
3.  **访问资产**：在完成回调中，使用 `Get Imported Static Mesh` 或直接通过资产路径（如 `/Game/ImportedModel/MyMesh`）加载导入的网格体和材质，并将其应用到场景中的 Actor 上。

## C++ 用法

### 头文件引入

```cpp
// 核心翻译器接口
#include "DatasmithCADTranslator.h"
// Wire (Alias) 格式特定模块
#include "WireInterfaceModule.h"
// CAD 几何处理库
#include "CADLibrary.h"
// 多进程调度器
#include "DatasmithDispatcher.h"
```

### 基本用法

以下代码展示了如何以编程方式触发一个 CAD 文件的导入过程，这是插件内部翻译器工作的典型模式。

```cpp
// 来源: DatasmithCADTranslator 模块内部逻辑
#include "IDatasmithTranslator.h"
#include "DatasmithSceneFactory.h"

void ImportCADFile(const FString& CADFilePath)
{
    // 1. 获取 CAD 翻译器模块
    IDatasmithTranslator* Translator = FDatasmithCADTranslatorModule::Get().GetTranslator();
    if (!Translator)
    {
        UE_LOG(LogTemp, Error, TEXT("CAD Translator not available."));
        return;
    }

    // 2. 初始化翻译器并打开源文件
    TSharedRef<IDatasmithScene> Scene = FDatasmithSceneFactory::CreateScene(TEXT("MyCADImport"));
    Translator->SetScene(Scene);
    if (!Translator->OpenSource(CADFilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open CAD file: %s"), *CADFilePath);
        return;
    }

    // 3. 执行翻译（此过程可能耗时且复杂）
    Translator->Translate();

    // 4. 此时，`Scene` 对象中已填充了从 CAD 文件解析出的网格体、材质、层级等数据。
    //    后续步骤通常是将这个 Scene 对象传递给 Datasmith 的资产创建流程。
    UE_LOG(LogTemp, Log, TEXT("CAD file translated successfully. Scene has %d meshes."), Scene->GetMeshesCount());

    // 5. 清理
    Translator->CloseSource();
}
```

### 进阶用法

对于超大规模 CAD 装配体，插件使用 `DatasmithDispatcher` 进行多进程处理以提升性能。以下是一个简化的调度逻辑示例。

```cpp
// 来源: DatasmithDispatcher 模块
#include "DatasmithDispatcher.h"
#include "DatasmithWorker.h"

void DispatchCADImport(const FString& LargeAssemblyPath)
{
    // 1. 创建调度器
    FDatasmithDispatcher Dispatcher;

    // 2. 将大型装配体分解为多个子任务（例如按组件或几何体分组）
    TArray<FDatasmithImportTask> Tasks;
    // ... (此处省略复杂的任务分解逻辑) ...
    Tasks.Add(FDatasmithImportTask(LargeAssemblyPath, TEXT("Part1")));
    Tasks.Add(FDatasmithImportTask(LargeAssemblyPath, TEXT("Part2")));

    // 3. 将任务分发给工作进程
    Dispatcher.DispatchTasks(Tasks);

    // 4. 等待所有任务完成并收集结果
    Dispatcher.WaitForCompletion();

    // 5. 合并来自各个工作进程的结果
    TSharedRef<IDatasmithScene> MergedScene = Dispatcher.GetMergedResult();
    // ... 后续处理合并后的场景 ...
}
```

## Demo 示例

一个最小化的示例，展示如何创建一个自定义的 Datasmith 翻译器模块，该模块利用 `CADLibrary` 处理几何数据。

**MyCustomCADTranslator.h**
```cpp
#pragma once

#include "IDatasmithTranslator.h"
#include "CADLibrary.h"

class FMyCustomCADTranslator : public IDatasmithTranslator
{
public:
    virtual ~FMyCustomCADTranslator() = default;

    // IDatasmithTranslator 接口实现
    virtual void Initialize(const TSharedRef<IDatasmithScene>& InScene) override;
    virtual bool OpenSource(const FString& InFilePath) override;
    virtual void Translate() override;
    virtual void CloseSource() override;

private:
    TSharedPtr<IDatasmithScene> Scene;
    CADLibrary::FMeshDescription MeshData; // 使用 CADLibrary 处理后的网格数据
};
```

**MyCustomCADTranslator.cpp**
```cpp
#include "MyCustomCADTranslator.h"
#include "DatasmithSceneFactory.h"

void FMyCustomCADTranslator::Initialize(const TSharedRef<IDatasmithScene>& InScene)
{
    Scene = InScene;
}

bool FMyCustomCADTranslator::OpenSource(const FString& InFilePath)
{
    // 使用 CADLibrary 读取 CAD 文件并填充 MeshData
    // 这是一个简化的示意，实际需要处理格式检测、几何内核调用等
    CADLibrary::FMeshDescription RawMesh;
    if (!CADLibrary::ReadCADFile(InFilePath, RawMesh))
    {
        return false;
    }

    // 对原始网格进行优化（如曲面细分、法线计算）
    MeshData = CADLibrary::TessellateAndOptimize(RawMesh);
    return true;
}

void FMyCustomCADTranslator::Translate()
{
    if (!Scene.IsValid() || MeshData.IsEmpty())
    {
        return;
    }

    // 1. 创建静态网格体元素
    TSharedRef<IDatasmithMeshElement> MeshElement = FDatasmithSceneFactory::CreateMesh(TEXT("ImportedMesh"));
    // 2. 将 CADLibrary 处理后的网格数据设置到 MeshElement 中
    // MeshElement->SetMeshDescription(MeshData); // 伪代码，实际接口可能不同
    Scene->AddMesh(MeshElement);

    // 3. 创建材质元素（根据 CAD 文件中的材质信息）
    TSharedRef<IDatasmithMaterialElement> MaterialElement = FDatasmithSceneFactory::CreateMaterial(TEXT("CADMaterial"));
    Scene->AddMaterial(MaterialElement);

    // 4. 创建 Actor 并关联网格和材质
    TSharedRef<IDatasmithActorElement> ActorElement = FDatasmithSceneFactory::CreateActor(TEXT("ImportedActor"));
    ActorElement->SetMesh(MeshElement);
    ActorElement->SetMaterial(0, MaterialElement); // 假设槽位0
    Scene->AddActor(ActorElement);
}

void FMyCustomCADTranslator::CloseSource()
{
    MeshData.Reset();
    Scene.Reset();
}
```

## 模块依赖

该插件依赖于特定的第三方库来解析不同的 CAD 格式。

| 模块 | 用途 |
|---|---|
| `TechSoft` | 用于读取和解析多种主流 CAD 格式（如 CATIA, NX, SolidWorks, STEP, IGES）的核心库。 |
| `OpenNurbs6` | 用于读取和解析 Rhino 3DM 文件格式的库。 |

## 维护状态

### 近期更新

- `90f00dd86ae6` Added support for Alias 2026.0
  *解读：为最新的 Alias 2026.0 版本添加了支持，表明插件在持续跟进上游 CAD 软件的更新。*
- `39994edb437c` [Wire] Corrected missing incrementation The mesh was properly sectioned but the missing increment was assigning the same material to each section Somehow the increment step was deleted before submission :-(
  *解读：修复了 Alias (.wire) 文件导入时的一个材质分配错误，属于重要的 Bug 修复。*
- `61d36ec7677f` [Wire] Fixed missing colors when using group option - Fixed coding error in FDatasmithStaticMeshImporter::SetupStaticMesh which was eliminating sections when some were sharing the same material - Simplified material assignment to MeshElement's slots. - removed redundant material assignment on MeshActor. - Fixed wrong material slot name used in FMeshDescription. It has to be an integer to work in Datasmith import.
  *解读：一系列针对 Alias 文件导入的修复和优化，涉及颜色、材质分配和网格体设置，显著提升了导入的准确性和代码健壮性。*

### 维护评价

**活跃维护**。该插件创建于 2019 年，已有约 6 年历史，属于企业级核心功能。从近期提交记录看，Epic 仍在积极维护，包括：
1.  **功能更新**：持续添加对新版本 CAD 软件（如 Alias 2026.0）的支持。
2.  **Bug 修复**：定期修复导入过程中的各种问题，特别是材质和几何体相关的错误。
3.  **代码优化**：对导入逻辑进行简化和重构。

插件默认未启用 (`EnabledByDefault: false`)，这是企业功能的常见设置，需要用户手动在插件列表中启用。考虑到其重要性和持续的维护，**强烈推荐**在需要处理 CAD 数据的项目中使用此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests)