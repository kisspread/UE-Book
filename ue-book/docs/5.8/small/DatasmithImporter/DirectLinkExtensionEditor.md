# Datasmith Importer

> Importer for Datasmith files.

| 属性 | 值 |
|---|---|
| 中文名 | Datasmith 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithExternalSource` (Runtime), `DatasmithImporter` (Runtime), `DatasmithNativeTranslator` (Runtime), `DatasmithTranslator` (Runtime), `DirectLinkExtension` (Runtime), `DirectLinkExtensionEditor` (Runtime), `DirectLinkTest` (Runtime), `ExternalSource` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter) | |

## 用途

`DatasmithImporter` 插件的核心并非简单的“导入器”，它是一个**企业级 CAD/BIM 数据管理套件**，其核心功能围绕 **Datasmith DirectLink** 技术展开。DirectLink 允许 Unreal Engine 与外部 CAD/BIM 软件（如 SolidWorks, Revit, Navisworks 等）建立**实时双向链接**。

**主要解决的问题：**
1.  **实时同步**：当在外部软件中修改模型时，Unreal Engine 场景中的对应资产可以近乎实时地更新，无需手动重新导入整个文件。
2.  **数据溯源与管理**：追踪资产源自哪个外部源（DirectLink 源），并管理其同步状态（最新、过时、自动重新导入等）。
3.  **协作与审阅**：通过 DirectLink，团队成员可以在 Unreal Editor 内直接接收来自设计师的最新模型更新，用于实时审阅和可视化。

`DirectLinkExtensionEditor` 模块是此套件在**编辑器侧**的 UI 扩展，将 DirectLink 的状态信息（如同步状态指示器）集成到 Content Browser 中，并提供选择 DirectLink 源的对话框。

## 使用场景

-   **建筑、工程与施工（AEC）**：建筑师在 Revit 中修改墙体布局，Unreal 中的建筑可视化场景自动更新。
-   **工业设计与制造**：产品设计师在 SolidWorks 中调整零件形状，UE 中的产品配置器或营销视频实时反映更改。
-   **汽车设计**：造型师在 Alias 中细化曲面，UE 内的车辆渲染和 VR 评审环境同步更新。
-   **大型场景组装**：通过 DirectLink 从多个不同的 CAD/BIM 工具同步资产，整合到一个统一的虚拟场景中。

## 蓝图用法

`DirectLinkExtensionEditor` 模块本身不暴露大量蓝图函数，但提供了编辑器 UI 扩展和一个用于内容浏览器的搜索过滤器。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DisplayDirectLinkSourcesDialog` | 显示一个对话框，让用户从可用的 DirectLink 外部源中选择一个。返回选中的源对象。 | `IDirectLinkExtensionEditorModule` (C++ 接口) |
| `AddFrontEndFilterExtensions` | 为内容浏览器添加一个名为“DirectLink 来源”的前端过滤器，用于筛选出通过 DirectLink 导入的资产。 | `UDirectLinkSourceSearchFilter` |

### 使用示例（蓝图描述）

1.  **在内容浏览器中筛选 DirectLink 资产**：此功能通过 `UDirectLinkSourceSearchFilter` 自动集成。在 Content Browser 的搜索栏中，你可以找到并启用“DirectLink 来源”过滤器，快速隔离出所有由 DirectLink 同步管理的资产。
2.  **编程式选择 DirectLink 源**：在 C++ 编辑器工具中，你可以调用 `IDirectLinkExtensionEditorModule::Get().DisplayDirectLinkSourcesDialog()` 来弹出一个源选择窗口，并将返回的 `TSharedPtr<FDirectLinkExternalSource>` 用于后续的同步或检查操作。

## C++ 用法

`DirectLinkExtensionEditor` 模块主要扩展了编辑器功能，其 API 用于与 UI 和内容浏览器交互。

### 头文件引入

```cpp
#include "DirectLinkExtensionEditorModule.h"
```

### 基本用法

```cpp
// 检查 DirectLink Editor 模块是否可用
if (IDirectLinkExtensionEditorModule::IsAvailable())
{
    // 获取模块单例
    IDirectLinkExtensionEditorModule& EditorModule = IDirectLinkExtensionEditorModule::Get();
    
    // 调用一个需要 DirectLink 管理器的功能（例如，查询源状态）
    // UE::DatasmithImporter::IDirectLinkManager& Manager = EditorModule.GetManager();
}
```

### 进阶用法

结合资产数据，检查其是否与 DirectLink 源同步，并显示状态图标（由该模块内部处理，开发者可扩展或响应状态）：

```cpp
// 假设你有一个 FAssetData 对象
FAssetData MyAsset = ...; // 通过内容浏览器或其他方式获取

// DirectLinkExtensionEditor 模块会自动在内容浏览器中为有 DirectLink 链接的资产显示状态指示器。
// 开发者可以通过监听资产属性变化或 DirectLink 事件来响应同步状态变更，例如：
if (MyAsset.GetClass()->ImplementsInterface(UDirectLinkSyncable::StaticClass()))
{
    // 执行与同步状态相关的逻辑
}
```

## Demo 示例

以下示例展示了如何在自定义编辑器工具按钮中调用 DirectLink 源选择对话框。

**MyEditorTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FMyEditorTool
{
public:
    void OpenDirectLinkSourceSelector();

private:
    TSharedPtr<class UE::DatasmithImporter::FDirectLinkExternalSource> SelectedSource;
};
```

**MyEditorTool.cpp**
```cpp
#include "MyEditorTool.h"
#include "DirectLinkExtensionEditorModule.h"

void FMyEditorTool::OpenDirectLinkSourceSelector()
{
    // 确保模块可用
    if (!IDirectLinkExtensionEditorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("DirectLinkExtensionEditor module is not available."));
        return;
    }

    // 弹出选择对话框
    SelectedSource = IDirectLinkExtensionEditorModule::Get().DisplayDirectLinkSourcesDialog();

    if (SelectedSource.IsValid())
    {
        // 用户选择了一个有效的 DirectLink 源
        UE_LOG(LogTemp, Log, TEXT("Selected DirectLink source: %s"), *SelectedSource->GetUri().ToString());
        // 在这里可以对 SelectedSource 进行进一步操作，如同步、检查状态等。
    }
    else
    {
        // 用户取消了对话框
        UE_LOG(LogTemp, Log, TEXT("DirectLink source selection was cancelled."));
    }
}
```

## 模块依赖

使用 `DirectLinkExtensionEditor` 模块或依赖此插件提供的编辑器功能，需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `DirectLinkExternalSource` | 提供 `FDirectLinkExternalSource` 核心类，表示一个 DirectLink 连接源。 |
| `DirectLinkExtension` | `DirectLinkExtensionEditor` 的基础模块，提供 `IDirectLinkExtensionModule` 接口。 |
| `ContentBrowser` | 用于在内容浏览器中添加资产视图扩展（状态指示器、工具提示）和前端过滤器。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数产生的警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移到 `UE_LOGF`。 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introduced ... | 废弃了接受 `bIncludeNestedObjects` 参数的 `GetObjects*`/`ForEachObjectWithOuter` 函数，并引入了新的替代API。 |
| 2026-03-06 | `7b69892a` | clean up code changing texture properties with wrapping in PreEditChange/PostEditChange as required. | 清理了修改纹理属性的代码，确保按照要求在 `PreEditChange`/`PostEditChange` 中进行包装。 |
| 2026-03-05 | `1adb9f68` | New material translator work: | 新材质转换器相关工作： |

### 维护评价

该插件最初于 2019 年创建，历史悠久。然而，从 Git 提交记录来看，**维护非常活跃**。最近一次代码更新（2026年5月）距离现在仅数月，且提交内容涉及编译警告修复、API 现代化（日志迁移、废弃旧API）和核心功能（材质翻译器）的改进，表明 Epic 仍在持续维护和优化此企业级插件。

**综合评价：**
- **年龄**：创建时间较早，但属于核心企业功能。
- **活跃度**：高，持续有实质性代码更新和优化。
- **状态**：稳定且被官方支持。
- **推荐**：**强烈推荐**给需要进行 CAD/BIM 数据实时同步的建筑、工程、制造和产品可视化项目。它是 Datasmith 工作流在编辑器内的关键 UI 和管理扩展。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- 测试用例：未在提供的文件分析中明确列出，通常位于 `Engine/Tests/` 或插件内的 `Tests/` 目录。