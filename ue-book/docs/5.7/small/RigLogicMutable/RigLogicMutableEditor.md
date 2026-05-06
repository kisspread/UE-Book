# RigLogic Extensions For Mutable

> Adds Mutable functionality to work with RigLogic DNA

| 属性 | 值 |
|---|---|
| 中文名 | DNA可变集成 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RigLogicMutable` (Runtime), `RigLogicMutableEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RigLogicMutable) | |

## 用途

RigLogicMutable 插件为 **Mutable**（Customizable Object）系统提供了对 **RigLogic DNA** 数据的支持。在 Mutable 的可定制对象图形编辑器中，通过添加 `UCustomizableObjectNodeDNAConstant` 节点，允许将骨骼网格（Skeletal Mesh）中已绑定的 RigLogic DNA 数据导入到可定制对象的节点图中，从而使最终生成的变形模型能够保留面部动画等 DNA 驱动的能力。

该插件解决的核心问题：当使用 Mutable 系统动态生成角色外观时，需要正确传递并嵌入 RigLogic DNA 数据，否则定制后的模型将丢失原始的面部变形动画。该节点作为桥梁，从源骨骼网格复制 DNA 数据，并映射到可定制对象中指定的网格组件。

## 使用场景

- 你正在开发一款具有面部动画定制的角色创建游戏，使用 Mutable 实现服装/体型定制，同时使用 RigLogic 实现面部表情动画 → 需要此节点将 DNA 嵌入最终模型。
- 你希望将已有的、包含高精度面部绑定（RigLogic DNA）的骨骼网格应用到可定制对象系统中，无需手动重建面部变形。
- 你在 Mutable 图形中需要控制多个身体部位的 DNA 来源（例如头部和面部表情基因），通过设置不同的 `ComponentName` 来指定目标网格组件。

## 蓝图用法

该插件主要扩展了 Mutable 的节点图，图中使用 `CustomizableObjectNodeDNAConstant` 节点。该节点在蓝图（运行时可定制对象）中不可直接调用，而是在 Mutable 编辑器（Customizable Object Editor）中通过拖拽或右键菜单添加。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CustomizableObjectNodeDNAConstant` | 从给定的 Skeletal Mesh 中提取 DNA，并指定关联的 Component 名称，供 Mutable 系统使用 | `UCustomizableObjectNodeDNAConstant` |

**在 Mutable Editor 中的使用**：

1. 打开一个 Customizable Object 图表。
2. 在右键菜单中选择 `Extension Data Constant` → `DNA Constant`（根据 `ShouldAddToContextMenu` 的实现，该节点会被添加到“Extension Data”类别下）。
3. 连接该节点的输出引脚到需要 DNA 数据的节点（通常是最终的 Mesh 生成节点）。
4. 在细节面板中设置 `Skeletal Mesh`（包含 DNA 的资源）和 `Component Name`（该骨骼网格在 Customizable Object 中的组件名称，默认与源网格的组件名称一致）。

> **注意**：该节点是实验性功能，图表中会以黄色警告标识（`IsExperimental()` 返回 true）。

## C++ 用法

该模块主要供 C++ 开发者在使用 Mutable 扩展系统时集成 DNA 支持。以下为基于 API 的基本使用方法。

### 头文件引入

```cpp
#include "CustomizableObjectNodeDNAConstant.h"
```

### 基本用法

通过代码创建一个 DNA 常量节点并配置属性（通常在编辑器工具类中或自定义 Mutable 扩展编译器中）：

```cpp
// 创建节点实例（通常在 Mutable 图编译过程中）
UCustomizableObjectNodeDNAConstant* DNANode = NewObject<UCustomizableObjectNodeDNAConstant>(Item);
DNANode->SkeletalMesh = SourceSkeletalMesh;   // 设置包含 DNA 的骨骼网格
DNANode->ComponentName = TEXT("HeadMesh");    // 指定目标组件名称

// 该节点继承自 UCustomizableObjectNodeExtensionDataConstant，
// 其 GenerateMutableNode 方法会在编译时自动处理 DNA 数据的复制。
```

### 进阶用法

如果你想在自定义 Mutable 扩展节点中引用 DNA 数据，可以通过 `ICustomizableObjectExtensionNode` 接口实现自己的生成逻辑。例如，创建另一个常量节点并内部使用 `UCustomizableObjectNodeDNAConstant` 的输出数据。

## Demo 示例

以下是一个最小 C++ 示例，演示如何在编辑器模块中创建并使用该节点（假设你的自定义编辑器模块依赖于 RigLogicMutableEditor）。

### MyCustomCode.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "CustomizableObjectNodeDNAConstant.h"

class FMyCustomExtension
{
public:
    static void CreateDNANodeInGraph(class UEdGraph* Graph, class USkeletalMesh* DNAMesh, FName ComponentName);
};
```

### MyCustomCode.cpp

```cpp
#include "MyCustomCode.h"
#include "CustomizableObjectNodeDNAConstant.h"
#include "EdGraph/EdGraph.h"
#include "MuCOE/Graph/Nodes/CustomizableObjectNode.h"

void FMyCustomExtension::CreateDNANodeInGraph(UEdGraph* Graph, USkeletalMesh* DNAMesh, FName ComponentName)
{
    // 创建一个自定义对象节点（模板节点）
    UCustomizableObjectNode* NewNode = NewObject<UCustomizableObjectNodeDNAConstant>(Graph);
    if (UCustomizableObjectNodeDNAConstant* DNANode = Cast<UCustomizableObjectNodeDNAConstant>(NewNode))
    {
        DNANode->SkeletalMesh = DNAMesh;
        DNANode->ComponentName = ComponentName;
        // 在图中添加节点（简化，实际需调用图布局函数）
        Graph->AddNode(DNANode, false, false);
    }
}
```

## 模块依赖

在您自己的模块的 `Build.cs` 中，除标准 `Core`、`Engine` 等外，还需添加以下依赖：

| 模块 | 用途 |
|---|---|
| `RigLogicMutable` | 运行时模块，提供 DNA 数据在 Mutable 编译时的处理逻辑 |
| `RigLogicMutableEditor` | 编辑器模块，提供节点在 Mutable 图编辑器中的注册和 UI |
| `RigLogic` | RigLogic 运行时支持（DNA 加载、求解等） |
| `Mutable` | Mutable 运行时核心 |
| `MutableEditor` | Mutable 编辑器支持（仅在编辑器模块中需要） |
| `CustomizableObject` | Mutable 的可定制对象运行时 |
| `CustomizableObjectEditor` | Mutable 图编辑器基础 |

**注意**：`RigLogicMutableEditor` 是 UncookedOnly 模块，仅在编辑器中使用。运行时只需要 `RigLogicMutable`，且无需额外依赖 Mutable 编辑器模块。

## 维护状态

### 近期更新

- 2025-09-01 `75e4adbd` [Mutable] Change namespace name（调整命名空间，可能影响编译）
- 2025-06-20 `1ec52cfd` [Mutable] Allow load and recompile of the CustomizableObject model when in-game mode（支持在游戏模式下加载和重新编译可定制对象模型）
- 2025-02-06 `41fd6b90` [mutable] Fix compilation for plugin after removal of AddParticipatingObjects method（修复因去除 AddParticipatingObjects 方法导致的编译问题）
- 2025-01-29 `ea8756da` [Mutable] Convert ModelResources to UObject（将 ModelResources 转换为 UObject）
- 2024-12-09 `17fd035f` [RigLogicMutable] Fixed Game crash when generating a SKM with DNA（修复生成带 DNA 的骨骼网格时的游戏崩溃）

### 维护评价

- **创建时间**：2024-12-09，约为1年前。
- **近期更新**：2025年9月仍有提交，显示活跃维护。
- **活跃状态**：目前处于活跃维护中，主要跟随 Mutable 框架的演进进行适配修改。
- **已知问题**：插件版本为0.1，实验性标记，不保证长期 API 稳定。
- **推荐度**：✅ 推荐在需要结合 Mutable 和 RigLogic 的项目中使用，但需留意实验性警告，可能在引擎升级时需额外适配。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RigLogicMutable)
- [Mutable 官方文档](https://docs.unrealengine.com/5.7/en-US/mutable/)
- [RigLogic 官方文档](https://docs.unrealengine.com/5.7/en-US/rig-logic/)