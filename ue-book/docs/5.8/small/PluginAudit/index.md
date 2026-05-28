# Plugin Audit

> Editor plugin for auditing plugin connectivity.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 插件审计 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PluginAudit` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-02-10 |
| 年龄标签 | 👴 老古董（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PluginAudit) | |

## 用途

这是一个为大型或模块化项目设计的编辑器工具。其核心目的是在项目打包（Cook）前进行“健康检查”，验证所有计划打包的插件之间依赖关系的正确性。

它主要解决两个关键问题：
1.  **依赖完整性**：确保项目计划打包的所有插件，不会依赖任何没有被计划打包的插件。这可以避免因缺失依赖导致运行时崩溃。
2.  **Gameplay Tag 来源验证**：检查项目中使用的 `GameplayTag` 是否来源于一个将被排除（未计划打包）的插件。如果 Tag 来源不可用，依赖该 Tag 的逻辑（如 `GameplayAbility` 或 `GameplayCue`）将无法正常工作。

简单来说，这个插件是一个**依赖图分析器和验证器**，帮助开发者在复杂的插件依赖网络中发现潜在的“断链”和“隐藏炸弹”，是项目上线前的质量保障工具。

## 使用场景

- **模块化或使用 GameFeature 的项目**：项目由多个 GameFeature 插件组成，需要确保所有激活的功能模块及其依赖都能正确打包。
- **项目打包前最终检查**：在构建发布版本前，运行一次插件审计，快速发现依赖缺失问题，避免漫长的打包失败调试。
- **团队开发大型项目**：多个团队负责不同插件，需要一个中央视图来审计整个项目的插件健康状况。
- **怀疑有隐藏依赖**：当遇到某个功能在打包后失效，但编辑器里正常时，可以用此工具检查其 Gameplay Tag 来源是否被意外排除。

## 蓝图用法

经分析源码，此插件未暴露任何 `BlueprintCallable` 或 `BlueprintReadWrite` API。它是一个纯粹的**编辑器 UI 工具**，其功能通过编辑器菜单和自定义的审计浏览器界面触发，不提供蓝图节点。

## C++ 用法

此插件主要提供编辑器功能，其核心逻辑封装在 `SPluginAuditBrowser` 窗口控件中。以下是其内部逻辑的示例，展示了如何从 C++ 侧理解其工作流。

### 头文件引入

```cpp
#include "PluginAudit.h"
```

### 基本用法：理解审计流程

审计过程主要分为三步，如以下代码逻辑所示：
```cpp
// 1. 获取所有计划打包的插件列表（包括排除列表）
TArray<TSharedRef<IPlugin>> IncludedPlugins; // 计划打包的插件
TArray<TSharedRef<IPlugin>> ExcludedPlugins; // 明确排除的插件

// 2. 扫描违规行为（核心函数）
TArray<TSharedRef<FTokenizedMessage>> Violations = SPluginAuditBrowser::ScanForViolations(IncludedPlugins, ExcludedPlugins);

// 3. 检查特定 Gameplay Tag 来源（示例）
FGameplayTag TagToCheck = FGameplayTag::RequestGameplayTag(FName("MyGame.SpecificTag"));
bool bTagSafe = !SPluginAuditBrowser::IsTagOnlyAvailableFromExcludedSources(UGameplayTagsManager::Get(), TagToCheck, ExcludedPlugins);
```
*(逻辑提炼自 `SPluginAuditBrowser::RefreshViolations` 和相关静态函数)*

### 进阶用法：通过控制台命令触发

虽然插件本身不暴露 API，但你可以通过其他编辑器模块（例如一个自定义的编辑器工具）来启动审计。通常，它是通过菜单或一个预注册的命令来启动的。
```cpp
// 假设你已经找到了注册审计命令的方式，以下是一个概念性调用
// 实际的命令注册可能在 `FPluginAuditModule::StartupModule()` 中完成
FPluginAuditModule::Get().StartAudit();
```
*(提示：你需要查看 `PluginAudit.cpp` 中模块启动时的代码来找到确切的注册方式)*

## Demo 示例

由于此插件主要是编辑器UI，一个“可运行”的示例是演示如何通过一个简单的编辑器命令或菜单项来调用它。以下是基于其模块注册的简化示例。

```cpp
// MyEditorTool.h
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyEditorToolModule : public IModuleInterface
{
public:
    virtual void StartupModule() override
    {
        // 注册一个自定义的控制台命令来启动审计
        ConsoleCommand = IConsoleManager::Get().RegisterConsoleCommand(
            TEXT("MyEditorTool.RunPluginAudit"),
            TEXT("Triggers the Plugin Audit process via command."),
            FConsoleCommandDelegate::CreateLambda([]()
            {
                // 这里可以调用插件审计的启动逻辑
                // 例如：FPluginAuditModule::Get().StartAudit();
                UE_LOG(LogTemp, Display, TEXT("Plugin Audit triggered via MyEditorTool."));
            })
        );
    }

    virtual void ShutdownModule() override
    {
        if (ConsoleCommand)
        {
            IConsoleManager::Get().UnregisterConsoleObject(ConsoleCommand);
        }
    }

private:
    IConsoleCommand* ConsoleCommand = nullptr;
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameFeatures` | 用于识别和操作 GameFeature Plugin (GFP)，是依赖检查的核心目标。 |
| `AssetManagerEditor` | 提供编辑器内资产管理和查询功能，用于获取插件资产信息。 |
| `PluginReferenceViewer` | 提供可视化插件引用关系图的功能，插件中可右键直接打开此查看器。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-08-02 | `cecb3fd7` | Separate GFP PluginDetails and PluginURL query functionality. | 重构了 GFP 详情和 URL 查询逻辑，使其更模块化。 |
| 2024-02-14 | `7028c9b8` | Added ability to cancel the Plugin Audit process in the editor. | 新增取消正在进行的审计过程的功能，提升了用户体验。 |
| 2023-10-13 | `2a4f92dd` | GetGameFeaturePluginDetails API cleanup | 对获取 GameFeature 插件详情的 API 进行了清理和优化。 |
| 2023-06-09 | `af9ea875` | Double clicking a plugin name entry in the audit list will open the plugin reference viewer focused | 双击审计列表中的插件名会打开插件引用查看器并聚焦。 |
| 2023-06-09 | `f038a266` | Moving the plugin reference viewer into it’s own plugin and module so it can also be launched from t... | 将插件引用查看器移入独立模块，使其可以被其他工具调用。 |

### 维护评价

此插件目前处于**实验性（Beta）** 状态，且**未默认启用**。

**积极面**：
- **活跃维护**：从提交记录看，自 2023 年创建后，在 2024 年仍有功能更新（取消操作、重构），表明 Epic 团队仍在迭代它。
- **功能明确**：解决了 GameFeature 和插件化架构下的一个实际痛点。
- **集成良好**：与 `PluginReferenceViewer` 深度集成，提供了流畅的审计工作流。

**注意事项**：
- **实验性**：`IsBetaVersion: true`，意味着其API和行为在未来版本中可能发生改变。
- **适用范围窄**：主要面向使用 GameFeature Plugin 的大型或模块化项目。对于简单的单插件项目，此工具意义不大。
- **需要手动启用**：`EnabledByDefault: false`，用户需要主动在项目中启用此插件。

**结论**：如果你正在使用 GameFeature 或开发高度模块化的 UE5 项目，并希望确保打包安全，**推荐启用和使用此插件**。它目前仍在积极维护，但需接受其“实验性”标签带来的不确定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PluginAudit)
- 官方文档：无
- 测试用例：未在插件目录内发现明确的测试文件，其功能验证可能集成在更大的编辑器测试套件中。