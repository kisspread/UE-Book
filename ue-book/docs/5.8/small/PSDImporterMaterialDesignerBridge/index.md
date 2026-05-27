# PSD Importer Material Designer Bridge

> A bridge plugin between the PSD Importer and the Dynamic Material plugin.

| 属性 | 值 |
|---|---|
| 中文名 | PSD导入器-材质设计器桥接器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PSDImporterMaterialDesignerBridge` (Editor) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2025-04-28 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporterMaterialDesignerBridge) | |

## 用途

此插件是连接 **PSD Importer** 和 **Dynamic Material** 两个插件的桥梁。它解决了在游戏开发中，美术人员导入 Photoshop (PSD) 文件后，需要手动为导入的图层纹理创建复杂材质和场景对象的痛点。此插件自动化了这一过程，能够根据导入的PSD文档，一键生成对应的 `DynamicMaterial` 实例以及用于在场景中展示该材质的 `Quad` 演员。

**核心工作流程**：`PSDImporter` 导入PSD文件 → 此插件介入 → 自动生成 `DynamicMaterial` 资产 + `Quad` 演员。

## 使用场景

- 美术人员在Photoshop中设计UI或场景元素，导出为分层的PSD文件。
- 在UE5编辑器中，使用 `PSDImporter` 插件导入该PSD文件。
- 希望将导入的各个图层快速生成带有正确混合模式、裁剪和遮罩的动态材质，并在场景中预览。

## 蓝图用法

此插件的功能主要通过编辑器扩展（右键菜单）和工厂类内部实现，没有暴露大量直接的蓝图节点。主要交互方式是在内容浏览器中右键PSD导入器资产进行操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CanCreateMaterial` | 检查给定的PSD文档是否可以用来创建材质 | `UPSDImporterMDMaterialFactory` |
| `CreateMaterial` | 为一个PSD文档创建 `UDynamicMaterialInstance` 资产 | `UPSDImporterMDMaterialFactory` |
| `CreateQuadActor` | 为一个PSD文档创建用于展示材质的 `APSDQuadActor` 演员 | `UPSDImporterMDQuadsFactory` |
| `CreateQuads` | 在指定的 `QuadActor` 中为所有图层创建 `Quad` | `UPSDImporterMDQuadsFactory` |

### 使用示例（蓝图描述）

此插件的典型用法并非通过蓝图节点连接，而是通过**内容浏览器集成**：

1.  使用 `PSDImporter` 插件导入一个 `.psd` 文件，生成 `UPSDDocument` 资产。
2.  在**内容浏览器**中，右键单击该 `UPSDDocument` 资产。
3.  在右键菜单中，会出现由本插件注入的选项，例如“创建动态材质”或“创建四边形（Material Designer）”。
4.  点击相应菜单项，插件将自动在后台调用 `UPSDImporterMDMaterialFactory` 或 `UPSDImporterMDQuadsFactory` 来生成资产。

## C++ 用法

### 头文件引入

```cpp
#include "PSDImporterMDMaterialFactory.h"
#include "PSDImporterMDQuadsFactory.h"
#include "PSDImporterMDConstants.h"
```

### 基本用法

**1. 为PSD文档创建动态材质**

假设你已经有一个有效的 `UPSDDocument*` 对象（通常由 `PSDImporter` 插件提供）。

```cpp
// 来源: Private/Factories/PSDImporterMDMaterialFactory.h 以及对 CreateMaterial 的推断
#include "Factories/PSDImporterMDMaterialFactory.h"
#include "PSDDocument.h"

void CreateMaterialForPSD(UPSDDocument* InDocument)
{
    // 创建工厂实例
    UPSDImporterMDMaterialFactory* MaterialFactory = NewObject<UPSDImporterMDMaterialFactory>();

    // 检查是否可创建
    if (MaterialFactory->CanCreateMaterial(InDocument))
    {
        // 创建材质资产 (具体创建过程在工厂内部处理)
        UDynamicMaterialInstance* NewMaterial = MaterialFactory->CreateMaterial(InDocument);
        if (NewMaterial)
        {
            UE_LOG(LogPSDImporterMaterialDesignerBridge, Log, TEXT("Successfully created Dynamic Material: %s"), *NewMaterial->GetName());
        }
    }
}
```

**2. 为PSD文档创建Quad演员**

```cpp
// 来源: Private/Factories/PSDImporterMDQuadsFactory.h
#include "Factories/PSDImporterMDQuadsFactory.h"
#include "PSDQuadActor.h"

void CreateQuadActorForPSD(UWorld* InWorld, UPSDDocument* InDocument)
{
    UPSDImporterMDQuadsFactory* QuadsFactory = NewObject<UPSDImporterMDQuadsFactory>();

    // 创建 QuadActor（演员）
    APSDQuadActor* QuadActor = QuadsFactory->CreateQuadActor(*InWorld, InDocument);
    if (QuadActor)
    {
        // 为所有图层创建子 Quad (例如使用 Material Designer 类型)
        QuadsFactory->CreateQuads(*QuadActor, EPSDImporterMaterialDesignerType::MaterialDesigner);
        UE_LOG(LogPSDImporterMaterialDesignerBridge, Log, TEXT("Created QuadActor with quads for document: %s"), *InDocument->GetName());
    }
}
```

### 进阶用法

**使用常量为材质参数命名**

当你需要手动操作由本插件生成的材质参数时，可以使用预定义的常量名。

```cpp
// 来源: Public/PSDImporterMDConstants.h
#include "PSDImporterMDConstants.h"

void SetMaterialParameters(UMaterialInstanceDynamic* InMID)
{
    if (InMID)
    {
        // 设置发光纹理 (由工厂自动设置)
        // InMID->SetTextureParameterValue(UE::PSDImporterMaterialDesignerBridge::TextureEmissiveParameterName, SomeTexture);

        // 设置裁剪区域 (这些参数在创建材质时由工厂根据PSD图层信息设置)
        // InMID->SetScalarParameterValue(UE::PSDImporterMaterialDesignerBridge::OpacityCropLeft, 0.1f);
        // InMID->SetScalarParameterValue(UE::PSDImporterMaterialDesignerBridge::OpacityCropRight, 0.9f);
        UE_LOG(LogTemp, Log, TEXT("Material uses parameter: %s"), UE::PSDImporterMaterialDesignerBridge::TextureEmissiveParameterName);
    }
}
```

## Demo 示例

```cpp
// PSDImporterMDBridgeDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "PSDImporterMDBridgeDemo.generated.h"

class UPSDDocument;
class UDynamicMaterialInstance;
class APSDQuadActor;

UCLASS()
class APSDImporterMDBridgeDemoActor : public AActor
{
	GENERATED_BODY()

public:
	// 在编辑器中设置一个导入的PSD资产
	UPROPERTY(EditAnywhere, Category = "PSD Bridge Demo")
	TObjectPtr<UPSDDocument> Document;

	// 生成的材质资产（只读，演示用）
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "PSD Bridge Demo")
	TObjectPtr<UDynamicMaterialInstance> GeneratedMaterial;

	// 生成的Quad演员（只读，演示用）
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "PSD Bridge Demo")
	TObjectPtr<APSDQuadActor> GeneratedQuadActor;

	UFUNCTION(CallInEditor, Category = "PSD Bridge Demo")
	void DemoCreateMaterial();

	UFUNCTION(CallInEditor, Category = "PSD Bridge Demo")
	void DemoCreateQuadActor();
};
```

```cpp
// PSDImporterMDBridgeDemo.cpp
#include "PSDImporterMDBridgeDemo.h"
#include "Factories/PSDImporterMDMaterialFactory.h"
#include "Factories/PSDImporterMDQuadsFactory.h"
#include "PSDImporterMDBridgeLog.h"

void APSDImporterMDBridgeDemoActor::DemoCreateMaterial()
{
	if (!Document)
	{
		UE_LOG(LogPSDImporterMaterialDesignerBridge, Warning, TEXT("No PSD Document assigned!"));
		return;
	}

	UPSDImporterMDMaterialFactory* Factory = NewObject<UPSDImporterMDMaterialFactory>();
	if (Factory->CanCreateMaterial(Document))
	{
		GeneratedMaterial = Factory->CreateMaterial(Document);
		UE_LOG(LogPSDImporterMaterialDesignerBridge, Log, TEXT("Demo: Material created successfully."));
	}
}

void APSDImporterMDBridgeDemoActor::DemoCreateQuadActor()
{
	if (!Document || !GetWorld())
	{
		UE_LOG(LogPSDImporterMaterialDesignerBridge, Warning, TEXT("No PSD Document or World available!"));
		return;
	}

	UPSDImporterMDQuadsFactory* Factory = NewObject<UPSDImporterMDQuadsFactory>();
	GeneratedQuadActor = Factory->CreateQuadActor(*GetWorld(), Document);
	if (GeneratedQuadActor)
	{
		Factory->CreateQuads(*GeneratedQuadActor, EPSDImporterMaterialDesignerType::MaterialDesigner);
		UE_LOG(LogPSDImporterMaterialDesignerBridge, Log, TEXT("Demo: Quad Actor created successfully."));
	}
}
```

## 模块依赖

此插件作为**编辑器插件**，其使用者（也是编辑器环境）需要依赖以下核心模块：

| 模块 | 用途 |
|---|---|
| `DynamicMaterial` | 核心依赖，用于创建和操作 `UDynamicMaterialInstance` 和 `UDMMaterialSlot` 等材质设计器资产。 |
| `PSDImporter` | 核心依赖，提供 `UPSDDocument`、`FPSDFileLayer` 等导入数据结构。 |
| `LevelEditor` | 用于在编辑器中集成右键菜单（内容浏览器扩展）。 |
| `ContentBrowser` | 用于在内容浏览器资产选择菜单中添加条目。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-04-28 | `9216b924` | Horde issue 881859 | 可能是一次与构建系统或自动化测试相关的修复。 |
| 2025-04-28 | `fed4030e` | PSD Importer: Renamed and moved to Experimental | 插件创建，从其他位置移动并重命名为当前实验性路径。 |

### 维护评价

此插件**非常新**，创建于2025年4月，并且**仅在创建当天有提交记录**。它被明确标记为**实验性**（`IsExperimentalVersion: true`）且**默认未启用**（`Installed: false`）。

**评价**：
- **优点**：解决了一个具体的工作流问题（PSD到动态材质的自动化），设计清晰。
- **风险**：处于实验阶段，API和功能可能不稳定，且目前没有活跃的后续提交，**存在被移除或大幅修改的风险**。
- **建议**：可以用于探索和验证工作流，但**不建议在生产项目中作为核心功能依赖**。需密切关注后续更新动态。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporterMaterialDesignerBridge)
- [官方文档](）（无）