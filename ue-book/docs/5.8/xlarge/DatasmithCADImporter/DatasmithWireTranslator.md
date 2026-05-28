# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | CAD 文件导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithWireTranslator` (Runtime), `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020`–`WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

---

## 用途

DatasmithCADImporter 是 Datasmith 导入流水线的 CAD 后端扩展，专门负责将工业 CAD 格式（如 Alias/Wire、OpenNurbs/3DM、PLMXML 等）转换为 Unreal 可消费的 Datasmith 场景。

该插件存在的核心原因：**原生 UE5 不支持导入 CAD 格式**。CAD 模型使用参数化曲面（NURBS、B-Spline）而非多边形网格，需要专门的曲面细分（tessellation）和几何转换流程。DatasmithCADImporter 提供了这条完整的转换链：

1. **格式解析**：通过 WireInterface / OpenNurbsTranslator / PLMXMLTranslator 读取原始 CAD 文件
2. **曲面处理**：CADKernelSurface + ParametricSurface 负责参数化曲面到多边形的转换
3. **几何优化**：CADLibrary / CADTools 提供合并、分组、LOD 等优化
4. **场景构建**：DatasmithCADTranslator + DatasmithDispatcher 将结果组装为 IDatasmithScene

默认不启用（`EnabledByDefault=false`），因为需要第三方许可（TechSoft HOOPS、OpenNurbs、Autodesk Alias），仅面向企业用户。

---

## 使用场景

- 你在做**汽车设计可视化**，需要导入 Autodesk Alias 的 `.wire` 模型 → 用 DatasmithWireTranslator
- 你在做**工业产品展示**，需要导入 Rhino 的 `.3dm` 模型 → 用 DatasmithOpenNurbsTranslator
- 你在做**PLM 工作流集成**，需要导入 PLMXML 格式的产品数据 → 用 DatasmithPLMXMLTranslator
- 你需要**精确控制 CAD 模型的曲面细分质量**（公差、弦高、法线角度）→ 用 FWireSettings / FDatasmithTessellationOptions
- 你需要按**图层结构**组织导入的几何体 → 设置 `bUseLayerAsActor = true`

---

## 蓝图用法

该插件主要作为 Datasmith 导入管线的内部组件运行，直接暴露给蓝图的节点较少。可通过 `UDatasmithWireOptions` 在编辑器中配置导入参数。

### 核心结构体

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FWireSettings.bUseLayerAsActor` | 是否将 CAD 文件的图层作为场景中的独立 Actor | `FWireSettings` |
| `FWireSettings.bMergeGeometryByGroup` | 是否将同一 Group 下的几何节点合并 | `FWireSettings` |
| `FDatasmithTessellationOptions`（继承） | 曲面细分参数：公差、弦高、法线角度等 | `FWireSettings` |

### 核心类

| 类 | 说明 | 所在文件 |
|---|---|---|
| `UDatasmithWireOptions` | 编辑器配置面板，包裹 FWireSettings，可通过 Datasmith 导入选项 UI 访问 | `DatasmithWireTranslator.h` |

### 使用示例（蓝图描述）

该插件不提供可直接拖入蓝图的节点。使用方式为：

1. 启用插件（编辑 → 插件 → 搜索 "Datasmith CAD Importer" → 启用 → 重启）
2. 通过 Datasmith 导入流程（文件 → 导入 → Datasmith）选择 `.wire` / `.3dm` 等 CAD 文件
3. 在弹出的导入选项面板中配置 `UDatasmithWireOptions` 的参数：
   - 勾选 **Use Layer As Actor**：按图层拆分场景 Actor
   - 勾选 **Merge Geometry By Group**：合并同组几何体以减少 DrawCall
   - 调整继承自 `FDatasmithTessellationOptions` 的细分参数

---

## C++ 用法

### 头文件引入

```cpp
// Wire 接口头文件
#include "IWireInterface.h"

// 翻译器头文件（如果需要自定义翻译流程）
#include "DatasmithWireTranslator.h"
```

### 基本用法：实现自定义 Wire 接口

`IWireInterface` 是一个纯虚接口，用于适配不同版本的 Alias/Wire SDK。各 `WireInterfaceXXXX` 模块实现了该接口。

```cpp
// 来源: Public/IWireInterface.h
// 注册一个自定义的 Wire 接口实现
void RegisterMyWireInterface()
{
    IWireInterface::RegisterInterface(
        2026, 0,  // MajorVersion, MinorVersion
        []() -> TSharedPtr<IWireInterface>
        {
            return MakeShared<FMyWireInterfaceImpl>();
        }
    );
}

// 实现一个 Wire 接口
class FMyWireInterfaceImpl : public IWireInterface
{
public:
    virtual bool Initialize(const TCHAR* Filename) override
    {
        // 打开 Wire 文件，初始化内部状态
        return true;
    }

    virtual bool Load(TSharedPtr<IDatasmithScene> Scene) override
    {
        // 读取 Wire 文件内容，填充 IDatasmithScene
        return true;
    }

    virtual void SetImportSettings(const FWireSettings& Settings) override
    {
        // 应用用户配置的导入参数
    }

    virtual void SetOutputPath(const FString& Path) override
    {
        // 设置中间文件输出路径（用于缓存细分结果）
    }

    virtual bool LoadStaticMesh(
        const TSharedPtr<IDatasmithMeshElement> MeshElement,
        FDatasmithMeshElementPayload& OutMeshPayload,
        const FDatasmithTessellationOptions& InTessellationOptions) override
    {
        // 将 CAD 曲面细分并输出为多边形网格
        return true;
    }
};
```

### 基本用法：查询 Alias 版本需求

```cpp
// 来源: Public/IWireInterface.h
// 检查当前系统安装的 Alias 版本是否满足要求
uint64 RequiredVersion = IWireInterface::GetRequiredAliasVersion();
// 如果返回 0，表示不需要 Alias（例如使用了开源替代）
```

### 进阶用法：自定义翻译器管线

```cpp
// 来源: Private/DatasmithWireTranslator.h
// FDatasmithWireTranslator 继承自 FParametricSurfaceTranslator
// 可以在翻译器生命周期中注入自定义逻辑

// 示例：在加载场景前配置 WireSettings
FWireSettings Settings;
Settings.bUseLayerAsActor = false;           // 不按图层拆分
Settings.bMergeGeometryByGroup = true;       // 合并同组几何
Settings.StitchingTechnique = EDatasmithCADStitchingTechnique::StitchingNone;
Settings.LinearTolerance = 0.01f;            // 线性公差
Settings.NormalTolerance = 10.0f;            // 法线角度公差
Settings.ChordTolerance = 0.1f;              // 弦高公差

// Settings 的 Hash 可用于缓存判断
uint32 SettingsHash = Settings.GetHash();
```

---

## Demo 示例

以下展示如何编程式地加载 Wire 文件并获取网格数据：

```cpp
// MyWireLoader.h
#pragma once

#include "CoreMinimal.h"
#include "IWireInterface.h"

class FMyWireLoader
{
public:
    bool LoadWireFile(const FString& FilePath, TSharedPtr<IDatasmithScene> OutScene);

private:
    TSharedPtr<IWireInterface> WireInterface;
};
```

```cpp
// MyWireLoader.cpp
#include "MyWireLoader.h"

bool FMyWireLoader::LoadWireFile(const FString& FilePath, TSharedPtr<IDatasmithScene> OutScene)
{
    // 获取匹配的 Wire 接口（根据系统安装的 Alias 版本自动选择）
    // 实际接口通过 IWireInterface::RegisterInterface 机制动态注册
    // 这里假设已通过模块加载注册

    if (!WireInterface.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("No Wire interface available"));
        return false;
    }

    // 初始化接口，指向目标 .wire 文件
    if (!WireInterface->Initialize(*FilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize Wire interface for: %s"), *FilePath);
        return false;
    }

    // 配置导入参数
    FWireSettings Settings;
    Settings.bUseLayerAsActor = true;
    Settings.bMergeGeometryByGroup = true;
    Settings.LinearTolerance = 0.01f;
    Settings.NormalTolerance = 10.0f;
    WireInterface->SetImportSettings(Settings);

    // 设置缓存输出路径
    WireInterface->SetOutputPath(FPaths::ProjectSavedDir() / TEXT("WireCache"));

    // 加载场景
    if (!WireInterface->Load(OutScene))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load Wire scene"));
        return false;
    }

    UE_LOG(LogTemp, Log, TEXT("Wire file loaded successfully: %s"), *FilePath);
    return true;
}
```

---

## 模块依赖

该插件具有大量模块，以下是各子模块的**独特依赖**（不列出 Core/Engine 等标准依赖）：

| 模块 | 用途 |
|---|---|
| `TechSoft` | TechSoft HOOPS Exchange SDK，CAD 格式解析核心（被 CADInterfaces 依赖） |
| `OpenNurbs6` | OpenNurbs 库，Rhino `.3dm` 文件读取（被 DatasmithOpenNurbsTranslator 依赖） |
| `DatasmithContent` | Datasmith 核心数据类型（IDatasmithScene、IDatasmithMeshElement 等） |
| `DatasmithCore` | Datasmith 翻译器基础框架（IDatasmithTranslator、FDatasmithSceneSource 等） |
| `ParametricSurface` | 参数化曲面细分引擎 |
| `CADLibrary` | CAD 几何处理工具库 |
| `CADTools` | CAD 操作工具集 |

> **注意**：使用该插件需要获取 TechSoft HOOPS Exchange 的商业许可，OpenNurbs 为开源许可。部分 WireInterface 模块需要目标系统安装对应版本的 Autodesk Alias。

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的编译警告 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 兼容 Alias 2027 版本，确保 Wire 翻译器正常工作 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 升级 TechSoft HOOPS SDK 至 2026.3 版本 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新 CAD 缓存版本号（缓存格式变更） |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复 MSVC/Clang 间的类型转换警告兼容性 |

### 维护评价

**活跃维护** ✅

该插件近期（2026 年 5 月）仍有密集的实质性更新，包括：
- 持续跟进上游 CAD SDK（TechSoft）版本更新
- 主动适配新版本 Autodesk Alias（2027）的兼容性
- 修复编译器兼容性问题（MSVC/Clang 严格浮点模式）

从版本化的 WireInterface 模块（2020 → 2026_0）可以看出，Epic 在持续跟踪 Alias 的每年大版本更新。该插件是 Datasmith 企业功能的核心组成部分，有长期维护承诺。

**推荐使用**：如果你的项目需要导入 CAD 文件（特别是 Alias `.wire` 格式），该插件是官方推荐方案。但需注意：
- 默认未启用，需手动激活
- 需要 TechSoft 商业许可
- 部分功能依赖目标系统安装特定版本的 Alias

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- Wire 接口头文件：[IWireInterface.h](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter/Source/DatasmithWireTranslator/Public/IWireInterface.h)
- 翻译器实现：[DatasmithWireTranslator.h](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter/Source/DatasmithWireTranslator/Private/DatasmithWireTranslator.h)