# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | CAD文件导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020~2026` (Runtime) ×10 |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约7年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

本插件是 Datasmith 导入管线中专门处理 **CAD 工业设计数据** 的翻译器集合。它解决了从工业 CAD 软件（如 Autodesk Alias、CATIA、NX、Rhino 等）向 Unreal Engine 导入几何数据时的核心问题：将参数化曲面（Parametric Surface）和 NURBS 曲线转换为引擎可渲染的多边形网格。

插件的核心能力包括：

1. **Wire/Alias 文件翻译**：通过版本化的 WireInterface 模块（支持 Alias 2020 至 2026+），读取 Autodesk Alias 的 `.wire` 文件格式，保持图层（Layer）和分组（Group）的层级结构
2. **OpenNurbs 支持**：通过 OpenNurbs6 库解析 `.3dm` 等 Rhino 文件格式中的 NURBS 几何体
3. **PLMXML 翻译**：支持从 PLM（产品生命周期管理）系统导出的 XML 格式数据
4. **参数化曲面处理**：将 CAD 参数化曲面经过细分（Tessellation）转为三角网格，同时提供可控的精度和接缝策略
5. **TechSoft 集成**：利用 TechSoft 库读取多种通用 CAD 格式（STEP、IGES、JT 等）
6. **多进程分发**：通过 DatasmithDispatcher 支持在独立进程中处理大规模 CAD 数据，避免阻塞主编辑器

**默认未启用**——需要在编辑器的插件管理面板中手动启用，因为 CAD 导入依赖额外的第三方库授权（TechSoft 许可证）。

## 使用场景

- 你在做建筑可视化项目，需要导入来自 Revit/CATIA 的 BIM 数据 → 使用 DatasmithCADTranslator
- 你在做汽车设计可视化，需要从 Autodesk Alias 导入 `.wire` 外观面数据 → 使用 DatasmithWireTranslator
- 你在做工业产品展示，需要从 Rhino 导入 `.3dm` 模型 → 使用 DatasmithOpenNurbsTranslator
- 你需要从 PLM 系统（如 Teamcenter）获取产品结构数据 → 使用 DatasmithPLMXMLTranslator
- 你需要高精度控制 CAD 曲面的细分质量（公差、接缝策略） → 配置 `FWireSettings` / `FDatasmithTessellationOptions`

## 蓝图用法

本插件主要作为 Datasmith 翻译器在后台运行，蓝图直接交互的 API 较少。核心可配置结构体通过 Datasmith 选项面板暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FWireSettings::bUseLayerAsActor` | 是否将 Alias 文件的第一级图层作为 Actor 层级 | `FWireSettings` |
| `FWireSettings::bMergeGeometryByGroup` | 是否将同一 Group 下的几何节点合并 | `FWireSettings` |
| `UDatasmithWireOptions::Settings` | Wire 翻译器的完整导入设置 | `UDatasmithWireOptions` |

### 使用示例（蓝图描述）

Wire 翻译器的配置通过 Datasmith 导入选项面板自动呈现：

1. 在内容浏览器中选择要导入的 `.wire` 文件
2. Datasmith 导入对话框会自动显示 **Wire Translation Options** 面板
3. 勾选 `bUseLayerAsActor` 可保持 Alias 原始图层结构映射到 Unreal 的 Outliner 层级
4. 勾选 `bMergeGeometryByGroup` 可将同一 Group 下的多个曲面合并为单个 StaticMesh，减少 DrawCall
5. 底部的细分选项（继承自 `FDatasmithTessellationOptions`）控制网格精度

## C++ 用法

### 头文件引入

```cpp
#include "IWireInterface.h"
#include "DatasmithWireTranslator.h"
```

### 基本用法：通过 WireInterface 加载场景

以下示例展示如何直接使用 IWireInterface 接口加载 Wire 文件并提取网格数据。

```cpp
// 来源: Public/IWireInterface.h
// 创建 WireInterface 实例（内部根据 Alias 版本自动选择合适的实现）
TSharedPtr<IWireInterface> WireInterface = /* 通过工厂创建 */;

// 初始化接口，指定源文件
WireInterface->Initialize(TEXT("/Path/to/design.wire"));

// 配置导入选项
FWireSettings Settings;
Settings.bUseLayerAsActor = true;        // 图层映射为 Actor 层级
Settings.bMergeGeometryByGroup = true;   // 合并同组几何体
Settings.StitchingTechnique = EDatasmithCADStitchingTechnique::StitchingNone;
WireInterface->SetImportSettings(Settings);

// 设置缓存输出路径
WireInterface->SetOutputPath(FPaths::ProjectSavedDir() / TEXT("WireCache"));

// 加载场景（生成 Datasmith Scene 元素）
TSharedPtr<IDatasmithScene> Scene = MakeShared<IDatasmithScene>();
WireInterface->Load(Scene);

// 加载单个网格元素
TSharedPtr<IDatasmithMeshElement> MeshElement = /* 从 Scene 获取 */;
FDatasmithMeshElementPayload MeshPayload;
FDatasmithTessellationOptions TessOptions;
TessOptions.ChordTolerance = 0.1f;
TessOptions.MaxEdgeLength = 10.0f;

WireInterface->LoadStaticMesh(MeshElement, MeshPayload, TessOptions);
// MeshPayload 现在包含转换后的顶点和三角形数据
```

### 进阶用法：作为 Datasmith 翻译器注册

```cpp
// 来源: Private/DatasmithWireTranslator.h
// FDatasmithWireTranslator 继承自 FParametricSurfaceTranslator，
// 自动注册到 Datasmith 翻译器系统

// 当 Datasmith 处理 .wire 文件时，系统会自动实例化此翻译器
// 翻译器内部：
// 1. 检测本机安装的 Alias 版本
// 2. 选择匹配的 WireInterface 实现（2020~2026+）
// 3. 通过独立进程（DatasmithDispatcher）执行实际翻译
// 4. 输出 IDatasmithScene 和 StaticMesh 资产

// 如果需要自定义翻译行为，可继承 FDatasmithWireTranslator
class FMyWireTranslator : public FDatasmithWireTranslator
{
public:
    virtual void InitCommonTessellationOptions(FDatasmithTessellationOptions& Options) override
    {
        // 使用自动接缝而非手动接缝
        Options.StitchingTechnique = EDatasmithCADStitchingTechnique::StitchingSew;
    }
};
```

### Alias 版本自动检测

```cpp
// 来源: Public/IWireInterface.h
// IWireInterface 提供版本检测机制，自动选择合适的 WireInterface 实现
// 每个 WireInterface20XX 模块注册对应年份的接口

// 获取当前系统所需的 Alias 版本
uint64 RequiredVersion = IWireInterface::GetRequiredAliasVersion();
// 返回值对应本机安装的最高 Alias 版本，如 2026.0

// 模块通过 RegisterInterface 注册：
// IWireInterface::RegisterInterface(MajorVersion, MinorVersion, MakeInterface);
// 例如 WireInterface2026_0 注册 Alias 2026.0 版本的支持
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TechSoft` | 第三方 CAD 文件格式解析库（STEP、IGES、JT 等），由 CADInterfaces 依赖 |
| `OpenNurbs6` | NURBS 几体处理库（Rhino 3dm 格式），由 DatasmithOpenNurbsTranslator 依赖 |
| `DatasmithCore` | Datasmith 核心数据模型和翻译器框架 |
| `DatasmithContent` | Datasmith 资产类型和蓝图接口 |
| `MeshDescription` | 网格数据结构，用于传递细分后的三角面数据 |

> 无其他特殊依赖。其余均为标准 Core/Engine/Slate 等基础模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点的编译警告 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 添加兼容逻辑，支持安装了 Alias 2027 时 Wire 翻译器正常工作 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 升级 TechSoft 库至 2026.3 版本 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新 DatasmithCAD 缓存版本格式 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 提升类型转换警告在 MSVC 和 Clang 编译器间的可移植性 |

### 维护评价

- **活跃维护**：最近更新集中在 2026 年 5 月，距今不到 1 个月，且持续跟踪 Autodesk Alias 新版本（已支持到 2027）
- **第三方库定期更新**：TechSoft 和 OpenNurbs 依赖保持最新版本
- **跨平台兼容性改进**：持续修复 MSVC/Clang 差异问题和严格浮点模式警告
- **Enterprise 级别插件**：由 Epic Games 官方维护，用于专业建筑和工业设计可视化场景
- **推荐使用**：如果你的项目需要从 CAD 工业软件导入数据，这是官方唯一且持续维护的解决方案。注意需要手动启用且依赖 TechSoft 许可证

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)