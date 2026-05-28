# GPU Lightmass

> Static lighting building & previewing system using DXR

| 属性 | 值 |
|---|---|
| 中文名 | GPU光照烘焙 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `GPULightmass` (UncookedOnly), `GPULightmassEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-06-23 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GPULightmass) | |

## 用途

GPULightmass 插件旨在利用现代 GPU 的 DXR（DirectX Raytracing）硬件加速能力，替代传统的 CPU 光照构建（Lightmass）系统。它解决了传统 CPU 光照烘焙耗时过长的问题，特别是在大型复杂场景中。插件的核心功能包括**静态光照的快速构建**和**实时/准实时的光照预览**，允许美术和开发者在编辑器中快速迭代光照效果，大幅提升了工作流程效率。

## 使用场景

*   你正在为一个大型开放世界游戏或复杂的建筑可视化项目制作光照，需要快速获得全局光照（GI）效果，而传统 CPU 烘焙需要等待数小时 → 使用 **GPU Lightmass** 进行快速烘焙。
*   你希望在编辑器中实时预览动态物体在静态光照环境中的表现，以调整光照和材质 → 启用 **GPU Lightmass** 的“所见即所得”（Bake What You See）预览模式。
*   你的团队希望在保证视觉质量的前提下，显著缩短灯光迭代时间 → 将项目的工作流切换为基于 **GPU Lightmass**。

## 蓝图用法

该插件主要提供编辑器集成和控制接口，相关的蓝图可调用函数主要用于编辑器扩展和状态查询。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsBakeWhatYouSeeMode` | 查询是否处于“所见即所得”的实时烘焙预览模式 | `FGPULightmassEditorModule` |
| `IsRunning` | 查询当前是否有 GPU 光照烘焙任务正在运行 | `FGPULightmassEditorModule` |
| `IsRealtimeOn` | 查询实时（Realtime）视口是否已开启（GPU LM 预览需要） | `FGPULightmassEditorModule` |

*注：烘焙的启停控制通常通过编辑器界面（如点击“Build”按钮或使用菜单）触发，对应模块内的 `OnStartClicked`、`OnSaveAndStopClicked` 等函数，这些并非蓝图可直接调用的节点。*

### 使用示例（蓝图描述）

在自定义的编辑器工具或控件蓝图中，你可以：
1.  调用 `IsBakeWhatYouSeeMode` 节点判断当前视口是否支持 GPU LM 实时预览，并据此显示不同的 UI 状态（例如，一个“启用实时预览”的复选框应自动勾选）。
2.  调用 `IsRunning` 节点，在烘焙过程中向用户显示一个“烘焙中…”的进度条或提示信息。

## C++ 用法

GPULightmass 的 C++ 用法主要集中在**编辑器扩展**层面，用于集成或自定义其设置面板和构建菜单。

### 头文件引入

```cpp
#include "GPULightmassEditorModule.h"
```

### 基本用法

获取模块实例并访问其设置视图，常用于创建自定义的光照设置窗口。

```cpp
// 在某个编辑器工具或窗口类中
#include "GPULightmassEditorModule.h"
#include "ISettingsView.h"

// 获取模块实例
FGPULightmassEditorModule& GPULightmassModule = FModuleManager::GetModuleChecked<FGPULightmassEditorModule>(TEXT("GPULightmassEditor"));

// 访问其设置面板视图 (IDetailsView)
TSharedPtr<IDetailsView> SettingsView = GPULightmassModule.SettingsView;
if (SettingsView.IsValid())
{
    // 可以将其添加到你自己的停靠面板中
    // SNew(SDockTab) ... [ContentSlot][ SettingsView.ToSharedRef() ];
}
```

### 进阶用法

监听模块内的烘焙状态变化，例如，在烘焙开始或结束时执行自定义逻辑。

```cpp
// 假设你有一个自定义的编辑器模块需要响应 GPU LM 状态
void FMyEditorModule::StartupModule()
{
    // 可以监听关卡编辑器的映射变化，类似 GPULightmassModule.OnMapChanged
    FEditorDelegates::MapChange.AddRaw(this, &FMyEditorModule::OnMapChanged);

    // 也可以定期检查状态（轮询方式）
    // if (FGPULightmassEditorModule::IsRunning()) { ... }
}
```

## Demo 示例

以下是一个最小化的示例，展示如何创建一个简单的编辑器面板来显示和控制 GPU Lightmass 的状态。

**MyGPUTab.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"

class SMyGPUStatusPanel : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyGPUStatusPanel) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    FText GetStatusText() const;
    FReply OnBuildClicked();
};
```

**MyGPUTab.cpp**
```cpp
#include "MyGPUTab.h"
#include "GPULightmassEditorModule.h"

void SMyGPUStatusPanel::Construct(const FArguments& InArgs)
{
    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .AutoHeight()
        [
            SNew(STextBlock)
            .Text(this, &SMyGPUStatusPanel::GetStatusText)
        ]
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(5.0f)
        [
            SNew(SButton)
            .Text(FText::FromString(TEXT("开始烘焙")))
            .OnClicked(this, &SMyGPUStatusPanel::OnBuildClicked)
        ]
    ];
}

FText SMyGPUStatusPanel::GetStatusText() const
{
    if (FGPULightmassEditorModule::IsRunning())
    {
        return FText::FromString(TEXT("状态：正在烘焙..."));
    }
    else
    {
        return FText::FromString(TEXT("状态：就绪"));
    }
}

FReply SMyGPUStatusPanel::OnBuildClicked()
{
    // 注意：直接调用启动烘焙的函数通常是 Editor 模块内部命令的一部分。
    // 这里作为演示，你可以通过命令行或调用更底层的 API 来触发。
    // 实际中，更常见的是使用编辑器内置的“Build Lighting”菜单项。
    UE_LOG(LogTemp, Warning, TEXT("启动GPU Lightmass烘焙的演示逻辑"));
    return FReply::Handled();
}
```

## 模块依赖

使用此插件需要你的模块（通常是一个编辑器模块）链接以下特定依赖：

| 模块 | 用途 |
|---|---|
| `GPULightmassEditor` | 提供编辑器集成、设置界面和构建控制逻辑 |
| `RenderCore` | 提供渲染核心功能，DXR 光照烘焙的基础 |
| `RHI` | 提供渲染硬件接口抽象 |
| `D3D12RHI` | 提供 DirectX 12 RHI 实现，这是 DXR 功能的基础 |
| `RayTracing` | 提供引擎的光线追踪核心功能 |

*注：`GPULightmass` 核心模块作为 `UncookedOnly` 类型，在运行时不存在，其依赖由 `GPULightmassEditor` 在编辑器内处理。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `78d4e656` | [GPULM] Flush deferred SBT static-range frees on cached scene teardown | 修复了缓存场景销毁时着色器绑定表（SBT）静态范围内存未及时释放的问题 |
| 2026-05-12 | `98b3c0ef` | [HWRT] Add MeshBatchesView to FRayTracingDynamicGeometryUpdateParams and unify mesh batch ownership. | 重构了硬件光线追踪的动态几何体更新参数，统一了网格批处理的所有权管理 |
| 2026-04-21 | `a437915f` | [HWRT] Refactored shared vertex buffer management in FRayTracingDynamicGeometryUpdateManager. | 重构了硬件光线追踪动态几何体更新管理器中的共享顶点缓冲区管理 |
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 将 `BlockUntilGPUIdle` 和 `SubmitCommandsAndFlushGPU` 合并替换为 `SubmitAndBlockUntilGPUIdle` |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将部分 `UE_LOG` 宏迁移至 `UE_LOGF` 格式 |

### 维护评价

GPULightmass 仍处于**实验性（Beta）** 状态，且默认未启用，仅支持 Win64 平台。尽管如此，从提交历史看，其依赖的**底层硬件光线追踪（HWRT）和渲染核心模块仍在被 Epic 积极维护和重构**（如最近的 SBT 和顶点缓冲管理优化）。插件本身的功能性提交较少，更多是跟随底层引擎渲染技术的演进。它是一个**面向未来的技术预览**，适合希望尝鲜和测试最新 GPU 光照技术的用户，但**不建议用于要求绝对稳定的生产项目**。推荐用于内部测试、原型开发或对技术前沿感兴趣的团队。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GPULightmass)
- 官方文档（无）
- 测试用例（未在插件目录内发现标准测试文件）