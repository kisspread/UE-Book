# Code View

> Provides an in-editor code view of game classes and structures with direct IDE accessibility

| 属性 | 值 |
|---|---|
| 中文名 | 代码导航视图 |
| 分类 | Programming |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CodeView` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-08-14 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CodeView) | |

## 用途

Code View 提供一个嵌入在编辑器中的 **C++ 类和函数结构树**，允许开发者浏览当前项目中的游戏类、结构体及其成员函数，并直接跳转到对应的 IDE 中（如 Visual Studio、Rider）打开源代码文件。它解决了在编辑器内快速导航 C++ 代码的需求，避免频繁切换到外部 IDE 查找类定义。

该插件主要服务于 **C++ 游戏开发**，尤其适合大型项目中需要快速查看类层次和函数签名的场景。

## 使用场景

- 你在开发一个基于 C++ 的 UE 项目，需要快速跳转到某个 Actor 或 Component 的头文件或实现文件。
- 你想在编辑器中直观地查看当前项目所有蓝图可覆盖的虚函数或公开方法。
- 作为代码审查或教学工具，展示类结构与函数列表。

## 蓝图用法

Code View 是纯编辑器工具，**不提供任何公开的蓝图节点**。所有交互均通过编辑器界面完成。

## C++ 用法

### 头文件引入

```cpp
#include "SCodeView.h"
```

### 基本用法

创建 `SCodeView` 实例并添加到编辑器窗口。通常由插件模块在启动时注册到菜单或面板。

```cpp
// 在你的编辑器模块中
TSharedRef<SWidget> CreateCodeViewWidget()
{
    return SNew(SCodeView);
}
```

### 进阶用法

`SCodeView` 内部使用 `STreeView` 显示树形结构，节点类型为 `CodeView::FTreeItem` 的子类（`FClassTreeItem` 和 `FFunctionTreeItem`）。你可以通过 `SetOnTreeItemDoubleClicked` 等委托自定义双击行为，例如调用 `FSourceCodeNavigation::OpenSourceFile()` 跳转到 IDE。

```cpp
// 注册自定义导航
MyCodeView->SetOnTreeItemDoubleClicked(FOnTreeItemDoubleClicked::CreateLambda(
    [](TSharedPtr<CodeView::FTreeItem> Item)
    {
        if (Item->GetType() == CodeView::ETreeItemType::Class)
        {
            auto ClassItem = StaticCastSharedPtr<CodeView::FClassTreeItem>(Item);
            FSourceCodeNavigation::OpenSourceFile(ClassItem->AnyFunctionSymbolName);
        }
    }));
```

## Demo 示例

### 最小插件模块示例

以下是一个独立编辑器模块，演示如何将 `SCodeView` 注册到编辑器菜单中。

**CodeViewDemo.h**
```cpp
#pragma once
#include "Modules/ModuleInterface.h"

class FCodeViewDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**CodeViewDemo.cpp**
```cpp
#include "CodeViewDemo.h"
#include "SCodeView.h"
#include "Framework/MultiBox/MultiBoxBuilder.h"
#include "LevelEditor.h"

void FCodeViewDemoModule::StartupModule()
{
    // 注册到 LevelEditor 的菜单项
    FLevelEditorModule& LevelEditor = FModuleManager::LoadModuleChecked<FLevelEditorModule>("LevelEditor");
    TSharedPtr<FExtender> ToolbarExtender = MakeShareable(new FExtender());
    ToolbarExtender->AddToolBarExtension("Game", EExtensionHook::After, nullptr,
        FToolBarExtensionDelegate::CreateLambda([](FToolBarBuilder& Builder)
        {
            Builder.AddWidget(
                SNew(SButton)
                .Text(INVTEXT("Open Code View"))
                .OnClicked_Lambda([]() -> FReply
                {
                    // 创建并显示 Code View 窗口
                    TSharedRef<SWindow> Window = SNew(SWindow)
                        .Title(INVTEXT("Code View"))
                        .ClientSize(FVector2D(400, 600))
                        .Content()
                        [
                            SNew(SCodeView)
                        ];
                    FSlateApplication::Get().AddWindow(Window);
                    return FReply::Handled();
                }),
                INVTEXT("CodeView")
            );
        }));
    LevelEditor.GetToolBarExtensibilityManager()->AddExtender(ToolbarExtender);
}

void FCodeViewDemoModule::ShutdownModule()
{
    // 清理（略）
}

IMPLEMENT_MODULE(FCodeViewDemoModule, CodeViewDemo);
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate/UnrealEd 等） | – |

该插件为纯编辑器插件，所需的 Slate、UnrealEd 等为常见编辑器依赖。

## 维护状态

### 近期更新

- 2023-11-20 `763a6119` Fix C4072 warnings  
- 2023-01-16 `bbc37aa2` [Engine/Plugins]  
- 2022-10-21 `610c4676` Update vendor links for built-in plugins to use secure protocol.  
- 2022-05-09 `6248f8d4` Replacing legacy EditorStyle calls with AppStyle  
- 2020-08-14 `48113fc7` Adding EditorFramework to build.cs files  

### 维护评价

- **创建时间**：2020-08-14，距今约 5 年。  
- **活跃度**：最近一次更新为 2023 年 11 月的编译警告修复，近一年无功能性更新。  
- **状态**：维护不活跃，但仍在 UE5 标准发行版中（非弃用）。  
- **已知限制**：插件名称“Experimental”暗示其仍处于实验阶段，功能较为基础，可能不支持所有 UE 类结构（如 UBlueprint 生成的类）。  
- **推荐度**：对于需要快速 IDE 导航的 C++ 项目有一定价值，但注意它是实验性的，未来可能被移除或整合到其他工具中。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CodeView)