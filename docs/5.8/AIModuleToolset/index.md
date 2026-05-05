# AIModuleToolset

> Toolset for AIModule Systems（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（工具集资产） |
| 模块 | `AIModuleToolset` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-01 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/AIModuleToolset) | |

## 用途

这是一个实验性的编辑器工具插件，旨在为 Unreal Engine 的 AI 模块（如行为树、EQS 等）提供一套开发和调试工具集。它本身不包含具体的 AI 运行时逻辑，而是作为工具和扩展的注册中心，可能用于增强编辑器中对 AI 系统的可视化、调试或配置能力。由于其 `EditorOnly` 和 `IsExperimentalVersion` 标志，它主要用于 AI 系统的开发阶段。

## 使用场景

- 你正在开发或调试复杂的行为树（Behavior Tree）或环境查询系统（EQS），需要额外的编辑器工具来辅助分析。
- 你希望为 AI 模块系统添加自定义的编辑器扩展或调试视图。
- 你正在参与 AI 模块的引擎开发，需要一个工具集插件来组织相关的开发工具。

## 蓝图用法

根据提供的源码分析，此插件主要提供模块接口，未发现公开的 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`。其功能可能通过编辑器菜单、工具栏按钮或自定义资产编辑器来暴露，而非蓝图节点。

### 核心节点

无公开的蓝图节点。

### 使用示例（蓝图描述）

不适用。此插件的功能主要在编辑器界面中使用，而非通过蓝图图表。

## C++ 用法

### 头文件引入

```cpp
#include "AIModuleToolset.h"
```

### 基本用法

此插件主要作为模块存在，其核心功能是注册工具集。在 C++ 中，你通常需要确保此模块被加载，以便其工具集能够生效。

```cpp
// 检查模块是否已加载（通常在插件或模块的 StartupModule 中）
if (FModuleManager::Get().IsModuleLoaded("AIModuleToolset"))
{
    // AIModuleToolset 模块已加载，其注册的工具集应该可用
}
```
*（基于模块加载的一般模式推断）*

### 进阶用法

由于此插件依赖于 `ToolsetRegistry` 插件，其进阶用法很可能涉及向该注册表注册自定义的 AI 工具。具体的注册 API 需要参考 `ToolsetRegistry` 插件的文档。`AIModuleToolset` 模块本身可能在其 `StartupModule` 中完成了初始工具集的注册。

## Demo 示例

这是一个编辑器工具插件，没有独立的运行时组件。一个最小的“使用”示例是在你的项目或插件中启用它，并确保其依赖的 `ToolsetRegistry` 插件也已启用。

```cpp
// 在你的编辑器模块或插件中，你可能需要依赖 AIModuleToolset 模块
// 在你的 .Build.cs 文件中：
PublicDependencyModuleNames.AddRange(new string[] { "AIModuleToolset" });
```

## 模块依赖

从 `Build.cs` 分析，该模块仅依赖 `Core`。但其功能实现依赖于另一个插件。

| 模块/插件 | 用途 |
|---|---|
| `ToolsetRegistry` (插件) | 提供工具集注册框架，AIModuleToolset 依赖它来注册和管理 AI 工具 |

## 维护状态

### 近期更新

- 2026-04-03 `7f02bd73` [AI Toolsets]: Move all toolsets to load at post engine init to simplify registration when toolset r
- 2026-04-01 `f92c7327` [AI Toolsets]: Move AIModuleToolset under the Toolsets directory

### 维护评价

- **创建时间**：非常新（2026年4月创建）。
- **更新频率**：创建后两天内有两次提交，但均为结构调整（移动目录、更改加载阶段），无实质性功能更新。
- **活跃度**：处于早期开发或整合阶段，近期无新功能提交。
- **已知限制**：标记为实验性（`IsExperimentalVersion=true`）且默认不启用（`EnabledByDefault=false`），表明其 API 和功能可能不稳定。
- **推荐使用**：**不推荐**在生产项目中使用。仅适用于对 AI 模块系统进行底层开发或实验的开发者。普通项目用户应等待其脱离实验状态。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/AIModuleToolset)
- [官方文档]()（无）
- [测试用例]()（未在提供信息中发现）