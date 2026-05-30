# RHI Tests

> （Description 字段为空）

| 属性 | 值 |
|---|---|
| 中文名 | RHI 单元测试 |
| 分类 | Testing |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `RHITests` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/RHITests) | |

## 用途

该插件并非面向游戏开发者的功能插件，而是一套**针对 Unreal Engine 底层渲染硬件接口 (RHI) 的自动化单元测试集合**。其核心目的是在不同的图形 API (D3D12, Vulkan 等) 和平台下，验证 RHI 功能的正确性、稳定性和一致性。

**为什么存在？**
RHI 是引擎与 GPU 硬件交互的抽象层，极其关键且复杂。任何 RHI 代码的改动（如新功能、bug修复、驱动适配）都可能引入难以察觉的回归错误。此插件通过提供全面的测试套件，确保 RHI 层的核心操作（如缓冲区创建、纹理更新、UAV 清除、着色器绑定等）在各种场景和参数组合下都能按预期工作。它是 Epic Games 内部开发和持续集成 (CI) 流程的重要组成部分。

## 使用场景

- 你正在**开发或修改 UE5 的 RHI 抽象层或底层渲染代码**，需要确保你的改动没有破坏已有功能。
- 你是一名**引擎开发者**，在集成新的图形 API 或驱动后，需要运行一套标准测试来验证基础功能的正确性。
- 你正在**学习或调试 RHI**，可以通过运行这些测试用例来理解特定 RHI 函数（如 `FRHICommandListImmediate::ClearUAVUint`）的预期行为和边界情况。
- 你运行了自定义的渲染特性，怀疑 RHI 层存在 bug，可以运行相关测试用例来排查问题。

## 蓝图用法

此插件主要提供 C++ 测试类，并不暴露蓝图节点。其测试通常通过引擎的自动化测试框架或特定的控制台命令（如 `RHITest`）来运行。

## C++ 用法

插件内的测试类（如 `FRHIBufferTests`, `FRHITextureTests`）包含大量静态公共方法，每个方法对应一个具体的 RHI 功能测试。这些测试设计为在渲染线程上同步执行。

### 头文件引入

```cpp
#include "RHIBufferTests.h"
#include "RHITextureTests.h"
#include "RHITestsCommon.h" // 包含 RUN_TEST 宏等工具
```

### 基本用法

以下示例展示了如何运行一个简单的缓冲区创建测试。测试逻辑已封装在插件提供的静态函数中。

```cpp
// 假设在渲染线程的某个上下文中，已有 FRHICommandListImmediate& RHICmdList
// 来源：Source/RHITests/Public/RHIBufferTests.h 中 Test_RHIClearUAVUint_VertexBuffer 等函数

// 运行针对顶点缓冲区的 UAV 整数清除测试
bool bTestPassed = FRHIBufferTests::Test_RHIClearUAVUint_VertexBuffer(RHICmdList);

// 运行缓冲区创建测试（包括不同大小）
bool bCreateTestPassed = FRHIBufferTests::Test_RHICreateBuffer(RHICmdList);

// 使用 RUN_TEST 宏（定义在 RHITestsCommon.h），它会根据环境变量决定是否跳过特定测试
bool bResult = true;
RUN_TEST(FRHIBufferTests::Test_RHIClearUAVUint_StructuredBuffer(RHICmdList));
```

### 进阶用法

测试函数通常接受 `FRHICommandListImmediate&`，并组合多个底层 RHI 操作（创建资源、创建视图、状态转换、执行清除/更新、读回验证）来完成一个完整的验证流程。例如，`RunTest_UAVClear_Buffer` 模板函数演示了：
1. 创建带 `UAV` 和 `SourceCopy` 标志的缓冲区。
2. 创建全资源 UAV 和带偏移的 UAV。
3. 依次执行“清除到零”、“清除到指定值”、“清除带偏移 UAV 到零”操作。
4. 在每次操作后，通过 `VerifyBufferContents` 将 GPU 数据读回 CPU 并与预期值比对。
5. 验证不同像素格式（`PF_R8_UINT`, `PF_R32G32B32A32_UINT` 等）、带状缓冲区 (`BUF_StructuredBuffer`, `BUF_ByteAddressBuffer`) 以及原始/类型化视图下的清除行为。

## Demo 示例

以下是一个最小化的测试用例结构，展示了如何编写一个简单的 RHI 资源测试：

**RHIMyTest.h**
```cpp
#pragma once

#include "RHITestsCommon.h"

class FRHIMyTest
{
public:
    // 测试创建一个简单的 2D 纹理并读取其内容
    static bool Test_CreateAndVerifyTexture2D(FRHICommandListImmediate& RHICmdList)
    {
        const uint32 Width = 4;
        const uint32 Height = 4;
        const EPixelFormat Format = PF_R8G8B8A8_UINT;
        const TCHAR* TestName = TEXT("Test_CreateAndVerifyTexture2D");

        // 1. 创建纹理
        FRHITextureCreateDesc Desc = FRHITextureCreateDesc::Create2D(TestName, Width, Height, Format)
            .SetFlags(ETextureCreateFlags::ShaderResource | ETextureCreateFlags::UAV);
        FTextureRHIRef Texture = RHICmdList.CreateTexture(Desc);
        if (!Texture) return false;

        // 2. 准备用于验证的源数据
        TArray<uint8> SourceData;
        SourceData.SetNumUninitialized(Width * Height * GPixelFormats[Format].BlockBytes);
        for (uint32 i = 0; i < SourceData.Num(); ++i) SourceData[i] = i % 256;

        // 3. 更新纹理内容
        FUpdateTextureRegion2D Region(0, 0, 0, 0, Width, Height);
        RHICmdList.UpdateTexture2D(Texture, 0, Region, Width * GPixelFormats[Format].BlockBytes, SourceData.GetData());
        RHICmdList.ImmediateFlush(EImmediateFlushType::FlushRHIThread);

        // 4. (简化) 在实际测试中，这里会创建 SRV 并读回验证。
        // 此插件使用 VerifyTextureContents 等内部函数进行精确验证。
        // 这里仅为演示流程，假设更新成功。
        UE_LOG(LogRHIUnitTestCommandlet, Display, TEXT("Test passed: %s"), TestName);
        return true;
    }
};
```

**在您的测试模块中调用：**
```cpp
// 通常在 IMPLEMENT_SIMPLE_AUTOMATION_TEST 定义的测试函数中
bool bResult = RunOnRenderThreadSynchronous([](FRHICommandListImmediate& RHICmdList) -> bool
{
    return FRHIMyTest::Test_CreateAndVerifyTexture2D(RHICmdList);
});
```

## 模块依赖

此插件的测试代码深度依赖引擎的 RHI 和渲染核心模块。如果你想要**运行或扩展**这些测试，你的项目或测试模块需要链接以下依赖。

| 模块 | 用途 |
|---|---|
| `RHI` | 被测试的核心渲染硬件接口抽象层 |
| `RenderCore` | 提供渲染命令列表、任务调度等基础功能 |
| `Renderer` | 测试中可能用到的渲染器内部功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了格式化函数中作用域枚举可能引起乱码输出的问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了32/64位格式化说明符与参数位宽不匹配的问题 |
| 2026-04-15 | `2a295e97` | Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 统一使用新的 `SubmitAndBlockUntilGPUIdle` API |
| 2026-04-14 | `10c4d2ff` | Adding unit tests for RHI Root Constants. | 为 RHI 根常量添加了单元测试 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF |

### 维护评价

该插件自 2020 年创建以来一直存在。从最近的提交记录看，**维护状态为“维护中”**。近期的更新集中在**适配 RHI 接口的变更**（如日志宏、同步函数重命名）和**修复测试自身的工具代码**（格式化输出）。更重要的是，**新增了对 RHI Root Constants 的测试**（`10c4d2ff`），这表明该测试套件仍在跟随着引擎 RHI 新功能的开发而更新。

**优点**：它是 Epic Games 内部确保 RHI 质量的重要工具，测试覆盖全面，针对性强。
**限制**：作为内部测试工具，它默认禁用，且主要面向引擎开发者。普通游戏项目开发者通常不会直接使用。
**建议**：对于**引擎开发者**、**图形程序员**或**进行底层 RHI 研究和调试**的用户，此插件是验证代码正确性和学习 RHI 用法的宝贵资源。可以放心参考和使用其测试用例。它并没有过时，仍在活跃维护中。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/RHITests)
- 官方文档（无，此为内部测试工具）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/RHITests/Source/RHITests)