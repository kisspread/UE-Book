# Directory Placeholder

> Adds a lightweight Directory Placeholder asset type, which can be added to otherwise empty folders in order to add them to source control.

| 属性 | 值 |
|---|---|
| 分类 | Source Control |
| 默认启用 | 否 |
| 包含内容 | 否 |
| 模块 | DirectoryPlaceholder (Editor) |
| 创建时间 | 2025-01-29 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/DirectoryPlaceholder) | |

## 用途

这个 plugin 解决了一个 Git 工作流中的经典痛点：**Git 不追踪空目录**。

在 UE 项目中使用 Git 进行源码管理时，如果你在 Content Browser 中创建了一个空文件夹，Git 不会把它加入版本控制。当你提交代码并让队友 pull 下来后，那些空文件夹就消失了。

Directory Placeholder 的做法非常简单：在每个新创建的空文件夹中自动生成一个名为 `UE_Placeholder` 的轻量占位资产。这个 `.uasset` 文件让 Git（或其他版本控制系统）能够追踪这个目录。当文件夹中有了真正的资产后，占位资产会被自动清理掉。

## 使用场景

- 你的团队使用 Git 管理 UE 项目，且项目中有很多预设的目录结构（如 `Characters/`、`Weapons/`、`UI/` 等），需要在版本控制中保留这些空目录
- 你想在项目模板中预建目录结构，确保所有人 clone 后看到相同的目录布局
- 你需要一个自动化的方案来维护目录占位，不想手动管理一堆空的 `.gitkeep` 文件

## 编辑器用法

### 自动创建

插件默认启用后，会在以下目录监听新文件夹的创建事件，并自动生成占位资产：

- **项目 Content 目录**（`/Game/`）— 即项目的 `Content/` 文件夹
- **项目 Plugins 目录** — 即项目根目录下的 `Plugins/` 文件夹
- **额外插件目录** — 项目设置中配置的 Additional Plugin Directories

### 自动清理

当一个目录中已经有了真正的资产（非占位资产）时，该目录中的占位资产不再需要。你可以通过以下方式清理：

1. **右键菜单清理**：在 Content Browser 中右键点击文件夹 → 选择 **"Cleanup Directory Placeholders"**，会递归清理该文件夹及其子文件夹中不再需要的占位资产
2. **自动删除**：当删除一个只包含占位资产的文件夹时，占位资产会被自动删除

### 内容浏览器过滤器

Content Browser 中提供了一个内置过滤器 **"Show Directory Placeholders"**，默认会隐藏占位资产，避免它们干扰你的资产浏览体验。

### 设置项

通过 **Editor Preferences → Directory Placeholder** 可以配置以下选项：

| 设置 | 默认值 | 说明 |
|---|---|---|
| `bAutomaticallyCreatePlaceholders` | `true` | 总开关，是否自动创建占位资产 |
| `bAutomaticallyCreatePlaceholdersInProjectContent` | `true` | 是否在项目 Content 目录中自动创建 |
| `bAutomaticallyCreatePlaceholdersInProjectPlugins` | `true` | 是否在项目 Plugins 目录中自动创建 |
| `bAutomaticallyCreatePlaceholdersInAdditionalPlugins` | `true` | 是否在额外插件目录中自动创建 |
| `ExcludePaths` | 空 | 排除路径列表，这些路径下不会自动创建占位资产（使用 Content Browser 路径格式，如 `/Game/MyFolder/`） |

## C++ 用法

### 头文件引入

```cpp
#include "DirectoryPlaceholderUtils.h"
```

### 基本用法

`UDirectoryPlaceholderLibrary` 提供了蓝图和 C++ 均可调用的静态工具函数：

```cpp
// 清理指定路径下不再需要的占位资产（只在目录中还有其他资产时才删除占位资产）
UDirectoryPlaceholderLibrary::CleanupPlaceholdersInPath(TEXT("/Game/MyFolder"));

// 批量清理多个路径
TArray<FString> Paths = { TEXT("/Game/Characters"), TEXT("/Game/Weapons") };
UDirectoryPlaceholderLibrary::CleanupPlaceholdersInPaths(Paths);

// 强制删除指定路径下所有占位资产（不管目录中是否有其他资产）
UDirectoryPlaceholderLibrary::DeletePlaceholdersInPath(TEXT("/Game/MyFolder"));
```

> **来源**: `Source/DirectoryPlaceholder/Private/DirectoryPlaceholderUtils.cpp`

### 清理逻辑说明

`CleanupPlaceholdersInPath` 的工作方式是递归的：

1. 先递归处理所有子文件夹
2. 检查当前文件夹中是否有非占位资产，或者子文件夹中是否有资产
3. 如果当前文件夹（或其子文件夹）中存在真正的资产，则删除当前文件夹中的占位资产
4. 如果当前文件夹是纯空（只有占位资产），则保留占位资产

注意：清理操作仅适用于 `/Game/` 路径下的目录。

> **来源**: `Source/DirectoryPlaceholder/Private/DirectoryPlaceholderUtils.cpp` — `CleanupPlaceholdersInternal()`

## Demo 示例

由于这是一个纯编辑器工具型 plugin，没有运行时组件，因此不需要额外的 Build.cs 配置。你只需在编辑器中启用插件即可。

如果你想在自己的编辑器工具或 Blueprint 中使用清理功能：

**Blueprint 用法**：

1. 打开任意 Blueprint 图表
2. 搜索 `Cleanup Directory Placeholders` 或 `Delete Directory Placeholders`
3. 拖出 `Cleanup Directory Placeholders In Path` 节点，传入要清理的路径即可

**C++ 编辑器工具用法**：

```cpp
// MyEditorTool.cpp
#include "DirectoryPlaceholderUtils.h"

void UMyEditorTool::CleanupMyFolder()
{
    // 清理 /Game/MyFolder 及其子目录中不再需要的占位资产
    UDirectoryPlaceholderLibrary::CleanupPlaceholdersInPath(TEXT("/Game/MyFolder"));
}
```

## 模块依赖

该插件没有公开的 PublicDependencyModuleNames。它是一个纯编辑器插件，所有依赖都在 Private 中：

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型和日志 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `UnrealEd` | 编辑器框架 |
| `AssetDefinition` | 资产类型定义 |
| `ContentBrowser` | Content Browser 集成 |
| `ContentBrowserData` | Content Browser 数据访问 |
| `DeveloperSettings` | 项目设置集成 |
| `Slate` / `SlateCore` | UI 框架 |
| `ToolMenus` | 编辑器菜单扩展 |
| `Projects` | 项目和插件目录管理 |

由于所有依赖都是 Private，外部模块不需要（也无法）直接依赖此插件。如果你需要在自己的代码中调用清理功能，需要将 `DirectoryPlaceholder` 添加到你的模块的 PrivateDependencyModuleNames。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-09-29 | `4bb05c7373c9` | 支持在额外插件目录自动创建占位；新增编辑器设置项控制创建范围；修复目录监听器注册/取消注册不匹配的问题；扩展 OnDeleteFolders 支持从任意目录删除纯占位文件夹 | 功能增强 + Bug 修复，扩展了插件的适用范围 |
| 2025-09-12 | `8e9db1854c53` | 修复占位资产意外创建在 ExternalActors 和 ExternalObjects 文件夹中的问题；新增排除路径列表项目设置 | 重要 Bug 修复，防止 LWC 场景中的脏数据 |
| 2025-05-16 | `28ae7a113331` | 修复批量创建占位资产时逐个保存导致的崩溃问题，改为一次性调用 SavePackages | 稳定性修复 |

### 维护评价

- **创建时间**：2025-01-29，约 1 年前
- **最近更新**：2025-09-29（约 7 个月前），有实质性功能更新
- **维护状态**：**维护中** — 功能在持续完善，近期有新特性和 Bug 修复
- **注意事项**：`.uplugin` 中标记为 `IsExperimentalVersion: true`，说明 Epic 仍将其视为实验性功能
- **推荐程度**：如果你的团队使用 Git 管理 UE 项目，强烈推荐启用。虽然标记为实验性，但代码质量良好，功能聚焦且实用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/DirectoryPlaceholder)
- [官方文档]()（暂无）
