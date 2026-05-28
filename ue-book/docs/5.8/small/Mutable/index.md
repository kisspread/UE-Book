# Mutable

> Mutable adds the tools and runtime to create customizable objects for your games.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 可变对象系统 |
| 分类 | CustomizableObjects |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `CustomizableObject` (Runtime), `CustomizableObjectEditor` (Runtime), `MutableRuntime` (Runtime), `MutableTools` (Runtime), `MutableValidation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable) | |

## 用途

Mutable 是一个完整的 **可定制对象（Customizable Object）系统**，旨在解决游戏运行时动态生成和修改复杂资产（如角色、装备）的问题。它提供了从编辑器工具链到运行时生成的一整套解决方案，允许开发者定义对象的可变属性（如纹理、网格、材质），并在运行时根据这些属性高效地生成最终的游戏资产，从而实现高度可定制的游戏内容，如玩家角色捏脸、装备组合等。

## 使用场景

- **玩家角色深度自定义**：实现类似《黑神话：悟空》的装备组合系统，玩家可以自由搭配头、身、手、腿等部位的装备，系统实时生成最终的角色网格和材质。
- **动态外观变化**：在游戏中根据状态（如损坏、沾染泥土、涂装）动态改变物体的纹理和材质。
- **装备与部件系统**：管理大量可组合的装备部件，运行时按需生成，减少初始内存占用和加载时间。
- **LOD 与流送优化**：根据可定制对象的复杂性，生成优化的 LOD 层级和流送数据。

## 蓝图用法

Mutable 提供了丰富的蓝图节点，主要围绕可定制对象实例的创建、参数修改和最终应用展开。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Customizable Object Instance` | 从一个可定制对象资产创建一个新的实例。 | `UCustomizableObjectInstance` |
| `Set (各种参数)` | 设置实例上的参数值，如 `Set Int Parameter Value`, `Set Float Parameter Value`, `Set Vector Parameter Value`。 | `UCustomizableObjectInstance` |
| `Update Customizable Object` | 在设置参数后，调用此节点开始处理并生成最终的资源（如网格、纹理）。此过程可能异步。 | `UCustomizableObjectInstance` |
| `Apply Customizable Object` | 将生成的资源应用到目标组件（如 `SkeletalMeshComponent`）上。 | `UCustomizableObjectInstance` |
| `Get Parameter Value` | 获取实例上当前设置的参数值。 | `UCustomizableObjectInstance` |
| `Get Customizable Object` | 从实例中获取其源可定制对象资产。 | `UCustomizableObjectInstance` |

### 使用示例（蓝图描述）

1.  **创建实例**：使用 `Create Customizable Object Instance` 节点，从一个已配置好的 `CustomizableObject` 资产创建一个新实例。
2.  **设置参数**：调用一系列 `Set xxx Parameter Value` 节点，为该实例的各个可变参数（如 `HeadIndex`, `ShirtColor`）赋值。这些参数值可以来自玩家选择或游戏逻辑。
3.  **生成与应用**：调用 `Update Customizable Object` 触发资产生成（可能是异步的）。待生成完成后，调用 `Apply Customizable Object` 并将目标 `SkeletalMeshComponent` 作为参数，将生成的最终网格和材质应用到角色上。

## C++ 用法

Mutable 的 C++ 接口与蓝图类似，但更底层且灵活，常用于需要更精细控制或高性能批量处理的场景。

### 头文件引入

```cpp
#include "CustomizableObject.h"
#include "CustomizableObjectInstance.h"
```

### 基本用法

创建并操作一个可定制对象实例。
（来源：引擎使用模式及 `CustomizableObject` 模块核心代码）

```cpp
// 假设你有一个已加载的 UCustomizableObject* 指针 CustomizableObjectAsset
UCustomizableObjectInstance* MyInstance = CustomizableObjectAsset->CreateInstance();

// 设置参数
MyInstance->SetIntParameter(TEXT("HeadIndex"), 2);
MyInstance->SetFloatParameter(TEXT("BodyFat"), 0.8f);

// 触发更新（可以绑定委托来知道何时完成）
MyInstance->UpdateSkeletalMeshAsync(true, FOnUpdateSkeletalMeshCompleted::CreateLambda(
    [&](UCustomizableObjectInstance* Instance)
    {
        // 生成完成，可以应用了
        MySkeletalMeshComponent->SetSkeletalMesh(Instance->GetSkeletalMesh());
    }
));
```

### 进阶用法

1.  **监听参数变化**：通过 `UCustomizableObjectInstance::OnParameterChanged` 委托响应特定参数的变化，实现动态 UI 更新。
2.  **资源管理与优化**：利用 `MutableRuntime` 提供的底层缓存和流送接口，管理生成资产的生命周期，优化内存使用。
3.  **编辑器扩展**：使用 `CustomizableObjectEditor` 和 `MutableTools` 模块中的 API，在编辑器工具中创建自定义的资产预览或批量处理工具。

## 模块列表

| 模块 | 一句话说明 |
|---|---|
| **CustomizableObject** | **核心运行时模块**。包含可定制对象资产 (`UCustomizableObject`) 和实例 (`UCustomizableObjectInstance`) 的定义与核心运行时逻辑，是使用者最常交互的模块。 |
| **CustomizableObjectEditor** | **编辑器扩展模块**。提供在 Unreal Editor 中创建、编辑和预览 `CustomizableObject` 资产所需的 UI 工具和资产编辑器。 |
| **MutableRuntime** | **底层运行时引擎**。包含 Mutable 系统的核心算法、数据结构和优化后的运行时执行代码，负责实际的资产生成计算。 |
| **MutableTools** | **构建时处理工具**。包含将编辑器中设计的可定制对象转换为运行时高效数据格式所需的工具链和处理逻辑。 |
| **MutableValidation** | **验证与测试工具**。提供用于验证可定制对象资产正确性、检查潜在问题的工具和运行时验证逻辑。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `70229bdc` | [Mutable] Fix duplicated Skeletal Mesh geometry if there is multiple SKM with the same name. | 修复了当存在同名骨骼网格体时，生成的几何体重复的问题。 |
| 2026-05-26 | `2b0ca8bd` | [mutable] Fixed "Clip mesh with UV Mask" op not loading the appropriate mask mip. | 修复了“使用UV遮罩裁剪网格”操作未能加载正确遮罩Mip级别的问题。 |
| 2026-05-26 | `06ea27d3` | [Mutable] Fix texture parameters using the wrong method to compute the LODBias. An incorrect LODBias | 修复了纹理参数使用了错误的LODBias计算方法。 |
| 2026-05-26 | `e9c39661` | [Mutable] Allow more clothing asset types by using the ClothingAssetBase interface. | 通过使用 `ClothingAssetBase` 接口，允许支持更多类型的布料资产。 |
| 2026-05-25 | `c8ce9ff7` | [Mutable] Fix possible data race when comparing PassthroughObjects. | 修复了比较直通对象时可能出现的数据竞争问题。 |

### 维护评价

- **活跃维护**：该插件于 **2024年9月** 从实验状态移入Beta版，距今不到两年。从近期 Git 历史看，**维护非常活跃**，最近几天（截至提供的历史）连续提交了多个重要的 Bug 修复和功能优化，涉及几何体生成、纹理处理、布料支持和多线程安全等核心领域。
- **Beta 状态**：当前版本为 1.8.0，仍处于 **Beta 测试阶段**。这意味着功能基本完整，但 API 可能还会调整，且可能存在未发现的边缘情况问题。
- **推荐使用**：**推荐在项目中试用和集成**，特别是对于需要深度角色定制或复杂资产组合的项目。鉴于其 Beta 状态和活跃的修复速度，建议密切关注更新日志，并做好应对潜在问题或 API 变更的准备。它已成为 UE5 中实现该类功能的官方核心方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Mutable)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/customizable-objects-in-unreal-engine/)（UE 官方可定制对象文档，可能包含此插件内容）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Mutable)（引擎级测试，路径可能）