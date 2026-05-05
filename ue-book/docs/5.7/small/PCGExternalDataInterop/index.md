# Procedural Content Generation Framework (PCG) External Data Interop

> Extra plugin for Procedural Content Generation Framework interacting with external data formats.

| 属性 | 值 |
|---|---|
| 分类 | PCGInterops (原 Editor) |
| 默认启用 | 否 |
| 包含内容 | 是 |
| 模块 | PCGExternalDataInterop (Runtime), PCGExternalDataInteropEditor (Editor) |
| 创建时间 | 2023-06-14 |
| 年龄标签 | 🆕 (≤5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/PCGInterops/PCGExternalDataInterop) | |

## 用途

PCGExternalDataInterop 是 PCG 框架的一个扩展插件，专门用于将外部数据格式导入到 PCG 图表中。目前该插件的核心功能是**读取 Alembic (.abc) 文件中的点云数据**，并将其转换为 PCG 可用的 `UPCGBasePointData`。

这个插件解决的核心问题是：PCG 框架本身专注于运行时程序化内容生成，但用户经常需要从外部 DCC 工具（如 Houdini、Maya、3ds Max）导出的 Alembic 文件中获取预计算的点云数据。该插件充当桥梁，将 Alembic 点云直接桥接到 PCG 数据管线中，使得外部生成的空间分布数据可以直接驱动 PCG 图表的放置逻辑。

**注意**：此插件默认未启用，且标记为 Beta 版本（`IsBetaVersion: true`）。

## 使用场景

- **你从 Houdini 导出了一个城市街区的点云** → 用此插件在 PCG 图表中直接加载这些点位，驱动建筑/植被的放置
- **你有一组预定义的散布点位**（来自外部工具）→ 通过 Alembic 文件导入 PCG，结合 PCG 规则进行细节生成
- **CitySample 风格的工作流** → 插件内置了 CitySample 预设，自动配置右手坐标系 Y-up 及 orient/scale 映射

## 蓝图用法

此插件提供了蓝图函数库 `UPCGLoadAlembicFunctionLibrary`，可通过蓝图直接调用 Alembic 导入功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ExportAlembicFileToPCG` | 将 Alembic 文件导出为 PCG Data Asset | `UPCGLoadAlembicFunctionLibrary` |
| `SetupFromStandard` | 使用预设配置（如 CitySample）自动设置转换参数 | `UPCGLoadAlembicFunctionLibrary` |
| `LoadAlembicFileToPCG` | ⚠️ **已废弃**，请使用 `ExportAlembicFileToPCG` | `UPCGLoadAlembicFunctionLibrary` |

### 使用示例（蓝图描述）

**场景：通过蓝图将 Alembic 文件导出为 PCG Asset**

1. 创建一个 `FPCGLoadAlembicBPData` 结构体变量
2. 设置 `AlembicFilePath` 为你的 `.abc` 文件路径
3. 根据需要配置 `ConversionSettings`（缩放/旋转）和 `AttributeMapping`
4. 如果使用 CitySample 格式，调用 `SetupFromStandard` 节点，传入 `EPCGLoadAlembicStandardSetup::CitySample` 自动配置
5. 调用 `ExportAlembicFileToPCG`，传入设置数据和导出参数
6. 生成的 PCG Data Asset 将包含从 Alembic 文件中提取的点云数据

**PCG 图表中的 Load Alembic 节点**：

在 PCG 图表编辑器中，插件注册了一个 **"Load Alembic"** 节点（`UPCGLoadAlembicSettings`）。该节点：
- 在 Alembic 类别下提供 `AlembicFilePath` 属性（带 .abc 文件过滤器）
- 支持 `ConversionScale`、`ConversionRotation`、`bConversionFlipHandedness` 转换参数
- 支持 `AttributeMapping` 将 Alembic 属性映射到 PCG 属性
- 所有属性都标记为 `PCG_Overridable`，可在 PCG 图表中动态覆盖

## C++ 用法

### 头文件引入

```cpp
// Runtime 模块
#include "Elements/PCGLoadAlembicElement.h"

// Editor 模块（蓝图函数库）
#include "PCGLoadAlembic.h"
```

### 基本用法

Alembic 加载的核心是 `FPCGLoadAlembicElement`，它继承自 `FPCGExternalDataElement`，实现了 Alembic 特定的 `PrepareLoad` 和 `ExecuteLoad` 逻辑。

**PCG 图表节点设置（Runtime）**：

```cpp
// 创建 Load Alembic 节点设置
UPCGLoadAlembicSettings* Settings = NewObject<UPCGLoadAlembicSettings>();
Settings->AlembicFilePath.FilePath = TEXT("/Game/Data/pointcloud.abc");

// 配置坐标转换（默认值适配 Maya 的右手 Y-up 坐标系）
Settings->ConversionScale = FVector(1.0f, -1.0f, 1.0f); // 翻转 Y 轴
Settings->ConversionRotation = FVector::ZeroVector;
Settings->bConversionFlipHandedness = false;
```

来源：`Source/PCGExternalDataInterop/Public/Elements/PCGLoadAlembicElement.h`

### 进阶用法

**CitySample 预设配置**：

```cpp
// 使用 CitySample 预设自动配置所有参数
UPCGLoadAlembicSettings* Settings = NewObject<UPCGLoadAlembicSettings>();
Settings->SetupFromStandard(EPCGLoadAlembicStandardSetup::CitySample);
```

CitySample 预设会自动设置：
- `ConversionScale = (1, 1, 1)` — 不缩放
- `ConversionRotation = (0, 0, 0)` — 不旋转
- `bConversionFlipHandedness = true` — 翻转旋转方向
- 属性映射：
  - `position` → `$Position.xzy`（交换 Y/Z 轴）
  - `scale` → `$Scale.xzy`
  - `orient` → `$Rotation.xzyw`（交换 Y/Z 分量）

来源：`Source/PCGExternalDataInterop/Private/Elements/PCGLoadAlembicElement.cpp` 第 101-126 行

**通过蓝图函数库导出 PCG Asset（Editor）**：

```cpp
#include "PCGLoadAlembic.h"

FPCGLoadAlembicBPData LoadData;
LoadData.AlembicFilePath.FilePath = TEXT("/Game/Data/pointcloud.abc");

// 使用 CitySample 预设
UPCGLoadAlembicFunctionLibrary::SetupFromStandard(LoadData, EPCGLoadAlembicStandardSetup::CitySample);

// 导出为 PCG Data Asset
FPCGAssetExporterParameters ExportParams;
ExportParams.bSaveOnExport = true;
ExportParams.PackagePath = TEXT("/Game/PCG/ImportedPointCloud");
UPCGLoadAlembicFunctionLibrary::ExportAlembicFileToPCG(LoadData, ExportParams);
```

来源：`Source/PCGExternalDataInteropEditor/Private/PCGLoadAlembic.cpp`

### 支持的 Alembic 数据类型

插件通过 `CreateAlembicPropAccessor` 函数支持以下 Alembic 数据类型到 PCG 类型的映射：

| Alembic 类型 | Extent | PCG 类型 |
|---|---|---|
| float32 | 1 | `float` |
| float32 | arrayExtent 2 | `FVector2D` |
| float32 | arrayExtent 3 | `FVector` |
| float32 | arrayExtent 4 | `FVector4` |
| float32 | 2 | `FVector2D` |
| float32 | 3 | `FVector` |
| float32 | 4 | `FVector4` |
| float64 | 1 | `double` |
| float64 | 2-4 | `FVector2D`/`FVector`/`FVector4` |
| boolean | 1 | `bool` |
| int8/int16/int32/int64 | 1 | `int32`/`int64` |
| string | 1 | `FString` |

**Position 特殊处理**：Alembic 中的 `position` 属性会被直接映射到 PCG 点的 Transform 位置，除非用户在 `AttributeMapping` 中提供了自定义映射。

**注意**：只支持 `IPoints` 类型的 Alembic 对象（点云），不支持网格体或曲线等其他 Alembic 几何类型。

## Demo 示例

### 最小使用示例

```cpp
// MyPCGAlembicLoader.h
#pragma once

#include "CoreMinimal.h"

class FMyPCGAlembicLoader
{
public:
    static void LoadAlembicPointCloud(const FString& AbcFilePath);
};
```

```cpp
// MyPCGAlembicLoader.cpp
#include "MyPCGAlembicLoader.h"
#include "PCGLoadAlembic.h"

void FMyPCGAlembicLoader::LoadAlembicPointCloud(const FString& AbcFilePath)
{
    FPCGLoadAlembicBPData LoadData;
    LoadData.AlembicFilePath.FilePath = AbcFilePath;
    
    // 使用 CitySample 预设
    UPCGExternalDataInteropEditorLibrary::SetupFromStandard(
        LoadData, EPCGLoadAlembicStandardSetup::CitySample);
    
    // 导出到 PCG Asset
    FPCGAssetExporterParameters Params;
    Params.bSaveOnExport = true;
    UPCGExternalDataInteropEditorLibrary::ExportAlembicFileToPCG(LoadData, Params);
}
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "PCG"
});

PrivateDependencyModuleNames.AddRange(new string[]
{
    "PCGExternalDataInterop",
    "PCGExternalDataInteropEditor",
    "AlembicLib",
    "AlembicLibrary"
});
```

## 模块依赖

### PCGExternalDataInterop (Runtime)

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型和工具 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `Projects` | 插件/模块管理 |
| `PCG` | PCG 框架核心 |
| `UnrealEd` | （仅编辑器构建）编辑器支持 |
| `AlembicLib` | （仅编辑器构建）Alembic C++ 库底层支持 |
| `AlembicLibrary` | （仅编辑器构建）UE 的 Alembic 抽象层 |

### PCGExternalDataInteropEditor (Editor)

| 模块 | 用途 |
|---|---|
| `Core`, `CoreUObject`, `Engine`, `Projects`, `PCG` | 同上 |
| `PCGEditor` | PCG 编辑器集成 |
| `PCGExternalDataInterop` | Runtime 模块 |
| `UnrealEd` | 编辑器框架 |
| `AlembicLib`, `AlembicLibrary` | Alembic 库 |

### 插件依赖

| 插件 | 用途 |
|---|---|
| `PCG` | PCG 框架主插件 |
| `AlembicImporter` | UE 的 Alembic 文件导入器 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-09-23 | `17a2876` | Better management of windows headers wrt alembic files | 修复 Windows 平台头文件与 Alembic 库的冲突问题 |
| 2025-09-23 | `ded2b7e` | Moved code to implementation file for better isolation. Also removed GetObject define that could cause issues. | 重构：将代码移到 .cpp 文件以改善隔离性，修复 `GetObject` 宏冲突 |
| 2025-05-14 | `6bd1bde` | Fix compile error because winnt.h is included by Alembic includes | 修复 Alembic 头文件中 `winnt.h` 重定义 `MemoryBarrier` 导致的编译错误 |

### 维护评价

- **创建时间**：2023-06-14（约 2.9 年前）
- **最近更新频率**：2025 年有 3 次提交，主要集中在编译兼容性修复
- **维护状态**：**维护中** — 有持续的 bug 修复，但主要是平台兼容性问题，无功能性更新
- **Beta 状态**：`IsBetaVersion: true`，`EnabledByDefault: false`，说明 Epic 将其视为实验性功能
- **已知限制**：
  - 仅支持 Alembic 的 `IPoints`（点云）类型，不支持网格/曲线
  - Alembic 解析仅在编辑器构建中可用（`#if WITH_EDITOR`），运行时会报错
  - Windows 平台与 Alembic 库存在头文件冲突问题（已修复但需注意）
- **推荐程度**：如果你的工作流涉及从 Houdini/Maya 等 DCC 工具向 PCG 导入点云数据，推荐使用。但需注意这是 Beta 功能，API 可能变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/PCGInterops/PCGExternalDataInterop)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)
- 测试用例：未发现专门的测试文件
