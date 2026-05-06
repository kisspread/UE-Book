# Mutable Groom Extensions

> Adds Mutable functionality to work with Grooms from the HairStrands plugin

| 属性 | 值 |
|---|---|
| 中文名 | 可变发型扩展 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `HairStrandsMutable` (Runtime), `HairStrandsMutableEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-29 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/HairStrandsMutable) | |

---

## 用途

将 Mutable（可自定义对象系统）与 HairStrands（毛发系统）集成，提供在自定义对象图中直接引用 Groom 资源（发丝数据）的能力。该插件定义了一个编辑器节点 `UCustomizableObjectNodeGroomConstant`，允许用户在 Mutable 的 Customizable Object 图形中将一个 Groom 作为常量数据输入，从而在运行时通过 Mutable 系统动态生成带有自定义发型的角色。

解决的问题：在没有该插件之前，Mutable 仅支持普通 mesh、材质、贴图等，无法直接处理 HairStrands 的 Groom 资源。该扩展填补了这一空白，使得基于 Mutable 的角色自定义系统（如服装搭配、发型切换）能够直接使用高性能的 Strand-Based Hair。

---

## 使用场景

- 你在开发一个允许玩家自定义角色发型的游戏，发型使用 HairStrands 系统（Strand 发丝），同时角色整体使用 Mutable 进行服装/身体部件组合
- 你需要将发型作为 Mutable 自定义对象图中的一个输入，与其他身体部件一起参与 LOD、纹理等可配置参数
- 你需要在运行时通过 Mutable 动态切换不同的 Groom 资源（例如短发、长发、辫子），而不需要重新编译整个模型

---

## 蓝图用法

当前模块 `HairStrandsMutableEditor` 是一个编辑器模块，暴露的蓝图节点主要用于 Mutable Customizable Object 编辑器。核心节点为 `CustomizableObjectNodeGroomConstant`，它继承自 `UCustomizableObjectNodeExtensionDataConstant`。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CustomizableObjectNodeGroomConstant` | 在 Customizable Object 图中添加一个 Groom 常量节点，引用一个 Groom 资源 | `UCustomizableObjectNodeGroomConstant` |

**使用步骤**（蓝图级编辑器操作，非运行蓝图）：

1. 打开一个 Customizable Object 编辑器（如 `CustomizableObject` 蓝图编辑图）。
2. 在节点图上右键，选择 **Mutable > Extension Data > Groom Constant** 或直接在上下文菜单中搜索 "Groom Constant"。
3. 拖动创建出的节点，在细节面板中设置 `GroomData` 属性（类型为 `FGroomPinData`，通常包含一个 Groom Asset 引用）。
4. 连接该节点的输出引脚到支持 Extension Data 输入的节点（如 `ModifyExtensionData` 或自定义渲染节点）。

> 注意：`ShouldAddToContextMenu` 返回 `true`，因此该节点会自动出现在右键菜单中（分类由 `GetNodeTitle` 提供）。

---

## C++ 用法

### 头文件引入

```cpp
#include "CustomizableObjectNodeGroomConstant.h"
```

### 基本用法

以下示例演示如何在自定义代码中创建一个 `UCustomizableObjectNodeGroomConstant` 节点（通常用于编辑器自动化或测试）。此节点仅用于编辑器环境（`WITH_EDITOR`）。

```cpp
// 假设已在 CustomizableObject 编辑上下文中
UEdGraph* Graph = ...;
FGraphNodeCreator<UCustomizableObjectNodeGroomConstant> NodeCreator(*Graph);
UCustomizableObjectNodeGroomConstant* GroomNode = NodeCreator.CreateNode();
GroomNode->NodePosX = 100;
GroomNode->NodePosY = 200;

// 设置引用 Groom 资源
FGroomPinData GroomData;
GroomData.Groom = LoadObject<UGroomAsset>(nullptr, TEXT("/Game/MyHair.MyHair"));
GroomNode->GroomData = GroomData;

// 完成创建
NodeCreator.Finalize();
```

### 进阶用法

除了直接创建节点，还可以通过 `ICustomizableObjectExtensionNode` 接口扩展节点行为。该节点实现了 `GenerateMutableNode` 方法，负责在 Mutable 编译阶段生成对应的可编译数据。用户不需要手动调用，但可以重写该函数以添加自定义编译逻辑（当前实现为使用 `FGroomPinData` 生成）。

```cpp
// 在自定义派生类中重写
virtual UE::Mutable::Private::Ptr<UE::Mutable::Private::NodeExtensionData> GenerateMutableNode(
    FExtensionDataCompilerInterface& CompilerInterface) const override
{
    // 默认实现已处理 GroomData -> Mutable 内部数据转换
    return Super::GenerateMutableNode(CompilerInterface);
}
```

> 该函数位于 `UCustomizableObjectNodeGroomConstant`，属于编辑器模块 `HairStrandsMutableEditor`。

---

## Demo 示例

以下是一个可编译的最小示例，展示在编辑器模块中注册并测试该节点（需要 `WITH_EDITOR` 宏，且项目启用了 Mutable 和 HairStrands 插件）。

### File: `MyHairStrandsTest.h`

```cpp
#pragma once

#include "CoreMinimal.h"
#include "HairStrandsMutableEditor/Public/CustomizableObjectNodeGroomConstant.h"

namespace MyHairStrandsTest
{
    void CreateGroomNodeInGraph(class UEdGraph* Graph);
}
```

### File: `MyHairStrandsTest.cpp`

```cpp
#include "MyHairStrandsTest.h"
#include "EdGraph/EdGraph.h"
#include "GraphEditor.h"
#include "MuCOE/Nodes/CustomizableObjectNode.h"

namespace MyHairStrandsTest
{
    void CreateGroomNodeInGraph(UEdGraph* Graph)
    {
        if (!Graph) return;

        // 创建 Groom Constant 节点
        FGraphNodeCreator<UCustomizableObjectNodeGroomConstant> NodeCreator(*Graph);
        UCustomizableObjectNodeGroomConstant* GroomNode = NodeCreator.CreateNode();
        GroomNode->NodePosX = 200;
        GroomNode->NodePosY = 300;

        // 设置 Groom 数据（需要有效的 Groom 资源路径）
        FGroomPinData GroomData;
        GroomData.Groom = LoadObject<UGroomAsset>(nullptr, TEXT("/Game/Characters/Hair/LongHair.LongHair"));
        GroomNode->GroomData = GroomData;

        NodeCreator.Finalize();

        // 自动分配默认引脚
        GroomNode->AllocateDefaultPins(nullptr);
    }
}
```

> 注意：此示例需要在 `WITH_EDITOR` 环境下编译，且需要引用 `HairStrandsMutableEditor` 模块（在 Build.cs 中添加公共依赖）。

---

## 模块依赖

以下是 `HairStrandsMutableEditor` 的依赖（仅列出非标准依赖）：

| 模块 | 用途 |
|---|---|
| `HairStrands` | 提供 Groom 资源类型及渲染支持 |
| `Mutable` (核心) | Mutable 自定义对象系统运行时与编辑器核心 |
| `MuCOE` | Mutable Customizable Object 编辑器（节点基类 `UCustomizableObjectNodeExtensionDataConstant`） |
| `MuCO` | Mutable 运行时数据定义 |

**省略常见依赖**：Core, CoreUObject, Engine, Slate, SlateCore, UMG, InputCore, UnrealEd, EditorStyle, PropertyEditor, Projects, DeveloperSettings 等。

---

## 维护状态

### 近期更新

- 2025-09-01 `75e4adbd` [Mutable] Change namespace name（调整命名空间）
- 2025-08-29 `24228d19` [mutable] Changed friendly name to the MutableDataflow and HairStrandsMutable experimental plugins（修改友好名称）
- 2025-08-26 `1dbf0316` [Mutable] Add component naming support for spawned groom components（为生成的 Groom 组件添加命名支持）
- 2025-06-20 `1ec52cfd` [Mutable] Allow load and recompile of the CustomizableObject model when in-game mode（允许在游戏模式下加载和重新编译 CustomizableObject 模型）
- 2025-01-29 `ea8756da` [Mutable] Convert ModelResources to UObject（将 ModelResources 转换为 UObject 对象）

### 维护评价

- **创建时间**：2025-01-29，至今约 8 个月。
- **更新频率**：近半年有多次实质性更新（添加组件命名、允许运行时编译、命名空间调整），表明插件仍处于活跃开发阶段。
- **实验性状态**：`.uplugin` 中标记为 `IsExperimentalVersion=true`，属于早期实验功能，API 可能不稳定。
- **建议**：由于该插件依赖 Mutable（本身也是实验性）和 HairStrands，整体风险较高，适合原型验证或内部项目，不建议在生产游戏中直接使用。但如果项目已经使用 Mutable 毛发系统，该插件可大幅简化集成工作。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/HairStrandsMutable)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/mutable-overview/)（Mutable 官方文档，包含插件使用说明）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/HairStrandsMutable/Tests)（如存在）