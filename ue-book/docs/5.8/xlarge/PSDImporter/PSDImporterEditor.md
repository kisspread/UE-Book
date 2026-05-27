# PSD Importer

> 将 Adobe Photoshop (.psd) 文件导入到 Unreal Engine 5 中，支持图层、蒙版和材质生成。

| 属性 | 值 |
|---|---|
| 中文名 | PSD 导入器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质函数） |
| 模块 | `PSDImporter` (Runtime), `PSDImporterCore` (Runtime), `PSDImporterEditor` (Editor) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2025-04-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter) | |

## 用途

该插件不仅用于简单的图像导入，而是提供了一个从 Adobe Photoshop 设计稿到 UE5 可交互资产的完整工作流。它能够：

1.  **解析 PSD 文件结构**：读取包含多个图层、图层组、调整图层和图层蒙版的复杂 PSD 文件。
2.  **保留图层信息**：将每个图层和蒙版分别导入为独立的 `UTexture2D` 资产，并记录它们的可见性、不透明度、位置等属性。
3.  **生成材质资产**：根据导入的图层结构，自动创建分层材质（`UMaterial`），并正确连接纹理和参数，以便在运行时控制图层显示。
4.  **创建 3D 场景表示**：为导入的 PSD 文档创建 `APSDQuadActor`，其中包含代表每个图层的四边形网格体（`APSDQuadMeshActor`），使其能够作为 3D 对象在场景中显示和交互。
5.  **支持重新导入**：当 PSD 源文件修改后，可以重新导入更新内容，同时尝试保留已创建资产之间的关联。

**存在意义**：简化了将 2D 设计资源（如 UI 界面、游戏资产、概念图）集成到 3D UE5 项目中的过程，让设计师的工作成果能更直接、更结构化地为程序所用。

## 使用场景

-   **游戏 UI 快速原型与实现**：UI 设计师在 Photoshop 中完成多层 UI 设计后，可直接导入 UE5，自动生成带有图层控制的材质和扁平化的 3D UI 元素，便于程序在运行时动态切换 UI 状态。
-   **动态背景与场景元素制作**：将包含不同深度信息的背景 PSD 文件导入，自动转化为按图层排列的四边形网格，轻松实现视差滚动背景或可拆分的场景装饰物。
-   **角色皮肤或材质变体制作**：将角色的不同纹理细节（如伤疤、纹身、装备样式）放在不同的 PSD 图层中，导入后生成一个参数化的材质，方便在游戏中动态切换外观。
-   **设计资产批量处理与维护**：对于需要频繁更新的 2D 资产，利用重新导入功能保持 UE5 资产与源 PSD 文件同步。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create PSD Material` | 根据导入的 PSD 文档资产，创建一个分层材质。 | `UPSDImporterLayeredMaterialFactory` |
| `Create PSD Quads` | 根据 PSD 文档资产，在场景中创建一个包含所有图层四边形的 `APSDQuadActor`。 | `UPSDQuadsFactory` |
| `Resize Layers To Document` | 导入设置：是否将图层纹理裁剪/缩放到文档尺寸。 | `UPSDImporterEditorSettings` |
| `Import Invisible Layers` | 导入设置：是否导入 PSD 中不可见的图层。 | `UPSDImporterEditorSettings` |

### 使用示例（蓝图描述）

1.  **内容浏览器集成**：
    -   在内容浏览器中右键点击导入的 `PSDDocument` 资产。
    -   在扩展菜单中，可以看到 **“Create PSD Material”** 和 **“Create PSD Quads”** 选项。
    -   点击这些选项，插件会自动在当前文件夹下生成对应的材质和四边形 Actor 资产。

2.  **运行时图层控制（蓝图逻辑）**：
    -   假设你有一个由 PSD 导入生成的材质实例 `MI_CharacterOutfit`。
    -   在材质中，图层是否显示由名为 `Layer_Visible_0`, `Layer_Visible_1` 等的静态开关参数控制。
    -   在蓝图中，你可以使用 **Set Scalar Parameter Value** 节点，将这些参数的值设为 0 或 1，来在运行时切换不同图层的可见性，从而改变角色外观。

3.  **自定义导入流程（蓝图逻辑）**：
    -   你可以通过 **Set Editor Settings** 节点，在导入前修改 `bResizeLayersToDocument` 或 `bImportInvisibleLayers` 的值，然后通过 **Reimport Asset** 节点重新导入 PSD 文件，以应用新的设置。

## C++ 用法

### 头文件引入

```cpp
// 核心运行时数据结构
#include "PSDImporterCore/PSDImporterTypes.h"

// 文档资产类
#include "PSDImporterCore/PSDDocument.h"

// 工厂类（用于材质和四边形创建）
#include "PSDImporterEditor/Factories/PSDImporterLayeredMaterialFactory.h"
#include "PSDImporterEditor/Factories/PSDQuadsFactory.h"

// 材质创建工具库
#include "PSDImporterEditor/Utils/PSDImporterMaterialLibrary.h"
```

### 基本用法

**示例：以编程方式为导入的 PSD 文档创建材质**
（代码逻辑参考 `PSDImporterLayeredMaterialFactory.h`）

```cpp
#include "PSDImporterEditor/Factories/PSDImporterLayeredMaterialFactory.h"
#include "PSDImporterCore/PSDDocument.h"

void CreateMaterialForPSDAsset(UPSDDocument* ImportedPSDAsset)
{
    if (!ImportedPSDAsset) return;

    // 1. 实例化工厂
    UPSDImporterLayeredMaterialFactory* MaterialFactory = NewObject<UPSDImporterLayeredMaterialFactory>();

    // 2. 检查文档是否满足材质创建条件（例如，有可见的图层）
    if (MaterialFactory->CanCreateMaterial(ImportedPSDAsset))
    {
        // 3. 创建材质，它将自动生成并保存在与 PSD 文档相同的路径下
        UMaterial* CreatedMaterial = MaterialFactory->CreateMaterial(ImportedPSDAsset);
        if (CreatedMaterial)
        {
            UE_LOG(LogTemp, Log, TEXT("Material '%s' created from PSD Document."), *CreatedMaterial->GetName());
        }
    }
}
```

### 进阶用法

**示例：在关卡中动态生成 PSD 四边形 Actor**
（代码逻辑参考 `PSDQuadsFactory.h` 和 `PSDImporterMaterialLibrary.h`）

```cpp
#include "PSDImporterEditor/Factories/PSDQuadsFactory.h"
#include "PSDImporterCore/PSDDocument.h"
#include "Actors/PSDQuadActor.h"

void SpawnPSDQuadActorInWorld(UWorld* World, UPSDDocument* PSDAsset, const FVector& SpawnLocation)
{
    if (!World || !PSDAsset) return;

    // 1. 实例化四边形工厂
    UPSDQuadsFactory* QuadFactory = NewObject<UPSDQuadsFactory>();

    // 2. 在指定世界中创建四边形根 Actor
    APSDQuadActor* QuadRootActor = QuadFactory->CreateQuadActor(*World, *PSDAsset);
    if (QuadRootActor)
    {
        // 3. 为该 Actor 创建所有图层子四边形
        QuadFactory->CreateQuads(*QuadRootActor);

        // 4. 设置位置
        QuadRootActor->SetActorLocation(SpawnLocation);
    }
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何创建一个执行“在编辑器中为选中PSD资产创建材质”命令的自定义编辑器按钮。

**PSDImporterDemoButton.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "EditorUtilityWidget.h"
#include "PSDImporterDemoButton.generated.h"

class UPSDDocument;

UCLASS()
class UPSDImporterDemoButton : public UEditorUtilityWidget
{
    GENERATED_BODY()

public:
    // 蓝图可调用函数，作为按钮的绑定事件
    UFUNCTION(BlueprintCallable, Category = "PSD Importer Demo")
    void CreateMaterialFromSelectedPSDAsset();

private:
    // 获取内容浏览器中选中的第一个PSD文档资产
    UPSDDocument* GetSelectedPSDDocument() const;
};
```

**PSDImporterDemoButton.cpp**
```cpp
#include "PSDImporterDemoButton.h"
#include "PSDImporterEditor/Factories/PSDImporterLayeredMaterialFactory.h"
#include "PSDImporterCore/PSDDocument.h"
#include "Editor.h"
#include "AssetRegistry/AssetData.h"

void UPSDImporterDemoButton::CreateMaterialFromSelectedPSDAsset()
{
    UPSDDocument* SelectedDoc = GetSelectedPSDDocument();
    if (!SelectedDoc)
    {
        UE_LOG(LogTemp, Warning, TEXT("No PSD Document selected in the Content Browser."));
        return;
    }

    // 使用插件提供的工厂创建材质
    UPSDImporterLayeredMaterialFactory* Factory = NewObject<UPSDImporterLayeredMaterialFactory>();
    if (Factory->CanCreateMaterial(SelectedDoc))
    {
        UMaterial* NewMat = Factory->CreateMaterial(SelectedDoc);
        if (NewMat)
        {
            // 成功，可以在编辑器中通知用户
            FText Msg = FText::Format(NSLOCTEXT("PSDDemo", "CreateMatSuccess", "Successfully created material: {0}"),
                FText::FromString(NewMat->GetName()));
            FNotificationInfo Info(Msg);
            Info.ExpireDuration = 5.0f;
            FSlateNotificationManager::Get().AddNotification(Info);
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("The selected PSD Document cannot be used to create a material."));
    }
}

UPSDDocument* UPSDImporterDemoButton::GetSelectedPSDDocument() const
{
    TArray<FAssetData> SelectedAssets;
    GEditor->GetContentBrowserSelections(SelectedAssets);

    for (const FAssetData& Asset : SelectedAssets)
    {
        if (Asset.GetClass() == UPSDDocument::StaticClass())
        {
            return Cast<UPSDDocument>(Asset.GetAsset());
        }
    }
    return nullptr;
}
```

## 模块依赖

该插件依赖于以下非标准模块：

| 模块 | 用途 |
|---|---|
| `GeometryMask` | 提供几何遮罩材质功能，用于在生成的图层材质中正确应用图层蒙版。 |
| `Slate`, `SlateCore` | 用于构建编辑器内的属性自定义化界面和内容浏览器扩展菜单。 |
| `EditorWidgets` | 用于创建编辑器工具和资产定义。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏 `UE_LOG` 迁移至更新的 `UE_LOGF` 宏，属于代码现代化更新。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修正一次错误的查找替换操作后的第二次提交，修复了可能引入的编译问题。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了之前的提交 `CL51314860`，表明一次代码合并遇到了问题。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复引擎初始化顺序问题，确保插件在正确的时机注册，防止功能缺失。 |
| 2025-07-15 | `bafe5da2` | Silence incorrect V1051 warnings | 抑制静态分析工具发出的不准确的 V1051 警告，提升编译体验。 |

### 维护评价

-   **创建时间**：2025年4月创建，非常年轻。
-   **近期活动**：最近一次实质性提交在 2026年4月，主要为技术性适配（日志宏迁移）。之前有重要的初始化修复。虽然更新频率不高，但近期有维护迹象。
-   **状态**：该插件标记为 `IsExperimentalVersion: true`，且默认未启用（`Installed: false`）。这明确表明它是一个**实验性功能**，可能还不稳定或API未最终确定。
-   **推荐**：**谨慎推荐**。适用于愿意尝试新工作流并接受其局限性的项目。不建议用于即将上线的生产项目核心功能中。可作为提升美术与程序协作效率的工具进行评估和试用。请密切关注后续版本更新和可能的破坏性变更。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter)
-   [官方文档]() (暂无)
-   [测试用例]() (源码中未发现专门的测试文件目录)