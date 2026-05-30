# nDisplay Fill Derived Data Cache

> 该模块负责在编辑器启动时异步执行 DDC（Derived Data Cache）填充任务，以预先缓存 nDisplay 所需的着色器和材质资源，避免项目运行时首次加载时出现卡顿。

| 属性 | 值 |
|---|---|
| 中文名 | nDisplay DDC 预热模块 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、蓝图、材质等） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

本模块是 nDisplay 虚拟制片插件的一个辅助模块，核心功能是**预热衍生数据缓存（DDC）**。

在复杂的虚拟制片（Virtual Production）项目中，nDisplay 需要编译大量特殊的着色器（如用于几何校正、色彩映射的着色器）。这些着色器在首次加载或修改后都需要进行编译，可能会导致编辑器或运行时出现可感知的延迟（如“着色器编译中...”的卡顿）。

**`DisplayClusterFillDerivedDataCache` 模块的存在就是为了解决这个问题**。它通过在编辑器后台异步运行一个 DDC 填充命令行（`DerivedDataCacheCommandlet`），预先将 nDisplay 所需的资源编译并存入本地 DDC。当用户后续打开 nDisplay 配置或运行项目时，所需资源已存在于缓存中，从而显著提升了编辑器的响应速度和项目的启动体验。

## 使用场景

- **你正在开发一个使用 nDisplay 进行 LED 墙渲染的虚拟制片项目**，项目中包含大量 nDisplay 的配置文件和自定义材质。项目首次在新电脑上打开或拉取新版本后，启动编辑器会非常缓慢。
- **希望避免在会议演示或实时拍摄前，因着色器编译导致意外延迟**。启用此插件可以在后台提前完成编译工作。
- **你是一个技术美术或管线工程师，需要为团队优化项目的工作流**，可以预先配置此插件，让所有成员的编辑器启动后自动进行 DDC 预热。

## 蓝图用法

该模块没有暴露任何公开的蓝图 API。其所有功能均为后台自动化任务，由模块在编辑器启动时自动触发，或通过控制台命令手动触发。无需在蓝图中直接调用。

### 核心节点

无公开蓝图 API。该模块的操作完全由系统自动管理或通过控制台命令 `DisplayCluster.FillDerivedDataCache` 执行。

## C++ 用法

此模块主要通过模块生命周期自动工作，开发者通常无需直接与其 C++ 接口交互。但了解其内部工作机制有助于定制或调试。

### 头文件引入

```cpp
// 如果需要直接访问模块接口（通常不需要）
#include "DisplayClusterFillDerivedDataCacheModule.h"
```

### 基本用法（模块行为）

该模块在编辑器启动时自动注册一个引擎初始化完成的委托，并在回调中创建一个异步任务工作者（`FDisplayClusterFillDerivedDataCacheWorker`）来执行 DDC 填充。

**来源文件**: `Source/DisplayClusterFillDerivedDataCache/Public/DisplayClusterFillDerivedDataCacheModule.h`
```cpp
// 模块启动时的简化逻辑
void FDisplayClusterFillDerivedDataCacheModule::StartupModule()
{
    // 注册引擎初始化完成的回调
    FCoreDelegates::OnFEngineLoopInitComplete.AddRaw(this, &FDisplayClusterFillDerivedDataCacheModule::OnFEngineLoopInitComplete);
}

// 回调中创建工作线程
void FDisplayClusterFillDerivedDataCacheModule::OnFEngineLoopInitComplete()
{
    CreateAsyncTaskWorker(); // 启动后台任务
}
```

### 进阶用法（任务工作者）

后台工作者 (`FDisplayClusterFillDerivedDataCacheWorker`) 继承自 `FRunnable`，在独立线程中执行命令行程序，并监控其输出以更新编辑器通知。

**来源文件**: `Source/DisplayClusterFillDerivedDataCache/Public/DisplayClusterFillDerivedDataCacheWorker.h`
```cpp
// 工作者核心运行逻辑
uint32 FDisplayClusterFillDerivedDataCacheWorker::Run()
{
    ReadCommandletOutputAndUpdateEditorNotification(); // 阻塞，读取命令行输出
    return 0;
}

// 解析命令行输出以获取进度
void FDisplayClusterFillDerivedDataCacheWorker::ReadCommandletOutputAndUpdateEditorNotification()
{
    // 循环读取进程的标准输出管道
    // 使用正则表达式解析日志，提取“枚举资源总数”、“加载进度”、“编译进度”
    // 根据解析结果更新 TUniquePtr<FAsyncTaskNotification> ProgressNotification
    // 例如：
    // RegexParseForEnumerationCount(LogString); // 解析正在枚举的资源数量
    // RegexParseForLoadingProgress(LogString);  // 解析加载进度
    // RegexParseForCompilationProgress(LogString); // 解析着色器编译进度
}
```

## Demo 示例

本模块为编辑器自动化后台服务，不适用于创建运行时 Demo。其“使用”方式是在插件描述中启用该模块。以下为模块初始化的核心框架代码示例：

**DisplayClusterFillDerivedDataCacheWorker.h (关键部分)**
```cpp
#pragma once
#include "HAL/Runnable.h"

class FDisplayClusterFillDerivedDataCacheWorker : public FRunnable, public FSingleThreadRunnable
{
public:
    FDisplayClusterFillDerivedDataCacheWorker();
    virtual ~FDisplayClusterFillDerivedDataCacheWorker() override;

    // FRunnable 接口
    virtual uint32 Run() override;
    virtual void Stop() override;

    // FSingleThreadRunnable 接口 (用于编辑器tick)
    virtual void Tick() override;
    virtual FSingleThreadRunnable* GetSingleThreadInterface() override;

private:
    void ReadCommandletOutputAndUpdateEditorNotification();
    void CancelTask();

    TUniquePtr<FAsyncTaskNotification> ProgressNotification;
    FProcHandle ProcessHandle;
    void* ReadPipe;
    void* WritePipe;
    // ... 其他进度跟踪变量
};
```

**DisplayClusterFillDerivedDataCacheWorker.cpp (简化示例)**
```cpp
#include "DisplayClusterFillDerivedDataCacheWorker.h"
#include "Async/AsyncWork.h"
#include "Misc/ScopedSlowTask.h"

uint32 FDisplayClusterFillDerivedDataCacheWorker::Run()
{
    // 构建并启动 DDC 填充命令行程序
    // 例如：UProject.exe -run=DerivedDataCacheCommandlet -Fill -platform=Windows
    FString ExePath = FPlatformProcess::ExecutablePath();
    FString Params = GetDdcCommandletParams();
    FPlatformProcess::CreatePipe(ReadPipe, WritePipe);
    ProcessHandle = FPlatformProcess::CreateProc(*ExePath, *Params, false, true, true, nullptr, 0, nullptr, WritePipe);

    if (ProcessHandle.IsValid())
    {
        // 进入循环，持续读取管道输出并更新通知
        ReadCommandletOutputAndUpdateEditorNotification();
    }
    return 0;
}

void FDisplayClusterFillDerivedDataCacheWorker::Stop()
{
    CancelTask(); // 请求取消任务
}

void FDisplayClusterFillDerivedDataCacheWorker::Tick()
{
    // 在单线程模式下（编辑器Tick）定期检查状态并更新UI通知
    ReadCommandletOutputAndUpdateEditorNotification();
}

void FDisplayClusterFillDerivedDataCacheWorker::CancelTask()
{
    bWasCancelled = true;
    if (ProcessHandle.IsValid())
    {
        FPlatformProcess::TerminateProc(ProcessHandle);
    }
    CompleteCommandletAndShowNotification();
}
```

## 模块依赖

该模块自身的 `Build.cs` 未在提供的信息中列出详细依赖。但作为 nDisplay 插件的一部分，其隐含的运行时依赖通常包括 nDisplay 的核心模块。

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 核心运行时模块 |
| `DisplayClusterConfiguration` | 加载和解析 nDisplay 配置文件（.ndisplay） |
| `DisplayClusterShaders` | 包含 nDisplay 特殊着色器，是 DDC 预热的主要目标之一 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | nDisplay 支持 MovieGraph 的多层 EXR 输出。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 统一了 MoviePipeline 中的 WarpBlend 和 WarpBlendAlpha 模式。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了 MRG 中拓扑感知相机命名及 MPCDI/ICVFX 着色器中的不透明度问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复了输出帧编码回退时未使用自定义 DisplayGamma 的问题。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了 GUI 纹理尺寸小于视口尺寸时出现的闪烁问题。 |

### 维护评价

- **创建时间**：约 8 年前（2018年），是一个非常成熟的模块。
- **维护状态**：**活跃维护**。从近期提交记录看，nDisplay 作为一个整体（包括此模块）仍在持续获得新功能和 Bug 修复，最近的活动集中在支持新的 Movie Graph 管线和修复着色器问题。
- **推荐度**：**推荐使用**。对于任何使用 nDisplay 进行虚拟制片的项目，启用此模块可以显著改善编辑器工作流体验，尤其在资产量大的情况下。它作为 Epic Games 官方维护的核心插件的一部分，稳定性和可靠性有保障。
- **注意事项**：此模块为**可选模块**（`EnabledByDefault: false`），需要在插件设置中手动启用。它仅在编辑器运行时生效，对打包后的项目无影响。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterFillDerivedDataCache)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/nDisplay-in-Unreal-Engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests) (整个 nDisplay 插件的测试集)