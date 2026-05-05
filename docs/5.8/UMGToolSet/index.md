# UMG ToolSet

> AI assistant tools for creating and manipulating UMG widgets via reflection.

| 属性 | 值 |
|---|---|
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UMGToolSet` (EditorNoCommandlet) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-14 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/UMGToolSet) | |

## 用途

UMGToolSet 是一个为 AI 助手设计的工具集插件。它通过 Unreal Engine 的反射系统，为 AI 提供了一套标准化的函数（工具），使其能够以编程方式理解、创建和操作 UMG（Unreal Motion Graphics）控件蓝图。

这个插件解决的核心问题是：**如何让 AI 助手能够像人类开发者一样与 UMG 系统交互**。它抽象了 UMG 控件的创建、属性查询与设置、层次结构管理等复杂操作，将其封装成 AI 可以调用的“工具”。这使得 AI 能够辅助或自动化 UI 的搭建、修改和调试过程。

## 使用场景

- **AI 辅助 UI 开发**：你正在使用一个 AI 编程助手（如基于大语言模型的工具），希望它能根据你的自然语言描述（例如“创建一个包含标题和图片的垂直布局”）直接生成对应的 UMG 控件层次结构。
- **自动化 UI 测试生成**：你需要为复杂的 UI 界面生成测试用例，AI 可以利用此工具集遍历现有 UI 结构或创建特定结构的 UI 用于测试。
- **UI 原型快速迭代**：在概念验证阶段，希望通过 AI 快速生成和调整 UI 布局，而无需手动在编辑器中拖拽。

## 蓝图用法

该插件主要为 AI 工具链提供后端支持，其核心函数通常不直接在用户蓝图中调用，而是由 AI 助手框架（如 `ToolsetRegistry`）调用。然而，其定义的数据结构和函数是理解其能力的关键。

### 核心数据结构

| 结构体 | 说明 |
|---|---|
| `FUMGWidgetInfo` | 描述一个 UMG 控件的完整信息，包括控件实例、父级、插槽、所属命名槽宿主、类路径、名称以及是否为变量、是否继承等。这是所有查询和创建操作的主要返回类型。 |
| `FUMGNamedSlotEntry` | 描述一个命名槽的绑定信息，包括槽名和内容控件。 |

### 核心功能节点（概念）

基于源码注释和结构体设计，插件提供的工具函数可能包括：

| 功能 | 说明 | 所在类/结构 |
|---|---|---|
| **查询控件** | 获取指定控件蓝图中的所有控件信息（`FUMGWidgetInfo` 列表）。 | `UUMGToolSet` (推断) |
| **创建控件** | 在指定的父控件（`UPanelWidget`）下创建一个新的指定类的控件。 | `UUMGToolSet` (推断) |
| **设置属性** | 通过反射设置控件或其插槽（`UPanelSlot`）的属性值。 | `UUMGToolSet` (推断) |
| **获取命名槽** | 获取控件蓝图中所有命名槽及其当前内容。 | `UUMGToolSet` (推断) |
| **设置命名槽内容** | 将指定控件设置为某个命名槽的内容。 | `UUMGToolSet` (推断) |

### 使用示例（AI 工具调用流程描述）

1.  **AI 调用 `查询控件`**：传入一个 `UWidgetBlueprint` 对象，获取其根控件及所有子控件的 `FUMGWidgetInfo` 列表。
2.  **AI 分析 `FUMGWidgetInfo`**：通过 `WidgetClassPath` 了解控件类型，通过 `Parent` 和 `Slot` 理解层次关系，通过 `bIsVariable` 判断是否可被蓝图变量引用。
3.  **AI 调用 `创建控件`**：传入一个父控件的 `FUMGWidgetInfo.Widget`（作为 `UPanelWidget`）和一个控件类路径（如 `UVerticalBox::StaticClass()`），创建新控件并获得其 `FUMGWidgetInfo`。
4.  **AI 调用 `设置属性`**：使用 `ObjectTools`（来自另一个工具集）配合新控件的 `FUMGWidgetInfo.Widget` 或 `FUMGWidgetInfo.Slot`，设置其具体属性（如 `Text`、`Padding`、`Brush` 等）。

## C++ 用法

该插件的 C++ 接口主要面向工具集开发者和测试。以下示例展示了如何定义具有 `BindWidget` 要求的控件父类，这是 UMG 工具集需要处理的一种典型场景。

### 头文件引入

```cpp
#include "UMGToolSet.h" // 主要工具集头文件
#include "Blueprint/UserWidget.h"
```

### 基本用法：定义带 BindWidget 的测试控件

此示例来自测试夹具，展示了如何创建一个 C++ 基类，其中包含必须或可选绑定到子蓝图控件的属性。UMG 工具集在操作继承此类的蓝图时，需要理解这些约束。

```cpp
// 来源: Engine/Plugins/Experimental/Toolsets/UMGToolSet/Source/UMGToolSet/Private/Tests/UMGToolSetTestFixtures.h
UCLASS()
class UUMGTestWidgetWithBindings : public UUserWidget
{
    GENERATED_BODY()

public:
    /** 必需的 BindWidget — 如果子蓝图中缺失，编译将报错。 */
    UPROPERTY(meta = (BindWidget))
    TObjectPtr<UTextBlock> RequiredText = nullptr;

    /** 必需的 BindWidget — 如果子蓝图中缺失，编译将报错。 */
    UPROPERTY(meta = (BindWidget))
    TObjectPtr<UImage> RequiredImage = nullptr;

    /** 可选的 BindWidget — 编译器会提示，但不会报错。 */
    UPROPERTY(meta = (BindWidgetOptional))
    TObjectPtr<UImage> OptionalIcon = nullptr;

    /** 普通属性（非 BindWidget），用于名称冲突测试。 */
    UPROPERTY()
    TObjectPtr<UWidget> InternalRef = nullptr;
};
```

### 进阶用法：理解 FUMGWidgetInfo 的层次上下文

`FUMGWidgetInfo` 的 `Parent`、`Slot` 和 `NamedSlotHost` 字段共同定义了控件在 UI 树中的位置。在编写工具函数或测试时，需要正确处理这些关系。

```cpp
// 概念性代码，展示如何解读 FUMGWidgetInfo
void AnalyzeWidgetInfo(const FUMGWidgetInfo& Info)
{
    if (Info.Parent == nullptr && Info.NamedSlotHost == nullptr)
    {
        // 这是根控件
    }
    else if (Info.NamedSlotHost != nullptr)
    {
        // 这是一个命名槽的内容控件
        // 要修改它的位置，应使用 SetNamedSlotContent 工具，而不是 AddWidget
        UWidget* Host = Info.NamedSlotHost;
        // ... 获取 Host 的命名槽列表并操作
    }
    else if (Info.Parent != nullptr)
    {
        // 这是一个普通子控件，其插槽信息在 Info.Slot 中
        UPanelSlot* Slot = Info.Slot;
        // 可以通过反射设置 Slot 的 Padding, Alignment 等属性
    }

    if (Info.bInherited)
    {
        // 此控件定义在 C++ 父类中，AI 工具可能不应删除或重命名它
    }
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，模拟了 AI 工具集可能执行的一个操作：创建一个垂直盒子并为其添加一个文本块。

```cpp
// MyUITool.h
#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "UMGToolSet.h" // 包含 FUMGWidgetInfo 等结构
#include "MyUITool.generated.h"

UCLASS()
class UMyUITool : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    /** 模拟一个 AI 工具：创建简单的垂直布局。 */
    UFUNCTION(BlueprintCallable, Category = "AI|UMG")
    static FUMGWidgetInfo CreateSimpleVerticalLayout(UWidgetBlueprint* TargetBlueprint);
};

// MyUITool.cpp
#include "MyUITool.h"
#include "Components/VerticalBox.h"
#include "Components/TextBlock.h"
#include "Engine/Blueprint.h"
#include "Kismet2/BlueprintEditorUtils.h"

FUMGWidgetInfo UMyUITool::CreateSimpleVerticalLayout(UWidgetBlueprint* TargetBlueprint)
{
    FUMGWidgetInfo Result;
    if (!TargetBlueprint) return Result;

    // 1. 创建垂直盒子作为根控件 (概念性调用，实际需通过工具集API)
    // UVerticalBox* VerticalBox = CreateWidget<UVerticalBox>(...);
    // Result.Widget = VerticalBox;
    // Result.WidgetClassPath = UVerticalBox::StaticClass();
    // Result.WidgetName = FName("RootVerticalBox");

    // 2. 创建文本块作为子控件
    // UTextBlock* TextBlock = CreateWidget<UTextBlock>(...);
    // FUMGWidgetInfo ChildInfo;
    // ChildInfo.Widget = TextBlock;
    // ChildInfo.Parent = VerticalBox; // 设置父级
    // ChildInfo.WidgetClassPath = UTextBlock::StaticClass();
    // ChildInfo.WidgetName = FName("TitleText");

    // 3. 设置文本块属性 (概念性调用 ObjectTools)
    // ObjectTools::SetProperties(TextBlock, {{"Text", FText::FromString("Hello AI")}});

    // 4. 将文本块添加到垂直盒子 (概念性调用 AddWidget 工具)
    // AddWidget(VerticalBox, ChildInfo.WidgetClassPath, ChildInfo.WidgetName);

    // 注意：以上是概念流程。实际实现需要调用 UMGToolSet 模块提供的具体函数。
    // 此示例仅说明工具集可能封装的操作逻辑。
    return Result;
}
```

## 模块依赖

从 `.uplugin` 的 `Plugins` 字段和模块类型推断，使用此插件需要以下依赖：

| 模块 | 用途 |
|---|---|
| `ToolsetRegistry` | 提供工具集注册和发现的框架，UMGToolSet 依赖它来注册自己提供的 AI 工具。 |

## 维护状态

### 近期更新

- `6471b168` 2026-04-18 — [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,.
- `8c911af5` 2026-04-17 — [Backout] - CL52878047
- `9404cd3e` 2026-04-17 — [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,.

### 维护评价

- **状态**：**活跃维护的实验性插件**。
- **分析**：
    1.  **创建时间**：非常新（约 2 年前创建）。
    2.  **更新频率**：最近一周内有多次提交，表明正在积极开发和调整中。
    3.  **更新内容**：近期提交主要围绕“AIAssistant”和“ToolsetDefinitions”的核心机制进行修改和回退，说明该插件处于功能定义和接口稳定的关键阶段。
    4.  **实验性**：`.uplugin` 中明确标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，表明 Epic 将其视为前沿功能，API 和行为可能发生变化。
- **建议**：可以关注和学习其设计思路，但**不建议在生产项目中依赖此插件**。适合用于研究 AI 与 UE 编辑器集成的开发者。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/UMGToolSet)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/UMGToolSet/Source/UMGToolSet/Private/Tests)