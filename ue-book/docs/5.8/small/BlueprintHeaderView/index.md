# Blueprint C++ Header Preview

> A tool to help convert Blueprint Classes to Native C++.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 蓝图C++头预览 |
| 分类 | Blueprints |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（代码资产） |
| 模块 | `BlueprintHeaderView` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-01-24 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/BlueprintHeaderView) | |

## 用途

这是一个编辑器扩展工具，其核心功能是在虚幻编辑器中为蓝图类和用户自定义结构体提供一个预览面板，实时显示其对应的 C++ 头文件代码。

它解决的核心问题是：**帮助开发者理解蓝图资产的底层 C++ 数据结构**。当开发者使用蓝图进行快速原型开发并计划将其重构为原生 C++ 代码以获得更好性能时，这个工具可以直观地展示蓝图中的变量、函数等元素将如何被翻译为 C++ 代码，包括 UPROPERTY/UFUNCTION 宏、访问说明符、类型名称等。它不仅仅是一个只读预览器，还允许用户在预览的代码中直接进行重命名操作（如果名称不合法），并提供了跳转到蓝图图表的功能，极大地辅助了蓝图到 C++ 的转换和调试过程。

## 使用场景

- **蓝图转 C++ 迁移**：你有一个复杂的蓝图类，准备将其转换为 C++ 以优化性能。你可以打开此工具查看其等效的 C++ 头文件，对照着在 C++ 工程中创建对应的 .h 文件。
- **理解蓝图数据结构**：你在调试一个与蓝图交互的 C++ 插件或模块，需要了解某个蓝图资产中变量的确切 C++ 类型和声明方式。
- **规范命名检查**：你发现蓝图中的某些变量名或函数名包含空格或特殊字符，这些在 C++ 中是非法的。此工具会高亮显示这些非法名称，并允许你直接重命名。
- **查看继承与结构**：快速查看一个蓝图类的父类、实现的接口，以及其包含的所有 UPROPERTY 和 UFUNCTION 的声明，无需切换到 C++ IDE。

## 蓝图用法

此插件主要作为编辑器面板和上下文菜单使用，不提供传统意义上的蓝图节点。其核心功能通过编辑器 UI 交互触发。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OpenHeaderViewForAsset` | 为指定的蓝图资产数据打开头视图面板 | `FBlueprintHeaderViewModule` |
| `IsClassHeaderViewSupported` | 判断给定的 UClass 是否支持头视图（例如，检查是否是蓝图类或用户定义结构体） | `FBlueprintHeaderViewModule` |

### 使用示例（蓝图描述）

**场景：通过内容浏览器上下文菜单打开**
1. 在内容浏览器中，选中一个 **蓝图资产**（如 `BP_MyActor`）或一个 **用户定义结构体**。
2. 右键点击该资产。
3. 在弹出的上下文菜单中，找到并点击 **“Blueprint C++ Header Preview”** 选项。
4. 编辑器将打开或激活“蓝图C++头预览”标签页，并自动加载选中资产的 C++ 头文件预览。

**场景：通过类选择器打开**
1. 通过菜单栏的“窗口” -> “开发者工具” 或通过其他方式打开“蓝图C++头预览”面板。
2. 面板顶部有一个类选择器下拉框。
3. 点击下拉框，将出现一个资产选择器，可以搜索并选择任意蓝图类或用户定义结构体。
4. 选择后，下方的代码预览区域将立即显示对应资产的 C++ 头文件内容。

## C++ 用法

此插件的 C++ API 主要用于在编辑器扩展或工具中以编程方式控制头视图。

### 头文件引入

```cpp
#include "BlueprintHeaderView.h"
```

### 基本用法

**检查类是否支持头视图**
```cpp
// 检查一个UClass是否为蓝图类或用户定义结构体，从而判断是否可用头视图预览
UClass* MyClass = SomeActor->GetClass();
if (FBlueprintHeaderViewModule::IsClassHeaderViewSupported(MyClass))
{
    // 该类支持头视图，可以安全地为其打开预览面板
    UE_LOG(LogTemp, Log, TEXT("Class '%s' supports Header View."), *MyClass->GetName());
}
```
*(来源：推断自 `FBlueprintHeaderViewModule::IsClassHeaderViewSupported` 的声明)*

**以编程方式打开头视图**
```cpp
// 假设你有一个指向蓝图资产的 FAssetData（例如，从内容浏览器获取）
FAssetData BlueprintAssetData = ...; // 获取你的蓝图资产数据

// 使用模块函数直接打开该资产的头视图
FBlueprintHeaderViewModule::OpenHeaderViewForAsset(BlueprintAssetData);
```
*(来源：推断自 `FBlueprintHeaderViewModule::OpenHeaderViewForAsset` 的声明)*

### 进阶用法

**直接构造并使用头视图 Slate 控件（高级）**
虽然通常通过模块函数打开面板，但理论上你也可以直接构造 `SBlueprintHeaderView` 控件并将其嵌入到自定义的编辑器窗口或面板中。
```cpp
// 在创建自定义编辑器面板时
TSharedRef<SBlueprintHeaderView> HeaderViewWidget = SNew(SBlueprintHeaderView);
// 可以将此 Widget 放置到你的 SVerticalBox 或其他容器中
// 注意：直接使用需要处理更多生命周期和资产选择逻辑。
```
*(来源：`SBlueprintHeaderView.h` 中的类声明)*

## Demo 示例

以下是一个最小的编辑器模块示例，展示如何在自定义的编辑器窗口中使用 BlueprintHeaderView 模块的功能。

**MyEditorModule.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    void OpenHeaderViewForSelectedAsset();
};
```

**MyEditorModule.cpp**
```cpp
#include "MyEditorModule.h"
#include "BlueprintHeaderView.h" // 引入头视图模块头文件
#include "IContentBrowserSingleton.h"
#include "ContentBrowserModule.h"

#define LOCTEXT_NAMESPACE "FMyEditorModule"

void FMyEditorModule::StartupModule()
{
    // 模块启动逻辑
}

void FMyEditorModule::ShutdownModule()
{
    // 模块关闭逻辑
}

void FMyEditorModule::OpenHeaderViewForSelectedAsset()
{
    // 获取内容浏览器中当前选中的资产
    FContentBrowserModule& ContentBrowserModule = FModuleManager::LoadModuleChecked<FContentBrowserModule>("ContentBrowser");
    TArray<FAssetData> SelectedAssets;
    ContentBrowserModule.Get().GetSelectedAssets(SelectedAssets);

    if (SelectedAssets.Num() > 0)
    {
        // 取第一个选中的资产，并检查其是否支持头视图
        const FAssetData& Asset = SelectedAssets[0];
        UClass* AssetClass = Asset.GetClass();

        if (AssetClass && FBlueprintHeaderViewModule::IsClassHeaderViewSupported(AssetClass))
        {
            // 支持，打开头视图
            FBlueprintHeaderViewModule::OpenHeaderViewForAsset(Asset);
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("Selected asset is not a Blueprint or UserDefinedStruct."));
        }
    }
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyEditorModule, MyEditorModule)
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG宏迁移至新的UE_LOGF宏。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 使用工具将默认析构函数体改为空。 |
| 2025-10-07 | `bafb0226` | Fixed non unity/pch by adding includes | 修复了非统一构建/预编译头时缺少头文件包含的问题。 |
| 2025-05-31 | `8396b185` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of ty | 使用工具确保DLL导出/导入说明符正确应用在方法和静态变量上。 |
| 2024-10-22 | `98a8e0e0` | Removed lots of UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes | 移除了大量已弃用的包含顺序兼容性宏作用域。 |

### 维护评价

**综合评价：不活跃维护。**

该插件于 2022 年 1 月创建，距今已超过 3 年。从近期提交记录来看，最后一次包含功能性更新或重大改动的提交很可能发生在创建初期。2024 年至 2026 年的所有提交均为**代码维护性工作**，主要围绕引擎全局的代码规范迁移（如日志宏、析构函数写法、DLL导出说明符、头文件包含等），没有涉及该插件自身功能的新增、修复或优化。

**结论**：
1.  **创建时间**：3年多。
2.  **更新频率**：最近 3 年内无功能性更新，仅有被动的引擎代码规范化改动。
3.  **活跃度**：处于**维护不活跃**状态，接近于“维护性搁置”。
4.  **已知问题/限制**：从代码看，它专注于蓝图和用户定义结构体的头文件预览，不支持其他UClass。
5.  **是否推荐使用**：该插件的核心功能稳定，作为编辑器辅助工具依然**可以使用**。但由于长期没有功能性迭代，若未来引擎有重大变更（如新的蓝图特性或C++标准），其兼容性可能存在风险。对于新项目，建议评估其是否满足当前需求，对于已有项目中的依赖则可继续使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/BlueprintHeaderView)
- 官方文档：无
- 测试用例：未在提供路径中找到明确的测试文件。