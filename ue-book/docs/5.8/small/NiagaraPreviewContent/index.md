# Niagara Preview Content

> Contains movie files used in Niagara

| 属性 | 值 |
|---|---|
| 中文名 | 尼亚加拉预览素材 |
| 分类 | FX |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（电影资产） |
| 模块 | `NiagaraPreviewContent` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-05-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/NiagaraPreviewContent) | |

## 用途

这个插件是一个**纯内容插件**，其核心功能是作为尼亚加拉（Niagara）特效系统相关电影（Movie）预览资产的**专用存储容器**。它的存在解决了 Niagara 特效的脚本（Scripts）、发射器（Emitters）和系统（Systems）在编辑器内预览时，需要通过一个统一的路径来引用演示视频文件的问题。通过软对象路径（Soft Object Path）链接到存储在本插件中的电影文件，Niagara 编辑器可以为用户提供一个快速、直观的视频预览（例如工具提示中的视频），而无需将这些大型媒体文件打包到主内容项目或 Niagara 核心插件中，有助于保持内容结构的清晰。

## 使用场景

- **你在使用 Niagara 制作特效**：当你在 Niagara 编辑器中创作或调试一个特效脚本、发射器或系统时，希望为其关联一个展示最终效果的视频预览。
- **你希望在资产上提供动态预览**：当你悬停在 Niagara 资产上时，希望在工具提示（Tooltip）中直接播放一段对应的演示视频，以便快速识别其效果。
- **你需要管理预览资源**：作为一个插件，它便于 Epic 官方或内容创作者集中管理和分发这些预览素材，而不污染用户的主项目内容目录。

## 蓝图用法

本插件是一个纯内容插件，其主要功能（即存储和提供预览视频文件）不暴露任何蓝图可调用的函数或属性。它在 Niagara 编辑器内部通过资产路径被引用，为 Niagara 资产的预览功能提供底层内容支持。

### 核心节点

本插件没有对外提供蓝图节点。其作用体现在 Niagara 资产的编辑器属性中，例如在脚本、发射器或系统的详细信息面板中，可能会有一个字段用于指定预览视频的软对象路径，该路径会指向本插件中存储的媒体文件。

## C++ 用法

由于这是一个纯内容插件，其模块 `FNiagaraPreviewContentModule` 仅负责基本的模块生命周期管理（启动和关闭），没有对外暴露任何额外的 C++ API。

### 头文件引入

如果你需要在自己的插件或模块中引用此模块（通常不需要），可以包含：

```cpp
// 引自：Engine/Plugins/FX/NiagaraPreviewContent/Source/NiagaraPreviewContent/Public/NiagaraPreviewContent.h
#include "NiagaraPreviewContent.h"
```

### 基本用法

本插件的模块类 `FNiagaraPreviewContentModule` 实现了标准的 `IModuleInterface` 接口，其 `StartupModule` 和 `ShutdownModule` 方法在当前源码中为空实现。这表明该模块的加载主要目的是声明插件的存在并可能管理其包含内容资产的加载，而不执行自定义的 C++ 逻辑。

## Demo 示例

本插件不包含可运行的 C++ 逻辑，因此没有独立的代码示例。其使用完全体现在编辑器的工作流中（通过 Niagara 资产关联视频）。以下代码展示了如果你希望在自己的编辑器模块中模仿这种模式，如何定义一个空的模块类：

**NiagaraPreviewContentExample.h**
```cpp
#pragma once

#include "Modules/ModuleManager.h"

class FMyPreviewContentModule : public IModuleInterface
{
public:
    /** IModuleInterface implementation */
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**NiagaraPreviewContentExample.cpp**
```cpp
#include "NiagaraPreviewContentExample.h"

void FMyPreviewContentModule::StartupModule()
{
    // 模块启动时可执行的初始化代码（如有）
}

void FMyPreviewContentModule::ShutdownModule()
{
    // 模块关闭时可执行的清理代码（如有）
}

IMPLEMENT_MODULE(FMyPreviewContentModule, MyPreviewContentModule);
```

## 模块依赖

从插件的 `Build.cs` 文件分析，该模块 `NiagaraPreviewContent` 的类型为 `Editor`。由于它是一个内容容器插件，其模块依赖通常仅限于引擎编辑器的核心模块，用于支持资产编辑器的基本功能。没有发现对其他特定功能模块（如 Niagara 模块本身）的显式代码依赖，内容层面的引用通过资产路径完成。

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-05-05 | `fd724acf` | Niagara Movie Preview Assets - Added new plugin to contain the movie files - Scripts, Emitters and Systems can link to a movie file via soft object path that can be used for preview purposes - Implemented movie tooltip for scripts | 创建了插件，用于存放尼亚加拉特技的预览电影文件，并实现了脚本的电影工具提示功能。 |

### 维护评价

- **创建时间**：该插件创建于 2025 年 5 月，非常新。
- **更新频率**：目前仅有一次初始提交（`fd724acf`），记录了插件的创建和初始功能。
- **维护状态**：插件处于**非常早期的阶段**。自创建后（截至文档生成时），没有后续的更新记录。由于其功能相对单一（作为内容容器），后续的维护可能主要围绕其包含的电影资产文件的更新（如添加新特效的预览视频）或适配 Niagara 核心插件的新功能。
- **已知问题或限制**：无源码层面的已知问题。其“限制”在于功能单一，不提供任何编辑器扩展或运行时逻辑。
- **推荐使用**：此插件作为 Niagara 系统的标准组成部分，由 Epic Games 官方维护。用户**无需主动“使用”它**，它的存在和启用是为了支持 Niagara 编辑器内置的预览功能。确保其处于启用状态即可。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/NiagaraPreviewContent)