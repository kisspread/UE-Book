# Blank Example Plugin

> An example of a minimal plugin.  This can be used as a starting point when creating your own plugin.

| 属性 | 值 |
|---|---|
| 中文名 | 空白示例插件 |
| 分类 | Examples |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BlankPlugin` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/BlankPlugin) | |

## 用途

BlankPlugin 是一个**最小化插件模板**。它本身没有任何功能代码，仅包含一个空的、符合规范的插件模块结构。

**它解决的问题是：** 为开发者提供一个清晰、标准的插件创建起点。当你想要学习 UE5 插件的基本结构、模块接口声明方式，或者需要快速创建一个新插件时，可以此为基础进行复制和修改。

## 使用场景

- 你正在学习如何为 UE5 开发自定义插件。
- 你需要创建一个全新的、不包含任何初始内容的插件框架。
- 你想了解一个插件模块（`IModuleInterface`）的标准接口声明。

## 蓝图用法

此插件为纯代码模块，其公开接口 (`IBlankPlugin`) 是 C++ 模块接口，**未暴露任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性**到蓝图中。因此，在蓝图编辑器中无法直接使用此插件提供的节点。

### 核心节点

无。此插件不包含任何蓝图节点。

### 使用示例（蓝图描述）

不适用。

## C++ 用法

此插件的主要用途是作为模板参考，其代码展示了模块接口的标准实现模式。

### 头文件引入

```cpp
#include "IBlankPlugin.h"
```

### 基本用法

以下代码展示了如何检查 `BlankPlugin` 模块是否加载，并获取其实例。这通常用于检查某个可选插件或功能模块是否可用。

```cpp
// 来源: Engine/Plugins/Developer/BlankPlugin/Source/BlankPlugin/Public/IBlankPlugin.h
// 检查模块是否已加载并可用
if (IBlankPlugin::IsAvailable())
{
    // 安全地获取模块实例并使用其接口
    IBlankPlugin& BlankPluginModule = IBlankPlugin::Get();
    // 在此处调用模块的方法（如果有的话）
}
else
{
    // 模块未加载的处理逻辑
}
```

### 进阶用法

作为最小模板，此插件没有更复杂的用法。其价值在于展示了：
1.  如何定义一个继承自 `IModuleInterface` 的纯接口类。
2.  如何提供 `Get()` 和 `IsAvailable()` 的静态便捷访问方法。

你可以将此模式复制到自己插件的 `Public/IYourPlugin.h` 文件中，并扩展该接口。

## Demo 示例

以下是一个基于 `BlankPlugin` 接口模式的最小示例，展示了如何在你自己的模块中声明和使用一个模块接口。

**MyPluginModule.h**
```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FMyPluginModule : public IModuleInterface
{
public:
    /** 模块启动时调用 */
    virtual void StartupModule() override;
    /** 模块关闭时调用 */
    virtual void ShutdownModule() override;

    /** 获取单例实例 */
    static inline FMyPluginModule& Get()
    {
        return FModuleManager::LoadModuleChecked<FMyPluginModule>("MyPlugin");
    }

    /** 检查模块是否可用 */
    static inline bool IsAvailable()
    {
        return FModuleManager::Get().IsModuleLoaded("MyPlugin");
    }
};
```

**MyPluginModule.cpp**
```cpp
#include "MyPluginModule.h"

#define LOCTEXT_NAMESPACE "FMyPluginModule"

void FMyPluginModule::StartupModule()
{
    // 模块启动时的初始化代码
}

void FMyPluginModule::ShutdownModule()
{
    // 模块关闭时的清理代码
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyPluginModule, MyPlugin)
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件目录的通用维护性提交。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 将内置插件的供应商链接更新为安全协议。 |
| 2019-12-27 | `28d3d740` | (Integrating from Dev-EngineMerge to Main) | 从开发分支集成到主线的通用合并。 |
| 2019-09-02 | `e7f83a71` | Convert all remaining "Developer" modules to "UncookedOnly", to preserve existing behavior. | 将剩余“开发”模块转换为“仅未打包”类型以维持行为。 |
| 2018-12-14 | `530369c6` | Merging //UE4/Dev-Main to Dev-Build (//UE4/Dev-Build) | 开发主线到开发构建分支的合并。 |

### 维护评价

- **年龄与活跃度**：插件创建于 2014 年，是一个历史悠久的“文物”。最近一次实质性更新（模块类型转换）停留在 2019 年，此后仅有零星的通用维护提交。
- **维护状态**：**维护不活跃**。超过 5 年没有功能性更新，但因其作为“模板示例”的特殊性质，其基本结构仍然有效。
- **已知限制**：无任何功能代码，仅作为结构参考。
- **推荐使用**：✅ **推荐用于学习目的**。如果你需要理解 UE5 插件的基本骨架，这是一个很好的起点。但请注意，`e7f83a71` 这次提交表明其模块类型在 2019 年曾被调整，在新项目中直接复制可能需要确认模块类型（Runtime/UncookedOnly）是否符合你的预期。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/BlankPlugin)
- [官方文档]()（无）
- [测试用例]()（此插件无测试用例）