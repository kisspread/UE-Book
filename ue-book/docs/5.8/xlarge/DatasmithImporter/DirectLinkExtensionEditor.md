# Direct Link Extension Editor

> A simulated cable component.

| 属性 | 值 |
|---|---|
| 中文名 | Direct Link 编辑器扩展 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DirectLinkExtensionEditor` (Runtime), `DirectLinkExtension` (Runtime), `DatasmithImporter` (Runtime), `DatasmithTranslator` (Runtime), `DatasmithNativeTranslator` (Runtime), `DatasmithExternalSource` (Runtime), `ExternalSource` (Runtime), `DirectLinkTest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter) | |

## 用途

Direct Link Extension Editor 模块是 DatasmithImporter 企业插件的编辑器扩展组件，它主要解决以下问题：

1. **提供编辑器集成的 DirectLink 源浏览器**：在编辑器环境中为用户提供一个可视化界面，用于选择和连接可用的 DirectLink 外部源，简化了从 CAD/BIM 等设计软件通过 DirectLink 协议实时同步数据的工作流程。

2. **资产管理的 DirectLink 状态指示**：在内容浏览器中为导入的资产添加可视化状态指示（如图标和工具提示），让用户一目了然地识别资产的同步状态（最新、过时、自动重新导入等），提升资产管理和协作效率。

3. **内容浏览器过滤器扩展**：添加专门的内容浏览器前端过滤器，帮助用户快速筛选出通过 DirectLink 导入的资产，便于批量管理这些特定来源的资产。

4. **编辑器专用的 URI 解析器**：提供编辑器环境下的 URI 解析能力，当解析器被调用时，会自动弹出 DirectLink 源选择对话框，实现了更智能的源发现和连接机制。

这个模块的核心价值在于将 DirectLink 的实时协作能力无缝集成到 Unreal Editor 的内容浏览器和资产管理工作流中，使设计师和工程师能够更直观、高效地处理来自外部设计软件的实时数据更新。

## 使用场景

- **建筑/工程/施工 (AEC) 工作流**：建筑师在 Revit 或 Rhino 中修改设计，通过 DirectLink 实时同步到 Unreal，编辑器会自动显示更新状态并允许一键刷新。
- **工业设计/产品设计**：产品设计师在 SolidWorks 或 CATIA 中调整 3D 模型，通过 DirectLink 同步到 Unreal，编辑器资产浏览器显示哪些资产已过时需要更新。
- **汽车设计审查**：汽车设计师在 Alias 中完成造型调整，通过 DirectLink 发送到 Unreal 的虚拟展厅，编辑器过滤器可以帮助快速找到所有刚同步过来的资产。
- **BIM 数据管理**：在大型建筑项目中，通过 DirectLink 导入大量 BIM 数据，使用内容浏览器过滤器快速定位所有 DirectLink 资产进行批量检查或更新。

## 蓝图用法

由于这是一个编辑器扩展模块，主要提供编辑器界面功能，因此大部分 API 都是面向 C++ 的。以下是从源码中提取的主要蓝图相关节点：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DisplayDirectLinkSourcesDialog` | 显示一个对话框让用户选择可用的 DirectLink 外部源，返回选中的源或空指针 | `IDirectLinkExtensionEditorModule` |

### 使用示例（蓝图描述）

虽然这个模块主要是 C++ 实现，但可以通过蓝图与 C++ 类交互：

1. **在蓝图中访问 DirectLink 编辑器模块**：
   - 通过 `IDirectLinkExtensionEditorModule::Get()` 获取模块实例
   - 调用 `DisplayDirectLinkSourcesDialog()` 显示源选择对话框
   - 处理用户选择结果，连接到选定的 DirectLink 源

2. **在编辑器工具蓝图中**：
   - 创建自定义编辑器工具按钮
   - 按钮点击时调用 `DisplayDirectLinkSourcesDialog()`
   - 获取选中的源后，可以启动导入或同步操作

## C++ 用法

### 头文件引入

```cpp
#include "DirectLinkExtensionEditorModule.h"
#include "DirectLinkExtensionUI.h"
#include "SDirectLinkAvailableSource.h"
```

### 基本用法

```cpp
// 来源：Source/DirectLinkExtensionEditor/Private/DirectLinkExtensionUI.h

// 获取 DirectLink 编辑器模块
if (IDirectLinkExtensionEditorModule::IsAvailable())
{
    IDirectLinkExtensionEditorModule& DirectLinkModule = IDirectLinkExtensionEditorModule::Get();
    
    // 获取 DirectLink 管理器
    UE::DatasmithImporter::IDirectLinkManager& Manager = DirectLinkModule.GetManager();
    
    // 显示源选择对话框
    TSharedPtr<UE::DatasmithImporter::FDirectLinkExternalSource> SelectedSource = 
        DirectLinkModule.DisplayDirectLinkSourcesDialog();
    
    if (SelectedSource.IsValid())
    {
        // 用户选择了源，可以进行后续操作
        UE_LOG(LogTemp, Log, TEXT("Selected DirectLink source: %s"), 
            *SelectedSource->GetSourceName().ToString());
    }
}
```

### 进阶用法

```cpp
// 来源：Source/DirectLinkExtensionEditor/Private/DirectLinkUriResolverInEditor.h

// 创建自定义 URI 解析器并覆盖默认行为
class FMyCustomUriResolver : public UE::DatasmithImporter::IUriResolver
{
public:
    virtual TSharedPtr<UE::DatasmithImporter::FExternalSource> BrowseExternalSource(
        const UE::DatasmithImporter::FSourceUri& DefaultSourceUri) const override
    {
        // 可以在这里添加自定义逻辑
        if (ShouldUseCustomResolver(DefaultSourceUri))
        {
            return ResolveCustomSource(DefaultSourceUri);
        }
        
        // 回退到默认的编辑器对话框
        return IDirectLinkExtensionEditorModule::Get().DisplayDirectLinkSourcesDialog();
    }
};

// 注册自定义解析器
if (IDirectLinkExtensionEditorModule::IsAvailable())
{
    auto MyResolver = MakeShared<FMyCustomUriResolver>();
    IDirectLinkExtensionEditorModule::Get().OverwriteUriResolver(MyResolver);
}
```

## Demo 示例

### 头文件示例

```cpp
// MyDirectLinkManager.h
#pragma once

#include "CoreMinimal.h"
#include "DirectLinkExtensionEditorModule.h"

class FMyDirectLinkManager
{
public:
    void ShowDirectLinkSourceDialog();
    void CheckDirectLinkStatus();
    
private:
    TSharedPtr<UE::DatasmithImporter::FDirectLinkExternalSource> CurrentSource;
};
```

### 实现文件示例

```cpp
// MyDirectLinkManager.cpp
#include "MyDirectLinkManager.h"
#include "DirectLinkExtensionEditorModule.h"

void FMyDirectLinkManager::ShowDirectLinkSourceDialog()
{
    if (!IDirectLinkExtensionEditorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("DirectLink Extension Editor module is not available"));
        return;
    }
    
    IDirectLinkExtensionEditorModule& Module = IDirectLinkExtensionEditorModule::Get();
    
    // 显示 DirectLink 源选择对话框
    TSharedPtr<UE::DatasmithImporter::FDirectLinkExternalSource> SelectedSource = 
        Module.DisplayDirectLinkSourcesDialog();
    
    if (SelectedSource.IsValid())
    {
        CurrentSource = SelectedSource;
        UE_LOG(LogTemp, Log, TEXT("Connected to DirectLink source: %s"), 
            *SelectedSource->GetSourceName().ToString());
        
        // 这里可以添加启动同步或导入的逻辑
    }
    else
    {
        UE_LOG(LogTemp, Log, TEXT("DirectLink source selection was cancelled"));
    }
}

void FMyDirectLinkManager::CheckDirectLinkStatus()
{
    if (!IDirectLinkExtensionEditorModule::IsAvailable())
    {
        return;
    }
    
    IDirectLinkExtensionEditorModule& Module = IDirectLinkExtensionEditorModule::Get();
    UE::DatasmithImporter::IDirectLinkManager& Manager = Module.GetManager();
    
    // 这里可以查询连接状态、源信息等
    // 具体 API 需要参考 IDirectLinkManager 接口
}
```

## 模块依赖

从源码分析，DirectLinkExtensionEditor 模块依赖以下特定模块（除了常见的 Core/Engine/Slate 模块）：

| 模块 | 用途 |
|---|---|
| `DirectLinkExtension` | DirectLink 扩展核心模块，提供 DirectLink 管理器和 URI 解析器基础接口 |
| `DatasmithImporter` | Datasmith 导入器核心模块，提供外部源管理和导入功能 |
| `DatasmithTranslator` | Datasmith 翻译器模块，提供资产翻译和转换功能 |
| `DatasmithNativeTranslator` | Datasmith 原生翻译器，处理特定格式的直接翻译 |
| `DatasmithExternalSource` | 外部源管理模块，处理 DirectLink 连接和数据同步 |
| `ExternalSource` | 外部源抽象层，提供通用的外部源接口 |
| `DirectLinkTest` | DirectLink 测试模块（可能包含测试工具和功能） |

**注**：由于这是企业插件，还可能依赖 Datasmith 其他相关模块。在项目中使用时，需要在 Build.cs 中正确设置模块依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断到浮点数的警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到 UE_LOGF 新格式 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introduced... | 废弃了包含 bIncludeNestedObjects 参数的 GetObjects*/ForEachObjectWithOuter 函数，引入新版本 |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 清理纹理属性修改代码，按需在 PreEditChange/PostEditChange 中封装 |
| 2026-03-05 | `1adb9f68` | New material translator work: | 新的材质翻译器工作 |

### 维护评价

**活跃维护**：DatasmithImporter 是 Epic Games 维护的企业级插件，专门用于支持工业设计和 BIM 数据导入工作流。DirectLinkExtensionEditor 模块作为其编辑器扩展部分，虽然更新频率不是特别高（最近几次更新集中在编译警告修复和 API 清理），但仍在持续维护中。

**推荐使用**：如果您的项目需要从 CAD/BIM 软件通过 DirectLink 协议实时同步数据，并且希望在编辑器中有更好的资产状态管理和工作流集成，推荐启用此模块。

**注意事项**：
1. 此插件默认未启用（`EnabledByDefault: false`），需要在插件管理器中手动启用。
2. 作为企业插件，可能在某些 Unreal Engine 发行版中不包含（如订阅制的企业功能）。
3. 最近的更新主要是编译器警告修复和 API 清理，没有重大功能变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [DirectLinkExtensionEditor 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter/Source/DirectLinkExtensionEditor)