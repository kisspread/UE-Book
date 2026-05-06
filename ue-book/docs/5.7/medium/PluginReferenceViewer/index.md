# Plugin Reference Viewer

> Editor plugin for viewing plugin references.

| 属性 | 值 |
|---|---|
| 中文名 | 插件引用查看器 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PluginReferenceViewer` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-31 |
| 年龄标签 | 🆕（约1年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PluginReferenceViewer) | |

## 用途

该插件为编辑器提供可视化插件引用关系的图形界面。它并不修改运行时行为，而是帮助开发者理解插件之间的依赖与被依赖关系。通过交互式的图表和工具函数，你可以：

- 查看某个插件依赖了哪些其他插件（引用链）
- 查看哪些插件依赖了该插件（被引用链）
- 分析依赖深度、是否出现重复引用
- 导出依赖数据为 CSV 文件
- 追踪从插件 A 到插件 B 是否存在依赖路径
- 查找声明特定 Gameplay Tag 的插件

为什么存在？在大型项目（尤其是多人协作或模块化项目）中，插件数量可能非常多，相互依赖关系复杂。纯文本方式无法直观展示依赖网络。该插件以图形式呈现，简化依赖分析，帮助避免循环依赖或冗余依赖。

## 使用场景

- 你正在清理项目中的插件依赖，需要找出哪些插件实际上没有被使用。
- 你想评估引入一个新插件是否会导致不必要的依赖链增长。
- 你需要向团队成员展示插件的依赖结构，或生成依赖报告。
- 你怀疑存在循环依赖导致编译出错，需要快速定位。
- 你需要在多个插件间追踪某个 Gameplay Tag 的定义来源。

## 蓝图用法

该插件为纯编辑器插件，未暴露任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。所有功能均通过编辑器 UI 或 C++ 调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 无 | 该插件不提供蓝图可调用接口 | — |

## C++ 用法

### 头文件引入

```cpp
#include "PluginReferenceViewerModule.h"
#include "PluginReferenceViewerUtils.h"
```

### 基本用法

#### 1. 打开插件引用查看器 UI（在脚本或工具栏扩展中调用）

```cpp
#include "PluginReferenceViewerModule.h"
#include "IPlugin.h"

void OpenPluginReferenceUI()
{
    // 假设你已经有一个插件实例
    TSharedPtr<IPlugin> MyPlugin = IPluginManager::Get().FindPlugin("MyPlugin");
    if (MyPlugin.IsValid())
    {
        FPluginReferenceViewerModule& Module = FModuleManager::LoadModuleChecked<FPluginReferenceViewerModule>("PluginReferenceViewer");
        Module.OpenPluginReferenceViewerUI(MyPlugin.ToSharedRef());
    }
}
```

来源：`Public/PluginReferenceViewerModule.h`

#### 2. 获取插件的资产依赖，并按持有插件分组

```cpp
#include "PluginReferenceViewerUtils.h"

TSharedPtr<IPlugin> TargetPlugin = IPluginManager::Get().FindPlugin("TargetPlugin");
if (TargetPlugin.IsValid())
{
    TArray<FAssetIdentifier> Dependencies = FPluginReferenceViewerUtils::GetAssetDependencies(TargetPlugin.ToSharedRef());
    TMap<FString, TArray<FAssetIdentifier>> ByPlugin = FPluginReferenceViewerUtils::SplitByPlugins(TargetPlugin.ToSharedRef(), Dependencies);
    for (const auto& Pair : ByPlugin)
    {
        UE_LOG(LogTemp, Log, TEXT("Plugin %s has %d assets depending on %s"), *TargetPlugin->GetName(), Pair.Value.Num(), *Pair.Key);
    }
}
```

来源：`Public/PluginReferenceViewerUtils.h`

#### 3. 导出插件依赖统计到 CSV

```cpp
TArray<FString> PluginNames = { "PluginA", "PluginB", "PluginC" };
FPluginReferenceViewerUtils::ExportPlugins(PluginNames, TEXT("D:\\DependencyReport.csv"));
```

来源：`Public/PluginReferenceViewerUtils.h`

#### 4. 追踪两个插件之间的依赖路径

```cpp
FString OutPath;
bool bExists = FPluginReferenceViewerUtils::TracePluginChain("PluginStart", "PluginEnd", OutPath);
if (bExists)
{
    UE_LOG(LogTemp, Log, TEXT("Path found: %s"), *OutPath);
}
else
{
    UE_LOG(LogTemp, Warning, TEXT("No dependency path from PluginStart to PluginEnd"));
}
```

来自 `Public/PluginReferenceViewerUtils.h`

### 进阶用法

结合 `FindGameplayTagSourcePlugins` 和导出工具，快速生成自定义报告：

```cpp
FName TagName = "Gameplay.Player.Combat";
TArray<TSharedRef<IPlugin>> SourcePlugins = FPluginReferenceViewerUtils::FindGameplayTagSourcePlugins(TagName);
if (SourcePlugins.Num() > 0)
{
    TArray<FString> PluginNames;
    for (const auto& Plugin : SourcePlugins)
    {
        PluginNames.Add(Plugin->GetName());
    }
    FPluginReferenceViewerUtils::ExportPlugins(PluginNames, FString::Printf(TEXT("TagSources_%s.csv"), *TagName.ToString()));
}
```

## Demo 示例

以下是一个完整的 C++ 编辑器模块示例，演示如何在自定义 UI 按钮点击时打开插件引用查看器。

**PluginRefViewerDemo.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"

DECLARE_LOG_CATEGORY_EXTERN(LogPluginRefViewerDemo, Log, All);

class FPluginRefViewerDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void OnMyButtonClicked();
};
```

**PluginRefViewerDemo.cpp**

```cpp
#include "PluginRefViewerDemo.h"
#include "PluginReferenceViewerModule.h"
#include "IPluginManager.h"
#include "Framework/MultiBox/MultiBoxBuilder.h"
#include "Widgets/SWindow.h"

IMPLEMENT_MODULE(FPluginRefViewerDemoModule, PluginRefViewerDemo)
DEFINE_LOG_CATEGORY(LogPluginRefViewerDemo);

void FPluginRefViewerDemoModule::StartupModule()
{
    // 注册一个扩展，例如在插件浏览器中添加按钮
    // 此处仅演示核心调用逻辑
}

void FPluginRefViewerDemoModule::ShutdownModule()
{
}

void FPluginRefViewerDemoModule::OnMyButtonClicked()
{
    // 获取目标插件（例如第一个加载的非引擎插件）
    TArray<TSharedRef<IPlugin>> Plugins = IPluginManager::Get().GetDiscoveredPlugins();
    for (const auto& Plugin : Plugins)
    {
        if (Plugin->GetType() != EPluginType::Engine)
        {
            // 打开引用查看器
            FPluginReferenceViewerModule& Module = FModuleManager::LoadModuleChecked<FPluginReferenceViewerModule>("PluginReferenceViewer");
            Module.OpenPluginReferenceViewerUI(Plugin);
            break;
        }
    }
}
```

## 模块依赖

如果要使用此插件的 C++ API（例如在你的编辑器模块中调用 `FPluginReferenceViewerUtils`），需要在你的 `Build.cs` 中添加以下依赖。由于插件本身为编辑器插件，通常仅在编辑器模块中使用。

| 模块 | 用途 |
|---|---|
| `AssetManagerEditor` | 提供资产标识符和资产管理相关功能 |
| `PluginUtils` | 提供插件查找、信息查询等工具函数 |
| `PluginBrowser` | 提供插件浏览器 UI 关联（便于从浏览器启动查看器） |

注意：`PluginReferenceViewer` 本身也是需要添加的依赖模块。

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "PluginReferenceViewer",
    "AssetManagerEditor",
    "PluginUtils",
    "PluginBrowser"
});
```

其他常见依赖（Core、CoreUObject、Engine、Slate、SlateCore、UnrealEd 等）会自动包含，无需额外添加。

## 维护状态

插件仍处于实验性阶段，但近期有活跃更新。

### 近期更新

- 2025-10-01 `6f23619b` Moved UEdGraphSchema asset reference filtering for drag and drop operations to their various implementations
- 2025-05-31 `52e3dac1` Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types
- 2025-04-29 `12054662` Show friendly plugin names in the plugin reference viewer
- 2025-04-11 `70ff78ff` [Truncation Warnings] Update EdGraphSchema and graph editor classes to use FVector2f
- 2025-03-31 `515ec7cd` [Truncation Warnings] Update SNodePanel and SGraphPanel to use FVector2f

### 维护评价

- **创建时间**：2025-03-31，距今约7个月，属于较新插件。
- **更新频率**：从历史记录看，几乎每个月都有功能性或适配性更新，最近一次在2025-10-01，维护活跃。
- **活跃度**：正在活跃维护，并且修复了图表拖放过滤、显示友好名称等用户体验改进。
- **已知问题**：当前为实验性插件（`IsExperimental=true`），API 和 UI 可能在未来版本中发生变化。不过核心功能已经可用。
- **推荐使用**：如果你需要在开发过程中可视化插件依赖关系，推荐启用使用。但请注意实验性标签，生产环境中做好版本兼容测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PluginReferenceViewer)
- [官方文档](https://docs.unrealengine.com/5.7/)（未提供独立的 DocsURL，可在引擎文档中搜索“插件引用查看器”）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PluginReferenceViewer/Tests)（若存在）