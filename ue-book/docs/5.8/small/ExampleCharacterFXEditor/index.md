# ExampleCharacterFXEditor

> Example asset editor using the BaseCharacterFXEditor base classes

| 属性 | 值 |
|---|---|
| 中文名 | 角色特效编辑器示例 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ExampleCharacterFXEditor` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2022-10-06 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CharacterFXEditor/ExampleCharacterFXEditor) | |

## 用途

`ExampleCharacterFXEditor` 是一个示例插件，用于演示如何基于 `BaseCharacterFXEditor` 框架构建一个自定义的资产编辑器。它并非一个功能完备的编辑器，而是一个开发者参考模板。其核心目的是展示如何：

1.  **集成交互式工具框架 (Interactive Tools Framework)**：将建模和修改工具（来自 `MeshModelingToolset` 插件）集成到一个专用的资产编辑界面中。
2.  **管理编辑器生命周期**：通过 `EditorSubsystem` 管理编辑器实例的创建、打开、关闭以及与资产（UObject）的关联。
3.  **定义编辑器模式**：创建一个特定的 `EditorMode`，用于处理工具目标的创建、工具的注册和绑定。

它存在的意义是为开发者提供一个结构清晰的起点，用于开发角色、粒子、布料、毛发等资产的专用编辑器，当通用编辑器或细节面板无法满足复杂交互需求时。

## 使用场景

- 你需要为你的自定义资产（例如一个 `UCustomFXAsset`）创建一个专门的、功能丰富的编辑界面，而不是使用默认的资产编辑器。
- 你的编辑器需要深度集成 MeshModelingToolset 中的工具（如 UV 编辑、网格修改、属性编辑等）来进行资产创作。
- 你需要一个示例来学习 `BaseCharacterFXEditor` 框架是如何工作的，以便快速搭建自己的编辑器框架。
- 你在开发一个 CharacterFX 工作流（例如自定义粒子、布料解决方案），需要为其构建配套的创作工具。

## 蓝图用法

此插件主要面向 C++ 开发，提供编辑器框架。其核心蓝图接口在于通过子系统启动编辑器。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Example Character FX Editor` | 启动或切换到编辑指定资产的编辑器实例。 | `UExampleCharacterFXEditorSubsystem` |
| `Are Objects Valid Targets` | 检查一组对象是否是此编辑器的有效目标。 | `UExampleCharacterFXEditorSubsystem` |
| `Are Assets Valid Targets` | 检查一组资产数据是否是此编辑器的有效目标（推荐，避免强制加载UObject）。 | `UExampleCharacterFXEditorSubsystem` |

### 使用示例（蓝图描述）

1.  **获取子系统引用**：在蓝图中，使用 “Get Editor Subsystem” 节点，并选择 `UExampleCharacterFXEditorSubsystem` 类。
2.  **启动编辑器**：将要编辑的资产（例如一个 `SkeletalMesh` 资产引用）连接到 `Start Example Character FX Editor` 节点的 `ObjectsToEdit` 引脚。执行该节点将打开或激活编辑该资产的专用编辑器窗口。
3.  **验证资产有效性**：在尝试启动编辑器前，可以使用 `Are Assets Valid Targets` 节点传入 `FAssetData` 数组来验证资产是否支持，从而避免触发不必要的资产加载。

## C++ 用法

### 头文件引入

```cpp
#include "ExampleCharacterFXEditorSubsystem.h"
#include "ExampleCharacterFXEditorMode.h"
```

### 基本用法

从子系统启动编辑器。假设你有一个有效的 `UObject*` 指向你的目标资产。

```cpp
// 获取示例编辑器子系统
UExampleCharacterFXEditorSubsystem* FXEditorSubsystem = GEditor->GetEditorSubsystem<UExampleCharacterFXEditorSubsystem>();
if (FXEditorSubsystem)
{
    // 验证目标对象是否有效
    TArray<UObject*> ObjectsToEdit = {MyTargetAsset};
    if (FXEditorSubsystem->AreObjectsValidTargets(ObjectsToEdit))
    {
        // 启动编辑器
        FXEditorSubsystem->StartExampleCharacterFXEditor(ObjectsToEdit);
    }
}
```
*来源：基于 `ExampleCharacterFXEditorSubsystem.h` 中的接口设计推断。*

### 进阶用法

理解编辑器的内部结构。当用户通过内容浏览器右键菜单打开一个受支持资产（如 `SkeletalMesh`）的此编辑器时，框架会执行以下关键步骤（涉及多个类）：

1.  `FExampleCharacterFXEditorModule::StartupModule()` 注册内容浏览器扩展菜单。
2.  用户选择“使用 ExampleCharacterFXEditor 打开”，触发 `UExampleCharacterFXEditorSubsystem::StartExampleCharacterFXEditor`。
3.  子系统创建或找到一个 `UExampleCharacterFXEditor` (继承自 `UBaseCharacterFXEditor`) 实例来管理编辑会话。
4.  `UExampleCharacterFXEditor::CreateToolkit()` 创建 `FExampleCharacterFXEditorToolkit`，后者负责创建 `UExampleCharacterFXEditorMode`。
5.  `UExampleCharacterFXEditorMode::InitializeTargets()` 被调用，它会使用 `UExampleCharacterFXEditorSubsystem` 创建的 `UToolTarget` 来设置编辑视图（例如创建 `UDynamicMeshComponent` 进行预览）。
6.  `UExampleCharacterFXEditorMode::RegisterTools()` 将来自 `MeshModelingToolset` 的工具（如属性编辑器）注册到编辑器的工具栏中。

## Demo 示例

一个最小化的 C++ 代码片段，展示如何从你的游戏模块或编辑器模块中打开此示例编辑器。

```cpp
// MyCustomEditorUtils.h
#pragma once

#include "CoreMinimal.h"

class FMyCustomEditorUtils
{
public:
    static void OpenAssetInExampleFXEditor(UObject* AssetToEdit);
};
```

```cpp
// MyCustomEditorUtils.cpp
#include "MyCustomEditorUtils.h"
#include "ExampleCharacterFXEditorSubsystem.h"
#include "Editor.h"

void FMyCustomEditorUtils::OpenAssetInExampleFXEditor(UObject* AssetToEdit)
{
    if (!AssetToEdit) return;

    UExampleCharacterFXEditorSubsystem* Subsystem = GEditor->GetEditorSubsystem<UExampleCharacterFXEditorSubsystem>();
    if (Subsystem)
    {
        TArray<UObject*> Assets = { AssetToEdit };
        if (Subsystem->AreObjectsValidTargets(Assets))
        {
            Subsystem->StartExampleCharacterFXEditor(Assets);
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("Asset %s is not a valid target for ExampleCharacterFXEditor."), *AssetToEdit->GetName());
        }
    }
}
```

## 模块依赖

此插件依赖于以下非标准模块，你的模块若要使用其功能，也需要添加对这些模块的依赖。

| 模块 | 用途 |
|---|---|
| `BaseCharacterFXEditor` | 提供本插件所基于的编辑器基类、模式、工具包等核心框架。 |
| `MeshModelingToolset` | 提供编辑器模式中集成的基础建模和修改工具。 |
| `MeshModelingToolsetExp` | 提供编辑器模式中集成的实验性建模工具。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-03-05 | `7ab43c2f` | Add and address deprecation warning after UEditorInteractiveToolsContext classes move to UnrealEd | 适配 `UEditorInteractiveToolsContext` 类的迁移，修复了弃用警告。 |
| 2024-12-20 | `d0cf4301` | ModelingTools: Promote experimental modeling tools to beta. | 随父级框架更新，模型工具从实验版升级至测试版。 |
| 2024-12-19 | `0b7db795` | [Backout] - CL38936187 | 回退了前一次提交。 |
| 2024-12-19 | `4581f566` | ModelingTools: Promote experimental modeling tools to beta. | （同 `d0cf4301`）模型工具从实验版升级至测试版。 |
| 2023-08-05 | `d3991fec` | Fixing potential compile errors ahead of enabling TObjectPtr GC barrier | 为启用 `TObjectPtr` 垃圾回收屏障提前修复潜在的编译错误。 |

### 维护评价

- **状态**：**维护中**。该插件最近一次实质性的框架兼容性更新发生在2025年3月，表明它仍然与最新的引擎版本保持同步。
- **活跃度**：作为**示例插件**，其功能本身已相对稳定，更新主要跟随其基础框架（`BaseCharacterFXEditor`, `MeshModelingToolset`）的变化而进行适应性调整，而非独立的功能开发。
- **已知限制**：标记为 `IsExperimentalVersion=true` 且 `Installed=false`，意味着它默认不启用，且属于实验性功能，API或用法在后续版本中可能发生变化。
- **推荐使用**：**仅推荐用于学习和参考**。如果你需要构建自己的 `CharacterFX` 类型编辑器，这是一个极佳的起点和蓝图。**不建议**在最终产品中直接依赖此示例插件，因为它可能包含示例专用的、非必要的代码，并且其名称和接口明确表明它是“示例”。正确做法是复制其结构，并基于你自己的资产和工具需求进行修改和扩展。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CharacterFXEditor/ExampleCharacterFXEditor)
- [官方文档]( ) （`.uplugin` 中 `DocsURL` 为空，暂无官方文档链接）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CharacterFXEditor/ExampleCharacterFXEditor/Tests) （需确认是否存在）