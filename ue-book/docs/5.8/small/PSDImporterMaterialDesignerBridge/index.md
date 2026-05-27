# PSD Importer Material Designer Bridge

> PSD Importer Material Designer Bridge

| 属性 | 值 |
|---|---|
| 中文名 | PSD导入材质设计器桥接 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器模块代码） |
| 模块 | `PSDImporterMaterialDesignerBridge` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-28 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporterMaterialDesignerBridge) | |

## 用途

本插件是一个**桥接插件**，用于连接 **PSD Importer** 和 **DynamicMaterial (Material Designer)** 这两个独立的工具。
它解决的核心问题是：将一个分层的 Photoshop (PSD) 文件直接转换为一个基于 DynamicMaterial 系统的、具有完整层结构和混合模式的材质实例。
这避免了设计师手动从 PSD 文件提取纹理并逐层创建动态材质的繁琐过程。该插件在内容浏览器中提供右键菜单集成，允许用户直接从导入的 `UPSDDocument` 资产生成材质和场景四边形，极大地优化了美术工作流。

## 使用场景

- 你是一名美术或技术美术，使用 Photoshop 设计 UI 或 2D 资产，并希望快速将分层的 PSD 文件导入 UE5 并自动生成可编辑的、支持层叠的动态材质。
- 你需要为每个 PSD 图层创建独立的四边形网格体（Quad Mesh），以便在 3D 场景中精确排列和显示 2D 图层。
- 你正在使用 DynamicMaterial 插件来创建高度可定制的材质，并希望利用现有的 PSD 文件作为素材来源。

## 蓝图用法

该插件主要提供编辑器集成功能（右键菜单）和 C++ 工厂类。源码分析未发现标记为 `UFUNCTION(BlueprintCallable)` 的公共蓝图接口函数。其核心操作通过编辑器右键菜单触发，具体流程由 C++ 工厂类在后台完成。

## C++ 用法

### 头文件引入

```cpp
// 使用插件提供的常量
#include "PSDImporterMDConstants.h"

// 使用材质/四边形工厂（通常在编辑器模块或工具中）
#include "Factories/PSDImporterMDMaterialFactory.h"
#include "Factories/PSDImporterMDQuadsFactory.h"
```

### 基本用法

**1. 使用常量（示例）**
这些常量定义了材质参数名称，可用于在材质图或代码中设置动态材质的属性。
（来源：`Public/PSDImporterMDConstants.h`）

```cpp
// 在设置动态材质参数时使用
UDynamicMaterialModel* MaterialModel = ...;
MaterialModel->SetTextureParameter(
    UE::PSDImporterMaterialDesignerBridge::TextureEmissiveParameterName,
    MyEmissiveTexture
);
```

**2. 使用工厂创建材质**
`UPSDImporterMDMaterialFactory` 负责根据 `UPSDDocument` 创建 `UDynamicMaterialInstance`。
（来源：`Private/Factories/PSDImporterMDMaterialFactory.h`）

```cpp
// 假设您已有一个有效的 UPSDDocument* Document
UPSDImporterMDMaterialFactory* MaterialFactory = NewObject<UPSDImporterMDMaterialFactory>();

if (MaterialFactory->CanCreateMaterial(Document))
{
    UDynamicMaterialInstance* NewMaterial = MaterialFactory->CreateMaterial(Document);
    if (NewMaterial)
    {
        // 材质创建成功，保存到内容浏览器或进行其他操作
        UE_LOG(LogTemp, Log, TEXT("Dynamic Material created: %s"), *NewMaterial->GetName());
    }
}
```

### 进阶用法

**创建带四边形的场景对象**
`UPSDImporterMDQuadsFactory` 负责在场景中生成 `APSDQuadActor`，并为其每个图层创建 `APSDQuadMeshActor`，同时将材质应用到网格体上。
（来源：`Private/Factories/PSDImporterMDQuadsFactory.h`）

```cpp
// 在拥有 World 上下文的编辑器工具或命令中
UWorld* World = GEditor->GetEditorWorldContext().World();
if (World && Document)
{
    UPSDImporterMDQuadsFactory* QuadsFactory = NewObject<UPSDImporterMDQuadsFactory>();
    
    // 1. 创建根 Quad Actor
    APSDQuadActor* QuadActor = QuadsFactory->CreateQuadActor(*World, Document);
    
    if (QuadActor)
    {
        // 2. 为 Quad Actor 创建各个图层的网格体并应用材质
        // EPSDImporterMaterialDesignerType 枚举应来自依赖的 PSDImporter 或本插件，需查阅头文件确认具体定义
        QuadsFactory->CreateQuads(*QuadActor, /* InType */);
        
        UE_LOG(LogTemp, Log, TEXT("PSD Quad Actor and meshes created in world."));
    }
}
```

## Demo 示例

以下是一个最小化示例，展示如何使用工厂类创建一个动态材质实例。此示例假设在编辑器工具或命令中执行。

**PSDImporterMDBridgeDemo.h**
```cpp
#pragma once

class UPSDDocument;

class FPSDImporterMDBridgeDemo
{
public:
    static void CreateDynamicMaterialFromPSD(UPSDDocument* InDocument);
};
```

**PSDImporterMDBridgeDemo.cpp**
```cpp
#include "PSDImporterMDBridgeDemo.h"
#include "Factories/PSDImporterMDMaterialFactory.h"
#include "PSDImporterMDConstants.h"
#include "DynamicMaterial/DynamicMaterialInstance.h"
#include "PSDImporter/PSDDocument.h"

void FPSDImporterMDBridgeDemo::CreateDynamicMaterialFromPSD(UPSDDocument* InDocument)
{
    if (!InDocument)
    {
        UE_LOG(LogTemp, Warning, TEXT("Invalid PSD Document."));
        return;
    }

    UPSDImporterMDMaterialFactory* Factory = NewObject<UPSDImporterMDMaterialFactory>();
    if (!Factory->CanCreateMaterial(InDocument))
    {
        UE_LOG(LogTemp, Warning, TEXT("Cannot create material from this PSD document."));
        return;
    }

    UDynamicMaterialInstance* MaterialInstance = Factory->CreateMaterial(InDocument);
    if (MaterialInstance)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully created Dynamic Material '%s' from PSD document '%s'."),
            *MaterialInstance->GetName(),
            *InDocument->GetName());

        // 在此处可以进一步操作 MaterialInstance，例如：
        // 1. 将其保存到内容浏览器的特定路径
        // 2. 应用到某个 StaticMeshComponent 上
        // 3. 设置额外的材质参数
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create Dynamic Material from PSD document."));
    }
}
```

## 模块依赖

要使用此插件的功能，您的模块需要依赖以下插件（或对应模块）：
- `DynamicMaterial`：提供 `UDynamicMaterialInstance`, `UDynamicMaterialModelEditorOnlyData`, `UDMMaterialSlot` 等核心类。
- `PSDImporter`：提供 `UPSDDocument`, `FPSDFileLayer`, `EPSDBlendMode` 等核心类。

您无需直接依赖此桥接插件模块，因为其工厂类（`UPSDImporterMDMaterialFactory`, `UPSDImporterMDQuadsFactory`）旨在被编辑器工具或内容浏览器扩展代码调用。您需要确保这两个插件在您的项目中已启用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-04-28 | `9216b924` | Horde issue 881859 | 构建系统问题修复（Horde） |
| 2025-04-28 | `fed4030e` | PSD Importer: Renamed and moved to Experimental | 从原位置重命名并移至实验性插件目录 |

### 维护评价

- **创建时间**：2025年4月，非常新的插件。
- **更新频率**：仅在创建当天（2025-04-28）有两次提交。自创建以来无任何功能更新或 bug 修复记录。
- **活跃程度**：**极不活跃**。缺乏后续维护和迭代。
- **已知问题/限制**：标记为实验性 (`IsExperimentalVersion: true`)，且仅支持 Win64 平台。功能可能不完整或不稳定。
- **使用建议**：**谨慎使用**。该插件目前仅作为实验性功能存在，没有活跃维护迹象。如果您是 DynamicMaterial 和 PSD Importer 的深度用户，并且迫切需要此桥接功能，可以尝试使用，但需自行承担风险。对于生产环境，建议等待其成熟或自行实现类似功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporterMaterialDesignerBridge)
- [官方文档]() (无)
- [测试用例]() (在提供的文件分析中未发现测试文件，可能位于 `Engine/Tests/` 或未包含)