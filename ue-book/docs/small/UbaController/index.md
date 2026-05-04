# UBA Controller

> Adds support for shader compiling distribution using UnrealBuildAccelerator (UBA)

| 属性 | 值 |
|---|---|
| 分类 | Build Distribution |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | UbaController (Editor, EarliestPossible) |
| 创建时间 | 2024-01-09 |
| 年龄标签 | 🆕 (~2 年) |
| 实验性 | ⚠️ IsExperimentalVersion = true |
| 支持平台 | Win64, Mac, Linux |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/UbaController) | |

## 用途

UbaController 是 UE5 分布式着色器编译系统的控制器插件，基于 Epic 自研的 **UnrealBuildAccelerator (UBA)** 框架实现。它的核心职责是将 ShaderCompileWorker 的编译任务分发到远程机器上执行，从而大幅加速着色器编译过程。

**为什么存在？** 大型 UE5 项目（尤其是开放世界游戏）可能有数万个着色器变体需要编译。单机编译耗时极长。UbaController 利用 UBA 的进程代理（process detouring）技术，将 ShaderCompileWorker 进程透明地重定向到远程机器执行——本地无需修改任何着色器编译流程，UBA 通过文件系统代理自动传输输入/输出文件。

该插件实现了 `IDistributedBuildController` 接口，作为引擎分布式编译框架的一个后端。它同时支持两种远程算力来源：
1. **局域网 (LAN)** — 通过 UBA 网络服务器自动发现并利用同网段的空闲机器
2. **Horde 集群** — 通过 Epic 的 Horde 构建系统分配远程构建代理

## 使用场景

- 你的项目有大量着色器需要编译（如开放世界、Lumen/Nanite 材质众多），本地编译一次需要 30 分钟以上
- 你的团队有 Horde 构建农场或局域网内有多台空闲机器可以贡献算力
- 你在 CI/CD 构建服务器上希望利用分布式资源加速 Cook 阶段的着色器编译
- 你想在编辑器中实时编辑材质时减少着色器编译等待时间

**不需要 UbaController 的场景：**
- 小型项目，着色器数量少，本地编译已经够快
- 没有多余的远程机器资源

## 蓝图用法

UbaController 是 Editor 模块且不暴露任何 `BlueprintCallable` 接口。它的全部功能通过引擎内部的 `IDistributedBuildController` 接口自动集成，用户无法也不需要在蓝图中直接调用。

控制该插件的方式是通过**命令行参数**和 **INI 配置**，详见下方 C++ 用法章节。

## C++ 用法

UbaController 是一个被动型模块——启动后自动注册为分布式编译控制器，由引擎的着色器编译管理器自动调度。用户通常不需要直接调用其 C++ API，但可以通过以下方式控制其行为。

### 命令行参数

| 参数 | 说明 |
|---|---|
| `-UBA` | 强制启用 UBA 控制器 |
| `-UBAEnableHorde` | 启用 Horde 远程代理支持 |
| `-NoUbaController` | 禁用 UBA 控制器（兼容旧参数名） |
| `-NoUbaShaderCompile` | 禁用 UBA 着色器编译分发 |
| `-NoShaderWorker` | 禁用所有远程着色器编译 |

### INI 配置

在 `Engine.ini` 或项目的 `[UbaController]` section 中配置 Horde 提供者：

```ini
[UbaController]
bIsProviderEnabled=true
```

### 控制台变量 (CVars)

所有 CVar 都以 `r.UbaController.` 为前缀，可在运行时通过控制台调整：

| CVar | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `r.UbaController.DumpTraceFiles` | bool | `true` | 是否在 `Saved/UbaController/` 下保存 UBA trace 文件（可用于 UBA Visualizer 分析） |
| `r.UbaController.SleepTimeBetweenActions` | float | `0.01` | 调度线程循环间隔（秒） |
| `r.UbaController.MaxTimeWithoutTasks` | float | `100.0` | 无任务后等待多久才关闭 UBA 连接（秒），避免频繁启停 |
| `r.UbaController.HeartBeatInterval` | float | `180.0` | 心跳日志输出间隔（秒） |
| `r.UbaController.AutoLaunchVisualizer` | bool | `false` | 是否自动启动 UBA Visualizer 工具 |
| `r.UbaController.AllowProcessReuse` | bool | `true` | 是否允许远程进程复用（减少启动开销） |
| `r.UbaController.DetailedTrace` | bool | `false` | 是否输出详细的 UBA trace 信息 |
| `r.UbaController.LogVerbosity` | int | `0` | UBA 日志转发级别：0=仅错误/警告，1=包含 Info，2=全部 |
| `r.UbaController.SaveTraceSnapshotInterval` | int | `0` | 定期保存 trace 快照的间隔（秒），0=仅结束时保存 |
| `r.UbaController.ProcessLogEnabled` | bool | `false` | 是否为每个 detoured 进程写日志文件（仅 UBA debug 编译有用） |

### 内部架构

如果你需要扩展或调试 UbaController，以下是其核心类关系：

```
引擎 ShaderCompileManager
    └── IDistributedBuildController (接口)
            └── FUbaControllerModule (Editor 模块)
                    ├── PendingRequestedCompilationTasks (SPSC 队列)
                    └── FUbaJobProcessor (后台 FRunnable 线程)
                            ├── uba::NetworkServer   ← UBA 网络层
                            ├── uba::StorageServer   ← UBA CAS 存储
                            ├── uba::SessionServer   ← UBA 会话管理
                            ├── uba::Scheduler       ← 本地/远程任务调度
                            └── FUbaHordeAgentManager ← Horde 代理管理
```

**工作流程：**
1. 引擎调用 `EnqueueTask()` 提交着色器编译任务
2. 后台 `FUbaJobProcessor` 线程从队列取出任务
3. 通过 UBA `Scheduler_EnqueueProcess()` 将 ShaderCompileWorker 进程分发到本地或远程执行
4. UBA 通过文件系统代理自动处理输入文件传输和输出文件回收
5. 进程退出回调中验证输出文件完整性，报告完成状态

### 访问模块实例

```cpp
#include "UbaControllerModule.h"

// 获取模块单例
FUbaControllerModule& Module = FUbaControllerModule::Get();

// 检查是否可用
if (Module.IsSupported())
{
    // UBA 控制器已启用且可用
}
```

**头文件引入：**
```cpp
#include "UbaControllerModule.h"  // 主模块接口
#include "UbaJobProcessor.h"      // 作业处理器（通常不需要直接引用）
```

### 自定义本地并行度

引擎通过 `SetMaxLocalWorkers()` 控制 UBA 在本地使用的最大核心数：

```cpp
// 限制本地最多使用 4 核
FUbaControllerModule::Get().SetMaxLocalWorkers(4);
```

实际本地并行数还受以下因素影响：
- INI 配置中的 `MaxParallelActions`
- 引擎着色器管理器的 `NumUnusedShaderCompilingThreads` 设置
- 远程任务数量（每 30 个远程任务自动让出 1 个本地核心）

## Demo 示例

UbaController 不需要用户编写代码集成——它是引擎内置的分布式编译后端，自动由着色器编译系统调度。

**最简启用步骤：**

1. 确保引擎目录下有 UBA 二进制文件：`Engine/Binaries/{Platform}/UnrealBuildAccelerator/`
2. 启动编辑器时添加命令行参数 `-UBA`
3. 或在 INI 中配置 Horde 提供者

**验证是否工作：**
```bash
# 启动编辑器，观察日志中是否有：
# "Starting up UBA/Horde connection for session ..."
# "Created UBA storage server: RootDir=..."

# 查看 trace 文件（如已启用）：
# {ProjectSavedDir}/UbaController/UbaController.MultiprocessId-*.Session-*.uba
```

**使用 UBA Visualizer 分析：**
```
# 设置自动启动 visualizer
r.UbaController.AutoLaunchVisualizer 1

# 或手动打开 trace 文件：
# {ProjectSavedDir}/UbaController/ 目录下的 .uba 文件
```

## 模块依赖

UbaController 的所有依赖都是 PrivateDependencyModuleNames，外部模块不需要额外依赖。

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `DistributedBuildInterface` | 分布式编译控制器接口定义（`IDistributedBuildController`） |
| `Projects` | 插件项目系统 |
| `RenderCore` | 渲染核心，着色器编译相关 |
| `TargetPlatform` | 目标平台管理，获取着色器编译器依赖文件列表 |
| `Horde` | Epic Horde 构建系统客户端 |
| `HTTP` | HTTP 通信模块（Horde 通信） |
| `Sockets` | Socket 网络通信（UBA 局域网通信） |
| `UbaCoordinatorHorde` | UBA 与 Horde 的协调层，提供 `FUbaHordeAgentManager` |
| `Json` | JSON 解析（Horde API 通信） |

**外部二进制依赖：**
- `UbaHost.dll` / `libUbaHost.dylib` / `libUbaHost.so` — UBA 宿主库，位于 `Engine/Binaries/{Platform}/UnrealBuildAccelerator/`

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-08-28 | `edf61350` | [UBA] Try to open file in WriteCasFileNoCheck() multiple times before giving up in case there is a race condition. | 修复 CAS 文件写入的竞态条件，通过重试机制提高可靠性 |
| 2025-07-22 | `2f998624` | [UBA] Explicitly load Sockets module in UbaController to ensure it's loading in the game thread. | 确保 Sockets 模块在游戏线程加载，修复潜在的线程安全问题 |
| 2025-06-24 | `e661e7e1` | [UBA] Clean up dispatcher thread shutdown code in UbaController. | 清理调度线程关闭逻辑，提升稳定性 |

### 维护评价

- **创建时间**：2024-01-09（约 2 年前）
- **最近更新**：2025-08-28（3 个月内），最近 3 次提交间距均匀（每月一次）
- **维护状态**：✅ **活跃维护** — 近期有实质性的 bug 修复和稳定性改进
- **实验性标记**：⚠️ `.uplugin` 中 `IsExperimentalVersion = true`，表明 Epic 尚未将其标记为正式发布
- **已知限制**：Mac 平台当前被禁用（代码中有 `#if PLATFORM_MAC return false`），原因是 shadermap 挂起和 UBA detour 问题
- **推荐程度**：如果你的项目有 Horde 构建农场或局域网资源可用，这是一个值得启用的性能优化插件。虽然是实验性状态，但代码质量高（Epic 内部使用），维护活跃。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/UbaController)
- [UBA 源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Programs/UnrealBuildAccelerator)
- 官方文档（无，`.uplugin` 中 DocsURL 为空）
- 测试用例（本插件目录下无独立测试文件）
