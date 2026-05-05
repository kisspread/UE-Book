# Derived Data Build Controller

> Adds support for shader compiling distribution using the Derived Data Build API

| 属性 | 值 |
|---|---|
| 分类 | Build Distribution |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DerivedDataBuildController` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-02-04 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/DerivedDataBuildController) | |

## 用途

该插件的核心功能是为引擎的**着色器编译**过程提供**分布式构建**支持。它通过集成“Derived Data Build API”，允许将耗时且资源密集的着色器编译任务分发到网络中的其他机器（如构建农场）上执行，从而显著加速大型项目的构建和迭代速度。它解决的是本地开发机在编译大量着色器时遇到的性能瓶颈问题。

## 使用场景

- 你正在开发一个拥有海量材质和着色器的大型项目（如开放世界游戏），本地编译着色器需要数十分钟甚至数小时。
- 你的团队拥有一个构建农场或分布式计算资源，希望利用这些资源来加速开发迭代。
- 你在持续集成/持续部署（CI/CD）流水线中，需要优化构建时间。

## 蓝图用法

该插件主要提供底层的 C++ 接口以集成到引擎的构建系统中，未发现暴露给蓝图的 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。其配置和使用主要通过引擎设置和 C++ 代码完成。

## C++ 用法

该插件作为编辑器模块，其主要作用是注册和提供分布式构建控制器。开发者通常不直接调用其 API，而是通过配置引擎来使用它。

### 头文件引入

```cpp
#include "DerivedDataBuildController.h"
```

### 基本用法

该插件的核心是实现一个 `IDerivedDataBuildController` 接口。启用插件后，引擎的派生数据缓存（DDC）系统会自动发现并使用它。开发者主要需要做的是配置连接到分布式构建服务。

```cpp
// 通常，开发者无需直接实例化该控制器。
// 它的生命周期由引擎的 DDC 系统管理。
// 使用场景是在引擎启动时，通过配置文件或命令行参数指定分布式构建后端。
// 例如，在 DefaultEngine.ini 中可能需要配置类似以下内容（具体配置项需查阅插件文档或源码）：
// [DerivedDataBuildController]
// BuildServiceURL=your.build.service.url
```

### 进阶用法

作为实验性功能，其高级用法可能涉及自定义构建任务的分发策略或与特定构建农场软件的集成。这通常需要深入阅读插件源码和 Derived Data Build API 的文档。

## Demo 示例

由于该插件是引擎基础设施的一部分，且为实验性功能，没有独立的运行时示例。其“示例”体现在正确配置后，引擎着色器编译过程的加速上。

```cpp
// 假设的配置示例代码，展示如何在引擎初始化时检查该插件状态。
// 注意：这并非直接使用插件 API，而是展示其存在性。
#include "Features/IModularFeatures.h"
#include "DerivedDataBuildController.h"

void CheckDDBuildControllerStatus()
{
    // 检查 DerivedDataBuildController 模块是否加载
    FModuleManager& ModuleManager = FModuleManager::Get();
    if (ModuleManager.IsModuleLoaded(TEXT("DerivedDataBuildController")))
    {
        UE_LOG(LogTemp, Log, TEXT("DerivedDataBuildController module is loaded and active."));
        // 在实际应用中，DDC 系统会自动使用它，无需手动干预。
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("DerivedDataBuildController module is not loaded."));
    }
}
```

## 模块依赖

从插件类型（Editor）和功能推断，它很可能依赖于引擎的核心派生数据和构建系统模块。

| 模块 | 用途 |
|---|---|
| `DerivedDataCache` | 引擎的派生数据缓存系统，是本插件集成的主要目标。 |
| `DerivedDataBuild` | Derived Data Build API 的核心模块，提供构建任务分发的基础框架。 |

## 维护状态

### 近期更新

- 2026-02-04 d31da60d Added a DerivedDataBuildController to support compiling shaders through the Derived Data Build API

### 维护评价

- **创建时间**：插件于 2026 年 2 月 4 日创建，非常新。
- **更新频率**：目前仅有一次初始提交，尚无后续更新记录。
- **活跃度**：作为新创建的实验性插件，处于早期开发阶段，活跃度未知。
- **已知限制**：标记为 `IsExperimentalVersion: true`，表明其 API 和功能可能不稳定，不建议在生产环境中依赖。
- **推荐使用**：**谨慎使用**。仅推荐给希望尝试前沿分布式构建技术、并能接受潜在不稳定性的高级用户或团队。对于大多数项目，建议等待其成熟并转为正式功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/DerivedDataBuildController)
- 官方文档：暂无
- 测试用例：暂无