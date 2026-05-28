# PSD Importer

> 

| 属性 | 值 |
|---|---|
| 中文名 | PSD导入器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `PSDImporterCore` (Runtime), `PSDImporter` (Runtime), `PSDImporterEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-28 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter) | |

## 用途

PSD Importer 插件提供了一套完整的工具链，用于将 Adobe Photoshop 的 PSD 文件直接导入 Unreal Engine 5。其核心功能是解析 PSD 文件的图层结构，并将其转换为引擎可用的资产（如材质、纹理和 UI 控件），特别适用于 UI 动画工作流。该插件解决了 UI 设计师需要在 Photoshop 中制作复杂图层效果，然后手动、繁琐地在 UE 中重建的问题，实现了设计稿到可交互 UI 的自动化或半自动化转换。

## 使用场景

-   你是一名 UI 设计师或美术，使用 Adobe Photoshop 制作了一套游戏 UI 设计稿（包含多个图层、图层样式和混合模式）。
-   你需要将这些设计稿快速导入到 UE5 的 UMG UI 编辑器中进行编辑和动画绑定，而不是手动创建每个材质和控件。
-   你正在为游戏 UI 制作复杂的交互动画，希望直接利用 PSD 文件中的图层结构来驱动动画（例如，使用 `GeometryMask` 组件来实现基于图层的遮罩动画）。

## 蓝图用法

此插件主要提供编辑器扩展功能，用于在 Content Browser 中导入和预览 PSD 文件。其核心蓝图节点通常在编辑器工具蓝图或自定义资产处理逻辑中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ImportTexture` | 从指定的 PSD 图层数据中导入并创建 UTexture2D 资产 | `UPsdTextureFactory` |
| `ImportMaterial` | 根据 PSD 图层信息创建 UMaterial 资产，包含正确的纹理引用和混合模式 | `UPsdMaterialFactory` |
| `CreateUIPanel` | (推测) 基于导入的图层结构，在 UMG 中生成对应的 Widget 树或启动 UI 编辑器流程 | `UPsdUIFactory` |

### 使用示例（蓝图描述）

1.  **在编辑器工具蓝图中**，你可以通过“PSD Importer”分类下的节点，调用“Import PSD”功能，传入一个 `UObject` 路径（例如 `/Game/UI/Design`），插件会解析该目录下的 PSD 文件。
2.  解析后，插件会为每个图层生成对应的纹理资产，并可选地为包含图层样式的图层生成材质资产。
3.  最终，在 Content Browser 的指定路径下，你会看到一个包含所有导入资源的文件夹结构，这些资源可以直接拖拽到 UMG 画布上使用。

## C++ 用法

以下用法基于插件模块功能推测，旨在展示典型的集成方式。

### 头文件引入

```cpp
// 使用核心解析库
#include "PsdSDK.h"

// 使用导入器工厂
#include "PsdTextureFactory.h"
#include "PsdMaterialFactory.h"
```

### 基本用法

```cpp
// 示例：通过工厂对象导入单个 PSD 文件
// 来源：基于 UPsdFactory 基类的用法模式
void ImportPSDFile(const FString& PSDFilePath, const FString& OutputPath)
{
    // 1. 创建纹理导入工厂
    UPsdTextureFactory* TextureFactory = NewObject<UPsdTextureFactory>();
    TextureFactory->SetOutputDirectory(OutputPath);

    // 2. 解析 PSD 文件 (核心 SDK 功能)
    // 假设有一个 FPsdDocument 类型的解析结果
    FPsdDocument* Document = FPsdSDK::Parse(PSDFilePath);
    if (!Document) return;

    // 3. 遍历图层并导入纹理
    for (const FPsdLayer& Layer : Document->GetLayers())
    {
        if (Layer.HasPixelData())
        {
            UTexture2D* Texture = TextureFactory->ImportTextureFromLayer(Layer);
            if (Texture)
            {
                // 保存资产到磁盘
                TextureFactory->SaveAsset(Texture, Layer.GetName());
            }
        }
    }

    // 4. 清理
    delete Document;
}
```

### 进阶用法

```cpp
// 示例：导入完整的 PSD 并创建材质
void ImportPSDWithMaterials(const FString& PSDFilePath, const FString& OutputPath)
{
    UPsdTextureFactory* TextureFactory = NewObject<UPsdTextureFactory>();
    UPsdMaterialFactory* MaterialFactory = NewObject<UPsdMaterialFactory>();
    TextureFactory->SetOutputDirectory(OutputPath + TEXT("/Textures"));
    MaterialFactory->SetOutputDirectory(OutputPath + TEXT("/Materials"));

    FPsdDocument* Document = FPsdSDK::Parse(PSDFilePath);
    if (!Document) return;

    // 导入所有图层的纹理
    TMap<FString, UTexture2D*> TextureMap;
    for (const FPsdLayer& Layer : Document->GetLayers())
    {
        UTexture2D* Texture = TextureFactory->ImportTextureFromLayer(Layer);
        if (Texture)
        {
            TextureMap.Add(Layer.GetName(), Texture);
            TextureFactory->SaveAsset(Texture, Layer.GetName());
        }
    }

    // 为需要样式的图层创建材质 (例如，带投影、发光的图层)
    for (const FPsdLayer& Layer : Document->GetLayers())
    {
        if (Layer.HasLayerStyles())
        {
            UMaterial* Material = MaterialFactory->CreateMaterialFromLayer(Layer, TextureMap);
            if (Material)
            {
                MaterialFactory->SaveAsset(Material, Layer.GetName() + TEXT("_Mat"));
            }
        }
    }

    delete Document;
}
```

## Demo 示例

一个触发 PSD 导入并创建基础资产的编辑器工具。

### MyPSDImporterTool.h
```cpp
#pragma once
#include "EditorUtilityWidget.h"
#include "MyPSDImporterTool.generated.h"

UCLASS()
class UMyPSDImporterTool : public UEditorUtilityWidget
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "PSD Tool")
    void ImportPSDToProject(const FString& PSDFilePath, const FString& DestinationFolder);

private:
    void ProcessPSDDocument(const FString& PSDFilePath, const FString& OutputFolder);
};
```

### MyPSDImporterTool.cpp
```cpp
#include "MyPSDImporterTool.h"
#include "PsdSDK.h"
#include "PsdTextureFactory.h"
#include "AssetRegistry/AssetRegistryModule.h"

void UMyPSDImporterTool::ImportPSDToProject(const FString& PSDFilePath, const FString& DestinationFolder)
{
    // 确保目标文件夹存在
    IFileManager::Get().MakeDirectory(*DestinationFolder, true);

    // 在游戏线程执行（工厂对象需要）
    AsyncTask(ENamedThreads::GameThread, [this, PSDFilePath, DestinationFolder]()
    {
        ProcessPSDDocument(PSDFilePath, DestinationFolder);
    });
}

void UMyPSDImporterTool::ProcessPSDDocument(const FString& PSDFilePath, const FString& OutputFolder)
{
    // 1. 解析 PSD
    FPsdDocument* Document = FPsdSDK::Parse(PSDFilePath);
    if (!Document)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to parse PSD file: %s"), *PSDFilePath);
        return;
    }

    // 2. 创建导入器
    UPsdTextureFactory* Factory = NewObject<UPsdTextureFactory>();
    Factory->SetOutputDirectory(OutputFolder);

    // 3. 导入每个图层
    int32 ImportedCount = 0;
    for (const FPsdLayer& Layer : Document->GetLayers())
    {
        if (Layer.HasPixelData())
        {
            UTexture2D* Texture = Factory->ImportTextureFromLayer(Layer);
            if (Texture)
            {
                // 为资产生成唯一的包名和对象名
                FString AssetName = FPaths::GetBaseFilename(Layer.GetName());
                AssetName = UPackage::MakeUniqueObjectName(FName(*OutputFolder), UTexture2D::StaticClass(), *AssetName).ToString();
                
                UPackage* Package = CreatePackage(*FPaths::Combine(OutputFolder, AssetName));
                Package->FullyLoad();

                Texture->Rename(*AssetName, Package);
                FAssetRegistryModule::AssetCreated(Texture);

                ImportedCount++;
            }
        }
    }

    UE_LOG(LogTemp, Log, TEXT("Imported %d textures from PSD."), ImportedCount);

    // 4. 清理与保存
    delete Document;
    Factory->ConditionalBeginDestroy();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PsdSDK` | 底层的 Photoshop 文件格式解析库（第三方） |
| `GeometryMask` | 提供基于几何形状（如图层轮廓）的 UI 遮罩组件，插件可能依赖其创建基于图层的动画 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 更新日志系统宏至新版，涉及格式修复。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复一次错误的全局替换后，重新提交变更。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回滚（Backout）了一次特定的代码提交。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复了因引擎代理（Delegate）注册问题导致的功能缺失。 |
| 2025-07-15 | `bafe5da2` | Silence incorrect V1051 warnings | 抑制了编译器发出的不正确的V1051警告。 |

### 维护评价

- **状态**: **活跃维护**。最近一次更新在 2026 年 4 月，距离创建时间（2025 年 4 月）不足一年，且近期有多个提交。
- **性质**: 该插件目前处于 **实验性**（`IsExperimentalVersion: true`）阶段，意味着其 API 和功能在未来版本中可能发生重大变化。
- **风险与建议**: 作为实验性插件，**不建议在需要长期稳定性的正式项目中深度依赖**。非常适合用于原型开发、内部工具或技术预研。使用时需要关注 Epic 的更新日志，并准备好应对接口变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter)
- [官方文档]()（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/PSDImporterTests/)