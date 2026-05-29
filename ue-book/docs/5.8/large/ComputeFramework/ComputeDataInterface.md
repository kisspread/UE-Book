# Compute Framework

> Support for user authored GPU compute graphs

| 属性 | 值 |
|---|---|
| 中文名 | 计算框架 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ComputeFramework` (Runtime), `ComputeFrameworkEditor` (Editor), `ComputeDataInterface` (Runtime), `EditableComputeGraph` (Runtime), `EditableComputeGraphEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-30 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ComputeFramework) | |

## 用途

ComputeFramework 提供了一套**用户自定义 GPU 计算图**的框架，让开发者无需直接编写复杂的 RDG（Render Dependency Graph）代码，就能构建 GPU 计算管线。

该框架的核心设计理念是**数据接口（Data Interface）模式**：
- **ComputeDataInterface**：定义数据如何流入/流出 GPU 计算内核（如 Buffer、纹理、调度参数等）
- **ComputeDataProvider**：负责在运行时为数据接口提供实际的 GPU 资源
- **ComputeGraph**：将多个计算内核连接成一个可执行的有向图

与直接使用 RDG 或 RHI 相比，该框架抽象了资源生命周期管理、着色器参数绑定、调度调度等繁琐细节，特别适合需要构建可重用、可视化编辑的 GPU 计算流程的场景（如 PCG、Optimus 动画系统等）。

## 使用场景

- 你需要构建自定义的 GPU 计算管线（如粒子模拟、图像处理、几何体生成）→ 用 ComputeFramework
- 你正在开发一个可视化节点编辑器来编辑 GPU 计算图 → 用 EditableComputeGraph
- 你想在 PCG 或 Optimus 中扩展自定义数据接口 → 用 ComputeDataInterface
- 你需要简单的 Buffer 读写操作交给 GPU → 用内置的 Buffer 数据接口
- 你需要控制计算调度的线程数 → 用内置的 Dispatch 数据接口

## 蓝图用法

ComputeFramework 的数据提供器（DataProvider）设计为 Blueprintable，允许蓝图层配置和驱动 GPU 计算。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ElementCount` | 设置 Buffer 元素数量 | `UBufferDataProvider` |
| `bClearBeforeUse` | 是否在使用前清空 Buffer | `UBufferDataProvider` |
| `ValueType` | 设置 Buffer 值类型（Int/Float 等） | `UBufferDataProvider` |
| `ThreadCount` | 设置 Dispatch 线程数（X, Y, Z） | `UDispatchDataProvider` |

### 使用示例（蓝图描述）

1. 创建一个 `UBufferDataProvider` 资产，设置 `ValueType` 为 `Float4`，`ElementCount` 为 1024
2. 在计算图中将 Buffer 数据接口连接到你的计算内核节点
3. 配置 `bClearBeforeUse = true` 确保每次执行前缓冲区被清零
4. 通过 `UDispatchDataProvider` 设置 `ThreadCount` 为 `FIntVector(256, 1, 1)` 控制调度维度

## C++ 用法

### 头文件引入

```cpp
#include "ComputeDataInterfaceBuffer.h"
#include "ComputeDataInterfaceDispatch.h"
```

### 基本用法 — 自定义 Buffer 数据接口

创建一个自定义 Buffer 数据提供器，配置 GPU 缓冲区：

```cpp
// 来源: Source/ComputeDataInterface/Internal/ComputeFramework/ComputeDataInterfaceBuffer.h

// 创建 Buffer 数据接口并配置
UComputeDataInterfaceBuffer* BufferDI = NewObject<UComputeDataInterfaceBuffer>();
BufferDI->ValueType = EComputeDataInterfaceBufferType::Float4;
BufferDI->bAllowReadWrite = true;

// 创建对应的数据提供器
UBufferDataProvider* BufferProvider = NewObject<UBufferDataProvider>();
BufferProvider->ValueType = EComputeDataInterfaceBufferType::Float4;
BufferProvider->ElementCount = 1024;
BufferProvider->bClearBeforeUse = true;
```

### 基本用法 — Dispatch 数据接口

控制计算着色器的调度参数：

```cpp
// 来源: Source/ComputeDataInterface/Internal/ComputeFramework/ComputeDataInterfaceDispatch.h

// 创建 Dispatch 数据接口
UComputeDataInterfaceDispatch* DispatchDI = NewObject<UComputeDataInterfaceDispatch>();

// 创建数据提供器并设置线程数
UDispatchDataProvider* DispatchProvider = NewObject<UDispatchDataProvider>();
DispatchProvider->ThreadCount = FIntVector(256, 1, 1); // 一维调度，256 个线程
```

### 进阶用法 — 自定义数据接口

继承 `UComputeDataInterface` 实现自定义数据接口：

```cpp
// 自定义数据接口类
UCLASS(MinimalAPI, Category = ComputeFramework)
class UMyComputeDataInterface : public UComputeDataInterface
{
    GENERATED_BODY()

    // 返回唯一的类名标识符
    TCHAR const* GetClassName() const override { return TEXT("MyInterface"); }

    // 声明支持的 HLSL 输入函数
    void GetSupportedInputs(TArray<FShaderFunctionDefinition>& OutFunctions) const override;

    // 声明支持的 HLSL 输出函数
    void GetSupportedOutputs(TArray<FShaderFunctionDefinition>& OutFunctions) const override;

    // 定义着色器参数结构
    void GetShaderParameters(
        TCHAR const* UID,
        FShaderParametersMetadataBuilder& InOutBuilder,
        FShaderParametersMetadataAllocations& InOutAllocations) const override;

    // 指定 HLSL 模板路径
    const TCHAR* GetShaderVirtualPath() const override;

    // 生成 HLSL 代码
    void GetHLSL(FString& OutHLSL, FString const& InDataInterfaceName) const override;

    // 创建对应的数据提供器
    UComputeDataProvider* CreateDataProvider() const override;
};

// 自定义数据提供器
UCLASS(MinimalAPI, Blueprintable, Category = ComputeFramework)
class UMyDataProvider : public UComputeDataProvider
{
    GENERATED_BODY()

    void Initialize(int32 InDataInterfaceIndex, UComputeDataInterface const* InDataInterface,
                    UObject* InBinding, uint64 InInputMask, uint64 InOutputMask) override;
    FComputeDataProviderRenderProxy* GetRenderProxy() override;

public:
    // 蓝图可编辑的自定义参数
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = DataInterface)
    int32 MyCustomValue = 0;
};
```

## Demo 示例

一个完整的自定义 Buffer 数据接口示例：

```cpp
// MyBufferInterface.h
#pragma once

#include "ComputeDataInterface.h"
#include "ComputeDataProvider.h"
#include "MyBufferInterface.generated.h"

UCLASS(MinimalAPI, Blueprintable, Category = ComputeFramework)
class UMyBufferDataProvider : public UComputeDataProvider
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = Buffer)
    int32 NumElements = 256;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = Buffer)
    bool bClearOnStart = true;
};
```

```cpp
// MyBufferInterface.cpp
#include "MyBufferInterface.h"

void UMyBufferDataProvider::Initialize(
    int32 InDataInterfaceIndex,
    UComputeDataInterface const* InDataInterface,
    UObject* InBinding,
    uint64 InInputMask,
    uint64 InOutputMask)
{
    Super::Initialize(InDataInterfaceIndex, InDataInterface, InBinding, InInputMask, InOutputMask);
    // 在此初始化缓冲区配置
}

FComputeDataProviderRenderProxy* UMyBufferDataProvider::GetRenderProxy()
{
    // 创建渲染线程代理，负责实际的 GPU 资源分配
    // 返回代理对象（需实现 FComputeDataProviderRenderProxy 子类）
    return nullptr;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RenderCore` | RDG 构建、着色器参数元数据 |
| `RHI` | RHI 缓冲区、SRV/UAV 创建 |
| `ShaderCore` | 着色器函数定义、HLSL 代码生成 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `057cf5d7` | ComputeFramework: Fix data races on FComputeKernelShaderMap registries. | 修复着色器映射注册表的多线程竞争条件 |
| 2026-04-24 | `59214322` | [ComputeFramework + Optimus] Added Per-kernel output mask for data interfaces as in certain cases (S... | 为数据接口添加内核级别输出掩码，优化特定场景 |
| 2026-04-21 | `f1e2ebe5` | [PCG][GPUPROFILER] Add support for user-provided stat objects to retrieve timing data from GPU execu... | 支持用户自定义统计对象以获取 GPU 执行时间数据 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志系统迁移到 UE_LOGF 宏 |
| 2026-04-09 | `e0689004` | [shaders] remove explicit finalized/released flags from job struct, replace with extended/refactored... | 重构着色器作业结构体，简化状态管理 |

### 维护评价

**活跃维护中**。该插件从 2022 年从 Experimental 迁移而来，至今约 4 年。最近 1 个月内有多次实质性更新，包括：
- 线程安全修复（数据竞争问题）
- 与 Optimus 和 PCG 子系统的集成改进
- GPU 性能分析支持
- 代码现代化（日志宏迁移）

该插件虽然标记为 `IsBetaVersion=true` 且 `EnabledByDefault=false`，但持续有 Epic 工程师维护，且与 PCG、Optimus 等重要系统深度集成。**适合在需要自定义 GPU 计算管线时使用，但需注意其 beta 状态，API 可能在未来版本中变化**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ComputeFramework)
- 测试用例：Plugin 内未发现独立测试文件，功能验证主要通过 PCG 和 Optimus 集成测试