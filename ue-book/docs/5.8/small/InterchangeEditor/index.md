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
| 创建时间 | 未知 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor) | |

## 用途

本插件是 Unreal Engine **Interchange 框架**在**编辑器端**的核心集成模块。它解决了将基于 Interchange 的资产（如 FBX、glTF、OBJ 等）工作流无缝集成到 Unreal Editor 的问题。其主要作用包括：

1.  **暴露核心导入功能**：将 `InterchangeManager` 等底层框架能力包装并提供给编辑器，作为资产导入的统一入口。
2.  **集成导入管线**：将 `InterchangeEditorPipelines` 模块中定义的资产特定管线（如静态网格、骨骼网格、纹理）注册到编辑器中，使导入过程能够遵循引擎的资产创建和转换规则。
3.  **提供编辑器工具**：通过 `InterchangeEditorUtilities` 提供一系列实用的编辑器工具和函数，方便开发者扩展或自定义导入流程。

简单来说，没有这个插件，Interchange 框架在编辑器中就无法使用。

## 使用场景

-   **从外部 DCC 工具（如 Blender, Maya）导入资产**：当你在这些软件中通过 Interchange 导出，并在 Unreal Editor 中通过标准文件浏览器导入时，幕后就是此插件在驱动流程。
-   **需要自定义或覆盖导入设置**：如果你需要为特定资产类型（如某个特定的 FBX 文件）修改默认的导入参数（如是否导入动画、合并网格等），这个插件提供了底层支持和扩展点。
-   **开发新的资产导入器**：如果你正在为一种新的 3D 文件格式编写导入器，并希望它与 Unreal Editor 的导入系统完全集成，你需要理解并可能扩展此插件的功能。

## 蓝图用法

此插件主要面向编辑器扩展和底层 C++ 集成，其蓝图节点相对较少，主要集中在 `InterchangeEditorUtilities` 模块提供的通用工具函数。核心的导入流程是通过编辑器菜单和对话框触发，而非蓝图节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetActorsFromLevelInstance` | 获取关卡实例中的 Actor，无需完整加载该关卡实例。 | `UInterchangeEditorScriptLibrary` |

### 使用示例（蓝图描述）

**获取关卡实例内的Actor：**
1.  获取一个 `UInterchangeEditorScriptLibrary` 类型的库对象（通常通过节点获取）。
2.  调用 `GetActorsFromLevelInstance` 节点。
3.  输入目标关卡实例资产。
4.  输出一个包含该实例内所有 Actor 的数组，可用于后续逻辑处理（如查找、修改），避免了强制加载整个子关卡的开销。

## C++ 用法

C++ 用法主要围绕扩展 Interchange 的导入流程和管线。

### 头文件引入

```cpp
#include "InterchangeEditorModule.h"
#include "InterchangeManager.h"
#include "InterchangeEditorPipelinesModule.h"
#include "InterchangeEditorUtilitiesModule.h"
```

### 基本用法

**1. 检查 Interchange 框架和编辑器模块是否可用**
（这是一个典型的初始化检查，确保在正确的模块中执行）
```cpp
// 来源: InterchangeEditor 模块初始化逻辑
if (FModuleManager::Get().IsModuleLoaded("InterchangeEditor"))
{
    IInterchangeEditorModule* EditorModule = FModuleManager::GetModulePtr<IInterchangeEditorModule>("InterchangeEditor");
    if (EditorModule)
    {
        // 可以通过 EditorModule 访问编辑器特定的接口
    }
}
```

### 进阶用法

**1. 获取并使用导入的资产管线**
（这是 Interchange 导入的核心概念，用于定义资产如何被处理）
```cpp
// 来源: InterchangeEditorPipelines 模块，用于获取默认管线
IInterchangeEditorPipelinesModule* PipelinesModule = FModuleManager::GetModulePtr<IInterchangeEditorPipelinesModule>("InterchangeEditorPipelines");
if (PipelinesModule)
{
    // 获取一个特定资产类型（例如静态网格）的导入管线
    UInterchangePipelineBase* MeshPipeline = PipelinesModule->GetDefaultMeshPipeline();
    // 此管线对象包含了如何将导入数据转换为 UStaticMesh 的所有规则
}
```

## 模块依赖

从各模块的 `Build.cs` 分析，本插件自身依赖于 Interchange 核心运行时模块。对于插件使用者（例如，想在自己的编辑器工具中调用 Interchange 导入），需要依赖这些模块。

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | Interchange 框架的核心抽象和接口定义。 |
| `InterchangeEngine` | Interchange 的引擎集成，负责实际的资产导入执行和资产创建。 |
| `InterchangeFactory` | 用于创建最终 Unreal 资产（如 `UStaticMesh`）的工厂类集合。 |
| `InterchangeImport` | 包含具体的文件格式翻译器（Translator），如 FBX、glTF 等。 |
| `InterchangeNodes` | 定义了中间交换节点（Interchange Node）的数据结构，是导入数据流的载体。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `fb1426e8` | [PackageAutoSaver] Add the ability to temporarily suspend the autosaver. | 关联功能：为Interchange导入流程添加了临时挂起自动保存器的能力，避免导入时触发不必要的保存。 |
| 2026-05-12 | `099f7387` | [Interchange] Animation frame alignment and glTF translator frame aligner removed. | 功能重构：移除了动画帧对齐和glTF翻译器的帧对齐器，简化了相关代码。 |
| 2026-04-22 | `cc360b1e` | Add accessor to InterchangeEditorScriptLibrary that returns actors in a level instance without loading it. | 新增API：在`InterchangeEditorScriptLibrary`中添加了无需加载关卡实例即可获取其内部Actor的接口。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 代码维护：将日志宏从`UE_LOG`迁移至`UE_LOGF`，统一日志格式。 |
| 2026-04-13 | `05458c60` | [Interchange] Reworking Static and Skeletal Mesh import settings. | 核心重构：对静态网格和骨骼网格的导入设置进行了重大重构，可能影响现有导入预设。 |

### 维护评价

-   **活跃维护**：最近一次更新在2天前（2026-05-12），且近期有多次功能性更新和重构。
-   **核心功能演进**：近期提交涉及导入设置重构、API新增和移除，表明插件仍在积极开发和完善中。
-   **推荐使用**：作为 Epic Games 官方维护的资产导入框架的编辑器前端，它是现代资产导入工作流的标准解决方案，处于活跃开发状态，推荐在需要高质量、可定制化资产导入的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Interchange)