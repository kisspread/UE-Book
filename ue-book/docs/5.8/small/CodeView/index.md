# Code View

> Provides an in-editor code view of game classes and structures with direct IDE accessibility

| 属性 | 值 |
|---|---|
| 中文名 | 代码视图 |
| 分类 | Programming |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CodeView` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CodeView) | |

## 用途
该插件提供了一个编辑器内的 Slate 控件（`SCodeView`），用于以树状结构显示当前场景中选中 Actor 所属的 C++ 类及其成员函数。它的核心目的是增强编辑器内的代码可读性和导航效率，允许开发者在不离开编辑器的情况下快速浏览游戏类的代码结构，并能直接跳转到 IDE 中的相应源文件。这解决了开发者在编辑器和外部代码编辑器之间频繁切换以查看类定义的痛点。

## 使用场景
- 你在场景中选中了一个 Actor，想要快速查看其 C++ 类的结构（包括父类、成员函数），而无需打开头文件。
- 你需要在编辑器中快速定位某个类的某个方法在源代码中的位置，并通过双击直接在 IDE 中打开。
- 你希望在编辑器内提供一个轻量级的、可搜索的代码结构浏览器。

## 蓝图用法
该插件主要提供编辑器 Slate UI，没有公开暴露给蓝图的 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。其核心功能是作为编辑器面板的一个组成部分存在。

## C++ 用法
### 头文件引入
该插件主要提供一个 Slate 控件，其使用依赖于对 Slate 框架的理解。
```cpp
// 核心头文件位于 Private 目录下
#include "SCodeView.h"
```
### 基本用法
`SCodeView` 是一个 Slate 控件，通常由编辑器模块（如 Details 面板自定义）创建和嵌入。你需要为它提供一个获取当前选中 Actor 的委托。

```cpp
// 假设你正在一个编辑器面板中添加代码视图
// （这是一个概念性示例，实际集成方式取决于具体的编辑器扩展点）

// 创建获取选中 Actor 的委托
FGetSelectedActors GetSelectedActorsDelegate = FGetSelectedActors::CreateLambda([]()
{
    // 返回当前编辑器中选中的Actor列表
    return GEditor->GetSelectedActors();
});

// 使用 Slate 宏创建 SCodeView 控件
TSharedRef<SCodeView> CodeViewWidget = SNew(SCodeView)
    .GetSelectedActors(GetSelectedActorsDelegate);

// 将控件添加到你的 Slate 布局中，例如一个 SDetailSection 或 SVerticalBox
// MyContainer->Slot() [ CodeViewWidget ];
```
*(注：此示例基于头文件中 `SCodeView` 的 `SLATE_BEGIN_ARGS` 定义和公共构造方法推导)*

### 进阶用法
该控件与 `SDetailSection` 集成时，可以通过 `OnDetailSectionExpansionChanged` 方法响应详情面板的展开/折叠状态。控件内部会自行管理树的展开、过滤和数据获取（通过 `FSourceCodeNavigation` 系统查询符号信息）。

## Demo 示例
以下是一个**概念性示例**，展示如何在自定义的编辑器面板中集成 `SCodeView`。由于该插件未暴露广泛的公共 API，此示例主要展示初始化逻辑。

**MyCodeViewPanel.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"

class SCodeView;

class SMyCodeViewPanel : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyCodeViewPanel) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    TSharedPtr<SCodeView> CodeViewPtr;
};
```

**MyCodeViewPanel.cpp**
```cpp
#include "MyCodeViewPanel.h"
#include "SCodeView.h" // 引用 CodeView 插件的控件头文件
#include "Widgets/Input/SSearchBox.h"
#include "Widgets/Views/STreeView.h"

void SMyCodeViewPanel::Construct(const FArguments& InArgs)
{
    // 定义获取选中 Actor 的委托（实际逻辑需根据你的上下文实现）
    FGetSelectedActors GetSelectedActors = FGetSelectedActors::CreateLambda([]() -> TArray<AActor*>
    {
        TArray<AActor*> SelectedActors;
        if (GEditor)
        {
            USelection* Selection = GEditor->GetSelectedActors();
            for (FSelectionIterator It(*Selection); It; ++It)
            {
                AActor* Actor = Cast<AActor>(*It);
                if (Actor)
                {
                    SelectedActors.Add(Actor);
                }
            }
        }
        return SelectedActors;
    });

    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .AutoHeight()
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("Code View (选中 Actor 的类结构)")))
        ]
        + SVerticalBox::Slot()
        .FillHeight(1.0f)
        [
            SAssignNew(CodeViewPtr, SCodeView)
            .GetSelectedActors(GetSelectedActors)
        ]
    ];
}
```
*(注：实际的构建过程可能涉及将此面板注册到编辑器布局中，这超出了本插件的范围。)*

## 模块依赖
从插件的模块类型（Editor）和功能（Slate UI）推断，其构建依赖于常见的编辑器和Slate模块。
无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态
### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复了编译时“不可达代码”的警告错误 |
| 2023-11-20 | `763a6119` | Fix C4072 warnings | 修复了C4072编译器警告 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件目录的常规整理或变更 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 将插件内的供应商链接更新为HTTPS安全协议 |
| 2022-05-09 | `6248f8d4` | Replacing legacy EditorStyle calls with AppStyle | 将已废弃的EditorStyle API调用替换为新的AppStyle |

### 维护评价
**⚠️ 警告：插件已超过1年无实质性功能更新。**

**综合评价：**
- **创建时间**：创建于2014年，是UE4早期插件，历史悠久。
- **更新频率**：近2年（2022-2024）仅有零星的维护性提交，修复编译警告、更新协议等，无任何功能增强或bug修复。
- **活跃度**：处于“维护模式”或“低优先级”状态，而非活跃开发。虽然插件仍存在于代码库中，但Epic可能已不再将其作为重点发展功能。
- **已知问题**：代码显示为“Experimental”，且 `EnabledByDefault=false`，表明它可能不完整或不适用于生产环境。
- **推荐使用**：**不推荐用于新的生产项目**。此插件更适合作为学习编辑器扩展（Slate、Details面板集成、代码导航）的参考，或者用于内部工具的原型开发。对于生产环境，建议使用更成熟、社区支持更好的编辑器扩展方案。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CodeView)
- [官方文档]() (无)
- [测试用例]() (未在提供的源码中发现)