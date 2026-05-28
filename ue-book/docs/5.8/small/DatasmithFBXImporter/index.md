# Datasmith FBX Importer

> Adds support for importing content from DeltaGen and VRED into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | Datasmith FBX 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithDeltaGenTranslator` (Editor), `DatasmithFBXTranslator` (Editor), `DatasmithVREDTranslator` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithFBXImporter) | |

## 用途

该插件是 Datasmith 生态系统的 FBX 翻译层，专门为汽车行业两大主流可视化工具 **DeltaGen**（3DEXCITE）和 **VRED**（Autodesk）提供导入支持。它通过解析这两款工具导出的 FBX 文件中的特有数据结构（如材质分层、场景层级、动画等），将其转换为 Unreal Engine 可理解的 Datasmith 资产。

为什么存在：DeltaGen 和 VRED 使用的 FBX 文件包含大量厂商特定的元数据和场景组织方式，标准 FBX 导入器无法正确处理。此插件填补了这一空白，是汽车数字化样机流程中不可或缺的一环。

## 模块列表

| 模块 | 说明 |
|---|---|
| `DatasmithFBXTranslator` | FBX 翻译器基础模块，处理通用 FBX → Datasmith 转换逻辑 |
| `DatasmithDeltaGenTranslator` | DeltaGen 特定翻译器，处理 DeltaGen 导出的 FBX 场景数据 |
| `DatasmithVREDTranslator` | VRED 特定翻译器，处理 VRED 导出的 FBX 场景数据（含 Python 导出器支持） |

## 使用场景

- 你在做**汽车数字化样机**，需要将 DeltaGen 中渲染的整车模型导入 UE → 启用此插件
- 你在使用 **Autodesk VRED** 进行汽车内饰/外饰可视化，需要导入到 UE 中做实时渲染 → 启用此插件
- 你需要将汽车供应商提供的 DeltaGen/VRED FBX 文件集成到 UE 虚拟展厅项目中 → 启用此插件

**注意**：此插件默认未启用（`EnabledByDefault: false`），需在 Edit → Plugins 中手动启用。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DatasmithImporter` | Datasmith 核心导入框架 |
| `DatasmithContent` | Datasmith 资产类型定义 |

无其他特殊依赖。

## 子模块文档

| 模块 | 文档 |
|---|---|
| DatasmithDeltaGenTranslator | [DatasmithDeltaGenTranslator.md](DatasmithDeltaGenTranslator.md) |
| DatasmithFBXTranslator | [DatasmithFBXTranslator.md](DatasmithFBXTranslator.md) |
| DatasmithVREDTranslator | [DatasmithVREDTranslator.md](DatasmithVREDTranslator.md) |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 转 float 的截断警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移至 UE_LOGF 宏 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复不可达代码编译错误 |
| 2025-03-13 | `b059f7b4` | Fix trivial unreachable code warnings. | 修复不可达代码警告 |
| 2024-10-02 | `0a14cf0e` | Update VRED python exporter to support API changes in VRED | 更新 VRED Python 导出器以适配 VRED API 变更 |

### 维护评价

该插件处于**被动维护**状态。近 2 年的更新全部为编译警告修复和平台适配，没有功能性增强。作为 Enterprise 级别的插件，它仍能正常工作且随引擎版本同步编译，但功能上已趋于稳定。

适合在需要导入 DeltaGen/VRED 资产的项目中使用。如果你的数据来源不是这两个工具，请使用通用的 DatasmithImporter 或标准 FBX 导入器。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithFBXImporter)
- [DatasmithImporter 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter)（前置依赖）