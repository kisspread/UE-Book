# Static Mesh Editor Modeling Mode

> Enable a Modeling Tools Tab in the Static Mesh Editor

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | false（需手动启用） |
| 包含内容 | true |
| 模块 | StaticMeshEditorModeling (Editor) |
| 创建时间 | 2021-09-16 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/StaticMeshEditorModeling) | |

## 用途

这个 plugin 解决的核心问题是：**在 Static Mesh Editor 内直接使用建模工具，而不需要切换到关卡编辑器的 Modeling Mode**。

UE5 的 Modeling Tools 主要通过关卡编辑器的 Modeling Mode 使用，但当你正在编辑一个 Static Mesh 资产时（双击打开 Static Mesh Editor），你无法直接访问这些工具。StaticMeshEditorModeling 就是为此而生——它在 Static Mesh Editor 的工具栏上添加一个 "Modeling Tools" 按钮，点击后进入一个嵌入式的建模模式，提供 LOD 生成、LOD 管理和网格检查三个核心工具。

这个 plugin 本身不实现任何建模算法，它是一个 **适配层**，将已有的建模工具（来自 MeshLODToolset、ModelingToolsEditorMode 等 plugin）桥接到 Static Mesh Editor 的上下文中。

## 使用场景

- 你在 Static Mesh Editor 中查看一个网格，想快速检查它的法线、UV、边距等几何信息 → 用 **Mesh Inspector** 工具
- 你需要为一个 Static Mesh 自动生成 LOD 层级（Nanite 之外的传统 LOD） → 用 **Generate Static Mesh LOD Asset** 工具
- 你需要在 Static Mesh Editor 内管理已有 LOD 的添加/删除/替换 → 用 **LOD Manager** 工具
- 你不想来回切换关卡编辑器和 Static Mesh Editor → 这个 plugin 就是为你准备的

## 蓝图用法

本 plugin 没有暴露任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。它完全通过编辑器 UI 操作，不提供蓝图接口。

## C++ 用法

本 plugin 主要面向编辑器 UI 集成，不提供可供外部模块调用的公共 C++ API。以下信息适用于理解其内部架构或进行二次开发。

### 头文件引入

```cpp
#include "StaticMeshEditorModelingModule.h"
#include "StaticMeshEditorModelingMode.h"
#include "StaticMeshEditorModelingToolkit.h"
```

### 内部架构

plugin 由 4 个核心类组成：

| 类 | 职责 |
|---|---|
| `FStaticMeshEditorModelingModule` | 模块入口，注册工具栏按钮和命令 |
| `UStaticMeshEditorModelingMode` | Editor Mode，管理工具的注册和生命周期 |
| `FStaticMeshEditorModelingToolkit` | Toolkit，负责 UI 面板和工具栏构建 |
| `FStaticMeshEditorModelingCommands` | 命令定义，注册 Toggle 按钮 |

#### 模块启动流程（源码分析）

`FStaticMeshEditorModelingModule::StartupModule()` 做了两件事：

1. 注册 `FStaticMeshEditorModelingCommands`（一个 Toggle 按钮命令）
2. 通过 `UToolMenus` 在 `AssetEditor.StaticMeshEditor.ToolBar` 上添加 "Modeling Tools" 按钮

当用户点击该按钮时，`OnToggleStaticMeshEditorModelingMode` 被调用，激活/停用 `UStaticMeshEditorModelingMode`。

#### 编辑器模式注册的工具（源码分析）

`UStaticMeshEditorModelingMode::Enter()` 中注册了 3 个工具：

```cpp
// 来源: StaticMeshEditorModelingMode.cpp
// 注册 Auto LOD 生成工具（以资产编辑器模式运行）
UGenerateStaticMeshLODAssetToolBuilder* Builder = NewObject<UGenerateStaticMeshLODAssetToolBuilder>();
Builder->bUseAssetEditorMode = true;
RegisterTool(ToolManagerCommands.BeginGenerateStaticMeshLODAssetTool, ...);

// 注册 LOD 管理工具
RegisterTool(ToolManagerCommands.BeginLODManagerTool, ...);

// 注册网格检查工具
RegisterTool(ToolManagerCommands.BeginMeshInspectorTool, ...);
```

## Demo 示例

本 plugin 是纯编辑器扩展，没有运行时组件。使用方式：

1. 启用 plugin：Edit → Plugins → 搜索 "Static Mesh Editor Modeling Mode" → Enable
2. 重启编辑器
3. 双击任意 Static Mesh 资产打开 Static Mesh Editor
4. 在工具栏找到新增的 **"Modeling Tools"** 按钮（建模工具图标）
5. 点击后进入建模模式，左侧出现工具面板，包含三个工具按钮：
   - **Generate Static Mesh LOD Asset** — 自动生成 LOD 层级
   - **LOD Manager** — 管理现有 LOD
   - **Mesh Inspector** — 检查网格几何信息
6. 选择工具后，视口底部出现 Accept/Cancel 按钮
7. 完成操作后可选择接受（Enter）或取消（Esc）

### 注意事项

- 使用 Generate LOD 工具时，系统会提示 "This tool may create new assets including new Static Meshes, Textures, and Materials"
- 切换出建模模式时，如果有未完成的工具操作，会弹出对话框询问是否接受/取消
- 仅支持 Win64 平台
- 当前为 Beta 版本（`IsBetaVersion: true`）

## 模块依赖

从 Build.cs 的 PrivateDependencyModuleNames 提取：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `InputCore` | 输入系统 |
| `Slate` / `SlateCore` | UI 框架 |
| `UnrealEd` | 编辑器框架 |
| `EditorFramework` | 编辑器框架扩展 |
| `ToolMenus` | 工具菜单注册系统 |
| `InteractiveToolsFramework` | 交互式工具框架（运行时） |
| `EditorInteractiveToolsFramework` | 交互式工具框架（编辑器） |
| `ModelingToolsEditorMode` | Modeling Tools 编辑器模式（提供工具命令和样式） |
| `ModelingComponentsEditorOnly` | 建模组件（编辑器专用） |
| `MeshLODToolset` | LOD 相关工具实现（AutoLOD、LOD Manager） |
| `MeshModelingToolsExp` | 建模工具集（Mesh Inspector 等） |
| `StaticMeshEditor` | Static Mesh Editor 集成接口 |

### Plugin 依赖

| Plugin | 用途 |
|---|---|
| `MeshLODToolset` | 提供 LOD 生成和管理工具 |
| `ModelingToolsEditorMode` | 提供建模工具框架、命令和 UI 样式 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-03-05 | `7ab43c2fa54` | Add and address deprecation warning after UEditorInteractiveToolsContext classes move to UnrealEd | 适配引擎重构：`UEditorInteractiveToolsContext` 类从原模块迁移到 UnrealEd，添加了弃用警告处理 |
| 2024-02-01 | `18df41a34cf` | Move StaticMeshEditorModeling into Editor plugins folder | 从 Experimental 目录迁移到 Editor 目录，标志着 plugin 脱离实验阶段 |

### 维护评价

- **创建时间**: 2021-09-16，约 4.6 年历史
- **从 Experimental 毕业**: 2024-02 迁移到 Editor 目录
- **更新频率**: 较低，最近一次功能性更新是适配引擎 API 迁移（2025-03），非新功能开发
- **Beta 状态**: .uplugin 中 `IsBetaVersion: true`，尽管已从 Experimental 毕业
- **平台限制**: 仅 Win64
- **代码规模**: 非常小（4 个 .h + 4 个 .cpp），主要是适配层代码
- **综合评价**: 这是一个轻量级的桥接 plugin，功能稳定但开发投入有限。作为建模工具在 Static Mesh Editor 中的入口，它完成得很好，但不要期待频繁的更新或新功能。**推荐使用**，尤其适合需要在资产编辑器中直接操作网格的工作流。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/StaticMeshEditorModeling)
- [ModelingToolsEditorMode plugin](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/ModelingToolsEditorMode) — 本 plugin 依赖的建模工具框架
- [MeshLODToolset plugin](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/MeshLODToolset) — LOD 工具实现
