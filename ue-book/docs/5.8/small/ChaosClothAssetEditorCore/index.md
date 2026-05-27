# Chaos Cloth Asset Editor Core

> Core required functionalities for editing and creating Dataflow based Cloth Assets.

| 属性 | 值 |
|---|---|
| 中文名 | 布料资产编辑核心 |
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器资产） |
| 模块 | `ChaosClothAssetEditor` (Runtime), `ChaosClothAssetEditorTools` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-01-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore) | |

## 用途

该插件是 Chaos Cloth Asset 编辑工具链的核心模块，提供基于 Dataflow 的布料资产编辑所需的基础框架和功能。它是在将原有的 `ChaosClothEditor` 插件进行重构拆分后诞生的，目的是将通用的编辑器功能与特定格式（如 USD）的导入导出功能解耦，使得核心编辑能力可以被其他模块复用，同时避免功能冗余。

## 使用场景

-   **资产创建与修改**：当你需要使用基于节点的 Dataflow 图来驱动和创建布料物理模拟资产时。
-   **编辑器内布料工作流**：希望在 UE 编辑器内部完成布料资产的设计、预览和迭代，而不是完全依赖外部 DCC 工具。
-   **插件开发基础**：开发需要处理 Chaos 布料资产的自定义编辑器工具或扩展，以此插件作为基础。

## 蓝图用法

本插件主要为编辑器工具和底层 C++ 框架提供支持，其核心功能更多体现在数据资产（如 `UChaosClothAsset`）和编辑器工具类上，而非直接暴露大量游戏逻辑蓝图节点。通常，与这些资产的交互会通过编辑器工具（如资产编辑器）或项目特定的蓝图逻辑进行。

## C++ 用法

本插件的核心在于提供 `UChaosClothAsset` 和相关的编辑器上下文框架。

### 头文件引入

```cpp
#include “ChaosClothAsset/ClothAsset.h”
// 根据需要，引入工具模块
#include “ChaosClothAssetEditorTools/ToolTargets/ChaosClothEditorToolTarget.h”
```

### 基本用法

获取和操作布料资产的基本示例。

```cpp
// 引擎模块上下文中，假设已获得一个 UChaosClothAsset 对象指针
UChaosClothAsset* ClothAsset = LoadObject<UChaosClothAsset>(nullptr, TEXT(“/Game/Characters/Cloth/T_Cape”));
if (ClothAsset)
{
    // 资产内部的数据通常由 Dataflow 图生成和管理
    // 此处可以读取或设置资产的元数据等属性
}
```
*来源：根据 `ChaosClothAsset` 模块的通用用法推断。*

### 进阶用法

使用编辑器工具模块与资产进行交互，例如设置编辑器上下文。

```cpp
// 在编辑器工具中，需要为目标资产设置正确的编辑器上下文
TObjectPtr<UEditableMesh> EditableMesh = CreateEditableMeshFromClothAsset(ClothAsset);
// 此 EditableMesh 可用于驱动与网格相关的编辑工具，如变形、绘制权重等
```
*来源：根据 `ChaosClothAssetEditorTools` 模块的功能推断。*

## Demo 示例

一个最小的示例，展示如何在编辑器工具中加载并关联一个布料资产。

```cpp
// MyClothTool.h
#pragma once
#include “Tools/UEdMode.h”
#include “ChaosClothAsset/ClothAsset.h”

class FMyClothEditorTool : public FEdMode
{
public:
    virtual void Enter() override;

private:
    UPROPERTY()
    TObjectPtr<UChaosClothAsset> CurrentClothAsset;
};

// MyClothTool.cpp
#include “MyClothTool.h”
#include “Engine/AssetManager.h”

void FMyClothEditorTool::Enter()
{
    FEdMode::Enter();

    // 假设从资产选择器或路径获取资产
    CurrentClothAsset = LoadObject<UChaosClothAsset>(nullptr, TEXT(“/Game/MyClothAsset”));
    if (CurrentClothAsset)
    {
        // 在此处初始化与该布料资产相关的编辑器状态和 UI
        UE_LOG(LogTemp, Log, TEXT(“Loaded Cloth Asset: %s”), *CurrentClothAsset->GetName());
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ChaosClothAsset` | 布料资产的数据定义和核心类型 |
| `EditableMesh` | 提供可编辑的网格表示，用于布料网格编辑工具 |
| `Interchange` | 支持资产（如布料资产）的导入/导出流程 |
| `MeshDescription` | 描述网格数据的中间格式，与资产导入相关 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理布料资产转换器代码 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量转浮点的编译警告 |
| 2026-05-12 | `a7e94182` | Interchange Cloth Asset: Add support for reimporting; | 为布料资产添加重新导入支持 |
| 2026-05-12 | `f1d5a018` | Dataflow : add HUD selection information to both Cloth and dataflow selection tool viewports | 为布料和数据流选择工具视口添加 HUD 选择信息 |
| 2026-04-27 | `b6b093cd` | CIS - Fixed Issue 1323734: Compile warnings in Module.ChaosClothAssetEditor.cpp, ChaosClothAssetEdit | 修复模块中的编译警告 |

### 维护评价

该插件于 2026 年 1 月创建，是一个较新的组件。从近期的 Git 记录看，在 2026 年 5 月内仍有频繁的提交，内容涉及功能增强（如重新导入支持）、Bug 修复（编译警告）和代码优化（清理），表明它处于**活跃维护**状态。作为 Chaos 布料工作流的核心编辑部分，它是 Epic Games 官方工具链的一部分，稳定性与后续支持有保障，**推荐在需要相关功能时使用**。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore)