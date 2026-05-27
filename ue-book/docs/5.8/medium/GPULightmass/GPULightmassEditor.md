# GPU Lightmass

> Static lighting building & previewing system using DXR

| 属性 | 值 |
|---|---|
| 中文名 | GPU 光照烘培 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具、设置资产） |
| 模块 | `GPULightmass` (UncookedOnly), `GPULightmassEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-06-23 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GPULightmass) | |

## 用途

GPULightmass 是 Unreal Engine 中基于 DXR (DirectX Raytracing) 的静态光照构建系统，旨在替代传统的 CPU 光照烘培（Lightmass）。它通过利用 GPU 硬件加速的光线追踪技术，大幅加速全局光照、光遮蔽、反射等静态光照信息的计算过程。

它的核心价值在于：
1.  **速度**：相比 CPU 烘培，GPU 烘培的速度通常提升数十倍甚至更多，极大地缩短了关卡灯光设计和迭代的时间。
2.  **实时预览**：支持 “Bake What You See”（所见即烘培）模式，允许开发者在编辑器中以接近实时的反馈调整灯光参数并快速查看结果，无需经历漫长的烘培等待过程。
3.  **工作流程改进**：通过提供一个集成的、交互式的烘培界面，改善了传统静态光照工作流程中“调整-等待-查看”循环的低效问题。

**存在原因**：传统 CPU 光照烘培速度慢，是美术和关卡设计迭代的主要瓶颈之一。随着实时光线追踪硬件的普及，利用 GPU 进行离线烘培成为一种既快速又能保证高质量结果的可行方案。此插件是 Epic Games 对这一方向的实验性探索和实现。

## 使用场景

-   你正在为一个大型开放世界场景设置灯光，希望快速看到调整太阳角度或环境光强度后的全局光照效果。
-   你的美术团队需要频繁迭代灯光方案，传统 CPU 烘培（可能耗时数小时）严重拖慢了工作进度。
-   你希望在编辑器中进行最终光照效果的实时预览，并立即将预览结果“固化”为高质量的静态光照数据。
-   你的工作站配备了支持 DXR 的 NVIDIA RTX 系列显卡，希望充分利用其性能优势。

## 蓝图用法

GPULightmass 主要通过编辑器 UI 和控制台命令交互，其核心功能通过 `FGPULightmassEditorModule` 暴露给编辑器扩展和蓝图。虽然它不是一个为游戏运行时设计的蓝图库，但以下功能可用于编辑器工具脚本或蓝图编辑器工具。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsRunning()` | 检查 GPULightmass 烘培进程是否正在运行。 | `FGPULightmassEditorModule` (Static) |
| `IsBakeWhatYouSeeMode()` | 检查是否处于“所见即烘培”的实时预览模式。 | `FGPULightmassEditorModule` (Static) |
| `IsRealtimeOn()` | 检查实时更新是否开启。 | `FGPULightmassEditorModule` (Static) |

### 使用示例（蓝图描述）

由于主要交互发生在专用设置面板，蓝图中的典型用法是**查询状态**。例如，在编辑器工具蓝图中，你可以：
1.  使用 `GPULightmass IsRunning` 节点检查当前是否正在烘培。
2.  如果正在运行，可以调用你自定义的“保存当前设置”函数。
3.  使用 `GPULightmass IsBakeWhatYouSeeMode` 来决定UI上某个按钮的文本或状态。

**操作按钮**（`OnStartClicked`， `OnSaveAndStopClicked`， `OnCancelClicked`）通常绑定在编辑器UI上，但在蓝图中可作为自定义编辑器扩展的一部分被调用。

## C++ 用法

### 头文件引入

```cpp
#include "GPULightmassEditorModule.h" // 访问编辑器模块和功能
```

### 基本用法

以下示例展示了如何从 C++ 编辑器工具中查询 GPULightmass 的状态。

```cpp
// 检查 GPULightmass 是否可用且正在运行
void CheckGPULightmassStatus()
{
    FGPULightmassEditorModule& GPULightmassModule = FModuleManager::GetModuleChecked<FGPULightmassEditorModule>("GPULightmassEditor");
    
    if (FGPULightmassEditorModule::IsRunning())
    {
        UE_LOG(LogTemp, Log, TEXT("GPULightmass 当前正在运行烘培任务。"));
    }
    
    if (FGPULightmassEditorModule::IsBakeWhatYouSeeMode())
    {
        UE_LOG(LogTemp, Log, TEXT("GPULightmass 处于‘所见即烘培’模式。"));
    }
}
```

### 进阶用法

结合其设计意图，C++ 中的进阶用法通常涉及创建自定义的编辑器工具或扩展其 UI。例如，你可能想向 GPULightmass 设置面板添加自定义参数。

```cpp
// 概念性代码，展示如何可能集成
void ExtendGPULightmassUI()
{
    // 获取 GPULightmass 的 Tab
    FGlobalTabmanager::Get()->RegisterNomadTabSpawner("GPULightmassSettings", 
        FOnSpawnTab::CreateLambda([](const FSpawnTabArgs& Args) -> TSharedRef<SDockTab>
        {
            // GPULightmass 内部会创建其 SettingsView
            // 此处仅为示例，实际扩展可能需要更深入的集成
            TSharedRef<SDockTab> Tab = SNew(SDockTab)
                .TabRole(ETabRole::NomadTab)
                [
                    SNew(STextBlock)
                    .Text(FText::FromString(TEXT("Custom GPULightmass Extension")))
                ];
            return Tab;
        }));
}
```

## Demo 示例

一个最小的编辑器模块示例，用于演示如何引用和查询 GPULightmass 状态。

**MyEditorModule.h**
```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    void LogGPULightmassStatus();
};
```

**MyEditorModule.cpp**
```cpp
#include "MyEditorModule.h"
#include "GPULightmassEditorModule.h"

#define LOCTEXT_NAMESPACE "FMyEditorModule"

void FMyEditorModule::StartupModule()
{
    // 模块启动后，可以查询GPULightmass状态
    LogGPULightmassStatus();
}

void FMyEditorModule::ShutdownModule()
{
}

void FMyEditorModule::LogGPULightmassStatus()
{
    if (FModuleManager::Get().IsModuleLoaded("GPULightmassEditor"))
    {
        UE_LOG(LogTemp, Log, TEXT("GPULightmassEditor 模块已加载。"));
        UE_LOG(LogTemp, Log, TEXT("GPULightmass 是否正在运行: %s"), 
            FGPULightmassEditorModule::IsRunning() ? TEXT("是") : TEXT("否"));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("GPULightmassEditor 模块未加载。"));
    }
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyEditorModule, MyEditor)
```

## 模块依赖

从模块类型和插件性质推断，使用者可能需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `Renderer` | 提供底层渲染和光线追踪支持。 |
| `RenderCore` | 核心渲染工具和数据结构。 |
| `LevelEditor` | 用于扩展关卡编辑器菜单和工具栏。 |
| `PropertyEditor` | 用于创建自定义的细节面板和设置界面。 |

**注意**：由于插件处于实验性状态且文档有限，具体的依赖关系可能因内部实现而有所不同。建议参考源码中的 `Build.cs` 文件进行精确配置。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `78d4e656` | [GPULM] Flush deferred SBT static-range frees on cached scene teardown | 修复了在缓存场景销毁时，着色器绑定表(SBT)静态范围延迟释放未刷新的问题。 |
| 2026-05-12 | `98b3c0ef` | [HWRT] Add MeshBatchesView to FRayTracingDynamicGeometryUpdateParams and unify mesh batch ownership. | 为硬件光线追踪(HWRT)的动态几何更新参数添加了网格批次视图，并统一了网格批次的所有权管理。 |
| 2026-04-21 | `a437915f` | [HWRT] Refactored shared vertex buffer management in FRayTracingDynamicGeometryUpdateManager. | 重构了 `FRayTracingDynamicGeometryUpdateManager` 中共享顶点缓冲区的管理。 |
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 移除了 `BlockUntilGPUIdle` 和 `SubmitCommandsAndFlushGPU` 函数，改用统一的 `SubmitAndBlockUntilGPUIdle`。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移至新的 `UE_LOGF` 格式。 |

### 维护评价

-   **状态**：**活跃维护中**。最近的提交（2026年5月）表明 Epic 仍在积极开发和修复与硬件光线追踪（HWRT）相关的问题，而 GPULightmass 深度依赖此功能。
-   **年龄与实验性**：创建于 2020 年，已存在 6 年，属于 **老古董** 级别的实验性功能。其状态一直为 “实验性（Beta）” 且 `EnabledByDefault: false`，表明它尚未被官方推荐为生产工作流的标准部分，但仍在持续改进。
-   **推荐度**：对于拥有兼容 DXR 显卡并希望大幅提升光照迭代速度的 **生产项目**，它是一个极具价值的**实验性工具**。可以用于原型开发和关卡灯光的快速迭代。但在将其用于最终发布的项目前，需要充分评估其稳定性和与现有资产管线的兼容性。它仍然是**实验性质**的。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GPULightmass)
-   [官方文档]() (无)
-   [测试用例]() (插件目录内未包含独立测试用例，测试可能集成在引擎核心渲染测试中)