# DirectLink Extension Editor

> Editor UI for DirectLink source management.

| 属性 | 值 |
|---|---|
| 中文名 | DirectLink 编辑器扩展 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DirectLinkExtensionEditor` (Runtime), `DirectLinkExtension` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter/Source/DirectLinkExtensionEditor) | |

## 用途

此模块是 **Datasmith Importer** 插件的一部分，专门提供**编辑器（Editor）环境下的用户界面**，用于管理和选择 DirectLink 外部数据源。它解决了以下核心问题：

1.  **可视化源选择**：提供一个标准对话框，让用户从当前网络中可用的 DirectLink 外部源列表中进行选择。
2.  **资产状态指示**：在内容浏览器中为已导入的资产添加额外的缩略图指示器（如同步状态），直观地显示其与 DirectLink 源的连接和同步状态。
3.  **内容浏览器过滤**：添加一个专门的过滤器，用于快速查找通过 DirectLink 源导入的所有资产。

简单来说，它是 `DirectLinkExtension` 运行时模块的“编辑器界面层”，为设计师和美术师提供了操作 DirectLink 数据流所需的可视化工具。

## 使用场景

-   **实时设计评审**：你正在使用 3ds Max 或其他支持 Datasmith 的软件进行设计，并希望通过 DirectLink 实时将场景同步到 Unreal Engine 中。你需要一个对话框来选择 Max 中正在运行的场景源。
-   **资产同步状态监控**：你的项目通过 DirectLink 同步了大量 CAD 或 BIM 模型资产。你需要在内容浏览器中一眼看出哪些资产是“最新”的（绿色对勾），哪些是“过期”的（黄色警告），以便进行手动同步。
-   **资产管理和查找**：你需要快速筛选出所有通过 DirectLink 方式导入的资产，而不是手动查找，以便进行统一的重新导入或清理。

## 蓝图用法

此模块主要为编辑器提供 C++ 和 Slate UI 服务，蓝图中可直接调用的功能节点较少。最核心的功能（如弹出源选择对话框）需要通过 C++ 调用模块接口实现。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DisplayDirectLinkSourcesDialog` | 弹出一个模态对话框，显示可用的 DirectLink 外部源列表，允许用户选择一个。返回值为选中的 `FDirectLinkExternalSource` 共享指针，若取消则为空。 | `IDirectLinkExtensionEditorModule` |
| （过滤器）`DirectLink` | 在内容浏览器的“过滤器”下拉列表中，可使用此过滤器筛选出所有通过 DirectLink 导入的资产。 | `UDirectLinkSourceSearchFilter` |

### 使用示例（蓝图描述）

由于核心对话框功能需要通过 C++ 访问模块接口调用，典型的蓝图使用场景集中在资产过滤：
1.  打开内容浏览器。
2.  在内容浏览器顶部的搜索栏左侧，点击“过滤器”下拉菜单。
3.  在列表中找到并勾选“`DirectLink`”。
4.  内容浏览器视图将立即更新，仅显示那些通过 DirectLink 源导入的资产。

## C++ 用法

### 头文件引入

```cpp
#include "DirectLinkExtensionEditorModule.h"
```

### 基本用法

获取 `IDirectLinkExtensionEditorModule` 单例并调用其核心方法。

```cpp
// 来源: DirectLinkExtensionEditorModule.h
// 场景：在某个编辑器工具或菜单命令中，需要让用户选择一个 DirectLink 源。
if (IDirectLinkExtensionEditorModule::IsAvailable())
{
    // 获取模块引用
    IDirectLinkExtensionEditorModule& DirectLinkEditorModule = IDirectLinkExtensionEditorModule::Get();
    
    // 弹出源选择对话框
    TSharedPtr<UE::DatasmithImporter::FDirectLinkExternalSource> SelectedSource = DirectLinkEditorModule.DisplayDirectLinkSourcesDialog();
    
    if (SelectedSource.IsValid())
    {
        // 用户选择了某个源，可以进行后续操作，例如绑定、同步等
        UE_LOG(LogTemp, Log, TEXT("用户选择了 DirectLink 源: %s"), *SelectedSource->GetSourceName());
        // ... 使用 SelectedSource 进行数据同步等 ...
    }
    else
    {
        // 用户取消了对话框
        UE_LOG(LogTemp, Log, TEXT("用户取消了 DirectLink 源选择。"));
    }
}
```

### 进阶用法

覆盖 URI 解析器，以自定义在特定上下文中如何解析 DirectLink 源 URI（例如，是否使用自定义对话框）。

```cpp
// 来源: DirectLinkExtensionEditorModule.h, DirectLinkUriResolverInEditor.h
// 场景：希望在插件或自定义编辑器工具中，用自己实现的对话框替代默认的“选择DirectLink源”对话框。
class FMyCustomDirectLinkResolver : public UE::DatasmithImporter::FDirectLinkUriResolver
{
public:
    virtual TSharedPtr<UE::DatasmithImporter::FExternalSource> BrowseExternalSource(const UE::DatasmithImporter::FSourceUri& DefaultSourceUri) const override
    {
        // 实现自定义的源浏览逻辑
        // 例如：弹出自己设计的 Slate 窗口，或者从配置文件读取源。
        return MyCustomSourceSelectionLogic();
    }
};

// 注册自定义解析器
if (IDirectLinkExtensionEditorModule::IsAvailable())
{
    auto MyResolver = MakeShared<FMyCustomDirectLinkResolver>();
    IDirectLinkExtensionEditorModule::Get().OverwriteUriResolver(MyResolver.ToSharedRef());
}
```

## Demo 示例

一个最小的编辑器工具类，展示如何集成 DirectLink 源选择对话框。

```cpp
// MyDirectLinkTool.h
#pragma once
#include "CoreMinimal.h"

class FMyDirectLinkTool
{
public:
    /** 打开一个对话框，让用户选择 DirectLink 源，并打印其信息。 */
    static void SelectAndLogDirectLinkSource();
};
```

```cpp
// MyDirectLinkTool.cpp
#include "MyDirectLinkTool.h"
#include "DirectLinkExtensionEditorModule.h"

void FMyDirectLinkTool::SelectAndLogDirectLinkSource()
{
    // 确保模块可用
    if (!IDirectLinkExtensionEditorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("DirectLinkExtensionEditor 模块未加载。"));
        return;
    }

    // 调用模块接口显示对话框
    TSharedPtr<UE::DatasmithImporter::FDirectLinkExternalSource> SelectedSource =
        IDirectLinkExtensionEditorModule::Get().DisplayDirectLinkSourcesDialog();

    if (SelectedSource.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("成功选择 DirectLink 源!"));
        UE_LOG(LogTemp, Log, TEXT("  源名称: %s"), *SelectedSource->GetSourceName());
        // 更多源信息可以从 SelectedSource 对象中获取...
    }
    else
    {
        UE_LOG(LogTemp, Log, TEXT("用户取消了选择。"));
    }
}
```

## 模块依赖

要使用 `DirectLinkExtensionEditor` 模块，你的项目或插件模块通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `DirectLinkExtension` | DirectLink 扩展的核心运行时模块，提供 `IDirectLinkManager`、`FDirectLinkExternalSource` 等基础类型。 |
| `ContentBrowser` | 内容浏览器核心模块，用于集成资产视图状态指示器和扩展过滤器。 |
| `Slate` / `SlateCore` | 用于构建所有 UI 组件（对话框、列表、指示器图标）。 |
| `EditorStyle` | 提供编辑器标准样式，用于 UI 控件。 |
| `PropertyEditor` | （可选）如果需要扩展资产属性面板等。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点的编译警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 宏。 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introd... | 废弃了包含布尔参数的旧对象迭代函数，引入新函数。 |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 清理代码，确保修改纹理属性时正确使用 PreEditChange/PostEditChange。 |
| 2026-03-05 | `1adb9f68` | New material translator work: | 新的材质翻译器相关工作。 |

### 维护评价

该模块作为企业级 Datasmith 工作流的关键组成部分，**仍在积极维护中**。
-   **活跃度**：最近一年内有多次代码更新，主要是编译警告修复、API 现代化（日志宏、对象迭代器）和代码清理，表明它与引擎其他部分同步维护。
-   **稳定性**：更新内容多为底层维护和兼容性修复，没有引入破坏性变更或重大新功能，说明其功能已经成熟稳定。
-   **推荐使用**：对于需要使用 DirectLink 功能进行实时数据同步的项目，此模块是**推荐使用**的。它提供了必要的编辑器集成，且处于良好的维护状态。需注意其 `EnabledByDefault: false`，需在项目设置中手动启用 `DatasmithImporter` 插件。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter/Source/DirectLinkExtensionEditor)
-   [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
-   [父插件源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter)