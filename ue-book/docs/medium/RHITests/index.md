# RHI Tests

> 

| 属性 | 值 |
|---|---|
| 分类 | Testing |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Shader 文件） |
| 模块 | `RHITests` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/RHITests) | |

## 用途

RHI Tests 是 Epic Games 官方的 RHI（Rendering Hardware Interface）单元测试插件。它不是给游戏项目使用的功能插件，而是用来**验证各图形后端（D3D11、D3D12、Vulkan、Metal）的 RHI 实现是否正确**的测试套件。

这个插件解决的核心问题是：UE5 的 RHI 是一个跨平台抽象层，覆盖了数十种像素格式、多种资源类型和各种 GPU 操作。每个图形后端都需要正确实现这些接口，而 RHI Tests 提供了系统化的验证手段，确保 Clear、Copy、Readback、Draw、UAV 绑定等底层操作在所有后端上行为一致。

插件默认关闭（`EnabledByDefault: false`），因为它是纯测试工具，不应在生产环境中加载。

## 使用场景

- 你是 RHI 后端开发者，正在实现或修改某个图形 API 的适配层 → 使用 RHITests 验证正确性
- 你在移植 UE5 到新平台，需要验证 RHI 层 → 运行 RHITests 作为回归测试
- 你在排查渲染 bug，怀疑是 RHI 层的问题 → 运行相关测试用例确认
- 你在做引擎级别的 CI/CD，需要自动化渲染正确性检查 → 集成 RHITests 到测试流程

## 蓝图用法

此插件不暴露任何蓝图接口。它是纯 C++ 测试套件，通过 `FRHITestsModule::RunAllTests()` 或自动化测试框架运行。

## C++ 用法

### 运行测试

RHI Tests 提供两种运行方式：

#### 方式一：命令行参数

通过 `-rhiunittest` 命令行参数触发，所有测试在渲染线程上同步执行：

```cpp
// 启动 UE 时添加参数
// UnrealEditor-Cmd.exe -rhiunittest
```

#### 方式二：自动化测试框架

通过 UE 自动化测试系统运行，测试注册在 `Rendering.RHI` 路径下：

```cpp
// 在自动化测试面板中搜索 "Rendering.RHI" 可找到所有测试用例
// 测试类: FAutomationRHITest (定义在 RHITests.spec.cpp)
```

### 测试结构

所有测试都遵循统一模式：在渲染线程上执行 RHI 操作，然后验证结果：

```cpp
// 基本模式（来自 RHITestsCommon.h）
bool RunOnRenderThreadSynchronous(TFunctionRef<bool(FRHICommandListImmediate&)> TestFunc);

// 使用方式
bool bResult = RunOnRenderThreadSynchronous(
    [](FRHICommandListImmediate& RHICmdList) -> bool
    {
        // 在渲染线程上执行 RHI 操作
        // 返回 true 表示测试通过
    }
);
```

### 各测试类详解

#### FRHIBufferTests — Buffer 操作测试

验证 Buffer 的创建、UAV 清除等操作。

```cpp
#include "RHIBufferTests.h"

// 测试 ClearUAVUint / ClearUAVFloat 对各种 Buffer 类型的效果
// 覆盖格式: R8_UINT, R8G8B8A8_UINT, R16_UINT, R32_UINT, R32_FLOAT 等
// Buffer 类型: VertexBuffer, StructuredBuffer, ByteAddressBuffer (Raw)
// 验证方式: Readback buffer 内容并与预期值逐字节比较
FRHIBufferTests::Test_RHIClearUAVUint_VertexBuffer(RHICmdList);
FRHIBufferTests::Test_RHIClearUAVFloat_VertexBuffer(RHICmdList);
FRHIBufferTests::Test_RHIClearUAVUint_StructuredBuffer(RHICmdList);
FRHIBufferTests::Test_RHIClearUAVFloat_StructuredBuffer(RHICmdList);

// 测试 Buffer 创建的多种方式
// 1. ZeroData — 全零初始化
// 2. Initializer — 通过 TRHIBufferInitializer 写入数据
// 3. ResourceArray — 通过 FResourceArrayUploadArrayView 上传
FRHIBufferTests::Test_RHICreateBuffer(RHICmdList);
FRHIBufferTests::Test_RHICreateBuffer_Parallel(RHICmdList);
```

#### FRHITextureTests — 纹理操作测试

验证纹理的创建、格式、UAV 清除、拷贝、更新等操作。

```cpp
#include "RHITextureTests.h"

// 测试所有 RHI 像素格式（RenderTarget、DepthStencil）
FRHITextureTests::Test_RHIFormats(RHICmdList);

// 测试 ClearUAV 对 Texture2D / Texture3D 的效果
// 覆盖: 不同尺寸（方形/矩形/奇数尺寸）、不同 Mip 数、不同 Slice 数
// 格式: PF_FloatRGBA, PF_R32_UINT
FRHITextureTests::Test_RHIClearUAV_Texture2D(RHICmdList);
FRHITextureTests::Test_RHIClearUAV_Texture3D(RHICmdList);

// 测试纹理拷贝和更新
FRHITextureTests::Test_RHICopyTexture(RHICmdList);
FRHITextureTests::Test_UpdateTexture(RHICmdList);
FRHITextureTests::Test_MultipleLockTexture2D(RHICmdList);
```

#### FRHIDrawTests — 绘制测试

验证 BaseVertex / BaseInstance / Indirect Draw 等绘制功能。

```cpp
#include "RHIDrawTests.h"

// 直接绘制：验证 BaseVertex 和 BaseInstance 偏移
FRHIDrawTests::Test_DrawBaseVertexAndInstanceDirect(RHICmdList);

// 间接绘制：通过 IndirectBuffer 传递绘制参数
FRHIDrawTests::Test_DrawBaseVertexAndInstanceIndirect(RHICmdList);

// 多次间接绘制：一次 DrawIndirect 调用执行多次绘制
FRHIDrawTests::Test_MultiDrawIndirect(RHICmdList);
```

#### FRHIClearTextureTests — RenderTarget 清除测试

验证 `RHICmdList.ClearTexture` 对 RenderTarget 的清除操作。

```cpp
#include "RHIClearTextureTests.h"

FRHIClearTextureTests::Test_ClearTexture(RHICmdList);
```

#### FRHIReadbackTests — GPU Readback 测试

验证从 GPU 读回数据到 CPU 的正确性。

```cpp
#include "RHIReadbackTests.h"

// Buffer Readback: 创建 Buffer → 填充数据 → Readback → 验证
FRHIReadbackTests::Test_BufferReadback(RHICmdList);

// Texture Readback: 创建 Texture → 填充数据 → Readback → 验证
FRHIReadbackTests::Test_TextureReadback(RHICmdList);
```

#### FRHIReservedResourceTests — Reserved Resource 测试

验证 Reserved（稀疏）资源的创建、Commit 和 Decommit。

```cpp
#include "RHIReservedResourceTests.h"

// Reserved Texture: 创建不分配物理内存的纹理
FRHIReservedResourceTests::Test_ReservedResource_CreateTexture(RHICmdList);
FRHIReservedResourceTests::Test_ReservedResource_CreateTextureWithMips(RHICmdList);
FRHIReservedResourceTests::Test_ReservedResource_CreateVolumeTexture(RHICmdList);

// Reserved Buffer: 创建 + Commit/Decommit 虚拟内存页
FRHIReservedResourceTests::Test_ReservedResource_CreateBuffer(RHICmdList);
FRHIReservedResourceTests::Test_ReservedResource_CommitBuffer(RHICmdList);
FRHIReservedResourceTests::Test_ReservedResource_DecommitBuffer(RHICmdList);
```

#### FRHIGraphicsUAVTests — 图形管线 UAV 绑定测试

验证 UAV 绑定到非 Compute Shader（Pixel/Vertex Shader）。

```cpp
#include "RHIGraphicsUAVTests.h"

FRHIGraphicsUAVTests::Test_GraphicsUAV_PixelShader(RHICmdList);
FRHIGraphicsUAVTests::Test_GraphicsUAV_VertexShader(RHICmdList);
```

#### FRHIAllocatorTests — 分配器测试

验证 Buffer Lock 操作的 16 字节对齐。

```cpp
#include "RHIAllocatorTests.h"

FRHIAllocatorTests::Test_LockBuffer16ByteAlignment(RHICmdList);
```

#### RHIBindlessTests — Bindless 资源测试

验证 RHI Resource Collection（Bindless 资源管理）。

```cpp
#include "RHIBindlessTests.h"

RHIBindlessTests::Test_ResourceCollection(RHICmdList);
```

## Demo 示例

以下是一个最小化的自定义 RHI 测试示例，展示如何使用 RHITests 的模式编写自己的 RHI 验证代码：

```cpp
// MyRHITest.h
#pragma once
#include "CoreMinimal.h"
#include "RHITestsCommon.h"  // 来自 RHITests 插件

class FMyRHITest
{
public:
    static bool Test_CreateAndVerifyBuffer(FRHICommandListImmediate& RHICmdList);
};
```

```cpp
// MyRHITest.cpp
#include "MyRHITest.h"

bool FMyRHITest::Test_CreateAndVerifyBuffer(FRHICommandListImmediate& RHICmdList)
{
    const uint32 BufferSize = 1024;
    const TCHAR* TestName = TEXT("MyBufferTest");

    // 创建一个带初始数据的 Buffer
    TArray<uint8> TestData;
    TestData.SetNumUninitialized(BufferSize);
    for (uint32 i = 0; i < BufferSize; ++i)
    {
        TestData[i] = static_cast<uint8>(i & 0xFF);
    }

    FResourceArrayUploadArrayView UploadView(TestData);
    const FRHIBufferCreateDesc CreateDesc =
        FRHIBufferCreateDesc::Create(TestName, BufferSize, 0, EBufferUsageFlags::VertexBuffer)
        .AddUsage(EBufferUsageFlags::SourceCopy)
        .SetInitActionResourceArray(&UploadView)
        .SetInitialState(ERHIAccess::CopySrc);

    FBufferRHIRef Buffer = RHICmdList.CreateBuffer(CreateDesc);
    if (!Buffer)
    {
        return false;
    }

    // 使用 RHITests 提供的验证工具
    return FRHIBufferTests::VerifyBufferContents(
        TestName, RHICmdList, Buffer.GetReference(),
        [&TestData](int32 BufferIndex, void* Ptr, uint32 NumBytes) -> bool
        {
            return FMemory::Memcmp(Ptr, TestData.GetData(), NumBytes) == 0;
        });
}
```

## 模块依赖

从 `RHITests.Build.cs` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、容器、日志 |
| `CoreUObject` | 对象系统 |
| `Engine` | 引擎核心（出现两次，Build.cs 中的冗余） |
| `RHI` | RHI 抽象层 — 本插件测试的核心目标 |
| `RenderCore` | 渲染核心：渲染线程、Command List |
| `Projects` | 插件管理（私有依赖，用于获取插件路径） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-08-25 | `71c9eadb` | 修复 Bindless 禁用时 RHI 单元测试的问题 |
| 2025-08-21 | `02fd6e5e` | RHIResourceCollection 更新 + 新增 Bindless RHI 单元测试 |
| 2025-08-21 | `735460cf` | RHI 对齐测试的小幅调整 |

### 维护评价

- **创建时间**：2020 年 9 月，约 6 年历史
- **活跃度**：近期（2025 年 8 月）有实质性更新，新增了 Bindless 资源测试
- **维护状态**：**活跃维护中** — 作为引擎核心渲染层的测试套件，随 RHI 层演进持续更新
- **测试覆盖**：覆盖了 Buffer、Texture、Draw、Readback、Reserved Resource、UAV、Allocator、Bindless 等主要 RHI 功能
- **推荐**：如果你在开发 RHI 后端或排查底层渲染问题，这是不可或缺的工具

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/RHITests)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Tests/RHITests/Source/RHITests/Private/RHITests.spec.cpp)
