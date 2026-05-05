# XGE Controller

> Adds support for shader compiling distribution using XGE

| 属性 | 值 |
|---|---|
| 分类 | Build Distribution |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | XGEController (UncookedOnly) |
| 创建时间 | 2020-10-22 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/XGEController) | |

## 用途

XGEController 是 Unreal Engine 的分布式构建控制插件，负责通过 **IncrediBuild (XGE)** 将 Shader 编译任务分发到网络中的其他机器执行。

Shader 编译是 UE 项目中最耗时的构建步骤之一，大型项目可能有数万个 Shader 需要编译。XGEController 通过 XGE 的分布式编译能力，将这些编译任务自动分发到局域网内的多台机器上并行执行，显著缩短编译等待时间。

插件通过 Named Pipe 与 `XGEControlWorker.exe` 进程通信，实现任务的调度和结果回收。它实现了 `IDistributedBuildController` 接口，通过 Modular Features 系统注册，引擎的 Shader 编译管理器 (`GShaderCompilingManager`) 会自动发现并使用它。

## 使用场景

- 你的项目有大量 Shader 需要编译（如大型开放世界游戏），本地编译耗时过长 → 启用 XGEController 将编译任务分发到网络中的其他机器
- 你的团队部署了 IncrediBuild 许可证，有多台空闲机器可用于分布式编译 → XGEController 自动利用这些资源
- 你想要避免分布式任务占用本机资源（减少 oversubscription）→ 通过 `r.XGEController.AvoidUsingLocalMachine` 控制

## 前置条件

使用 XGEController 需要满足以下条件：

1. **Windows 平台**：仅支持 Win64，不支持其他平台
2. **IncrediBuild 已安装**：需要安装 Xoreax IncrediBuild，且版本 ≥ 8.01 (build 1867)
3. **BuildService 运行中**：IncrediBuild 的后台服务 `BuildService.exe` 必须正在运行
4. **XGEControlWorker.exe 存在**：引擎 Binaries 目录下需要有此文件

插件启动时会自动检测这些条件，如果任一条件不满足，会回退到本地编译。

## 蓝图用法

XGEController 是一个纯 C++ 的构建系统插件，没有暴露任何 Blueprint 节点。它的所有配置通过控制台变量 (CVar) 和命令行参数完成。

## C++ 用法

XGEController 作为底层构建基础设施，通常不需要用户直接调用其 API。引擎的 Shader 编译管理器会自动使用它。但你可以通过以下方式与其交互：

### 获取模块实例

```cpp
#include "XGEControllerModule.h"

// 获取模块单例
FXGEControllerModule& XGEController = FXGEControllerModule::Get();

// 检查 XGE 是否可用
if (XGEController.IsSupported())
{
    // XGE 可用于分布式编译
}
```

### 检查本地 Worker 支持

```cpp
// 查询是否支持在本机运行任务
bool bSupportsLocal = XGEController.SupportsLocalWorkers();
```

### 通过 Modular Features 发现控制器

```cpp
#include "Features/IModularFeatures.h"
#include "DistributedBuildControllerInterface.h"

// 通用方式：通过 Modular Features 查找所有注册的分布式构建控制器
TArray<IModularFeature*> Features = IModularFeatures::Get().GetModularFeatureImplementations(
    IDistributedBuildController::GetModularFeatureType());

for (IModularFeature* Feature : Features)
{
    IDistributedBuildController* Controller = static_cast<IDistributedBuildController*>(Feature);
    UE_LOG(LogTemp, Log, TEXT("Found controller: %s, Supported: %d"),
        *Controller->GetName(), Controller->IsSupported());
}
```

## 控制台变量

| CVar | 默认值 | 说明 |
|---|---|---|
| `r.XGEController.Enabled` | 1 | 启用/禁用 XGE 分布式构建。`0`: 仅本地编译；`1`: 使用 XGE 分发。**只读**，需在启动时通过 config ini 设置 |
| `r.XGEController.Timeout` | 2.0 | 所有任务完成后等待多少秒再关闭 XGE 控制器进程（秒） |
| `r.XGEController.AvoidUsingLocalMachine` | 1 | 控制 XGE 任务是否避免在本机运行。`0`: 不避免，所有 agent 包括本机都参与；`1`: 避免在本机运行，但在 commandlet 或 build machine 模式下仍使用本机（默认）；`2`: 始终避免在本机运行 |

## 命令行参数

| 参数 | 说明 |
|---|---|
| `-xgecontroller` | 强制启用 XGE Controller（覆盖 CVar） |
| `-noxgecontroller` | 强制禁用 XGE Controller |
| `-noxgeshadercompile` | 强制禁用 XGE（同 `-noxgecontroller`） |
| `-noshaderworker` | 强制禁用 XGE（同 `-noxgecontroller`） |
| `-buildmachine` | 标记为构建机器，影响 `AvoidUsingLocalMachine` 行为 |

## 工作原理

1. **启动检测**：模块加载时（`EarliestPossible` 阶段）注册为 Modular Feature
2. **初始化**：`InitializeController()` 检查 IncrediBuild 安装状态，查找 `xgConsole.exe`
3. **任务调度**：引擎将 Shader 编译任务通过 `EnqueueTask()` 提交，任务进入待处理队列
4. **进程通信**：通过 Named Pipe 与 `XGEControlWorker.exe` 双向通信
   - `WriteOutThreadProc`：将待处理任务发送给 XGE 控制进程
   - `ReadBackThreadProc`：接收完成的任务结果
5. **超时回收**：任务完成后等待 `r.XGEController.Timeout` 秒，如果没有新任务则关闭 XGE 控制进程
6. **崩溃保护**：启动 `XGEControlWorker.exe` 监控进程，确保引擎崩溃时 XGE 构建进程也能被终止

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础功能（线程、文件系统、进程管理等） |
| `Slate` | 访问 `GShaderCompilingManager` |
| `RHI` | 访问 `GShaderCompilingManager` |
| `RenderCore` | 访问 `GShaderCompilingManager` |
| `Engine` | 访问 `GShaderCompilingManager` |
| `DistributedBuildInterface`（Include 路径） | `IDistributedBuildController` 接口定义 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-05-30 | `2739c3d` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 4/n | 代码质量改进，修正 DLL 导出标记，无功能变化 |
| 2025-05-23 | `46329b5` | Abstracting _M_ARM64 and _M_ARM64EC | ARM64 架构支持改进，添加 arm64ec 和 arm64 的 XGEControlWorker 变体 |
| 2025-03-24 | `9e2717b` | Update shader compiler worker references for arm64 and arm64ec | 更新 ARM64 平台的 ShaderCompileWorker 引用 |

### 维护评价

- **创建时间**：2020-10-22，约 5.5 年历史
- **更新频率**：近期更新主要是平台适配（ARM64）和代码规范化，非功能性变更
- **活跃程度**：维护中，但无重大功能更新
- **稳定程度**：成熟稳定，作为核心构建基础设施，变更频率低是正常的
- **推荐使用**：如果团队部署了 IncrediBuild，这是开箱即用的集成方案。插件默认启用，只要环境满足前置条件即可自动工作

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/XGEController)
- [DistributedBuildInterface 接口](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Developer/DistributedBuildInterface)
