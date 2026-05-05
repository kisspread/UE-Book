# OneSky

> OneSky localization service

| 属性 | 值 |
|---|---|
| 分类 | Localization |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 否 |
| 模块 | OneSkyLocalizationService (Editor) |
| 创建时间 | 2015-05-21 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/OneSkyLocalizationService) | |

## 用途

OneSkyLocalizationService 是 UE5 内置本地化服务框架（`LocalizationService` 模块）的一个 **Provider 实现**，将 Unreal 的 Localization Dashboard 与 [OneSky](https://www.oneskyapp.com/) 翻译管理平台连接起来。

它解决的核心问题是：**在 UE 编辑器内直接完成翻译文件的上传/下载**，无需手动导出 `.po` 文件再上传到 OneSky 网站。具体来说：

- 将 UE 本地化目标（Localization Target）的源文本导出为 `.po` 文件并上传到 OneSky
- 从 OneSky 下载已翻译的 `.po` 文件并导入回 UE 本地化系统
- 支持按单个目标、目标集合（Target Set）批量操作
- 通过 OneSky API 管理项目组、项目、语言等

## 使用场景

- 你的项目需要多语言本地化，且使用 OneSky 作为翻译管理平台 → 用此插件
- 你希望在 Localization Dashboard 中一键导入/导出翻译，避免手动文件操作 → 用此插件
- 你需要在编辑器内查看翻译状态、管理 OneSky 项目 → 用此插件

## 蓝图用法

此插件没有暴露任何 BlueprintCallable 节点。它是一个纯 Editor 模块，通过 UE 的 Localization Dashboard UI 进行交互。

## 编辑器用法

### 启用插件

1. 打开 **Edit → Plugins**
2. 搜索 "OneSky"
3. 启用 **OneSky** 插件并重启编辑器

### 配置 API 凭据

1. 打开 **Localization Dashboard**（Window → Localization Dashboard）
2. 在 **Localization Service** 设置区域找到 OneSky 配置项：
   - **OneSky API Public Key** — 你的 OneSky 公钥
   - **OneSky API Secret Key** — 你的 OneSky 私钥
   - **Remember Secret Key (WARNING: saved unencrypted)** — 是否保存私钥（明文存储）

### 配置本地化目标

在 Localization Dashboard 中选择一个 Localization Target，在其详情面板中：

- **OneSky Project ID** — 对应 OneSky 上的项目 ID（纯数字）
- **OneSky File Name** — 该目标在 OneSky 上对应的文件名

### 导入/导出操作

配置完成后，Localization Target 和 Target Set 的工具栏会出现额外按钮：

| 按钮 | 功能 |
|---|---|
| Import All Cultures from OneSky | 从 OneSky 下载所有语言的翻译并导入 |
| Export All Cultures to OneSky | 将本地所有语言的翻译导出并上传到 OneSky |
| Import All Targets from OneSky | 批量导入 Target Set 中所有目标的翻译 |
| Export All Targets to OneSky | 批量导出 Target Set 中所有目标的翻译 |

> ⚠️ 导出操作会 **覆盖** OneSky 上的数据，且不可撤销，编辑器会弹出确认对话框。

> ⚠️ Engine Target Set 不支持导出（只能导入）。

## C++ 用法

此插件主要作为编辑器集成使用，不提供公开的 C++ API。如需以编程方式与 OneSky 交互，可通过 `ILocalizationServiceModule` 接口：

```cpp
#include "ILocalizationServiceModule.h"

// 获取当前本地化服务 provider
ILocalizationServiceProvider& Provider = ILocalizationServiceModule::Get().GetProvider();
```

## 模块依赖

此插件仅使用 `PrivateDependencyModuleNames`，不暴露公开依赖。内部依赖：

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、路径、线程 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `Slate` / `SlateCore` | 编辑器 UI |
| `LocalizationService` | 本地化服务框架（Provider 接口） |
| `Localization` | 本地化模块（目标管理） |
| `LocalizationCommandletExecution` | 本地化 Commandlet（导入/导出文本） |
| `Json` | 解析 OneSky API 响应 |
| `HTTP` | 调用 OneSky REST API |
| `Serialization` | 数据序列化 |
| `MainFrame` | 获取编辑器主窗口（进度对话框） |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-03-13 | `b059f7b` | 修复 trivial unreachable code warnings |
| 2023-10-12 | `ffb133e` | 将 FJsonObject 的 ANSI 字符串用法更新为 TCHAR，移除不必要的字符串转换 |
| 2023-01-16 | `bbc37aa` | IWYU 更新，减少不必要的 include |

### 维护评价

- **状态**: ⚠️ 维护不活跃
- 插件创建于 **2015 年 5 月**，已超过 10 年
- `.uplugin` 标记为 `IsBetaVersion: true`、`EnabledByDefault: false`
- 最近 3 次更新都是编译器警告修复和代码清理，**无功能性更新**
- 代码中多处有 `// TODO` 注释，表明功能从未完整实现
- 部分注册的 Worker（如 `ShowPhraseCollection`、`ListProjectTypes`）被注释掉了
- OneSky 平台本身仍在运营，但此插件的 API 集成可能不完全匹配 OneSky 当前版本

**建议**: 如果你的项目确实使用 OneSky 且需要编辑器内集成，可以尝试启用，但要做好调试和修改的准备。对于新项目，考虑使用更现代的本地化方案或直接通过 OneSky 网站/API 手动管理 `.po` 文件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/OneSkyLocalizationService)
- [OneSky 官网](https://www.oneskyapp.com/)
- [OneSky API 文档](https://github.com/onesky/api-documentation-platform)
