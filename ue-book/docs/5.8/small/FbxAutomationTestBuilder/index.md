# FbxAutomationTestBuilder

> 

| 属性 | 值 |
|---|---|
| 中文名 | FBX自动化测试构建器 |
| 分类 | Testing |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `FbxAutomationTestBuilder` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2016-09-21 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/FbxAutomationTestBuilder) | |

## 用途
该插件是一个**内部开发与质量保证（QA）工具**，用于批量管理和执行 FBX 资产导入流程的自动化测试。它通过提供一个图形界面来创建、编辑、保存和运行针对特定 FBX 文件的导入“测试计划”（Test Plan），旨在验证 FBX 导入管线（Pipeline）的正确性和一致性。其核心目标是提升 FBX 相关功能开发（如 SDK 升级、导入流程修改）的测试效率和可重复性，减少人工回归测试的工作量。

## 使用场景
- **FBX 导入功能开发者**：在修改或升级 FBX 导入器（例如从 FBX SDK 2016 升级到 2020）后，需要验证所有关键资产类型的导入结果是否符合预期。
- **QA 工程师**：需要在不同引擎版本或硬件环境下，执行一批标准化的 FBX 导入测试，以确保功能没有回归。
- **技术美术（TA）或资产管线负责人**：需要为团队建立一套可重复执行的 FBX 资产导入验证流程，确保资产从 DCC 软件（如 Maya、3ds Max）到 Unreal 的转换正确无误。

## 蓝图用法
该插件未暴露任何蓝图可用的 API（未发现 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`），它是一个纯编辑器工具。

## C++ 用法
该插件主要提供编辑器扩展功能，其 C++ API 主要用于插件自身的模块化集成。

### 头文件引入
```cpp
#include "FbxAutomationBuilderModule.h"
```

### 基本用法
从模块类 `FFbxAutomationBuilderModule` 可以看出，插件提供创建和注册自定义编辑器标签页（Tab）的功能。
```cpp
// 在编辑器其他模块中，获取 FbxAutomationTestBuilder 模块并创建其UI
FFbxAutomationBuilderModule& FbxTestBuilderModule = FModuleManager::GetModuleChecked<FFbxAutomationBuilderModule>(“FbxAutomationTestBuilder”);
TSharedRef<SWidget> TestBuilderWidget = FbxTestBuilderModule.CreateFbxAutomationBuilderWidget();
// 可以将此 Widget 嵌入到自定义的编辑器窗口或面板中
```
*(来源：Engine/Plugins/Tests/FbxAutomationTestBuilder/Source/FbxAutomationTestBuilder/Public/FbxAutomationBuilderModule.h)*

### 进阶用法
插件的核心功能围绕 `UFbxTestPlan` 对象展开。一个测试计划（Test Plan）定义了要导入的 FBX 文件、预期的导入设置（例如，是否重新导入）以及测试结果验证方式。开发者可以通过该插件的 UI 来管理这些计划。
```cpp
// 伪代码示例：理解插件如何操作测试计划
// 1. 读取磁盘上已有的 JSON 格式的测试计划集合
// 2. 将每个 JSON 对象实例化为一个 UFbxTestPlan UObject
// 3. 用户在 UI 中选择一个 FBX 文件和一个测试计划
// 4. 插件调用引擎的 FBX 导入流程，应用测试计划中的设置
// 5. 执行导入并可能通过截图对比验证结果
```

## Demo 示例
以下示例展示了如何将 `FbxAutomationTestBuilder` 的界面集成到一个自定义的编辑器标签页中。
```cpp
// MyEditorModule.h
#pragma once
#include "Modules/ModuleManager.h"

class FMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
    
private:
    TSharedPtr<FTabManager> TabManager;
    void RegisterMenus();
    TSharedRef<SDockTab> SpawnTestBuilderTab(const FSpawnTabArgs& Args);
};
```
```cpp
// MyEditorModule.cpp
#include "MyEditorModule.h"
#include "FbxAutomationBuilderModule.h"
#include "WorkspaceMenuStructure.h"
#include "WorkspaceMenuStructureModule.h"

#define LOCTEXT_NAMESPACE "FMyEditorModule"

void FMyEditorModule::StartupModule()
{
    // 注册一个顶级菜单项
    UToolMenus::RegisterStartupCallback(FSimpleMulticastDelegate::FDelegate::CreateRaw(this, &FMyEditorModule::RegisterMenus));
}

void FMyEditorModule::RegisterMenus()
{
    FToolMenuOwnerScoped OwnerScoped(this);
    UToolMenu* Menu = UToolMenus::Get()->ExtendMenu(“LevelEditor.MainMenu.Tools”);
    FToolMenuSection& Section = Menu->FindOrAddSection(“MyTools”);
    Section.AddMenuEntry(
        "OpenFBXTestBuilder",
        LOCTEXT("OpenFBXTestBuilder", "FBX Test Builder"),
        LOCTEXT("OpenFBXTestBuilderTooltip", "Opens the FBX Automation Test Builder"),
        FSlateIcon(),
        FUIAction(FExecuteAction::CreateRaw(this, &FMyEditorModule::SpawnTestBuilderTab))
    );
}

TSharedRef<SDockTab> FMyEditorModule::SpawnTestBuilderTab(const FSpawnTabArgs& Args)
{
    // 获取FbxAutomationTestBuilder模块
    FFbxAutomationBuilderModule& FbxModule = FModuleManager::GetModuleChecked<FFbxAutomationBuilderModule>(“FbxAutomationTestBuilder”);
    TSharedRef<SWidget> Content = FbxModule.CreateFbxAutomationBuilderWidget();
    
    return SNew(SDockTab)
        .TabRole(ETabRole::NomadTab)
        .Label(LOCTEXT("FBXTestBuilderTab", "FBX Test Builder"))
        [
            Content
        ];
}

void FMyEditorModule::ShutdownModule()
{
    UToolMenus::UnRegisterStartupCallback(this);
    UToolMenus::UnregisterOwner(this);
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyEditorModule, MyEditorModule)
```
*注意：此示例仅用于演示集成方式。`FbxAutomationTestBuilder` 插件默认不启用（`EnabledByDefault: false`），你需要在编辑器插件设置中手动启用它，或者在你的模块 Build.cs 中声明依赖并确保其被加载。*

## 模块依赖
该插件是纯编辑器工具，没有面向外部模块的独特运行时依赖。

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Editor/Slate 等） | |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件目录的通用维护性更新（可能涉及路径或配置调整）。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新内置插件的厂商链接为安全协议（HTTPS）。 |
| 2022-05-09 | `6248f8d4` | Replacing legacy EditorStyle calls with AppStyle | 将已废弃的 EditorStyle API 调用替换为新的 AppStyle API。 |
| 2021-10-27 | `34f55d3a` | Merge from Release-Engine-Test @ 17946149 to UE5/Main | 从引擎测试分支合并代码到 UE5 主分支。 |
| 2021-05-10 | `45c87c95` | Check for object system existence before unregistering customizations. | 在注销自定义项前检查对象系统是否存在，防止崩溃。 |

### 维护评价
该插件是一个**陈旧的内部工具**。
- **创建时间**：2016 年 9 月，已近 9 年历史。
- **最近更新**：最后一次有实质意义的功能性更新（如 API 改动）可能在 2021 年之前。近期（2022-2023）的提交均为适配新版引擎的通用维护性修复（如 API 替换、链接更新），并非功能增强或 Bug 修复。
- **活跃度**：**维护不活跃**。超过 2 年没有针对插件本身功能的实质性提交。
- **状态**：该插件被标记为 `EnabledByDefault: false`，表明它是一个非标准工具，仅供内部或特定开发者使用。其 UI 和功能可能无法适配最新的 UE5 编辑器风格或导入管线变动。
- **推荐**：**不推荐普通项目使用**。它是一个高度特定化且可能过时的内部测试工具。如果你有类似的大规模 FBX 导入测试需求，建议参考其思路，使用 Unreal 的自动化测试框架（`AutomationTest`）和命令行工具（如 `RunUAT`）来构建自己的测试流程。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/FbxAutomationTestBuilder)
- 官方文档：无
- 测试用例：无公开的测试用例。该插件本身即为测试工具。