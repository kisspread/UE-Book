# FastBuild Controller

> Adds support for shader compiling distribution using FastBuild

| 属性 | 值 |
|---|---|
| 中文名 | FastBuild 编译控制器 |
| 分类 | Build Distribution |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `FastbuildController` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-23 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FastBuildController) | |

## 用途

该插件提供了一个分布式编译控制器，将 UE 的着色器编译任务通过 [FastBuild](https://www.fastbuild.org/) 工具分发到多台机器或本地集群上并行执行，从而显著缩短项目在编辑器或打包过程中的着色器编译等待时间。它实现了 `IDistributedBuildController` 接口，由 UE 的编译系统自动调度，用户无需手动干预即可利用 FastBuild 加速构建。

## 使用场景

- 你正在开发一个大型 UE 项目，着色器数量庞大导致每次编译等待时间长。
- 你已部署或可以使用 FastBuild 分布式构建环境（本机多核、局域网多机、或容器集群）。
- 你希望无需修改现有构建流程，仅启用插件即可获得即时的编译加速。

## 蓝图用法

该插件**不暴露任何蓝图可调用节点**。所有功能均通过 C++ 接口在后台自动执行，用户只需在项目设置中启用插件即可。

## C++ 用法

### 头文件引入

```cpp
#include "FastBuildControllerModule.h"
```

### 基本用法

FastBuild 控制器通过 `IDistributedBuildController` 接口与 UE 编译系统集成。通常在 `BuildConfiguration` 中启用分布式编译后，引擎会自动创建并使用匹配的控制器。以下代码展示如何获取控制器实例并检查其是否受支持：

```cpp
// 在模块 StartupModule 或 Engine 启动后
FFastBuildControllerModule& Controller = FFastBuildControllerModule::Get();
if (Controller.IsSupported())
{
    UE_LOG(LogTemp, Log, TEXT("FastBuildController is available."));
    // 可通过 Controller 创建唯一文件路径、排队任务等（通常由编译系统调用）
}
```

### 进阶用法

当引擎需要分发着色器编译任务时，会调用 `EnqueueTask` 将任务添加到控制器内部队列。控制器内部维护一个后台线程 `FFastBuildJobProcessor`，不断从队列取出任务，生成 FastBuild 脚本（.bff 格式）并启动 `FBuild.exe` 进程，然后轮询结果文件收集编译输出。

```cpp
// 头文件：Source/Public/FastBuildControllerModule.h
// 主要函数说明
// EnqueueTask(const FTaskCommandData& CommandData) -> TFuture<FDistributedBuildTaskResult>
// 将单个编译命令分发到 FastBuild。
// 返回一个 Future，当编译完成时填充结果。

// RemapPath(const FString& SourcePath) -> FString
// 将 UE 内部的路径映射为 FastBuild 可识别的绝对路径。
```

## Demo 示例

以下是一个最小示例，展示如何在自定义模块中集成 FastBuild 控制器（假设模块依赖已正确设置）。该示例仅验证插件是否启用，不做实际编译分发。

**MyBuildModule.h**
```cpp
#pragma once
#include "Modules/ModuleInterface.h"
#include "Modules/ModuleManager.h"

class FMyBuildModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MyBuildModule.cpp**
```cpp
#include "MyBuildModule.h"
#include "FastBuildControllerModule.h"

IMPLEMENT_MODULE(FMyBuildModule, MyBuildModule);

void FMyBuildModule::StartupModule()
{
    FFastBuildControllerModule& Controller = FFastBuildControllerModule::Get();
    if (Controller.IsSupported())
    {
        UE_LOG(LogTemp, Display, TEXT("FastBuild Controller is supported and ready."));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("FastBuild Controller is not supported on this platform."));
    }
}

void FMyBuildModule::ShutdownModule()
{
    // 控制器会在引擎关闭时自动清理
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DistributedBuildControllerInterface` | 定义 `IDistributedBuildController` 基类接口 |

其余依赖均为标准模块（Core, CoreUObject, Engine 等），此处省略。

## 维护状态

### 近期更新

- 2025-09-08 `69cf2d99` [Shaders] Disable FastBuildController plugin by default.
- 2025-01-17 `1334c9d5` [Shaders] Renamed FTask in DistributedBuildControllerInterface.h to FDistributedBuildTask to avoid conflict.
- 2025-01-16 `63c829d1` [Shaders] Minor code cleanup of canceling distributed shader compile tasks.
- 2024-11-10 `66e9bb39` Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base.
- 2024-09-23 `3ac66072` [misc] fix lots of FString::Printf format errors.

### 维护评价

该插件创建于 2024 年 9 月，至今约 1 年，仍处于早期版本（0.1）。最近一次更新在 2025 年 9 月，主要是禁用默认启用（避免非预期的调用），以及重构和重命名，表明维护团队在使用过程中持续调整。未发现废弃标记或严重问题。由于功能性强且仅作为可选加速组件，推荐有 FastBuild 环境的项目启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FastBuildController)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/distributed-shader-compilation/)（UE 分布式编译通用文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FastBuildController/Tests)（需确认是否存在，若不存在可忽略）