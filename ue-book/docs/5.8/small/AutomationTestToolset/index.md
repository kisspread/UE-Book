# AutomationTestToolset

> Automation test discovery and execution tools.

| 属性 | 值 |
|---|---|
| 分类 | Testing |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AutomationTestToolset` (Editor), `AutomationTestToolsetTests` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Toolsets/AutomationTestToolset) | |

## 用途

该插件提供了一套在编辑器内发现、组织和执行自动化测试的工具集。它旨在解决在大型项目中管理大量自动化测试用例的复杂性问题，为开发者提供一个集中的界面来浏览测试树、筛选测试并触发执行，从而提升测试工作流的效率。

## 使用场景

- 当你的项目拥有大量自动化测试（单元测试、集成测试、功能测试），需要在编辑器中进行可视化管理和快速执行时。
- 当你需要根据特定条件（如测试名称、标签、路径）快速筛选出目标测试用例并运行时。
- 当你希望将测试执行功能集成到自定义的编辑器工具或面板中时。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `AutomationTestToolset` | Editor | 核心模块，提供测试发现、管理和执行的编辑器工具与界面。 |
| `AutomationTestToolsetTests` | Editor | 测试模块，包含针对 `AutomationTestToolset` 插件自身功能的自动化测试用例。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Toolsets/AutomationTestToolset)
- [模块文档：AutomationTestToolset](AutomationTestToolset.md)
- [模块文档：AutomationTestToolsetTests](AutomationTestToolsetTests.md)