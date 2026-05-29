# UMG Viewmodel for UMG Preview

> A plugin to support UMG MVVM within the UMG Widget Preview plugin.

| 属性 | 值 |
|---|---|
| 中文名 | UMG MVVM预览 |
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ModelViewViewModelPreview` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-08 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ModelViewViewModelPreview) | |

## 用途

该插件是 **UMG MVVM 框架的配套调试工具**，其核心目的是在 **UMG Widget Preview（UMG 控件预览）** 编辑器环境中，为使用 MVVM 架构的 UI 控件提供可视化调试支持。它解决了在设计阶段实时验证数据绑定、查看 ViewModel 字段值变化和绑定执行日志的需求，让开发者无需运行游戏即可检查 UI 与数据层的连接是否正确，极大提升了 UI 开发和调试的效率。

## 使用场景

- **场景一：** 你正在使用 UE 的 MVVM 框架开发一个复杂的 UMG 界面（如库存、技能树），需要在编辑器中预览特定控件时，实时查看 ViewModel 的属性（如金币、等级）是否被正确绑定和更新。
- **场景二：** 你的 UI 绑定逻辑没有生效或值显示错误，需要在不启动游戏的情况下，调试是哪个绑定出了问题，以及字段值在何时发生了变化。
- **场景三：** 你希望将当前预览状态下的 ViewModel 数据导出为 JSON 文件，用于测试或分析。

## 蓝图用法

该插件为编辑器扩展，主要提供 Slate 界面和工具，**不包含供运行时蓝图调用的 UFUNCTION 节点**。

## C++ 用法

该插件主要作为编辑器模块运行，其提供的类（如 Slate 控件和扩展）通常由 `UMGWidgetPreview` 插件内部调用，插件使用者一般无需直接在 C++ 代码中引用。以下是其模块启动的基本结构：

### 头文件引入

```cpp
#include "ModelViewViewModelPreviewModule.h"
```

### 基本用法

这是模块的典型入口，它会在启动时注册与 `UMGWidgetPreview` 插件的集成。
*(来源: `Source/ModelViewViewModelPreview/Private/ModelViewViewModelPreviewModule.h`)*

```cpp
class FMVVMPreviewModule : public IModuleInterface
{
public:
    // 模块启动时调用，注册预览扩展
    virtual void StartupModule() override;

    // 模块关闭时调用，清理资源
    virtual void ShutdownModule() override;

private:
    // 持有与 UMGWidgetPreview 集成的扩展对象
    TSharedPtr<UE::MVVM::Private::FMVVMWidgetPreviewExtension> WidgetPreviewExtension;
};
```

## Demo 示例

以下是一个最小化的模块头文件和实现示例，展示了该插件如何作为编辑器模块进行生命周期管理。

**ModelViewViewModelPreviewModule.h**
```cpp
#pragma once

#include "Modules/ModuleManager.h"

namespace UE::MVVM::Private
{
    class FMVVMWidgetPreviewExtension;
}

class FMVVMPreviewModule : public IModuleInterface
{
public:
    static const FLazyName BindingMessageLogName;

    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    TSharedPtr<UE::MVVM::Private::FMVVMWidgetPreviewExtension> WidgetPreviewExtension;
};
```

**ModelViewViewModelPreviewModule.cpp**
```cpp
#include "ModelViewViewModelPreviewModule.h"
#include "MVVMWidgetPreviewExtension.h"

const FLazyName FMVVMPreviewModule::BindingMessageLogName = TEXT("MVVMWidgetPreviewBindings");

void FMVVMPreviewModule::StartupModule()
{
    WidgetPreviewExtension = MakeShared<UE::MVVM::Private::FMVVMWidgetPreviewExtension>();
    // 此处省略了向 UMGWidgetPreview 模块注册扩展的代码
    // WidgetPreviewExtension->Register(...);
}

void FMVVMPreviewModule::ShutdownModule()
{
    if (WidgetPreviewExtension.IsValid())
    {
        WidgetPreviewExtension.Reset();
    }
}

IMPLEMENT_MODULE(FMVVMPreviewModule, ModelViewViewModelPreview)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ModelViewViewModel` | 提供 MVVM 核心框架（ViewModel， 绑定逻辑） |
| `UMGWidgetPreview` | 提供 UMG 控件预览的基础框架和编辑器工具包 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏更新，无功能变化 |
| 2025-12-23 | `b3775500` | UMG MVVM Previewer: There's now an option to default construct missing viewmodels when the preview is started. | 预览时支持自动创建缺失的 ViewModel 实例 |
| 2025-12-10 | `01d01ea2` | UMG MVVM Widget Preview: You can now dump the current viewmodel data to a json file. | 新增将当前 ViewModel 数据导出为 JSON 文件的功能 |
| 2025-12-03 | `6cc231b5` | UMG MVVM: Bindings debugger | 添加了绑定调试器功能 |
| 2024-11-22 | `36771d79` | Updated uplugin descriptor files marked as both Experimental and Beta. Plugins with both flags in the ... | 修正插件描述符标志，将同时标记为实验性和Beta的改为仅Beta |

### 维护评价

该插件**处于活跃维护中**。
- **创建时间**：2024年8月，是一个相对较新的功能。
- **更新频率**：在2025年12月有连续的功能性更新（导出JSON、调试器、自动构造ViewModel），表明正在积极开发。
- **功能状态**：标记为 **Beta**（`IsBetaVersion=true`）且**默认不启用**（`EnabledByDefault=false`），意味着它尚未达到稳定发布状态，功能可能不完善，接口也可能变更，适合尝鲜和实验性使用。
- **推荐**：对于使用 UE5 MVVM 框架进行 UMG 开发并需要高级调试功能的团队，推荐在开发环境中启用此插件以提升调试效率。不建议在需要绝对稳定性的生产环境中依赖此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ModelViewViewModelPreview)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/umg-view-model-mvvm-in-unreal-engine/) (MVVM 框架文档，非此插件专属)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ModelViewViewModelPreview/Tests) (当前插件目录下无独立测试文件)