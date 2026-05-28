# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | Datasmith CAD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

DatasmithCADImporter 是 Unreal Engine Datasmith 导入管线的核心扩展，专门处理工业级 CAD 格式文件（如 STEP、IGES、JT、Rhino 等）的导入。与普通网格导入不同，CAD 文件包含参数化曲面、B-Rep 几何体和装配体层级结构，需要专门的转换流程才能在 UE 中使用。

该插件解决的核心问题是：**将 CAD 软件生成的精确参数化几何体（NURBS 曲面、B-Rep 实体）转换为 UE 可渲染的多边形网格（Static Mesh），同时保留材质、颜色、层级装配关系等元数据**。

插件采用多模块分层架构：
- **CADInterfaces / WireInterface***：对接底层 CAD SDK（TechSoft、各版本 Alias Wire），负责读取原生 CAD 格式
- **CADLibrary / CADTools**：提供通用的 CAD 数据结构（场景图归档、Body 网格、材质/颜色映射）
- **ParametricSurface / CADKernelSurface**：参数化曲面的细分和三角化算法
- **DatasmithCADTranslator**：Datasmith 翻译器入口，将 CAD 场景图转换为 Datasmith 场景元素
- **DatasmithDispatcher**：多进程分发，将 CAD 转换任务分发到独立进程执行，避免阻塞编辑器
- **DatasmithOpenNurbsTranslator / DatasmithPLMXMLTranslator / DatasmithWireTranslator**：针对特定 CAD 格式的翻译器

插件默认关闭（`EnabledByDefault: false`），需要在编辑器插件面板中手动启用或通过 `--EnablePlugins` 命令行参数激活。

## 使用场景

- 你在建筑/工程/制造项目中需要导入 SolidWorks、CATIA、NX、Rhino 的模型文件 → 用 DatasmithCADImporter
- 你需要将 STEP/IGES 格式的工业零件导入 UE 做数字孪生可视化 → 用 DatasmithCADImporter
- 你的 CAD 文件包含复杂装配体层级，需要保留产品结构树 → 用 DatasmithCADImporter
- 你需要将 CAD 模型的材质/颜色属性映射为 UE PBR 材质 → 用 DatasmithCADImporter

**注意**：此插件是 Datasmith 导入器的 CAD 扩展，基础 Datasmith 导入功能由 `DatasmithImporter` 插件提供。两者通常需要同时启用。

## 蓝图用法

本插件主要是 Datasmith 翻译器的底层实现，不直接暴露蓝图可调用函数。CAD 文件导入通过 Datasmith 导入面板（Import > Datasmith）触发，或通过 `UFactory` 自动检测文件类型。

导入流程由编辑器自动处理，无需蓝图节点。如需程序化导入 CAD 文件，可使用 Datasmith Core 的通用导入 API。

## C++ 用法

### 核心架构

#### 场景图构建器

`FDatasmithSceneGraphBuilder` 是场景图转换的核心类，负责将 CAD 归档数据（`FArchiveSceneGraph`）转换为 Datasmith 场景元素：

```cpp
#include "DatasmithSceneGraphBuilder.h"

// 创建场景图构建器
TMap<uint32, FString> CADFileToSceneGraphDescriptionFile;
// ... 填充 CAD 文件到场景图描述文件的映射

FDatasmithSceneGraphBuilder SceneGraphBuilder(
    CADFileToSceneGraphDescriptionFile,
    CachePath,
    DatasmithScene.ToSharedRef(),
    SceneSource,
    ImportParameters
);

// 执行构建：将 CAD 装配体层级转换为 Datasmith Actor 层级
bool bSuccess = SceneGraphBuilder.Build();
```

构建器内部递归处理：
- **Instance**（实例节点）→ 转换为 `IDatasmithActorElement`
- **Reference**（引用节点）→ 处理共享几何体引用
- **Body**（实体几何体）→ 创建 `IDatasmithMeshElement`

#### 网格构建器

`FDatasmithMeshBuilder` 负责将 CAD Body 数据转换为 `FMeshDescription`：

```cpp
#include "DatasmithMeshBuilder.h"

// 从缓存文件加载网格数据
FDatasmithMeshBuilder MeshBuilder(CADFileToMeshFileMap, CachePath, ImportParameters);

// 获取指定网格元素的 MeshDescription
TOptional<FMeshDescription> MeshDesc = MeshBuilder.GetMeshDescription(MeshElement, MeshParameters);
if (MeshDesc.IsSet())
{
    // MeshDesc 包含三角化后的几何数据，可直接用于 Static Mesh 创建
}
```

#### 翻译器接口

`FDatasmithCADTranslator` 是 Datasmith 翻译器的注册入口：

```cpp
#include "DatasmithCADTranslator.h"

// 翻译器自动注册到 Datasmith 管线
// FDatasmithCADTranslator 继承自 FParametricSurfaceTranslator
// 重写了 LoadScene() 和 LoadStaticMesh()
```

### 头文件引入

```cpp
#include "DatasmithSceneGraphBuilder.h"
#include "DatasmithMeshBuilder.h"
#include "DatasmithCADTranslatorModule.h"
```

## Demo 示例

以下示例展示如何在 C++ 中通过 Datasmith 翻译器框架处理 CAD 文件的场景图：

```cpp
// CADSceneProcessor.h
#pragma once

#include "CoreMinimal.h"
#include "DatasmithSceneGraphBuilder.h"
#include "DatasmithMeshBuilder.h"

class FCADSceneProcessor
{
public:
    bool ProcessCADScene(
        const FString& CachePath,
        TSharedRef<IDatasmithScene> Scene,
        const FDatasmithSceneSource& Source,
        const CADLibrary::FImportParameters& ImportParams,
        TMap<uint32, FString>& SceneGraphFiles,
        TMap<uint32, FString>& MeshFiles)
    {
        // 1. 构建场景图：CAD 层级结构 → Datasmith Actor 层级
        FDatasmithSceneGraphBuilder SceneBuilder(
            SceneGraphFiles, CachePath, Scene, Source, ImportParams);

        if (!SceneBuilder.Build())
        {
            UE_LOG(LogCADTranslator, Error, TEXT("Failed to build scene graph"));
            return false;
        }

        // 2. 加载并三角化网格
        FDatasmithMeshBuilder MeshBuilder(MeshFiles, CachePath, ImportParams);

        // 对每个 MeshElement 获取三角化后的 MeshDescription
        for (const TSharedPtr<IDatasmithMeshElement>& MeshElem : MeshElements)
        {
            CADLibrary::FMeshParameters MeshParams;
            TOptional<FMeshDescription> MeshDesc =
                MeshBuilder.GetMeshDescription(MeshElem.ToSharedRef(), MeshParams);

            if (MeshDesc.IsSet())
            {
                // MeshDesc 现在包含三角化网格数据
                // 可用于创建 UStaticMesh 资产
            }
        }

        return true;
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TechSoft` | TechSoft 3D Interop SDK，用于读取 STEP、JT、CATIA 等工业 CAD 格式 |
| `OpenNurbs6` | OpenNURBS 库，用于读取 Rhino (.3dm) 文件格式 |
| `DatasmithCore` | Datasmith 核心接口（IDatasmithScene、IDatasmithMeshElement 等） |
| `DatasmithImporter` | Datasmith 导入器基础框架（翻译器注册、资产创建） |
| `MeshDescription` | 网格描述数据结构，用于中间网格表示 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点的编译警告 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | Wire 翻译器兼容 Alias 2027 版本 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 升级 TechSoft SDK 至 2026.3 版本 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新 CAD 缓存版本格式 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 解决函数类型转换在 MSVC/Clang 间的可移植性警告 |

### 维护评价

该插件**活跃维护中**。最近更新集中在 2026 年 5 月，内容涉及 SDK 升级（TechSoft 2026.3）、新 CAD 软件版本兼容（Alias 2027）和编译器兼容性修复。从 2019 年创建至今约 7 年，属于 Enterprise 级别的成熟插件。

值得注意的是，插件包含多达 10 个 WireInterface 模块（对应 Alias Wire 不同年份版本 2020-2026），表明维护团队持续跟进上游 CAD SDK 的版本迭代。`EnabledByDefault: false` 是因为该插件依赖第三方商业 SDK（TechSoft），需要额外授权。

**推荐使用**：如果你的项目需要从工业 CAD 格式导入模型，这是 UE 官方支持的唯一方案。但需要注意：
1. 需要手动启用插件
2. TechSoft SDK 需要有效的许可证（通常通过 Datasmith 安装程序提供）
3. 大型 CAD 装配体导入可能较慢，插件通过多进程分发（DatasmithDispatcher）缓解此问题

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests)