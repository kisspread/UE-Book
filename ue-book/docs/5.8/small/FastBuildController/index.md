# FastBuild Controller

> Adds support for shader compiling distribution using FastBuild

| 属性 | 值 |
|---|---|
| 中文名 | FastBuild 着色器编译 |
| 分类 | Build Distribution |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `FastbuildController` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-05-26 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FastBuildController) | |

## 用途

FastBuildController 是 UE5 着色器编译的分布式构建控制器。它将引擎的着色器编译任务分发到 [FASTBuild](https://www.fastbuild.org/) 分布式构建系统上执行，利用多台机器的算力并行编译着色器，大幅缩短大型项目的着色器编译时间。

该插件实现了 `IDistributedBuildController` 接口，作为引擎着色器编译管线的一个可插拔后端。引擎本身支持多种分布式编译控制器（如 SN-DBS、XGE 等），FastBuildController 是其中基于 FASTBuild 的实现方案。

**注意**：默认未启用（`EnabledByDefault=false`），需要在项目设置或命令行中手动启用。2025 年 9 月的更新中更是明确将其默认关闭。

## 使用场景

- 你有一个大型 UE5 项目，着色器编译耗时严重（几分钟到几十分钟） → 用 FastBuild 分布式编译加速
- 你的团队有多台闲置编译机器且已部署 FASTBuild 基础设施 → 通过此插件让 UE5 着色器编译利用该集群
- 你想替代 Unreal Game Extensions (XGE) 或 SN-DBS 的分布式编译方案 → 使用 FASTBuild 作为替代
- 你需要跨平台的分布式构建支持（该插件选择器是 OS-agnostic 的）

## 蓝图用法

该插件是纯 C++ 运行时模块，没有暴露任何蓝图可调用的节点。所有操作通过引擎的着色器编译管线自动完成，用户只需配置启用即可。

## C++ 用法

### 头文件引入

```cpp
#include "FastBuildControllerModule.h"
#include "FastBuildUtilities.h"
#include "FastBuildJobProcessor.h"
```

### 基本用法

该插件作为 `IDistributedBuildController` 的实现，由引擎内部调度。以下是核心交互接口：

```cpp
// 获取控制器单例
FFastBuildControllerModule& Controller = FFastBuildControllerModule::Get();

// 检查是否支持当前平台
if (Controller.IsSupported())
{
    // 初始化控制器
    Controller.InitializeController();
}

// 提交着色器编译任务（通常由引擎自动调用）
TArray<FDistributedBuildTask*> Tasks;
// ... 填充任务 ...
Controller.EnqueueTask(Tasks);

// 检查任务状态
bool bPending = Controller.AreTasksPending();
bool bDispatched = Controller.AreTasksDispatched();
int32 PendingCount = Controller.GetPendingTasksAmount();
```

来源：`Source/Public/FastBuildControllerModule.h`

### 进阶用法

```cpp
// 获取工作目录信息
FString RootDir = Controller.GetRootWorkingDirectory();
FString WorkDir = Controller.GetWorkingDirectory();
FString ShaderDir = Controller.GetIntermediateShadersDirectory();

// 路径重映射（FastBuild 需要相对路径）
FString RemappedPath = Controller.RemapPath(SourcePath);

// 手动管理任务队列
FDistributedBuildTask* Task = Controller.DequeueTask();
Controller.RegisterDispatchedTask(Task);

TArray<uint32> CompletedIDs;
Controller.DeRegisterDispatchedTasks(CompletedIDs);
```

来源：`Source/Public/FastBuildControllerModule.h`

## Demo 示例

该插件是引擎内部集成的分布式构建控制器，不提供独立的使用 Demo。典型集成方式如下：

```cpp
// MyShaderCompileModule.h
#pragma once

#include "Modules/ModuleManager.h"

class FMyShaderCompileModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// MyShaderCompileModule.cpp
#include "MyShaderCompileModule.h"
#include "FastBuildControllerModule.h"

void FMyShaderCompileModule::StartupModule()
{
    // 确保 FastBuildController 模块已加载
    FModuleManager::Get().LoadModule(TEXT("FastbuildController"));
    
    FFastBuildControllerModule& Controller = FFastBuildControllerModule::Get();
    if (Controller.IsSupported())
    {
        UE_LOG(LogTemp, Log, TEXT("FastBuild Controller 已就绪，工作目录: %s"), 
            *Controller.GetRootWorkingDirectory());
    }
}

void FMyShaderCompileModule::ShutdownModule()
{
    // 控制器由引擎自动管理生命周期
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DistributedBuildController` | 引擎的分布式构建控制器接口基类（提供 `IDistributedBuildController`） |

> 其他依赖为标准 Core/Engine 模块（Core, CoreUObject, Engine 等），无需额外声明。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 新日志宏 |
| 2026-01-28 | `5f766aee` | Fixed modules that does not support portable toolchain | 修复不支持便携工具链的模块兼容性 |
| 2026-01-26 | `ae382a88` | [ubacontroller] virtual file support & other optimizations/improvements | UBA 控制器虚拟文件支持及其他优化改进 |
| 2026-01-13 | `4c04edd1` | [IOS/Mac] Initial pass to remove iOS/macOS sdk headers from Engine platform header files where possi | 移除引擎平台头文件中不必要的 iOS/macOS SDK 头文件引用 |
| 2025-09-08 | `df7203e2` | [Shaders] Disable FastBuildController plugin by default. | 将 FastBuildController 插件设为默认禁用 |

### 维护评价

**维护状态：活跃维护中**

该插件创建于 2021 年，最近一次实质性更新在 2026 年 4 月。从 git 历史来看：

- 2025 年 9 月被设为默认禁用，说明 Epic 可能在推动其他分布式编译方案（如 UBA）
- 但 2026 年初仍有编译修复和平台兼容性更新，说明未被废弃
- 作为小型 Runtime 插件（仅 6 个源文件），维护成本较低
- 插件功能单一明确，稳定性依赖外部 FASTBuild 工具的安装和配置

⚠️ **注意**：该插件已被默认禁用，且 2026 年初的更新中出现了 `[ubacontroller]` 相关的优化，可能预示着 UEBA（Unreal Build Accelerator）正在逐步替代 FastBuild 作为官方推荐的分布式编译方案。如果你的项目已依赖 FastBuild，建议关注后续版本是否继续维护。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FastBuildController)
- [FASTBuild 官方网站](https://www.fastbuild.org/)