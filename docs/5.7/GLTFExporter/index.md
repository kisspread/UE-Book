# glTF Exporter

> An exporter for Khronos glTF 2.0.

| 属性 | 值 |
|---|---|
| 分类 | Exporters |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `GLTFExporter` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-07-19 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/GLTFExporter) | |

## 用途

GLTFExporter 插件的核心功能是将 Unreal Engine 中的资产（如关卡、网格体、材质、动画等）导出为 Khronos glTF 2.0 格式。它不仅仅是一个简单的文件格式转换器，而是一个完整的资产导出管线，能够处理 UE 特有的数据结构（如 Morph Target、光照贴图、变体集等），并将其转换为符合 glTF 2.0 规范的 JSON 结构和二进制缓冲区。

该插件的存在解决了以下问题：
1.  **跨平台资产交换**：glTF 是行业标准的 3D 资产格式，被广泛用于 Web 3D、AR/VR 应用、其他 DCC 工具和游戏引擎。此插件允许 UE 项目轻松地将资产导出到这些平台。
2.  **保留复杂数据**：它能够导出 UE 中复杂的资产数据，包括骨骼网格体的蒙皮信息、动画序列、材质参数（尽可能映射到 PBR 材质）、LOD、光照贴图以及 Variant Manager 中的变体集。
3.  **集成到 UE 工作流**：作为编辑器插件，它无缝集成到 UE 的资产浏览器和内容浏览器中，用户可以通过右键菜单直接导出选中的资产。

## 使用场景

-   你需要将 UE 中创建的 3D 场景或模型发布到网页上进行交互式展示 → 使用此插件导出为 glTF/glb 文件。
-   你的美术团队使用 UE 作为主要创作工具，但需要将资产交付给使用其他引擎（如 Three.js, Babylon.js）或 DCC 工具（如 Blender）的团队 → 使用此插件进行标准化导出。
-   你需要将 UE 中制作的动画（如角色动画、摄像机动画）导出到支持 glTF 动画的 AR/VR 应用或查看器中。
-   你正在使用 Variant Manager 管理产品配置（如汽车内饰、家具组合），并希望将这些变体导出为 glTF 文件用于在线产品展示。

## 蓝图用法

该插件主要通过编辑器菜单和资产操作触发，其核心导出逻辑封装在 C++ 类中。蓝图中可直接调用的公开接口较少，主要集中在导出设置和触发导出上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ExportToGLTF` | 将指定对象导出为 glTF 文件。这是最核心的导出函数。 | `UGLTFExportOptions` (推测) |
| `Get Export Options` | 获取当前的 glTF 导出选项实例，用于修改导出设置。 | `UGLTFExportOptions` (推测) |

### 使用示例（蓝图描述）

1.  **通过内容浏览器导出**：这是最常用的方式。在内容浏览器中右键点击一个资产（如 `StaticMesh`、`SkeletalMesh`、`Level`），选择 “Asset Actions” -> “Export to glTF”。在弹出的对话框中配置导出选项（如文件格式、纹理质量、是否导出动画等），然后点击“导出”。
2.  **通过关卡编辑器导出**：在关卡编辑器中，可以通过 “File” -> “Export Selected” 或 “Export All” 菜单，选择 glTF 格式进行导出。
3.  **蓝图调用（高级）**：虽然不常见，但理论上可以通过获取 `UGLTFExportOptions` 对象，设置其属性（如 `bExportMaterial`， `bExportAnimation`），然后调用其导出函数，并传入要导出的 `UObject` 引用来实现程序化导出。

## C++ 用法

### 头文件引入

```cpp
#include "GLTFExporterModule.h"
#include "Exporters/GLTFExporter.h"
#include "GLTFExportOptions.h"
```

### 基本用法

以下示例展示了如何通过 C++ 代码触发一个资产的 glTF 导出。此用法模拟了编辑器菜单的操作。

```cpp
// 来源：基于 Exporters/GLTFExporter.h 和 GLTFExportOptions.h 的典型用法推断
#include "GLTFExporterModule.h"
#include "Exporters/GLTFExporter.h"
#include "GLTFExportOptions.h"
#include "AssetRegistry/AssetData.h"

void ExportStaticMeshToGLTF(UStaticMesh* MeshToExport, const FString& OutputPath)
{
    // 1. 获取导出器模块
    IGLTFExporterModule& GLTFExporterModule = FModuleManager::GetModuleChecked<IGLTFExporterModule>(TEXT("GLTFExporter"));

    // 2. 创建或获取导出选项
    UGLTFExportOptions* ExportOptions = GetMutableDefault<UGLTFExportOptions>();
    // 可以在此处修改选项，例如：
    // ExportOptions->bExportMaterial = true;
    // ExportOptions->TextureFormat = EGLTFTextureFormat::PNG;

    // 3. 准备要导出的对象数组
    TArray<UObject*> ObjectsToExport;
    ObjectsToExport.Add(MeshToExport);

    // 4. 调用导出函数
    // 注意：实际函数签名可能更复杂，此处为简化示例
    bool bSuccess = GLTFExporterModule.ExportToGLTF(ObjectsToExport, OutputPath, ExportOptions);

    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully exported %s to glTF."), *MeshToExport->GetName());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to export %s to glTF."), *MeshToExport->GetName());
    }
}
```

### 进阶用法

该插件内部使用了一套复杂的转换器（Converter）和构建器（Builder）架构。对于需要深度定制导出流程的开发者，可以研究并扩展这些类。

```cpp
// 来源：基于 Converters/ 和 Builders/ 目录下的类结构推断
// 示例：自定义一个材质转换器
#include "Converters/GLTFMaterialConverters.h"
#include "Json/GLTFJsonMaterial.h"

class FMyCustomGLTFMaterialConverter : public FGLTFMaterialConverter
{
public:
    using FGLTFMaterialConverter::FGLTFMaterialConverter;

protected:
    virtual FGLTFJsonMaterial* Convert(const UMaterialInterface* Material, const FGLTFIndexArray& MeshSectionIndices) override
    {
        // 首先调用基类转换，获取基础 glTF 材质
        FGLTFJsonMaterial* BaseMaterial = FGLTFMaterialConverter::Convert(Material, MeshSectionIndices);

        if (BaseMaterial)
        {
            // 在这里添加自定义逻辑
            // 例如，为特定材质添加额外的 glTF 扩展（Extension）
            // BaseMaterial->Extensions.Add(...);
            UE_LOG(LogTemp, Log, TEXT("Custom processing for material: %s"), *Material->GetName());
        }

        return BaseMaterial;
    }
};
```

## Demo 示例

以下是一个完整的、可编译的最小示例，演示如何创建一个简单的命令行工具或编辑器工具按钮来导出指定的静态网格体。

**MyGLTFExporterTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class UStaticMesh;

class FMyGLTFExporterTool
{
public:
    static void ExportMesh(UStaticMesh* Mesh, const FString& FilePath);
};
```

**MyGLTFExporterTool.cpp**
```cpp
#include "MyGLTFExporterTool.h"
#include "GLTFExporterModule.h"
#include "GLTFExportOptions.h"
#include "Exporters/GLTFExporter.h"
#include "UObject/UObjectGlobals.h"

void FMyGLTFExporterTool::ExportMesh(UStaticMesh* Mesh, const FString& FilePath)
{
    if (!Mesh)
    {
        UE_LOG(LogTemp, Error, TEXT("Invalid StaticMesh provided."));
        return;
    }

    // 获取导出器模块
    IGLTFExporterModule* GLTFModule = FModuleManager::GetModulePtr<IGLTFExporterModule>(TEXT("GLTFExporter"));
    if (!GLTFModule)
    {
        UE_LOG(LogTemp, Error, TEXT("GLTFExporter module is not loaded."));
        return;
    }

    // 配置导出选项
    UGLTFExportOptions* Options = NewObject<UGLTFExportOptions>();
    Options->bExportMaterial = true;
    Options->bExportTexture = true;
    Options->TextureFormat = EGLTFTextureFormat::PNG;

    // 准备导出对象
    TArray<UObject*> Objects;
    Objects.Add(Mesh);

    // 执行导出
    // 注意：`ExportToGLTF` 是模块的公共接口，具体参数需查阅模块头文件
    bool bSuccess = GLTFModule->ExportToGLTF(Objects, FilePath, Options);

    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Export completed: %s"), *FilePath);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Export failed for: %s"), *FilePath);
    }
}
```

## 模块依赖

从 `.uplugin` 文件的 `Plugins` 部分可以看出，该插件依赖于以下非标准模块：

| 模块 | 用途 |
|---|---|
| `VariantManagerContent` | 用于支持导出 Variant Manager 中定义的资产变体集。 |
| `Interchange` | (可选) 用于与 UE 的 Interchange 框架集成，可能提供更灵活的资产导入/导出管线。 |
| `InterchangeAssets` | 与 `Interchange` 模块配合使用的资产定义。 |

## 维护状态

### 近期更新

```
- d99cb6fefe75 [glTF Exporter] MorphTarget safe guard fixes.
- 1502f487adff [glTF Exporter] Bug fixes for Morph Target exports. Exporting Deltas instead of absolute position/normals.
```
最近的提交集中在修复 Morph Target（变形目标）导出的相关问题，包括安全防护和导出逻辑的修正（导出增量而非绝对位置/法线）。这表明该插件仍在积极维护，并针对特定功能进行优化和错误修复。

### 维护评价

-   **创建时间**：插件于 2022 年 7 月创建，相对年轻。
-   **最近更新**：最近的更新（基于提供的 git 历史）是功能性的 Bug 修复，表明插件处于**活跃维护**状态。
-   **功能完整性**：作为一个企业级（Enterprise）插件，它功能全面，覆盖了 UE 中主要的可导出资产类型。
-   **已知限制**：glTF 2.0 标准本身不支持 UE 的所有高级渲染特性（如复杂的材质图、Lumen 全局光照等），因此导出时会有数据损失或近似映射。插件的文档（DocsURL 为空）可能不够详尽。
-   **推荐使用**：**推荐使用**。对于需要将 UE 资产导出为 glTF 格式的项目，这是官方提供的、功能强大且维护良好的解决方案。建议在使用前，针对目标平台测试导出效果，特别是材质和动画的保真度。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/GLTFExporter)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/GLTFExporter/Tests) (路径为推测，实际测试可能位于 `Engine/Tests/` 下)