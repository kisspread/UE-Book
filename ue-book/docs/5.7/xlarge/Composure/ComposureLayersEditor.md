# Legacy Composure

> Legacy system for real-time compositing. This plugin is no longer developed. Use Composure going forward.

| 属性 | 值 |
|---|---|
| 分类 | Compositing |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `Composure` (Runtime), `ComposureEditor` (Runtime), `ComposureLayersEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-06-27 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Compositing/Composure) | |

## 用途

Composure 是 Unreal Engine 中用于**实时合成**的旧版插件系统。它提供了一个框架，允许开发者在编辑器中创建和管理合成元素（Compositing Elements），这些元素可以代表不同的视觉层（如背景、前景、特效、抠像等），并将它们实时合成到最终画面中。该插件的核心目标是简化虚拟制片和实时视觉特效工作流，使艺术家能够在编辑器中直接预览和调整合成效果。

**重要提示**：根据 `.uplugin` 的描述，此插件已被标记为“Legacy”（旧版），Epic Games 已停止对其开发。官方建议使用新的 `Composure` 插件（可能指代更新的版本或替代方案）。因此，本文档主要用于理解旧有项目或迁移参考。

## 使用场景

- **虚拟制片 (Virtual Production)**：在 LED 墙或绿幕前拍摄时，实时合成背景、前景元素和特效。
- **实时视觉特效 (Real-time VFX)**：在游戏或应用运行时，动态合成多个渲染层以创建复杂的视觉效果。
- **编辑器内合成预览**：在编辑器中搭建合成节点图，实时预览最终输出，无需打包运行。
- **旧项目维护**：维护或理解使用此旧版 Composure 系统的现有项目。

## 蓝图用法

由于此插件主要提供 C++ 运行时和编辑器模块，其核心功能通过 C++ 接口暴露。蓝图中可直接使用的节点相对有限，更多是通过编辑器 UI 或 C++ 代码进行操作。以下是从提供的头文件中推断出的、可能通过蓝图或编辑器扩展暴露的核心管理功能。

### 核心节点（通过编辑器模块接口）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateElement` | 在指定关卡中创建一个新的合成元素 Actor。 | `ICompElementManager` |
| `GetElement` | 根据名称获取一个已存在的合成元素 Actor。 | `ICompElementManager` |
| `DeleteElementAndChildren` | 删除指定的合成元素及其所有子元素。 | `ICompElementManager` |
| `RenameElement` | 重命名一个合成元素。 | `ICompElementManager` |
| `AttachCompElement` | 将一个合成元素附加为另一个元素的子元素。 | `ICompElementManager` |

### 使用示例（蓝图描述）

由于核心管理接口 (`ICompElementManager`) 是一个纯 C++ 接口，通常不直接在蓝图图表中调用。其操作主要通过以下方式触发：
1.  **编辑器 UI**：在 Composure 编辑器面板中，通过右键菜单或工具栏按钮执行创建、删除、重命名等操作。
2.  **C++ 代码**：在自定义的编辑器工具或运行时逻辑中，通过获取 `ICompElementEditorModule` 单例来访问管理器并执行操作。
3.  **蓝图编辑器工具**：如果插件提供了相应的蓝图函数库（Blueprint Function Library），则可能在蓝图中调用。但根据提供的代码片段，未发现此类公开的蓝图函数。

## C++ 用法

### 头文件引入

```cpp
#include "CompElementEditorModule.h"
#include "ICompElementManager.h"
```

### 基本用法

以下示例展示了如何在编辑器工具或自定义模块中获取合成元素管理器并执行基本操作。

```cpp
// 来源：基于 Engine/Plugins/Compositing/Composure/Source/ComposureLayersEditor/Public/CompElementEditorModule.h 和 ICompElementManager.h 的用法推断

// 1. 获取编辑器模块实例
ICompElementEditorModule& EditorModule = ICompElementEditorModule::Get();

// 2. 获取元素管理器
TSharedPtr<ICompElementManager> ElementManager = EditorModule.GetCompElementManager();
if (ElementManager.IsValid())
{
    // 3. 创建一个新的合成元素
    FName NewElementName = TEXT("MyBackground");
    TWeakObjectPtr<ACompositingElement> NewElement = ElementManager->CreateElement(
        NewElementName,
        ACompositingElement::StaticClass(), // 使用默认的合成元素类
        nullptr, // 在当前关卡上下文中创建
        RF_NoFlags
    );

    if (NewElement.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("成功创建合成元素: %s"), *NewElementName.ToString());
    }

    // 4. 获取一个已存在的元素
    TWeakObjectPtr<ACompositingElement> ExistingElement = ElementManager->GetElement(TEXT("ExistingElementName"));
    if (ExistingElement.IsValid())
    {
        // 对元素进行操作...
    }

    // 5. 删除一个元素及其子元素
    ElementManager->DeleteElementAndChildren(TEXT("ElementToDelete"));
}
```

### 进阶用法

管理器还提供了更复杂的操作，如批量操作、附加/分离元素以及使用过滤器。

```cpp
// 来源：基于 ICompElementManager.h 中的接口定义

// 获取所有元素
TArray<TWeakObjectPtr<ACompositingElement>> AllElements;
ElementManager->AddAllCompElementsTo(AllElements);

// 重命名一个元素
bool bRenamed = ElementManager->RenameElement(TEXT("OldName"), TEXT("NewName"));

// 将元素“ChildElement”附加为“ParentElement”的子元素
bool bAttached = ElementManager->AttachCompElement(TEXT("ParentElement"), TEXT("ChildElement"));

// 使用过滤器（需要实现 IFilter<const TWeakObjectPtr<AActor>&>）
// 例如，可以创建一个过滤器来只获取特定类型的元素。
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何在编辑器模块中集成 Composure 元素管理功能。

```cpp
// MyComposureTool.h
#pragma once

#include "CoreMinimal.h"

class FMyComposureTool
{
public:
    void CreateAndLogElement();
};
```

```cpp
// MyComposureTool.cpp
#include "MyComposureTool.h"
#include "CompElementEditorModule.h"
#include "ICompElementManager.h"
#include "CompositingElement.h" // 假设的头文件，用于 ACompositingElement

void FMyComposureTool::CreateAndLogElement()
{
    ICompElementEditorModule& EditorModule = ICompElementEditorModule::Get();
    TSharedPtr<ICompElementManager> Manager = EditorModule.GetCompElementManager();

    if (!Manager.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("无法获取合成元素管理器。"));
        return;
    }

    const FName ElementName = FName(*FString::Printf(TEXT("DemoElement_%d"), FDateTime::Now().GetMillisecond()));
    TWeakObjectPtr<ACompositingElement> Element = Manager->CreateElement(
        ElementName,
        ACompositingElement::StaticClass()
    );

    if (Element.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("成功创建演示元素: %s"), *ElementName.ToString());
        // 可以在这里对 Element 进行进一步配置
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("创建元素失败: %s"), *ElementName.ToString());
    }
}
```

## 模块依赖

从 `ComposureLayersEditor` 模块的 `Build.cs` 文件推断，其依赖关系如下。由于这是编辑器模块，它依赖于核心编辑器框架。

| 模块 | 用途 |
|---|---|
| `Composure` | 提供核心的运行时合成元素类和数据结构。 |
| `UnrealEd` | 提供编辑器基础框架、资产编辑器、关卡编辑器等功能。 |
| `PropertyEditor` | 用于在细节面板中自定义属性编辑界面。 |
| `Slate`, `SlateCore` | 用于构建编辑器 UI。 |
| `InputCore` | 处理编辑器输入。 |

**注意**：`Composure` 运行时模块本身可能依赖于 `Core`, `CoreUObject`, `Engine`, `RenderCore`, `RHI` 等底层渲染和引擎模块，但这些属于常见依赖，按规范省略。

## 维护状态

### 近期更新

```
- ca898522c1ec Composite: Preliminary renaming of display/friendly names to recycle Composure branding.
- d6a12ef6a0c3 Making UClass::ClassDefaultObject private.
- 3ee47591962e [Backout] - CL40449780 [FYI] Robert.Manuszewski #rnx Original CL Desc ----------------------------------------------------------------- Making UClass::ClassDefaultObject private.
```

**解读**：
- 最近的提交 (`ca98522`) 是关于重命名的准备工作，可能与新旧系统过渡有关。
- 后续两个提交 (`d6a12ef`, `3ee4759`) 是关于引擎核心类 `UClass` 的访问权限修改，属于底层引擎改动，并非针对 Composure 插件的功能性更新。

### 维护评价

**综合评价：不推荐用于新项目。**

1.  **官方状态**：`.uplugin` 明确声明此插件为“Legacy”且“no longer developed”，并指引用户使用新的“Composure”。这是最强烈的废弃信号。
2.  **更新频率**：从提供的 git 历史看，近期的提交均为底层引擎适配或重命名准备，没有针对插件本身的功能增强或重要错误修复。这表明该插件已进入维护冻结状态。
3.  **年龄**：插件创建于 2017 年，已有约 8 年历史，在快速发展的实时图形领域属于“老古董”。
4.  **建议**：
    - **新项目**：绝对不要使用此插件。请寻找并使用 Epic Games 官方推荐的新版合成系统。
    - **旧项目维护**：如果现有项目深度依赖此插件，可以继续使用，但应计划向新系统迁移。注意，未来引擎版本升级可能会移除此插件。
    - **学习参考**：可以研究其架构和代码，以理解实时合成系统的设计思路，但不要直接用于生产。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Compositing/Composure)
- [官方文档]() (无)
- [测试用例]() (未在提供的路径中发现标准测试文件)