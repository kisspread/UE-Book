# Static Mesh Editor Modeling Mode

> Enable a Modeling Tools Tab in the Static Mesh Editor（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 静态网格体编辑器建模模式 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（建模工具标签页） |
| 模块 | `StaticMeshEditorModeling` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-02-01 |
| 年龄标签 | 👴 老古董（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/StaticMeshEditorModeling) | |

## 用途

此插件将 **Unreal Engine 的建模工具（Modeling Tools）** 集成到 **静态网格体编辑器（Static Mesh Editor）** 中。它为编辑器添加了一个特殊的编辑模式（EdMode），使得用户无需离开静态网格体编辑器环境，即可直接使用各种多边形建模、网格体操作和资产创建工具。它解决的核心问题是：将专用的建模功能无缝嵌入资产编辑器工作流，避免在多个编辑器窗口间切换，提升美术和关卡设计人员迭代资产的效率。

## 使用场景

- **美术师或关卡设计师**需要对一个静态网格体资产进行快速调整或修复（例如，移除一个面、挤出一部分、修复法线），但不想启动完整的编辑器或导出到外部DCC软件。
- 在 **静态网格体编辑器** 中检查资产时，发现需要即时进行几何体修改，希望直接在该编辑器内完成。
- 希望利用 UE 内置的、基于 Geometry Processing 的建模工具来处理导入的网格体，同时保持与资产管线的紧密集成。

## 蓝图用法

本插件是纯粹的编辑器模式扩展，其主要功能通过编辑器UI（菜单、工具栏、工具面板）触发，**不提供可供蓝图脚本调用的 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性**。其交互完全在静态网格体编辑器窗口内完成。

## C++ 用法

### 头文件引入

```cpp
#include "StaticMeshEditorModelingModule.h"
```

### 基本用法

通过 `FStaticMeshEditorModelingModule` 模块接口控制建模模式的激活状态。

```cpp
// 来自源码分析：StaticMeshEditorModelingModule.h
FStaticMeshEditorModelingModule& ModelingModule = FModuleManager::Get().LoadModuleChecked<FStaticMeshEditorModelingModule>(TEXT("StaticMeshEditorModeling"));

// 检查给定的静态网格体编辑器实例是否已进入建模模式
TWeakPtr<IStaticMeshEditor> MyMeshEditor = /* ... 从某个上下文获取 ... */;
bool bIsInModelingMode = ModelingModule.IsStaticMeshEditorModelingModeActive(MyMeshEditor);

// 切换给定编辑器实例的建模模式
if (!bIsInModelingMode)
{
    ModelingModule.OnToggleStaticMeshEditorModelingMode(MyMeshEditor);
}
```

## Demo 示例

以下是一个最小示例，展示如何在自己的编辑器工具或自定义代码中，编程控制静态网格体编辑器建模模式的开启。

```cpp
// MyCustomTool.h
#pragma once
#include "CoreMinimal.h"

class IStaticMeshEditor;
class FStaticMeshEditorModelingModule;

class FMyCustomTool
{
public:
    void EnableModelingModeForEditor(const TSharedPtr<IStaticMeshEditor>& Editor);

private:
    FStaticMeshEditorModelingModule* ModelingModulePtr = nullptr;
};

// MyCustomTool.cpp
#include "MyCustomTool.h"
#include "StaticMeshEditorModelingModule.h" // 关键头文件
#include "Toolkits/IToolkit.h"

void FMyCustomTool::EnableModelingModeForEditor(const TSharedPtr<IStaticMeshEditor>& Editor)
{
    if (!Editor.IsValid())
    {
        return;
    }

    // 1. 获取建模模块
    if (!ModelingModulePtr)
    {
        ModelingModulePtr = FModuleManager::GetModulePtr<FStaticMeshEditorModelingModule>("StaticMeshEditorModeling");
    }

    if (ModelingModulePtr)
    {
        TWeakPtr<IStaticMeshEditor> WeakEditor = Editor;
        // 2. 调用切换函数，如果当前不是建模模式，则会进入
        ModelingModulePtr->OnToggleStaticMeshEditorModelingMode(WeakEditor);
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。
*（根据 Build.cs 分析，其依赖均为编辑器插件的基础模块，如 `Core`, `CoreUObject`, `Engine`, `Slate`, `SlateCore`, `UnrealEd` 等。）*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-02-20 | `2ce45174` | [Viewport ITF] Allow editor modes to opt-in to the new gizmos. When editor modes change, the ITF Tra... | 为编辑器模式接入新的视口交互框架（ITF）和 Gizmo 系统。 |
| 2025-03-05 | `7ab43c2f` | Add and address deprecation warning after UEditorInteractiveToolsContext classes move to UnrealEd | 应对 `UEditorInteractiveToolsContext` 类迁移到 `UnrealEd` 模块带来的废弃警告。 |
| 2024-02-01 | `18df41a3` | Move StaticMeshEditorModeling into Editor plugins folder | 将插件从其他位置移至当前的 `Editor` 插件文件夹，即本插件的创建提交。 |

### 维护评价

**不活跃维护**。该插件创建于 2024 年初，至今（2026年）约两年。初始提交后，仅有两次更新：一次是适应引擎底层框架变更（编辑器工具上下文迁移），另一次是接入新的视口系统。**没有发现针对该插件功能本身的增强或错误修复**。考虑到它仍处于 **Beta 状态 (`IsBetaVersion: true`) 且默认未启用**，这表明 Epic 将其视为实验性功能，可能仍在评估中或优先级不高。目前可以用于探索和体验，但不建议作为核心生产流程依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/StaticMeshEditorModeling)
- 官方文档：无
- 测试用例：未在插件目录内发现