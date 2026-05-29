# In-Editor Documentation

> Navigate a configured tutorial within the Unreal Editor as you explore a project.

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器内文档 |
| 分类 | Learning |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `InEditorDocumentation` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-30 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/InEditorDocumentation) | |

## 用途

这个插件在虚幻编辑器内部嵌入了一个 Web 浏览器面板，让用户无需离开编辑器即可阅读项目配置的教程文档。它主要解决的问题是：

1. **编辑器内教程导航**：通过可配置的 URL 加载教程页面（默认指向 Stack-O-Bot 示例游戏教程），在编辑器停靠面板（Dock Tab）中直接展示 Web 内容，实现边看文档边操作编辑器的体验。
2. **EDC 文档搜索（实验性）**：当选中视口中的 Actor 时，可自动查询 Epic Developer Community（dev.epicgames.com）的文档 API，获取与该 Actor 相关的文档信息，帮助开发者快速找到对应资料。
3. **Toast 提醒**：首次打开项目时弹出通知提示用户查看教程，支持"不再提醒"选项。

本质上这是一个**学习辅助工具**，面向刚接触 Unreal Engine 或特定项目的新人，降低学习门槛。

## 使用场景

- 你正在制作一个教学模板项目（如 TP_UEIntro_BP），需要在编辑器中嵌入步骤式教程 → 用此插件
- 你想让团队成员在编辑器内直接查阅文档，而不是切换到浏览器 → 配置此插件的 TutorialUrl
- 你选中了一个 Actor 想快速查找相关文档 → 启用 EDC Search 功能

## 蓝图用法

该插件不暴露任何蓝图 API。它完全通过编辑器 UI 交互：

- **菜单入口**：Level Editor 菜单栏中注册了 `OpenTutorial`（打开教程）和 `OpenSearch`（EDC 搜索）两个命令
- **停靠面板**：教程和搜索分别以独立的 Dock Tab 形式展示，内嵌 `SWebBrowser` 控件
- **设置面板**：通过 Editor → Plugins → In-Editor Documentation 配置项修改行为

## C++ 用法

该插件不提供面向其他模块的 C++ 公开 API。它是自包含的编辑器模块，仅通过以下方式交互：

### 设置类

`UInEditorDocumentationSettings` 暴露了可配置属性，其他模块可通过读取设置获取配置：

```cpp
// 头文件引入
#include "InEditorDocumentationSettings.h"

// 获取设置对象
const UInEditorDocumentationSettings* Settings = GetDefault<UInEditorDocumentationSettings>();
FString TutorialURL = Settings->TutorialUrl;
bool bSearchEnabled = Settings->bEnableEdcSearch;
```

### 可配置项

| 属性 | 类型 | 说明 |
|---|---|---|
| `TutorialUrl` | `FString` | 教程页面 URL，默认指向 Stack-O-Bot 教程 |
| `bEnableEdcSearch` | `bool` | 是否启用 EDC 搜索功能（实验性） |
| `EdcSearchApiEndpoint` | `FString` | EDC 搜索 API 端点 |
| `DocumentationPages` | `TMap<FString, FString>` | 预定义的 Actor → 文档页面映射 |

### 命令注册

插件通过 `FDocumentationCommands` 注册了两个 UI 命令：

```cpp
#include "DocumentationCommands.h"

// 命令列表
// OpenTutorial  - 打开教程面板
// OpenSearch    - 打开 EDC 搜索面板
```

## Demo 示例

该插件不需要编写代码。启用插件后，在编辑器菜单中即可使用。如需自定义教程 URL，在项目设置中修改：

**Editor → Plugins → In-Editor Documentation → Tutorial URL**

如果要为特定 Actor 指定文档页面，在 `DocumentationPages` Map 中添加条目，键为 Actor 类名，值为对应的文档 URL。

## 模块依赖

### 插件依赖

| 插件 | 用途 |
|---|---|
| `WebBrowserWidget` | 提供编辑器内嵌 Web 浏览器控件 `SWebBrowser` |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-16 | `aea11131` | Clean up WebBrowser module and init settings, handle module init failures | 清理 WebBrowser 模块初始化逻辑，处理初始化失败情况 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 将 UE_LOG 迁移为 UE_LOGF 宏 |
| 2026-01-13 | `169be8cf` | [InEditorDocumentation] Limit URLs opened to EDC URLs | 限制仅允许打开 EDC 域名的 URL，增强安全性 |
| 2025-10-17 | `b6abea02` | Removing ChangeWebBrowserUserAgent to fix crash caused by calling too early. | 移除过早调用的 UserAgent 设置，修复崩溃问题 |
| 2025-10-03 | `56b3c176` | Fix potential issue with top-level const declaration, and update comment. | 修复顶层 const 声明的潜在问题并更新注释 |

### 维护评价

- **创建时间**：2025-09-30，非常年轻的插件
- **活跃度**：最近一次更新在 2026-04-16，过去 6 个月内有持续的功能改进和稳定性修复
- **状态**：标记为 Experimental，正在积极开发中
- **已知限制**：EDC Search 功能标记为实验性，默认关闭；URL 导航被限制为 EDC 域名
- **推荐**：适合用于教学模板项目或团队内部文档集成。由于是实验性插件，生产环境使用需谨慎，API 可能变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/InEditorDocumentation)
- 官方文档（暂无）