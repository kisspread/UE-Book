# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | CAD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

---

## 用途

Datasmith CAD Importer 是 Unreal Engine Datasmith 生态系统中的 **CAD 格式原生导入能力**，为工业级 CAD 文件提供从源格式到 UE 内部表示的完整转换管线。

该插件的核心价值在于：**绕过通用中间格式，直接读取原生 CAD 数据结构**（B-Rep 拓扑、修剪曲面、分层信息等），通过 CADKernel 或 TechSoft 两个后端进行曲面细分（Tessellation），最终生成 MeshDescription 和 PBR 材质，供 UE 渲染管线使用。

插件的架构设计围绕不同 CAD 软件的数据模型：

- **WireInterface** 系列模块：处理 Autodesk Alias `.wire` 文件（工业设计/汽车造型领域的核心格式），每个版本对应一个 Alias 软件版本的数据结构变化
- **DatasmithOpenNurbsTranslator**：处理 Rhino/OpenNurbs `.3dm` 文件
- **DatasmithPLMXMLTranslator**：处理 PLMXML 数据交换格式
- **CADLibrary / CADTools**：共享的 CAD 数据抽象层和工具函数
- **CADKernelSurface / ParametricSurface**：曲面细分引擎，将 B-Rep 转换为三角网格
- **CADInterfaces**：与 TechSoft A3D 库的接口层（第三方商业 CAD 内核）

整个插件默认禁用（`EnabledByDefault = false`），需要通过项目设置手动启用或安装 Datasmith for CAD 导入器后自动加载。

---

## 使用场景

- 你在做 **汽车/交通工具外观设计评审** → 需要导入 Autodesk Alias 的 `.wire` 模型到 UE 中进行实时渲染预览
- 你在做 **工业产品可视化** → 需要将 Rhino `.3dm` 或 PLMXML 格式的 CAD 数据直接导入 UE
- 你在做 **建筑/工程 BIM 管线** → Datasmith 主框架配合此插件处理 CAD 原始数据
- 你需要 **保留 CAD 层级结构和材质信息** → 该插件在导入过程中维护 DAG 节点层级、图层映射和着色器参数（Blinn/Lambert/Phong 等）
- 你需要 **多版本 Alias 文件兼容** → WireInterface2020 ~ WireInterface2026_0 覆盖多个 Alias 软件版本

---

## 蓝图用法

该插件为纯 Runtime 翻译器模块，**不暴露任何 BlueprintCallable 函数或 BlueprintReadWrite 属性**。

所有 CAD 文件导入功能通过 UE 的标准 Datasmith 导入流程触发：

1. **编辑器中**：通过 Content Browser → Import，选择 `.wire` / `.3dm` 等 CAD 文件
2. **Datasmith 场景导入**：通过 Datasmith 面板导入包含 CAD 引用的场景
3. **Python/命令行自动化**：通过 `UImportSubsystem` 触发导入流程

---

## C++ 用法

该插件的 C++ 接口面向 **翻译器扩展开发者**，而非最终用户。以下是核心类的用法说明。

### 核心架构

```
输入文件 (.wire/.3dm/.plmxml)
    ↓
Translator (DatasmithWireTranslator / DatasmithOpenNurbsTranslator / ...)
    ↓ 读取源格式，遍历 DAG 树
    ↓
CADKernel / TechSoft Converter
    ↓ B-Rep → 三角网格细分 (Tessellation)
    ↓
IDatasmithScene / IDatasmithMeshElement
    ↓
UE 渲染管线
```

### WireInterface 模块入口

每个 WireInterface 模块暴露一个 `IWireInterface` 实现，由 `DatasmithWireTranslator` 统一调度。以 `WireInterface2024_1` 为例：

```cpp
// 来源: Source/WireInterface/WireInterface2024_1/Private/WireInterfaceImpl.h

// 使用 WireInterface 模块的翻译器
TSharedPtr<IWireInterface> Translator = MakeShared<FWireTranslatorImpl>();

// 初始化，传入 .wire 文件路径
bool bSuccess = Translator->Initialize(TEXT("/path/to/model.wire"));

// 设置导入参数
FWireSettings Settings;
Translator->SetImportSettings(Settings);

// 设置输出路径（临时几何数据缓存目录）
Translator->SetOutputPath(TEXT("/path/to/output/"));

// 加载场景，结果写入 IDatasmithScene
TSharedPtr<IDatasmithScene> Scene = FDatasmithSceneFactory::CreateScene(TEXT("ImportedWire"));
Translator->Load(Scene);
```

### 模块接口

```cpp
// 来源: Source/WireInterface/WireInterface2024_1/Public/WireInterfaceModule.h

// 检查模块是否已加载
if (FDatasmithWireTranslatorModule::IsAvailable())
{
    FDatasmithWireTranslatorModule& Module = FDatasmithWireTranslatorModule::Get();
    
    // 获取临时目录（用于中间几何数据缓存）
    FString TempDir = Module.GetTempDir();
}
```

### DAG 节点遍历

内部实现遍历 Alias 的 DAG（有向无环图）节点树，将每个节点类型映射到 Datasmith Actor：

```cpp
// 来源: Source/WireInterface/WireInterface2024_1/Private/WireInterfaceImpl.h

// 节点类型映射关系（伪代码展示流程）:
// AlDagNode → 根据类型分派:
//   - GroupNode → IDatasmithActorElement (作为父级容器)
//   - GeometryNode (Mesh/Surface/Shell) → IDatasmithMeshElement + IDatasmithActorElement
//   - Layer → 层级分组 Actor
```

### B-Rep 到网格的转换

两个可选后端用于将 Alias B-Rep 数据转换为三角网格：

```cpp
// CADKernel 路径（默认，UE 内置引擎）
// 来源: Source/WireInterface/WireInterface2024_1/Private/AliasModelToCADKernelConverter.h
class FAliasModelToCADKernelConverter : public FCADModelToCADKernelConverterBase
{
    // 将 Alias B-Rep 添加到 CADKernel 拓扑结构
    bool AddBRep(const FAlDagNodePtr& DagNode, const FColor& Color, EAliasObjectReference ObjectReference);
    
    // 执行细分
    virtual bool Tessellate(const CADLibrary::FMeshParameters& InMeshParameters, 
                            FMeshDescription& OutMeshDescription) override;
    
    // 修复拓扑（处理孔洞、退化边等）
    virtual bool RepairTopology() override;
};

// TechSoft 路径（商业 CAD 内核，可选）
// 来源: Source/WireInterface/WireInterface2024_1/Private/AliasModelToTechSoftConverter.h
class FAliasModelToTechSoftConverter : public FCADModelToTechSoftConverterBase
{
    bool AddBRep(const FAlDagNodePtr& DagNode, const FColor& Color, EAliasObjectReference ObjectReference);
    
    virtual bool AddGeometry(const CADLibrary::FCADModelGeometry& Geometry) override;
};
```

### 材质映射

Alias 着色器模型被映射到 UE PBR 材质：

```cpp
// 来源: Source/WireInterface/WireInterface2024_1/Private/WireInterfaceImpl.h
// Alias 着色器类型支持:
// - Blinn (AddAlBlinnParameters)
// - Lambert (AddAlLambertParameters)
// - Phong (AddAlPhongParameters)
// - LightSource (AddAlLightSourceParameters)
// 均转换为 IDatasmithUEPbrMaterialElement
```

---

## Demo 示例

由于该插件是内部翻译器管线，不提供独立的可编译 Demo。以下展示如何在 C++ 中通过 Datasmith API 触发 CAD 文件导入：

### MyCADImporter.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "DatasmithSceneFactory.h"
#include "DatasmithMesh.h"

class FMyCADImporter
{
public:
    /**
     * 导入 .wire 文件并获取场景数据
     * @param InFilePath .wire 文件的完整路径
     * @return 导入成功返回 Datasmith 场景，失败返回 nullptr
     */
    static TSharedPtr<IDatasmithScene> ImportWireFile(const FString& InFilePath);
    
    /**
     * 获取导入的网格元素列表
     * @param InScene 由 ImportWireFile 返回的场景
     * @return 场景中所有网格元素
     */
    static TArray<TSharedPtr<IDatasmithMeshElement>> GetMeshElements(
        const TSharedPtr<IDatasmithScene>& InScene);
};
```

### MyCADImporter.cpp

```cpp
#include "MyCADImporter.h"
#include "DatasmithSceneExporter.h"
#include "WireInterfaceModule.h"

TSharedPtr<IDatasmithScene> FMyCADImporter::ImportWireFile(const FString& InFilePath)
{
    // 检查 WireInterface 模块可用性
    if (!FDatasmithWireTranslatorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("DatasmithCADImporter 插件未启用"));
        return nullptr;
    }
    
    // 创建 Datasmith 场景
    TSharedPtr<IDatasmithScene> Scene = FDatasmithSceneFactory::CreateScene(
        *FPaths::GetBaseFilename(InFilePath));
    
    // 实际的 .wire 导入通过 Datasmith 导入子系统自动触发
    // 此处展示的是通过 Datasmith API 获取结果的工作流
    
    return Scene;
}

TArray<TSharedPtr<IDatasmithMeshElement>> FMyCADImporter::GetMeshElements(
    const TSharedPtr<IDatasmithScene>& InScene)
{
    TArray<TSharedPtr<IDatasmithMeshElement>> MeshElements;
    
    if (!InScene.IsValid())
    {
        return MeshElements;
    }
    
    // 遍历场景元素，提取所有网格
    for (int32 i = 0; i < InScene->GetMeshesCount(); ++i)
    {
        MeshElements.Add(InScene->GetMesh(i));
    }
    
    return MeshElements;
}
```

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DatasmithCore` | Datasmith 场景/元素工厂、接口定义 |
| `CADLibrary` | CAD 数据抽象层（FCADModelGeometry、FMeshParameters 等） |
| `CADTools` | CAD 工具函数库 |
| `CADKernelSurface` | UE 内置 CADKernel B-Rep → 网格细分引擎 |
| `ParametricSurface` | 参数化曲面细分支持 |
| `TechSoft` | 第三方商业 CAD 内核（A3D 库），用于 TechSoft 转换路径 |
| `OpenNurbs6` | OpenNurbs 6.x 库（仅 DatasmithOpenNurbsTranslator 使用） |

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度到单精度的截断警告 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 新增 Alias 2027 版本兼容支持 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | TechSoft CAD 内核升级至 2026.3 版本 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新 Datasmith CAD 缓存版本号 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复跨编译器（MSVC/Clang）的类型转换警告 |

### 维护评价

**活跃维护** ⭐⭐⭐⭐

- 该插件创建于 **2019 年**（约 7 年），是 Datasmith 企业版的核心组件
- 最近更新集中在 **2026 年 5 月**，且包含实质性功能更新（Alias 2027 兼容、TechSoft 版本升级）
- WireInterface 模块保持 **逐年版本更新**（2020 ~ 2026），紧跟 Autodesk Alias 软件的每次主版本迭代
- 属于 Epic Games 官方维护的企业级功能，与 Autodesk 等 CAD 厂商合作，长期维护有保障
- **注意**：该插件默认禁用（`EnabledByDefault = false`），需通过 Datasmith 安装器或手动启用
- 部分 WireInterface 版本模块（如 WireInterface2020）可能在较新引擎中逐步废弃，建议根据实际使用的 Alias 版本选择对应模块

**推荐**：如果你的工作流涉及 Alias .wire 文件或原生 CAD 格式导入，这是必装插件。对于纯 Rhino/OpenNurbs 用户，仅需 DatasmithOpenNurbsTranslator 相关模块即可。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)