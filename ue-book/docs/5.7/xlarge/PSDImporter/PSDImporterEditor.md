# PSD Importer

> 

| 属性 | 值 |
|---|---|
| 中文名 | PSD 导入器 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（材质函数、网格资源、测试资源） |
| 模块 | `PSDImporterEditor` (Editor), `PSDImporter` (Runtime), `PSDImporterCore` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-15 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PSDImporter) | |

## 用途

PSD Importer 是一个实验性插件，用于在 Unreal Engine 中直接导入 Adobe Photoshop 的 `.psd` 文件。它解析 PSD 的图层结构，将每个图层转换为独立的 Actor（四边面网格），并自动生成对应的分层材质，支持图层可见性、透明度、蒙版等常见 PSD 特性。该插件特别适合 2D 游戏、UI 设计、平面布局等需要将 Photoshop 设计稿无缝移植到 UE 中的工作流。

## 使用场景

- **2D 游戏关卡搭建**：将 PSD 中的场景元素（角色、背景、装饰）按图层导入，自动生成 Actor，直接摆放用于 2D 游戏。
- **UI 原型导入**：将 UI 设计稿的 PSD 分层导入，快速转换为可交互的 UI 控件基础。
- **平面设计可视化**：将复杂的设计矢量/位图分层作为叠加材质，在 3D 空间中展示或用作广告牌。
- **四边面网格与材质生成**：每个图层导出为一张纹理，生成对应的简单网格（四边面），并构建逐层混合的材质，支持裁剪、蒙版、全局透明度等效果。

## 蓝图用法

该插件主要面向编辑器工作流，蓝图中不直接暴露 PSD 导入相关的函数调用。导入后生成的 `APSDQuadActor` 和 `APSDQuadMeshActor` 可以在关卡蓝图中使用标准 Actor 方法（如设置位置、旋转、材质等）。用户可通过蓝图访问图层的纹理资产和材质实例。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateQuadActor` | 在指定世界中创建 PSD Quad Actor（蓝图不可见，编辑器内部调用） | `UPSDQuadsFactory` |

## C++ 用法

通过 C++ 可以编程式导入 PSD 文件，或使用工厂类创建分层 Actor/材质。

### 头文件引入

```cpp
#include "PSDDocumentImportFactory.h"
#include "PSDQuadsFactory.h"
#include "PSDImporterLayeredMaterialFactory.h"
#include "PSDDocument.h"
```

### 基本用法

**导入 PSD 文件并获取文档对象**

```cpp
// 使用工厂导入文件
UPersistentObject* CreatePSDAsset(const FString& FilePath)
{
    UPSDDocumentImportFactory* Factory = NewObject<UPSDDocumentImportFactory>();
    UObject* Package = CreatePackage(nullptr, TEXT("/Game/MyPSD"));
    FName AssetName = TEXT("MyDocument");
    EObjectFlags Flags = RF_Public | RF_Standalone;
    bool bCanceled = false;
    UObject* NewAsset = Factory->FactoryCreateFile(
        UPSDDocument::StaticClass(),
        Package,
        AssetName,
        Flags,
        FilePath,
        nullptr,
        nullptr,
        bCanceled
    );
    return NewAsset;
}
```

**从文档创建 Actor 和材质**

```cpp
// 在关卡中创建 Quad Actor
void CreatePSDQuadsInLevel(UWorld* World, UPSDDocument* Document)
{
    UPSDQuadsFactory* QuadsFactory = NewObject<UPSDQuadsFactory>();
    APSDQuadActor* QuadActor = QuadsFactory->CreateQuadActor(*World, *Document);
    // QuadActor 已包含所有图层对应的网格 Actor（APSDQuadMeshActor）
}

// 创建分层材质
void CreateLayeredMaterial(UPSDDocument* Document)
{
    UPSDImporterLayeredMaterialFactory* MaterialFactory = NewObject<UPSDImporterLayeredMaterialFactory>();
    if (MaterialFactory->CanCreateMaterial(Document))
    {
        UMaterial* Material = MaterialFactory->CreateMaterial(Document);
        // Material 包含了所有图层的混合逻辑
    }
}
```

**从已导入的资源重新创建**

内容浏览器右键菜单集成了快速创建材质和 Quad 的功能，详见“Demo 示例”。

### 进阶用法

**自定义导入选项**

通过设置 `UPSDImporterEditorSettings` 控制导入行为：

```cpp
// 获取设置
UPSDImporterEditorSettings* Settings = UPSDImporterEditorSettings::Get();
Settings->bResizeLayersToDocument = true;  // 将图层大小调整到文档尺寸
Settings->bImportInvisibleLayers = false;  // 跳过隐藏图层
```

**图层数据访问**

导入后通过 `UPSDDocument` 访问图层列表：

```cpp
TArray<FPSDFileLayer> Layers = Document->GetLayers();
for (const FPSDFileLayer& Layer : Layers)
{
    // 访问图层名称、可见性、纹理、蒙版等
    UTexture2D* LayerTexture = Layer.Texture;
    UTexture2D* MaskTexture = Layer.MaskTexture;
}
```

## Demo 示例

以下是一个最小可编译的编辑器模块，演示编程式导入 PSD 并生成 Actor。（需添加对应依赖）

**MyPSDImporter.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Engine/World.h"

class UPSDDocument;

class FMyPSDImporter
{
public:
    static void ImportAndSpawnInWorld(const FString& PSDFilePath, UWorld* InWorld);
};
```

**MyPSDImorter.cpp**

```cpp
#include "MyPSDImporter.h"
#include "PSDDocumentImportFactory.h"
#include "PSDQuadsFactory.h"
#include "PSDDocument.h"
#include "PSDImporterLayeredMaterialFactory.h"

void FMyPSDImporter::ImportAndSpawnInWorld(const FString& PSDFilePath, UWorld* InWorld)
{
    // 1. 导入 PSD 文件，创建资产
    UPSDDocumentImportFactory* Factory = NewObject<UPSDDocumentImportFactory>();
    UPackage* Package = CreatePackage(nullptr, TEXT("/Game/TempPSD"));
    FName AssetName = *FPaths::GetBaseFilename(PSDFilePath);
    EObjectFlags Flags = RF_Public | RF_Standalone;
    bool bCanceled = false;
    UPSDDocument* Document = Cast<UPSDDocument>(
        Factory->FactoryCreateFile(UPSDDocument::StaticClass(), Package, AssetName, Flags,
            PSDFilePath, nullptr, nullptr, bCanceled)
    );
    if (!Document) return;

    // 2. 创建分层材质
    UPSDImporterLayeredMaterialFactory* MatFactory = NewObject<UPSDImporterLayeredMaterialFactory>();
    if (MatFactory->CanCreateMaterial(Document))
    {
        UMaterial* Material = MatFactory->CreateMaterial(Document);
        // 材质保存在 /Game/TempPSD/ 下
    }

    // 3. 在关卡中生成 Quad Actor
    UPSDQuadsFactory* QuadFactory = NewObject<UPSDQuadsFactory>();
    APSDQuadActor* QuadActor = QuadFactory->CreateQuadActor(*InWorld, *Document);
    if (QuadActor)
    {
        QuadActor->SetActorLocation(FVector(0.0f, 0.0f, 100.0f));
    }
}
```

## 模块依赖

通过分析 `.uplugin` 和外部库引用，使用该插件需要以下依赖（标准 Core/Editor 模块省略）：

| 模块 | 用途 |
|---|---|
| `GeometryMask` | 几何体蒙版效果，用于图层蒙版处理 |
| `PSDImporter` | 运行时 PSD 文档数据模型 |
| `PSDImporterCore` | 核心 PSD 解析与图层处理逻辑 |
| `PSDImporterEditor` | 编辑器工具、工厂、自定义 UI |

第三方依赖：`PsdSDK`（外部静态库，提供底层 PSD 文件解析功能）。

## 维护状态

### 近期更新

- 2025-07-15 `bafe5da2` Silence incorrect V1051 warnings
- 2025-06-05 `00f9a7c0` Add Windows Arm64 libraries for PSD SDK + add build helper batch file
- 2025-05-15 `41b521d3` PSD Importer: Importing 16 and 32-bit PSDs now works correctly.
- 2025-05-15 `708e8190` PSD Importer: Hidden Quad Actor property AdjustForViewDistance because it is not user friendly.
- 2025-05-15 `c35a5c0e` PSD Importer: Importing layers with special characters now sanitizes the layer name.

### 维护评价

该插件创建于 2025 年 5 月，属于全新概念验证型实验性插件。目前处于活跃开发阶段（最近更新 2025-07-15），开发团队持续修复问题并扩展平台支持（如新增 Windows Arm64 库）。功能上基本可用，但可能存在以下限制：
- 仅支持 Windows 64 位平台（计划中可能扩展）。
- 实验性状态意味着 API 和行为可能发生较大变化。
- 需要对 PSD 文件进行一定兼容性测试（色彩模式、位深度等）。

**推荐使用场景**：适合 2D 游戏快速原型、UI 工作流验证。生产项目需谨慎评估稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PSDImporter)
- [官方文档]（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PSDImporter/Tests)