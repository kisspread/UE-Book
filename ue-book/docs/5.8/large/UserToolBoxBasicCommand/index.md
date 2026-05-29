# UserToolBoxBasicCommand

> Basic set of command to populate a custom editor tab

| 属性 | 值 |
|---|---|
| 中文名 | 基础命令集 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UserToolBoxBasicCommand` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-18 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UserToolBoxBasicCommand) | |

## 用途

该插件为 **UserToolBoxCore** 插件提供了一套预置的、可扩展的基础编辑器命令（Command）。它并非独立工作，而是作为 `UserToolBoxCore` 命令系统的“素材库”，包含了大量用于自动化编辑器操作的具体命令实现，例如选择、清理、合并、镜像Actor等。

**核心价值**：解决了需要在自定义编辑器工具栏或标签页中快速集成常用、重复性编辑操作的需求。开发者或技术美术可以利用这些现成的命令，通过蓝图或C++快速搭建功能丰富的编辑器工具，而无需从零开始编写每一个基础操作。

## 使用场景

-   你需要创建一个自定义编辑器面板，一键清理从Datasmith导入的混乱场景层级。
-   你需要批量选择场景中具有特定元数据或特定类型组件的Actor。
-   你需要一个按钮来执行复杂的控制台命令序列或Python脚本。
-   你需要在编辑器中快速实现物体镜像、法线翻转、高精度设置等操作。
-   你需要构建一个命令切换器（Toggle Command），在多个预设状态间循环切换。

## 蓝图用法

该插件的核心是提供一系列 `UUTBBaseCommand` 的子类。这些命令主要通过编辑器属性面板进行配置，而不是通过蓝图节点图连接。

### 核心命令类

以下是该插件提供的主要可蓝图实例化的命令类（均继承自 `UUTBBaseCommand`）：

| 命令类 | 说明 | 所在文件 |
|---|---|---|
| `USelectActorByFilter` | 根据一个或多个可配置的过滤规则（如类名、组件、元数据、层级关系）来选择Actor。支持组合筛选（并集、交集、差集）。 | `SelectActorByFilter.h` |
| `UCompositeCommand` / `UCompositeInlineCommand` | 组合命令，将多个已注册的命令按顺序执行。 | `CompositeCommand.h` |
| `UToggleCommand` / `UToggleCommandInline` | 循环切换命令，依次执行预设的命令列表，每次点击执行下一个。 | `ToggleCommand.h` |
| `UCleanHierarchy` | 清理场景层级，可移除空分支、无几何体的中间Actor，并选择性保留某些元数据。 | `CleanHierarchy.h` |
| `UMirrorActorCommand` | 沿指定的X/Y/Z轴镜像选中的Actor。 | `MirrorActorCommand.h` |
| `UConsoleVariable` | 执行一个或多个控制台命令/变量设置。 | `ConsoleVariable.h` |
| `UExecutePythonScript` | 执行一个指定的Python脚本文件，并可传递参数。 | `ExecutePythonScript.h` |
| `UEngineCommand` | 执行一个引擎命令字符串。 | `EngineCommand.h` |
| `UIsolateSelection` | 隔离当前选中的Actor（隐藏其他）。 | `IsolateSelection.h` |
| `UMerge` | 合并选中的静态网格体Actor。 | `MergeCommand.h` |

### 使用示例（蓝图描述）

在 `UserToolBoxCore` 创建的编辑器UI（如工具栏按钮）中，通常不会直接在蓝图图中“调用”这些命令。正确的使用方式是：

1.  **配置命令**：在你的编辑器UI资产（例如一个UUserToolBoxWidget）的“Commands”数组中，添加一个 `USelectActorByFilter` 的实例。
2.  **设置属性**：在属性面板中，配置该命令的 `FilterStack`，添加过滤规则。例如，添加一个 `UIsClassOf` 过滤器，并设置其 `ActorClass` 为 `AStaticMeshActor`。
3.  **执行**：当用户在编辑器中点击对应工具栏按钮时，框架会自动调用这个命令实例的 `Execute()` 函数，从而根据你配置的规则选择所有静态网格体Actor。

组合命令的使用类似，将多个命令实例填入 `UCompositeCommand` 的 `Commands` 数组即可。

## C++ 用法

虽然该插件本身是实验性的Editor插件，不建议在运行时模块中深度依赖，但了解其设计模式有助于理解或扩展 `UserToolBoxCore`。

### 头文件引入

由于该插件模块类型为 `Editor`，你的代码（通常是Editor模块）需要添加对其的依赖。
```cpp
// 在你的模块头文件或Build.cs中，可能需要包含
#include "UserToolBoxBasicCommand.h"
```

### 基本用法

命令的核心是继承 `UUTBBaseCommand` 并重写 `Execute()` 函数。
```cpp
// 示例：创建一个自定义命令
#include "UTBBaseCommand.h" // 来自 UserToolBoxCore 模块

UCLASS()
class UMyCustomCommand : public UUTBBaseCommand
{
    GENERATED_BODY()

public:
    UMyCustomCommand()
    {
        Name = TEXT("My Command");
        Tooltip = TEXT("Does something custom");
        Category = TEXT("Custom");
    }

    // 命令参数
    UPROPERTY(EditAnywhere, Category="Custom")
    FString SomeParameter;

    virtual void Execute() override
    {
        // 在这里实现你的编辑器操作逻辑
        UE_LOG(LogTemp, Log, TEXT("Executed MyCustomCommand with param: %s"), *SomeParameter);
    }
};
```

### 进阶用法

该插件的源码展示了如何利用 Actor Filter 系统进行复杂选择。以下是其内部逻辑的简化版，可用于理解或在你的命令中复用筛选逻辑。
```cpp
// 假设你有一个 Actor 列表需要筛选
TArray<AActor*> AllActorsInLevel; // ... 获取方法省略

// 实例化一个过滤器
UGetAllDescendants* DescendantFilter = NewObject<UGetAllDescendants>();
// UHasComponentOfClass* ComponentFilter = NewObject<UHasComponentOfClass>();
// ComponentFilter->ComponentClass = UStaticMeshComponent::StaticClass();

// 执行筛选
TArray<AActor*> FilteredActors = DescendantFilter->FilterImpl(AllActorsInLevel);

// 对筛选结果执行操作
for (AActor* Actor : FilteredActors)
{
    // 例如：设置Actor为隐藏
    Actor->SetActorHiddenInGame(true);
}
```

## Demo 示例

一个最小化的自定义命令示例，用于将选中Actor旋转90度。

```cpp
// MyRotateActorCommand.h
#pragma once

#include "UTBBaseCommand.h"
#include "MyRotateActorCommand.generated.h"

UCLASS(Blueprintable)
class UMyRotateActorCommand : public UUTBBaseCommand
{
    GENERATED_BODY()

public:
    UMyRotateActorCommand();

    virtual void Execute() override;

private:
    UPROPERTY(EditAnywhere, Category="Rotation")
    float YawDegrees = 90.0f;
};
```

```cpp
// MyRotateActorCommand.cpp
#include "MyRotateActorCommand.h"
#include "Editor.h"

UMyRotateActorCommand::UMyRotateActorCommand()
{
    Name = TEXT("Rotate Selected");
    Tooltip = TEXT("Rotates selected actors by the specified yaw angle.");
    Category = TEXT("Transform");
}

void UMyRotateActorCommand::Execute()
{
    // 获取编辑器当前选择
    USelection* SelectedActors = GEditor->GetSelectedActors();
    if (!SelectedActors) return;

    // 迭代所有选中的Actor
    for (FSelectionIterator It(*SelectedActors); It; ++It)
    {
        AActor* Actor = Cast<AActor>(*It);
        if (Actor)
        {
            // 创建旋转量
            FRotator RotationDelta(0.0f, YawDegrees, 0.0f);
            // 应用旋转
            Actor->AddActorWorldRotation(RotationDelta);
            // 标记需要保存
            Actor->Modify();
        }
    }
}
```

## 模块依赖

该插件依赖于以下核心和编辑器插件：

| 模块 | 用途 |
|---|---|
| `UserToolBoxCore` | 命令系统基础框架，提供 `UUTBBaseCommand` 基类和工具箱UI管理。 |
| `EditorScriptingUtilities` | 提供编辑器专用的蓝图/C++脚本功能，如 `UEditorLevelLibrary`。 |
| `DatasmithContent` | 与Datasmith导入流程相关的类型和功能，用于处理导入资产。 |
| `GeometryScripting` | 几何体脚本操作，可能用于 `UMerge` 等网格处理命令。 |

**使用者注意**：如果你要基于此插件开发，你的 `Build.cs` 文件需要包含对上述插件模块（特别是 `UserToolBoxBasicCommand` 和 `UserToolBoxCore`）的依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志输出宏从 UE_LOG 迁移至 UE_LOGF，跟随引擎更新。 |
| 2026-02-04 | `80b637db` | Fixed printf format specifiers. | 修复了 printf 格式说明符，解决潜在编译或运行时问题。 |
| 2025-03-05 | `7ab43c2f` | Add and address deprecation warning after UEditorInteractiveToolsContext classes move to UnrealEd. | 处理了因工具类移动而产生的废弃警告，保持代码兼容性。 |
| 2025-02-04 | `98d40fea` | Add an actor filter and new usertoolbox command to support automobile import issue. | 增加了新的Actor过滤器和命令，以支持汽车资产导入的特定问题。 |
| 2025-01-23 | `2c03c908` | Avoid dirtying the level when isolating an actor. | 优化了隔离Actor功能，避免意外将场景标记为“已修改”。 |

### 维护评价

该插件创建于 **2023年初**，属于实验性插件（`IsExperimentalVersion=true`），默认未启用。从提交历史看，它在 **2025年仍有功能性更新**（如增加过滤器），表明在**维护中**。最后一次实质性代码改动在 **2025年3月**，之后主要是编译适配和日志优化。

**总结**：这是一个**稳定但处于维护期**的实验性插件。它提供了丰富且实用的编辑器命令，是 `UserToolBoxCore` 的重要配套。虽然不建议用于生产环境的核心功能，但对于构建内部工具、编辑器扩展或学习UE编辑器工具开发模式非常有价值。考虑到其实验性质和最后更新时间，使用时需留意未来版本中可能出现的接口变更或废弃。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UserToolBoxBasicCommand)
- 官方文档（无）
- 测试用例（无独立测试目录）