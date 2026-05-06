# ExampleCharacterFXEditor

> Example asset editor using the BaseCharacterFXEditor base classes

| 属性 | 值 |
|---|---|
| 中文名 | 示例角色FX编辑器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器模板与示例代码） |
| 模块 | `ExampleCharacterFXEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-08-05 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CharacterFXEditor/ExampleCharacterFXEditor) | |

## 用途

本插件是一个**教学示例**，用于演示如何基于 `BaseCharacterFXEditor` 框架快速构建一个自定义资产编辑器。它不提供生产级别的功能，而是展示以下关键步骤：

- 继承 `UBaseCharacterFXEditor`、`UBaseCharacterFXEditorMode`、`FBaseCharacterFXEditorToolkit` 等基类实现编辑器核心。
- 通过 `UEditorSubsystem`（`UExampleCharacterFXEditorSubsystem`）组织编辑器实例的创建与管理。
- 利用 `InteractiveToolsFramework` 注册工具（如示例中的 `BeginAttributeEditorTool`），并在编辑模式下集成。
- 通过 `SlateStyle` 和命令系统为编辑器提供界面样式与快捷键支持。

该插件主要面向**希望为自己的资产类型创建类似 Modeling Tools 风格编辑器的引擎开发者**，作为学习和复用的起点。

## 使用场景

- 你正在开发一个需要**交互式建模/雕刻工具**的自定义资产编辑器（如角色面部变形、布料模拟等）。
- 你想了解如何将 `BaseCharacterFXEditor` 基类与 `MeshModelingToolset`、`MeshModelingToolsetExp` 结合。
- 你需要一个最小化的示例来快速启动一个具备工具面板、属性细节和视口交互的编辑器。

## 蓝图用法

本插件**未暴露任何可蓝图调用的函数或属性**。所有功能均通过 C++ 和编辑器工具框架实现，蓝图无法直接交互。

## C++ 用法

### 头文件引入

```cpp
#include "ExampleCharacterFXEditorModule.h"
#include "ExampleCharacterFXEditorSubsystem.h"
#include "ExampleCharacterFXEditorMode.h"
```

### 基本用法

#### 1. 启动编辑器（通过子系统）

```cpp
// 获取子系统并启动编辑器，传入要编辑的资产对象（如 StaticMesh、SkeletalMesh）
UExampleCharacterFXEditorSubsystem* Subsystem = GEditor->GetEditorSubsystem<UExampleCharacterFXEditorSubsystem>();
if (Subsystem)
{
    TArray<TObjectPtr<UObject>> ObjectsToEdit;
    // 填充需要编辑的资产...
    Subsystem->StartExampleCharacterFXEditor(ObjectsToEdit);
}
```
*来源: `ExampleCharacterFXEditorSubsystem.h` 中的 `StartExampleCharacterFXEditor` 方法*

#### 2. 检查资产是否支持编辑

```cpp
if (Subsystem->AreAssetsValidTargets(AssetDatas))
{
    // 可以安全地启动编辑器
}
```
*来源: `ExampleCharacterFXEditorSubsystem.h`*

#### 3. 自定义工具注册（在模式类中）

在 `UExampleCharacterFXEditorMode::RegisterTools()` 中，可以像下面这样注册新的工具：

```cpp
void UExampleCharacterFXEditorMode::RegisterTools()
{
    // 示例：注册一个简单的属性编辑工具
    UInteractiveToolManager* ToolManager = GetToolManager();
    ToolManager->RegisterToolType(
        FExampleCharacterFXEditorCommands::BeginAttributeEditorToolIdentifier,
        NewObject<UExampleAttributeEditorToolBuilder>(this));
}
```
*来源: `ExampleCharacterFXEditorMode.cpp`（示例思路，实际工具需要自行实现）*

### 进阶用法

#### 自定义编辑器主题与样式

`FExampleCharacterFXEditorStyle` 提供了 Slate 样式集，可重写图标、颜色等：

```cpp
const FSlateBrush* Brush = FExampleCharacterFXEditorStyle::Get().GetBrush("ExampleCharacterFXEditor.SomeIcon");
```
*来源: `ExampleCharacterFXEditorStyle.h`*

#### 多实例管理

子系统通过 `OpenedEditorInstances` 映射追踪已打开的编辑器实例，确保同一组对象不会重复打开：

```cpp
Subsystem->NotifyThatExampleCharacterFXEditorClosed(ObjectsItWasEditing);
```
*来源: `ExampleCharacterFXEditorSubsystem.h`*

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何在模块启动时注册菜单并触发编辑器。

**ExampleCharacterFXEditorDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"

class FExampleCharacterFXEditorDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**ExampleCharacterFXEditorDemo.cpp**
```cpp
#include "ExampleCharacterFXEditorDemo.h"
#include "ExampleCharacterFXEditorSubsystem.h"
#include "Engine/Selection.h"
#include "Editor.h"

void FExampleCharacterFXEditorDemoModule::StartupModule()
{
    // 注册一个简单的控制台命令来演示启动编辑器
    IConsoleManager::Get().RegisterConsoleCommand(
        TEXT("DemoOpenExampleFXEditor"),
        TEXT("Opens the ExampleCharacterFXEditor with currently selected assets"),
        FConsoleCommandDelegate::CreateLambda([]()
        {
            UExampleCharacterFXEditorSubsystem* Subsystem = GEditor->GetEditorSubsystem<UExampleCharacterFXEditorSubsystem>();
            if (!Subsystem)
                return;

            TArray<TObjectPtr<UObject>> SelectedObjects;
            for (FSelectionIterator It = GEditor->GetSelectedActorIterator(); It; ++It)
            {
                if (AActor* Actor = Cast<AActor>(*It))
                {
                    SelectedObjects.Add(Actor);
                }
            }
            if (SelectedObjects.Num() > 0)
            {
                Subsystem->StartExampleCharacterFXEditor(SelectedObjects);
            }
        })
    );
}

void FExampleCharacterFXEditorDemoModule::ShutdownModule()
{
    // 清理命令
}
```
> **注意**：该示例仅为演示概念，实际使用需要正确链接模块依赖并结合适当的资产类型检查。

## 模块依赖

要使用 `ExampleCharacterFXEditor` 插件，你的模块需要在 `Build.cs` 中添加以下依赖（省略标准 Core/Engine 模块）：

| 模块 | 用途 |
|---|---|
| `BaseCharacterFXEditor` | 提供编辑器基类（模式、工具包、编辑器对象） |
| `MeshModelingToolset` | 建模工具集基础（工具类型、目标工厂） |
| `MeshModelingToolsetExp` | 实验性建模工具（如属性编辑工具） |

## 维护状态

### 近期更新

- 2025-03-05 `7ab43c2f` 添加并处理 `UEditorInteractiveToolsContext` 类迁移至 UnrealEd 后的弃用警告
- 2024-12-20 `d0cf4301` 建模工具从实验性提升为 Beta（影响依赖包）
- 2024-12-19 `0b7db795` 回退上一次提交
- 2024-12-19 `4581f566` 建模工具提升为 Beta（第二次尝试）
- 2023-08-05 `d3991fec` 修复潜在的编译错误（TObjectPtr 垃圾回收屏障）

### 维护评价

- **创建时间**：2023 年 8 月，约 1.5 年
- **近期更新**：2025 年 3 月仍有一次性修复，整体跟随 `BaseCharacterFXEditor` 框架和建模工具集的演进而被动更新
- **活跃度**：不活跃（仅适配性修改，无功能新增）
- **已知限制**：
  - 仅支持 Win64 平台
  - 实验性版本，API 可能在不通知的情况下变更
  - 不是任何资产类型的默认编辑器，需要通过子系统手动触发
- **推荐使用**：作为学习 `BaseCharacterFXEditor` 框架的参考示例非常合适；**不建议在生产项目中直接依赖**，因为其随时可能被移除或重构

## 相关链接

- [源码（Plugin 根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CharacterFXEditor/ExampleCharacterFXEditor)
- [基类插件 BaseCharacterFXEditor 源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CharacterFXEditor/BaseCharacterFXEditor)
- [测试用例（Engine/Tests 下可能包含相关测试）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Tests)