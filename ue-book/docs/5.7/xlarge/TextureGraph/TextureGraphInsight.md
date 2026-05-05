# Texture Graph

> Texture creation tool using graphs.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `TextureGraph` (Runtime), `TextureGraphEditor` (Runtime), `TextureGraphEngine` (Runtime), `TextureGraphInsight` (Runtime), `TextureGraphInsightEditor` (Runtime), `Continuable` (External), `Function2` (External) |
| 实验性 | 否 |
| 创建时间 | 2023-12-20 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/TextureGraph) | |

## 用途

TextureGraph 是一个基于节点图的程序化纹理创建工具。它允许用户通过连接各种操作节点（如数学运算、噪声生成、图像处理等）来定义复杂的纹理生成逻辑，类似于材质编辑器，但专注于生成纹理数据本身。其核心引擎 `TextureGraphEngine` 负责编译和执行这些节点图。

`TextureGraphInsight` 模块是该插件的**调试与性能分析工具**。它提供了一个独立的编辑器窗口，用于实时监控 `TextureGraphEngine` 的运行状态，包括：
- **会话（Session）管理**：记录和回放纹理生成会话。
- **设备（Device）监控**：查看 GPU/CPU 等设备的内存使用、缓冲区状态。
- **作业（Job）与批次（Batch）跟踪**：可视化纹理生成任务的执行流程、依赖关系和耗时。
- **资源（Resource）与 Blob 查看**：检查生成的纹理数据（Blob）及其在设备上的存储状态。
- **操作（Action）与混合（Mix）记录**：记录用户操作和混合节点的执行历史。

简而言之，TextureGraph 解决了“如何通过可视化编程生成复杂纹理”的问题，而 TextureGraphInsight 则解决了“如何调试和优化这个生成过程”的问题。

## 使用场景

- 你需要为游戏或应用程序创建程序化生成的纹理（如地形、材质、特效贴图），且希望过程可视化、可复用。
- 你正在使用 TextureGraph 进行纹理生成，但遇到了性能瓶颈或结果不符合预期，需要深入分析引擎内部的执行情况、内存占用和任务调度。
- 你需要一个工具来记录和回放纹理生成过程，以便进行问题复现或性能对比。

## 蓝图用法

TextureGraphInsight 模块主要提供编辑器 UI 和 C++ 调试接口，其核心类（如 `TextureGraphInsight`、`TextureGraphInsightSession`）并未暴露 `BlueprintCallable` 函数。因此，**该模块不适用于蓝图直接调用**。其功能主要通过编辑器窗口（Insight 窗口）和 C++ API 进行交互。

## C++ 用法

TextureGraphInsight 模块为开发者提供了在 C++ 中集成调试和监控能力的接口。

### 头文件引入

```cpp
#include "TextureGraphInsight.h"
#include "Model/TextureGraphInsightSession.h"
#include "Model/TextureGraphInsightObserver.h"
```

### 基本用法：创建和销毁 Insight 实例

Insight 实例是单例，需要在 TextureGraphEngine 存在时创建。

```cpp
// 来源: Engine/Plugins/TextureGraph/Source/TextureGraphInsight/Public/TextureGraphInsight.h
// 创建 Insight 实例（仅在引擎已创建且无现有实例时成功）
bool bCreated = TextureGraphInsight::Create();

// 获取 Insight 实例
TextureGraphInsight* InsightInstance = TextureGraphInsight::Instance();
if (InsightInstance)
{
    // 获取当前会话
    TextureGraphInsightSessionPtr Session = InsightInstance->GetSession();
    // ... 使用 Session 进行查询或监听
}

// 在不需要时销毁实例
TextureGraphInsight::Destroy();
```

### 进阶用法：实现自定义观察者

你可以继承 `TextureGraphInsightObserver.h` 中定义的观察者基类，来监听引擎的特定事件。

```cpp
// 来源: Engine/Plugins/TextureGraph/Source/TextureGraphInsight/Public/Model/TextureGraphInsightObserver.h
// 自定义一个调度器观察者，用于记录批次完成事件
class FMySchedulerObserver : public TextureGraphInsightSchedulerObserver
{
protected:
    virtual void BatchDone(JobBatchPtr Batch) override
    {
        // 在批次完成时执行自定义逻辑，例如记录日志或触发分析
        UE_LOG(LogTemp, Log, TEXT("TextureGraph Batch Done: %s"), *Batch->GetId().ToString());
        // 调用基类实现以确保 Insight 内部记录正常
        TextureGraphInsightSchedulerObserver::BatchDone(Batch);
    }
};

// 在引擎创建后安装自定义观察者
// 通常需要在 TextureGraphInsightEngineObserver 的 Created() 回调中处理
```

## Demo 示例

以下示例展示了如何在 C++ 中初始化 TextureGraphInsight 并监听引擎事件。

**MyTextureGraphDebugger.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "TextureGraphInsight.h"

class FMyTextureGraphDebugger
{
public:
    void Initialize();
    void Shutdown();

private:
    // 保持对 Insight 会话的引用，以便持续监听
    TextureGraphInsightSessionPtr CachedSession;
};
```

**MyTextureGraphDebugger.cpp**
```cpp
#include "MyTextureGraphDebugger.h"
#include "TextureGraphEngine.h" // 确保引擎模块可用

void FMyTextureGraphDebugger::Initialize()
{
    // 确保 TextureGraphEngine 已初始化
    if (!TextureGraphEngine::IsInitialized())
    {
        UE_LOG(LogTemp, Warning, TEXT("TextureGraphEngine not initialized. Cannot start Insight."));
        return;
    }

    // 创建 Insight 实例
    if (TextureGraphInsight::Create())
    {
        TextureGraphInsight* Insight = TextureGraphInsight::Instance();
        if (Insight)
        {
            CachedSession = Insight->GetSession();
            UE_LOG(LogTemp, Log, TEXT("TextureGraphInsight initialized successfully."));
            // 此时，Insight 内部的观察者已开始工作，会话数据开始被记录。
            // 你可以通过 CachedSession 查询记录，或等待编辑器窗口显示数据。
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create TextureGraphInsight instance."));
    }
}

void FMyTextureGraphDebugger::Shutdown()
{
    // 销毁 Insight 实例
    TextureGraphInsight::Destroy();
    CachedSession.reset();
    UE_LOG(LogTemp, Log, TEXT("TextureGraphInsight shut down."));
}
```

## 模块依赖

要使用 TextureGraphInsight 模块，你的项目模块需要依赖以下内容：

| 模块 | 用途 |
|---|---|
| `TextureGraphEngine` | TextureGraph 的核心运行时引擎，Insight 的监控目标。 |
| `Slate`, `SlateCore`, `UMG` | 构建 Insight 编辑器窗口的 UI 框架。 |
| `RenderCore`, `RHI` | 用于与 GPU 设备和缓冲区交互，获取设备状态信息。 |

## 维护状态

### 近期更新

```
- 2024-05-10 842bdc5a051d PR #13505: Linux: TextureGraph and MetaHuman support
- 2024-04-22 3413adf5ae37 Ran UnrealCodeFixup to fix dll storage
- 2024-04-18 36763ff96ea2 Add slack notifications for "Fortnite VerseVM Compile". Fix failures in "Fortnite VerseVM Compile".
```

### 维护评价

- **创建时间**：插件于 2023 年底创建，相对年轻。
- **最近更新**：最近一次实质性更新（Linux 平台支持）在 2024 年 5 月，距今约 5 个月。后续两次更新为代码维护和构建修复。
- **活跃度**：插件仍在维护中，近期有平台兼容性改进。作为 Epic 官方插件，其长期支持有保障。
- **已知限制**：文档和示例相对较少，主要依赖源码和引擎内置的 Insight 窗口进行学习。`EnabledByDefault=false` 表明它仍被视为一个可选的高级/调试工具。
- **推荐使用**：**推荐**给需要进行程序化纹理生成并希望获得强大调试能力的开发者。对于简单的纹理需求，可能过于复杂。建议结合编辑器内的 Insight 窗口和本文档的 C++ API 进行使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/TextureGraph)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/TextureGraph/Tests) (如果存在)