# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | CAD 文件导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` ~ `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

DatasmithCADImporter 是 Datasmith 导入框架的 CAD 后端，负责将工业 CAD 格式（Alias、Rhino、OpenNurbs、PLMXML、Wire 等）转换为 UE 可用的网格和场景数据。

该插件的核心价值在于：工业 CAD 模型使用参数化曲面（NURBS/B-Rep）而非三角面片，无法直接渲染。本插件通过 TechSoft 和 CADKernel 两大内核将参数化几何体 **细分（Tessellation）** 为三角网格，同时保留拓扑修复、UV 映射、对称检测等高级功能。

**为什么需要手动启用（EnabledByDefault=false）**：该插件依赖第三方库 TechSoft（商业授权），并非所有 UE 用户都需要或拥有此依赖。

## 使用场景

- 你在做 **建筑可视化 / 工业数字孪生** → 需要导入 Catia、SolidWorks、STEP、IGES 等 CAD 格式 → 启用本插件
- 你需要对已导入的 CAD 模型进行 **重新细分（Retessellation）** 以调整精度 → 本插件提供 `FDatasmithRetessellationOptions` 支持
- 你需要导入 **Rhino (.3dm) / OpenNurbs** 格式的参数化模型 → 使用 `DatasmithOpenNurbsTranslator` 模块
- 你需要导入 **Alias Wire** 格式 → 使用 `DatasmithWireTranslator` + 对应年份的 `WireInterface` 模块
- 你需要导入 **PLMXML** 产品生命周期数据 → 使用 `DatasmithPLMXMLTranslator` 模块

## 架构概览

本插件采用 **模块化翻译器架构**，核心流程如下：

```
CAD 文件格式
    │
    ▼
┌─────────────────────────┐
│  DatasmithCADTranslator  │  ← 总入口，路由到具体翻译器
│  DatasmithOpenNurbs…     │
│  DatasmithPLMXML…        │
│  DatasmithWireTranslator │
└──────────┬──────────────┘
           │ 解析 CAD 几何体
           ▼
┌─────────────────────────┐
│    CADInterfaces         │  ← TechSoft SDK 封装
│    CADLibrary            │  ← 通用 CAD 工具库
│    CADTools              │
└──────────┬──────────────┘
           │ 参数化曲面转换
           ▼
┌─────────────────────────┐
│    ParametricSurface     │  ← NURBS → 三角网格细分
│    ParametricSurfaceExt  │
│    CADKernelSurface      │  ← CADKernel 内核细分
└──────────┬──────────────┘
           │ 网格数据
           ▼
┌─────────────────────────┐
│    DatasmithDispatcher   │  ← 多进程调度（批量导入加速）
└─────────────────────────┘
```

**WireInterface 模块族**（2020 ~ 2026）是版本化的 Alias Wire 格式接口，每个年份对应一个独立模块，确保向后兼容。

## 蓝图用法

本插件主要面向编辑器导入流程，直接暴露的蓝图节点较少。关键的 USTRUCT 已标记 `BlueprintType`，可在蓝图中操作：

### 核心结构体

| 结构体 | 说明 |
|---|---|
| `FParametricSceneParameters` | 场景级参数：坐标系、公制单位、缩放因子 |
| `FParametricMeshParameters` | 网格级参数：法线翻转、对称设置 |

### 蓝图数据资产

| 类 | 说明 |
|---|---|
| `UDatasmithParametricSurfaceData` | 附加到 StaticMesh 的参数化曲面原始数据，支持 Retessellation |
| `UTechSoftParametricSurfaceData` | TechSoft 专用的参数化曲面数据子类，实现了真正的 Retessellation |

## C++ 用法

### 核心接口：ICADModelConverter

这是所有 CAD 模型转换器的基接口，定义了完整的转换流水线：

```cpp
// Source/ParametricSurface/Public/CADModelConverter.h
namespace CADLibrary
{
    class ICADModelConverter
    {
    public:
        // 1. 初始化转换会话
        virtual void InitializeProcess() = 0;
        
        // 2. 添加几何体（可多次调用以合并多个 Body）
        virtual bool AddGeometry(const FCADModelGeometry& Geometry) = 0;
        
        // 3. 拓扑修复（缝合间隙、修复退化面等）
        virtual bool RepairTopology() = 0;
        
        // 4. 保存 B-Rep 文件（用于后续 Retessellation）
        virtual bool SaveModel(const TCHAR* OutputPath, TSharedPtr<IDatasmithMeshElement> MeshElement) = 0;
        
        // 5. 细分为三角网格
        virtual bool Tessellate(const FMeshParameters& InMeshParameters, FMeshDescription& OutMeshDescription) = 0;
        
        // 设置细分精度参数
        virtual void SetImportParameters(
            double ChordTolerance,      // SAG（弦高公差）
            double MaxEdgeLength,       // 最大边长
            double NormalTolerance,     // 相邻三角面法线夹角
            EStitchingTechnique StitchingTechnique  // 拓扑缝合策略
        ) = 0;
        
        // 为已生成的网格附加参数化曲面数据（用于后期 Retessellation）
        virtual void AddSurfaceDataForMesh(
            const TCHAR* InFilePath,
            const FMeshParameters& InMeshParameters,
            const FDatasmithTessellationOptions& InTessellationOptions,
            FDatasmithMeshElementPayload& OutMeshPayload
        ) const = 0;
    };
}
```

### TechSoft 转换器示例

```cpp
// Source/ParametricSurface/Public/CADModelToTechSoftConverterBase.h
#include "CADModelToTechSoftConverterBase.h"

// 创建转换器实例（使用默认导入参数）
CADLibrary::FImportParameters ImportParams;
FCADModelToTechSoftConverterBase Converter(ImportParams);

// 设置细分参数：弦高 0.5mm，最大边长 10mm，法线公差 15°
Converter.SetImportParameters(0.5, 10.0, 15.0, CADLibrary::EStitchingTechnique::StitchingSew);

// 执行完整流程
Converter.InitializeProcess();
// ... AddGeometry() 调用 ...
Converter.RepairTopology();
Converter.SaveModel(*OutputPath, MeshElement);

FMeshDescription MeshDescription;
Converter.Tessellate(MeshParams, MeshDescription);
```

### 翻译器基础类

```cpp
// Source/ParametricSurface/Public/ParametricSurfaceTranslator.h
// 自定义翻译器时继承 FParametricSurfaceTranslator
class FMyCADTranslator : public FParametricSurfaceTranslator
{
protected:
    // 覆写此方法来设置默认细分选项
    virtual void InitCommonTessellationOptions(FDatasmithTessellationOptions& TessellationOptions) override
    {
        TessellationOptions.ChordTolerance = 0.1f;
        TessellationOptions.MaxEdgeLength = 5.0f;
        TessellationOptions.NormalTolerance = 10.0f;
    }
};
```

### 参数化曲面数据工具函数

```cpp
// Source/ParametricSurface/Public/ParametricSurfaceTranslator.h
namespace ParametricSurfaceUtils
{
    // 为已有的网格附加参数化曲面数据
    bool AddSurfaceData(
        const TCHAR* MeshFilePath,
        const CADLibrary::FImportParameters& InSceneParameters,
        const CADLibrary::FMeshParameters& InMeshParameters,
        const FDatasmithTessellationOptions& InCommonTessellationOptions,
        FDatasmithMeshElementPayload& OutMeshPayload
    );
}
```

## Demo 示例

```cpp
// MyCADImporter.h
#pragma once
#include "CADModelConverter.h"
#include "CADModelToTechSoftConverterBase.h"
#include "ParametricSurfaceTranslator.h"
#include "DatasmithParametricSurfaceData.h"

class FMyCADImportSession
{
public:
    void ImportCADFile(const FString& FilePath);
};

// MyCADImporter.cpp
#include "MyCADImporter.h"
#include "ParametricSurfaceModule.h"

void FMyCADImportSession::ImportCADFile(const FString& FilePath)
{
    // 检查 ParametricSurface 模块是否可用（需要 TechSoft 依赖）
    if (!FParametricSurfaceModule::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("ParametricSurface module is not available. Check TechSoft installation."));
        return;
    }

    // 创建参数化曲面数据对象
    UDatasmithParametricSurfaceData* SurfaceData = FParametricSurfaceModule::CreateParametricSurface();
    
    // 设置场景参数
    CADLibrary::FImportParameters ImportParams;
    ImportParams.SetTesselationParameters(
        0.5,   // ChordTolerance (SAG)
        10.0,  // MaxEdgeLength
        15.0,  // NormalTolerance
        CADLibrary::EStitchingTechnique::StitchingSew
    );
    
    SurfaceData->SetImportParameters(ImportParams);
    
    // 加载原始 CAD 数据
    SurfaceData->SetFile(*FilePath);
    
    // 验证数据有效性
    if (SurfaceData->IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("CAD file loaded: %s"), *FilePath);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TechSoft` | TechSoft HOOPS 内核，提供 CAD 格式解析和 B-Rep 几何操作 |
| `OpenNurbs6` | OpenNurbs 库，用于 Rhino (.3dm) 格式解析 |
| `DatasmithCore` | Datasmith 核心框架（IDatasmithTranslator、MeshElement 等） |
| `DatasmithImporter` | Datasmith 导入器框架（场景构建、资产管理） |
| `MeshDescription` | 网格数据结构（FMeshDescription） |
| `StaticMeshDescription` | StaticMesh 网格描述扩展 |

> 注意：`TechSoft` 是商业库，需要单独获取许可证。没有 TechSoft 时本插件的核心功能不可用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 支持 Alias 2027 环境下的 Wire 格式翻译器 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 升级 TechSoft 依赖至 2026.3 版本 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新 CAD 缓存格式版本号 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复 MSVC 与 Clang 之间的类型转换警告兼容性 |

### 维护评价

- **活跃维护**：最近一次更新在 2026 年 5 月，距今不到 1 个月，且持续进行实质性更新（TechSoft 版本升级、新 Alias 版本支持）
- **企业级插件**：由 Epic Games 官方维护，作为 Datasmith 企业级管线的核心组件
- **版本化接口**：WireInterface 采用年份版本化设计（2020~2026），说明此插件面向长期工业用户
- **推荐使用**：如果你的工作流涉及 CAD 文件导入，本插件是 UE5 中唯一的企业级解决方案，且维护状态良好

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)