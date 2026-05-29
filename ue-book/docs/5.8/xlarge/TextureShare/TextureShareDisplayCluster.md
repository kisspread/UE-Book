# Texture Share

> Share textures and data between processes（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 纹理共享 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置模板） |
| 模块 | `TextureShareCore` (Runtime), `TextureShare` (Runtime), `TextureShareDisplayCluster` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-06-25 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/TextureShare) | |

## 用途
TextureShare 插件的核心目的是实现**跨进程的纹理和数据共享**。它基于 Unreal Engine 的纹理共享 SDK 构建，并提供了与 nDisplay 虚拟制片框架的深度集成。这个插件主要解决在虚拟制片、多机渲染（如 LED 墙体渲染集群）等复杂场景下，不同 UE 进程（或与其他应用程序）之间需要实时、高效地同步渲染画面、投影矩阵等数据的需求。通过它，一个主进程可以将其渲染的特定视图或纹理共享给从进程，从而实现大规模、同步的视觉输出。

## 使用场景
- **多屏同步渲染**：在虚拟制片中使用 nDisplay 控制多个 LED 屏幕时，需要确保所有渲染节点（PC）的画面严格同步。
- **远程画面预览或合成**：将渲染进程的画面实时共享到另一个用于监控、合成或录制的进程。
- **自定义投影校准**：需要从外部进程（如校准工具）动态接收并应用自定义投影矩阵到 nDisplay 的视口。

## 蓝图用法
该插件主要面向 C++ 和 nDisplay 配置，未发现直接暴露给蓝图的核心函数库。其功能主要通过 nDisplay 的配置文件（.ndisplay）进行配置，并在 C++ 层通过接口进行扩展和控制。

## C++ 用法
### 头文件引入
```cpp
#include "ITextureShareDisplayCluster.h"
#include "ITextureShareDisplayClusterAPI.h"
```

### 基本用法
获取 TextureShare 的 nDisplay 集成模块接口，并设置手动投影数据。
```cpp
// 来源: ITextureShareDisplayCluster.h
if (ITextureShareDisplayCluster::IsAvailable())
{
    // 获取 TextureShareDisplayCluster 模块的 API 接口
    ITextureShareDisplayClusterAPI& DisplayClusterAPI = ITextureShareDisplayCluster::Get().GetTextureShareDisplayClusterAPI();
    
    // 假设你有一个指向 nDisplay 投影策略的共享指针 (TSharedPtr<IDisplayClusterProjectionPolicy>)
    TSharedPtr<IDisplayClusterProjectionPolicy, ESPMode::ThreadSafe> MyProjectionPolicy = /* ... */;
    
    // 准备要设置的自定义投影数据
    TArray<FTextureShareCoreManualProjection> ProjectionData;
    ProjectionData.Add(/* 填充投影矩阵、视图位置等信息 */);
    
    // 调用 API 设置投影数据到指定的策略
    bool bSuccess = DisplayClusterAPI.TextureSharePolicySetProjectionData(MyProjectionPolicy, ProjectionData);
}
```

### 进阶用法
理解并利用其后处理（PostProcess）和投影策略（ProjectionPolicy）工厂，在 nDisplay 管线中注册自定义逻辑。
```cpp
// 来源: TextureSharePostprocessFactory.h, TextureShareProjectionPolicyFactory.h
// 插件在启动时会自动向 nDisplay 注册以下工厂：
// 1. FTextureSharePostprocessFactory: 创建 TextureShare 后处理节点，用于在 nDisplay 渲染管线中捕获和共享纹理。
// 2. FTextureShareProjectionPolicyFactory: 创建 TextureShare 投影策略，用于接收外部投影数据。
//
// 你通常不需要直接调用这些工厂，它们由插件模块（FTextureShareDisplayCluster）的 StartupModule 自动注册。
// 但你需要在 nDisplay 配置中引用它们，例如：
//   Postprocess: Type="TextureShare", Id="SharedFrame"
//   Projection:  Type="textureshare", Id="SharedProjection"
```

## Demo 示例
一个简单的示例，演示如何在自己的模块中访问 TextureShareDisplayCluster 的 API。
```cpp
// MyModule.h
#pragma once
#include "Modules/ModuleManager.h"

class FMyModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void TryAccessTextureShareAPI();
};
```

```cpp
// MyModule.cpp
#include "MyModule.h"
#include "ITextureShareDisplayCluster.h"
#include "ITextureShareDisplayClusterAPI.h"

#define LOCTEXT_NAMESPACE "FMyModule"

void FMyModule::StartupModule()
{
    // 延迟访问，确保 TextureShareDisplayCluster 模块已加载
    TryAccessTextureShareAPI();
}

void FMyModule::ShutdownModule()
{
}

void FMyModule::TryAccessTextureShareAPI()
{
    if (ITextureShareDisplayCluster::IsAvailable())
    {
        ITextureShareDisplayClusterAPI& API = ITextureShareDisplayCluster::Get().GetTextureShareDisplayClusterAPI();
        UE_LOG(LogTemp, Log, TEXT("Successfully obtained TextureShareDisplayClusterAPI."));
        // 在这里存储 `&API` 指针或进行其他操作。
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("TextureShareDisplayCluster module is not available."));
    }
}

#undef LOCTEXT_NAMESPACE
IMPLEMENT_MODULE(FMyModule, MyModule)
```

## 模块依赖
| 模块 | 用途 |
|---|---|
| `nDisplay` | 提供显示集群（Display Cluster）的核心框架、投影策略和后处理接口，是本插件集成的基石。 |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复跨编译器的函数类型转换警告。 |
| 2026-04-16 | `270dc64a` | Fix unreachable code warnings | 修复无法到达的代码警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏至新版本（UE_LOGF）。 |
| 2026-03-18 | `c8d86942` | Deprecate more unused includes from public rendering headers. | 清理公共渲染头文件中未使用的包含项。 |
| 2026-03-02 | `c3f81430` | VulkanRHI: Remove extensions that don't need to be manually loaded anymore from plugin startup: | 移除插件启动时不再需要手动加载的 Vulkan 扩展。 |

### 维护评价
- **创建时间**：2022年6月，插件年龄约3年。
- **活跃度**：根据 Git 历史，插件仍在持续维护，最近的提交集中在2026年3月至5月。
- **更新内容**：近期的更新主要是**代码质量维护**，包括修复编译警告、清理代码和迁移日志宏，没有新的功能特性引入。这表明插件功能已趋于稳定。
- **状态**：插件标记为 `IsBetaVersion=true`，且 `EnabledByDefault=false`，表明它仍处于实验性阶段，并非所有项目默认可用。
- **推荐**：该插件是为特定虚拟制片场景（nDisplay集成）设计的。如果你正在搭建基于 nDisplay 的多机渲染系统，并需要进程间纹理同步，那么这个插件是必要的。对于其他通用场景，则无需使用。鉴于其“实验性”标签，在生产环境中使用前应进行充分测试。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/TextureShare)
- [官方文档]()（无）
- [测试用例]()（未在提供的信息中发现）