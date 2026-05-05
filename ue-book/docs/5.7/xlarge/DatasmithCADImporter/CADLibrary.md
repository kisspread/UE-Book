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

DatasmithCADImporter 是 Unreal Engine 的企业级 CAD 文件导入解决方案。它解决的核心问题是：**将工业 CAD 格式（如 STEP、IGES、JT、Rhino 3DM、PLMXML 等）高效转换为 UE 可用的网格和材质数据**。

该插件存在的原因：
- 工业/建筑/制造领域的设计师使用 CAD 软件（SolidWorks、CATIA、NX、Rhino 等）创建精确的参数化模型
- 这些模型使用 NURBS 曲面、B-Rep 实体等数学表示，而非游戏引擎常用的三角网格
- 需要一个智能的转换管线：解析 CAD 拓扑 → 曲面细分（Tessellation）→ 生成 MeshDescription → 导入 UE

插件架构分为三层：
1. **WireInterface 层**：通过 TechSoft 的 A3DSDK 读取各种 CAD 格式（每个版本对应不同年份的 SDK）
2. **CADLibrary/CADKernel 层**：核心几何处理，包括 NURBS 曲面细分、网格优化、材质映射
3. **DatasmithCADTranslator 层**：与 Datasmith 管线集成，实现标准导入流程

**注意**：此插件默认禁用（`EnabledByDefault: false`），需要在项目设置中手动启用，且依赖外部商业库（TechSoft A3DSDK）。

## 使用场景

- 你在做建筑可视化，需要导入 Revit/Rhino 的 CAD 模型 → 用 DatasmithCADImporter
- 你在做汽车设计评审，需要导入 CATIA/NX 的 STEP 文件 → 用 DatasmithCADImporter
- 你在做工业数字孪生，需要导入 SolidWorks/JT 格式的机械零件 → 用 DatasmithCADImporter
- 你需要保留 CAD 模型的层级结构和材质信息 → 用 DatasmithCADImporter
- 你需要控制曲面细分质量（精度 vs 性能）→ 用 DatasmithCADImporter 的 ImportParameters

## 蓝图用法

此插件主要通过 Datasmith 导入管线工作，不直接暴露蓝图节点。CAD 文件通过以下方式导入：

1. **Datasmith 导入器**：在编辑器中使用 Datasmith Import 按钮，选择 CAD 文件
2. **Python 脚本**：通过 `unreal.DatasmithSceneElement` API 批量导入
3. **C++ 管线集成**：通过 `IDatasmithTranslator` 接口自定义导入流程

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无直接蓝图节点） | CAD 导入通过 Datasmith 管线自动处理 | — |

## C++ 用法

### 头文件引入

```cpp
#include "CADLibrary/CADKernelTools.h"
#include "CADLibrary/CADMeshDescriptionHelper.h"
#include "CADData.h"
#include "CADOptions.h"
```

### 基本用法：CAD 网格细分

从 CADKernel 实体生成 MeshDescription：

```cpp
// 来源: CADLibrary/Public/CADKernelTools.h

#include "CADKernelTools.h"
#include "CADData.h"

using namespace CADLibrary;

// 准备导入参数和网格参数
FImportParameters ImportParameters;
FMeshParameters MeshParameters;

// 创建网格转换上下文
FMeshConversionContext Context(ImportParameters, MeshParameters, 0.001);

// 假设已有 CADKernel 实体（从 CAD 文件解析得到）
UE::CADKernel::FTopologicalShapeEntity& CADKernelEntity = /* ... */;

// 执行细分，生成 MeshDescription
FMeshDescription MeshDescription;
bool bSuccess = FCADKernelTools::Tessellate(CADKernelEntity, Context, MeshDescription);

if (bSuccess)
{
    // MeshDescription 现在包含三角化后的网格数据
    // 可以用于创建 StaticMesh 等
}
```

### 基本用法：BodyMesh 转换

```cpp
// 来源: CADLibrary/Public/CADKernelTools.h

#include "CADKernelTools.h"

using namespace CADLibrary;

// 定义网格细分标准
UE::CADKernel::FModelMesh MeshModel;
FImportParameters ImportParameters;
double GeometricTolerance = 0.001;

FCADKernelTools::DefineMeshCriteria(MeshModel, ImportParameters, GeometricTolerance);

// 获取 Body 的细分结果
UE::CADKernel::FBody& Body = /* ... */;
FBodyMesh OutBodyMesh;
FCADKernelTools::GetBodyTessellation(MeshModel, Body, OutBodyMesh);

// OutBodyMesh 包含每个面的网格数据
```

### 进阶用法：材质处理与 MeshDescription 转换

```cpp
// 来源: CADLibrary/Public/CADMeshDescriptionHelper.h

#include "CADMeshDescriptionHelper.h"
#include "CADData.h"

using namespace CADLibrary;

// 从 CAD 材质创建 UE PBR 材质
FCADMaterial CADMaterial;
CADMaterial.Color = FColor(255, 128, 0); // 橙色
CADMaterial.Transparency = 0.0f;

TSharedRef<IDatasmithScene> Scene = /* ... */;
TSharedPtr<IDatasmithUEPbrMaterialElement> PBRMaterial = 
    CreateUEPbrMaterialFromMaterial(CADMaterial, Scene);

// 或者从纯颜色创建材质
TSharedPtr<IDatasmithUEPbrMaterialElement> SimpleMaterial = 
    CreateUEPbrMaterialFromColor(FColor(0, 255, 0));

// 创建默认材质
TSharedPtr<IDatasmithUEPbrMaterialElement> DefaultMaterial = 
    CreateDefaultUEPbrMaterial();

// 将 BodyMesh 转换为 MeshDescription
FBodyMesh Body = /* ... */;
FMeshDescription MeshDescription;

FImportParameters ImportParams;
FMeshParameters MeshParams;
FMeshConversionContext ConversionContext(ImportParams, MeshParams);

bool bConverted = ConvertBodyMeshToMeshDescription(ConversionContext, Body, MeshDescription);

// 启用 CAD Patch Group 属性（用于追踪每个三角形属于哪个 CAD 面）
TPolygonAttributesRef<int32> PatchGroupAttr = EnableCADPatchGroups(MeshDescription);

// 获取已有的 Patch ID 集合
TSet<int32> ExistingPatches;
GetExistingPatches(MeshDescription, ExistingPatches);
```

### 进阶用法：MeshDescription 数据缓存

```cpp
// 来源: CADLibrary/Public/CADMeshDescriptionHelper.h

#include "CADMeshDescriptionHelper.h"

using namespace CADLibrary;

// 在进行 DynamicMesh 转换前，缓存 MeshDescription 的材质信息
FMeshDescription OriginalMesh = /* ... */;
FMeshDescriptionDataCache Cache(OriginalMesh);

// ... 执行 DynamicMesh 转换操作 ...
// DynamicMesh 转换可能会改变 PolygonGroupId

// 转换完成后，恢复材质槽名称
FMeshDescription UpdatedMesh = /* ... */;
Cache.RestoreMaterialSlotNames(UpdatedMesh);
// UpdatedMesh 现在恢复了正确的材质槽映射
```

## Demo 示例

### CAD 网格导入处理器

```cpp
// CADMeshImporter.h
#pragma once

#include "CoreMinimal.h"
#include "CADData.h"
#include "CADOptions.h"

class FCADMeshImporter
{
public:
    /** 从 CAD Body 导入网格到 StaticMesh */
    static bool ImportCADBodyToStaticMesh(
        class UStaticMesh* TargetMesh,
        const CADLibrary::FBodyMesh& BodyMesh,
        const CADLibrary::FImportParameters& ImportParams
    );

    /** 批量导入多个 CAD Body */
    static int32 ImportCADBodies(
        const TArray<CADLibrary::FBodyMesh>& Bodies,
        const FString& OutputPath
    );
};
```

```cpp
// CADMeshImporter.cpp
#include "CADMeshImporter.h"
#include "CADLibrary/CADKernelTools.h"
#include "CADLibrary/CADMeshDescriptionHelper.h"
#include "StaticMeshDescription.h"
#include "MeshDescription.h"
#include "Engine/StaticMesh.h"

using namespace CADLibrary;

bool FCADMeshImporter::ImportCADBodyToStaticMesh(
    UStaticMesh* TargetMesh,
    const FBodyMesh& BodyMesh,
    const FImportParameters& ImportParams)
{
    if (!TargetMesh)
    {
        return false;
    }

    // 创建转换上下文
    FMeshParameters MeshParams;
    FMeshConversionContext Context(ImportParams, MeshParams, ImportParams.GetGeometricTolerance());

    // 转换 BodyMesh 到 MeshDescription
    FMeshDescription MeshDescription;
    FBodyMesh MutableBody = BodyMesh; // 需要非 const 引用
    bool bSuccess = ConvertBodyMeshToMeshDescription(Context, MutableBody, MeshDescription);

    if (!bSuccess)
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to convert CAD body to MeshDescription"));
        return false;
    }

    // 启用 CAD Patch Group 属性
    EnableCADPatchGroups(MeshDescription);

    // 获取材质信息并创建对应的 UE 材质
    TSet<int32> PatchIds;
    GetExistingPatches(MeshDescription, PatchIds);

    // 构建 StaticMesh
    UStaticMesh::FBuildMeshDescriptionsParams BuildParams;
    BuildParams.bBuildSimpleCollision = true;
    BuildParams.bCommitMeshDescription = true;

    TArray<const FMeshDescription*> MeshDescriptions;
    MeshDescriptions.Add(&MeshDescription);
    TargetMesh->BuildFromMeshDescriptions(MeshDescriptions, BuildParams);

    UE_LOG(LogTemp, Log, TEXT("Successfully imported CAD body with %d patches"), PatchIds.Num());
    return true;
}

int32 FCADMeshImporter::ImportCADBodies(
    const TArray<FBodyMesh>& Bodies,
    const FString& OutputPath)
{
    FImportParameters DefaultParams;
    int32 SuccessCount = 0;

    for (int32 i = 0; i < Bodies.Num(); ++i)
    {
        FString AssetName = FString::Printf(TEXT("CADMesh_%d"), i);
        UStaticMesh* NewMesh = NewObject<UStaticMesh>(
            GetTransientPackage(), FName(*AssetName));

        if (ImportCADBodyToStaticMesh(NewMesh, Bodies[i], DefaultParams))
        {
            ++SuccessCount;
        }
    }

    return SuccessCount;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TechSoft` | TechSoft A3DSDK 封装，用于读取各种 CAD 格式（STEP、IGES、JT 等） |
| `OpenNurbs6` | OpenNURBS 库，用于读取 Rhino 3DM 文件格式 |
| `DatasmithContent` | Datasmith 内容类型定义（材质、场景元素等） |
| `DatasmithCore` | Datasmith 核心接口（IDatasmithScene、IDatasmithTranslator 等） |
| `MeshDescription` | UE 网格描述格式，用于中间网格表示 |
| `MeshConversion` | 网格格式转换工具 |
| `DynamicMesh` | 动态网格库，用于网格处理和优化 |
| `GeometryCore` | 几何核心库，提供基础几何运算 |

## 维护状态

### 近期更新

```
- 9d3e9979d5ec Issue 542235 : Back out CL 35420560
  回退了一个有问题的变更，说明有活跃的问题修复
- 3b0464de916d Made sure ensure is disabled when compiling the CADWorker
  修复 CADWorker 编译时的 ensure 断言问题
- af690b62c96d Renamed FMeshConversionContext to FCADMeshConversionContext
  API 重构：重命名转换上下文类以避免命名冲突
```

### 维护评价

**维护状态：活跃维护中**

- **创建时间**：2019 年，已有约 6 年历史
- **更新频率**：持续有更新，包括 bug 修复、API 重构、SDK 版本升级
- **模块化程度**：高度模块化，21 个模块覆盖不同功能和 CAD SDK 版本
- **WireInterface 版本跨度**：从 2020 到 2026，说明持续跟进 TechSoft SDK 更新
- **企业级支持**：作为 Epic 官方 Enterprise 插件，有专门团队维护

**已知限制**：
- 默认禁用，需要手动启用
- 依赖商业库 TechSoft A3DSDK，完整功能需要相应许可证
- 大型 CAD 文件导入可能较慢，需要调整细分参数平衡质量与性能

**推荐使用**：✅ 强烈推荐用于工业/建筑 CAD 数据导入场景。这是 UE 官方支持的最完整的 CAD 导入方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests)