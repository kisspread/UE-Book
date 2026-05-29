# nDisplay Fill Derived Data Cache

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 显示集群填充派生数据缓存 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DisplayClusterFillDerivedDataCache` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterFillDerivedDataCache) | |

## 用途

`DisplayClusterFillDerivedDataCache` 模块是一个 **编辑器增强工具**，其核心功能是在编辑器启动时，**自动、异步地**预热与 nDisplay 相关的派生数据缓存（Derived Data Cache， DDC）。它通过启动一个独立的命令行进程（Commandlet），扫描并预编译 nDisplay 配置和渲染管线可能用到的着色器等资产，从而避免开发者在首次运行时经历漫长的实时编译等待，提升工作流效率。该模块并非运行时渲染功能，而是服务于内容创作和开发阶段。

## 使用场景

- **大型 nDisplay 项目开发**：当你的项目包含复杂的 nDisplay 集群渲染配置（如多通道、投影、WarpBlend）以及大量相关的材质和着色器时，在编辑器启动阶段预先填充 DDC，可以显著减少首次播放或打包时因着色器编译导致的卡顿。
- **团队协作与 CI/CD**：在持续集成环境中，确保构建前 DDC 已包含 nDisplay 所需的资源，可以稳定构建时间。

## 蓝图用法

该模块不提供任何可直接在蓝图中调用的函数（无 `BlueprintCallable`）。它是一个纯后台服务模块，在编辑器生命周期中自动运行。

### 核心节点

无

### 使用示例（蓝图描述）

不适用。该模块的功能是自动触发的，无需也无法在蓝图中手动调用。

## C++ 用法

该模块没有对外暴露供其他 C++ 模块直接调用的 API。它的作用通过其模块生命周期（`StartupModule`）自动完成。外部模块无需直接依赖或使用它。

### 头文件引入

通常，其他模块无需包含此模块的头文件。

### 基本用法

模块在引擎初始化完成（`FEngineLoop::Init`）后自动启动其预热工作线程。其核心逻辑封装在内部类 `FDisplayClusterFillDerivedDataCacheWorker` 中。
*代码来源: `Public/DisplayClusterFillDerivedDataCacheWorker.h`*

```cpp
// 该模块内部工作线程的核心循环（简化示例）
class FDisplayClusterFillDerivedDataCacheWorker : public FRunnable
{
    virtual uint32 Run() override
    {
        // 执行命令行输出解析和编辑器通知更新
        ReadCommandletOutputAndUpdateEditorNotification();
        return 0;
    }

    virtual void Stop() override
    {
        // 健壮性检查，处理取消情况
        CancelTask();
    }
};

// 模块启动时创建并启动工作线程
void FDisplayClusterFillDerivedDataCacheModule::OnFEngineLoopInitComplete()
{
    CreateAsyncTaskWorker();
    // ... 启动线程 ...
}
```

### 进阶用法

该模块的“进阶”体现在其内部实现细节，而非外部调用接口。它通过解析命令行进程（DDC Commandlet）的输出日志，使用正则表达式提取枚举、加载和编译的进度信息，并将其反馈到编辑器的任务通知系统中。
*代码来源: `Public/DisplayClusterFillDerivedDataCacheWorker.h`*

```cpp
// 解析DDC命令行日志以获取进度
void FDisplayClusterFillDerivedDataCacheWorker::ReadCommandletOutputAndUpdateEditorNotification()
{
    // 从进程管道读取日志输出
    FString LogString;
    // ... 读取逻辑 ...
    
    // 使用正则表达式解析日志，更新枚举、加载、编译的总数
    RegexParseForEnumerationCount(LogString);
    RegexParseForLoadingProgress(LogString);
    RegexParseForCompilationProgress(LogString);
    
    // 根据解析出的进度更新编辑器通知UI
    if (ProgressNotification)
    {
        // ... 更新通知的进度条和文本 ...
    }
}
```

## Demo 示例

该模块没有可编译的独立示例。其作用是在编辑器启动时作为后台服务运行。一个最小化的“使用”方式是确保 nDisplay 插件已启用，那么在编辑器下次启动时，该模块将自动工作。观察编辑器右下角的任务通知（如果预热开始），可以看到其运行状态。

## 模块依赖

根据该模块的命名和功能（预热 nDisplay 的 DDC），它会隐式依赖于 nDisplay 的核心配置和渲染模块。对于直接使用此模块的外部代码，无需额外依赖。

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

虽然以下提交是针对 nDisplay 插件整体或其它子模块的更新，但表明 nDisplay 插件本身处于**极度活跃**的维护状态。`DisplayClusterFillDerivedDataCache` 模块的功能是相对稳定的基础设施，其最近变更可能包含在插件级提交中。

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为MovieGraph和nDisplay添加EXR多层支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 在nDisplay的MoviePipeline中，将WarpBlendAlpha模式合并到WarpBlend模式。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复多机渲染中拓扑感知相机的命名；修复MPCDI/ICVFX着色器中的不透明Alpha问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | nDisplay：在输出帧编码回退路径中支持非默认的显示伽马值。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复当GUI纹理尺寸小于视口尺寸时的闪烁问题。 |

### 维护评价

- **活跃维护**：nDisplay 插件整体维护非常活跃，近期（2026年5月）仍有密集的功能更新和bug修复。
- **模块状态**：`DisplayClusterFillDerivedDataCache` 作为插件的基础设施模块，其核心逻辑（启动DDC预热进程）可能相对稳定，较少需要更新。它的存在意味着整个插件的开发流程是经过优化的。
- **推荐使用**：**强烈推荐**在任何使用 nDisplay 的项目中保持此插件（及该模块）启用。它是一项重要的性能优化和开发体验改进工具，无需额外配置即可生效。
- **警告**：该模块的功能依赖于特定的 nDisplay 配置和资产。如果项目完全没有使用 nDisplay，此模块不会产生任何效果或开销。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterFillDerivedDataCache)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/ndisplay-in-unreal-engine/) (nDisplay 主文档)