# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.

| 属性 | 值 |
|---|---|
| 分类 | CustomizableObjects |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（工具、运行时） |
| 模块 | `MutableRuntime` (Runtime), `CustomizableObject` (Runtime), `MutableTools` (Runtime), `MutableValidation` (Runtime), `CustomizableObjectEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-09-26 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Mutable) | |

## 用途

Mutable 是一个用于创建**运行时可定制对象**的完整系统。它解决的核心问题是：如何在不显著增加内存和磁盘占用的前提下，让游戏中的资产（如角色、装备、载具）在运行时拥有高度的可变性。

传统的做法是为每一种变体创建一个独立的资产，这会导致资产数量爆炸。Mutable 通过一个**基于节点图的工具链**（MutableTools）来定义资产的可变部分（如纹理、网格、材质参数），并在运行时（MutableRuntime）根据玩家的选择或游戏逻辑，动态地合成最终的资产。这使得开发者可以创建一个基础资产，然后通过参数组合生成成千上万种视觉变体，同时保持较低的内存占用和高效的加载速度。

## 使用场景

- **角色换装系统**：玩家可以自由组合发型、服装、配饰、纹身等，系统实时生成最终的角色外观。
- **装备外观定制**：武器、盔甲等装备可以通过更换贴花、改变材质颜色、添加附件等方式进行个性化。
- **程序化生成变体**：为游戏中的NPC或环境物体生成大量视觉上略有差异的变体，增加世界丰富度。
- **动态材质效果**：根据游戏状态（如角色血量、环境光照）实时修改材质参数，实现动态视觉效果。

## 蓝图用法

Mutable 插件的核心是一个 C++ 节点图系统和运行时库。其主要的用户交互界面是 **Customizable Object** 资产编辑器，这是一个基于节点图的可视化工具，用于定义可定制对象的逻辑。在蓝图中，通常不直接操作底层的 `MutableTools` 节点，而是通过操作 `UCustomizableObjectInstance` 来设置参数并触发更新。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Vector Parameter Value` | 设置可定制对象实例的向量参数（如颜色） | `UCustomizableObjectInstance` |
| `Set Scalar Parameter Value` | 设置可定制对象实例的标量参数（如浮点数） | `UCustomizableObjectInstance` |
| `Set Bool Parameter Value` | 设置可定制对象实例的布尔参数 | `UCustomizableObjectInstance` |
| `Set Projector Parameter Value` | 设置可定制对象实例的投影器参数（用于贴花等） | `UCustomizableObjectInstance` |
| `Update Skeletal Mesh` | 根据当前参数更新实例的骨骼网格体 | `UCustomizableObjectInstance` |
| `Update Cloth` | 根据当前参数更新实例的布料模拟数据 | `UCustomizableObjectInstance` |

### 使用示例（蓝图描述）

1.  **创建实例**：从 `UCustomizableObject` 资产创建一个 `UCustomizableObjectInstance`。
2.  **设置参数**：使用 `Set Scalar Parameter Value` 等节点，根据玩家选择设置实例的各个参数（例如，将“肤色”参数设为0.8，“发型”参数设为2）。
3.  **触发更新**：调用 `Update Skeletal Mesh` 节点。系统会根据设置的参数，动态合成并应用新的网格体和材质到关联的 `SkeletalMeshComponent` 上。

## C++ 用法

`MutableTools` 模块提供了用于程序化构建可定制对象节点图的 C++ API。这通常用于自动化资产生成流程或创建复杂的、无法仅通过编辑器完成的定制逻辑。

### 头文件引入

```cpp
#include "MuT/Node.h"
#include "MuT/NodeScalarConstant.h"
#include "MuT/NodeImageSwitch.h"
#include "MuT/NodeMesh.h"
// ... 根据需要引入其他节点类型头文件
```

### 基本用法

以下示例展示了如何用 C++ 创建一个简单的节点图，该图根据一个标量参数在两张纹理之间切换。
（来源：基于 `NodeScalarSwitch` 和 `NodeImageSwitch` 的设计模式推断）

```cpp
using namespace UE::Mutable::Private;

// 1. 创建一个标量参数节点，它将作为选择器
Ptr<NodeScalarParameter> SelectorParam = new NodeScalarParameter();
SelectorParam->Name = TEXT("TextureSelector");

// 2. 创建两个图像节点（这里用常量示意，实际可能是纹理引用）
Ptr<NodeImageConstant> ImageA = new NodeImageConstant();
Ptr<NodeImageConstant> ImageB = new NodeImageConstant();

// 3. 创建一个图像切换节点
Ptr<NodeImageSwitch> ImageSwitch = new NodeImageSwitch();
ImageSwitch->Parameter = SelectorParam; // 连接参数
ImageSwitch->Options.Add(ImageA);       // 添加选项0
ImageSwitch->Options.Add(ImageB);       // 添加选项1

// 4. 将 ImageSwitch 作为最终输出连接到对象的某个图像通道
// ... (连接到 NodeObject 的相应输入)
```

### 进阶用法

结合多个节点类型可以构建复杂的逻辑。例如，创建一个根据角色等级（标量）改变装备材质颜色（颜色），并同时切换装备网格（网格）的系统。

```cpp
// 假设已有等级参数节点 LevelParam

// 颜色逻辑：等级 < 10 为白色，>= 10 为金色
Ptr<NodeScalarConstant> Ten = new NodeScalarConstant();
Ten->Value = 10.0f;
Ptr<NodeScalarLess> IsLowLevel = new NodeScalarLess();
IsLowLevel->A = LevelParam;
IsLowLevel->B = Ten;

Ptr<NodeColourConstant> White = new NodeColourConstant();
White->Value = FVector4f(1,1,1,1);
Ptr<NodeColourConstant> Gold = new NodeColourConstant();
Gold->Value = FVector4f(1, 0.84f, 0, 1);

Ptr<NodeColourSwitch> ColorSwitch = new NodeColourSwitch();
ColorSwitch->Parameter = IsLowLevel; // 使用比较结果作为布尔选择器
ColorSwitch->Options.Add(White);
ColorSwitch->Options.Add(Gold);

// 网格逻辑：等级 < 10 用基础剑，>= 10 用黄金剑
Ptr<NodeMesh> BasicSword = ...; // 引用基础网格
Ptr<NodeMesh> GoldSword = ...;  // 引用黄金网格

Ptr<NodeMeshSwitch> MeshSwitch = new NodeMeshSwitch();
MeshSwitch->Parameter = IsLowLevel;
MeshSwitch->Options.Add(BasicSword);
MeshSwitch->Options.Add(GoldSword);

// 将 ColorSwitch 和 MeshSwitch 分别连接到对象材质和网格的输出节点
```

## Demo 示例

一个最小化的 C++ 示例，展示如何构建一个包含标量参数和图像切换的可定制对象定义。

**MyCustomizableObjectBuilder.h**
```cpp
#pragma once

#include "MuT/NodeObjectNew.h"
#include "MuT/NodeScalarParameter.h"
#include "MuT/NodeImageSwitch.h"
#include "MuT/NodeImageConstant.h"

class FMyCustomizableObjectBuilder
{
public:
    static UE::Mutable::Private::Ptr<UE::Mutable::Private::NodeObjectNew> BuildSimpleObject();
};
```

**MyCustomizableObjectBuilder.cpp**
```cpp
#include "MyCustomizableObjectBuilder.h"

using namespace UE::Mutable::Private;

Ptr<NodeObjectNew> FMyCustomizableObjectBuilder::BuildSimpleObject()
{
    // 创建对象根节点
    Ptr<NodeObjectNew> RootObject = new NodeObjectNew();
    RootObject->Name = TEXT("SimpleSword");

    // 创建标量参数节点
    Ptr<NodeScalarParameter> SkinParam = new NodeScalarParameter();
    SkinParam->Name = TEXT("SkinType");
    SkinParam->DefaultValue = 0.0f;

    // 创建两个图像常量节点（代表两种皮肤纹理）
    Ptr<NodeImageConstant> SkinA = new NodeImageConstant();
    // SkinA->Value = ...; // 设置纹理数据
    Ptr<NodeImageConstant> SkinB = new NodeImageConstant();
    // SkinB->Value = ...; // 设置纹理数据

    // 创建图像切换节点
    Ptr<NodeImageSwitch> SkinSwitch = new NodeImageSwitch();
    SkinSwitch->Parameter = SkinParam;
    SkinSwitch->Options.Add(SkinA);
    SkinSwitch->Options.Add(SkinB);

    // 将切换节点连接到对象的“基础颜色”图像通道
    // 注意：实际连接需要通过 NodeComponent 和 NodeSurface 等中间节点，此处为简化示意。
    // RootObject->Components[0]->Surfaces[0]->ImageChannels[BaseColorIndex] = SkinSwitch;

    return RootObject;
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。`MutableTools` 模块本身是一个纯 C++ 库，不依赖 UE 的编辑器或特定运行时模块。其上层模块 `CustomizableObject` 依赖 `UnrealEd`、`DerivedDataCache` 等，但这些是编辑器和通用模块，对于仅使用运行时功能的项目无需额外关注。

## 维护状态

### 近期更新

- 2025-10-03 e5fb0aef9746 [mutable] Fixed CO Compilation race condition due to the wrong mutex being used.
- 2025-09-15 0ce66e5a582b [mutable] Fixed bug preventing the activation of some sections due to the wrong handling of repeated section tags. - Previously, if two sections did share the same tag, both sections were required to be active for the tag to be enabled. Now, as it is expected, only one section is required to activate the tag. - Replaced some code with more functional code (removed pointer operations). - Fixed some typos - Improved overall code readability by enforcing UE coding standards.
- 2025-08-20 c15f1e279d4c [mutable] Updated Required Tags and MultipleTagPolicy comments in favor of more descriptive ones.

### 维护评价

Mutable 是一个相对较新（约3年）且**活跃维护**的插件。从近期提交记录看，Epic 团队仍在持续修复 bug（如竞态条件、标签逻辑错误）并改进代码质量。作为官方插件，其稳定性和与引擎版本的兼容性有保障。它解决了游戏开发中一个常见且复杂的需求（资产定制化），并提供了从工具到运行时的完整解决方案。**推荐使用**，特别是对于需要高度角色或装备定制化的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Mutable)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Mutable/Tests)