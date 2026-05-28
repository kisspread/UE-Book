# Naming Tokens

> Define tokens which can be recognized during string evaluation.

| 属性 | 值 |
|---|---|
| 中文名 | 命名标记 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（标记定义资产） |
| 模块 | `NamingTokens` (Runtime), `NamingTokensEditor` (Runtime), `NamingTokensUI` (Runtime), `NamingTokensUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/NamingTokens) | |

## 用途

NamingTokens 是一个字符串模板标记系统，允许用户定义自定义标记（token），并在字符串求值时自动识别和替换这些标记。典型应用场景是文件路径中的动态命名——例如将 `{ProjectName}`、`{Date}`、`{Sequence}` 等标记嵌入文件路径模板中，运行时自动替换为实际值。

该插件解决的核心问题是：在虚拟制作、资产管理等工作流中，需要基于上下文自动生成一致的文件名和路径，避免手动命名导致的格式不统一问题。插件提供了标记定义、求值引擎、自动补全 UI 和编辑器集成等完整功能链。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `NamingTokens` | Runtime | 核心运行时模块，提供标记定义、注册和字符串求值引擎 |
| `NamingTokensEditor` | Runtime | 编辑器集成模块，提供资产工厂和资产定义，使标记资产在内容浏览器中可见 |
| `NamingTokensUI` | Runtime | UI 模块，提供自动补全菜单、标记提示等用户界面功能 |
| `NamingTokensUncookedOnly` | Runtime | 仅未打包时加载的模块，处理烘焙前的标记解析等逻辑 |

## 使用场景

- **虚拟制作文件命名**：在 VP 工作流中，使用标记模板自动生成镜头、序列、日期等文件路径
- **资产命名规范**：团队需要统一的资产命名规则时，通过标记模板强制执行格式
- **批量导出**：导出资源时根据上下文（项目名、平台、版本等）动态生成输出路径
- **编辑器工具开发**：需要基于运行时上下文动态生成字符串的编辑器工具

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/NamingTokens)
- [NamingTokens 核心模块](./NamingTokens.md)
- [NamingTokensEditor 编辑器模块](./NamingTokensEditor.md)
- [NamingTokensUI 界面模块](./NamingTokensUI.md)
- [NamingTokensUncookedOnly 模块](./NamingTokensUncookedOnly.md)