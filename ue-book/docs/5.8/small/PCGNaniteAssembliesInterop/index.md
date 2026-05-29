# PCG Nanite Assemblies Interop

> Extra plugin for Procedural Content Generation Framework interacting with Nanite Assemblies.

| 属性 | 值 |
|---|---|
| 中文名 | PCG纳米组装互操作 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PCGNaniteAssembliesInterop` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-16 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGInterops/PCGNaniteAssembliesInterop) | |

## 用途

这个插件是PCG框架与Nanite组装技术之间的桥梁。它解决的核心问题是：在程序化生成内容（PCG）的工作流中，如何将PCG生成的点数据（Points）高效地转换为使用Nanite技术的静态网格体（Static Mesh），特别是支持Nanite组装（Nanite Assemblies）功能。

Nanite组装允许将多个静态网格体组合成一个更高效的渲染对象，此插件则允许PCG节点驱动这种组装的创建过程，从而在PCG生成的大型、复杂场景中充分利用Nanite的性能优化。

## 使用场景

-   **PCG生成大规模场景时**：你需要将PCG生成的散布点（例如树木、岩石）转换为利用Nanite组装优化的静态网格体，以提升渲染性能和内存效率。
-   **需要动态组装静态网格体**：你希望通过PCG逻辑，在运行时或编辑时根据属性动态决定将哪些网格体和材质组合成一个Nanite组装体。
-   **实验性PCG+Nanite工作流**：你正在探索如何将PCG的灵活性与Nanite的最新渲染特性结合，进行原型开发和概念验证。

## 蓝图用法

该插件主要提供了一个PCG设置节点，可在蓝图PCG图中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `PCGNaniteAssemblyStaticMeshBuilder` | 根据输入点数据创建Nanite组装的静态网格体。 | `UPCGNaniteAssemblyStaticMeshBuilderSettings` |

### 使用示例（蓝图描述）

1.  在PCG蓝图图中，从PCG图表编辑器拖入一个 **PCGNaniteAssemblyStaticMeshBuilder** 节点。
2.  将你生成点数据的PCG输出（如Surface Sampler, Point Generator等）连接到该节点的输入引脚。
3.  在节点的细节面板中配置：
    *   `MeshAttribute`：指定一个点属性，用于确定每个点要实例化哪个网格体。
    *   `MaterialOverrides`：指定一个或多个点属性数组，用于覆盖网格体对应槽位的材质。
    *   `ExportParams`：配置最终静态网格体资产的导出参数。
    *   `bSynchronousLoad`：调试选项，强制同步加载网格体和材质，便于调试。

## C++ 用法

此插件主要面向蓝图PCG用户，但也提供了C++扩展的可能性。

### 头文件引入

```cpp
#include "Elements/PCGNaniteAssemblyStaticMeshBuilder.h"
```

### 基本用法

从设置类派生，自定义Nanite组装构建器的行为。

```cpp
// 创建一个自定义的PCG设置类，继承自PCGNaniteAssemblyStaticMeshBuilderSettings
// 来源：基于 Elements/PCGNaniteAssemblyStaticMeshBuilder.h 推断
UCLASS()
class UMyCustomNaniteBuilderSettings : public UPCGNaniteAssemblyStaticMeshBuilderSettings
{
    GENERATED_BODY()

public:
    // 覆盖节点名称和标题
#if WITH_EDITOR
    virtual FName GetDefaultNodeName() const override { return FName("MyCustomNaniteBuilder"); }
    virtual FText GetDefaultNodeTitle() const override { return NSLOCTEXT("PCG", "MyCustomNaniteBuilder", "My Custom Nanite Builder"); }
#endif
};
```

### 进阶用法

在PCG元素中处理自定义上下文和异步加载。

```cpp
// 基于 FPCGNaniteAssemblyStaticMeshBuilderContext 的结构进行扩展
// 来源：基于 Elements/PCGNaniteAssemblyStaticMeshBuilder.h 推断
struct FMyCustomNaniteContext : public FPCGNaniteAssemblyStaticMeshBuilderContext
{
    // 添加额外的自定义数据
    int32 CustomProcessingStep = 0;
};

class FMyCustomNaniteElement : public FPCGNaniteAssemblyStaticMeshBuilderElement
{
protected:
    virtual bool PrepareDataInternal(FPCGContext* InContext) const override
    {
        // 可以在此进行自定义的数据准备逻辑
        // 调用基类方法进行默认处理
        return FPCGNaniteAssemblyStaticMeshBuilderElement::PrepareDataInternal(InContext);
    }
};
```

## Demo 示例

一个最小化的、自定义Nanite组装构建器设置的声明示例。

**MyNaniteBuilderSettings.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Elements/PCGNaniteAssemblyStaticMeshBuilder.h"
#include "MyNaniteBuilderSettings.generated.h"

UCLASS(MinimalAPI, BlueprintType, ClassGroup = (Procedural))
class UMyNaniteBuilderSettings : public UPCGNaniteAssemblyStaticMeshBuilderSettings
{
    GENERATED_BODY()

public:
#if WITH_EDITOR
    virtual FName GetDefaultNodeName() const override { return FName("MyNaniteBuilder"); }
    virtual FText GetDefaultNodeTitle() const override { return NSLOCTEXT("PCG", "MyNaniteBuilder", "My Nanite Builder"); }
    virtual FText GetNodeTooltipText() const override { return NSLOCTEXT("PCG", "MyNaniteBuilderTooltip", "My custom builder for Nanite assemblies."); }
#endif

protected:
    virtual TArray<FPCGPinProperties> InputPinProperties() const override
    {
        TArray<FPCGPinProperties> Pins = Super::InputPinProperties();
        // 可以在此添加额外的输入引脚
        return Pins;
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PCG` | 核心的程序化内容生成框架。 |
| `NaniteAssemblyEditorUtils` | 提供Nanite组装的编辑器工具和核心功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-09-17 | `ec984481` | [PCG] Small QoL for Nanite Assembly Builder | 为Nanite组装构建器添加了小型生活质量改进。 |
| 2025-09-16 | `bd70919e` | [PCG - Nanite Assemblies] Initial prototype of Nanite Assemblies builder | 创建了Nanite组装构建器的初始原型。 |

### 维护评价

此插件创建于2025年9月，**极其年轻**，目前处于**活跃的初始开发阶段**。

*   **优点**：由Epic Games官方在开发，代码质量有保障。最近一次提交在创建后一天内，表明正在积极开发中。
*   **风险与限制**：这是一个**实验性插件**（`IsExperimentalVersion=true`），并且默认未启用（`EnabledByDefault=false`）。API和功能在未来版本中**极有可能发生破坏性变更**。目前仅为初始原型，功能和稳定性未经大规模验证。
*   **建议**：不推荐用于生产环境。仅适合在实验性项目、原型设计或学习研究PCG与Nanite集成时试用。请密切关注其后续版本更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGInterops/PCGNaniteAssembliesInterop)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGInterops/PCGNaniteAssembliesInterop/Tests) (如果存在)