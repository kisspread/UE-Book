# TEDS: Editor Data Storage

> A central extendable data storage for editors and their corresponding data with support for viewing and editing through a collection of widgets.

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器数据存储 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器数据与UI资源） |
| 模块 | `TedsCore` (EditorAndProgram), `TedsUI` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-19 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorage) | |

## 总体用途

TEDS 提供了一个**集中式且可扩展的编辑器数据存储系统**。它允许编辑器插件和内部模块将任意数据（例如资产元数据、场景对象状态、工具设置）以统一的方式存储、查询和关联，并通过一组内置的 Widget 系统（基于 `TedsUI`）进行可视化和交互。其核心目标是：

- **解耦数据与表现**：数据存储逻辑与 UI 逻辑分离，可独立演化。
- **高效查询**：基于行的存储和索引，支持复杂过滤与排序。
- **编辑器内协作**：提供协作时间分片等功能，支持多用户编辑数据。
- **生命周期管理**：自动处理数据的注册、变更通知和取消注册。

## 模块列表

| 模块名 | 类型 | 一句话总结 |
|---|---|---|
| [`TedsCore`](TedsCore.md) | Runtime (EditorAndProgram) | 核心数据存储引擎，负责行管理、列定义、查询、变更命令（Command）处理和数据兼容层。 |
| [`TedsUI`](TedsUI.md) | Editor | 基于 Slate 的 Widget 系统，提供数据视图（如表格、树状视图）和交互控件，直接与 TedsCore 数据绑定。 |

## 使用场景

1. **资产浏览器增强**：在资产浏览器中增加自定义列（如标签、评级），通过 TEDS 统一存储和查询。
2. **关卡编辑工具**：管理场景中 Actor 的自定义数据（如导航网格标记、碰撞预设），并允许用户通过专用 Widget 编辑。
3. **编辑器设置面板**：将编辑器偏好设置或项目设置存储为表格行，支持 UI 直接修改和同步。
4. **协作编辑**：利用 TEDS 提供的时间分片和命令缓冲机制，实现多人同时编辑同一数据集合。
5. **自定义面板**：基于 `TedsUI` 的 Widget 模板，快速构建展示动画曲线、材质属性或物理参数的数据表格。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ApplicationCore` | 编辑器程序基础支持 |
| `JsonUtilities` | 数据序列化（推测，未在源码中明确） |
| `DataRegistry` | 数据注册表（推测用于兼容） |
| `Slate` / `SlateCore` | UI 框架（TedsUI 必须） |
| `EditorSubsystem` | 编辑器子系统集成 |

> **注意**：实际依赖请查看各模块的 `Build.cs`。上述列表基于典型 Editor 插件所需。

## 维护状态

### 近期更新

```
- 2025-08-21 5883629 修复 FRegistrationCommandChange 和 FDeregistrationCommandChange 中空指针保护
- 2025-08-21 80aef2fc 释放 UEditorDataStorageCompatibility 对 Environment 的引用
- 2025-08-20 881afb9e 添加 FEnvironment 析构函数以清除 Legacy::FCommandBuffer 中的待处理命令
- 2025-08-19 d054c8d3 [TEDS] 添加基础协作时间分片支持
- 2025-08-19 5273c342 TEDS 层级：处理 SetParent() 引起的层级行变化
```

### 维护评价

TEDS 是 **实验性** 插件，创建于 2025 年 8 月，至今约 1 年。近期更新集中在 bug 修复和功能增强（协作分片、层级管理），表明项目仍 **活跃维护中**。但由于仍处于实验阶段，API 可能频繁变更，不推荐在正式项目中使用。适合作为学习或原型探索。

## 相关链接

- [源码目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorage)
- [TedsCore 模块文档](TedsCore.md)
- [TedsUI 模块文档](TedsUI.md)
- [官方文档](https://docs.unrealengine.com/)（暂无 TEDS 专门页面）