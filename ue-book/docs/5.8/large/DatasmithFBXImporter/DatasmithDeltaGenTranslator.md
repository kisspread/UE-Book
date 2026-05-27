# Datasmith FBX Importer

> Adds support for importing content from DeltaGen and VRED into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | Datasmith FBX导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（翻译器模块） |
| 模块 | `DatasmithVREDTranslator` (Editor), `DatasmithDeltaGenTranslator` (Editor), `DatasmithFBXTranslator` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithFBXImporter) | |

## 用途

此插件为 Unreal Engine 的 Datasmith 导入框架增加了特定于汽车设计与可视化软件（DeltaGen 和 VRED）的 FBX 场景文件导入支持。其核心功能远超通用 FBX 导入器，旨在完整解析并转换这些专业软件生成的场景数据，包括：
*   **复杂的变体系统 (Variants)**：解析 `.var` 文件，导入几何体切换、材质切换、相机切换、组合包等高级变体逻辑。
*   **预设状态 (POS States)**：解析 `.pos` 文件，导入预定义的场景状态（如不同配置、材质方案）。
*   **时间轴动画 (TML Animations)**：解析 `.tml` 文件，导入复杂的、带有贝塞尔控制点的曲线动画。

它将这些专用数据转换为引擎内的 Datasmith 资产（如关卡序列、变体集），从而实现从汽车设计软件到 Unreal Engine 的完整、高保真的工作流迁移。

## 使用场景

*   **汽车设计可视化**：设计师使用 DeltaGen 或 VRED 创建了包含多配置、材质方案和复杂动画的车辆/产品数字孪生模型，需要将其无缝导入 Unreal Engine 进行实时渲染、交互式配置展示或虚拟评审。
*   **遗留系统集成**：你的工作流程严重依赖于 DeltaGen 或 VRED 的专有 FBX 输出格式（包含附加的 `.var`, `.pos`, `.tml` 数据），并且需要将这些数据完整地带入 UE。

## 蓝图用法

此插件主要提供编辑器内的导入功能，其核心逻辑通过 C++ 的 `IDatasmithTranslator` 接口实现，并不直接暴露为蓝图节点。用户交互主要通过标准的 Datasmith “导入” 对话框完成，插件会在其中提供 DeltaGen 和 VRED 特有的导入选项。

### 导入选项

在导入 DeltaGen 或 VRED 的 FBX 文件时，可以在导入对话框中找到并配置 `UDatasmithDeltaGenImportOptions`。关键选项包括：

| 选项 | 说明 |
|---|---|
| **Import Variants** (`bImportVar`) | 是否导入 `.var` 变体文件 |
| **Import POS States** (`bImportPos`) | 是否导入 `.pos` 预设状态文件 |
| **Import TML Animations** (`bImportTml`) | 是否导入 `.tml` 时间轴动画文件 |
| **Shadow Textures** (`ShadowTextureMode`) | 控制如何处理阴影纹理（忽略、作为AO、作为乘数等） |
| **Remove Invisible Nodes** (`bRemoveInvisibleNodes`) | 是否移除在原始场景中标记为不可见的节点 |
| **Simplify Node Hierarchy** (`bSimplifyNodeHierarchy`) | 是否简化无网格、无动画的中间节点层级 |

## C++ 用法

### 头文件引入

通常你不会直接与这些类交互，因为它们被 Datasmith 的导入管线内部使用。但如果需要扩展或调试，可以引入：

```cpp
#include "DatasmithDeltaGenImporter.h"
```

### 基本用法

主要的交互点是 `FDatasmithDeltaGenTranslator`，它实现了 `IDatasmithTranslator` 接口，被 Datasmith 导入器自动发现和使用。

```cpp
// 通常由 Datasmith 导入系统内部调用，以下为示意代码
// 创建导入器实例
TSharedRef<IDatasmithScene> OutScene = MakeShared<FScene>();
TObjectPtr<UDatasmithDeltaGenImportOptions> Options = NewObject<UDatasmithDeltaGenImportOptions>();
FDatasmithDeltaGenImporter Importer(OutScene, Options);

// 配置导入选项
Options->bImportVar = true;
Options->bImportTml = true;
Options->ShadowTextureMode = EShadowTextureMode::AmbientOcclusionAndMultiplier;

// 加载场景文件
const FString FBXPath = TEXT("D:/Path/To/DeltaGenScene.fbx");
if (Importer.OpenFile(FBXPath))
{
    // 处理并发送场景数据到 Datasmith 系统
    Importer.SendSceneToDatasmith();
    // 清理
    Importer.UnloadScene();
}
```

**来源：** 基于 `DatasmithDeltaGenImporter.h` 中 `FDatasmithDeltaGenImporter` 的公共接口设计。

### 进阶用法

对于 DeltaGen 特有的数据处理，插件内部使用了多个专用处理器：
1.  **场景处理**：`FDatasmithDeltaGenSceneProcessor` 负责处理轴心点分解 (`DecomposePivots`) 和环境光遮蔽纹理 (`SetupAOTextures`)。
2.  **动画插值**：`DeltaGen::FInterpolator` 及其派生类 (`FConstInterpolator`, `FLinearInterpolator`, `FCubicInterpolator`) 用于精确评估 VRED/DeltaGen 定义的贝塞尔动画曲线。
3.  **辅助文件解析**：`FDatasmithDeltaGenAuxFiles` 提供静态方法 (`ParseVarFile`, `ParsePosFile`, `ParseTmlFile`) 来解析对应的辅助文件格式。

## Demo 示例

以下是一个概念性的 C++ 示例，展示了如何使用此插件的核心类来导入一个 DeltaGen FBX 场景并处理其数据。这是一个**最小化演示**，省略了错误处理和完整的 Datasmith 资产保存流程。

**Source/DatasmithDeltaGenImporterDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class UDatasmithDeltaGenImportOptions;
class FDatasmithDeltaGenImporter;
class IDatasmithScene;

class FDeltaGenImportDemo
{
public:
    void RunImportDemo(const FString& InFBXPath);
private:
    TSharedPtr<IDatasmithScene> Scene;
    TUniquePtr<FDatasmithDeltaGenImporter> Importer;
    UDatasmithDeltaGenImportOptions* Options = nullptr;
};
```

**Source/DatasmithDeltaGenImporterDemo.cpp**
```cpp
#include "DatasmithDeltaGenImporterDemo.h"
#include "DatasmithDeltaGenImporter.h"
#include "DatasmithDeltaGenImportOptions.h"
#include "DatasmithScene.h"

void FDeltaGenImportDemo::RunImportDemo(const FString& InFBXPath)
{
    // 1. 创建 Datasmith 场景对象和导入选项
    Scene = MakeShared<FScene>();
    Options = NewObject<UDatasmithDeltaGenImportOptions>(GetTransientPackage(), TEXT("DemoImportOptions"));

    // 2. 配置导入选项
    Options->bImportVar = true;   // 导入变体
    Options->bImportPos = true;   // 导入预设状态
    Options->bImportTml = true;   // 导入时间轴动画
    Options->ShadowTextureMode = EShadowTextureMode::AmbientOcclusion;

    // 3. 实例化导入器
    Importer = MakeUnique<FDatasmithDeltaGenImporter>(Scene.ToSharedRef(), Options);
    Importer->SetImportOptions(Options);

    // 4. 执行导入流程
    if (Importer->OpenFile(InFBXPath))
    {
        UE_LOG(LogTemp, Log, TEXT("DeltaGen FBX 文件加载成功: %s"), *InFBXPath);

        // 此处可以添加对解析后数据的检查，例如:
        // auto ImporterData = Importer->GetInternalData(); // 假设有这样的访问器

        if (Importer->SendSceneToDatasmith())
        {
            UE_LOG(LogTemp, Log, TEXT("场景数据已成功发送到 Datasmith 系统。"));
            // 接下来通常由 Datasmith 导入器处理场景资产（网格体、材质、关卡序列等）的最终创建。
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("发送场景数据到 Datasmith 失败。"));
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("无法打开 DeltaGen FBX 文件: %s"), *InFBXPath);
    }

    // 5. 清理资源
    if (Importer.IsValid())
    {
        Importer->UnloadScene();
    }
    Scene.Reset();
}
```

## 模块依赖

从 `Build.cs` 分析，要使用或扩展此插件，你的模块需要依赖以下独特的模块：

| 模块 | 用途 |
|---|---|
| `DatasmithRuntime` | Datasmith 运行时的核心模块 |
| `DatasmithCore` | Datasmith 核心数据类型和接口 |
| `DatasmithImporter` | Datasmith 导入框架 |
| `DatasmithContent` | Datasmith 内容资产（材质、蓝图等） |
| `DatasmithExporter` | 用于访问导出时的一些工具类 |
| `FBX` | Autodesk FBX SDK 的集成模块 |
| `MeshDescription` | 用于处理网格体描述数据 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复不可达代码错误 |
| 2025-03-13 | `b059f7b4` | Fix trivial unreachable code warnings. | 修复琐碎的不可达代码警告 |
| 2024-10-02 | `0a14cf0e` | Update VRED python exporter to support API changes in VRED | 更新VRED Python导出器以支持VRED的API变更 |

### 维护评价

*   **状态**：**维护中但不活跃**。插件创建于2019年，是一个相对成熟的**遗留系统集成**组件。
*   **最近活动**：最近几次更新（2024-2026年）均为**代码维护性修复**（编译器警告、代码规范、小错误修复），**没有新功能或重大改进**。最后一次与DeltaGen/VRED工作流相关的实质性更新可能是在很久以前。
*   **功能完整**：从其核心结构看，变体、状态、动画的导入支持已经实现。
*   **推荐使用**：如果你的项目**必须**支持从DeltaGen或VRED的特定FBX格式导入数据，并且使用UE5.8或相近版本，此插件是必需且可用的。但对于新的项目或不依赖这些特定软件的工作流，**无需启用**此插件。
*   **注意**：由于它是一个专用于特定第三方软件格式的转换器，其长期活力取决于上游软件（DeltaGen/VRED）的演变。目前看来，维护仅限于跟随UE引擎本身的编译和API变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithFBXImporter)
- [官方文档](): `.uplugin` 中未提供官方文档链接
- [测试用例](): 该插件目录下未包含显式的测试文件（如 `Tests/` 文件夹）。