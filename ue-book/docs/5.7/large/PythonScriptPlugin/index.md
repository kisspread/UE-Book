```markdown
# Python Editor Script Plugin

> Python integration for the Unreal Editor.

| 属性 | 值 |
|---|---|
| 中文名 | Python 编辑器脚本插件 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资源） |
| 模块 | `PythonScriptPluginPreload` (Runtime), `PythonScriptPlugin` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PythonScriptPlugin) | |

## 总体用途

PythonScriptPlugin 为 Unreal Editor 提供了完整的 Python 语言集成。它通过嵌入 CPython 运行时，使开发者能够使用 Python 脚本实现编辑器自动化、资产处理、蓝图脚本化、自定义工具开发以及与外部系统（如 Maya、Houdini）的数据交换。该插件是实验性的，需要手动启用。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `PythonScriptPluginPreload` | Runtime | 在引擎启动早期（`EarliestPossible`）初始化 Python 环境，确保后续功能可用 |
| `PythonScriptPlugin` | UncookedOnly | 提供核心 Python 绑定、编辑器命令、资产操作、日志和调试接口 |

详细 API 请参考：  
- [PythonScriptPlugin 模块文档](PythonScriptPlugin.md)  
- [PythonScriptPluginPreload 模块文档](PythonScriptPluginPreload.md)

## 使用场景

- **编辑器自动化**：批量修改资产属性、执行重命名、清理场景  
- **资产管道**：通过 Python 导入/导出 FBX、处理材质、创建数据表  
- **测试与质量控制**：编写编辑器测试用例，自动验证资产合规性  
- **自定义工具**：开发面板、菜单、窗口、自定义命令  
- **外部集成**：与 DCC 工具（如 Maya、Blender）通信，实现跨软件工作流

## 模块依赖

需要以下非标准模块（省略 Core/Engine 等常见依赖）：

| 模块 | 用途 |
|---|---|
| `Python3` | 绑定 Python 3 解释器 |
| `ContentBrowserFileDataSource` | 支持在内容浏览器中直接操作 Python 文件 |

## 维护状态

### 近期更新

- 2025-11-18 `f928db93` 修复 Python 初始化失败时关闭阶段的崩溃
- 2025-10-08 `5a0811f8` 允许 Python 无法正常加载时引擎继续运行
- 2025-09-26 `cb970b02` 移除 PyUnicode 转 FString 时的多余 Python 对象
- 2025-09-12 `ce6ff392` 处理 `nodiscard` 属性警告
- 2025-08-27 `b1317838` 暴露 `FTSTicker` 给 Python

### 维护评价

插件于 2025 年 8 月创建，至今仍在活跃维护（最近提交为 2025 年 11 月），修复了多个初始化与关闭阶段的稳定性问题。作为实验性插件，其接口可能在未来版本中变化，但当前功能已较为完整。推荐在需要编辑器脚本化的项目中使用，但建议在升级引擎时关注更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PythonScriptPlugin)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/Editor/ScriptingAndAutomation/Python/index.html)
- [PythonScriptPlugin 模块文档](PythonScriptPlugin.md)
- [PythonScriptPluginPreload 模块文档](PythonScriptPluginPreload.md)
```