# Mesh Resizing

> Mesh Resizing

| 属性 | 值 |
|---|---|
| 中文名 | 网格调整 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `MeshResizingCore` (Runtime), `MeshResizingEditorTools` (Runtime), `MeshResizingEngine` (Runtime), `MeshResizingDataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing) | |

## 用途

Mesh Resizing 插件旨在为数字角色（Digital Human）制作流程提供网格变形和重拓扑工具。其核心目的是优化角色衣物的网格拓扑，使其在满足高质量的衣料模拟（如 Chaos Cloth）的同时，拥有较少的顶点数量，从而提升运行时性能。它通过一种“调整”过程，将一个高精度的网格（如从扫描或雕刻软件获得）适配到一个用于模拟和实时渲染的简化网格上，确保视觉保真度与性能之间的平衡。

## 使用场景

- 你在创建数字角色，并需要为其高精度的服装资产准备一个可用于实时物理模拟（衣料）的低精度版本。
- 你的工作流程依赖于将高模细节（如雕刻褶皱）“烘焙”或适配到为游戏优化的低模上。
- 你需要使用 Dataflow 节点系统来程序化或批处理网格调整任务。

## 蓝图用法

由于该插件默认禁用且处于实验阶段，其蓝图 API 主要集中在 `MeshResizingEditorTools` 模块中，为编辑器工具提供支持。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ResizeMesh` | 对传入的网格资产执行调整操作 | `UMeshResizingBPLibrary` |

### 使用示例（蓝图描述）

1.  在蓝图编辑器中，调用 `ResizeMesh` 节点。
2.  将源网格（高模）和目标网格（用于调整的基础低模）资产引用连接到输入引脚。
3.  配置调整参数（如迭代次数、约束强度等）。
4.  执行节点，输出调整后的网格数据或直接保存为新资产。

## C++ 用法

该插件的核心调整算法位于 `MeshResizingCore` 和 `MeshResizingEngine` 模块中。

### 头文件引入

```cpp
#include "MeshResizingEngine/MeshResizingEngine.h" // 用于引擎级调整功能
#include "MeshResizingCore/MeshResizing.h"        // 用于核心数据结构与算法
```

### 基本用法

以下为调用网格调整功能的简化示例，需在编辑器环境下运行。

```cpp
// 假设已经获取了 UStaticMesh* SourceMesh 和 UStaticMesh* TargetMesh
#include "MeshResizingEngine/MeshResizingSubsystem.h"

// 通过子系统执行调整
if (UMeshResizingSubsystem* MeshResizingSubsystem = GEditor->GetEditorSubsystem<UMeshResizingSubsystem>())
{
    FMeshResizingParameters Params;
    // 设置参数...
    
    FMeshResizingResult Result;
    MeshResizingSubsystem->ResizeMesh(SourceMesh, TargetMesh, Params, Result);
    
    if (Result.bSuccess)
    {
        // 使用调整后的网格数据 Result.ResizedMesh
    }
}
```

*（注意：以上为基于模块功能和UE插件模式的推断代码，具体API请参考实际头文件。）*

## Demo 示例

一个最小化的 C++ 编辑器工具示例，演示如何调用调整功能。

**MyMeshResizingTool.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "EditorUtilityWidget.h"
#include "MyMeshResizingTool.generated.h"

UCLASS()
class UMyMeshResizingTool : public UEditorUtilityWidget
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Mesh Resizing")
    UStaticMesh* SourceHighResMesh;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Mesh Resizing")
    UStaticMesh* TargetLowResMesh;

    UFUNCTION(BlueprintCallable, Category = "Mesh Resizing")
    void ExecuteResize();
};
```

**MyMeshResizingTool.cpp**
```cpp
#include "MyMeshResizingTool.h"
#include "MeshResizingEngine/MeshResizingSubsystem.h"

void UMyMeshResizingTool::ExecuteResize()
{
    if (!SourceHighResMesh || !TargetLowResMesh)
    {
        UE_LOG(LogTemp, Warning, TEXT("源或目标网格未设置。"));
        return;
    }

    UMeshResizingSubsystem* Subsystem = GEditor->GetEditorSubsystem<UMeshResizingSubsystem>();
    if (Subsystem)
    {
        FMeshResizingParameters Parameters; // 使用默认参数
        FMeshResizingResult Result;
        
        if (Subsystem->ResizeMesh(SourceHighResMesh, TargetLowResMesh, Parameters, Result) && Result.bSuccess)
        {
            UE_LOG(LogTemp, Log, TEXT("网格调整成功！"));
            // 可在此处处理或保存 Result.ResizedMesh
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("网格调整失败。"));
        }
    }
}
```

## 模块依赖

要使用 MeshResizing 功能，你的模块通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `MeshResizingCore` | 核心数据结构和算法库 |
| `MeshResizingEngine` | 提供子系统、引擎服务和主要调整流程 |

此外，根据你的具体用途，可能还需要依赖：
- `MeshResizingEditorTools`：如果需要使用编辑器UI工具或蓝图API。
- `MeshResizingDataflowNodes`：如果需要在 Dataflow 图表中使用调整节点。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点的警告。 |
| 2026-05-12 | `a7802337` | Dataflow: | Dataflow 相关更新。 |
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 在即将到来的头文件清理前添加必要的包含。 |
| 2026-01-30 | `7b60de76` | Dataflow : add support to lasso to the paint tool by leveraging the newly added feature in the mesh | Dataflow：为涂抹工具添加套索支持，利用网格中新添加的功能。 |
| 2025-12-19 | `f86e1e20` | Dataflow : update a lot of nodes to use the new rendering system | Dataflow：更新大量节点以使用新的渲染系统。 |

### 维护评价

- **创建时间**：约 1 年（2024年12月）。
- **更新频率**：从提交记录看，在创建后的约半年内有持续的功能性更新和改进，尤其集中在 Dataflow 节点系统上。最近的提交（2026年5月）是编译修复，表明仍处于活跃开发中。
- **状态**：**实验性活跃维护**。插件标记为 `IsExperimentalVersion: true` 且默认禁用，表明其 API 和功能可能在未来发生重大变化。但近期更新表明 Epic 正在积极完善它，特别是其 Dataflow 集成部分。
- **推荐度**：目前**仅推荐**给需要研究前沿网格处理技术、或愿意接受API变动风险的开发者和艺术家，用于原型开发和评估。不建议用于需要长期稳定的核心生产管线。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing)
- 官方文档：暂无
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing/Tests)