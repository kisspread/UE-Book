# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图类、编辑器设置、测试资源） |
| 模块 | `USDSchemas` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `GeometryCacheUSD` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-01 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDImporter) | |

## 用途

USD Importer 插件提供完整的 USD (Universal Scene Description) 格式支持，允许从 USD 文件导入资产（静态网格体、骨骼网格体、材质、动画、关卡等），也支持将 Unreal Engine 资产导出为 USD 格式。USDExporter 模块是导出功能的核心，包含多个导出器（Exporter），可将静态网格体、骨骼网格体、几何缓存、材质、动画序列、关卡、关卡序列等内容转换为 USD 文件，并支持丰富的选项控制（LOD、材质烘焙、元数据、子层等）。同时提供 `UUsdConversionBlueprintContext` 和 `UUsdConversionBlueprintLibrary` 两个蓝图可用类，方便脚本自动化导出。

## 使用场景

- **DCC 互操作**：将 UE 中的静态网格体、骨骼网格体或动画序列导出为 `.usda` / `.usdc` / `.usdz` 文件，以便在 Maya、Houdini、Blender 等 DCC 工具中继续编辑。
- **资产归档**：将整个关卡或选定 Actor 导出为 USD 场景，保留层级结构、材质、变换和元数据，用于归档或跨应用交换。
- **自动化管线**：使用 Python 或蓝图脚本批量导出资产，例如将项目中的所有静态网格体按目录结构导出为 USD 每帧文件。
- **材质烘焙**：将 UE 的复杂材质网络烘焙为 UsdPreviewSurface 所需的纹理，并输出为 USD 材质资产。
- **版本比较与增量导出**：利用 `GenerateObjectVersionString` 导出的版本哈希，配合 `bReExportIdenticalAssets` 选项，仅导出发生变化的资产，提升迭代效率。

## 蓝图用法

以下 BlueprintCallable 函数和属性主要来自 `USDExporter` 模块的 `UUsdConversionBlueprintContext`、`UUsdConversionBlueprintLibrary` 以及每个导出器的选项对象。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetStageRootLayer` | 打开或创建 USD 阶段（Stage），设置根层文件路径 | `UUsdConversionBlueprintContext` |
| `SetEditTarget` | 设置当前编辑目标层（后续转换内容写入该层） | `UUsdConversionBlueprintContext` |
| `GetActorsToConvert` | 获取将要参与导出的 Actor 集合（用于关卡导出） | `UUsdConversionBlueprintLibrary` |
| `GenerateObjectVersionString` | 生成对象版本号字符串，可结合导出选项防止重复导出 | `UUsdConversionBlueprintLibrary` |
| `CanExportToLayer` | 检查目标路径是否可以创建 USD 层（文件是否可写） | `UUsdConversionBlueprintLibrary` |
| `InsertSubLayer` | 在指定父层中插入一个子层引用 | `UUsdConversionBlueprintLibrary` |
| `IsUsdAvailable` | 检查运行时是否可使用 USD（USD 库是否加载成功） | `UStaticMeshExporterUsd` |

### 使用示例（蓝图描述）

**示例：导出静态网格体到 USD**

1. 使用“Spawn Actor from Class”创建 `UUsdConversionBlueprintContext` 对象。
2. 调用 `SetStageRootLayer` 指定目标文件路径（如 `"C:/MyUSD/Cube.usda"`）。
3. 调用 `SetEditTarget` 指定编辑层（通常与根层相同）。
4. 遍历网格体 Actor 或直接使用静态网格体资产，调用导出函数（如 `ExportStaticMesh`，属于上下文类，但需注意导出函数在上下文类中定义，例如 `ExportMeshToUsd`）。
5. 完成后调用 `Cleanup` 释放 USD 阶段引用。

> 注：`UUsdConversionBlueprintContext` 提供了 `ExportStaticMesh`、`ExportSkeletalMesh`、`ExportLevel` 等蓝图函数，可以在蓝图中直接调用。由于头文件未完整列出，建议在实际使用中参考 Blueprint 节点面板。

## C++ 用法

### 头文件引入

```cpp
#include "USDExporterModule.h"
#include "StaticMeshExporterUSDOptions.h"
#include "LevelExporterUSDOptions.h"
#include "USDConversionBlueprintLibrary.h"
#include "USDConversionBlueprintContext.h"
```

### 基本用法

**直接使用 UExporter 子类**（引擎标准导出流程）：

```cpp
// 通过资产导出任务（UAssetExportTask）导出静态网格体
UStaticMeshExporterUsd* Exporter = NewObject<UStaticMeshExporterUsd>();
UStaticMesh* Mesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Props/Cube.Cube"));
if (Mesh && Exporter->SupportsObject(Mesh))
{
    const FString FilePath = TEXT("C:/Export/Cube.usda");
    const FString Filename = TEXT("Cube.usda");
    // 设置导出选项
    UStaticMeshExporterUSDOptions* Options = GetMutableDefault<UStaticMeshExporterUSDOptions>();
    Options->StageOptions.FileFormat = EUsdFileFormat::Usda;
    Options->MeshAssetOptions.bUsePayload = false;
    Options->bReExportIdenticalAssets = false;

    UAssetExportTask* Task = NewObject<UAssetExportTask>();
    Task->Object = Mesh;
    Task->Exporter = Exporter;
    Task->Filename = FilePath;
    Task->Options = Options;
    Task->bAutomated = true;

    UExporter::RunAssetExportTask(Task);
}
```
*来源：Header 中 UStaticMeshExporterUsd::ExportBinary 实现；类似模式也可用于其他导出器。*

### 进阶用法

**使用 USD 转换上下文进行批量导出**：

```cpp
#include "USDConversionBlueprintContext.h"

void ExportAllMeshesInLevel(UWorld* World)
{
    UUsdConversionBlueprintContext* Context = NewObject<UUsdConversionBlueprintContext>();
    Context->SetStageRootLayer(FFilePath{ TEXT("C:/Export/LevelExport.usda") });
    Context->SetEditTarget(FFilePath{ TEXT("C:/Export/LevelExport.usda") });

    // 获取要转换的 Actor（通常从关卡收集）
    TSet<AActor*> ActorsToConvert = UUsdConversionBlueprintLibrary::GetActorsToConvert(World);

    // 遍历转换每个 Actor
    for (AActor* Actor : ActorsToConvert)
    {
        // 根据 Actor 类型调用对应的导出函数（此处仅为示意，实际有独立的 ExportActor 函数）
        if (AStaticMeshActor* SMActor = Cast<AStaticMeshActor>(Actor))
        {
            // Context->ExportStaticMeshComponent(SMActor->GetStaticMeshComponent(), ...);
        }
    }

    // 关闭并释放阶段
    Context->Cleanup();
}
```
*来源：UUsdConversionBlueprintContext 定义中的 SetStageRootLayer、SetEditTarget 方法，以及 UUsdConversionBlueprintLibrary::GetActorsToConvert。*

**结合版本字符串的增量导出**：

```cpp
#include "USDConversionBlueprintLibrary.h"

bool ShouldReexport(const UObject* Object, UObject* ExportOptions)
{
    FString VersionString = UUsdConversionBlueprintLibrary::GenerateObjectVersionString(Object, ExportOptions);
    // 可将 VersionString 存储在外部数据库或文件名中，比较后决定是否跳过
    return VersionString != StoredVersion;
}
```
*来源：UUsdConversionBlueprintLibrary::GenerateObjectVersionString。*

## Demo 示例

以下是一个完整的 C++ 示例，它使用 USDExporter 模块将编辑器中的选定静态网格体导出为 USD 文件。假设在编辑器模块中运行（例如自定义 Editor Utility Widget）。

**MyUSDExporter.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyUSDExporter.generated.h"

UCLASS(Blueprintable)
class UMyUSDExporter : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "USD|Demo")
    static bool ExportSelectedStaticMeshToUSD(const FString& OutputFilePath);
};
```

**MyUSDExporter.cpp**
```cpp
#include "MyUSDExporter.h"

#include "Engine/StaticMesh.h"
#include "Editor.h"
#include "Subsystems/EditorActorSubsystem.h"

#include "USDExporterModule.h"
#include "StaticMeshExporterUSDOptions.h"
#include "Exporters/Exporter.h"
#include "AssetExportTask.h"

bool UMyUSDExporter::ExportSelectedStaticMeshToUSD(const FString& OutputFilePath)
{
    // 获取当前选中对象
    UEditorActorSubsystem* EditorActorSubsystem = GEditor->GetEditorSubsystem<UEditorActorSubsystem>();
    TArray<AActor*> SelectedActors = EditorActorSubsystem->GetSelectedActorSet();
    if (SelectedActors.Num() == 0)
    {
        UE_LOG(LogTemp, Warning, TEXT("No actors selected."));
        return false;
    }

    // 假设第一个选中对象包含静态网格组件
    AActor* Actor = SelectedActors[0];
    UStaticMeshComponent* MeshComp = Actor->FindComponentByClass<UStaticMeshComponent>();
    if (!MeshComp || !MeshComp->GetStaticMesh())
    {
        UE_LOG(LogTemp, Warning, TEXT("Selected actor has no static mesh."));
        return false;
    }

    UStaticMesh* Mesh = MeshComp->GetStaticMesh();

    // 创建导出器
    UStaticMeshExporterUsd* Exporter = NewObject<UStaticMeshExporterUsd>();
    if (!Exporter->SupportsObject(Mesh))
    {
        UE_LOG(LogTemp, Warning, TEXT("Exporter does not support this mesh."));
        return false;
    }

    // 准备选项
    UStaticMeshExporterUSDOptions* Options = GetMutableDefault<UStaticMeshExporterUSDOptions>();
    Options->StageOptions.FileFormat = EUsdFileFormat::Usda;
    Options->MeshAssetOptions.bUsePayload = false;
    Options->MeshAssetOptions.bBakeMaterials = false;
    Options->bReExportIdenticalAssets = true; // 总是覆盖

    // 构建导出任务
    UAssetExportTask* Task = NewObject<UAssetExportTask>();
    Task->Object = Mesh;
    Task->Exporter = Exporter;
    Task->Filename = OutputFilePath;
    Task->Options = Options;
    Task->bAutomated = true;
    Task->bReplaceIdentical = true;

    // 执行导出
    UExporter::RunAssetExportTask(Task);

    return true;
}
```

**用法**：在编辑器蓝图或 Python 中调用 `UMyUSDExporter::ExportSelectedStaticMeshToUSD("C:/Temp/Cube.usda")`，即可将选中 Actor 上的静态网格导出。

## 模块依赖

以下为 `USDExporter` 模块独特的依赖项（不包含 Core、Engine、Slate 等标准模块）：

| 模块 | 用途 |
|---|---|
| `USDStage` | USD 阶段操作（打开、创建、编辑目标等） |
| `USDClasses` | USD 资产选项、元数据、转换支持结构体 |
| `UnrealUSDWrapper` | 底层 USD 库的 C++ 包装器 |
| `MaterialBaking` | 材质烘焙为纹理（UsdPreviewSurface 所需） |
| `Sequencer` | 导出关卡序列时涉及序列求值和烘焙 |
| `Landscape` | 导出 landscape 时需要的 LandscapeEditor / Landscape 模块 |

除了上述，还包括常见的 `CoreUObject`、`Engine`、`UnrealEd` 等。

## 维护状态

### 近期更新

- 2025-10-22 a1039b21 USD: Disabled UE allocator in USD for Windows.
- 2025-10-17 be609b71 [Backout] - CL47041219
- 2025-10-17 7ab79237 USD: Disabled UE allocator in USD for Windows.
- 2025-10-03 d887bd60 USD: Use the default collision profile for generated static meshes.
- 2025-10-01 b4449c58 Anim In Engine: Fix broken linked anim sequences.

### 维护评价

USDImporter 插件在 UE 5.7 中持续获得更新，最近的提交集中在运行时稳定性修复（禁用 UE 分配器以避免冲突）、导出碰撞预设改进等。创建于 2025-10-01，距今仅约 1 个月，属于全新功能插件。虽然仍处于 Beta 版本（`IsBetaVersion=true`），但更新频率高且内容实质，推荐使用。已知限制：部分材质转换可能无法完全保留视觉效果；关卡导出时对复杂序列的支持需要验证。整体维护积极，暂无废弃迹象。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDImporter)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/universal-scene-description-in-unreal-engine/)（UE 官方 USD 文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDImporter/Source/USDTests)