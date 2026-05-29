# UV Editor

> Asset editor for modifying the UV mapping of a mesh（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | UV编辑器 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器资产） |
| 模块 | `UVEditor` (Editor), `UVEditorTools` (Editor), `UVEditorToolsEditorOnly` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-06-15 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/UVEditor) | |

## 用途

这是一个专门用于编辑3D网格（Mesh）UV纹理坐标的资产编辑器插件。它解决的问题是：在引擎内部直接提供一套专业的UV编辑工具，让美术和开发者无需离开UE环境，即可对网格体的UV布局进行查看、分析、拆分、编辑和修复。这对于优化纹理映射、减少纹理拉伸、为光照贴图准备UV岛等任务至关重要。

## 使用场景

- 你正在为一个角色模型调整UV，希望减少面部的纹理拉伸 → 使用 UVEditor 的移动、缩放、旋转工具直接调整UV岛。
- 你需要为一个静态网格体创建第二套UV（Lightmap UV）用于光照烘焙 → 使用 UVEditor 的自动拆分或手动拆分工具来生成合适的UV布局。
- 你在处理导入的模型，其UV杂乱无章或有重叠 → 使用 UVEditor 的排布和布局工具进行快速整理。
- 你需要检查模型的UV密度和接缝位置 → 使用 UVEditor 的可视化分析功能（如显示UV岛边界、纹理密度热力图）。

## 模块列表

该插件的功能由以下三个模块协同实现：

-   **UVEditor**：核心编辑器应用模块，负责整个UV编辑器窗口、视口、与资产的交互以及主编辑循环。
-   **UVEditorTools**：具体的UV操作工具模块，实现了各种UV编辑工具（如选择、变换、拆分、焊接等）的核心逻辑。
-   **UVEditorToolsEditorOnly**：仅编辑器工具模块，包含那些只在编辑器环境下（而非运行时）使用的特定工具或辅助功能。

## 蓝图用法

UVEditor 作为一个资产编辑器，其核心交互通过编辑器界面（菜单、工具栏、视口操作）完成，而非暴露大量的蓝图节点。主要的蓝图或脚本交互点在于：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UVEditor` (Editor Context) | 通过右键资产或菜单进入UV编辑器 | `UVEditorModule` |

### 使用示例（蓝图描述）

1.  在内容浏览器中，右键点击一个 Static Mesh 或 Skeletal Mesh 资产。
2.  在上下文菜单中找到并点击 “UV Editor” 选项。
3.  编辑器窗口打开，即可使用左侧工具栏和顶部的菜单进行UV操作。

## C++ 用法

对于插件开发者，UVEditor 提供了扩展和集成的接口。

### 头文件引入

```cpp
#include “UVEditor.h”
// 可能需要引入具体工具模块的头文件，例如：
#include “UVEditorToolsModule.h”
```

### 基本用法

```cpp
// （概念性示例，展示如何以编程方式检查UV编辑器模块状态）
#include “Modules/ModuleManager.h”

if (FModuleManager::Get().IsModuleLoaded(“UVEditor”))
{
    UE_LOG(LogTemp, Log, TEXT(“UVEditor模块已加载。”));
    // 获取模块实例（如果有公开接口）
    // IUVEditorModule* UVEditorModule = FModuleManager::GetModulePtr<IUVEditorModule>(“UVEditor”);
}
```

### 进阶用法

通常涉及为UVEditor开发新的自定义工具。这需要继承并实现`UInteractiveTool`或相关基类，并通过工具注册机制将你的工具添加到编辑器中。具体的工具开发范式可参考`UVEditorTools`模块中的现有工具实现。

## 模块依赖

该插件依赖于其他多个编辑器插件和模块，以提供底层的几何处理和建模工具能力。

| 模块 | 用途 |
|---|---|
| `GeometryProcessing` | 提供底层的几何数据处理、网格分析和算法支持。 |
| `MeshModelingToolset` | 提供基础的网格建模和编辑工具集框架。 |
| `MeshModelingToolsetExp` | 提供实验性的网格建模工具集扩展。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数产生的编译警告。 |
| 2026-04-24 | `0213bc37` | [ITF] Call `UInputRouter::ForceTerminateSource()` from within `UInputRouter::DeregisterSource()` pri | [输入系统] 改进输入路由的源注销逻辑，强制终止相关操作。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG日志宏迁移至新的UE_LOGF格式。 |
| 2026-03-10 | `0b781d0c` | Add/RemoveOverlayWidget: | 增加了添加/移除覆盖层控件的功能。 |
| 2026-03-05 | `1adb9f68` | New material translator work: | 开展新的材质转换器相关工作。 |

### 维护评价

该插件**仍在积极维护中**。它从实验目录迁移到编辑器插件目录（创建信息）显示其已正式化。近期（2026年）仍有针对代码质量、输入系统和新功能的提交，表明Epic Games仍在投入开发。由于其`IsBetaVersion=true`，它可能尚未达到完全稳定，但功能已足够丰富且默认启用，是UE内进行UV编辑的推荐方案。对于需要内置UV编辑流程的项目，值得使用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/UVEditor)
-   官方文档链接待补充（.uplugin中DocsURL为空）