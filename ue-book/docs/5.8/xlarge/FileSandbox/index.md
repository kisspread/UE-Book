# File Sandbox

> Core functionality for sandboxing files in the editor.

| 属性 | 值 |
|---|---|
| 分类 | Developer |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `FileSandboxCore` (UncookedOnly), `FileSandboxUI` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-16 |
| 年龄标签 | 🆕（约 -2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Sandbox/FileSandbox) | |

## 用途

File Sandbox 插件为 Unreal Editor 提供了一个文件操作沙盒环境。其核心目的是在编辑器开发或测试过程中，安全地隔离文件操作（如读取、写入、监控），防止对项目原始文件造成意外修改或污染。它通过创建一个受控的虚拟文件系统或目录映射，让开发者可以在不影响实际项目资产的情况下进行文件相关的功能测试和调试。

## 使用场景

- **资产导入/导出测试**：你需要测试一个自定义的资产导入器或导出器，但不想每次测试都修改或覆盖项目中的真实资产文件。
- **编辑器工具开发**：你正在开发一个需要频繁读写临时文件或配置文件的编辑器工具，希望这些操作被限制在一个安全的沙盒内。
- **文件监控功能验证**：你需要验证一个基于 `DirectoryWatcher` 的文件变更监听功能，但希望在受控的、可预测的目录结构下进行，避免干扰项目目录。
- **插件开发与调试**：作为插件开发者，你需要一个干净的环境来测试你的插件对文件系统的依赖和影响。

## 蓝图用法

本插件的核心功能主要通过 C++ 模块提供。`FileSandboxUI` 模块可能提供编辑器界面（如面板、菜单项）来管理沙盒环境。具体的蓝图可调用函数和属性，请参阅各子模块的详细文档。

- **详细 API 文档**：请参考 [FileSandboxCore 模块文档](FileSandboxCore.md) 和 [FileSandboxUI 模块文档](FileSandboxUI.md)。

## C++ 用法

本插件的功能通过两个独立的 C++ 模块提供。`FileSandboxCore` 提供底层沙盒逻辑，`FileSandboxUI` 提供编辑器集成。

- **详细用法与示例**：请参考各子模块的详细文档，其中包含从源码和测试用例中提取的用法说明。
    - [FileSandboxCore 模块文档](FileSandboxCore.md)
    - [FileSandboxUI 模块文档](FileSandboxUI.md)

## Demo 示例

完整的、可编译的最小示例代码包含在各子模块的文档中。请查阅上述模块文档以获取 `.h` 和 `.cpp` 文件示例。

## 模块依赖

使用本插件无需在你的项目模块中添加特殊依赖。插件自身的模块依赖如下：

| 模块 | 用途 |
|---|---|
| `DirectoryWatcher` | `FileSandboxCore` 模块依赖此模块，用于监控沙盒目录内的文件系统变更。 |

## 维护状态

### 近期更新

（基于提供的创建时间 2026-04-16，此插件为新建插件，尚无历史提交记录。）

### 维护评价

- **创建时间**：插件创建于 2026 年，非常新。
- **版本状态**：`.uplugin` 标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`，表明这是一个**实验性**插件，功能可能不完整且不稳定。
- **维护状态**：作为新创建的实验性插件，其长期维护计划和稳定性尚不明确。
- **推荐使用**：**不推荐**在生产项目中使用。仅建议用于开发、测试或学习 Unreal Editor 文件系统沙盒相关功能的场景。使用前请充分评估其风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Sandbox/FileSandbox)
- [FileSandboxCore 模块文档](FileSandboxCore.md)
- [FileSandboxUI 模块文档](FileSandboxUI.md)