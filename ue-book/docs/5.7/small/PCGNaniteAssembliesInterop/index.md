# Procedural Content Generation Framework (PCG) Nanite Assemblies Interop

> Extra plugin for Procedural Content Generation Framework interacting with Nanite Assemblies.

| 属性 | 值 |
|---|---|
| 中文名 | PCG Nanite 装配体互操作性 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PCGNaniteAssembliesInterop` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PCGInterops/PCGNaniteAssembliesInterop) | |

## 用途

此插件为 Procedural Content Generation Framework (PCG) 提供了一个实验性节点，能够将 Nanite 装配体（Nanite Assemblies）整合到程序化生成流程中。它允许你从输入的点数据创建静态网格（Static Mesh），其中每个点可以引用一个已有的 Nanite 装配体网格，并支持通过属性选择器动态覆盖材质。主要用于在编辑器环境下，利用 Nanite 的高性能渲染能力，程序化地生成复杂、细节丰富的场景元素。

**为什么存在？**  
- PCG 原生支持生成静态网格，但需要手动引用每个网格资源。此插件扩展了 PCG，使其能与 Nanite 装配体无缝交互，简化了大型场景中重复使用 Nanite 网格的流程。
- 通过属性选择器，可以将点数据的属性（如随机选择的网格）动态绑定到每个生成点上，实现高度可变的程序化输出。

## 使用场景

- **场景地形装饰**：在程序化生成的地形上，使用 Nanite 装配体（如岩石、树木、建筑碎片）作为装饰物，每个点根据属性选择不同的网格并覆盖材质。
- **建筑群生成**：通过 PCG 规则生成建筑轮廓点，每个点引用一个 Nanite 装配体（如窗户、阳台模块），快速构建可交互建筑。
- **动态 LOD 优化**：由于使用 Nanite 装配体，生成的网格自动受益于 Nanite 的虚拟几何体系统，无需手动管理 LOD。

## 蓝图用法

此插件核心是一个 PCG 节点（`PCGNaniteAssemblyStaticMeshBuilder`），节点名称为“Nanite Assembly Static Mesh Builder”。你可以在 PCG 图表中将它连接在点数据输出之后，设置属性即可使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `PCGNanite Assembly Static Mesh Builder` | 根据输入的点数据，为每个点创建一个由指定 Nanite 装配体构成的静态网格 | `UPCGNaniteAssemblyStaticMeshBuilderSettings` |

### 使用示例（蓝图描述）

1. **基本流程**  
   在 PCG 图表中放置 `Nanite Assembly Static Mesh Builder` 节点，将上游的点数据（如来自 `Surface Sampler` 或 `Spawn Points`）连接到其输入引脚。  
   节点的输出会生成静态网格，可连接至 `Static Mesh Spawner`（或直接通过 `Export` 节点导出）。

2. **配置属性**  
   - **MeshAttribute**：选择点数据上的一个属性，该属性应存储对 `StaticMesh` 对象的引用（如 `SoftObjectPath(UStaticMesh)`）。节点会读取此属性决定每个点生成哪个网格。  
   - **MaterialOverrides**：提供一个属性选择器数组，用于覆盖生成网格上的材质插槽。每个选择器对应一个材质槽（如 `StaticMeshComponent` 的 Material Slots）。  
   - **ExportParams**：设置导出参数（如资产路径、命名规则），控制生成网格的保存方式。  
   - **Synchronous Load**：勾选后，网格和材质会同步加载（异步加载为默认），适合调试或小规模生成。

3. **材质覆盖示例**  
   例如，点数据有一个属性 `TileMaterial`（类型为 `SoftObjectPath(UMaterialInterface)`）。将 `MaterialOverrides` 数组的第一个元素设置为该属性选择器，则生成时每个点会用自己的 `TileMaterial` 覆盖网格的第一个材质槽。

## C++ 用法

此插件主要面向 PCG 节点的直接使用，若需在 C++ 中构建自定义 PCG 图或对节点进行脚本化控制，可按以下方式操作。

### 头文件引入

```cpp
#include "Elements/PCGNaniteAssemblyStaticMeshBuilder.h"
```

### 基本用法

创建设置对象并配置属性，然后通过 `FPCGNaniteAssemblyStaticMeshBuilderElement` 执行。

```cpp
// 来源：Engine/Plugins/Experimental/PCGInterops/PCGNaniteAssembliesInterop/Source/PCGNaniteAssembliesInterop/Private/Elements/PCGNaniteAssemblyStaticMeshBuilder.h

// 1. 创建设置对象
UPCGNaniteAssemblyStaticMeshBuilderSettings* Settings = NewObject<UPCGNaniteAssemblyStaticMeshBuilderSettings>();

// 2. 配置属性选择器
Settings->MeshAttribute.SetAttributeName(TEXT("Mesh")); // 选择点数据中的 "Mesh" 属性
Settings->MaterialOverrides.Add({}); // 添加一个空选择器，后续选择材质覆盖属性
Settings->MaterialOverrides[0].SetAttributeName(TEXT("OverrideMat"));

// 3. 设置导出参数
Settings->ExportParams.OutputPath = TEXT("/Game/Generated/MyMesh");

// 4. 同步加载（可选）
Settings->bSynchronousLoad = true;

// 5. 执行元素（需在 PCG 图上下文中使用）
// 通常通过 PCG 图框架调用；若手动执行，需构造 FPCGContext 并调用元素
```

### 进阶用法

结合 PCG 节点创建与执行：

```cpp
// 假设已有 PCG 图实例和输入点数据
TArray<FPCGPoint> Points;
// ... 填充点数据，并为每个点添加属性 "Mesh"（SoftObjectPath）

FPCGDataCollection InputData;
InputData.TaggedData.Add(FPCGTaggedData{ Points });

UPCGNode* Node = PCGGraph->AddNodeOfType(UPCGNaniteAssemblyStaticMeshBuilderSettings::StaticClass());
// 设置节点输入、连接等...
// 然后通过 PCGGraph 的执行管线运行
```

## Demo 示例

以下是一个最小化 C++ 示例，展示如何在游戏模块中创建并使用该节点设置属性（假定 PCG 图已存在）：

```cpp
// DemoNaniteBuilder.h
#pragma once
#include "CoreMinimal.h"
#include "PCGContext.h"
#include "UObject/ObjectMacros.h"

class FDemoNaniteBuilder
{
public:
    static void BuildAndExport(UPCGNode* InNode, const TArray<FPCGPoint>& InPoints);
};

// DemoNaniteBuilder.cpp
#include "DemoNaniteBuilder.h"
#include "Elements/PCGNaniteAssemblyStaticMeshBuilder.h"

void FDemoNaniteBuilder::BuildAndExport(UPCGNode* InNode, const TArray<FPCGPoint>& InPoints)
{
    // 获取设置对象
    UPCGNaniteAssemblyStaticMeshBuilderSettings* Settings = Cast<UPCGNaniteAssemblyStaticMeshBuilderSettings>(InNode->DefaultSettings);
    if (!Settings)
    {
        Settings = NewObject<UPCGNaniteAssemblyStaticMeshBuilderSettings>();
        InNode->DefaultSettings = Settings;
    }

    // 配置属性
    Settings->MeshAttribute.SetAttributeName(TEXT("MeshRef")); // 点数据中的网格引用属性
    Settings->ExportParams.OutputPath = TEXT("/Game/Generated/Assembly/");
    Settings->bSynchronousLoad = true;

    // 输入数据
    FPCGDataCollection InputData;
    InputData.TaggedData.Add(FPCGTaggedData{ InPoints });

    // 手动执行节点（简化，实际需要在图管线中执行）
    TUniquePtr<FPCGContext> Context = MakeUnique<FPCGContext>(InNode, InputData, nullptr);
    Settings->GetElement()->Execute(Context.Get());
}
```

## 模块依赖

在你的模块 `Build.cs` 中需添加以下依赖：

| 模块 | 用途 |
|---|---|
| `PCG` | PCG 框架核心模块 |
| `NaniteAssemblyEditorUtils` | Nanite 装配体编辑器工具，提供装配体操作接口 |

其他常见依赖（如 `Core`, `Engine`, `Slate` 等）无需手动添加，插件已包含。

## 维护状态

### 近期更新

- 2025-09-23 `ab85c523` — [PCG] Small QoL for Nanite Assembly Builder  
- 2025-09-23 `17341006` — [PCG - Nanite Assemblies] Initial prototype of Nanite Assemblies builder  

### 维护评价

- **创建时间**：2025-09-23，距今不到 1 个月（极新）。  
- **版本**：0.1，标记为实验性。  
- **近期更新**：仅两次提交，均为初始原型构建和小改进。  
- **推荐使用**：适合预览 Nanite 装配体与 PCG 结合的可能性。但由于是实验性版本，API 可能不稳定，功能有限，不建议在正式项目中使用。若需稳定版本，建议等待后续迭代。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PCGInterops/PCGNaniteAssembliesInterop)  
- [官方 PCG 文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)