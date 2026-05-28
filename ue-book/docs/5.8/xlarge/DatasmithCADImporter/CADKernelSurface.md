# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | CAD 文件导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

DatasmithCADImporter 是 Datasmith 导入管线的 **CAD 格式扩展层**，专门负责将工业级 CAD 文件（CATIA、NX、SolidWorks、STEP、IGES 等）转换为 Unreal Engine 可消费的几何数据。

该插件解决的核心问题是：CAD 软件使用参数化曲面（NURBS/B-Rep）描述几何体，而 UE 使用三角化网格（Mesh），两者之间存在巨大的表达鸿沟。该插件通过以下管线完成转换：

1. **格式解析**：通过 TechSoft (HOOPS) 和 OpenNurbs 库读取各厂商专有格式
2. **拓扑修复**：使用 CADKernel 的 Topomaker 进行缝合（Stitching）、壳体分割和法线朝向修正
3. **曲面细分**：将参数化曲面根据精度要求（弦公差、法线公差、最大边长）转换为三角网格
4. **参数化数据保存**：将原始 CADKernel 会话序列化为 `.ugeom` 文件，支持后续重新细分（Retessellation）

**注意**：该插件默认未启用（`EnabledByDefault: false`），需要在项目设置中手动启用。

## 使用场景

- 你在导入 CATIA/NX/SolidWorks 等工业 CAD 模型到 UE → 启用此插件后通过 Datasmith 导入
- 你需要导入 STEP (.stp)、IGES (.igs)、JT 等中间格式 → 该插件提供对应的翻译器模块
- 你导入 CAD 模型后需要调整细分精度（更精细或更粗糙）→ 使用 Retessellation 功能重新细分
- 你在处理来自 Alias（工业设计软件）的 Wire 文件 → 使用版本化的 WireInterface 模块匹配对应年份

## 蓝图用法

该插件主要作为 Datasmith 导入管线的底层模块运行，不直接暴露蓝图节点。用户通过 Datasmith Import 面板或 `UImportSubsystem` 的导入接口间接使用。

### 核心交互方式

所有 CAD 导入操作通过 Datasmith 统一导入界面完成，无需手动调用蓝图节点。细分参数在导入设置面板中配置。

## C++ 用法

### 头文件引入

```cpp
#include "CADKernelSurfaceModule.h"
#include "CADKernelSurfaceExtension.h"
#include "CADModelToCADKernelConverterBase.h"
```

### 基本用法

从 `CADModelToCADKernelConverterBase` 派生自定义转换器（来源：`Public/CADModelToCADKernelConverterBase.h`）：

```cpp
// 创建一个基于 CADKernel 的 CAD 模型转换器
class FMyCADConverter : public FCADModelToCADKernelConverterBase
{
public:
    FMyCADConverter(const CADLibrary::FImportParameters& InImportParameters)
        : FCADModelToCADKernelConverterBase(InImportParameters)
    {
        // 设置几何和缝合公差
        SetTolerances(0.01, 0.01);
    }

    // 实现添加几何体的逻辑（基类默认返回 false）
    virtual bool AddGeometry(const CADLibrary::FCADModelGeometry& Geometry) override
    {
        // 将 CAD 几何体添加到 CADKernel 会话
        return true;
    }
};
```

### 进阶用法

使用 `AddSurfaceDataForMesh` 从 `.ugeom` 存档重建表面数据，支持 Retessellation（来源：`Public/CADKernelSurfaceExtension.h`）：

```cpp
// 从 CADKernel 存档中提取表面数据
FDatasmithMeshElementPayload MeshPayload;
CADLibrary::FImportParameters ImportParams;
CADLibrary::FMeshParameters MeshParams;
FDatasmithTessellationOptions TessOptions;

CADKernelSurface::AddSurfaceDataForMesh(
    TEXT("/path/to/model.ugeom"),
    ImportParams,
    MeshParams,
    TessOptions,
    MeshPayload
);
```

使用 `UCADKernelParametricSurfaceData` 进行 Retessellation（来源：`Public/CADKernelSurfaceExtension.h`）：

```cpp
// 对已导入的 StaticMesh 重新细分
UCADKernelParametricSurfaceData* SurfaceData = /* 从 Mesh 资产获取 */;
UStaticMesh* StaticMesh = /* 目标网格 */;
FDatasmithRetessellationOptions RetessellateOptions;

// 使用新的细分参数重新生成网格
bool bSuccess = SurfaceData->Tessellate(*StaticMesh, RetessellateOptions);
```

## Demo 示例

### 自定义 CAD 模型转换器

**MyCADConverter.h**
```cpp
#pragma once

#include "CADModelToCADKernelConverterBase.h"

class FMyCADConverter : public FCADModelToCADKernelConverterBase
{
public:
    FMyCADConverter(const CADLibrary::FImportParameters& InImportParameters)
        : FCADModelToCADKernelConverterBase(InImportParameters)
    {
        // 使用更精细的公差
        SetTolerances(0.005, 0.005);
    }

    virtual bool AddGeometry(const CADLibrary::FCADModelGeometry& Geometry) override
    {
        // 处理传入的 CAD 几何体
        // Geometry 包含 B-Rep 数据，需要将其导入 CADKernel 会话
        return true;
    }
};
```

**MyCADConverter.cpp**
```cpp
#include "MyCADConverter.h"

// 注册和使用示例
void RegisterCustomConverter(const CADLibrary::FImportParameters& ImportParams)
{
    // 创建转换器实例
    TSharedRef<FMyCADConverter> Converter = MakeShared<FMyCADConverter>(ImportParams);

    // 初始化处理管线
    Converter->InitializeProcess();

    // 设置细分参数：弦公差、最大边长、法线公差、缝合技术
    Converter->SetImportParameters(0.01, 10.0, 10.0, CADLibrary::EStitchingTechnique::StitchingHeal);

    // 修复拓扑（缝合、分割、朝向修正）
    Converter->RepairTopology();

    // 执行细分：将参数化曲面转换为三角网格
    FMeshDescription MeshDescription;
    CADLibrary::FMeshParameters MeshParams;
    Converter->Tessellate(MeshParams, MeshDescription);

    // 保存模型为 .ugeom 文件
    TSharedPtr<IDatasmithMeshElement> MeshElement = /* 从 Datasmith 管线获取 */;
    Converter->SaveModel(TEXT("/Game/Imported"), MeshElement);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TechSoft` | HOOPS Exchange 库，用于解析 CATIA、NX、SolidWorks、STEP、IGES 等工业 CAD 格式 |
| `OpenNurbs6` | Rhino 的 OpenNurbs 库，用于解析 .3dm 格式和 NURBS 几何处理 |
| `DatasmithContent` | Datasmith 内容类型定义（FDatasmithTessellationOptions、UDatasmithParametricSurfaceData 等） |

**注意**：该插件的核心依赖 `TechSoft` 和 `OpenNurbs6` 均为第三方商业/开源库，需要在 UE 构建环境中单独配置。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 到 float 截断警告 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | Wire 翻译器兼容 Alias 2027 安装环境 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 升级 TechSoft 库至 2026.3 版本 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新 DatasmithCAD 缓存版本 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复函数类型转换警告，兼容 MSVC 和 Clang |

### 维护评价

**活跃维护** ⭐⭐⭐⭐

该插件作为 Datasmith Enterprise 套件的核心组件，保持着良好的维护状态：

- **更新频率**：最近一周内有 5 次提交，涉及第三方库升级、兼容性修复和编译器警告清理
- **模块化设计**：21 个模块按功能清晰划分，版本化的 WireInterface 模块支持多版本共存
- **第三方依赖**：TechSoft (HOOPS) 定期更新以支持新版本 CAD 软件，OpenNurbs 保持同步
- **注意**：默认未启用（`EnabledByDefault: false`），适合企业级 CAD 导入场景

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)