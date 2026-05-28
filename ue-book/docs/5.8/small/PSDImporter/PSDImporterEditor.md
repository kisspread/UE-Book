# PSD Importer

> 导入 Adobe Photoshop (.psd) 文件，提取图层、纹理和遮罩，并自动创建对应的 UE5 资产（材质、纹理、四边形网格）。

| 属性 | 值 |
|---|---|
| 中文名 | PSD 导入器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质资产、纹理资产、文档资产） |
| 模块 | `PSDImporterEditor` (Editor), `PSDImporter` (Runtime), `PSDImporterCore` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter) | |

## 用途

PSD Importer 是一个**工作流工具**，旨在简化将 Adobe Photoshop 的 PSD 设计文件集成到 Unreal Engine 5 中的过程。它不仅仅是导入一张合并后的图片，而是**保留 PSD 文件的完整图层结构**。

这个插件的核心价值在于：
1.  **分层导入**：将 PSD 文件的每个图层（以及可选的遮罩）作为独立的 `UTexture2D` 纹理资产导入。
2.  **材质自动化**：基于导入的图层，**自动创建**一个分层材质（Layered Material）。这个材质能够根据图层的可见性、混合模式和顺序，将多个纹理组合成最终效果。
3.  **场景集成**：自动创建带有四边形网格的 Actor（Quad Mesh Actor），并将创建的材质实例应用其上，使用户可以在关卡中直接看到 PSD 设计的效果。

它主要解决游戏开发中**UI 设计稿、2D 素材、快速原型**等场景下，设计师与程序员之间的资产同步和迭代效率问题。

## 使用场景

- **游戏 UI 设计**：设计师在 Photoshop 中设计 UI 界面，包含背景、图标、文字等多个图层。使用此插件一键导入，即可在 UE5 中获得一个与设计稿图层结构完全对应的材质和 Actor，方便进行后续的交互逻辑开发和动画制作。
- **2D 游戏素材管理**：对于使用大量 2D 贴图的游戏（如地图、角色立绘），可以将相关的美术资源组织在一个 PSD 文件的不同图层中，导入后能清晰管理每个独立部件。
- **快速原型与布局**：关卡设计师可以将布局草图保存为 PSD，导入后快速搭建出场景的视觉原型。
- **需要分层材质控制的场景**：当需要在引擎内通过参数动态控制图层的显示、透明度或顺序时，自动生成的材质提供了基础。

## 蓝图用法

此插件的核心功能主要通过**编辑器操作和资产工厂**实现，而非暴露大量蓝图节点。其主要的“蓝图用法”体现在生成的资产上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetAssetData` | 获取导入的 PSD 文档资产信息。 | `UAssetDefinition_PSDDocument` (用于内容浏览器集成) |
| `CreateQuadActor` | 根据 PSD 文档创建一个包含四边形网格的 Actor。 | `UPSDQuadsFactory` |
| `CreateMaterial` | 根据 PSD 文档创建分层材质。 | `UPSDImporterLayeredMaterialFactory` |

**使用示例（蓝图描述）：**
1.  通过内容浏览器，将 `.psd` 文件拖拽到项目文件夹中。
2.  导入完成后，会生成一个 `UPSDDocument` 资产以及对应的纹理和材质资产。
3.  在内容浏览器中右键点击 `UPSDDocument` 资产，选择“创建 PSD 材质”或“创建 PSD 四边形”。
4.  将生成的 `APSDQuadActor` 拖入关卡，即可在场景中看到导入的 PSD 设计效果。

## C++ 用法

### 头文件引入

根据使用的功能模块，引入相应头文件：
```cpp
// 引入运行时核心类型（如文档资产）
#include "PSDImporter/PSDImporter.h"
// 引入编辑器功能（如工厂、自定义）
#include "PSDImporterEditor/PSDImporterEditor.h"
```

### 基本用法（工厂模式）

插件的核心逻辑封装在工厂类中，常用于编辑器工具开发。

```cpp
// 示例：在C++工具代码中，通过工厂类创建材质和四边形
// 来源文件：基于 Private/Factories/PSDImporterLayeredMaterialFactory.h 和 Private/Factories/PSDQuadsFactory.h 推断

// 假设已经获取到导入的 UPSDDocument 资产指针 (DocumentAsset)
if (DocumentAsset)
{
    // 1. 创建材质
    UPSDImporterLayeredMaterialFactory MaterialFactory;
    if (MaterialFactory.CanCreateMaterial(DocumentAsset))
    {
        UMaterial* NewMaterial = MaterialFactory.CreateMaterial(DocumentAsset);
        if (NewMaterial)
        {
            // 材质创建成功，可进一步处理
            UE_LOG(LogTemp, Log, TEXT("Created Material: %s"), *NewMaterial->GetName());
        }
    }

    // 2. 在指定世界中创建四边形 Actor
    if (UWorld* World = GEditor->GetEditorWorldContext().World())
    {
        UPSDQuadsFactory QuadFactory;
        APSDQuadActor* QuadActor = QuadFactory.CreateQuadActor(*World, *DocumentAsset);
        if (QuadActor)
        {
            // 四边形 Actor 创建成功，可设置位置等
            UE_LOG(LogTemp, Log, TEXT("Created Quad Actor: %s"), *QuadActor->GetName());
        }
    }
}
```

### 进阶用法（内容浏览器集成）

插件本身就是一个编辑器扩展的范例，其内容浏览器集成展示了如何扩展资产的右键菜单。

```cpp
// 示例：参考 PSDImporterContentBrowserIntegration.h，为自定义资产类型添加右键菜单项
// 来源文件：基于 Private/PSDImporterContentBrowserIntegration.h 推断

class FMyCustomAssetIntegration
{
public:
    void Integrate()
    {
        // 获取内容浏览器模块
        FContentBrowserModule& ContentBrowserModule = FModuleManager::LoadModuleChecked<FContentBrowserModule>(TEXT("ContentBrowser"));

        // 扩展资产选择菜单
        ContentBrowserModule.GetAllAssetViewContextMenuExtenders().Add(
            FContentBrowserMenuExtender_SelectedAssets::CreateRaw(this, &FMyCustomAssetIntegration::OnExtendContentBrowserAssetSelectionMenu));
    }

    TSharedRef<FExtender> OnExtendContentBrowserAssetSelectionMenu(const TArray<FAssetData>& InSelectedAssets)
    {
        TSharedRef<FExtender> Extender = MakeShared<FExtender>();
        // 添加菜单逻辑...
        return Extender;
    }
};
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何在编辑器工具中触发 PSD 导入并处理生成的资产。此示例假设你已配置好模块依赖。

```cpp
// MyPSDTool.h
#pragma once

#include "CoreMinimal.h"

class UPSDDocument;

class FMyPSDTool
{
public:
    /** 模拟一个导入PSD文件并创建基础资产的函数 */
    void ImportPSDAndCreateAssets(const FString& PSDFilePath);

private:
    /** 内部回调，处理导入完成后的文档资产 */
    void OnDocumentImported(UPSDDocument* ImportedDocument);
};
```

```cpp
// MyPSDTool.cpp
#include "MyPSDTool.h"
#include "PSDImporter/PSDImporter.h" // 引入UPSDDocument类型
#include "Factories/PSDDocumentImportFactory.h" // 引入导入工厂
#include "AssetRegistry/AssetRegistryModule.h"

void FMyPSDTool::ImportPSDAndCreateAssets(const FString& PSDFilePath)
{
    // 获取导入工厂
    UPSDDocumentImportFactory* ImportFactory = NewObject<UPSDDocumentImportFactory>();
    if (!ImportFactory)
    {
        return;
    }

    // 设置导入参数
    UPackage* Package = CreatePackage(nullptr, TEXT("/Game/ImportedPSD/TestDocument"));
    EObjectFlags Flags = RF_Public | RF_Standalone;
    bool bOperationCanceled = false;
    FFeedbackContext Warn;

    // 执行导入
    UObject* ImportedObject = ImportFactory->FactoryCreateFile(
        UPSDDocument::StaticClass(),
        Package,
        FName(TEXT("TestDocument")),
        Flags,
        PSDFilePath,
        nullptr,
        &Warn,
        bOperationCanceled
    );

    if (UPSDDocument* Document = Cast<UPSDDocument>(ImportedObject))
    {
        OnDocumentImported(Document);
    }
}

void FMyPSDTool::OnDocumentImported(UPSDDocument* ImportedDocument)
{
    if (!ImportedDocument) return;

    // 记录导入的资产
    UE_LOG(LogTemp, Display, TEXT("Successfully imported PSD document: %s"), *ImportedDocument->GetName());
    
    // 这里可以调用插件提供的其他工厂，如 MaterialFactory 或 QuadFactory
    // 来为导入的文档自动创建材质和四边形，逻辑参见上文“基本用法”。
    
    // 保存新创建的资产包
    FAssetRegistryModule::AssetCreated(ImportedDocument);
    ImportedDocument->GetOutermost()->MarkPackageDirty();
}
```

## 模块依赖

要使用此插件，你的模块需要根据具体使用场景添加以下依赖。常见的 Core、Engine 等依赖已省略。

| 模块 | 用途 |
|---|---|
| `PSDImporter` | 引入 `UPSDDocument` 等运行时核心数据类型。 |
| `PSDImporterEditor` | 引入编辑器工厂、自定义、资产定义等功能，用于创建资产或扩展编辑器UI。 |
| `GeometryMask` | 插件生成的材质可能会使用此模块提供的几何遮罩功能。 |

在你的 `.Build.cs` 文件中，添加类似如下代码：
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "PSDImporter",          // 如果需要访问文档数据
    "PSDImporterEditor",    // 如果需要在编辑器工具中使用导入功能
    "GeometryMask"          // 通常由PSDImporter模块内部依赖，但若直接使用遮罩功能则需要
});
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移，无功能变化。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复上次代码替换错误后的重新提交。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回滚了之前的提交（CL51314860）。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修改委托访问方式以修复注册问题。 |
| 2025-07-15 | `bafe5da2` | Silence incorrect V1051 warnings. | 静音静态分析工具的错误警告。 |

### 维护评价

- **状态**：**实验性且维护不活跃**。
- **分析**：该插件于 2025 年 4 月首次提交，标记为实验性（`IsExperimentalVersion=true`）。最近的提交（2026年4月）均为**编译警告修复、日志系统迁移或代码回滚**，没有新的功能开发。这表明插件在提交后处于**基本维护状态**，以保证其能在最新引擎版本上编译通过，但**未进行功能增强或活跃开发**。
- **建议**：由于是实验性插件且功能已基本成型但停止开发，**不推荐用于生产项目的关键路径**。它适合用于**原型制作、内部工具链或学习参考**。使用前需自行评估其稳定性和功能完备性。主要限制在于仅支持 Win64 平台。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter)
- 官方文档：无
- 测试用例：未在提供的路径中发现公开的自动化测试文件。