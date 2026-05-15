# UMG ToolSet

> AI assistant tools for creating and manipulating UMG widgets via reflection.

| 属性 | 值 |
|---|---|
| 中文名 | UMG工具集 |
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UMGToolSet` (Editor) |
| 实验性 | ⚚ 是 |
| 创建时间 | 2026-04-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/UMGToolSet) | |

## 用途

UMGToolSet 是一套面向 AI 编程助手的编辑器专用工具集。它通过提供一系列 `UFUNCTION(BlueprintCallable, meta=(AICallable))` 标记的静态函数，使 AI 助手能够完全程序化地操作 Unreal Motion Graphics (UMG) 控件蓝图的创建、查询、修改和编译全流程。

该插件的核心价值在于解决了 AI 助手无法直接在 UMG 可视化编辑器中“看到”和“拖拽”控件的问题。它为 AI 提供了一套底层、确定性的 API，让 AI 能够：
1.  **创建资产**：从零开始创建控件蓝图。
2.  **构建控件树**：程序化地向蓝图中添加、移动、移除、重命名控件。
3.  **查询状态**：获取完整的控件树结构、属性详情和命名插槽信息。
4.  **执行修改**：操作控件变量、绑定事件、替换控件、包装控件。
5.  **完成生命周期**：编译蓝图并处理错误。

简而言之，它是 AI 驱动 UI 生成的“手”和“眼”。

## 使用场景

-   **AI 驱动的 UI 生成工具**：您正在开发一个 AI 助手，该助手需要根据自然语言描述或设计稿，自动生成复杂的 UMG 控件蓝图。本插件提供了底层的创建和操控能力。
-   **自动化 UI 测试**：您需要编写自动化测试用例，程序化地创建和修改 UMG 控件，以验证 UI 逻辑或布局。
-   **脚本化 UI 工作流**：您希望用脚本（通过 AI 或手动调用）批量处理或标准化大量 UMG 资产，例如批量更新某个控件的属性或结构。

## 蓝图用法

所有函数均标记为 `AICallable`，主要面向 AI 代理调用，但也可在编辑器工具蓝图或脚本中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateWidgetBlueprint` | 在指定内容路径创建一个新的控件蓝图资产。 | `UUMGToolSet` |
| `AddWidget` | 向控件树中的指定父面板添加一个新的控件实例。 | `UUMGToolSet` |
| `GetWidgets` | 以深度优先顺序返回整个控件树的完整信息（控件、槽、父级关系等）。 | `UUMGToolSet` |
| `SetNamedSlotContent` | 将指定控件填充到宿主控件的命名插槽中。 | `UUMGToolSet` |
| `MoveWidget` | 将一个控件移动到新的父面板和子索引位置。 | `UUMGToolSet` |
| `RemoveWidget` | 从控件树中移除指定控件及其所有子控件。 | `UUMGToolSet` |
| `RenameWidget` | 重命名一个控件实例。 | `UUMGToolSet` |
| `ToggleWidgetAsVariable` | 切换控件的 `bIsVariable` 标志，决定其是否暴露为蓝图变量。 | `UUMGToolSet` |
| `BindToEventProperty` | 为控件的多播委托事件（如按钮的 `OnClicked`）创建一个蓝图事件处理器图节点。 | `UUMGToolSet` |
| `WrapWidgets` | 将选中的一个或多个控件包装在一个新的指定类别的面板控件中。 | `UUMGToolSet` |
| `ReplaceWidgetWithTemplate` | 用另一个模板类替换控件树中的某个控件，并尝试保留兼容的引用。 | `UUMGToolSet` |
| `GetWidgetDescription` | 获取控件树的详细属性描述文本，用于调试和理解结构。 | `UUMGToolSet` |
| `AddUIComponent` | 向指定控件添加一个 UI 组件。 | `UUMGToolSet` |
| `CompileWidgetBlueprint` | 编译控件蓝图，并报告包括缺失的 `BindWidget` 在内的所有错误。 | `UUMGToolSet` |

### 使用示例（蓝图描述）

1.  **创建并构建一个简单的 UI**：
    -   调用 `CreateWidgetBlueprint` 创建 `“/Game/UI”` 路径下的 `“WBP_MainMenu”`。
    -   调用 `AddWidget`，传入上一步返回的蓝图、`UVerticalBox` 类和 `“RootBox”` 名称，将其设为根控件。
    -   再次调用 `AddWidget`，父控件传入 `RootBox`，控件类选择 `UButton`，名称为 `“StartButton”`。
    -   调用 `GetWidgets` 查看构建结果。
    -   最后调用 `CompileWidgetBlueprint` 编译蓝图，并检查返回的布尔值确认是否成功。

2.  **查询并修改现有控件**：
    -   使用 `ListWidgetBlueprints` 或资产路径加载一个现有的 `UWidgetBlueprint`。
    -   调用 `GetWidgets` 获取整个控件树信息，其中每个 `FUMGWidgetInfo` 都包含 `Widget` 指针。
    -   对感兴趣的控件（如某个 `UTextBlock`），将其 `Widget` 指针传给 `ObjectTools` 的 `list_properties` 和 `set_properties` 节点来修改其文本、颜色等属性。
    -   使用 `MoveWidget` 调整控件在树中的位置。

## C++ 用法

该插件主要面向蓝图和 AI 系统，其核心类 `UUMGToolSet` 的函数均为静态函数，且标记为 `AICallable`。在 C++ 中直接使用的场景较少，更多是作为底层服务被调用。

### 头文件引入

```cpp
// 如果您的模块需要依赖此插件，需要在 .h 中包含其公开头文件
#include "UMGToolSetModule.h"
// 主要的类定义在私有头文件中，通常不直接包含，而是通过函数调用
// #include “UMGToolSet.h” // 私有
```

### 基本用法（模拟 AI 调用流程）

在编辑器工具或测试代码中，您可以像 AI 一样调用这些静态函数。

```cpp
// 假设您已经有了一个 UWidgetBlueprint 指针（WidgetBlueprint）
// 创建一个新的按钮控件并添加到根控件下
FUMGWidgetInfo NewButtonInfo = UUMGToolSet::AddWidget(
    WidgetBlueprint,
    UButton::StaticClass(), // TSubclassOf<UWidget>
    TEXT(“MyNewButton”),
    nullptr, // ParentWidget = nullptr 表示添加到根或空树
    -1       // ChildIndex = -1 表示追加到末尾
);

if (NewButtonInfo.Widget.IsValid())
{
    // 成功创建，现在可以通过 ObjectTools 设置按钮的属性
    // ... 调用 ObjectTools 系列函数 ...
}
```

### 进阶用法（从测试用例推断）

从测试夹具文件 `UMGToolSetTestFixtures.h` 可以看出，该插件主要用于验证各种边界情况，例如 `BindWidget` 的绑定。

```cpp
// 模拟测试一个带有 BindWidget 的父类
// 1. 创建一个继承自 UUMGTestWidgetWithBindings 的控件蓝图
UWidgetBlueprint* TestBP = UUMGToolSet::CreateWidgetBlueprint(
    TestMountPoint, TEXT(“WBP_TestBindings”),
    UUMGTestWidgetWithBindings::StaticClass()
);

// 2. 为其添加必需的 BindWidget 控件（RequiredText, RequiredImage）
UUMGToolSet::AddWidget(TestBP, UTextBlock::StaticClass(), TEXT(“RequiredText”));
UUMGToolSet::AddWidget(TestBP, UImage::StaticClass(), TEXT(“RequiredImage”));

// 3. 编译，期望成功
bool bSuccess = UUMGToolSet::CompileWidgetBlueprint(TestBP);
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何在一个编辑器命令或工具函数中使用 `UUMGToolSet` 来创建一个简单的控件蓝图。

```cpp
// MinimalUMGToolSetDemo.h
#pragma once

#include “CoreMinimal.h”
#include “Kismet/BlueprintFunctionLibrary.h”
#include “MinimalUMGToolSetDemo.generated.h”

UCLASS()
class UMinimalUMGToolSetDemo : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    /**
     * 创建一个包含垂直盒子和按钮的简单 UMG 控件蓝图。
     * @param SavePath 资产保存路径，例如 “/Game/Demo”
     * @param AssetName 资产名称，例如 “WBP_DemoUI”
     * @return 创建成功返回 true，否则返回 false。
     */
    UFUNCTION(BlueprintCallable, Category=“Demo”)
    static bool CreateSimpleDemoUI(const FString& SavePath, const FString& AssetName);
};
```

```cpp
// MinimalUMGToolSetDemo.cpp
#include “MinimalUMGToolSetDemo.h”
// 包含所需 UMG 控件的头文件
#include “Components/VerticalBox.h”
#include “Components/Button.h”
#include “Components/TextBlock.h”
// 包含 UMGToolSet 的私有头文件以访问其静态函数
// 注意：在实际项目中，通常通过插件接口或全局函数访问，此处为演示简化
#include “Private/UMGToolSet.h”

bool UMinimalUMGToolSetDemo::CreateSimpleDemoUI(const FString& SavePath, const FString& AssetName)
{
    // 1. 创建控件蓝图
    UWidgetBlueprint* NewBlueprint = UUMGToolSet::CreateWidgetBlueprint(
        SavePath, AssetName, UUserWidget::StaticClass()
    );
    if (!NewBlueprint) return false;

    // 2. 添加根垂直盒子
    FUMGWidgetInfo RootBoxInfo = UUMGToolSet::AddWidget(
        NewBlueprint,
        UVerticalBox::StaticClass(),
        TEXT(“RootVBox”)
    );
    if (!RootBoxInfo.Widget.IsValid()) return false;

    // 3. 向垂直盒子中添加一个按钮
    FUMGWidgetInfo ButtonInfo = UUMGToolSet::AddWidget(
        NewBlueprint,
        UButton::StaticClass(),
        TEXT(“DemoButton”),
        Cast<UWidget>(RootBoxInfo.Widget.Get()), // 指定父控件为 RootVBox
        0 // 作为第一个子项
    );
    if (!ButtonInfo.Widget.IsValid()) return false;

    // 4. 向按钮中添加文本块
    FUMGWidgetInfo TextInfo = UUMGToolSet::AddWidget(
        NewBlueprint,
        UTextBlock::StaticClass(),
        TEXT(“ButtonText”),
        Cast<UWidget>(ButtonInfo.Widget.Get()) // 指定父控件为 DemoButton
    );
    if (!TextInfo.Widget.IsValid()) return false;

    // 5. 编译蓝图
    return UUMGToolSet::CompileWidgetBlueprint(NewBlueprint);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ToolsetRegistry` | 提供 `UToolsetDefinition` 基类和工具集注册框架，本插件的 `UUMGToolSet` 继承自它。 |
| `UMGEditor` | 提供 `UWidgetBlueprint` 及其编辑器操作的核心功能。 |
| `AssetTools` | 用于资产的创建、保存等操作（通过 `ObjectTools` 等工具集间接依赖）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `6611dd10` | Main implementation for UE-373928 | 实现了 UE-373928 的主要功能，为 Wrap 和 Replace 等操作添加了核心逻辑。 |
| 2026-05-13 | `dca1fade` | WidgetBlueprintOperationUtils: remove overloads for Wrap and Replace functions | 重构了工具函数，移除了 Wrap 和 Replace 功能的冗余重载版本，简化了接口。 |
| 2026-05-12 | `21f108ac` | Cherry-pick UMGToolSet | 将 UMGToolSet 插件从开发分支精选到当前分支。 |
| 2026-04-18 | `6471b168` | [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools | 调整了 AI 助手识别工具函数的方式，可能影响 `AICallable` 函数的暴露规则。 |
| 2026-04-17 | `8c911af5` | [Backout] - CL52878047 | 回滚了之前的某次提交。 |

### 维护评价

-   **创建时间**：该插件于 2026 年 4 月初创建，是一个非常新的功能。
-   **活跃度**：从 git 历史看，近期（5月）有频繁的功能提交和重构，表明正处于**活跃开发**阶段。
-   **状态**：插件明确标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，属于**实验性功能**，API 和行为可能在未来发生变化。
-   **推荐度**：如果您正在构建 **AI 驱动的 UI 工具链**，并且愿意接受实验性 API 的变动，那么本插件是目前唯一且核心的选择。对于普通的 UMG 开发，无需关注此插件。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/UMGToolSet)
-   [官方文档]() (无)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/UMGToolSet/Source/UMGToolSet/Private/Tests)