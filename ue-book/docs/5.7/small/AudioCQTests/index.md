# Audio Code Quality Tests

> Audio Code Quality Tests

| 属性 | 值 |
|---|---|
| 分类 | Testing |
| 默认启用 | — |
| 包含内容 | false |
| 模块 | AudioCQTests (Runtime) |
| 创建时间 | 2025-08-05 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/AudioCQTests) | |

## 用途

AudioCQTests 是 UE5 音频子系统的 **代码质量测试插件**，专门用于验证 `AudioRenderScheduler`（音频渲染调度器）的正确性。

AudioRenderScheduler 是 AudioMixer 模块中的一个 DAG（有向无环图）调度器，负责在音频渲染线程中按依赖顺序编排各种渲染步骤（如普通音源渲染、Bus 混音、Source Bus 渲染等）。该插件通过 CQTest 测试框架，全面测试调度器在各种拓扑结构下的行为：线性依赖、循环依赖检测与打破、幽灵节点（只声明依赖但未注册的步骤）、稠密图、重复运行一致性等。

**为什么存在：** 音频渲染对时序极其敏感，步骤执行顺序错误会导致音频爆音或丢失。这个插件确保调度器在复杂依赖关系下仍能正确排序。

## 使用场景

- 你正在开发或修改 `AudioRenderScheduler`，需要验证改动不破坏现有调度逻辑
- 你正在为音频系统添加新的渲染步骤，需要确认依赖关系被正确处理
- 你在做 UE5 音频子系统的回归测试

## 蓝图用法

无。本插件仅包含自动化测试代码，不暴露任何蓝图 API。

## C++ 用法

本插件的测试代码使用 CQTest 框架编写，测试的是 `IAudioRenderSchedulerTester` 接口，该接口是对 `AudioRenderScheduler` 的测试封装。

### 头文件引入

```cpp
#include "AudioRenderSchedulerTester.h"  // AudioMixer 模块提供
#include "CQTest.h"                       // CQTest 测试框架
```

### 基本用法

`IAudioRenderSchedulerTester` 提供以下核心方法：

```cpp
// 创建测试器实例
TUniquePtr<IAudioRenderSchedulerTester> Tester = IAudioRenderSchedulerTester::Create();

// 添加编号步骤
Tester->AddStep(0);
Tester->AddStep(1);

// 添加依赖关系（0 必须在 1 之前执行）
Tester->AddDependency(0, 1);

// 执行调度，返回实际执行顺序
TArray<int> Results = Tester->Run();
// Results: [0, 1]

// 移除依赖
Tester->RemoveDependency(0, 1);
```

> 来源：`Engine/Plugins/Tests/AudioCQTests/Source/AudioCQTests/Private/AudioRenderSchedulerTests.cpp`

### 进阶用法

**循环依赖处理：** 调度器能自动打破循环。当存在循环 0→1→2→0 时，调度器会断开其中一条边，输出一个合法的循环排列：

```cpp
// 设置循环依赖
Tester->AddDependency(0, 1);
Tester->AddDependency(1, 2);
Tester->AddDependency(2, 0);

TArray<int> Results = Tester->Run();
// Results 是 [0,1,2] 的某个循环排列，如 [1,2,0] 或 [2,0,1]
// 验证: Results[1] == (Results[0] + 1) % 3
```

**幽灵节点处理：** 只声明了依赖关系但未通过 `AddStep` 注册的步骤会被忽略：

```cpp
Tester->AddDependency(0, 1);  // 步骤 0 和 1 从未 AddStep
TArray<int> Results = Tester->Run();
// Results.Num() == 0，幽灵节点被安全跳过
```

**重复运行一致性：** 多次调用 `Run()` 不改变调度状态，结果一致：

```cpp
TArray<int> First = Tester->Run();
TArray<int> Second = Tester->Run();
// First 和 Second 的顺序完全相同
```

**动态修改依赖：** 可以在运行后修改依赖关系，再次调度会反映新拓扑：

```cpp
Tester->RemoveDependency(3, 4);
Tester->AddDependency(4, 0);
TArray<int> NewResults = Tester->Run();
// NewResults 反映新的依赖拓扑
```

> 来源：`AudioRenderSchedulerTests.cpp` 中的 `TwoCyclesRepeated` 测试

## Demo 示例

本插件不提供独立的运行时功能，无法作为独立 demo 使用。测试通过 UE5 的自动化测试框架运行：

```
# 在编辑器中打开 Session Frontend → Automation → 搜索 "Audio.RenderScheduler"
# 或通过命令行运行:
UnrealEditor-Cmd.exe -ExecCmds="Automation RunTests Audio.RenderScheduler; Quit"
```

## 模块依赖

从 `AudioCQTests.Build.cs` 的 `PrivateDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `AudioMixer` | 提供 `AudioRenderScheduler` 和 `IAudioRenderSchedulerTester` 接口 |
| `Core` | UE5 核心模块（容器、内存管理等） |
| `CQTest` | CQTest 测试框架，提供 `TEST_CLASS`、`TEST_METHOD`、`ASSERT_THAT` 等宏 |
| `Engine` | UE5 引擎模块 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-09-02 | `7c48b5b6` | [Audio Render Scheduler] Move bus mixing and source bus rendering into scheduled steps, and add dependencies so all these steps are ordered and synchronized correctly. | 将 Bus 混音和 Source Bus 渲染纳入调度步骤，并添加依赖确保正确排序。测试用例随功能一起更新。 |
| 2025-08-05 | `f028b6c4` | Add audio rendering scheduler, use it to render normal (non-bus) sources | 初始提交。引入 AudioRenderScheduler 及其测试插件。 |

### 维护评价

- **创建时间：** 2025-08-05，不到 1 年
- **活跃度：** 活跃维护。两次提交间隔约 1 个月，第二次是对调度器的功能扩展
- **测试覆盖：** 覆盖了空步骤、单步、线性依赖、循环依赖、幽灵节点、稠密图等场景，共 15 个测试用例
- **推荐使用：** ✅ 作为 AudioRenderScheduler 的参考实现和回归测试，质量很高。如果你在修改音频渲染管线，建议运行这些测试

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Tests/AudioCQTests)
- [AudioRenderScheduler 源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Runtime/AudioMixer/Private/AudioRenderScheduler.cpp)
- [IAudioRenderSchedulerTester 接口](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Runtime/AudioMixer/Public/AudioRenderSchedulerTester.h)
