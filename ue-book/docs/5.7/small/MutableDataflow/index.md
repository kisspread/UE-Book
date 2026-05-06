# Mutable Dataflow Extensions

> Adds Mutable functionality to work with Dataflow objects from the Dataflow plugin. WARNING: All nodes in this plugin are experimental and will be changed/deprecated in the future. The Dataflow system does not yet fully support mutable so the functionality of these nodes is currently quite limited and manual.

| 属性 | 值 |
|---|---|
| 中文名 | Mutable 数据流扩展 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MutableDataflowEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-29 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MutableDataflow) | |

## 用途

本插件为 Dataflow 系统添加了一组实验性的 Mutable 节点，允许你在 Dataflow 图中创建和配置 CustomizableObject 实例（COI），并提取其生成的 Skeletal Mesh 资源。

**为什么存在？**  
Mutable 本身是一个运行时自定义系统，但它与 Dataflow 的数据驱动工作流结合后，可以在编辑器中将自定义参数（如替换骨骼网格、纹理、材质）以节点图的形式表达，并通过 Dataflow 节点输出最终生成的网格。目前该集成非常早期，节点功能有限，主要用于原型验证。

## 使用场景

- 你正在使用 **Dataflow** 构建程序化资产生成管线，并希望引入 **Mutable** 的动态参数化能力（例如运行时装备切换、角色外观自定义）。
- 你需要将 Mutable 的 CustomizableObjectInstance 生成逻辑 **可视化** 地集成到 Dataflow 图中，而不是手动编写 C++ 或蓝图逻辑。
- 你正在探索 **Experimental** 功能，愿意接受 API 变化和有限的功能。

## 蓝图用法

本插件所有节点都是 **Dataflow 节点**，并非蓝图节点。它们只能在 Dataflow 资产（`.Dataflow`）的编辑图中使用。节点通过 `USTRUCT` 宏定义，并带有 `meta=(Experimental)` 和 `DATAFLOW_NODE_DEFINE_INTERNAL`。

### 核心节点

| 节点 | 说明 | 所在结构 |
|---|---|---|
| `GenerateCustomizableObjectInstance` | 根据输入的 CustomizableObject 和参数数组生成 COI，并输出 `GeneratedResources` | `FCOInstanceGeneratorNode` |
| `GetComponentMesh` | 从 GeneratedResources 中根据组件名称提取对应的 `SkeletalMesh` | `FCOInstanceGetComponentMesh` |
| `MutableSkeletalMeshParameter` | 将参数名称和 SkeletalMesh 打包为单个 `FMutableSkeletalMeshParameter` | `FMutableSkeletalMeshParameterNode` |
| `MutableTextureParameter` | 将参数名称和 Texture2D 打包为单个 `FMutableTextureParameter` | `FMutableTextureParameterNode` |
| `MutableMaterialParameter` | 将参数名称和 MaterialInterface 打包为单个 `FMutableMaterialParameter` | `FMutableMaterialParameterNode` |
| `MakeMutableSkeletalMeshParametersArray` | 将多个 `FMutableSkeletalMeshParameter` 合并为数组（支持动态增加/删除输入引脚） | `FMakeMutableSkeletalMeshParametersArrayNode` |
| `MakeMutableTextureParametersArray` | 将多个 `FMutableTextureParameter` 合并为数组 | `FMakeMutableTextureParametersArrayNode` |
| `MakeMutableMaterialParametersArray` | 将多个 `FMutableMaterialParameter` 合并为数组 | `FMakeMutableMaterialParametersArrayNode` |

### 使用示例（蓝图描述）

这些节点只能在 Dataflow 编辑器中使用，无法在蓝图图表中添加。以下描述假设你已开启 Dataflow 插件（`Dataflow`）并创建一个 Dataflow 资产。

1. **基本流程**：  
   - 添加 `GenerateCustomizableObjectInstance` 节点，连接一个 `CustomizableObject` 引用作为输入。
   - 可选地，连接 `SkeletalMeshParameters`、`TextureParameters`、`MaterialParameters` 数组输入（使用对应的 `MakeMutable*Array` 节点构建）。
   - 从 `COInstanceGeneratorNode` 的输出 `GeneratedResources` 连接到 `GetComponentMesh` 节点，指定 `ComponentName` 字符串输入（例如 `"body"`），输出为 `USkeletalMesh`。

2. **构建参数数组**：  
   - 添加 `MutableSkeletalMeshParameter` 节点，设置 `ParameterName` 和 `SkeletalMesh` 输入。
   - 再添加一个 `MakeMutableSkeletalMeshParametersArray` 节点，它会自动生成一个初始输入引脚；你可以通过右键菜单或节点上的“+”按钮添加更多输入引脚，将各个 `MutableSkeletalMeshParameter` 节点的输出连接到这些引脚上。

3. **实验性限制**：  
   插件声明中强调这些节点是实验性的，目前功能有限且需手动管理。不建议用于生产项目。

## C++ 用法

由于插件主要提供编辑器端的 Dataflow 节点，C++ 使用者通常无需直接实例化这些结构，而是通过 Dataflow 图资产引擎自动调用节点的 `Evaluate` 方法。以下内容供自定义 Dataflow 节点开发参考。

### 头文件引入

```cpp
#include "MutableDataflowEditorModule.h"
#include "Nodes/COInstanceGeneratorNode.h"
#include "Nodes/MutableSkeletalMeshParameterNode.h"
// ... 其他节点头文件
```

### 基本用法

节点通过 `FDataflowNode::Evaluate` 在 Dataflow 上下文中执行。例如 `FCOInstanceGeneratorNode` 的典型评估流程（来自 `Source/MutableDataflowEditor/Private/Nodes/COInstanceGeneratorNode.cpp`）：

```cpp
void FCOInstanceGeneratorNode::Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const
{
    // 1. 获取输入 CustomizableObject
    const TObjectPtr<UCustomizableObject>& CO = GetValue<TObjectPtr<UCustomizableObject>>(Context, CustomizableObjectInput);
    
    // 2. 获取输入参数数组（骨骼网格、纹理、材质）
    TArray<FMutableSkeletalMeshParameter> SkeletalParams = GetValue<TArray<FMutableSkeletalMeshParameter>>(Context, SkeletalMeshParametersInput);
    // ... 类似获得纹理和材质参数
    
    // 3. 创建 CustomizableObjectInstance 并设置参数
    UCustomizableObjectInstance* Instance = ...;
    // 遍历参数并设置到 Instance 上
    
    // 4. 更新实例并提取生成的骨骼网格列表
    TArray<FMutableGeneratedResource> GeneratedResources;
    // ...
    
    // 5. 输出 GeneratedResources
    SetValue(Context, GeneratedResourcesOutput, GeneratedResources);
}
```

### 进阶用法

想要在代码中直接使用这些节点（而不通过 Dataflow 资产），可以手动模拟 Dataflow 上下文：

```cpp
#include "Dataflow/DataflowNode.h"
#include "Dataflow/DataflowContext.h"

void ManualEvaluate()
{
    // 创建节点实例（通常由 Dataflow 图管理，此处仅为示意）
    FGuid NodeGuid = FGuid::NewGuid();
    UE::Dataflow::FNodeParameters Params;
    FCOInstanceGeneratorNode Node(Params, NodeGuid);
    
    // 建立上下文
    UE::Dataflow::FContext Context;
    
    // 设置输入值
    TObjectPtr<UCustomizableObject> MyCO = ...; // 加载你的 CustomizableObject
    SetValue(Context, Node.CustomizableObjectInput, MyCO);
    // ... 设置其他输入
    
    // 执行评估
    Node.Evaluate(Context, &Node.GeneratedResourcesOutput);
    
    // 获取结果
    TArray<FMutableGeneratedResource> Result = GetValue<TArray<FMutableGeneratedResource>>(Context, Node.GeneratedResourcesOutput);
}
```

**注意**：直接调用 `Evaluate` 需要自行处理 Dataflow 图依赖和缓存，实际项目中更推荐使用 Dataflow 资产。

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何注册插件模块并确保 Dataflow 节点可用（无需手动调用节点，节点自动由资产系统管理）。

### `MutableDataflowDemo.h`

```cpp
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"

class FMutableDataflowDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

### `MutableDataflowDemo.cpp`

```cpp
#include "MutableDataflowDemo.h"
#include "MutableDataflowEditorModule.h" // 如果插件模块自动加载，无需显式包含

IMPLEMENT_MODULE(FMutableDataflowDemoModule, MutableDataflowDemo);

void FMutableDataflowDemoModule::StartupModule()
{
    // 本插件（MutableDataflow）作为依赖会自动加载，节点自动注册到 Dataflow 系统
    UE_LOG(LogTemp, Log, TEXT("MutableDataflowDemo 模块已启动。"));
}

void FMutableDataflowDemoModule::ShutdownModule()
{
}
```

**使用方式**：  
1. 在你的项目或插件的 `Build.cs` 中添加 `"MutableDataflowEditor"` 和 `"Dataflow"`、`"Mutable"` 依赖（见下一章）。  
2. 创建一个 Dataflow 资产，右键添加节点即可在 `Mutable` 类别下看到所有实验性节点。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Dataflow` | 提供 Dataflow 框架核心：节点基类、上下文、输入/输出注册 |
| `Mutable` | 提供 Mutable 核心类型：`UCustomizableObject`、`UCustomizableObjectInstance`、参数设置等 |

**无特殊依赖（仅标准 Core/Engine/Slate 等）**。

## 维护状态

### 近期更新

- 2025-09-04 `54a347bf` — [mutable-Dataflow] Set the MutableDataflow plugin disabled by default  
- 2025-08-29 `06bc17a1` — [mutable] Fixed dataflow node issue causing the generation of COIs even after a compilation failure  
- 2025-08-29 `24228d19` — [mutable] Changed friendly name to the MutableDataflow and HairStrandsMutable experimental plugins.  
- 2025-08-29 `553d524d` — [mutable] Renamed the plugin "DataflowMutable" to "MutableDataflow"  

### 维护评价

- **创建时间**：2025-08-29，距今不到一个月，属于全新插件。  
- **活跃度**：截至最后一个提交（2025-09-04），有多次提交，包括重命名和修复，显示团队正在积极开发。  
- **稳定性**：`IsExperimentalVersion=true`，警告“所有节点均为实验性且将来会更改/废弃”，不推荐用于生产。  
- **推荐使用场景**：仅适用于原型验证或对最新技术感兴趣的开发者，不建议依赖其 API 的稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MutableDataflow)  
- 官方文档：无（实验性插件，暂无独立文档）