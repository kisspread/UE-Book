# IREEDriverRDG

> A runtime implementing the Neural Network Engine (NNE) API which is based on IREE, MLIR and LLVM and compiles neural networks directly to game code.

| 属性 | 值 |
|---|---|
| 中文名 | IREE RDG 驱动 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `IREEDriverRDG` (Runtime), `IREEUtils` (Runtime), `NNERuntimeIREE` (Runtime), `NNERuntimeIREEEditor` (Editor), `NNERuntimeIREEShader` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeIREE) | |

## 用途

IREEDriverRDG 是 NNERuntimeIREE 插件的一个核心运行时模块，它提供了一个基于 IREE (Intermediate Representation Execution Environment) 的 **HAL (Hardware Abstraction Layer) 设备驱动**，该驱动专门与 UE5 的渲染依赖图 (Render Dependency Graph, RDG) 深度集成。

**核心目标**是让 IREE 编译的神经网络模型推理任务能够无缝地嵌入到 UE 的渲染管线中。通过该驱动，模型的输入/输出张量可以直接引用 RDG 缓冲区（`FRDGBuffer`），从而避免昂贵的 CPU-GPU 数据拷贝，实现高效的 GPU 推理。它负责管理 IREE 设备、内存分配器、命令缓冲区、可执行文件（编译后的模型）等资源，并利用 UE 的图形基础设施（如 RHI 和 RDG）来执行。

## 使用场景

- **游戏内实时 AI 推理**：在游戏玩法循环中，需要高性能的神经网络推理，例如用于角色行为树、NPC 决策、或动态内容生成。
- **GPU 后处理效果**：将 ML 模型（如图像超分辨率、风格迁移）作为 UE 渲染后处理管线的一部分，通过 RDG 整合，无需单独的 Compute Shader 编写。
- **物理模拟**：利用神经网络加速的物理模拟（如流体、布料），将其集成到渲染流程中。
- **与现有渲染架构集成**：当你需要一个能与 UE 的 `FRDGBuilder` 和其他渲染模块（如 Niagara、材质系统）共享 GPU 资源的机器学习运行时。

## 蓝图用法

此模块**未暴露任何蓝图节点**。所有核心功能均通过 C++ 接口实现，不与蓝图直接交互。开发者需要在 C++ 层面使用本模块。

## C++ 用法

### 头文件引入

```cpp
#include "IREEDriverRDG.h"
```

### 基本用法

以下代码展示了如何创建一个 IREE RDG 设备驱动，并使用它来创建、提交和执行一个简单的计算任务。

**来源**: `Engine/Plugins/Experimental/NNERuntimeIREE/Source/IREEDriverRDG/Private/IREEDriverRDGDevice.cpp`

```cpp
#include "IREEDriverRDG.h"
#include "RenderGraphBuilder.h"
#include "RHIResources.h"

// 假设我们已经有一个编译好的 IREE 可执行文件（Executables 数据）
TMap<FString, TConstArrayView<uint8>> Executables;
// ... 初始化 Executables ...

// 1. 创建 IREE HAL 设备（基于 RDG）
iree_hal_device_t* Device = nullptr;
iree_status_t Status = UE::IREE::HAL::RDG::DeviceCreate(
    iree_string_view_t{"MyRDGDevice"},
    iree_allocator_host(),
    Executables,
    &Device
);
if (!iree_status_is_ok(Status))
{
    UE_LOG(LogTemp, Error, TEXT("Failed to create RDG device: %s"), *AnsiToFString(iree_status_code_string(iree_status_code(Status))));
    return;
}

// 2. 创建 IREE 命令缓冲区（用于提交图执行）
iree_hal_command_buffer_t* CommandBuffer = nullptr;
Status = UE::IREE::HAL::RDG::DirectCommandBufferCreate(
    iree_allocator_host(),
    iree_hal_device_allocator(Device),
    IREE_HAL_COMMAND_BUFFER_MODE_ONE_SHOT,
    IREE_HAL_COMMAND_CATEGORY_TRANSFER | IREE_HAL_COMMAND_CATEGORY_DISPATCH,
    IREE_HAL_QUEUE_AFFINITY_ANY,
    0, // BindingCapacity
    &CommandBuffer
);

// 3. 创建 IREE 可执行文件并绑定
// 使用 UE::IREE::HAL::RDG::ExecutableCreate(...)

// 4. 在命令缓冲区中编码图执行操作（由 IREE 生成的 IR 完成，此处省略）

// 5. 提交并执行（在 UE RDG 的上下文中）
// 通常在你的渲染线程函数中调用 IREE 的 iree_hal_device_submit_and_wait
```

### 进阶用法：包装 RDG 缓冲区

这是该模块的核心优势之一。你可以将一个已经存在于 RDG 中的 `FRDGBuffer` 包装为 IREE 的 `iree_hal_buffer_t`，无需拷贝数据即可在 IREE 内核中使用。

**来源**: `Engine/Plugins/Experimental/NNERuntimeIREE/Source/IREEDriverRDG/Private/IREEDriverRDGBuffer.cpp`

```cpp
#include "RenderGraphBuilder.h"
#include "RenderGraphResources.h"

// 假设你在某个渲染 pass 的上下文中
void MyRenderPass(FRDGBuilder& GraphBuilder)
{
    // 创建一个 RDG 缓冲区（模型输出结果将写入这里）
    FRDGBufferRef OutputBuffer = GraphBuilder.CreateBuffer(
        FRDGBufferDesc::CreateByteDesc(1024), TEXT("ModelOutput")
    );

    // 将 RDG 缓冲区包装为 IREE 硬件缓冲区
    iree_hal_buffer_t* IREEOutputBuffer = nullptr;
    iree_status_t Status = UE::IREE::HAL::RDG::BufferWrapRDG(
        iree_allocator_host(),
        DeviceAllocator, // 从何处获取？需要 DeviceAllocator
        IREE_HAL_MEMORY_TYPE_DEVICE_LOCAL,
        IREE_HAL_MEMORY_ACCESS_ALL,
        IREE_HAL_BUFFER_USAGE_DISPATCH_STORAGE,
        1024, // AllocationSize
        0,    // ByteOffset
        1024, // ByteLength
        &GraphBuilder,
        OutputBuffer,
        iree_hal_buffer_release_callback_null(),
        &IREEOutputBuffer
    );
    
    if (iree_status_is_ok(Status))
    {
        // 现在可以将 IREEOutputBuffer 传递给 IREE 的 dispatch 操作
        // ...
    }
}
```

## Demo 示例

以下是一个简化的示例，展示如何在一个自定义 Rendering Pass 中集成 IREE 推理，并将结果写入一个 RDG 缓冲区。

**IREERDGComputePass.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "RHI.h"
#include "RenderGraph.h"

class FIREEIREERDGComputePass
{
public:
    static void Execute(FRDGBuilder& GraphBuilder, FRDGBufferRef InputBuffer, FRDGBufferRef OutputBuffer, const TMap<FString, TConstArrayView<uint8>>& ModelExecutables);
};
```

**IREERDGComputePass.cpp**

```cpp
#include "IREERDGComputePass.h"
#include "IREEDriverRDG.h"
#include "Containers/Map.h"

void FIREEIREERDGComputePass::Execute(
    FRDGBuilder& GraphBuilder,
    FRDGBufferRef InputBuffer,
    FRDGBufferRef OutputBuffer,
    const TMap<FString, TConstArrayView<uint8>>& ModelExecutables)
{
    // 1. 创建 IREE 设备
    iree_hal_device_t* Device = nullptr;
    bool bDeviceCreated = false;
    {
        iree_status_t Status = UE::IREE::HAL::RDG::DeviceCreate(
            iree_string_view_t{"DemoModelDevice"},
            iree_allocator_host(),
            ModelExecutables,
            &Device
        );
        if (!iree_status_is_ok(Status)) { return; }
        bDeviceCreated = true;
    }

    // 2. 包装输入/输出缓冲区为 IREE 缓冲区
    iree_hal_buffer_t* IREEInputBuffer = nullptr;
    iree_hal_buffer_t* IREEOutputBuffer = nullptr;
    if (bDeviceCreated)
    {
        iree_hal_allocator_t* DeviceAllocator = iree_hal_device_allocator(Device);
        
        // 从 DeviceAllocator 获取 GraphBuilder (需要提前设置)
        // UE::IREE::HAL::RDG::DeviceAllocatorSetGraphBuilder(DeviceAllocator, GraphBuilder);
        
        // 包装输入
        UE::IREE::HAL::RDG::BufferWrapRDG(
            iree_allocator_host(),
            DeviceAllocator,
            IREE_HAL_MEMORY_TYPE_DEVICE_LOCAL,
            IREE_HAL_MEMORY_ACCESS_READ,
            IREE_HAL_BUFFER_USAGE_DISPATCH_STORAGE,
            InputBuffer->Desc.Size,
            0,
            InputBuffer->Desc.Size,
            &GraphBuilder,
            InputBuffer,
            iree_hal_buffer_release_callback_null(),
            &IREEInputBuffer
        );

        // 包装输出
        UE::IREE::HAL::RDG::BufferWrapRDG(
            iree_allocator_host(),
            DeviceAllocator,
            IREE_HAL_MEMORY_TYPE_DEVICE_LOCAL,
            IREE_HAL_MEMORY_ACCESS_WRITE,
            IREE_HAL_BUFFER_USAGE_DISPATCH_STORAGE,
            OutputBuffer->Desc.Size,
            0,
            OutputBuffer->Desc.Size,
            &GraphBuilder,
            OutputBuffer,
            iree_hal_buffer_release_callback_null(),
            &IREEOutputBuffer
        );
    }

    // 3. 编码并执行 (简化，省略了 dispatch 命令)
    // 实际上需要从 ModelExecutables 中获取 dispatch 信息
    // 并调用 iree_hal_command_buffer_dispatch(...)

    // 4. 清理 (在渲染线程执行完毕时)
    // iree_hal_device_release(Device);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `IREE` | 提供 IREE 核心 C API 库 |
| `RenderGraph` | 提供 UE 的渲染依赖图 (RDG) 框架 |
| `RHI` |提供底层硬件接口抽象 |
| `NNERuntimeIREEShader` | 提供着色器元数据分配和管理工具，用于从编译后的模型提取着色器绑定信息 |
| `NNEMlirTools` | 提供 MLIR 相关工具，用于编译模型时分析 SPIR-V 着色器参数 |

## 维护状态

### 近期更新

- 2025-09-26   e0d52775   [NNE] NNERuntime IREE support of path with spaces on RelTest build on Mac for RDG.
- 2025-09-24   ca784fe6   [NNE] NNERuntimeIREERdg always prefer wave32 to be consistent with used GPU profiles from IREE.
- 2025-09-24   1dc2a8b6   [NNE] NNERuntimeIREE fix typo in Linux build script.
- 2025-09-24   08183aae   [NNE] NNERuntime IREE support of path with spaces on RelTest build on Mac.
- 2025-09-12   f4a4fff3   [NNE] NNERuntimeIREE fix onnx importer dependencies not staged for Engine installed build.

### 维护评价

该模块自 2025 年 9 月创建以来处于 **活跃维护** 状态。提交记录显示开发团队正积极修复跨平台问题（尤其是 Mac 和 Linux 路径处理）并优化 GPU 配置（如强制使用 wave32 以提高与 IREE GPU 配置文件的兼容性）。当前没有弃用或废弃迹象，但应注意其 **实验性** 标签 (`IsExperimentalVersion=true`)，API 和功能可能在未来的 UE 版本中发生重大变化。对于需要前沿 ML 推理集成的项目，可以考虑使用，但需做好适配未来版本的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeIREE)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeIREE/Tests)