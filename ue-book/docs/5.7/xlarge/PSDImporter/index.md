# PSD Importer

> (Description from .uplugin 为空，由代码分析补充)

| 属性 | 值 |
|---|---|
| 中文名 | PSD 导入器 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（可能包含示例资源） |
| 模块 | `PSDImporterEditor` (Editor), `PSDImporter` (Runtime), `PSDImporterCore` (Runtime), `PsdSDK` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-15 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PSDImporter) | |

> 注意：该插件标记为实验性，API 和行为可能在未来版本中发生变更。

## 总体用途

**PSD Importer** 允许用户将 Adobe Photoshop（.psd）文件直接导入 Unreal Engine，并利用 PSD 中的图层、图层组、混合模式、蒙版等信息，在编辑器中生成对应的纹理、材质、2D 分层 Actor 或 UI 组件。它专注于**保留原始设计文件的层次结构**，适合需要将分层设计的 2D 资源无缝集成到引擎中的工作流，例如：

- UI 设计师将带有多图层的界面稿导入为 UMG 或 2D 演员。
- 2D 游戏角色或场景的拆分资产（各部位分图层绘制）导入后自动绑定。
- 需要将 PSD 文件作为“源文件”并保持版本可追溯的项目。

> 该插件依赖 **GeometryMask** 插件，并使用了第三方 **PsdSDK** 进行底层文件解析。

## 模块总览

| 模块 | 类型 | 一句话描述 | 文档 |
|------|------|------------|------|
| `PSDImporterCore` | Runtime | 核心 PSD 解析和层数据结构定义 | [文档](./PSDImporterCore.md) |
| `PSDImporter` | Runtime | 运行时加载和播放导入的 PSD 数据（如动态纹理更新） | [文档](./PSDImporter.md) |
| `PSDImporterEditor` | Editor | 编辑器端的导入 UI、资产工厂、资产类型注册 | [文档](./PSDImporterEditor.md) |
| `PsdSDK` | External (ThirdParty) | 封装第三方 PSD 解析库，提供底层文件读写 | [文档](./PsdSDK.md) |

## 使用场景

- **2D 游戏开发**：将包含角色、道具、环境等分层图的 PSD 导入为 ActorBlueprint，保留各层单独控制（可见性、位置、颜色等）。
- **UI 设计流程**：设计师在 Photoshop 中完成界面分层稿后，直接用此插件导入为 UMG 控件或 2D 演员，减少重建 UI 结构的工作量。
- **程序化纹理生成**：利用 PSD 中的层合成信息，在运行时动态生成纹理（如用户自定义装饰）。
- **版本管理**：将 PSD 作为单一源文件，导入后自动生成对应的 UE 资产，避免导出 PNG 碎片导致的版本混乱。

## 常见工作流

1. **安装并启用**：确保已启用 `PSD Importer` 和 `GeometryMask` 插件。
2. **导入 PSD**：在编辑器中右键 Content Browser → Import → 选择 `.psd` 文件。
3. **配置导入选项**：选择如何解析图层（平铺/拉伸、是否生成独立纹理、是否创建分层 Actor 等）。
4. **使用导入资产**：导入后生成一个 `PSDImportData` 实例（或根据选项生成多个纹理/材质），可拖入场景或用于 UI。

## 相关链接

- [源码目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PSDImporter)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PSDImporter/Tests)（如存在）
- [依赖插件 - GeometryMask](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryMask)

## 维护状态

- **近期更新**（2025-07-15 至 2025-05-15）：
  - 2025-07-15 — 修复静默错误（V1051 误报）
  - 2025-06-05 — 添加 Windows Arm64 PSD SDK 库及编译批处理文件
  - 2025-05-15 — 修复 16/32 位 PSD 导入、隐藏对用户不友好的 `AdjustForViewDistance` 属性、转义特殊字符的图层名称
- **综合评价**：
  - 创建于 2025-05-15，属于全新插件（🆕），仅两个月的开发历史。
  - 近期保持活跃更新，包含功能修复和平台支持扩展。
  - 仍标记为实验性，部分 API 可能尚未稳定。
  - **推荐使用**：对于需要处理 Modern PSD 分层设计的工作流非常有用，但请注意后续版本可能有不兼容变更。