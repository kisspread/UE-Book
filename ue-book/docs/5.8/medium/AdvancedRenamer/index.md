# Batch Renamer

> Rename multiple selected actors or assets, and standardize their prefixes and suffixes.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 批量重命名器 |
| 分类 | Experimental |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AdvancedRenamer` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-26 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AdvancedRenamer) | |

## 用途

AdvancedRenamer 是一个编辑器插件，旨在解决在 Unreal Engine 中批量、高效地重命名大量演员（Actor）或资产（Asset）的痛点。它提供了一个现代化、功能丰富的用户界面，允许用户通过添加前后缀、编号、搜索替换、改变大小写等多种操作来规范化命名，避免了逐个手动修改的繁琐过程。

## 使用场景

- 你在组织一个大型关卡，其中数百个同类演员（如树木、石头）命名混乱 → 使用 AdvancedRenamer 给它们添加统一前缀和递增编号。
- 你从外部导入了一批资产，文件名带有冗余的版本号或后缀 → 使用 AdvancedRenamer 的搜索替换或删除后缀功能进行清理。
- 你需要快速将所有选中的资产名称改为全大写或全小写，以符合项目规范 → 使用 Change Case 功能一键完成。

## 蓝图用法

此插件主要通过 C++ 模块接口提供功能，蓝图可直接调用的公开函数较少，核心功能集中在编辑器 UI 和 C++ API 上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OpenAdvancedRenamerForActors` | 为给定的演员数组打开高级重命名面板 | `IAdvancedRenamerModule` |
| `OpenAdvancedRenamer` | 为给定的数据提供者（Provider）打开高级重命名面板 | `IAdvancedRenamerModule` |
| `GetActorsSharingClassesInWorld` | 获取世界中与输入演员具有相同类的所有演员 | `IAdvancedRenamerModule` |

### 使用示例（蓝图描述）

1.  获取 `IAdvancedRenamerModule` 引用：使用 `FModuleManager::LoadModuleChecked<IAdvancedRenamerModule>(TEXT(“AdvancedRenamer”))` 或静态方法 `IAdvancedRenamerModule::Get()`。
2.  准备一个演员数组 (`TArray<AActor*>`)，例如通过“Get All Actors Of Class”节点获得。
3.  调用 `OpenAdvancedRenamerForActors` 节点，并传入该数组和一个 `IToolkitHost` 或 `SWidget` 引用（通常来自编辑器上下文），即可弹出重命名窗口。
4.  在窗口中配置重命名规则（如添加前缀“SM_”，启用递增编号），然后点击“应用”。

## C++ 用法

### 头文件引入

```cpp
#include “IAdvancedRenamerModule.h”
```

### 基本用法

通过模块接口，为一组演员打开重命名器。
*来源: `IAdvancedRenamerModule.h` 及其使用示例。*

```cpp
// 确保模块已加载
if (IAdvancedRenamerModule::IsLoaded())
{
    IAdvancedRenamerModule& RenamerModule = IAdvancedRenamerModule::Get();

    // 假设你有一组演员指针
    TArray<AActor*> SelectedActors = ...;

    // 在编辑器工具包（Toolkit）中打开重命名器
    if (TSharedPtr<IToolkitHost> ToolkitHost = FToolkitManager::Get().FindToolkitForAsset(GetOuter()))
    {
        RenamerModule.OpenAdvancedRenamerForActors(SelectedActors, ToolkitHost);
    }
    // 或者在一个父Slate控件中打开
    else if (TSharedPtr<SWidget> ParentWidget = ... )
    {
        RenamerModule.OpenAdvancedRenamerForActors(SelectedActors, ParentWidget);
    }
}
```

### 进阶用法

实现自定义的 `IAdvancedRenamerProvider` 以支持自定义对象类型的重命名。
*来源: `IAdvancedRenamerProvider.h` 和 `FAdvancedRenamerObjectProvider` 的实现模式。*

```cpp
// 1. 创建一个自定义的 Provider，继承自 IAdvancedRenamerProvider
class FMyCustomObjectProvider : public IAdvancedRenamerProvider
{
public:
    // 实现所有纯虚函数，如 Num(), GetOriginalName(), CanRename() 等
    // 在 PrepareRename 和 ExecuteRename 中实现你自己的重命名逻辑
    virtual bool ExecuteRename() override
    {
        for (const auto& Pair : MyObjectToNewNameList)
        {
            // 对你的自定义对象执行重命名操作
            Pair.Key->Rename(*Pair.Value);
        }
        return true;
    }
    // ... 其他实现
private:
    TArray<TTuple<UMyObject*, FString>> MyObjectToNewNameList;
};

// 2. 使用 Provider 创建并打开重命名器
TSharedRef<FMyCustomObjectProvider> MyProvider = MakeShared<FMyCustomObjectProvider>();
MyProvider->SetObjectList(MyCustomObjects);

IAdvancedRenamerModule& RenamerModule = IAdvancedRenamerModule::Get();
TSharedRef<IAdvancedRenamer> Renamer = RenamerModule.CreateAdvancedRenamer(MyProvider);
RenamerModule.OpenAdvancedRenamer(Renamer, ToolkitHost);
```

## Demo 示例

一个最小的示例，演示如何在编辑器模块中为选中的演员打开 AdvancedRenamer。
*注：需在项目的 `.Build.cs` 中添加对 `AdvancedRenamer` 模块的依赖。*

**MyEditorModule.h**
```cpp
#pragma once

#include “CoreMinimal.h”
#include “Modules/ModuleManager.h”

class FMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void OnOpenRenamerClicked();
};
```

**MyEditorModule.cpp**
```cpp
#include “MyEditorModule.h”
#include “IAdvancedRenamerModule.h”
#include “Toolkits/ToolkitManager.h”
#include “LevelEditor.h”

void FMyEditorModule::StartupModule()
{
    // 可以在这里注册菜单项或快捷键来触发 OnOpenRenamerClicked
}

void FMyEditorModule::ShutdownModule()
{
}

void FMyEditorModule::OnOpenRenamerClicked()
{
    if (!IAdvancedRenamerModule::IsLoaded())
    {
        return;
    }

    IAdvancedRenamerModule& RenamerModule = IAdvancedRenamerModule::Get();

    // 获取当前关卡编辑器选中的演员
    TArray<AActor*> SelectedActors;
    // ... 获取选中的演员逻辑 (例如使用 GEditor->GetSelectedActors())

    if (SelectedActors.Num() > 0)
    {
        // 尝试获取关卡编辑器的 ToolkitHost
        FLevelEditorModule& LevelEditorModule = FModuleManager::LoadModuleChecked<FLevelEditorModule>(“LevelEditor”);
        TSharedPtr<IToolkitHost> ToolkitHost = LevelEditorModule.GetLevelEditorInstance().Pin();

        if (ToolkitHost.IsValid())
        {
            RenamerModule.OpenAdvancedRenamerForActors(SelectedActors, ToolkitHost);
        }
    }
}

IMPLEMENT_MODULE(FMyEditorModule, MyEditor)
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。要在你的模块中使用此插件，需在 `Build.cs` 中添加：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    “AdvancedRenamer” // 添加此模块
});
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到新的 UE_LOGF。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 代码修复：将空的析构函数体替换为 `= default`。 |
| 2024-11-14 | `c033e1eb` | Add a way to disable opening the advanced renamer for actors that don‘t support renaming | 新增过滤功能，可禁用对不支持重命名的演员打开重命名器。 |
| 2024-10-22 | `cabb7dd8` | Fix a few more menus that did not take into consideration bCanBeModified | 修复更多菜单未考虑 `bCanBeModified` 属性的问题。 |
| 2024-09-25 | `7428c89c` | [BatchRenamer] numbering should be based on the ordering requested and not always on the initial ord | 修复编号逻辑，使其基于请求的排序顺序，而非初始顺序。 |

### 维护评价

该插件创建于 2024 年初，至今仍在活跃维护中（最近更新在 2026 年 4 月）。近期更新包括功能增强（如过滤不支持重命名的演员）、Bug 修复和代码现代化。

**主要特点与风险：**
*   **优点**：功能全面，界面现代，由 Epic Games 开发维护，有持续更新。
*   **风险**：插件被标记为 `IsExperimentalVersion = true`，这意味着其 API 和功能在未来版本中可能发生不兼容的变化。
*   **推荐**：**推荐使用**，尤其适合需要频繁进行批量重命名操作的工作流。但应意识到其“实验性”状态，在升级引擎版本时需注意可能的接口变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AdvancedRenamer)
- 官方文档：无
- 测试用例：无（插件内未发现测试文件）