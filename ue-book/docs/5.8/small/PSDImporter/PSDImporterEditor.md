# PSD Importer

> （无描述）

| 属性 | 值 |
|---|---|
| 中文名 | PSD 导入器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质模板、资产定义） |
| 模块 | `PSDImporterEditor` (Editor), `PSDImporter` (Runtime), `PSDImporterCore` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter) | |

## 用途

该插件解决了从 Adobe Photoshop (PSD) 文件到 Unreal Engine 的资产导入和材质创建工作流问题。其核心功能是将一个 PSD 文件解析为其文档结构和各个图层，并能够：

1.  **资产导入**：将 PSD 文件作为 `UPSDDocument` 资产导入内容浏览器，并为其每个图层单独生成纹理资产。
2.  **材质生成**：自动创建复杂的分层材质（Layered Material），该材质能够根据 PSD 图层的顺序、透明度和遮罩（Mask）信息，在引擎中正确地合成和显示图像。
3.  **场景集成**：提供 Actor 工厂，允许将导入的 `PSDDocument` 直接拖拽到关卡中，生成对应的四边形网格 Actor (Quad Actor) 以在 3D 空间中显示设计稿。
4.  **编辑器集成**：在内容浏览器中为 PSD 资产添加右键菜单，支持快速创建材质和场景四边形，并提供自定义属性面板以预览图层和遮罩缩略图。

简而言之，它是 UE 与 Photoshop 设计稿之间的桥梁，特别适用于需要精确还原 UI 设计或 2D 平面艺术资产的场景。

## 使用场景

-   你是一位 UI 设计师，将设计稿保存为分层的 PSD 文件 → 用此插件导入，可自动生成对应的 UI 纹理和材质，便于在 UMG 中使用。
-   你是一位 2D 美术，绘制了包含多个图层和特效（如光照、混合模式）的角色立绘或场景背景 → 用此插件导入，自动创建材质，可在 3D 空间中作为海报或墙面贴图展示，且能保留图层的叠加逻辑。
-   你需要在引擎中快速预览一个 Photoshop 设计稿的最终效果 → 用此插件导入并拖入关卡，即可直接看到合成后的结果。
-   你的工作流需要频繁地根据 PSD 文件的修改更新引擎中的资产 → 此插件支持重新导入（Reimport），可以同步更新图层纹理和材质。

## 蓝图用法

此插件的核心功能主要通过编辑器菜单和拖放操作触发，公开的蓝图可调用函数较少。主要的交互发生在资产上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateMaterial` | 根据传入的 `UPSDDocument` 资产，创建对应的分层材质资产。 | `UPSDImporterLayeredMaterialFactory` |
| `CreateQuadActor` | 在指定的世界中，根据 `UPSDDocument` 创建一个包含所有图层四边形的 Actor。 | `UPSDQuadsFactory` |

### 使用示例（蓝图描述）

1.  **导入 PSD**：在内容浏览器中右键，选择“导入到...”，选择你的 .psd 文件。一个 `PSDDocument` 资产和对应的纹理资产会被生成。
2.  **创建材质**：在内容浏览器中选中刚刚导入的 `PSDDocument` 资产，右键，在扩展菜单中找到并点击“创建 PSD 材质”（Create PSD Material）。一个名为 `M_[文档名]` 的材质资产将被创建。
3.  **生成场景四边形**：在内容浏览器中选中 `PSDDocument` 资产，右键，点击“创建 PSD 四边形”（Create PSD Quads）。然后将此资产从内容浏览器拖拽到关卡视口中，一个 `PSDQuadActor` 将会被放置在场景中，它会自动使用之前创建的材质进行渲染。
4.  **查看属性**：选中场景中的 `PSDQuadActor`，在细节面板中你可以看到其引用的源 `PSDDocument`，并可以调整其整体缩放等属性。

## C++ 用法

该插件的 Runtime 模块 (`PSDImporterCore`) 提供了 PSD 文件解析的核心库，而 Editor 模块则构建了完整的导入和材质创建流程。

### 头文件引入

```cpp
#include "PSDImporterCore/PSDFileDocument.h"
#include "PSDImporterCore/PSDFileLayer.h"
#include "PSDImporter/PSDDocument.h"
```

### 基本用法

以下代码展示了如何在 C++ 中检查一个已导入的 `PSDDocument` 资产的基本信息。

*基于 `PSDFileDocument.h` 和 `PSDDocument.h` 的接口设计。*

```cpp
// 假设你已经通过某种方式（如资产注册表）获得了一个 UPSDDocument 指针
if (UPSDDocument* MyPSDDocument = Cast<UPSDDocument>(SomeLoadedObject))
{
    // 获取底层的 PSD 文件数据结构（包含解析后的图层信息）
    const FPSDFileDocument& FileDoc = MyPSDDocument->GetFileDocument();

    UE_LOG(LogTemp, Log, TEXT("导入的 PSD 文档: %s"), *MyPSDDocument->GetName());
    UE_LOG(LogTemp, Log, TEXT("尺寸: %d x %d"), FileDoc.GetHeader().Width, FileDoc.GetHeader().Height);
    UE_LOG(LogTemp, Log, TEXT("图层数量: %d"), FileDoc.GetLayers().Num());

    // 遍历图层
    for (const FPSDFileLayer& Layer : FileDoc.GetLayers())
    {
        UE_LOG(LogTemp, Log, TEXT("  图层: %s, 可见: %s"),
            *Layer.Name.ToString(),
            Layer.bIsVisible ? TEXT("是") : TEXT("否"));
        if (Layer.HasMask())
        {
            UE_LOG(LogTemp, Log, TEXT("    包含图层蒙版"));
        }
    }
}
```

### 进阶用法

编辑器模块中的工厂类展示了如何创建资产和材质。以下是对 `UPSDDocumentImportFactory` 核心导入逻辑的简化理解。

*基于 `PSDDocumentImportFactory.h` 和 `PSDDocumentImportFactory_Visitors.h` 的代码逻辑。*

```cpp
// 这是一个概念性的流程，实际实现由编辑器自动触发
bool MyCustomImportLogic(const FString& PSDFilePath, UObject* ParentPackage)
{
    // 1. 创建文档资产
    UPSDDocument* Document = NewObject<UPSDDocument>(ParentPackage, NAME_None, RF_Public | RF_Standalone);

    // 2. 使用工厂进行导入（包含解析和资产创建）
    UPSDDocumentImportFactory Factory;
    bool bInOutOperationCanceled = false;
    FFeedbackContext Context;
    UObject* Result = Factory.FactoryCreateFile(
        UPSDDocument::StaticClass(),
        ParentPackage,
        FPaths::GetBaseFilename(PSDFilePath),
        RF_NoFlags,
        PSDFilePath,
        nullptr,
        &Context,
        bInOutOperationCanceled
    );

    if (Result)
    {
        // 3. （可选）创建材质
        UPSDImporterLayeredMaterialFactory MaterialFactory;
        if (MaterialFactory.CanCreateMaterial(Document))
        {
            UMaterial* NewMaterial = MaterialFactory.CreateMaterial(Document);
            // ... 对材质进行进一步操作
        }
    }

    return Result != nullptr;
}
```

## Demo 示例

一个最小化的示例，展示如何在编辑器工具中通过 C++ 代码触发 PSD 资产的创建和材质生成。这通常需要放在一个 Editor 模块中。

**PSDImporterDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Editor/EditorEngine.h" // 或其它编辑器头文件

class FPSDImporterDemo
{
public:
    /** 通过代码导入一个 PSD 文件并为其生成材质 */
    static void ImportPSDAndCreateMaterial(const FString& PSDFilePath);
};
```

**PSDImporterDemo.cpp**
```cpp
#include "PSDImporterDemo.h"
#include "PSDImporterEditor/Factories/PSDDocumentImportFactory.h"
#include "PSDImporterEditor/Factories/PSDImporterLayeredMaterialFactory.h"
#include "PSDImporter/PSDDocument.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "Misc/FeedbackContext.h"

void FPSDImporterDemo::ImportPSDAndCreateMaterial(const FString& PSDFilePath)
{
    // 获取内容浏览器的当前路径作为父包
    FAssetToolsModule& AssetToolsModule = FModuleManager::LoadModuleChecked<FAssetToolsModule>("AssetTools");
    FString PackagePath = AssetToolsModule.Get().GetCurrentContentBrowserPath();

    // 1. 创建工厂并执行导入
    UPSDDocumentImportFactory ImportFactory;
    FScopedSlowTask SlowTask(2.0f, NSLOCTEXT("PSDDemo", "ImportingPSD", "导入 PSD 文件..."));
    SlowTask.MakeDialog();

    FFeedbackContext Context;
    bool bCanceled = false;
    UObject* ImportedObject = ImportFactory.FactoryCreateFile(
        UPSDDocument::StaticClass(),
        CreatePackage(*PackagePath / FPaths::GetBaseFilename(PSDFilePath)),
        *FPaths::GetBaseFilename(PSDFilePath),
        RF_Public | RF_Standalone,
        PSDFilePath,
        nullptr,
        &Context,
        bCanceled
    );

    UPSDDocument* Document = Cast<UPSDDocument>(ImportedObject);
    if (!Document)
    {
        UE_LOG(LogTemp, Error, TEXT("PSD 导入失败"));
        return;
    }

    SlowTask.EnterProgressFrame(1.0f);

    // 2. 为导入的文档创建材质
    UPSDImporterLayeredMaterialFactory MaterialFactory;
    if (MaterialFactory.CanCreateMaterial(Document))
    {
        UMaterial* Material = MaterialFactory.CreateMaterial(Document);
        if (Material)
        {
            // 保存新建的资产
            FAssetRegistryModule::AssetCreated(Material);
            Material->MarkPackageDirty();
            UE_LOG(LogTemp, Log, TEXT("成功创建材质: %s"), *Material->GetName());
        }
    }

    UE_LOG(LogTemp, Log, TEXT("PSD 文档导入完成: %s"), *Document->GetName());
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GeometryMask` | 用于在材质中创建和应用几何遮罩，支持 PSD 图层蒙版在引擎中的精确还原。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 UE_LOG 宏迁移到新的 UE_LOGF 格式。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了之前一次错误的全局替换操作。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 撤销了编号为 CL51314860 的提交。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 更新引擎委托的调用方式，修复了注册失败的问题。 |
| 2025-07-15 | `bafe5da2` | Silence incorrect V1051 warnings | 抑制了 PVS-Studio 生成的不正确 V1051 警告。 |

### 维护评价

PSD Importer 插件创建于约一年前，属于实验性插件。从 git 历史看，它在 **2026年2月** 和 **4月** 仍有活跃的提交，主要是进行代码维护、错误修复和编译器警告清理，表明它仍在被积极维护和关注。最近的更新集中在代码质量和稳定性上，而非新功能开发。

该插件解决了特定的美术工作流需求（PSD 到 UE），对于相关团队而言非常有用。然而，它仍处于 **实验性 (Experimental)** 状态，且默认未启用 (`Installed: false`)，这意味着其 API 和功能在未来版本中可能会发生变化，且官方不提供完全稳定性的保证。

**结论**：这是一个针对特定工作流、仍在维护中的实验性插件。如果你需要在项目中集成 PSD 文件，并且能接受其可能的不稳定性和未来变化，可以尝试使用。对于生产环境，建议充分测试并关注其后续更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter)
- [官方文档]()（暂无）