# PSD Importer Material Designer Bridge

> 

| 属性 | 值 |
|---|---|
| 中文名 | PSD材质桥接器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PSDImporterMaterialDesignerBridge` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-28 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporterMaterialDesignerBridge) | |

## 用途

本插件是一个桥接器，用于连接 **PSDImporter**（PSD文件导入插件）和 **DynamicMaterial**（动态材质插件）。

其核心功能是：当用户通过 `PSDImporter` 插件导入一个 Adobe Photoshop (.psd) 文件后，本插件可以**自动根据该文件的图层结构，使用 `DynamicMaterial` 插件创建对应的材质和用于显示的“四方体”（Quad）模型资产**。

它解决了在游戏UI或2D内容制作中，将Photoshop设计稿快速转换为引擎内可编辑、可动态调整的材质资产这一繁琐的手动流程。通过自动解析PSD图层（特别是裁剪、混合模式和透明度蒙版），生成带有正确参数化材质（如偏移、平铺、裁剪区域）的`DynamicMaterialInstance`，并为其创建展示用的`APSDQuadActor`和`APSDQuadMeshActor`。

## 使用场景

- **游戏UI制作**：美术在Photoshop中设计了一套UI界面（.psd文件），包含多个图层。使用`PSDImporter`导入后，通过本插件的右键菜单功能，一键生成每个图层对应的材质和显示模型，无需手动创建材质、设置纹理参数。
- **2D动画或视觉元素**：对于需要引擎内动态控制（如滚动、裁剪、特效混合）的2D元素，本插件提供了从PSD设计到可用材质资产的自动化管线。

## 蓝图用法

该插件主要通过**内容浏览器的右键上下文菜单**进行操作，其核心逻辑由C++工厂类实现，并未暴露大量蓝图可调用节点。用户交互流程如下：

1.  在内容浏览器中，选中一个通过 `PSDImporter` 导入的 `UPSDDocument` 资产。
2.  右键点击，在菜单中寻找 **“Material Designer”** 子菜单（由 `FPSDImporterMaterialDesignerContentBrowserIntegration` 添加）。
3.  选择创建选项（如“Create Material”或“Create Quads”），插件会调用底层工厂类，在当前资产附近生成材质资产和四方体演员资产。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| (无直接蓝图公开函数) | 核心创建功能由 `UPSDDocument` 右键菜单触发，不通过蓝图节点调用 | `UPSDImporterMDMaterialFactory`, `UPSDImporterMDQuadsFactory` |

### 使用示例（蓝图描述）

无法在蓝图图表中直接连接节点。操作流程为：
1.  打开内容浏览器，导航到存放导入的 `.PSD` 资产的文件夹。
2.  右键单击目标 `PSD Document` 资产。
3.  在弹出的上下文菜单中，找到并展开 **“Material Designer”** 选项。
4.  点击 **“Create Material”** 以生成对应的动态材质实例。
5.  或者点击 **“Create Quads”**，进一步选择类型以生成包含材质的四方体演员。

## C++ 用法

该插件主要在编辑器内使用，其公开API较少，主要逻辑通过内部工厂类实现。

### 头文件引入

```cpp
#include "PSDImporterMDConstants.h"
// 其他内部头文件通常在插件私有作用域内使用。
```

### 基本用法

通过工厂类为导入的 `PSDDocument` 创建材质资产。以下代码展示了如何检查并创建材质。

```cpp
// 假设 InDocument 是一个已加载的 UPSDDocument 指针
#include "Factories/PSDImporterMDMaterialFactory.h"
#include "PSDImporterMDConstants.h"

void CreateMaterialFromPSD(UPSDDocument* InDocument)
{
    if (!InDocument)
    {
        return;
    }

    // 创建材质工厂实例
    UPSDImporterMDMaterialFactory* MaterialFactory = NewObject<UPSDImporterMDMaterialFactory>();

    // 检查是否可以为该文档创建材质
    if (MaterialFactory->CanCreateMaterial(InDocument))
    {
        // 执行创建，返回生成的动态材质实例
        UDynamicMaterialInstance* CreatedMaterial = MaterialFactory->CreateMaterial(InDocument);
        if (CreatedMaterial)
        {
            // 材质创建成功，可以进行后续操作
            UE_LOG(LogPSDImporterMaterialDesignerBridge, Log, TEXT("Created Dynamic Material: %s"), *CreatedMaterial->GetName());
        }
    }
}
```

**来源**: 基于 `Source/PSDImporterMaterialDesignerBridge/Private/Factories/PSDImporterMDMaterialFactory.h` 和 `.cpp` 逻辑推断。

### 进阶用法

创建包含材质的四方体演员，用于在场景中展示PSD内容。此操作涉及World上下文和类型选择。

```cpp
#include "Factories/PSDImporterMDQuadsFactory.h"
#include "PSDImporterMDTypes.h" // 假设包含 EPSDImporterMaterialDesignerType

void CreateQuadsFromPSD(UWorld* InWorld, UPSDDocument* InDocument, EPSDImporterMaterialDesignerType InType)
{
    if (!InWorld || !InDocument)
    {
        return;
    }

    // 创建四方体工厂实例
    UPSDImporterMDQuadsFactory* QuadsFactory = NewObject<UPSDImporterMDQuadsFactory>();

    // 先创建一个四方体演员容器
    APSDQuadActor* QuadActor = QuadsFactory->CreateQuadActor(*InWorld, *InDocument);
    if (QuadActor)
    {
        // 为文档中的每个图层创建对应的四方体网格，并应用指定的材质设计类型
        QuadsFactory->CreateQuads(*QuadActor, InType);
        UE_LOG(LogPSDImporterMaterialDesignerBridge, Log, TEXT("Created Quad Actor: %s"), *QuadActor->GetName());
    }
}
```

**来源**: 基于 `Source/PSDImporterMaterialDesignerBridge/Private/Factories/PSDImporterMDQuadsFactory.h` 和 `.cpp` 逻辑推断。

## Demo 示例

一个最小的C++示例，演示如何使用本插件的工厂类。

```cpp
// MyPSDMaterialDemo.h
#pragma once
#include "CoreMinimal.h"

class UPSDDocument;
class UWorld;

class FPSDMaterialDemo
{
public:
    static void GenerateMaterialAndQuads(UWorld* InWorld, UPSDDocument* InDocument);
};

// MyPSDMaterialDemo.cpp
#include "MyPSDMaterialDemo.h"
#include "Factories/PSDImporterMDMaterialFactory.h"
#include "Factories/PSDImporterMDQuadsFactory.h"
#include "PSDImporterMDTypes.h" // 引入材质设计类型枚举

void FPSDMaterialDemo::GenerateMaterialAndQuads(UWorld* InWorld, UPSDDocument* InDocument)
{
    if (!InWorld || !InDocument)
    {
        return;
    }

    // 1. 创建材质
    UPSDImporterMDMaterialFactory* MatFactory = NewObject<UPSDImporterMDMaterialFactory>();
    if (MatFactory->CanCreateMaterial(InDocument))
    {
        UDynamicMaterialInstance* Material = MatFactory->CreateMaterial(InDocument);
        // Material 现在是一个已配置好的动态材质实例
    }

    // 2. 创建用于展示的四方体（以材质类型为例）
    UPSDImporterMDQuadsFactory* QuadFactory = NewObject<UPSDImporterMDQuadsFactory>();
    APSDQuadActor* Actor = QuadFactory->CreateQuadActor(*InWorld, *InDocument);
    if (Actor)
    {
        // 使用材质设计类型生成四方体
        QuadFactory->CreateQuads(*Actor, EPSDImporterMaterialDesignerType::Material); // 假设存在此枚举值
    }
}
```

## 模块依赖

使用本插件时，你的编辑器模块需要依赖以下插件提供的模块：

| 模块 | 用途 |
|---|---|
| `DynamicMaterial` | 提供 `UDynamicMaterialInstance`, `UDMMaterialModel` 等核心材质类和编辑器功能 |
| `PSDImporter` | 提供 `UPSDDocument`, `FPSDFileLayer` 等PSD文件解析和数据结构 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-04-28 | `9216b924` | Horde issue 881859 | 构建系统问题修复。 |
| 2025-04-28 | `fed4030e` | PSD Importer: Renamed and moved to Experimental | 插件被重命名并移至Experimental目录，标志着其作为独立实验插件的诞生。 |

### 维护评价

这是一个**刚刚创建、处于实验阶段**的插件。
- **创建时间**: 2025年4月28日，历史非常短。
- **近期更新**: 仅有两次提交，均在创建日。第一次是创建与迁移，第二次是构建修复。没有功能性更新的历史。
- **维护状态**: 由于刚创建且标记为实验性 (`IsExperimentalVersion=true`)，目前**无法判断长期维护状态**。它依赖于两个其他插件 (`PSDImporter`, `DynamicMaterial`)，其稳定性也受这些插件影响。
- **已知限制**:
    1.  `Installed: false`，需要手动在插件列表中启用。
    2.  目前仅支持 `Win64` 平台。
    3.  功能相对单一，专注于PSD到动态材质的转换流程。
- **推荐使用**: **谨慎推荐**。它是一个有明确用途的工具，非常适合需要此特定工作流的团队。但由于是实验性质，可能在未来发生重大变更或被移除。建议在生产项目中充分测试，并关注 `DynamicMaterial` 和 `PSDImporter` 主插件的更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporterMaterialDesignerBridge)
- [官方文档]() (无)
- 相关插件：
    - [PSDImporter 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PSDImporter)
    - [DynamicMaterial 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/DynamicMaterial)