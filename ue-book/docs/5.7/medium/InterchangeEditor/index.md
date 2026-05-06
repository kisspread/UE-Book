# Interchange Editor

> The Interchange Editor plugin exposes the Interchange import framework and pipelines to Unreal Editor.

| 属性 | 值 |
|---|---|
| 中文名 | 交换编辑器 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeEditor` (Runtime), `InterchangeEditorPipelines` (Runtime), `InterchangeEditorUtilities` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-09-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Editor) | |

## 总体用途

Interchange Editor 插件将 **Interchange 导入框架** 的配置、管线和工具完整地暴露到 Unreal Editor 中。它提供了导入对话框的 UI、管线设置面板、节点编辑器集成以及资产导入后的自动处理功能，让用户无需编写代码即可自定义导入行为（如 FBX、GLTF 等格式）。如果没有此插件，Interchange 框架仅能通过 C++ 或 Python 脚本驱动。

## 模块列表

| 模块 | 类型 | 一句话说明 | 详细文档 |
|---|---|---|---|
| `InterchangeEditor` | Runtime | 核心编辑器集成，负责导入对话框、资产工厂、右键菜单等 UI 层交互 | [InterchangeEditor.md](./InterchangeEditor.md) |
| `InterchangeEditorPipelines` | Runtime | 提供可视化的导入管线配置（Pipeline Configuration）面板，允许用户组合自定义处理步骤 | [InterchangeEditorPipelines.md](./InterchangeEditorPipelines.md) |
| `InterchangeEditorUtilities` | Runtime | 提供蓝图/C++ 可用的辅助函数，如资产重命名、友好名称格式化、日志记录等 | [InterchangeEditorUtilities.md](./InterchangeEditorUtilities.md) |

## 使用场景

- **需要自定义 FBX/GLTF 导入流程**：通过 InterchangeEditorPipelines 的 UI 拖拽组合预处理、后处理节点，无需编写 C++ 管线。
- **在编辑器中批量导入资产**：利用 InterchangeEditor 模块的导入对话框，可选择多个文件并应用统一的导入设置。
- **开发导入工具或自动化脚本**：通过 InterchangeEditorUtilities 提供的蓝图节点快速获取文件名、分类等元数据，减少重复代码。
- **调试和日志分析**：使用 InterchangeEditor 模块内置的日志窗口（从 git log 的“Temp fix for Interchange Logging”可推断）追踪导入过程中的错误。

## 维护状态

### 近期更新

- 2025-10-02 `35b266d6` — [Interchange UI] 在导入对话框详情面板中添加分隔节标题
- 2025-09-24 `d2b213b6` — Interchange 导入性能改进尝试
- 2025-09-24 `c5a21eff` — [BUGFIX] FBX Python 关卡导入测试修复
- 2025-09-23 `dcd0cb0d` — 临场修复用户关闭导入对话框时的崩溃
- 2025-09-23 `24638fbb` — [Interchange] 临时修复日志记录

### 维护评价

该插件创建于 2025-09-23，至今不足一个月，但已连续多次提交更新，包含 UI 增强、性能优化、崩溃修复和测试修复，表明团队正在积极开发中。作为 Interchange 导入框架的编辑器层，目前无已知重大限制，推荐在 UE 5.5+ 中用于替代旧的 FBXImporter 导入方式。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Editor)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/interchange-import-framework-in-unreal-engine/)（Interchange 框架概述）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Tests)（Interchange 公共测试，部分覆盖编辑器功能）