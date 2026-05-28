# Compute Framework

> Support for user authored GPU compute graphs

| 属性 | 值 |
|---|---|
| 中文名 | 计算图框架 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ComputeFramework` (Runtime), `ComputeFrameworkEditor` (Editor), `ComputeDataInterface` (Runtime), `EditableComputeGraph` (Runtime), `EditableComputeGraphEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-30 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ComputeFramework) | |

## 用途

ComputeFramework 是一个实验性框架，旨在让用户通过数据驱动的方式构建和执行 GPU 计算图。它解决了在运行时动态编排和执行复杂 GPU 计算任务的问题，而无需为每项任务编写和管理独立的 Compute Shader 及其绑定代码。其核心是一个图执行引擎，负责调度计算任务、管理资源依赖和处理 GPU 命令提交。

该插件通常作为其他需要 GPU 加速的系统（如程序化内容生成 (PCG) 或物理模拟）的底层支撑。

## 使用场景

-   **GPGPU 计算**：你需要在运行时执行通用 GPU 计算（例如物理模拟、粒子系统、图像处理），并希望通过图形化或数据化的方式定义计算流程，而不是编写底层的 `FRHIComputeCommandList` 调用。
-   **PCG 与程序化系统**：你正在使用 UE5 的程序化内容生成 (PCG) 框架，并希望将 GPU 计算集成到生成流程中，以提升大规模场景的生成效率。
-   **动态计算任务**：你的计算任务需要根据运行时数据（如游戏状态、玩家输入）动态改变其结构或参数，ComputeGraph 提供了这种灵活性。

## 蓝图用法

由于该插件实验性且文档缺失，蓝图 API 主要由 `EditableComputeGraph` 模块提供，用于在编辑器中创建和测试计算图资产。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `创建计算图对象` | 根据计算图资产创建一个可执行的运行时实例 | `UEditableComputeGraph` |
| `执行计算图` | 调度并执行计算图实例 | `UEditableComputeGraph` |
| `绑定数据接口` | 为计算图中的数据端口绑定输入/输出数据源（如纹理、缓冲区） | `UComputeDataInterface` |

## C++ 用法

### 头文件引入

```cpp
#include "ComputeFramework.h"
#include "EditableComputeGraph.h"
#include "ComputeDataInterface.h"
```

### 基本用法

1.  **创建和执行计算图**（概念性示例）：
    ```cpp
    // 假设已有一个 UEditableComputeGraph 资产 GraphAsset
    UEditableComputeGraph* GraphInstance = NewObject<UEditableComputeGraph>();
    GraphInstance->SetGraphAsset(GraphAsset);

    // 绑定输入数据
    // GraphInstance->BindDataInterface(TEXT("InputBuffer"), MyDataInterface);

    // 在渲染线程或合适的位置调度执行
    // GraphInstance->Execute();
    ```

### 进阶用法

-   **自定义数据接口**：继承 `UComputeDataInterface`，实现 `GetResources()` 和 `GetShaderParameters()` 等虚函数，以提供自定义的计算资源（如结构化缓冲区）给计算图节点。
-   **与渲染管线集成**：理解 `ComputeFramework` 模块如何与 `FRHICommandList` 交互，以便在自定义渲染通道中插入 GPU 计算任务。

## 模块依赖

从各模块的 Build.cs 分析，该插件具有特定的模块依赖关系。

| 模块 | 用途 |
|---|---|
| `Niagara` | `ComputeDataInterface` 模块依赖，可能用于共享某些 GPU 数据接口或粒子数据 |
| `NiagaraShader` | `ComputeFramework` 模块依赖，可能用于复用着色器编译或参数反射基础设施 |
| `ComputeDataInterface` | `EditableComputeGraph` 模块依赖，提供基础的数据接口定义 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `057cf5d7` | ComputeFramework: Fix data races on FComputeKernelShaderMap registries. | 修复内核着色器映射注册表中的数据竞争问题 |
| 2026-04-24 | `59214322` | [ComputeFramework + Optimus] Added Per-kernel output mask for data interfaces as in certain cases (S | 为数据接口添加了逐内核的输出掩码，优化特定情况下的数据传递 |
| 2026-04-21 | `f1e2ebe5` | [PCG][GPUPROFILER] Add support for user-provided stat objects to retrieve timing data from GPU execu | 增加对用户提供的统计对象的支持，用于从GPU执行中获取计时数据 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF |
| 2026-04-09 | `e0689004` | [shaders] remove explicit finalized/released flags from job struct, replace with extended/refactored | 重构着色器作业结构，移除显式标志，使用更完善的生命周期管理机制 |

### 维护评价

-   **创建时间**：约 3 年前（2022-08-30）。
-   **活跃程度**：**活跃维护**。最近一次更新在 2026 年 5 月，且近期更新包含功能性改进（输出掩码）和重要的 Bug 修复（数据竞争）。
-   **实验状态**：`IsBetaVersion = true`，`EnabledByDefault = false`，明确标记为实验性。API 和功能可能会发生破坏性变更。
-   **结论**：该插件是 Epic 内部使用和积极开发的一部分（近期提交涉及 PCG 和 Optimus）。对于愿意承担实验性风险的开发者，它是一个强大的工具，但不建议用于需要长期稳定的生产项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ComputeFramework)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ComputeFramework/Tests) (推测路径，需验证)