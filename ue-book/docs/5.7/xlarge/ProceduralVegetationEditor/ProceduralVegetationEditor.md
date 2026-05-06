# Procedural Vegetation Editor

> Node Graph based Editor that allows users to create Nanite Foliage ready vegetation directly in the engine. Users can load Procedural Vegetation Presets that contain prebuilt data for a species, and customize/create variations using the node graph.

| 属性 | 值 |
|---|---|
| 中文名 | 程序化植被编辑器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具、可视化组件、节点图） |
| 模块 | `ProceduralVegetation` (Runtime), `ProceduralVegetationEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-12-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ProceduralVegetationEditor) | |

## 用途

该插件基于 **PCG（程序化内容生成）** 框架扩展，提供了一个 **节点图编辑器**，帮助美术/设计师在编辑器内直接创建 Nanite 就绪的植被资产。用户可以从预置（Preset）加载特定物种的构建数据，再通过节点图自定义和生成变体，最终输出 **Static Mesh** 或 **Skeletal Mesh** 叶子/树枝等植被模型，并自动启用 **Nanite** 以优化渲染性能。

核心功能包括：
- **节点式工作流**：基于 PCG 图形编辑器，用节点定义分枝、叶子、风力变形等
- **实时可视化**：视口支持多种渲染模式（点、网格、骨头、风力网格等）
- **导出管线**：将生成的几何数据导出为静态或骨骼网格，附带 Nanite 装配数据
- **调试可视化**：显示点云、枝条、骨骼等中间数据，便于调试

## 使用场景

- 你想在引擎内利用节点图快速生成风格化或写实的树木/植物，而不依赖外部 DCC（如 Blender/Maya）
- 需要生成大量 Nanite 植被，并希望每棵植物的分枝、叶子位置、风力变形等参数可调
- 需要使用程序化工作流，在运行时或构建时生成多变的植物变体
- 你已经是 PCG 用户，希望扩展 PCG 管线至植被领域

## 蓝图用法

该插件主要面向编辑器和工作流，运行时蓝图暴露的接口有限。以下列出与编辑器设置相关的可配置属性（在 Project Settings 中配置）。

### 编辑器设置

| 节点/属性 | 说明 | 所在类 |
|---|---|---|
| `Export Type` | 选择导出模式：选中节点输出 / 批量导出 | `UPVEditorSettings` |
| `bShowMannequin` | 视口中显示角色模型参考 | `UPVEditorSettings` |
| `bShowScaleVisualization` | 显示比例标尺 | `UPVEditorSettings` |
| `GrowthDataPinColor` | 节点图中“GrowthData”引脚的颜色 | `UPVEditorSettings` |
| `MeshDataPinColor` | 节点图中“MeshData”引脚的颜色 | `UPVEditorSettings` |
| `FoliageMeshDataPinColor` | 节点图中“FoliageMeshData”引脚的颜色 | `UPVEditorSettings` |

以上属性可通过 **Edit > Project Settings > Procedural Vegetation Editor Settings** 访问和修改，也可以在蓝图中通过 `GetDefault<UPVEditorSettings>()` 读取。

> 注意：目前没有公开 `BlueprintCallable` 或 `BlueprintImplementableEvent` 函数，如需自动化请使用 C++ 或 Python 脚本。

## C++ 用法

### 头文件引入

```cpp
#include "ProceduralVegetationEditorModule.h"
#include "PVEditorSettings.h"
#include "PVEditor.h"               // 编辑器实例
#include "AssetDefinition_ProceduralVegetation.h"
```

### 基本用法

#### 创建并打开编辑器

```cpp
// 在资产编辑器中打开 ProceduralVegetation 资产
UPackage* Package = CreatePackage(nullptr, TEXT("/Game/MyVegetation"));
UProceduralVegetation* Vegetation = NewObject<UProceduralVegetation>(Package, FName("MyVegetation"), RF_Public | RF_Standalone);

// 获取编辑器模块
FProceduralVegetationEditorModule& Module = FModuleManager::LoadModuleChecked<FProceduralVegetationEditorModule>("ProceduralVegetationEditor");
Module.Get()->RegisterMenus();

// 打开编辑器（需要实现具体工具上下文）
// FAssetEditorManager::Get().OpenEditorForAsset(Vegetation);
```

*来源: PVEditorCommands.h, PVEditor.h*

#### 配置编辑器设置

```cpp
// 修改导出模式为批量导出
UPVEditorSettings* Settings = GetMutableDefault<UPVEditorSettings>();
Settings->ExportType = EPVExportType::BatchExport;
Settings->SaveConfig();
```

*来源: PVEditorSettings.h*

#### 访问节点图数据并导出

```cpp
// 假设已有 ProceduralVegetation 对象和其节点图
UProceduralVegetation* Vegetation = ...;

// 调用导出辅助函数（需要 Include ExportHelper）
PV::Export::EExportResult Result = PV::Export::ExportCollectionAsMesh(
    Vegetation,
    *Collection,          // FManagedArrayCollection 引用
    ExportParams,
    OutCreatedAssets,
    StatusReportCallback
);
```

*来源: Helpers/PVExportHelper.h*

### 进阶用法

#### 自定义可视化渲染模式

```cpp
// 在编辑器视口切换渲染模式
if (SPVEditorViewport* Viewport = ...)
{
    Viewport->OnNodeInspectionChanged(Settings);
    Viewport->OnVisualizationModeChanged(EPVVisualizationMode::BonesMesh);
}
```

*来源: SPVEditorViewport.h*

#### 注册自定义调试可视化器

继承 `FPVDebugVisualizationBase` 并实现 `GetPivotPositions` 和 `GetPivot`，然后通过 `FPVDebugVisualizer::CreateVisualizer` 注册。

```cpp
class FMyCustomVisualization : public FPVDebugVisualizationBase
{
protected:
    virtual TArray<FVector3f> GetPivotPositions(const FManagedArrayCollection& InCollection) override;
    virtual void GetPivot(const FManagedArrayCollection& InCollection, int InIndex, FVector3f& OutPos, float& OutScale) override;
};

// 在适当位置创建并绘制
FPVDebugVisualizationPtr Visualizer = MakeShared<FMyCustomVisualization>();
FVisualizerDrawContext Context(Collection, Settings, SceneParams);
Visualizer->Draw(Context);
```

*来源: Visualizations/DebugVisualization/PVDebugVisualizationBase.h*

## Demo 示例

以下简易示例创建一个 `ProceduralVegetation` 资产并打开编辑器（假设已有模块加载）。实际使用需要结合 PCG 节点图框架。

```cpp
// PVEditorDemo.h
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"

class FPVEditorDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// PVEditorDemo.cpp
#include "PVEditorDemo.h"
#include "ProceduralVegetation.h"
#include "PVEditor.h"

IMPLEMENT_MODULE(FPVEditorDemoModule, PVEditorDemo)

void FPVEditorDemoModule::StartupModule()
{
    // 创建临时包
    UPackage* TempPackage = CreatePackage(nullptr, TEXT("/Temp/DemoVegetation"));
    UProceduralVegetation* Veg = NewObject<UProceduralVegetation>(TempPackage, FName("DemoVeg"), RF_Public | RF_Standalone);
    
    // 打开编辑器（需要确保资产已注册）
    if (FAssetEditorManager::Get().OpenEditorForAsset(Veg) == EBindingOrOpeningResult::Failed)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open Procedural Vegetation editor"));
    }
}

void FPVEditorDemoModule::ShutdownModule() {}
```

注意：实际编辑器打开可能需要先注册资产类型，更完整的示例请参考引擎自带的 `ProceduralVegetation` 测试。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PCG` | PCG 运行时框架，提供节点图底层 |
| `PCGEditor` | PCG 编辑器扩展，本编辑器继承自 `FPCGEditor` |
| `GeometryCollectionEngine` | 使用 `FManagedArrayCollection` 作为核心数据容器 |
| `GeometryCollectionEditor` | 几何集合编辑器支持（Nanite装配数据构建） |
| `NaniteActorTools` | Nanite 装配数据构建辅助 |
| `AssetTools` | 资产注册、导出等 |
| `EditorStyle` | 编辑器 UI 样式 |

其余为常见模块（Core, Engine, Slate, UnrealEd 等），不逐一列出。

## 维护状态

### 近期更新

- 2025-12-18 `b0eaa7e8` — [PVE] Foliage condition system
- 2025-12-18 `e6d3fae0` — [PVE] Added UV1 and UV2 data also added Generation data in UV0.X
- 2025-12-18 `0565d5cc` — [PVE] Fix the missing bones for some parts of the mesh.
- 2025-12-18 `5a2cd1cc` — Fixed foliage face orientation
- 2025-12-18 `e46aff7e` — Bug fixes

### 维护评价

- **创建时间**：2025-12-18，非常新。
- **近期更新**：全部集中在同一天，包含功能新增（条件系统、UV数据）和 Bug 修复，表明初始开发阶段。
- **活跃度**：极高，但尚处于实验性阶段。
- **已知问题**：从 commit message 看仍有骨头缺失等 Bug；缺乏正式文档和测试资源。
- **推荐使用**：仅建议在尝鲜或参与开发时使用，生产项目需谨慎。插件仅支持 UE5.5+，且依赖 PCG 实验性模块。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ProceduralVegetationEditor)
- 官方文档：暂无（`DocsURL` 为空）
- 测试用例：暂未发现独立测试目录（推测在 Engine/Tests 下未有公开）