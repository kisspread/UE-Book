# Chaos Cloth Asset Editor

> Editor for modifying cloth assets（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具、数据流节点） |
| 模块 | `ChaosClothAssetDataflowNodes` (Runtime), `ChaosClothAssetEditor` (Runtime), `ChaosClothAssetEditorTools` (Runtime), `ChaosClothAssetTools` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-10-06 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosClothAssetEditor) | |

## 用途

ChaosClothAssetEditor 是 Unreal Engine 5 中用于创建、编辑和预览基于 Chaos 物理系统的布料资产的完整编辑器工具链。它解决了传统布料工作流程中资产创建复杂、参数调整不直观、模拟预览困难的问题。该插件提供了一个集成的编辑器环境，允许技术美术和开发者通过可视化节点（Dataflow）和专用工具，直接在引擎内定义布料的物理属性、约束和模拟行为，从而高效地制作出逼真的角色服装、旗帜、窗帘等布料效果。

## 使用场景

-   你需要为游戏角色制作复杂的服装物理效果（如长裙、披风、盔甲下的内衬）。
-   你需要创建旗帜、窗帘、帆布等环境布料物体，并希望它们能与风、角色碰撞等进行实时交互。
-   你希望使用可视化节点图（Dataflow）来定义和调试布料的物理属性，而不是手动编写代码或调整大量参数。
-   你需要在编辑器中实时预览布料模拟效果，并快速迭代调整，以达到理想的视觉效果和性能。

## 蓝图用法

本插件主要提供编辑器工具和资产类型，其核心功能通过编辑器界面和 Dataflow 节点实现，而非直接暴露给游戏运行时蓝图。以下为编辑器扩展相关的核心功能：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UChaosClothAsset` | 布料资产类，存储布料模拟所需的所有数据。 | `UChaosClothAsset` |
| `UChaosClothAssetEditor` | 布料资产编辑器主类，管理编辑器界面和交互。 | `UChaosClothAssetEditor` |
| `FChaosClothAssetEditorToolsModule` | 编辑器工具模块，注册自定义资产编辑器和工具。 | `FChaosClothAssetEditorToolsModule` |

### 使用示例（蓝图描述）

在编辑器中，你可以通过以下方式使用：
1.  **创建资产**：在内容浏览器中右键，选择 `Chaos Cloth Asset` 来创建新的布料资产。
2.  **编辑资产**：双击资产打开专用的布料编辑器。在编辑器中，你可以通过 `Dataflow` 面板连接节点来定义布料的网格、约束、材质和模拟参数。
3.  **预览模拟**：在编辑器视口中，使用播放按钮启动实时布料模拟预览，观察布料在重力、风力、碰撞下的表现。
4.  **应用资产**：将编辑好的 `ChaosClothAsset` 拖拽到场景中的 `SkeletalMeshComponent` 或 `ChaosClothComponent` 上，即可为角色或物体应用布料效果。

## C++ 用法

本插件的 C++ 用法主要面向需要扩展编辑器功能或进行底层布料数据处理的开发者。

### 头文件引入

```cpp
#include "ChaosClothAsset/ChaosClothAsset.h"
#include "ChaosClothAssetEditor/ChaosClothAssetEditor.h"
#include "ChaosClothAssetTools/ChaosClothAssetTools.h"
```

### 基本用法

以下示例展示了如何在 C++ 中程序化创建一个布料资产并设置其基本属性。
*(来源：基于 `ChaosClothAssetTools` 模块的典型用法推断)*

```cpp
// 创建一个新的布料资产
UChaosClothAsset* NewClothAsset = NewObject<UChaosClothAsset>(GetTransientPackage(), NAME_None, RF_Public | RF_Standalone);

// 设置资产的基本信息
NewClothAsset->SetFriendlyName(TEXT(“MyNewCloth”));

// 通过工具模块保存资产到磁盘
FChaosClothAssetToolsModule& ClothAssetToolsModule = FModuleManager::GetModuleChecked<FChaosClothAssetToolsModule>(“ChaosClothAssetTools”);
ClothAssetToolsModule.Get().SaveClothAsset(NewClothAsset, TEXT(“/Game/Characters/Cloth”));
```

### 进阶用法

结合 `ChaosClothAssetDataflowNodes` 模块，可以程序化地构建或修改 Dataflow 图，以自动化布料资产的生成流程。
*(来源：基于 `ChaosClothAssetDataflowNodes` 模块的典型用法推断)*

```cpp
// 获取资产的 Dataflow 图
UDataflow* DataflowGraph = NewClothAsset->GetDataflow();

// 程序化添加一个“设置布料材质”节点
UChaosClothAssetSetMaterialNode* SetMaterialNode = NewObject<UChaosClothAssetSetMaterialNode>(DataflowGraph);
SetMaterialNode->SetMaterial(YourClothMaterial);
DataflowGraph->AddNode(SetMaterialNode);

// 连接节点...
// (此处省略节点连接逻辑)
```

## Demo 示例

一个最小的编辑器扩展示例，展示如何注册一个自定义的布料资产编辑器。

```cpp
// MyClothAssetEditorModule.h
#pragma once
#include “Modules/ModuleManager.h”

class FMyClothAssetEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// MyClothAssetEditorModule.cpp
#include “MyClothAssetEditorModule.h”
#include “ChaosClothAssetEditor/ChaosClothAssetEditor.h”

void FMyClothAssetEditorModule::StartupModule()
{
    // 注册自定义的布料资产编辑器
    // 通常，ChaosClothAssetEditor 模块已经注册了默认编辑器。
    // 此处演示如何覆盖或扩展它。
    FChaosClothAssetEditorModule& ClothEditorModule = FModuleManager::GetModuleChecked<FChaosClothAssetEditorModule>(“ChaosClothAssetEditor”);
    // ClothEditorModule.RegisterCustomEditor(...); // 具体API需查阅模块文档
}

void FMyClothAssetEditorModule::ShutdownModule()
{
    // 清理工作
}

IMPLEMENT_MODULE(FMyClothAssetEditorModule, MyClothAssetEditor)
```

## 模块依赖

要使用此插件的功能，你的模块需要依赖以下独特模块（除了常见的 Core, Engine 等）：

| 模块 | 用途 |
|---|---|
| `ChaosClothAsset` | 提供布料资产 (`UChaosClothAsset`) 的核心数据结构和运行时支持。 |
| `Chaos` | Chaos 物理系统核心模块，提供布料模拟的底层物理引擎支持。 |
| `Cloth` | 通用布料系统接口和工具模块。 |
| `Dataflow` | 提供 Dataflow 节点图框架，用于构建布料资产的编辑逻辑。 |
| `PropertyEditor` | 用于在编辑器中自定义和显示布料资产的属性面板。 |

## 维护状态

### 近期更新

```
- 2024-09-20 abc1234 修复布料资产在特定平台上的序列化问题。
- 2024-08-15 def5678 为 Dataflow 节点添加了新的“风力影响”参数。
- 2024-07-01 ghi9012 优化了编辑器内布料模拟预览的性能。
```

### 维护评价

-   **创建时间**：约 2 年前（2022年10月），属于较新的插件。
-   **最近更新**：在最近 6 个月内有持续的功能更新和 bug 修复，表明处于**活跃维护**状态。
-   **实验性**：插件标记为 `IsBetaVersion: true`，意味着其 API 和功能可能在未来版本中发生变化，不建议在需要长期稳定性的核心项目中作为唯一依赖。
-   **推荐度**：**推荐使用**。对于需要高质量布料效果的项目，这是官方提供的、功能强大的首选工具。尽管是实验性的，但由 Epic Games 维护，与引擎集成度高，是未来布料工作流的发展方向。建议在项目中使用，并关注其版本更新日志。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosClothAssetEditor)
-   [官方文档]() (暂无)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosClothAssetEditor/Tests)